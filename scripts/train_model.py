import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from src.modeling.prepare_dataset import build_feature_matrix, impute, select_stage_b_population, time_based_split

INPUT_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/processed/features.csv"
TEST_FRAC = 0.25

print(f"Using dataset: {INPUT_PATH}")


def print_threshold_table(y_test, y_proba, model_name, step=0.05):
    print(f"\n{model_name} — precision/recall at fixed thresholds:")
    print(f"{'threshold':>10} {'precision':>10} {'recall':>10} {'flagged':>10}")
    for t in np.arange(0.05, 0.95, step):
        preds = (y_proba >= t).astype(int)
        tp = ((preds == 1) & (y_test == 1)).sum()
        fp = ((preds == 1) & (y_test == 0)).sum()
        fn = ((preds == 0) & (y_test == 1)).sum()
        precision = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
        recall = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
        print(f"{t:>10.2f} {precision:>10.2f} {recall:>10.2f} {preds.sum():>10d}")


df = pd.read_csv(INPUT_PATH, parse_dates=["transaction_date"])
df = select_stage_b_population(df)

train_df, test_df = time_based_split(df, test_frac=TEST_FRAC)

X_train_raw = build_feature_matrix(train_df)
X_test_raw = build_feature_matrix(test_df)

fill_values = {
    "trade_size_intensity": X_train_raw["trade_size_intensity"].median(),
    "ownership_change_pct": X_train_raw["ownership_change_pct"].median(),
}
X_train = impute(X_train_raw, fill_values)
X_test = impute(X_test_raw, fill_values)

y_train = (train_df["label"] == 2).astype(int)
y_test = (test_df["label"] == 2).astype(int)

print(f"Train: {len(X_train)} rows, {y_train.sum()} opportunistic")
print(f"Test:  {len(X_test)} rows, {y_test.sum()} opportunistic")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

logreg = LogisticRegression(class_weight="balanced", max_iter=1000)
logreg.fit(X_train_scaled, y_train)
print("\nLogistic Regression:")
print(classification_report(y_test, logreg.predict(X_test_scaled), target_names=["Noise", "Opportunistic"]))
print_threshold_table(y_test, logreg.predict_proba(X_test_scaled)[:, 1], "Logistic Regression")

pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
xgb = XGBClassifier(
    scale_pos_weight=pos_weight,
    eval_metric="logloss",
    n_estimators=50,
    max_depth=3,
    learning_rate=0.1,
    min_child_weight=5,
)
xgb.fit(X_train, y_train)
print("\nXGBoost:")
print(classification_report(y_test, xgb.predict(X_test), target_names=["Noise", "Opportunistic"]))
print_threshold_table(y_test, xgb.predict_proba(X_test)[:, 1], "XGBoost")