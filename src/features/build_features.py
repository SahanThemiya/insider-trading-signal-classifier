import pandas as pd


def ownership_change_pct(df: pd.DataFrame) -> pd.Series:
    signed_shares = df["shares"].where(df["acquired_disposed"] == "A", -df["shares"])
    shares_before = (df["shares_owned_after"] - signed_shares).astype(float)
    shares_before = shares_before.replace(0, float("nan"))
    return signed_shares / shares_before

def trade_size_intensity(df: pd.DataFrame) -> pd.Series:
    ordered = df.sort_values(["owner_name", "transaction_date"])
    dollar_value = ordered["shares"] * ordered["price"]
    prior_median = dollar_value.groupby(ordered["owner_name"]).transform(
        lambda s: s.expanding().median().shift(1)
    )
    return (dollar_value / prior_median).reindex(df.index)


def insider_clustering(df: pd.DataFrame, window_days: int = 7) -> pd.Series:
    ordered = df.sort_values("transaction_date")
    counts = []
    for _, row in ordered.iterrows():
        window_start = row["transaction_date"] - pd.Timedelta(days=window_days)
        mask = (
            (ordered["ticker"] == row["ticker"])
            & (ordered["owner_name"] != row["owner_name"])
            & (ordered["transaction_date"] >= window_start)
            & (ordered["transaction_date"] < row["transaction_date"])
        )
        counts.append(ordered.loc[mask, "owner_name"].nunique())
    return pd.Series(counts, index=ordered.index).reindex(df.index)


def pre_trade_volatility(stock_bars: pd.DataFrame, trade_date: pd.Timestamp, window: int = 14) -> float:
    dates = stock_bars.index.tz_localize(None).normalize()
    prior = stock_bars.loc[dates < trade_date].sort_index()
    returns = prior["close"].pct_change().dropna().tail(window)
    return returns.std()