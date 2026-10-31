from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "WineQT.csv"
RESULTS_DIR = BASE_DIR / "results"
OUTPUT_PATH = RESULTS_DIR / "threshold_test_evaluation.json"

RANDOM_STATE = 42
TARGET_CUTOFF = 7


def load_split_data():
    df = pd.read_csv(DATA_PATH)
    df["target"] = (df["quality"] >= TARGET_CUTOFF).astype(int)

    features = [col for col in df.columns if col not in {"quality", "target", "Id"}]
    X = df[features]
    y = df["target"]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=y_temp,
    )

    return X_train, y_train, X_val, y_val, X_test, y_test


def evaluate_threshold(y_true, probabilities, threshold):
    pred = (probabilities >= threshold).astype(int)
    return {
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(y_true, pred)),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
    }


def main():
    X_train, y_train, X_val, y_val, X_test, y_test = load_split_data()

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(
        n_estimators=500,
        random_state=RANDOM_STATE,
        class_weight="balanced_subsample",
        min_samples_leaf=3,
        n_jobs=-1,
    )
    model.fit(X_train_scaled, y_train)

    proba_test = model.predict_proba(X_test_scaled)[:, 1]

    thresholds = [0.50, 0.46, 0.42]
    threshold_metrics = {
        f"t_{str(t).replace('.', '_')}": evaluate_threshold(y_test, proba_test, t)
        for t in thresholds
    }

    payload = {
        "config": {
            "target_definition": "quality >= 7",
            "split": "train 70%, validation 15%, test 15% (estratificado)",
            "model": "RandomForestClassifier(class_weight='balanced_subsample', n_estimators=500, min_samples_leaf=3)",
            "threshold_source": "Etapa 3 de validacao cruzada",
            "thresholds_tested": thresholds,
        },
        "probability_metrics": {
            "roc_auc": float(roc_auc_score(y_test, proba_test)),
            "average_precision": float(average_precision_score(y_test, proba_test)),
        },
        "threshold_metrics": threshold_metrics,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)

    print("=== Avaliacao final no teste reservado com limiares da Etapa 3 ===")
    for key, values in threshold_metrics.items():
        print(
            f"{key}: acc={values['accuracy']:.4f}, f1={values['f1']:.4f}, "
            f"recall={values['recall']:.4f}, precision={values['precision']:.4f}"
        )
    print(
        "ROC-AUC={:.4f} | AP={:.4f}".format(
            payload["probability_metrics"]["roc_auc"],
            payload["probability_metrics"]["average_precision"],
        )
    )
    print(f"Resultado salvo em: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
