import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "services" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.nlp.dialect_parser import ParsedListingText, parse_listing_text  # noqa: E402
from app.nlp.quality import assess_listing_quality  # noqa: E402


DEFAULT_INPUT = Path(__file__).with_name("sample_irbid_posts.json")
DEFAULT_OUTPUT = Path(__file__).with_name("parsed_irbid_posts.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse raw Irbid listing posts into AI-ready JSON.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    parsed_posts = parse_posts_file(args.input)

    args.output.write_text(
        json.dumps(parsed_posts, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Parsed {len(parsed_posts)} posts into {args.output}")


def parse_posts_file(path: Path) -> list[dict[str, Any]]:
    raw_posts = json.loads(path.read_text(encoding="utf-8"))
    return [parse_post(post) for post in raw_posts]


def parse_post(post: dict[str, Any]) -> dict[str, Any]:
    parsed = parse_listing_text(str(post["text"]))
    return {
        "source": post.get("source"),
        "external_id": post.get("external_id"),
        "raw_text": post["text"],
        "parsed": parsed_to_dict(parsed),
    }


def parsed_to_dict(parsed: ParsedListingText) -> dict[str, Any]:
    quality = assess_listing_quality(parsed)
    return {
        "city": parsed.city,
        "intent": parsed.intent.value,
        "property_type": parsed.property_type,
        "price_jod": parsed.price_jod,
        "price_period": parsed.price_period,
        "price_per_sqm_jod": parsed.price_per_sqm_jod,
        "price_per_dunum_jod": parsed.price_per_dunum_jod,
        "negotiable": parsed.negotiable,
        "area_sqm": parsed.area_sqm,
        "land_area_dunum": parsed.land_area_dunum,
        "bedrooms": parsed.bedrooms,
        "bathrooms": parsed.bathrooms,
        "floor_number": parsed.floor_number,
        "building_age_years": parsed.building_age_years,
        "furnished": parsed.furnished,
        "has_phone_number": parsed.has_phone_number,
        "contact_exposure": parsed.contact_exposure,
        "audiences": [audience.value for audience in parsed.audiences],
        "motivated_seller": parsed.motivated_seller,
        "neighborhoods": [
            {"key": neighborhood.key, "display_name": neighborhood.display_name}
            for neighborhood in parsed.neighborhoods
        ],
        "landmarks": [
            {
                "key": landmark.key,
                "display_name": landmark.display_name,
                "latitude": landmark.latitude,
                "longitude": landmark.longitude,
            }
            for landmark in parsed.landmarks
        ],
        "location_signals": parsed.location_signals,
        "extracted_terms": parsed.extracted_terms,
        "quality": {
            "score": quality.score,
            "grade": quality.grade,
            "is_model_ready": quality.is_model_ready,
            "missing_fields": quality.missing_fields,
            "warnings": quality.warnings,
        },
    }


if __name__ == "__main__":
    main()
