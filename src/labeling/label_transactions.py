import pandas as pd


def apply_10b5_1_labels(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["label"] = float("nan")
    df.loc[df["is_10b5_1"], "label"] = 0
    return df


def derive_thresholds(car: pd.Series, lower_q: float = 0.15, upper_q: float = 0.85) -> tuple[float, float]:
    return car.quantile(lower_q), car.quantile(upper_q)


def apply_car_labels(df: pd.DataFrame, lower: float, upper: float) -> pd.DataFrame:
    df = df.copy()
    unlabeled = df["label"].isna()
    is_buy_signal = (df["transaction_code"] == "P") & (df["car"] > upper)
    is_sell_signal = (df["transaction_code"] == "S") & (df["car"] < lower)

    df.loc[unlabeled & (is_buy_signal | is_sell_signal), "label"] = 2
    df.loc[unlabeled & df["car"].notna() & ~(is_buy_signal | is_sell_signal), "label"] = 1
    return df