import pandas as pd

from src.features.build_features import (
    insider_clustering,
    ownership_change_pct,
    pre_trade_volatility,
    trade_size_intensity,
)


def test_ownership_change_pct_buy_and_sell():
    df = pd.DataFrame([
        {"shares": 50, "shares_owned_after": 1050, "acquired_disposed": "A"},
        {"shares": 300, "shares_owned_after": 700, "acquired_disposed": "D"},
    ])
    result = ownership_change_pct(df)

    assert abs(result.iloc[0] - 0.05) < 1e-9
    assert abs(result.iloc[1] - (-0.30)) < 1e-9


def test_ownership_change_pct_full_divestiture_is_negative_one():
    df = pd.DataFrame([{"shares": 1000, "shares_owned_after": 0, "acquired_disposed": "D"}])
    result = ownership_change_pct(df)

    assert abs(result.iloc[0] - (-1.0)) < 1e-9


def test_ownership_change_pct_first_ever_grant_stays_numeric():
    df = pd.DataFrame([
        {"shares": 500, "shares_owned_after": 500, "acquired_disposed": "A"},
        {"shares": 50, "shares_owned_after": 1050, "acquired_disposed": "A"},
    ])
    result = ownership_change_pct(df)

    assert result.dtype == "float64"
    assert pd.isna(result.iloc[0])
    assert abs(result.iloc[1] - 0.05) < 1e-9


def test_trade_size_intensity_uses_only_prior_trades():
    df = pd.DataFrame([
        {"owner_name": "Doe", "transaction_date": pd.Timestamp("2026-01-01"), "shares": 100, "price": 10.0},
        {"owner_name": "Doe", "transaction_date": pd.Timestamp("2026-02-01"), "shares": 200, "price": 10.0},
        {"owner_name": "Doe", "transaction_date": pd.Timestamp("2026-03-01"), "shares": 400, "price": 10.0},
    ])
    result = trade_size_intensity(df)

    assert pd.isna(result.iloc[0])
    assert abs(result.iloc[1] - (2000 / 1000)) < 1e-9
    assert abs(result.iloc[2] - (4000 / 1500)) < 1e-9


def test_insider_clustering_trailing_window_only():
    df = pd.DataFrame([
        {"ticker": "XOM", "owner_name": "A", "transaction_date": pd.Timestamp("2026-01-01")},
        {"ticker": "XOM", "owner_name": "B", "transaction_date": pd.Timestamp("2026-01-05")},
        {"ticker": "XOM", "owner_name": "C", "transaction_date": pd.Timestamp("2026-01-20")},
        {"ticker": "CVX", "owner_name": "D", "transaction_date": pd.Timestamp("2026-01-05")},
    ])
    result = insider_clustering(df, window_days=7)

    assert result.iloc[0] == 0
    assert result.iloc[1] == 1
    assert result.iloc[2] == 0
    assert result.iloc[3] == 0


def test_pre_trade_volatility_excludes_trade_date_itself():
    dates = pd.date_range("2026-01-01", periods=20, freq="B")
    closes = pd.Series(range(100, 120), index=dates, dtype=float)
    bars = pd.DataFrame({"close": closes})

    trade_date = dates[15]
    result = pre_trade_volatility(bars, trade_date, window=14)
    expected = closes.loc[:trade_date].iloc[:-1].pct_change().dropna().tail(14).std()

    assert abs(result - expected) < 1e-9