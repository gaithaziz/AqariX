import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from data.append_collected_post import (  # noqa: E402
    DEFAULT_OUTPUT,
    DEFAULT_SOURCE_LOG,
    append_collected_post,
    next_external_id,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Append a batch of collected Irbid listings.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--source", default="manual_collection")
    parser.add_argument("--collection-status", default="needs_review")
    parser.add_argument("--captured-at")
    parser.add_argument("--source-log", type=Path, default=DEFAULT_SOURCE_LOG)
    args = parser.parse_args()

    if args.input.resolve() == args.output.resolve():
        raise ValueError("Input and output must be different files")

    rows = load_input_rows(args.input)
    appended = append_batch_rows(
        rows,
        args.output,
        default_source=args.source,
        default_collection_status=args.collection_status,
        default_captured_at=args.captured_at,
        source_log_path=args.source_log,
    )
    print(f"Appended {appended} rows to {args.output}")


def load_input_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return load_csv_rows(path)
    if suffix == ".json":
        return load_json_rows(path)
    raise ValueError("Input must be a .csv or .json file")


def load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [dict(row) for row in csv.DictReader(file)]


def load_json_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "items" in payload:
        payload = payload["items"]
    if not isinstance(payload, list):
        raise ValueError("JSON input must be a list of rows or an object with an items array")
    return [dict(item) for item in payload]


def append_batch_rows(
    rows: list[dict[str, Any]],
    output: Path,
    *,
    default_source: str,
    default_collection_status: str,
    default_captured_at: str | None,
    source_log_path: Path | None = DEFAULT_SOURCE_LOG,
) -> int:
    appended = 0
    for row in rows:
        prepared = prepare_row(
            row,
            output,
            default_source=default_source,
            default_collection_status=default_collection_status,
            default_captured_at=default_captured_at,
        )
        append_collected_post(output, prepared, source_log_path=source_log_path)
        appended += 1
    return appended


def prepare_row(
    row: dict[str, Any],
    output: Path,
    *,
    default_source: str,
    default_collection_status: str,
    default_captured_at: str | None,
) -> dict[str, str]:
    source = clean(row.get("source")) or default_source
    text = clean(row.get("text"))
    source_url = clean(row.get("source_url")) or ""
    captured_at = clean(row.get("captured_at")) or default_captured_at
    collection_status = clean(row.get("collection_status")) or default_collection_status
    external_id = clean(row.get("external_id"))

    if not text:
        raise ValueError("Each batch row must include text")
    if not captured_at:
        raise ValueError("Each batch row must include captured_at or use --captured-at")

    if not external_id:
        external_id = next_external_id(output, captured_at)

    return {
        "source": source,
        "external_id": external_id,
        "text": text,
        "source_url": source_url,
        "captured_at": captured_at,
        "collection_status": collection_status,
    }


def clean(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


if __name__ == "__main__":
    main()
