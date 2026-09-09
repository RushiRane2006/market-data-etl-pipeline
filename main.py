import time

from config import TICKERS
from extract import fetch_daily_data
from transform import raw_to_dataframe, compute_daily_change_pct
from load import insert_price_data
from alerts import check_price_change_alert, save_alerts


def run_pipeline_once():
    """
    Runs one full pass of the pipeline across all configured tickers:
    extract -> transform -> load -> check for alerts.
    """
    print(f"\n=== Pipeline run started: {time.strftime('%Y-%m-%d %H:%M:%S')} ===")

    for ticker in TICKERS:
        print(f"\n--- {ticker} ---")

        raw = fetch_daily_data(ticker)
        if raw is None:
            # extract.py already printed the reason (rate limit, API
            # error, etc.) — we just skip this ticker for this run
            # rather than crashing the whole pipeline over one failure.
            print(f"[{ticker}] Skipped this run due to fetch failure.")
            continue

        df = raw_to_dataframe(raw, ticker)
        df = compute_daily_change_pct(df)

        insert_price_data(df)

        found_alerts = check_price_change_alert(df, ticker)
        if found_alerts:
            save_alerts(found_alerts)
        else:
            print(f"[{ticker}] No alert triggered this run.")

        time.sleep(1.5)

    print(f"\n=== Pipeline run finished: {time.strftime('%Y-%m-%d %H:%M:%S')} ===")


if __name__ == "__main__":
    run_pipeline_once()

    # --- uncomment below to run on a schedule instead of once ---
    #
    # import schedule
    # schedule.every(1).hours.do(run_pipeline_once)
    # print("Scheduler started — pipeline will run every hour. Ctrl+C to stop.")
    # while True:
    #     schedule.run_pending()
    #     time.sleep(30)
