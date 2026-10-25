from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "WineQT.csv"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "prepared"

TARGET_CUTOFF = 7
RANDOM_STATE = 42


def build_target_column(df: pd.DataFrame, cutoff: int = TARGET_CUTOFF) -> pd.DataFrame:
    """Create the binary target using the current provisional threshold.

    The challenge text suggests quality >= 7 as the high-quality class. This is kept
    as a provisional decision and can be revisited after the data audit is reviewed.
    """
    result = df.copy()
    result["target"] = (result["quality"] >= cutoff).astype(int)
    return result


def prepare_split(df: pd.DataFrame, test_size: float = 0.20, val_size: float = 0.25):
    """Split the data in a leakage-safe order.

    The workflow follows the charter:
    - reserve the final test set for final evaluation
    - create the train/validation split before fitting preprocessing
    - keep transformations fitted on training data only
    """
    y = df["target"]
    train_val, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    train_y = train_val["target"]
    train_df, val_df = train_test_split(
        train_val,
        test_size=val_size,
        random_state=RANDOM_STATE,
        stratify=train_y,
    )

    return train_df, val_df, test_df


def build_preprocessor(feature_columns):
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), feature_columns),
        ],
        remainder="drop",
    )
    return preprocessor


def prepare_modeling_data():
    df = pd.read_csv(DATA_PATH)
    df = build_target_column(df, cutoff=TARGET_CUTOFF)

    feature_columns = [
        column for column in df.columns if column not in {"quality", "target", "Id"}
    ]

    train_df, val_df, test_df = prepare_split(df)

    preprocessor = build_preprocessor(feature_columns)

    X_train = preprocessor.fit_transform(train_df[feature_columns])
    X_val = preprocessor.transform(val_df[feature_columns])
    X_test = preprocessor.transform(test_df[feature_columns])

    train_prepared = pd.DataFrame(X_train, columns=feature_columns, index=train_df.index)
    train_prepared["target"] = train_df["target"].values

    val_prepared = pd.DataFrame(X_val, columns=feature_columns, index=val_df.index)
    val_prepared["target"] = val_df["target"].values

    test_prepared = pd.DataFrame(X_test, columns=feature_columns, index=test_df.index)
    test_prepared["target"] = test_df["target"].values

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    train_prepared.to_csv(OUTPUT_DIR / "train_prepared.csv", index=True)
    val_prepared.to_csv(OUTPUT_DIR / "validation_prepared.csv", index=True)
    test_prepared.to_csv(OUTPUT_DIR / "test_prepared.csv", index=True)

    return {
        "feature_columns": feature_columns,
        "train": train_df,
        "validation": val_df,
        "test": test_df,
        "prepared": {
            "train": train_prepared,
            "validation": val_prepared,
            "test": test_prepared,
        },
        "preprocessor": preprocessor,
    }


if __name__ == "__main__":
    result = prepare_modeling_data()
    print(f"training rows: {len(result['train'])}")
    print(f"validation rows: {len(result['validation'])}")
    print(f"test rows: {len(result['test'])}")
    print(f"excluded columns: ['Id']")
    print(f"feature columns: {len(result['feature_columns'])}")
    print(f"prepared files saved to: {OUTPUT_DIR}")
