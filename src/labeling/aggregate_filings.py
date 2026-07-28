import pandas as pd


def _collapse(group: pd.DataFrame) -> pd.Series:
    total_shares = group["shares"].sum()
    weighted_price = (group["shares"] * group["price"]).sum() / total_shares if total_shares else 0.0
    last = group.sort_values("row_index").iloc[-1]

    return pd.Series({
        "ticker": last["ticker"],
        "owner_name": last["owner_name"],
        "title": last["title"],
        "is_officer": last["is_officer"],
        "is_director": last["is_director"],
        "transaction_date": last["transaction_date"],
        "transaction_code": last["transaction_code"],
        "shares": total_shares,
        "price": weighted_price,
        "acquired_disposed": last["acquired_disposed"],
        "shares_owned_after": last["shares_owned_after"],
        "is_10b5_1": last["is_10b5_1"],
        "car": last["car"],
        "label": last["label"],
    })


def aggregate_by_filing(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["accession_number", "direct_or_indirect"], dropna=False)
        .apply(_collapse, include_groups=False)
        .reset_index()
    )