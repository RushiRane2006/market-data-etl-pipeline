from config import PRICE_CHANGE_ALERT_PCT
from load import get_connection
import pandas as pd


def check_price_change_alert(df, ticker):
    """
    Looks at the most recent row in the (already-transformed) DataFrame
    and checks whether its day-over-day % change exceeds our threshold.

    Returns: a list of alert dicts (usually 0 or 1 items).
    """
    alerts = []

    if df.empty or "change_pct" not in df.columns:
        return alerts

    latest = df.iloc[-1]  # most recent row, since transform.py sorts oldest->newest
    change = latest["change_pct"]

    if pd.isna(change):
        # This happens on the very first row of a series (no previous
        # day to compare against) — nothing to alert on, not an error.
        return alerts

    if abs(change) >= PRICE_CHANGE_ALERT_PCT:
        direction = "up" if change > 0 else "down"
        message = (f"{ticker} moved {direction} {abs(change):.2f}% "
                    f"on {latest['ts'].date()} (close: {latest['close']})")
        alerts.append({
            "ticker": ticker,
            "alert_type": "price_change",
            "message": message,
        })

    return alerts


def save_alerts(alerts):
    """
    Writes a list of alert dicts into the alerts table, and also prints them.
    """
    if not alerts:
        return

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                for alert in alerts:
                    cur.execute(
                        """
                        INSERT INTO alerts (ticker, alert_type, message)
                        VALUES (%s, %s, %s)
                        """,
                        (alert["ticker"], alert["alert_type"], alert["message"]),
                    )
                    print(f"🚨 ALERT: {alert['message']}")
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
            found = check_price_change_alert(df, ticker)
            if found:
                save_alerts(found)
            else:
                print(f"[{ticker}] No alert — latest change within threshold.")
        time.sleep(1.5)
