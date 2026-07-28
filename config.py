import os
from dotenv import load_dotenv

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BENCHMARK_TICKER = "SPY"

TICKERS = ["XOM", "CVX", "COP", "MPC", "LMT", "RTX", "PLTR", "LDOS", "UAL", "FDX", "DAL"]

SEC_USER_AGENT = os.getenv("SEC_USER_AGENT")