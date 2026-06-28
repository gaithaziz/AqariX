import argparse
import sys
from pathlib import Path


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from modeling.export_modeling_dataset import build_modeling_rows, load_parsed_posts, write_modeling_dataset  # noqa: E402
from modeling.valuation_ml import (  # noqa: E402
    DEFAULT_EXPERIMENT_OUTPUT as DEFAULT_REPORT_OUTPUT,
    DEFAULT_MODEL_OUTPUT as DEFAULT_MODEL_ARTIFACT,
    run_valuation_ml_experiment,
)


DEFAULT_DATASET = Path(__file__).with_name("valuation_modeling_dataset.csv")
DEFAULT_RAW_INPUT = JOBS_ROOT / "scraper" / "sample_irbid_posts.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the AqariX ridge+text valuation starter model.")
    parser.add_argument("--input", type=Path, default=DEFAULT_DATASET, help="Exported modeling CSV.")
    parser.add_argument(
        "--raw-input",
        type=Path,
        default=DEFAULT_RAW_INPUT,
        help="Raw JSON/CSV seed input used to build the modeling CSV when it does not exist yet.",
    )
    parser.add_argument("--model-output", type=Path, default=DEFAULT_MODEL_ARTIFACT)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_OUTPUT)
    parser.add_argument("--test-ratio", type=float, default=0.2)
    args = parser.parse_args()

    dataset_path = ensure_dataset(args.input, args.raw_input)
    report = run_valuation_ml_experiment(
        dataset_path,
        model_output=args.model_output,
        report_output=args.report_output,
        test_ratio=args.test_ratio,
    )
    print(
        f"Saved {report['model_name']} experiment: "
        f"rows={report['dataset']['usable_rows']}, "
        f"mape={report['evaluation']['mape']}, "
        f"status={report['readiness']['status']}"
    )
    print(f"Model artifact: {report['artifact']}")


def ensure_dataset(dataset_path: Path, raw_input_path: Path) -> Path:
    if dataset_path.exists():
        return dataset_path
    if not raw_input_path.exists():
        raise SystemExit(
            f"Modeling dataset not found at {dataset_path} and raw input not found at {raw_input_path}."
        )

    parsed_posts = load_parsed_posts(raw_input_path)
    rows = build_modeling_rows(parsed_posts, model_ready_only=True)
    if not rows:
        raise SystemExit(f"No model-ready rows could be built from {raw_input_path}.")

    write_modeling_dataset(rows, dataset_path)
    print(f"Exported {len(rows)} model-ready rows to {dataset_path}")
    return dataset_path


if __name__ == "__main__":
    main()
