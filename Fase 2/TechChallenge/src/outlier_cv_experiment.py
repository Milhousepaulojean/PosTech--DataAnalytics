from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "WineQT.csv"
RESULTS_DIR = BASE_DIR / "results"
OUTPUT_PATH = RESULTS_DIR / "outlier_cv_experiment.json"

TARGET_CUTOFF = 7
RANDOM_STATE = 42


class IQRClipper(BaseEstimator, TransformerMixin):
    """Clip values by IQR limits learned on each training fold."""

    def __init__(self, factor: float = 1.5):
        self.factor = factor

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X)
        q1 = X_df.quantile(0.25)
        q3 = X_df.quantile(0.75)
        iqr = q3 - q1
        self.lower_bounds_ = q1 - self.factor * iqr
        self.upper_bounds_ = q3 + self.factor * iqr
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X).copy()
        return X_df.clip(lower=self.lower_bounds_, upper=self.upper_bounds_, axis=1)


class QuantileClipper(BaseEstimator, TransformerMixin):
    """Clip values using training-fold quantiles (winsorization style)."""

    def __init__(self, lower_quantile: float = 0.01, upper_quantile: float = 0.99):
        self.lower_quantile = lower_quantile
        self.upper_quantile = upper_quantile

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X)
        self.lower_bounds_ = X_df.quantile(self.lower_quantile)
        self.upper_bounds_ = X_df.quantile(self.upper_quantile)
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X).copy()
        return X_df.clip(lower=self.lower_bounds_, upper=self.upper_bounds_, axis=1)


def load_data():
    df = pd.read_csv(DATA_PATH)
    df["target"] = (df["quality"] >= TARGET_CUTOFF).astype(int)

    features = [
        col for col in df.columns if col not in {"Id", "quality", "target"}
    ]
    X = df[features]
    y = df["target"]
    return X, y, features


def build_pipeline(feature_columns, outlier_transformer=None):
    numeric_steps = []
    if outlier_transformer is not None:
        numeric_steps.append(("outlier", outlier_transformer))
    numeric_steps.append(("scaler", StandardScaler()))

    numeric_pipeline = Pipeline(steps=numeric_steps)

    preprocessor = ColumnTransformer(
        transformers=[("num", numeric_pipeline, feature_columns)],
        remainder="drop",
    )

    model = RandomForestClassifier(
        n_estimators=500,
        random_state=RANDOM_STATE,
        class_weight="balanced_subsample",
        min_samples_leaf=3,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )


def summarize_cv(cv_result: dict[str, np.ndarray]) -> dict[str, dict[str, float]]:
    metric_keys = {
        "f1": "test_f1",
        "recall": "test_recall",
        "precision": "test_precision",
        "roc_auc": "test_roc_auc",
        "average_precision": "test_average_precision",
    }

    summary = {}
    for output_name, cv_key in metric_keys.items():
        values = cv_result[cv_key]
        summary[output_name] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values, ddof=1)),
            "fold_scores": [float(v) for v in values],
        }
    return summary


def build_delta_vs_baseline(
    baseline_summary: dict[str, dict[str, float]],
    candidate_summary: dict[str, dict[str, float]],
) -> dict[str, float]:
    deltas = {}
    for metric in ["f1", "recall", "precision", "roc_auc", "average_precision"]:
        deltas[f"delta_{metric}_mean"] = (
            candidate_summary[metric]["mean"] - baseline_summary[metric]["mean"]
        )
    return deltas


def main():
    X, y, features = load_data()

    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scoring = ["f1", "recall", "precision", "roc_auc", "average_precision"]

    strategies = {
        "baseline_sem_tratamento": None,
        "iqr_clipping_1_5": IQRClipper(factor=1.5),
        "winsor_quantil_1_99": QuantileClipper(0.01, 0.99),
    }

    cv_summaries = {}
    for strategy_name, outlier_transformer in strategies.items():
        pipeline = build_pipeline(features, outlier_transformer=outlier_transformer)
        cv_result = cross_validate(
            pipeline,
            X,
            y,
            scoring=scoring,
            cv=splitter,
            n_jobs=-1,
            return_train_score=False,
            error_score="raise",
        )
        cv_summaries[strategy_name] = summarize_cv(cv_result)

    baseline = cv_summaries["baseline_sem_tratamento"]
    deltas = {
        name: build_delta_vs_baseline(baseline, summary)
        for name, summary in cv_summaries.items()
        if name != "baseline_sem_tratamento"
    }

    ranking = sorted(
        cv_summaries.items(),
        key=lambda item: (
            item[1]["f1"]["mean"],
            item[1]["average_precision"]["mean"],
            item[1]["roc_auc"]["mean"],
        ),
        reverse=True,
    )

    payload = {
        "config": {
            "target_definition": "quality >= 7",
            "cv": "StratifiedKFold(n_splits=5, shuffle=True, random_state=42)",
            "model": "RandomForestClassifier(class_weight='balanced_subsample', n_estimators=500, min_samples_leaf=3)",
            "metrics": ["f1", "recall", "precision", "roc_auc", "average_precision"],
            "class_imbalance_note": "Classe positiva minoritaria; decisao nao baseada em acuracia isolada.",
        },
        "strategy_results": cv_summaries,
        "delta_vs_baseline": deltas,
        "ranking_by_f1_ap_roc_auc": [name for name, _ in ranking],
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)

    print("=== Etapa 2 - Validacao experimental de outliers (CV) ===")
    for name, metrics in ranking:
        print(
            f"{name}: "
            f"F1={metrics['f1']['mean']:.4f} (+/- {metrics['f1']['std']:.4f}), "
            f"Recall={metrics['recall']['mean']:.4f}, "
            f"Precision={metrics['precision']['mean']:.4f}, "
            f"ROC-AUC={metrics['roc_auc']['mean']:.4f}, "
            f"AP={metrics['average_precision']['mean']:.4f}"
        )

    print(f"\nResultado salvo em: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
