import pandas as pd

from src.modeling.prepare_dataset import build_feature_matrix, impute, select_stage_b_population, time_based_split


def test_select_stage_b_population_excludes_class_0():
    df = pd.DataFrame({"label": [0, 1, 2, 0, 1]})
    result = select_stage_b_population(df)

    assert list(result["label"]) == [1, 2, 1]


def test_build_feature_matrix_flags_missing_and_encodes_buy():
    df = pd.DataFrame({
        "transaction_code": ["P", "S"],
        "trade_size_intensity": [float("nan"), 2.0],
        "ownership_change_pct": [0.1, -0.2],
        "insider_clustering": [0, 1],
        "pre_trade_volatility": [0.02, 0.03],
        "is_officer": [True, False],
        "is_director": [False, True],
    })
    result = build_feature_matrix(df)

    assert result.loc[0, "is_buy"] == 1
    assert result.loc[1, "is_buy"] == 0
    assert result.loc[0, "trade_size_missing"] == 1
    assert result.loc[1, "trade_size_missing"] == 0


def test_impute_uses_provided_fill_values():
    df = pd.DataFrame({
        "trade_size_intensity": [1.0, float("nan")],
        "ownership_change_pct": [float("nan"), 0.2],
    })
    result = impute(df, {"trade_size_intensity": 5.0, "ownership_change_pct": 9.0})

    assert result.loc[1, "trade_size_intensity"] == 5.0
    assert result.loc[0, "ownership_change_pct"] == 9.0


def test_time_based_split_is_chronological():
    df = pd.DataFrame({
        "transaction_date": pd.date_range("2023-01-01", periods=10),
        "label": range(10),
    })
    train, test = time_based_split(df, test_frac=0.3)

    assert len(train) == 7
    assert len(test) == 3
    assert train["transaction_date"].max() < test["transaction_date"].min()