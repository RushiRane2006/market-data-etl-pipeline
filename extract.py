import requests
import time
from config import ALPHA_VANTAGE_API_KEY, ALPHA_VANTAGE_BASE_URL


def fetch_daily_data(ticker, max_retries=3):
    """
    Calls Alpha Vantage's TIME_SERIES_DAILY endpoint for one ticker.

    Returns: raw dict from the API (still in Alpha Vantage's own format),
             or None if every retry fails.
    """
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "outputsize": "compact",  
        "apikey": ALPHA_VANTAGE_API_KEY,
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
            response.raise_for_status()  # raises an exception on 4xx/5xx status codes
            data = response.json()

            if "Note" in data or "Information" in data:
                print(f"[{ticker}] API limit or info message: "
                      f"{data.get('Note') or data.get('Information')}")
                return None

            if "Error Message" in data:
                print(f"[{ticker}] API error: {data['Error Message']}")
                return None

            return data

        except requests.exceptions.RequestException as e:
            print(f"[{ticker}] Attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(2 * attempt)  # wait a bit longer each retry (backoff)

    print(f"[{ticker}] All {max_retries} attempts failed. Skipping this cycle.")
    return None


if __name__ == "__main__":
    from config import TICKERS
    for t in TICKERS:
        result = fetch_daily_data(t)
        if result:
            print(f"[{t}] Got data. Top-level keys: {list(result.keys())}")
        time.sleep(1.5)  