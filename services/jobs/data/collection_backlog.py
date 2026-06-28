import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from data.audit_collection_sources import DEFAULT_SOURCE_LOG, load_source_log  # noqa: E402
from data.collection_progress import build_collection_progress  # noqa: E402


DEFAULT_COLLECTION = Path(__file__).with_name("collected_irbid_posts.csv")
DEFAULT_OUTPUT = Path(__file__).with_name("collection_backlog.json")
REQUIRED_PROPERTY_TYPES = ("apartment", "villa", "land", "commercial")
REQUIRED_INTENTS = ("sale", "rent")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a practical Irbid collection backlog.")
    parser.add_argument("--input", type=Path, default=DEFAULT_COLLECTION)
    parser.add_argument("--source-log", type=Path, default=DEFAULT_SOURCE_LOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    report = build_collection_backlog(args.input, source_log_path=args.source_log)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print_backlog(report)


def build_collection_backlog(path: Path, source_log_path: Path = DEFAULT_SOURCE_LOG) -> dict[str, Any]:
    progress = build_collection_progress(path, source_log_path=source_log_path)
    source_log = load_source_log(source_log_path)
    source_counts = Counter(progress["source_counts"])
    property_type_counts = Counter(progress["property_type_counts"])
    intent_counts = Counter(progress["intent_counts"])
    missing_fields = progress["top_missing_fields"]

    priorities: list[dict[str, Any]] = []

    if progress["unknown_source_keys"]:
        priorities.append(
            priority_item(
                1,
                "source",
                "Resolve unknown source keys",
                f"Unknown source keys found: {', '.join(progress['unknown_source_keys'])}",
                target_rows=0,
                current_rows=progress["unknown_source_rows"],
            )
        )

    for source_key, source_info in source_log.items():
        if source_key in source_counts:
            continue
        priorities.append(
            priority_item(
                len(priorities) + 1,
                "source",
                f"Add {source_info['source_name']}",
                f"No rows collected from approved source key '{source_key}' yet.",
                target_rows=1,
                current_rows=0,
            )
        )

    for property_type in REQUIRED_PROPERTY_TYPES:
        current_rows = property_type_counts.get(property_type, 0)
        if current_rows:
            continue
        priorities.append(
            priority_item(
                len(priorities) + 1,
                "property_type",
                f"Collect {property_type} listings",
                f"No {property_type} rows are present yet.",
                target_rows=2,
                current_rows=current_rows,
            )
        )

    for intent in REQUIRED_INTENTS:
        current_rows = intent_counts.get(intent, 0)
        if current_rows:
            continue
        priorities.append(
            priority_item(
                len(priorities) + 1,
                "intent",
                f"Collect {intent} listings",
                f"No {intent} rows are present yet.",
                target_rows=2,
                current_rows=current_rows,
            )
        )

    for item in missing_fields[:3]:
        priorities.append(
            priority_item(
                len(priorities) + 1,
                "quality",
                f"Improve {item['name']} coverage",
                f"{item['count']} rows are still missing '{item['name']}'.",
                target_rows=0,
                current_rows=0,
            )
        )

    if len(progress["neighborhood_counts"]) < 3:
        priorities.append(
            priority_item(
                len(priorities) + 1,
                "neighborhood",
                "Widen neighborhood coverage",
                "Collect listings from at least three different neighborhoods.",
                target_rows=3,
                current_rows=len(progress["neighborhood_counts"]),
            )
        )

    return {
        "input": str(path),
        "total_rows": progress["total_rows"],
        "model_ready_rows": progress["model_ready_rows"],
        "known_source_rows": progress["known_source_rows"],
        "unknown_source_rows": progress["unknown_source_rows"],
        "unknown_source_keys": progress["unknown_source_keys"],
        "priorities": priorities[:8],
        "recommended_focus": priorities[0]["title"] if priorities else "keep_collecting_current_mix",
        "progress": progress,
    }


def priority_item(
    priority: int,
    category: str,
    title: str,
    reason: str,
    *,
    target_rows: int,
    current_rows: int,
) -> dict[str, Any]:
    return {
        "priority": priority,
        "category": category,
        "title": title,
        "reason": reason,
        "target_rows": target_rows,
        "current_rows": current_rows,
        "remaining_rows": max(target_rows - current_rows, 0),
    }


def print_backlog(report: dict[str, Any]) -> None:
    print(f"Backlog focus: {report['recommended_focus']}")
    for item in report["priorities"][:5]:
        print(f"- {item['title']}: {item['reason']}")


if __name__ == "__main__":
    main()
