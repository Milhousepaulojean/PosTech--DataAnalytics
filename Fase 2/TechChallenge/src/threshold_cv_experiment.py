from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "WineQT.csv"
RESULTS_DIR = BASE_DIR / "results"
OUTPUT_PATH = RESULTS_DIR / "threshold_cv_experiment.json"

TARGET_CUTOFF = 7
RANDOM_STATE = 42


def load_data():
    df = pd.read_csv(DATA_PATH)
    df["target"] = (df["quality"] >= TARGET_CUTOFF).astype(int)

    features = [
        col for col in df.columns if col not in {"Id", "quality", "target"}
    ]
    X = df[features]
    y = df["target"]
    return X, y


def build_pipeline():
    model = RandomForestClassifier(
        n_estimators=500,
        random_state=RANDOM_STATE,
        class_weight="balanced_subsample",
        min_samples_leaf=3,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("model", model),
        ]
    )


def compute_threshold_metrics(y_true, probabilities, threshold):
    pred = (probabilities >= threshold).astype(int)
    return {
        "threshold": float(threshold),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
    }


def main():
    X, y = load_data()

    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    pipeline = build_pipeline()

    oof_proba = cross_val_predict(
        pipeline,
        X,
        y,
        cv=splitter,
        method="predict_proba",
        n_jobs=-1,
    )[:, 1]

    roc_auc = float(roc_auc_score(y, oof_proba))
    average_precision = float(average_precision_score(y, oof_proba))

    thresholds = np.round(np.arange(0.20, 0.81, 0.02), 2)
    threshold_rows = [compute_threshold_metrics(y, oof_proba, t) for t in thresholds]
    threshold_df = pd.DataFrame(threshold_rows)

    baseline_row = threshold_df.loc[np.isclose(threshold_df["threshold"], 0.50)].iloc[0]

    best_f1_row = threshold_df.sort_values(
        by=["f1", "recall", "precision"], ascending=False
    ).iloc[0]

    tradeoff_rows = threshold_df[
        (threshold_df["recall"] > baseline_row["recall"])
        & (threshold_df["f1"] >= baseline_row["f1"] - 0.01)
    ]
    if tradeoff_rows.empty:
        tradeoff_row = None
    else:
        tradeoff_row = tradeoff_rows.sort_values(
            by=["recall", "f1", "precision"], ascending=False
        ).iloc[0]

    payload = {
        "config": {
            "target_definition": "quality >= 7",
            "cv": "StratifiedKFold(n_splits=5, shuffle=True, random_state=42)",
            "model": "RandomForestClassifier(class_weight='balanced_subsample', n_estimators=500, min_samples_leaf=3)",
            "threshold_grid": [float(t) for t in thresholds],
            "selection_rule": "best_f1_and_tradeoff_recall",
            "class_imbalance_note": "Classe positiva minoritaria; decisao guiada por F1/recall/precision.",
        },
        "global_probability_metrics": {
            "roc_auc": roc_auc,
            "average_precision": average_precision,
        },
        "baseline_threshold_0_50": {
            "threshold": float(baseline_row["threshold"]),
            "f1": float(baseline_row["f1"]),
            "recall": float(baseline_row["recall"]),
            "precision": float(baseline_row["precision"]),
        },
        "best_threshold_by_f1": {
            "threshold": float(best_f1_row["threshold"]),
            "f1": float(best_f1_row["f1"]),
            "recall": float(best_f1_row["recall"]),
            "precision": float(best_f1_row["precision"]),
        },
        "high_recall_tradeoff": None
        if tradeoff_row is None
        else {
            "threshold": float(tradeoff_row["threshold"]),
            "f1": float(tradeoff_row["f1"]),
            "recall": float(tradeoff_row["recall"]),
            "precision": float(tradeoff_row["precision"]),
        },
        "threshold_metrics": threshold_df.to_dict(orient="records"),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)

    print("=== Etapa 3 - Ajuste de limiar por validacao cruzada ===")
    print(
        "Baseline t=0.50: "
        f"F1={payload['baseline_threshold_0_50']['f1']:.4f}, "
        f"Recall={payload['baseline_threshold_0_50']['recall']:.4f}, "
        f"Precision={payload['baseline_threshold_0_50']['precision']:.4f}"
    )
    print(
        "Melhor F1: "
        f"t={payload['best_threshold_by_f1']['threshold']:.2f}, "
        f"F1={payload['best_threshold_by_f1']['f1']:.4f}, "
        f"Recall={payload['best_threshold_by_f1']['recall']:.4f}, "
        f"Precision={payload['best_threshold_by_f1']['precision']:.4f}"
    )

    if payload["high_recall_tradeoff"] is None:
        print("Trade-off de recall: nenhum limiar superou recall com queda de F1 <= 0.01")
    else:
        print(
            "Trade-off de recall: "
            f"t={payload['high_recall_tradeoff']['threshold']:.2f}, "
            f"F1={payload['high_recall_tradeoff']['f1']:.4f}, "
            f"Recall={payload['high_recall_tradeoff']['recall']:.4f}, "
            f"Precision={payload['high_recall_tradeoff']['precision']:.4f}"
        )

    print(f"ROC-AUC (OOF): {roc_auc:.4f} | AP (OOF): {average_precision:.4f}")
    print(f"Resultado salvo em: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
