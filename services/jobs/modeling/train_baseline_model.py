import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from modeling.baseline_valuation import (  # noqa: E402
    DEFAULT_INPUT,
    build_baseline_report,
    parse_posts_file,
)


DEFAULT_OUTPUT = Path(__file__).with_name("baseline_valuation_model.json")
MODEL_VERSION = "baseline-median-unit-price-v0.1"


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the AqariX baseline median-unit-price model.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    parsed_posts = parse_posts_file(args.input)
    artifact = train_baseline_model(parsed_posts)
    args.output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Saved {artifact['model_version']} with "
        f"{artifact['training_summary']['comparable_records']} comparable records to {args.output}"
    )


def train_baseline_model(parsed_posts: list[dict[str, Any]]) -> dict[str, Any]:
    report = build_baseline_report(parsed_posts)
    group_lookup = {
        model_key(
            item["intent"],
            item["property_type"],
            item["neighborhood"],
            item["unit_metric"],
        ): item
        for item in report["group_unit_price_stats"]
    }
    fallback_lookup = {
        fallback_key(item["intent"], item["property_type"], item["unit_metric"]): item
        for item in report["fallback_unit_price_stats"]
    }

    return {
        "model_version": MODEL_VERSION,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_summary": report["dataset"],
        "readiness": report["readiness"],
        "group_unit_price_lookup": group_lookup,
        "fallback_unit_price_lookup": fallback_lookup,
        "evaluation": report["baseline_evaluation"],
    }


def model_key(intent: str, property_type: str, neighborhood: str, unit_metric: str) -> str:
    return "|".join([intent, property_type, neighborhood, unit_metric])


def fallback_key(intent: str, property_type: str, unit_metric: str) -> str:
    return "|".join([intent, property_type, unit_metric])


if __name__ == "__main__":
    main()
