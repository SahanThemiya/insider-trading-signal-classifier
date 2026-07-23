import pandas as pd

from src.data.trading_calendar import snap_to_trading_day, trading_days_after, trading_window


def test_snap_to_trading_day_weekend():
    saturday = pd.Timestamp("2024-03-02")
    assert snap_to_trading_day(saturday) == pd.Timestamp("2024-03-04")


def test_trading_window_bounds():
    trade_date = pd.Timestamp("2024-03-01")
    start, end = trading_window(trade_date, days_before=30, days_after=60)
    assert start < trade_date < end


def test_trading_days_after_count():
    trade_date = pd.Timestamp("2024-03-01")
    target = trading_days_after(trade_date, 30)
    assert target > trade_date
