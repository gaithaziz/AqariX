import argparse
import json
import sys
from pathlib import Path
from typing import Any


JOBS_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = JOBS_ROOT.parent / "api"
for path in (JOBS_ROOT, API_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.nlp.dialect_parser import parse_listing_text  # noqa: E402
from app.nlp.quality import assess_listing_quality  # noqa: E402
from modeling.train_baseline_model import DEFAULT_OUTPUT, fallback_key, model_key  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate a listing price with the baseline AqariX model.")
    parser.add_argument("--model", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--text", required=True)
    args = parser.parse_args()

    model = json.loads(args.model.read_text(encoding="utf-8"))
    prediction = predict_price(args.text, model)
    print(json.dumps(prediction, ensure_ascii=False, indent=2))


def predict_price(text: str, model: dict[str, Any]) -> dict[str, Any]:
    parsed = parse_listing_text(text)
    quality = assess_listing_quality(parsed)
    unit_metric = "dunum" if parsed.property_type == "land" else "sqm"
    unit_area = parsed.land_area_dunum if unit_metric == "dunum" else parsed.area_sqm
    neighborhood = parsed.neighborhoods[0].key if parsed.neighborhoods else "unknown"

    if parsed.intent.value == "unknown" or not parsed.property_type or not unit_area:
        return {
            "estimated_price_jod": None,
            "confidence": "low",
            "reason": "missing_required_prediction_fields",
            "quality": quality.__dict__,
        }

    lookup_key = model_key(parsed.intent.value, parsed.property_type, neighborhood, unit_metric)
    fallback_lookup_key = fallback_key(parsed.intent.value, parsed.property_type, unit_metric)
    matched = model["group_unit_price_lookup"].get(lookup_key)
    confidence = "medium"
    if matched is None:
        matched = model["fallback_unit_price_lookup"].get(fallback_lookup_key)
        confidence = "low"
    if matched is None:
        return {
            "estimated_price_jod": None,
            "confidence": "low",
            "reason": "no_comparable_unit_price",
            "quality": quality.__dict__,
        }

    estimate = round(float(matched["median_unit_price_jod"]) * float(unit_area))
    return {
        "estimated_price_jod": estimate,
        "confidence": confidence,
        "unit_metric": unit_metric,
        "unit_area": unit_area,
        "matched_unit_price_jod": matched["median_unit_price_jod"],
        "matched_count": matched["count"],
        "model_version": model["model_version"],
        "quality": quality.__dict__,
    }


if __name__ == "__main__":
    main()
