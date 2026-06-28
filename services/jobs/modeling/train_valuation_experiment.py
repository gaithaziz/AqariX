import argparse
import csv
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from modeling.export_modeling_dataset import DEFAULT_OUTPUT as DEFAULT_DATASET  # noqa: E402
from modeling.export_modeling_dataset import build_modeling_rows, load_parsed_posts, write_modeling_dataset  # noqa: E402
from scraper.parse_sample_posts import DEFAULT_INPUT as DEFAULT_RAW_INPUT  # noqa: E402


DEFAULT_OUTPUT = Path(__file__).with_name("valuation_experiment.json")
MODEL_VERSION = "valuation-median-comparable-experiment-v0.1"
MIN_EXPERIMENT_RECORDS = 30
MIN_PROMOTION_RECORDS = 300
MAX_PROMOTION_MAPE = 0.20


def main() -> None:
    parser = argparse.ArgumentParser(description="Train/evaluate the first AqariX valuation experiment.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--raw-input", type=Path, default=DEFAULT_RAW_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--test-ratio", type=float, default=0.2)
    args = parser.parse_args()

    if not args.dataset.exists():
        parsed_posts = load_parsed_posts(args.raw_input)
        rows = build_modeling_rows(parsed_posts, model_ready_only=True)
        write_modeling_dataset(rows, args.dataset)

    rows = load_modeling_dataset(args.dataset)
    artifact = train_valuation_experiment(rows, test_ratio=args.test_ratio)
    args.output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Experiment {artifact['model_version']}: "
        f"{artifact['dataset']['usable_records']} usable rows, "
        f"mape={artifact['evaluation']['mape']}, "
        f"status={artifact['promotion']['status']}"
    )


def load_modeling_dataset(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return [normalize_row(row) for row in csv.DictReader(file)]


def normalize_row(row: dict[str, str]) -> dict[str, Any]:
    normalized: dict[str, Any] = dict(row)
    for field in (
        "target_price_jod",
        "area_sqm",
        "land_area_dunum",
        "unit_price_jod",
        "bedrooms",
        "bathrooms",
        "floor_number",
        "building_age_years",
        "quality_score",
    ):
        normalized[field] = to_number(row.get(field))
    normalized["is_model_ready"] = str(row.get("is_model_ready", "")).lower() == "true"
    return normalized


def train_valuation_experiment(
    rows: list[dict[str, Any]],
    *,
    test_ratio: float = 0.2,
) -> dict[str, Any]:
    usable_rows = [
        row
        for row in rows
        if row["is_model_ready"] and row["target_price_jod"] and row["unit_price_jod"]
    ]
    train_rows, test_rows = deterministic_split(usable_rows, test_ratio=test_ratio)
    model = build_comparable_model(train_rows)
    evaluation = evaluate_model(model, test_rows)

    blocking_reasons = []
    if len(usable_rows) < MIN_EXPERIMENT_RECORDS:
        blocking_reasons.append("not_enough_experiment_records")
    if len(usable_rows) < MIN_PROMOTION_RECORDS:
        blocking_reasons.append("not_enough_promotion_records")
    if evaluation["mape"] is None or evaluation["mape"] > MAX_PROMOTION_MAPE:
        blocking_reasons.append("mape_above_promotion_threshold")

    return {
        "model_version": MODEL_VERSION,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "total_rows": len(rows),
            "usable_records": len(usable_rows),
            "train_records": len(train_rows),
            "test_records": len(test_rows),
            "minimum_experiment_records": MIN_EXPERIMENT_RECORDS,
            "minimum_promotion_records": MIN_PROMOTION_RECORDS,
        },
        "model": model,
        "evaluation": evaluation,
        "promotion": {
            "status": "approved" if not blocking_reasons else "blocked",
            "blocking_reasons": blocking_reasons,
            "max_allowed_mape": MAX_PROMOTION_MAPE,
        },
        "usage_guidance": {
            "allowed_use": "offline_modeling_experiment",
            "requires_human_review": True,
            "notes": [
                "Use this as a modeling workflow check, not as production AVM quality.",
                "Collect real listings before comparing ML models.",
            ],
        },
    }


def deterministic_split(
    rows: list[dict[str, Any]],
    *,
    test_ratio: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not rows:
        return [], []
    sorted_rows = sorted(rows, key=lambda row: str(row.get("external_id") or ""))
    test_size = max(1, round(len(sorted_rows) * test_ratio)) if len(sorted_rows) > 1 else 0
    return sorted_rows[:-test_size] if test_size else sorted_rows, sorted_rows[-test_size:] if test_size else []


def build_comparable_model(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "group_unit_price_lookup": build_lookup(rows, group_key),
        "fallback_unit_price_lookup": build_lookup(rows, fallback_key),
        "global_unit_price_lookup": build_lookup(rows, global_key),
    }


def build_lookup(rows: list[dict[str, Any]], key_fn) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[float]] = {}
    for row in rows:
        key = key_fn(row)
        grouped.setdefault(key, []).append(float(row["unit_price_jod"]))

    return {
        key: {"count": len(values), "median_unit_price_jod": round(statistics.median(values), 2)}
        for key, values in sorted(grouped.items())
    }


def evaluate_model(model: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    predictions = []
    for row in rows:
        prediction = predict_row(model, row)
        if prediction["estimated_price_jod"] is None:
            continue
        error_pct = abs(prediction["estimated_price_jod"] - row["target_price_jod"]) / row["target_price_jod"]
        predictions.append(
            {
                "external_id": row["external_id"],
                "actual_price_jod": row["target_price_jod"],
                "estimated_price_jod": prediction["estimated_price_jod"],
                "confidence": prediction["confidence"],
                "absolute_error_jod": round(abs(prediction["estimated_price_jod"] - row["target_price_jod"])),
                "absolute_error_pct": round(error_pct, 3),
            }
        )

    mae = round(statistics.mean(item["absolute_error_jod"] for item in predictions), 2) if predictions else None
    mape = round(statistics.mean(item["absolute_error_pct"] for item in predictions), 3) if predictions else None
    return {
        "method": "holdout_median_comparable_unit_price",
        "evaluated_records": len(predictions),
        "mae_jod": mae,
        "mape": mape,
        "predictions": predictions,
    }


def predict_row(model: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    unit_area = row["land_area_dunum"] if row["unit_metric"] == "dunum" else row["area_sqm"]
    if not unit_area:
        return {"estimated_price_jod": None, "confidence": "low"}

    for lookup_name, confidence, key in (
        ("group_unit_price_lookup", "medium", group_key(row)),
        ("fallback_unit_price_lookup", "low", fallback_key(row)),
        ("global_unit_price_lookup", "low", global_key(row)),
    ):
        matched = model[lookup_name].get(key)
        if matched:
            return {
                "estimated_price_jod": round(matched["median_unit_price_jod"] * unit_area),
                "confidence": confidence,
            }
    return {"estimated_price_jod": None, "confidence": "low"}


def group_key(row: dict[str, Any]) -> str:
    return "|".join([row["intent"], row["property_type"], row["neighborhood"], row["unit_metric"]])


def fallback_key(row: dict[str, Any]) -> str:
    return "|".join([row["intent"], row["property_type"], row["unit_metric"]])


def global_key(row: dict[str, Any]) -> str:
    return "|".join([row["intent"], row["unit_metric"]])


def to_number(value: str | None) -> float | int | None:
    if value is None or value == "":
        return None
    number = float(value)
    return int(number) if number.is_integer() else number


if __name__ == "__main__":
    main()
