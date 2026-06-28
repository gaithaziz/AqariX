import argparse
import json
import sys
from pathlib import Path
from typing import Any


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from data.audit_collection_sources import DEFAULT_SOURCE_LOG  # noqa: E402
from data.collection_backlog import build_collection_backlog  # noqa: E402
from data.collection_progress import build_collection_progress, print_progress  # noqa: E402
from modeling.export_modeling_dataset import (  # noqa: E402
    DEFAULT_OUTPUT as DEFAULT_DATASET_OUTPUT,
    build_modeling_rows,
    load_parsed_posts,
    write_modeling_dataset,
)
from modeling.train_valuation_experiment import (  # noqa: E402
    DEFAULT_OUTPUT as DEFAULT_EXPERIMENT_OUTPUT,
    load_modeling_dataset,
    train_valuation_experiment,
)


DEFAULT_COLLECTION = Path(__file__).with_name("collected_irbid_posts.csv")
DEFAULT_OUTPUT = Path(__file__).with_name("collection_pipeline_report.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full Irbid collection-to-modeling pipeline.")
    parser.add_argument("--input", type=Path, default=DEFAULT_COLLECTION)
    parser.add_argument("--source-log", type=Path, default=DEFAULT_SOURCE_LOG)
    parser.add_argument("--dataset-output", type=Path, default=DEFAULT_DATASET_OUTPUT)
    parser.add_argument("--experiment-output", type=Path, default=DEFAULT_EXPERIMENT_OUTPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    report = run_collection_pipeline(
        args.input,
        source_log_path=args.source_log,
        dataset_output=args.dataset_output,
        experiment_output=args.experiment_output,
    )
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print_progress(report["collection"])
    print(f"Backlog focus: {report['backlog']['recommended_focus']}")
    for item in report["backlog"]["priorities"][:3]:
        print(f"- {item['title']}: {item['reason']}")
    print(f"Dataset rows: {report['dataset']['rows']} -> {report['dataset']['output']}")
    print(
        f"Experiment status: {report['experiment']['promotion']['status']} "
        f"(mape={report['experiment']['evaluation']['mape']})"
    )
    print(f"Pipeline status: {report['status']} ({report['collection']['next_action']})")


def run_collection_pipeline(
    collection_path: Path,
    *,
    source_log_path: Path = DEFAULT_SOURCE_LOG,
    dataset_output: Path = DEFAULT_DATASET_OUTPUT,
    experiment_output: Path = DEFAULT_EXPERIMENT_OUTPUT,
) -> dict[str, Any]:
    collection = build_collection_progress(collection_path, source_log_path=source_log_path)
    backlog = build_collection_backlog(collection_path, source_log_path=source_log_path)
    parsed_posts = load_parsed_posts(collection_path)
    dataset_rows = build_modeling_rows(parsed_posts, model_ready_only=True)
    write_modeling_dataset(dataset_rows, dataset_output)
    experiment = train_valuation_experiment(load_modeling_dataset(dataset_output))
    write_json(experiment_output, experiment)

    return {
        "status": "ok",
        "collection": collection,
        "backlog": backlog,
        "dataset": {
            "output": str(dataset_output),
            "rows": len(dataset_rows),
        },
        "experiment": experiment,
        "next_action": collection["next_action"],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
