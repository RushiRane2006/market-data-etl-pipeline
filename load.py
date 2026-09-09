import psycopg2
from psycopg2.extras import execute_values
from config import DB_CONFIG


def get_connection():
    """
    Opens a new connection to Postgres using the settings in config.py.
    """
    return psycopg2.connect(**DB_CONFIG)


def insert_price_data(df):
    """
    Inserts rows from the DataFrame into the price_data table.
    """
    if df.empty:
        print("No rows to insert (empty DataFrame).")
        return 0

    records = list(
        df[["ticker", "ts", "open", "high", "low", "close", "volume"]]
        .itertuples(index=False, name=None)
    )

    insert_query = """
        INSERT INTO price_data (ticker, ts, open, high, low, close, volume)
        VALUES %s
        ON CONFLICT (ticker, ts) DO NOTHING
    """

    conn = get_connection()
    try:
        with conn:  
            with conn.cursor() as cur:
                execute_values(cur, insert_query, records)
                inserted = cur.rowcount
        print(f"Inserted {len(records)} row(s) submitted "
              f"({inserted} new, {len(records) - inserted} skipped as duplicates).")
        return inserted
    finally:
        conn.close()


def get_latest_rows(ticker, limit=5):
    """
    Small helper to pull back the most recent rows for a ticker —
    useful for sanity-checking that data actually landed correctly.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ticker, ts, open, high, low, close, volume
                FROM price_data
                WHERE ticker = %s
                ORDER BY ts DESC
                LIMIT %s
                """,
                (ticker, limit),
            )
            return cur.fetchall()
    finally:
        conn.close()


if __name__ == "__main__":
    import time
    from config import TICKERS
    from extract import fetch_daily_data
    from transform import raw_to_dataframe, compute_daily_change_pct

    for ticker in TICKERS:
        raw = fetch_daily_data(ticker)
        if raw:
            df = raw_to_dataframe(raw, ticker)
            df = compute_daily_change_pct(df)
            insert_price_data(df)
        time.sleep(1.5)

    # Confirm data actually landed by reading it back.
    print("\n--- Verifying via SELECT ---")
    for ticker in TICKERS:
        rows = get_latest_rows(ticker)
        print(f"\n[{ticker}] Latest rows in DB:")
        for row in rows:
            print(row)
