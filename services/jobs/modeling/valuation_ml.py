import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler


JOBS_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = JOBS_ROOT.parent / "api"
for path in (JOBS_ROOT, API_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.nlp.dialect_parser import parse_listing_text  # noqa: E402
from app.repository import parsed_to_response  # noqa: E402
from app.nlp.quality import assess_listing_quality  # noqa: E402


DEFAULT_MODEL_OUTPUT = Path(__file__).with_name("valuation_ml_model.joblib")
DEFAULT_EXPERIMENT_OUTPUT = Path(__file__).with_name("valuation_ml_experiment.json")
MODEL_VERSION = "sklearn-ridge-text-v0.1"
RANDOM_STATE = 42
MIN_ROWS_FOR_ML = 100
MIN_ROWS_TO_FIT = 2
TARGET_COLUMN = "target_price_jod"
TEXT_COLUMN = "text_bundle"

NUMERIC_FEATURES = [
    "area_sqm",
    "land_area_dunum",
    "bedrooms",
    "bathrooms",
    "floor_number",
    "building_age_years",
    "quality_score",
    "text_length_chars",
    "text_token_count",
    "landmark_count",
    "audience_count",
    "extracted_term_count",
    "missing_field_count",
    "warning_count",
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

FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TEXT_COLUMN]
LEAKAGE_COLUMNS = ["unit_price_jod"]
PRICE_REGEXES = (
    r"\b\d+(?:\.\d+)?\s*(?:الف|ألف|k|K)\s*(?:دينار|jod|jd)?\b",
    r"\b\d{2,7}(?:\.\d+)?\s*(?:دينار|jod|jd)\b",
    r"\b(?:السعر|المطلوب|بسعر|الثمن|ثمنه)\s*\d{2,7}(?:\.\d+)?(?:\s*(?:الف|ألف|k|K))?(?:\s*(?:دينار|jod|jd))?\b",
)


def load_dataset(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def prepare_training_frame(df: pd.DataFrame) -> pd.DataFrame:
    prepared = enrich_frame(df)
    if "is_model_ready" in prepared.columns:
        prepared = prepared[prepared["is_model_ready"]]
    prepared[TARGET_COLUMN] = pd.to_numeric(prepared[TARGET_COLUMN], errors="coerce")
    prepared = prepared[prepared[TARGET_COLUMN].notna() & (prepared[TARGET_COLUMN] > 0)]
    if len(prepared) < MIN_ROWS_TO_FIT:
        raise ValueError("Need at least two usable rows to train the first ML starter.")
    return prepared.reset_index(drop=True)


def enrich_frame(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()

    for column in NUMERIC_FEATURES + [TARGET_COLUMN]:
        if column in prepared.columns:
            prepared[column] = pd.to_numeric(prepared[column], errors="coerce")
        else:
            prepared[column] = np.nan

    prepared["raw_text"] = ensure_series(prepared, "raw_text", "").fillna("").astype(str)

    for column in CATEGORICAL_FEATURES:
        if column not in prepared.columns:
            prepared[column] = ""
        prepared[column] = prepared[column].map(normalize_category)

    if "is_model_ready" in prepared.columns:
        prepared["is_model_ready"] = prepared["is_model_ready"].astype(str).str.lower() == "true"
    else:
        prepared["is_model_ready"] = True

    prepared["text_length_chars"] = prepared["raw_text"].map(lambda value: len(str(value)))
    prepared["text_token_count"] = prepared["raw_text"].map(lambda value: len(str(value).split()))
    prepared["landmark_count"] = ensure_series(prepared, "landmarks", "").map(count_pipe_values)
    prepared["audience_count"] = ensure_series(prepared, "audiences", "").map(count_pipe_values)
    prepared["extracted_term_count"] = ensure_series(prepared, "extracted_terms", "").map(count_pipe_values)
    prepared["missing_field_count"] = ensure_series(prepared, "missing_fields", "").map(count_pipe_values)
    prepared["warning_count"] = ensure_series(prepared, "warnings", "").map(count_pipe_values)
    prepared[TEXT_COLUMN] = prepared.apply(build_text_bundle, axis=1)

    return prepared


def build_text_bundle(row: pd.Series) -> str:
    parts = [
        strip_price_mentions(str(row.get("raw_text", ""))),
        normalize_text_fragment(row.get("landmarks")),
        normalize_text_fragment(row.get("audiences")),
        normalize_text_fragment(row.get("extracted_terms")),
        normalize_text_fragment(row.get("missing_fields")),
        normalize_text_fragment(row.get("warnings")),
    ]
    return re.sub(r"\s+", " ", " ".join(part for part in parts if part)).strip()


def normalize_category(value: Any) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not pd.isna(value):
        return str(value)
    if is_missing_value(value):
        return "unknown"
    text = normalize_text_fragment(value)
    return text.lower() if text else "unknown"


def ensure_series(frame: pd.DataFrame, column: str, default: Any) -> pd.Series:
    if column in frame.columns:
        return frame[column]
    return pd.Series([default] * len(frame), index=frame.index)


def normalize_text_fragment(value: Any) -> str:
    if is_missing_value(value):
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple, set)):
        parts = [normalize_text_fragment(item) for item in value]
        return " ".join(part for part in parts if part)
    text = str(value).replace("|", " ").replace("_", " ")
    return re.sub(r"\s+", " ", text).strip()


def is_missing_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (list, tuple, set, dict)):
        return False
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def count_pipe_values(value: Any) -> int:
    if is_missing_value(value):
        return 0
    text = str(value).strip()
    if not text:
        return 0
    return len([item for item in text.split("|") if item.strip()])


def strip_price_mentions(text: str) -> str:
    cleaned = text
    for pattern in PRICE_REGEXES:
        cleaned = re.sub(pattern, " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def build_model() -> TransformedTargetRegressor:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler(with_mean=False)),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", make_one_hot_encoder()),
        ]
    )
    text_pipeline = Pipeline(
        steps=[
            ("flatten", FunctionTransformer(flatten_text_documents, validate=False)),
            ("vectorizer", TfidfVectorizer(max_features=300, ngram_range=(1, 2), token_pattern=r"(?u)\b\w+\b")),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
            ("text", text_pipeline, TEXT_COLUMN),
        ],
        remainder="drop",
    )
    regressor = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", Ridge(alpha=2.0, solver="lsqr")),
        ]
    )
    return TransformedTargetRegressor(
        regressor=regressor,
        func=np.log1p,
        inverse_func=np.expm1,
        check_inverse=False,
    )


def make_one_hot_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=True)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=True)


def flatten_text_documents(values: Any) -> list[str]:
    if isinstance(values, pd.DataFrame):
        raw_values = values.iloc[:, 0].tolist()
    elif isinstance(values, pd.Series):
        raw_values = values.tolist()
    else:
        raw_array = np.asarray(values)
        if raw_array.ndim == 0:
            raw_values = [raw_array.item()]
        else:
            raw_values = raw_array.reshape(-1).tolist()
    return ["" if is_missing_value(value) else str(value) for value in raw_values]


def split_frame(frame: pd.DataFrame, test_ratio: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    if len(frame) <= 1:
        return frame, frame.iloc[0:0]
    test_size = max(1, round(len(frame) * test_ratio))
    if len(frame) - test_size < 1:
        test_size = 1
    train_frame, test_frame = train_test_split(frame, test_size=test_size, random_state=RANDOM_STATE, shuffle=True)
    return train_frame.reset_index(drop=True), test_frame.reset_index(drop=True)


def evaluate_predictions(actual: list[float], predicted: np.ndarray) -> dict[str, Any]:
    if not actual:
        return {
            "evaluated_records": 0,
            "mae_jod": None,
            "mape": None,
            "r2": None,
        }

    actual_array = np.asarray(actual, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)
    mae = float(mean_absolute_error(actual_array, predicted_array))
    mape = float(mean_absolute_percentage_error(actual_array, predicted_array))
    r2 = float(r2_score(actual_array, predicted_array)) if len(actual_array) > 1 else None
    return {
        "evaluated_records": int(len(actual_array)),
        "mae_jod": round(mae, 2),
        "mape": round(mape, 3),
        "r2": None if r2 is None else round(r2, 3),
    }


def run_valuation_ml_experiment(
    dataset_path: Path,
    *,
    model_output: Path = DEFAULT_MODEL_OUTPUT,
    report_output: Path = DEFAULT_EXPERIMENT_OUTPUT,
    test_ratio: float = 0.2,
) -> dict[str, Any]:
    dataset = load_dataset(dataset_path)
    prepared = prepare_training_frame(dataset)
    train_frame, test_frame = split_frame(prepared, test_ratio=test_ratio)

    model = build_model()
    model.fit(train_frame[FEATURE_COLUMNS], train_frame[TARGET_COLUMN])
    predictions = model.predict(test_frame[FEATURE_COLUMNS]) if len(test_frame) else np.asarray([])
    evaluation = evaluate_predictions(test_frame[TARGET_COLUMN].tolist(), predictions)

    model_bundle = {
        "model_version": MODEL_VERSION,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "dataset_summary": {
            "total_rows": int(len(dataset)),
            "usable_rows": int(len(prepared)),
            "train_rows": int(len(train_frame)),
            "test_rows": int(len(test_frame)),
            "minimum_rows_for_ml": MIN_ROWS_FOR_ML,
            "leakage_guardrails": ["unit_price_jod excluded from features", "explicit price mentions stripped from text_bundle"],
        },
        "evaluation": evaluation,
        "model": model,
    }
    model_output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_bundle, model_output)

    readiness_status = "ready_for_iteration" if len(prepared) >= MIN_ROWS_FOR_ML else "collect_more_data"
    blocking_reasons = [] if readiness_status == "ready_for_iteration" else ["not_enough_rows_for_ml"]
    report = {
        "model_name": "sklearn_ridge_text_regressor",
        "model_version": MODEL_VERSION,
        "trained_at": model_bundle["trained_at"],
        "dataset": model_bundle["dataset_summary"],
        "features": {
            "numeric": NUMERIC_FEATURES,
            "categorical": CATEGORICAL_FEATURES,
            "text": [TEXT_COLUMN],
            "target": TARGET_COLUMN,
        },
        "evaluation": evaluation,
        "readiness": {
            "status": readiness_status,
            "blocking_reasons": blocking_reasons,
            "minimum_rows_for_ml": MIN_ROWS_FOR_ML,
        },
        "artifact": str(model_output),
    }
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def load_model_bundle(model_path_or_bundle: Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(model_path_or_bundle, dict):
        return model_path_or_bundle
    return joblib.load(model_path_or_bundle)


def build_inference_frame(text: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    parsed = parse_listing_text(text)
    quality = assess_listing_quality(parsed)
    neighborhood = parsed.neighborhoods[0].key if parsed.neighborhoods else "unknown"
    unit_metric = "dunum" if parsed.property_type == "land" else "sqm"
    row = {
        "area_sqm": parsed.area_sqm,
        "land_area_dunum": parsed.land_area_dunum,
        "bedrooms": parsed.bedrooms,
        "bathrooms": parsed.bathrooms,
        "floor_number": parsed.floor_number,
        "building_age_years": parsed.building_age_years,
        "quality_score": quality.score,
        "text_length_chars": len(parsed.original_text),
        "text_token_count": len(parsed.normalized_text.split()),
        "landmark_count": len(parsed.landmarks),
        "audience_count": len(parsed.audiences),
        "extracted_term_count": len(parsed.extracted_terms),
        "missing_field_count": len(quality.missing_fields),
        "warning_count": len(quality.warnings),
        "intent": parsed.intent.value,
        "property_type": parsed.property_type or "unknown",
        "city": parsed.city or "unknown",
        "neighborhood": neighborhood,
        "unit_metric": unit_metric,
        "quality_grade": quality.grade,
        "furnished": parsed.furnished,
        "negotiable": parsed.negotiable,
        "motivated_seller": parsed.motivated_seller,
        "has_phone_number": parsed.has_phone_number,
        "contact_exposure": parsed.contact_exposure,
        "raw_text": parsed.original_text,
        "landmarks": "|".join(item.key for item in parsed.landmarks),
        "audiences": "|".join(item.value for item in parsed.audiences),
        "extracted_terms": "|".join(parsed.extracted_terms),
        "missing_fields": "|".join(quality.missing_fields),
        "warnings": "|".join(quality.warnings),
    }
    frame = enrich_frame(pd.DataFrame([row]))
    return frame, {
        "parsed": parsed,
        "quality": quality,
        "neighborhood": neighborhood,
        "unit_metric": unit_metric,
    }


def predict_price_from_text(text: str, model_path_or_bundle: Path | dict[str, Any]) -> dict[str, Any]:
    model_bundle = load_model_bundle(model_path_or_bundle)
    frame, context = build_inference_frame(text)
    parsed = context["parsed"]
    quality = context["quality"]
    parsed_response = parsed_to_response(parsed)
    completeness = feature_completeness(frame)
    if parsed.intent.value == "unknown" or not parsed.property_type:
        return {
            "estimated_price_jod": None,
            "confidence": "low",
            "reason": "missing_required_prediction_fields",
            "method": "sklearn_ridge_text_regressor",
            "model_version": model_bundle["model_version"],
            "feature_completeness": round(completeness, 3),
            "training_rows": model_bundle["dataset_summary"]["usable_rows"],
            "quality": parsed_response.quality.model_dump(mode="json"),
            "parsed": parsed_response.model_dump(mode="json"),
        }

    predicted_price = float(model_bundle["model"].predict(frame[FEATURE_COLUMNS])[0])
    estimated_price = max(round(predicted_price), 0)
    confidence = score_prediction_confidence(model_bundle, parsed_response, completeness)

    return {
        "estimated_price_jod": estimated_price,
        "confidence": confidence,
        "reason": "ml_ridge_text_regressor",
        "method": "sklearn_ridge_text_regressor",
        "model_version": model_bundle["model_version"],
        "feature_completeness": round(completeness, 3),
        "training_rows": model_bundle["dataset_summary"]["usable_rows"],
        "quality": parsed_response.quality.model_dump(mode="json"),
        "parsed": parsed_response.model_dump(mode="json"),
    }


def score_prediction_confidence(
    model_bundle: dict[str, Any],
    parsed_response: Any,
    completeness: float,
) -> str:
    dataset_summary = model_bundle["dataset_summary"]
    evaluation = model_bundle["evaluation"]
    if not parsed_response.quality.is_model_ready or completeness < 0.6:
        return "low"
    if dataset_summary["usable_rows"] >= MIN_ROWS_FOR_ML and evaluation.get("mape") is not None and evaluation["mape"] <= 0.25:
        return "medium"
    if dataset_summary["usable_rows"] >= 20 and completeness >= 0.75:
        return "medium"
    return "low"


def feature_completeness(frame: pd.DataFrame) -> float:
    row = frame.iloc[0]
    present = 0
    for column in FEATURE_COLUMNS:
        value = row[column]
        if is_missing_value(value):
            continue
        if isinstance(value, str) and value.strip().lower() in {"", "unknown", "nan", "none"}:
            continue
        present += 1
    return present / len(FEATURE_COLUMNS)
