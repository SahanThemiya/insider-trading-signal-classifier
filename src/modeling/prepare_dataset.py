import pandas as pd

FEATURE_COLUMNS = [
    "ownership_change_pct",
    "trade_size_intensity",
    "insider_clustering",
    "pre_trade_volatility",
    "is_officer",
    "is_director",
    "is_buy",
]


def select_stage_b_population(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["label"].isin([1, 2])].copy()


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["is_buy"] = (df["transaction_code"] == "P").astype(int)
    df["trade_size_missing"] = df["trade_size_intensity"].isna().astype(int)
    return df[FEATURE_COLUMNS + ["trade_size_missing"]]


def impute(df: pd.DataFrame, fill_values: dict) -> pd.DataFrame:
    return df.fillna(fill_values)


def time_based_split(df: pd.DataFrame, date_col: str = "transaction_date", test_frac: float = 0.25):
    ordered = df.sort_values(date_col)
    split_idx = int(len(ordered) * (1 - test_frac))
    return ordered.iloc[:split_idx].copy(), ordered.iloc[split_idx:].copy()