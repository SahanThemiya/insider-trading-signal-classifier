import pandas as pd
import pandas_market_calendars as mcal

from src.labeling.car import cumulative_abnormal_return

_NYSE = mcal.get_calendar("NYSE")


def _synthetic_bars(base_price: float, schedule: pd.DatetimeIndex) -> pd.DataFrame:
    close = pd.Series(range(int(base_price), int(base_price) + len(schedule)), index=schedule, dtype=float)
    bars = pd.DataFrame({"close": close})
    bars.index = bars.index.tz_localize("UTC") + pd.Timedelta(hours=5)
    return bars


def test_cumulative_abnormal_return():
    schedule = _NYSE.schedule(start_date="2024-01-01", end_date="2024-06-01").index
    stock_bars = _synthetic_bars(100, schedule)
    benchmark_bars = _synthetic_bars(200, schedule)

    trade_date = schedule[10]
    expected_stock_ret = stock_bars["close"].iloc[40] / stock_bars["close"].iloc[10] - 1
    expected_bench_ret = benchmark_bars["close"].iloc[40] / benchmark_bars["close"].iloc[10] - 1
    expected_car = expected_stock_ret - expected_bench_ret

    result = cumulative_abnormal_return(stock_bars, benchmark_bars, trade_date, horizon=30)

    assert abs(result - expected_car) < 1e-9