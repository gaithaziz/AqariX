import argparse
import json
import sys
from pathlib import Path
from typing import Any


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from data.audit_collected_posts import audit_collected_posts  # noqa: E402
from data.audit_collection_sources import DEFAULT_SOURCE_LOG, audit_collection_sources  # noqa: E402
DEFAULT_COLLECTION = Path(__file__).with_name("collected_irbid_posts.csv")
DEFAULT_OUTPUT = Path(__file__).with_name("collection_progress.json")
TARGETS = {
    "first_real_experiment": 30,
    "colab_ml_starter": 100,
    "promotion_candidate": 300,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Report Irbid listing collection progress.")
    parser.add_argument("--input", type=Path, default=DEFAULT_COLLECTION)
    parser.add_argument("--source-log", type=Path, default=DEFAULT_SOURCE_LOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    report = build_collection_progress(args.input, source_log_path=args.source_log)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print_progress(report)


def build_collection_progress(path: Path, source_log_path: Path = DEFAULT_SOURCE_LOG) -> dict[str, Any]:
    audit = audit_collected_posts(path)
    source_audit = audit_collection_sources(path, source_log_path)
    summary = audit["summary"]
    model_ready = summary["model_ready_posts"]
    total = summary["total_posts"]
    return {
        "input": str(path),
        "total_rows": total,
        "model_ready_rows": model_ready,
        "model_ready_rate": summary["model_ready_rate"],
        "targets": {
            name: {
                "required_model_ready_rows": required,
                "remaining_model_ready_rows": max(required - model_ready, 0),
                "complete": model_ready >= required,
            }
            for name, required in TARGETS.items()
        },
        "top_missing_fields": top_items(summary["missing_field_counts"]),
        "top_warnings": top_items(summary["warning_counts"]),
        "property_type_counts": summary["property_type_counts"],
        "intent_counts": summary["intent_counts"],
        "source_counts": summary["source_counts"],
        "collection_status_counts": summary["collection_status_counts"],
        "known_source_rows": source_audit["known_source_rows"],
        "unknown_source_rows": source_audit["unknown_source_rows"],
        "known_source_rate": source_audit["known_source_rate"],
        "unknown_source_keys": source_audit["unknown_source_keys"],
        "neighborhood_counts": summary["neighborhood_counts"],
        "next_action": next_action(model_ready, source_audit["unknown_source_keys"]),
    }


def print_progress(report: dict[str, Any]) -> None:
    first_target = report["targets"]["first_real_experiment"]
    print(
        f"Collection progress: {report['model_ready_rows']}/{first_target['required_model_ready_rows']} "
        f"model-ready rows for first experiment "
        f"({first_target['remaining_model_ready_rows']} remaining)."
    )
    print(
        f"Source coverage: {report['known_source_rows']}/{report['total_rows']} known "
        f"({report['known_source_rate']:.3f})"
    )
    print(f"Source mix: {format_counts(report['source_counts'])}")
    print(f"Status mix: {format_counts(report['collection_status_counts'])}")
    if report["unknown_source_keys"]:
        print(f"Unknown sources: {', '.join(report['unknown_source_keys'])}")
    print(f"Next action: {report['next_action']}")


def next_action(model_ready_rows: int, unknown_source_keys: list[str]) -> str:
    if unknown_source_keys:
        return "resolve_unknown_sources"
    if model_ready_rows < TARGETS["first_real_experiment"]:
        return "collect_more_real_irbid_listings"
    if model_ready_rows < TARGETS["colab_ml_starter"]:
        return "run_local_experiment_and_continue_collection"
    if model_ready_rows < TARGETS["promotion_candidate"]:
        return "run_colab_ml_starter_and_continue_collection"
    return "run_promotion_evaluation"


def top_items(counts: dict[str, int], limit: int = 5) -> list[dict[str, int | str]]:
    return [
        {"name": name, "count": count}
        for name, count in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]
    ]


def format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{name}={count}" for name, count in counts.items())


if __name__ == "__main__":
    main()
