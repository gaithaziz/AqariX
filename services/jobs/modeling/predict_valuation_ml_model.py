import argparse
import json
import sys
from pathlib import Path


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from modeling.valuation_ml import DEFAULT_MODEL_OUTPUT, predict_price_from_text  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate a listing price with the learned AqariX model.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_OUTPUT)
    parser.add_argument("--text", required=True)
    args = parser.parse_args()

    if not args.model.exists():
        raise SystemExit(
            f"Model artifact not found at {args.model}. Train it first with train_valuation_ml_model.py."
        )

    prediction = predict_price_from_text(args.text, args.model)
    print(json.dumps(prediction, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
