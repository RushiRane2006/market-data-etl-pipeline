# Market Data ETL Pipeline

A small, self-contained ETL (Extract, Transform, Load) pipeline that pulls daily
stock price data from the Alpha Vantage API, cleans and validates it, stores it
in PostgreSQL, and flags significant day-over-day price moves as alerts.

## Why this project

Before any analysis, dashboard, or trading strategy can run, raw market data has
to be reliably fetched, cleaned, and stored somewhere queryable — that's the job
of an ETL pipeline, and it's one of the most common real-world patterns in data
and quant engineering. This project is a small, honest version of that pattern:
built to understand it hands-on, not just as a theoretical concept.

## Architecture

```
Alpha Vantage API
      |
      v
 extract.py    -> fetches raw JSON, handles retries/rate limits/errors
      |
      v
 transform.py  -> cleans data, fixes types, computes % daily change
      |
      v
  load.py      -> writes to PostgreSQL (idempotent — safe to re-run)
      |
      v
 alerts.py     -> checks thresholds, logs alerts to DB + console
      |
      v
 main.py       -> orchestrates the full pipeline across all tickers
```

Each file has exactly one responsibility. `extract.py` doesn't know anything
about pandas or SQL; `transform.py` doesn't know anything about HTTP or
Alpha Vantage; `load.py` doesn't know anything about the API. This separation
means any one piece (e.g. the data source) can be swapped without touching
the rest of the pipeline.

## Tech Stack

- **Python** — `requests`, `pandas`, `psycopg2`
- **PostgreSQL** — persistent storage, with a `UNIQUE (ticker, ts)` constraint
  enforcing idempotency (re-running the pipeline never creates duplicate rows)
- **Alpha Vantage API** — free-tier daily equity price data

## Setup

1. Clone the repo and install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Get a free Alpha Vantage API key:
   https://www.alphavantage.co/support/#api-key

3. Create a `.env` file in the project root:
   ```
   ALPHA_VANTAGE_API_KEY=your_key_here
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=market_pipeline
   DB_USER=postgres
   DB_PASSWORD=your_postgres_password
   ```

4. Create the database and run the schema:
   ```
   createdb market_pipeline
   psql -U postgres -d market_pipeline -f schema.sql
   ```

5. Run the pipeline:
   ```
   python main.py
   ```

6. Run the tests:
   ```
   python test_transform.py
   ```

## Design Decisions Worth Noting

- **Idempotent loading**: uses `ON CONFLICT (ticker, ts) DO NOTHING`, so
  re-running the pipeline on overlapping data never creates duplicates —
  verified by running the pipeline twice in a row and confirming the second
  run reports 0 new rows.
- **Retry logic with backoff**: API calls fail sometimes for reasons unrelated
  to the code (network blips, rate limits). `extract.py` retries with
  increasing delays rather than crashing on the first failure.
- **Secrets kept out of source control**: API keys and DB credentials are
  loaded from a `.env` file (excluded via `.gitignore`), never hardcoded.
- **`Decimal` over `float` for prices**: PostgreSQL's `NUMERIC` type (returned
  as Python `Decimal`) avoids floating-point rounding issues that would be
  inappropriate for financial data.

## Example Output

```
=== Pipeline run started: 2026-09-09 12:06:55 ===

--- AAPL ---
Inserted 100 row(s) submitted (0 new, 100 skipped as duplicates).
ALERT: AAPL moved down 1.17% on 2026-09-08 (close: 316.22)

--- MSFT ---
Inserted 100 row(s) submitted (0 new, 100 skipped as duplicates).
ALERT: MSFT moved down 1.15% on 2026-09-08 (close: 493.95)

=== Pipeline run finished: 2026-09-09 12:07:01 ===
```

![Alt Text](images\alerts.png)
![Alt Text](images\price_data.png)

## Possible Future Improvements

- Move from a manual/`schedule`-based loop to a proper scheduler (e.g. Airflow)
  for production-grade orchestration.
- Move secrets from `.env` to a proper secrets manager for production use.
- Add more tickers and a simple dashboard (e.g. Streamlit) to visualize
  stored data over time.
- Add volume-spike detection as a second alert type, alongside price change.
