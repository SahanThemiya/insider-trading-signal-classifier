import pandas as pd
import pandas_market_calendars as mcal

_NYSE = mcal.get_calendar("NYSE")


def _schedule(start: pd.Timestamp, end: pd.Timestamp) -> pd.DatetimeIndex:
    return _NYSE.schedule(start_date=start, end_date=end).index


def snap_to_trading_day(date: pd.Timestamp) -> pd.Timestamp:
    """Snap a date to itself or the next valid NYSE trading day."""
    schedule = _schedule(date, date + pd.Timedelta(days=7))
    return schedule[schedule >= date][0]


def trading_window(trade_date: pd.Timestamp, days_before: int = 30, days_after: int = 60) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return calendar start/end dates spanning N trading days before/after trade_date."""
    trade_date = snap_to_trading_day(trade_date)
    schedule = _schedule(
        trade_date - pd.Timedelta(days=days_before * 2 + 10),
        trade_date + pd.Timedelta(days=days_after * 2 + 10),
    )
    anchor_idx = schedule.searchsorted(trade_date)
    start_idx = max(anchor_idx - days_before, 0)
    end_idx = min(anchor_idx + days_after, len(schedule) - 1)
    return schedule[start_idx], schedule[end_idx]


def trading_days_after(trade_date: pd.Timestamp, n: int) -> pd.Timestamp:
    """Return the date exactly n trading days after trade_date."""
    trade_date = snap_to_trading_day(trade_date)
    schedule = _schedule(trade_date, trade_date + pd.Timedelta(days=n * 2 + 10))
    anchor_idx = schedule.searchsorted(trade_date)
    return schedule[min(anchor_idx + n, len(schedule) - 1)]
