-- schema.sql
-- Run this once against your Postgres database to set up the tables.
-- e.g.: psql -h <host> -U <user> -d market_pipeline -f schema.sql

CREATE TABLE IF NOT EXISTS price_data (
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    ts TIMESTAMP NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    inserted_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (ticker, ts)
);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    message TEXT NOT NULL,
    triggered_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_price_data_ticker_ts
    ON price_data (ticker, ts DESC);
