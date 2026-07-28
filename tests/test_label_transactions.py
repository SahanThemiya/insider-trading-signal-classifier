import pandas as pd

from src.labeling.label_transactions import apply_10b5_1_labels, apply_car_labels, derive_thresholds


def _row(transaction_code, is_10b5_1, car=None):
    return {"transaction_code": transaction_code, "is_10b5_1": is_10b5_1, "car": car}


def test_apply_10b5_1_labels():
    df = pd.DataFrame([_row("P", True), _row("S", False)])
    result = apply_10b5_1_labels(df)

    assert result.loc[0, "label"] == 0
    assert pd.isna(result.loc[1, "label"])


def test_derive_thresholds():
    car = pd.Series(range(100))
    lower, upper = derive_thresholds(car, lower_q=0.15, upper_q=0.85)

    assert lower == car.quantile(0.15)
    assert upper == car.quantile(0.85)


def test_apply_car_labels_buy_and_sell_signals():
    df = pd.DataFrame([
        _row("P", False, car=0.20),
        _row("S", False, car=-0.20),
        _row("P", False, car=0.01),
        _row("S", False, car=0.20),
        _row("P", False, car=-0.20),
    ])
    df["label"] = float("nan")

    result = apply_car_labels(df, lower=-0.10, upper=0.10)

    assert result.loc[0, "label"] == 2
    assert result.loc[1, "label"] == 2
    assert result.loc[2, "label"] == 1
    assert result.loc[3, "label"] == 1
    assert result.loc[4, "label"] == 1


def test_apply_car_labels_skips_already_labeled_rows():
    df = pd.DataFrame([_row("P", True, car=0.50)])
    df["label"] = 0.0

    result = apply_car_labels(df, lower=-0.10, upper=0.10)

    assert result.loc[0, "label"] == 0