import argparse
import csv
from datetime import date
from pathlib import Path


DEFAULT_OUTPUT = Path(__file__).with_name("collected_irbid_posts.csv")
FIELDNAMES = ["source", "external_id", "text", "source_url", "captured_at", "collection_status"]
ALLOWED_COLLECTION_STATUSES = {"public", "approved", "needs_review"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Append one collected Irbid listing to the local CSV.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--text", required=True)
    parser.add_argument("--source", default="manual_collection")
    parser.add_argument("--external-id")
    parser.add_argument("--source-url", default="")
    parser.add_argument("--captured-at", default=date.today().isoformat())
    parser.add_argument(
        "--collection-status",
        choices=sorted(ALLOWED_COLLECTION_STATUSES),
        default="needs_review",
    )
    args = parser.parse_args()

    external_id = args.external_id or next_external_id(args.output, args.captured_at)
    append_collected_post(
        args.output,
        {
            "source": args.source,
            "external_id": external_id,
            "text": args.text,
            "source_url": args.source_url,
            "captured_at": args.captured_at,
            "collection_status": args.collection_status,
        },
    )
    print(f"Appended {external_id} to {args.output}")


def append_collected_post(path: Path, row: dict[str, str]) -> None:
    cleaned = clean_row(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0

    if exists:
        validate_unique_external_id(path, cleaned["external_id"])

    with path.open("a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        if not exists:
            writer.writeheader()
        writer.writerow(cleaned)


def clean_row(row: dict[str, str]) -> dict[str, str]:
    cleaned = {field: str(row.get(field, "")).strip() for field in FIELDNAMES}
    missing = [field for field in ("source", "external_id", "text", "captured_at") if not cleaned[field]]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    if cleaned["collection_status"] not in ALLOWED_COLLECTION_STATUSES:
        raise ValueError(
            "collection_status must be one of: "
            + ", ".join(sorted(ALLOWED_COLLECTION_STATUSES))
        )
    return cleaned


def validate_unique_external_id(path: Path, external_id: str) -> None:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            if row.get("external_id") == external_id:
                raise ValueError(f"Duplicate external_id: {external_id}")


def next_external_id(path: Path, captured_at: str) -> str:
    prefix = f"irbid-{captured_at[:4]}-"
    highest = 0
    if path.exists():
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                external_id = row.get("external_id", "")
                if external_id.startswith(prefix):
                    suffix = external_id.removeprefix(prefix)
                    if suffix.isdigit():
                        highest = max(highest, int(suffix))
    return f"{prefix}{highest + 1:04d}"


if __name__ == "__main__":
    main()
