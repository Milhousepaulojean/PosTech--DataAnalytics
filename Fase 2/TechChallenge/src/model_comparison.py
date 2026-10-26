from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "prepared"
RESULTS_DIR = BASE_DIR / "results"


def load_prepared_data():
    train = pd.read_csv(DATA_DIR / "train_prepared.csv", index_col=0)
    val = pd.read_csv(DATA_DIR / "validation_prepared.csv", index_col=0)
    return train, val


def build_models():
    return {
        "baseline_majority": DummyClassifier(strategy="most_frequent"),
        "logreg_balanced": LogisticRegression(
            max_iter=4000,
            class_weight="balanced",
            random_state=42,
            C=1.0,
        ),
        "random_forest_balanced": RandomForestClassifier(
            n_estimators=500,
            random_state=42,
            class_weight="balanced_subsample",
            min_samples_leaf=3,
            n_jobs=-1,
        ),
        "hist_gb": HistGradientBoostingClassifier(
            max_depth=5,
            learning_rate=0.05,
            max_iter=300,
            random_state=42,
            l2_regularization=0.0,
        ),
    }


def evaluate_model(model, X_train, y_train, X_val, y_val):
    model.fit(X_train, y_train)
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_val)[:, 1]
    else:
        proba = model.decision_function(X_val)

    pred = model.predict(X_val)

    metrics = {
        "accuracy": accuracy_score(y_val, pred),
        "balanced_accuracy": balanced_accuracy_score(y_val, pred),
        "precision": precision_score(y_val, pred, zero_division=0),
        "recall": recall_score(y_val, pred, zero_division=0),
        "f1": f1_score(y_val, pred, zero_division=0),
        "roc_auc": roc_auc_score(y_val, proba),
        "average_precision": average_precision_score(y_val, proba),
        "confusion_matrix": confusion_matrix(y_val, pred).tolist(),
    }
    return metrics


def main():
    train_df, val_df = load_prepared_data()
    target_col = "target"
    feature_cols = [col for col in train_df.columns if col != target_col]

    X_train = train_df[feature_cols]
    y_train = train_df[target_col]
    X_val = val_df[feature_cols]
    y_val = val_df[target_col]

    results = {}
    for name, model in build_models().items():
        metrics = evaluate_model(model, X_train, y_train, X_val, y_val)
        results[name] = metrics

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with (RESULTS_DIR / "model_validation_metrics.json").open(
        "w", encoding="utf-8"
    ) as fp:
        json.dump(results, fp, indent=2)

    ranking = sorted(
        results.items(),
        key=lambda item: (
            item[1]["f1"],
            item[1]["average_precision"],
            item[1]["roc_auc"],
        ),
        reverse=True,
    )

    print("Validation model ranking:")
    for rank, (name, metrics) in enumerate(ranking, start=1):
        print(
            f"{rank}. {name}: f1={metrics['f1']:.4f}, "
            f"precision={metrics['precision']:.4f}, recall={metrics['recall']:.4f}, "
            f"roc_auc={metrics['roc_auc']:.4f}, avg_precision={metrics['average_precision']:.4f}"
        )

    print(f"Saved metrics to: {RESULTS_DIR / 'model_validation_metrics.json'}")


if __name__ == "__main__":
    main()
