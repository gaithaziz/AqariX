import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path(__file__).with_name("real_irbid_posts_template.csv")
DEFAULT_OUTPUT = Path(__file__).with_name("collected_irbid_posts.ingest.json")
REQUIRED_COLUMNS = {"source", "external_id", "text"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert collected Irbid listing CSV rows to ingest JSON.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = csv_to_ingest_payload(args.input)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Converted {len(payload['items'])} rows into {args.output}")


def csv_to_ingest_payload(path: Path) -> dict[str, list[dict[str, Any]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        validate_columns(reader.fieldnames)
        items = [row_to_item(row, index + 2) for index, row in enumerate(reader)]

    if not items:
        raise ValueError(f"{path} does not contain any listing rows")
    return {"items": items}


def validate_columns(fieldnames: list[str] | None) -> None:
    columns = set(fieldnames or [])
    missing = sorted(REQUIRED_COLUMNS - columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")


def row_to_item(row: dict[str, str], line_number: int) -> dict[str, Any]:
    source = clean(row.get("source"))
    external_id = clean(row.get("external_id"))
    text = clean(row.get("text"))
    source_url = clean(row.get("source_url"))
    collection_status = clean(row.get("collection_status"))

    if not source:
        raise ValueError(f"Row {line_number} is missing source")
    if not external_id:
        raise ValueError(f"Row {line_number} is missing external_id")
    if not text:
        raise ValueError(f"Row {line_number} is missing text")

    return {
        "source": source,
        "external_id": external_id,
        "text": text,
        "source_url": source_url,
        "collection_status": collection_status,
    }


def clean(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


if __name__ == "__main__":
    main()
