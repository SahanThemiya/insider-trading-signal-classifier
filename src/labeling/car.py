import pandas as pd

from src.data.trading_calendar import snap_to_trading_day, trading_days_after


def _close_on(bars: pd.DataFrame, date: pd.Timestamp) -> float:
    dates = bars.index.tz_localize(None).normalize()
    return bars.loc[dates == date, "close"].iloc[0]


def cumulative_abnormal_return(
    stock_bars: pd.DataFrame,
    benchmark_bars: pd.DataFrame,
    trade_date: pd.Timestamp,
    horizon: int = 30,
) -> float:
    """Forward CAR: stock return minus benchmark return over `horizon` trading days."""
    trade_date = snap_to_trading_day(trade_date)
    end_date = trading_days_after(trade_date, horizon)

    stock_return = _close_on(stock_bars, end_date) / _close_on(stock_bars, trade_date) - 1
    benchmark_return = _close_on(benchmark_bars, end_date) / _close_on(benchmark_bars, trade_date) - 1

    return stock_return - benchmark_return