import argparse
import csv
import sys
from pathlib import Path
from typing import Any


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from modeling.baseline_valuation import to_model_record  # noqa: E402
from data.csv_to_ingest_posts import csv_to_ingest_payload  # noqa: E402
from scraper.parse_sample_posts import DEFAULT_INPUT, parse_post, parse_posts_file  # noqa: E402


DEFAULT_OUTPUT = Path(__file__).with_name("valuation_modeling_dataset.csv")

FIELDNAMES = [
    "external_id",
    "intent",
    "property_type",
    "city",
    "neighborhood",
    "target_price_jod",
    "area_sqm",
    "land_area_dunum",
    "unit_metric",
    "unit_price_jod",
    "bedrooms",
    "bathrooms",
    "floor_number",
    "building_age_years",
    "furnished",
    "negotiable",
    "motivated_seller",
    "has_phone_number",
    "contact_exposure",
    "quality_score",
    "quality_grade",
    "is_model_ready",
    "missing_fields",
    "warnings",
    "landmarks",
    "audiences",
    "extracted_terms",
    "raw_text",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Export parsed AqariX listings as a flat modeling CSV.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--model-ready-only",
        action="store_true",
        help="Only include rows that pass parser quality checks for modeling.",
    )
    args = parser.parse_args()

    parsed_posts = load_parsed_posts(args.input)
    rows = build_modeling_rows(parsed_posts, model_ready_only=args.model_ready_only)
    write_modeling_dataset(rows, args.output)
    print(f"Exported {len(rows)} modeling rows to {args.output}")


def build_modeling_rows(
    parsed_posts: list[dict[str, Any]],
    *,
    model_ready_only: bool = False,
) -> list[dict[str, Any]]:
    rows = [to_modeling_row(post) for post in parsed_posts]
    if model_ready_only:
        rows = [row for row in rows if row["is_model_ready"]]
    return rows


def load_parsed_posts(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        payload = csv_to_ingest_payload(path)
        return [parse_post(item) for item in payload["items"]]
    return parse_posts_file(path)


def to_modeling_row(post: dict[str, Any]) -> dict[str, Any]:
    parsed = post["parsed"]
    model_record = to_model_record(post)
    quality = parsed["quality"]

    return {
        "external_id": post.get("external_id"),
        "intent": model_record["intent"],
        "property_type": model_record["property_type"],
        "city": parsed["city"],
        "neighborhood": model_record["neighborhood"],
        "target_price_jod": model_record["price_jod"],
        "area_sqm": model_record["area_sqm"],
        "land_area_dunum": model_record["land_area_dunum"],
        "unit_metric": model_record["unit_metric"],
        "unit_price_jod": model_record["unit_price_jod"],
        "bedrooms": parsed["bedrooms"],
        "bathrooms": parsed["bathrooms"],
        "floor_number": parsed["floor_number"],
        "building_age_years": parsed["building_age_years"],
        "furnished": parsed["furnished"],
        "negotiable": parsed["negotiable"],
        "motivated_seller": parsed["motivated_seller"],
        "has_phone_number": parsed["has_phone_number"],
        "contact_exposure": parsed["contact_exposure"],
        "quality_score": quality["score"],
        "quality_grade": quality["grade"],
        "is_model_ready": quality["is_model_ready"],
        "missing_fields": "|".join(quality["missing_fields"]),
        "warnings": "|".join(quality["warnings"]),
        "landmarks": "|".join(item["key"] for item in parsed["landmarks"]),
        "audiences": "|".join(parsed["audiences"]),
        "extracted_terms": "|".join(parsed["extracted_terms"]),
        "raw_text": post.get("raw_text") or post["text"],
    }


def write_modeling_dataset(rows: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
