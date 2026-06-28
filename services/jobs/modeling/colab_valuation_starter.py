import argparse
import sys
from pathlib import Path


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from modeling.train_valuation_ml_model import ensure_dataset  # noqa: E402
from modeling.valuation_ml import (  # noqa: E402
    DEFAULT_EXPERIMENT_OUTPUT as DEFAULT_REPORT_OUTPUT,
    DEFAULT_MODEL_OUTPUT as DEFAULT_MODEL_ARTIFACT,
    run_valuation_ml_experiment,
)


DEFAULT_INPUT = Path("valuation_modeling_dataset.csv")
DEFAULT_RAW_INPUT = Path("sample_irbid_posts.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Colab-ready AqariX valuation ML starter.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--raw-input", type=Path, default=DEFAULT_RAW_INPUT)
    parser.add_argument("--model-output", type=Path, default=DEFAULT_MODEL_ARTIFACT)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_OUTPUT)
    parser.add_argument("--test-ratio", type=float, default=0.2)
    args = parser.parse_args()

    dataset_path = ensure_dataset(args.input, args.raw_input)
    report = run_valuation_ml_experiment(
        dataset_path,
        model_output=args.model_output,
        report_output=args.output,
        test_ratio=args.test_ratio,
    )
    print(
        f"Saved {report['model_name']} experiment: "
        f"rows={report['dataset']['usable_rows']}, "
        f"mape={report['evaluation']['mape']}, "
        f"status={report['readiness']['status']}"
    )
    print(f"Model artifact: {report['artifact']}")


if __name__ == "__main__":
    main()
