import pandas as pd


def raw_to_dataframe(raw_data, ticker):
    """
    Converts Alpha Vantage's raw TIME_SERIES_DAILY response into a
    clean DataFrame with one row per trading day.

    Input:  raw_data -> the dict returned by extract.fetch_daily_data()
            ticker   -> the ticker string, e.g. "AAPL"

    Output: a DataFrame with columns:
            ticker, ts, open, high, low, close, volume
            sorted by date ascending (oldest first)
    """
    daily_series = raw_data.get("Time Series (Daily)")

    if not daily_series:
        raise ValueError(f"[{ticker}] No 'Time Series (Daily)' key found in raw data.")

    df = pd.DataFrame.from_dict(daily_series, orient="index")

    df = df.rename(columns={
        "1. open": "open",
        "2. high": "high",
        "3. low": "low",
        "4. close": "close",
        "5. volume": "volume",
    })

    df.index.name = "ts"
    df = df.reset_index()
    df["ts"] = pd.to_datetime(df["ts"])

    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    before = len(df)
    df = df.dropna(subset=["open", "high", "low", "close"])
    dropped = before - len(df)
    if dropped > 0:
        print(f"[{ticker}] Dropped {dropped} row(s) with unparseable price data.")

    df["ticker"] = ticker

    df = df.sort_values("ts").reset_index(drop=True)

    df = df[["ticker", "ts", "open", "high", "low", "close", "volume"]]

    return df


def compute_daily_change_pct(df):
    df = df.copy()
    df["change_pct"] = df["close"].pct_change() * 100
    return df


if __name__ == "__main__":
    import time
    from config import TICKERS
    from extract import fetch_daily_data

    for ticker in TICKERS:
        raw = fetch_daily_data(ticker)
        if raw:
            df = raw_to_dataframe(raw, ticker)
            df = compute_daily_change_pct(df)
            print(f"\n[{ticker}] Clean data — last 5 rows:")
            print(df.tail(5).to_string(index=False))
        time.sleep(1.5)
