import pandas as pd
from transform import raw_to_dataframe, compute_daily_change_pct


def make_fake_raw_data():
    return {
        "Meta Data": {"2. Symbol": "TEST"},
        "Time Series (Daily)": {
            "2026-09-03": {
                "1. open": "100.00", "2. high": "105.00",
                "3. low": "99.00", "4. close": "102.00", "5. volume": "1000",
            },
            "2026-09-02": {
                "1. open": "98.00", "2. high": "101.00",
                "3. low": "97.50", "4. close": "100.00", "5. volume": "800",
            },
            "2026-09-01": {
                "1. open": "95.00", "2. high": "99.00",
                "3. low": "94.00", "4. close": "98.00", "5. volume": "600",
            },
        },
    }


def test_raw_to_dataframe_basic_shape():
    df = raw_to_dataframe(make_fake_raw_data(), "TEST")

    assert len(df) == 3, f"Expected 3 rows, got {len(df)}"
    assert list(df.columns) == ["ticker", "ts", "open", "high", "low", "close", "volume"], \
        f"Unexpected columns: {list(df.columns)}"
    assert (df["ticker"] == "TEST").all(), "Ticker column not set correctly on all rows"
    print("test_raw_to_dataframe_basic_shape passed")


def test_raw_to_dataframe_sorted_ascending():
    df = raw_to_dataframe(make_fake_raw_data(), "TEST")

    assert df["ts"].is_monotonic_increasing, "Rows are not sorted oldest-to-newest"
    assert df.iloc[0]["ts"] == pd.Timestamp("2026-09-01"), "First row should be the earliest date"
    print("test_raw_to_dataframe_sorted_ascending passed")


def test_raw_to_dataframe_types_are_numeric():
    df = raw_to_dataframe(make_fake_raw_data(), "TEST")

    for col in ["open", "high", "low", "close", "volume"]:
        assert pd.api.types.is_numeric_dtype(df[col]), \
            f"Column '{col}' is not numeric (got {df[col].dtype})"
    print("test_raw_to_dataframe_types_are_numeric passed")


def test_compute_daily_change_pct_known_value():
    df = raw_to_dataframe(make_fake_raw_data(), "TEST")
    df = compute_daily_change_pct(df)

    day2_change = df.iloc[1]["change_pct"]
    day3_change = df.iloc[2]["change_pct"]

    assert abs(day2_change - 2.0408) < 0.01, f"Day 2 change wrong: got {day2_change}"
    assert abs(day3_change - 2.0) < 0.01, f"Day 3 change wrong: got {day3_change}"
    assert pd.isna(df.iloc[0]["change_pct"]), "First row should have NaN change (no prior day)"
    print("test_compute_daily_change_pct_known_value passed")


def test_raw_to_dataframe_missing_key_raises():
    bad_data = {"Meta Data": {}}  
    try:
        raw_to_dataframe(bad_data, "TEST")
        assert False, "Expected a ValueError for missing 'Time Series (Daily)' key"
    except ValueError:
        pass 
    print("test_raw_to_dataframe_missing_key_raises passed")


if __name__ == "__main__":
    test_raw_to_dataframe_basic_shape()
    test_raw_to_dataframe_sorted_ascending()
    test_raw_to_dataframe_types_are_numeric()
    test_compute_daily_change_pct_known_value()
    test_raw_to_dataframe_missing_key_raises()
    print("\nAll tests passed!")
