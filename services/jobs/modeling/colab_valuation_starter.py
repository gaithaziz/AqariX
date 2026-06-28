import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path("valuation_modeling_dataset.csv")
DEFAULT_OUTPUT = Path("valuation_ml_experiment.json")
MIN_ROWS_FOR_ML = 100
RANDOM_STATE = 42

NUMERIC_FEATURES = [
    "area_sqm",
    "land_area_dunum",
    "unit_price_jod",
    "bedrooms",
    "bathrooms",
    "floor_number",
    "building_age_years",
    "quality_score",
]
CATEGORICAL_FEATURES = [
    "intent",
    "property_type",
    "city",
    "neighborhood",
    "unit_metric",
    "quality_grade",
    "furnished",
    "negotiable",
    "motivated_seller",
    "has_phone_number",
    "contact_exposure",
]
TARGET = "target_price_jod"


def main() -> None:
    parser = argparse.ArgumentParser(description="Colab-ready AqariX valuation ML starter.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    result = run_experiment(args.input)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Saved {result['model_name']} experiment: "
        f"rows={result['dataset']['usable_rows']}, "
        f"mape={result['metrics']['mape']}, "
        f"status={result['readiness']['status']}"
    )


def run_experiment(dataset_path: Path) -> dict[str, Any]:
    pd, sklearn = import_ml_dependencies()
    df = pd.read_csv(dataset_path)
    usable = prepare_dataframe(df)
    train_test_split = sklearn["train_test_split"]

    train_df, test_df = train_test_split(
        usable,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=stratify_series(usable),
    )
    pipeline = build_pipeline(sklearn)
    pipeline.fit(train_df[feature_columns()], train_df[TARGET])
    predictions = pipeline.predict(test_df[feature_columns()])
    metrics = evaluate_predictions(test_df[TARGET].to_list(), predictions)

    return {
        "model_name": "sklearn_hist_gradient_boosting_regressor",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "total_rows": int(len(df)),
            "usable_rows": int(len(usable)),
            "train_rows": int(len(train_df)),
            "test_rows": int(len(test_df)),
            "minimum_rows_for_ml": MIN_ROWS_FOR_ML,
        },
        "features": {
            "numeric": NUMERIC_FEATURES,
            "categorical": CATEGORICAL_FEATURES,
            "target": TARGET,
        },
        "metrics": metrics,
        "readiness": {
            "status": "ready_for_iteration" if len(usable) >= MIN_ROWS_FOR_ML else "collect_more_data",
            "blocking_reasons": [] if len(usable) >= MIN_ROWS_FOR_ML else ["not_enough_rows_for_ml"],
        },
    }


def import_ml_dependencies():
    try:
        import pandas as pd
        from sklearn.compose import ColumnTransformer
        from sklearn.ensemble import HistGradientBoostingRegressor
        from sklearn.impute import SimpleImputer
        from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder
    except ImportError as exc:
        raise SystemExit(
            "Install Colab dependencies first: pip install pandas scikit-learn"
        ) from exc

    return pd, {
        "ColumnTransformer": ColumnTransformer,
        "HistGradientBoostingRegressor": HistGradientBoostingRegressor,
        "OneHotEncoder": OneHotEncoder,
        "Pipeline": Pipeline,
        "SimpleImputer": SimpleImputer,
        "mean_absolute_error": mean_absolute_error,
        "mean_absolute_percentage_error": mean_absolute_percentage_error,
        "train_test_split": train_test_split,
    }


def prepare_dataframe(df):
    usable = df.copy()
    usable = usable[usable["is_model_ready"].astype(str).str.lower() == "true"]
    usable = usable[usable[TARGET].notna()]
    for column in NUMERIC_FEATURES + [TARGET]:
        usable[column] = usable[column].apply(to_number)
    for column in CATEGORICAL_FEATURES:
        usable[column] = usable[column].fillna("unknown").astype(str)
    return usable.dropna(subset=[TARGET])


def build_pipeline(sklearn: dict[str, Any]):
    numeric_pipeline = sklearn["Pipeline"](
        steps=[("imputer", sklearn["SimpleImputer"](strategy="median"))]
    )
    categorical_pipeline = sklearn["Pipeline"](
        steps=[
            ("imputer", sklearn["SimpleImputer"](strategy="most_frequent")),
            ("onehot", one_hot_encoder(sklearn)),
        ]
    )
    preprocessor = sklearn["ColumnTransformer"](
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )
    return sklearn["Pipeline"](
        steps=[
            ("preprocess", preprocessor),
            (
                "model",
                sklearn["HistGradientBoostingRegressor"](
                    learning_rate=0.05,
                    max_iter=200,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def evaluate_predictions(actual: list[float], predicted) -> dict[str, float]:
    _pd, sklearn = import_ml_dependencies()
    mae = sklearn["mean_absolute_error"](actual, predicted)
    mape = sklearn["mean_absolute_percentage_error"](actual, predicted)
    return {
        "mae_jod": round(float(mae), 2),
        "mape": round(float(mape), 3),
    }


def one_hot_encoder(sklearn: dict[str, Any]):
    try:
        return sklearn["OneHotEncoder"](handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return sklearn["OneHotEncoder"](handle_unknown="ignore", sparse=False)


def feature_columns() -> list[str]:
    return NUMERIC_FEATURES + CATEGORICAL_FEATURES


def stratify_series(df):
    if len(df) < 20:
        return None
    groups = df["intent"].astype(str) + "|" + df["property_type"].astype(str)
    return groups if groups.value_counts().min() >= 2 else None


def to_number(value):
    if value is None or value == "":
        return None
    return float(value)


if __name__ == "__main__":
    main()
