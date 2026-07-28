import numpy as np
import pandas as pd

N = 5000
SEED = 42
OUTPUT_PATH = "data/synthetic/synthetic_features.csv"

rng = np.random.default_rng(SEED)

dates = pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 1300, N), unit="D")
is_buy = rng.choice([0, 1], size=N, p=[0.85, 0.15])
is_officer = rng.choice([0, 1], size=N, p=[0.5, 0.5])
is_director = rng.choice([0, 1], size=N, p=[0.5, 0.5])

trade_size_intensity = rng.exponential(2.0, N)
insider_clustering = rng.poisson(0.8, N)
pre_trade_volatility = rng.uniform(0.005, 0.09, N)
ownership_change_pct = rng.normal(-0.1, 0.4, N)

size_z = (trade_size_intensity - trade_size_intensity.mean()) / trade_size_intensity.std()
cluster_z = (insider_clustering - insider_clustering.mean()) / (insider_clustering.std() + 1e-9)
latent_score = 1.4 * size_z + 1.0 * cluster_z + rng.normal(0, 1.5, N)
threshold = np.quantile(latent_score, 0.88)
label = np.where(latent_score > threshold, 2, 1)

df = pd.DataFrame({
    "transaction_date": dates,
    "transaction_code": np.where(is_buy == 1, "P", "S"),
    "ownership_change_pct": ownership_change_pct,
    "trade_size_intensity": trade_size_intensity,
    "insider_clustering": insider_clustering,
    "pre_trade_volatility": pre_trade_volatility,
    "is_officer": is_officer.astype(bool),
    "is_director": is_director.astype(bool),
    "label": label,
})

missing_mask = rng.random(N) < 0.25
df.loc[missing_mask, "trade_size_intensity"] = np.nan

df.to_csv(OUTPUT_PATH, index=False)
print(f"Generated {len(df)} synthetic rows -> {OUTPUT_PATH}")
print(df["label"].value_counts())