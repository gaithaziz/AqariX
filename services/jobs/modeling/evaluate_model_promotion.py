import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_MODEL = Path(__file__).with_name("baseline_valuation_model.json")
DEFAULT_OUTPUT = Path(__file__).with_name("baseline_valuation_model_card.json")
MAX_PROMOTION_MAPE = 0.20
MIN_PROMOTION_RECORDS = 300


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate whether a baseline valuation model can be promoted.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    model = json.loads(args.model.read_text(encoding="utf-8"))
    model_card = build_model_card(model)
    args.output.write_text(json.dumps(model_card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Promotion status: {model_card['promotion']['status']} "
        f"({'; '.join(model_card['promotion']['blocking_reasons']) or 'no blockers'})"
    )


def build_model_card(model: dict[str, Any]) -> dict[str, Any]:
    evaluation = model["evaluation"]
    training_summary = model["training_summary"]
    mape = evaluation.get("mape")
    blockers = []

    if training_summary["model_ready_posts"] < MIN_PROMOTION_RECORDS:
        blockers.append("not_enough_model_ready_records")
    if mape is None:
        blockers.append("no_evaluation_metric")
    elif mape > MAX_PROMOTION_MAPE:
        blockers.append("mape_above_threshold")

    return {
        "model_version": model["model_version"],
        "training_summary": training_summary,
        "evaluation": evaluation,
        "promotion": {
            "status": "blocked" if blockers else "promotable",
            "blocking_reasons": blockers,
            "minimum_model_ready_records": MIN_PROMOTION_RECORDS,
            "maximum_allowed_mape": MAX_PROMOTION_MAPE,
        },
        "usage_guidance": {
            "allowed_use": "internal_baseline_price_estimation",
            "not_allowed_use": "guaranteed_market_value_or_investment_advice",
            "requires_confidence_display": True,
            "requires_human_review": True,
        },
    }


if __name__ == "__main__":
    main()
