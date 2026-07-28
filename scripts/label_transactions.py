import pandas as pd
from src.labeling.aggregate_filings import aggregate_by_filing

from config import BENCHMARK_TICKER
from src.data.alpaca_client import fetch_daily_bars
from src.labeling.car import cumulative_abnormal_return
from src.labeling.label_transactions import apply_10b5_1_labels, apply_car_labels, derive_thresholds

HORIZON = 30
INPUT_PATH = "data/raw/form4_transactions.csv"
OUTPUT_PATH = "data/processed/labeled_transactions.csv"

df = pd.read_csv(INPUT_PATH, parse_dates=["transaction_date"])
df = df[df["transaction_code"].isin(["P", "S"])].reset_index(drop=True)

cutoff = pd.Timestamp.today() - pd.Timedelta(days=HORIZON * 2)
df = df[df["transaction_date"] <= cutoff].reset_index(drop=True)

df = apply_10b5_1_labels(df)
df["car"] = float("nan")

to_score = df[df["label"].isna()]
for ticker, group in to_score.groupby("ticker"):
    start = group["transaction_date"].min() - pd.Timedelta(days=10)
    end = group["transaction_date"].max() + pd.Timedelta(days=HORIZON * 2)

    stock_bars = fetch_daily_bars(ticker, start, end)
    benchmark_bars = fetch_daily_bars(BENCHMARK_TICKER, start, end)

    for idx, row in group.iterrows():
        try:
            df.loc[idx, "car"] = cumulative_abnormal_return(
                stock_bars, benchmark_bars, row["transaction_date"], horizon=HORIZON
            )
        except Exception as e:
            print(f"Skipped CAR for {ticker} {row['transaction_date'].date()}: {e}")

lower, upper = derive_thresholds(df.loc[df["car"].notna(), "car"])
print(f"CAR thresholds — lower: {lower:.4%}, upper: {upper:.4%}")

df = apply_car_labels(df, lower, upper)
df = df[df["label"].notna()].copy()
df["label"] = df["label"].astype(int)
df = aggregate_by_filing(df)

df.to_csv(OUTPUT_PATH, index=False)
print(df["label"].value_counts())
print(f"Saved {len(df)} labeled rows to {OUTPUT_PATH}")