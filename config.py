import os
from dotenv import load_dotenv

load_dotenv()

# --- Alpha Vantage ---
# Get a free key at https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# --- Tickers to track ---
TICKERS = ["AAPL", "MSFT"]

# --- Postgres connection ---
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432"),
    "dbname": os.environ.get("DB_NAME", "market_pipeline"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", ""),
}

# --- Alert thresholds ---
# If price moves more than this % within one polling interval, flag it.
PRICE_CHANGE_ALERT_PCT = 1.0
