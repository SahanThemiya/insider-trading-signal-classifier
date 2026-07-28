import pandas as pd

from src.data.alpaca_client import fetch_daily_bars
from src.features.build_features import (
    insider_clustering,
    ownership_change_pct,
    pre_trade_volatility,
    trade_size_intensity,
)

INPUT_PATH = "data/processed/labeled_transactions.csv"
OUTPUT_PATH = "data/processed/features.csv"
VOLATILITY_WINDOW = 14

df = pd.read_csv(INPUT_PATH, parse_dates=["transaction_date"])

df["ownership_change_pct"] = ownership_change_pct(df)
df["trade_size_intensity"] = trade_size_intensity(df)
df["insider_clustering"] = insider_clustering(df)

df["pre_trade_volatility"] = float("nan")
for ticker, group in df.groupby("ticker"):
    start = group["transaction_date"].min() - pd.Timedelta(days=VOLATILITY_WINDOW * 3)
    end = group["transaction_date"].max()

    stock_bars = fetch_daily_bars(ticker, start, end)

    for idx, row in group.iterrows():
        try:
            df.loc[idx, "pre_trade_volatility"] = pre_trade_volatility(
                stock_bars, row["transaction_date"], window=VOLATILITY_WINDOW
            )
        except Exception as e:
            print(f"Skipped volatility for {ticker} {row['transaction_date'].date()}: {e}")

df.to_csv(OUTPUT_PATH, index=False)
print(df[["ownership_change_pct", "trade_size_intensity", "insider_clustering", "pre_trade_volatility"]].describe())
print(f"Saved {len(df)} rows with features to {OUTPUT_PATH}")