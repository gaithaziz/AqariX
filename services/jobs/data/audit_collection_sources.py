import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from data.append_collected_post import DEFAULT_OUTPUT as DEFAULT_COLLECTION  # noqa: E402


DEFAULT_SOURCE_LOG = Path(__file__).with_name("source_log_template.csv")
DEFAULT_OUTPUT = Path(__file__).with_name("collection_source_audit.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit collected Irbid listing sources against the source log.")
    parser.add_argument("--input", type=Path, default=DEFAULT_COLLECTION)
    parser.add_argument("--source-log", type=Path, default=DEFAULT_SOURCE_LOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    report = audit_collection_sources(args.input, args.source_log)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Audited {report['total_rows']} rows: "
        f"{report['known_source_rows']} known-source, "
        f"{report['unknown_source_rows']} unknown-source"
    )


def audit_collection_sources(collection_path: Path, source_log_path: Path = DEFAULT_SOURCE_LOG) -> dict[str, Any]:
    source_log = load_source_log(source_log_path)
    rows = load_csv_rows(collection_path)
    source_counts = Counter((row.get("source") or "unknown") for row in rows)
    collection_status_counts = Counter((row.get("collection_status") or "unknown") for row in rows)

    known_source_keys = sorted(key for key in source_counts if key in source_log)
    unknown_source_keys = sorted(key for key in source_counts if key not in source_log)
    source_type_counts = Counter()
    allowed_use_counts = Counter()
    for row in rows:
        source_key = row.get("source") or "unknown"
        if source_key in source_log:
            source_type_counts[source_log[source_key]["source_type"]] += 1
            allowed_use_counts[source_log[source_key]["allowed_use"]] += 1

    known_source_rows = sum(source_counts[key] for key in known_source_keys)
    unknown_source_rows = sum(source_counts[key] for key in unknown_source_keys)
    total_rows = len(rows)

    return {
        "collection_input": str(collection_path),
        "source_log_input": str(source_log_path),
        "total_rows": total_rows,
        "known_source_rows": known_source_rows,
        "unknown_source_rows": unknown_source_rows,
        "known_source_rate": round(known_source_rows / total_rows, 3) if total_rows else 0,
        "source_counts": dict(sorted(source_counts.items())),
        "collection_status_counts": dict(sorted(collection_status_counts.items())),
        "known_source_keys": known_source_keys,
        "unknown_source_keys": unknown_source_keys,
        "source_type_counts": dict(sorted(source_type_counts.items())),
        "allowed_use_counts": dict(sorted(allowed_use_counts.items())),
        "approved_source_names": approved_source_names(source_log, known_source_keys),
        "next_action": next_action(unknown_source_keys),
    }


def load_source_log(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = [normalize_source_log_row(row, index + 2) for index, row in enumerate(reader)]
    if not rows:
        raise ValueError(f"{path} does not contain any source definitions")
    return {row["source_key"]: row for row in rows}


def normalize_source_log_row(row: dict[str, str], line_number: int) -> dict[str, str]:
    cleaned = {key: str(value).strip() for key, value in row.items()}
    source_key = cleaned.get("source_key") or ""
    source_type = cleaned.get("source_type") or ""
    source_name = cleaned.get("source_name") or ""
    allowed_use = cleaned.get("allowed_use") or ""

    missing = [name for name, value in (
        ("source_key", source_key),
        ("source_type", source_type),
        ("source_name", source_name),
        ("allowed_use", allowed_use),
    ) if not value]
    if missing:
        raise ValueError(f"Source log row {line_number} is missing: {', '.join(missing)}")

    return {
        "source_key": source_key,
        "source_type": source_type,
        "source_name": source_name,
        "source_url": cleaned.get("source_url", ""),
        "allowed_use": allowed_use,
        "approval_owner": cleaned.get("approval_owner", ""),
        "notes": cleaned.get("notes", ""),
    }


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [dict(row) for row in csv.DictReader(file)]


def approved_source_names(source_log: dict[str, dict[str, str]], source_keys: list[str]) -> list[str]:
    return [source_log[key]["source_name"] for key in source_keys if key in source_log]


def next_action(unknown_source_keys: list[str]) -> str:
    if unknown_source_keys:
        return "resolve_unknown_sources"
    return "continue_collecting_rows"


if __name__ == "__main__":
    main()
