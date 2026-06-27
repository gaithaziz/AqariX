import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from scraper.parse_sample_posts import DEFAULT_INPUT, parse_posts_file  # noqa: E402


DEFAULT_OUTPUT = Path(__file__).with_name("baseline_valuation_report.json")
MIN_MODEL_READY_FOR_TRAINING = 300
MIN_GROUP_SIZE_FOR_ESTIMATE = 2


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a baseline valuation report from parsed Irbid seeds.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    parsed_posts = parse_posts_file(args.input)
    report = build_baseline_report(parsed_posts)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Baseline report: {report['dataset']['model_ready_posts']} model-ready posts, "
        f"training_ready={report['readiness']['training_ready']}"
    )


def build_baseline_report(parsed_posts: list[dict[str, Any]]) -> dict[str, Any]:
    records = [to_model_record(post) for post in parsed_posts]
    model_ready = [record for record in records if record["is_model_ready"]]
    comparable_records = [record for record in model_ready if record["unit_metric"] and record["unit_price_jod"]]

    group_stats = build_group_stats(comparable_records)
    fallback_stats = build_fallback_stats(comparable_records)
    evaluation = evaluate_baseline(comparable_records)

    return {
        "dataset": {
            "total_posts": len(records),
            "model_ready_posts": len(model_ready),
            "comparable_records": len(comparable_records),
            "sale_records": sum(1 for record in model_ready if record["intent"] == "sale"),
            "rent_records": sum(1 for record in model_ready if record["intent"] == "rent"),
        },
        "readiness": {
            "training_ready": len(model_ready) >= MIN_MODEL_READY_FOR_TRAINING,
            "minimum_model_ready_required": MIN_MODEL_READY_FOR_TRAINING,
            "next_step": (
                "collect_real_irbid_posts"
                if len(model_ready) < MIN_MODEL_READY_FOR_TRAINING
                else "train_baseline_model"
            ),
        },
        "group_unit_price_stats": group_stats,
        "fallback_unit_price_stats": fallback_stats,
        "baseline_evaluation": evaluation,
    }


def to_model_record(post: dict[str, Any]) -> dict[str, Any]:
    parsed = post["parsed"]
    neighborhood = parsed["neighborhoods"][0]["key"] if parsed["neighborhoods"] else "unknown"
    unit_metric = None
    unit_price = None
    if parsed["property_type"] == "land":
        unit_metric = "dunum"
        unit_price = parsed["price_per_dunum_jod"]
    elif parsed["area_sqm"]:
        unit_metric = "sqm"
        unit_price = parsed["price_per_sqm_jod"]

    return {
        "external_id": post.get("external_id"),
        "intent": parsed["intent"],
        "property_type": parsed["property_type"] or "unknown",
        "neighborhood": neighborhood,
        "price_jod": parsed["price_jod"],
        "area_sqm": parsed["area_sqm"],
        "land_area_dunum": parsed["land_area_dunum"],
        "unit_metric": unit_metric,
        "unit_price_jod": unit_price,
        "is_model_ready": parsed["quality"]["is_model_ready"],
    }


def build_group_stats(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    for record in records:
        key = (
            record["intent"],
            record["property_type"],
            record["neighborhood"],
            record["unit_metric"],
        )
        grouped[key].append(record["unit_price_jod"])

    return [
        {
            "intent": key[0],
            "property_type": key[1],
            "neighborhood": key[2],
            "unit_metric": key[3],
            "count": len(values),
            "median_unit_price_jod": round(statistics.median(values), 2),
        }
        for key, values in sorted(grouped.items())
    ]


def build_fallback_stats(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for record in records:
        key = (record["intent"], record["property_type"], record["unit_metric"])
        grouped[key].append(record["unit_price_jod"])

    return [
        {
            "intent": key[0],
            "property_type": key[1],
            "unit_metric": key[2],
            "count": len(values),
            "median_unit_price_jod": round(statistics.median(values), 2),
        }
        for key, values in sorted(grouped.items())
    ]


def evaluate_baseline(records: list[dict[str, Any]]) -> dict[str, Any]:
    estimates = []
    for index, record in enumerate(records):
        training = records[:index] + records[index + 1 :]
        estimate = estimate_price(record, training)
        if estimate is None or not record["price_jod"]:
            continue
        error_pct = abs(estimate - record["price_jod"]) / record["price_jod"]
        estimates.append(
            {
                "external_id": record["external_id"],
                "actual_price_jod": record["price_jod"],
                "estimated_price_jod": round(estimate),
                "absolute_error_pct": round(error_pct, 3),
            }
        )

    mape = round(statistics.mean(item["absolute_error_pct"] for item in estimates), 3) if estimates else None
    return {
        "method": "leave_one_out_median_unit_price",
        "evaluated_records": len(estimates),
        "mape": mape,
        "estimates": estimates,
    }


def estimate_price(record: dict[str, Any], training: list[dict[str, Any]]) -> float | None:
    candidates = [
        item
        for item in training
        if item["intent"] == record["intent"]
        and item["property_type"] == record["property_type"]
        and item["neighborhood"] == record["neighborhood"]
        and item["unit_metric"] == record["unit_metric"]
    ]
    if len(candidates) < MIN_GROUP_SIZE_FOR_ESTIMATE:
        candidates = [
            item
            for item in training
            if item["intent"] == record["intent"]
            and item["property_type"] == record["property_type"]
            and item["unit_metric"] == record["unit_metric"]
        ]
    if not candidates:
        return None

    median_unit_price = statistics.median(item["unit_price_jod"] for item in candidates)
    if record["unit_metric"] == "dunum":
        return median_unit_price * record["land_area_dunum"]
    return median_unit_price * record["area_sqm"]


if __name__ == "__main__":
    main()
