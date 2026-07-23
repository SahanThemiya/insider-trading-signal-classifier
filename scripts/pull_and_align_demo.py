import pandas as pd

from config import BENCHMARK_TICKER
from src.data.alpaca_client import fetch_daily_bars
from src.data.trading_calendar import trading_window

TICKER = "AAPL"
TRADE_DATE = pd.Timestamp("2024-03-01")

start, end = trading_window(TRADE_DATE, days_before=30, days_after=60)

stock_bars = fetch_daily_bars(TICKER, start, end)
benchmark_bars = fetch_daily_bars(BENCHMARK_TICKER, start, end)

print(f"Window: {start.date()} -> {end.date()}")
print(stock_bars[["close"]].head())
print(benchmark_bars[["close"]].head())
