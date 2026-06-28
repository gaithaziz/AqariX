import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from scraper.parse_sample_posts import DEFAULT_INPUT, parse_posts_file


DEFAULT_OUTPUT = Path(__file__).with_name("sample_irbid_posts_summary.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize parsed Irbid listing seed quality.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    parsed_posts = parse_posts_file(args.input)
    summary = summarize_parsed_posts(parsed_posts)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Summarized {summary['total_posts']} posts: "
        f"{summary['model_ready_posts']} model-ready, "
        f"{summary['contact_exposed_posts']} with contact exposure"
    )


def summarize_parsed_posts(parsed_posts: list[dict[str, Any]]) -> dict[str, Any]:
    property_types = Counter()
    intents = Counter()
    sources = Counter()
    collection_statuses = Counter()
    quality_grades = Counter()
    neighborhoods = Counter()
    missing_fields = Counter()
    warnings = Counter()
    model_ready = 0
    contact_exposed = 0

    for post in parsed_posts:
        parsed = post["parsed"]
        property_types.update([parsed.get("property_type") or "unknown"])
        intents.update([parsed.get("intent") or "unknown"])
        sources.update([post.get("source") or "unknown"])
        collection_statuses.update([post.get("collection_status") or "unknown"])
        quality = parsed["quality"]
        quality_grades.update([quality["grade"]])
        missing_fields.update(quality["missing_fields"])
        warnings.update(quality["warnings"])
        if quality["is_model_ready"]:
            model_ready += 1
        if parsed.get("contact_exposure"):
            contact_exposed += 1
        neighborhoods.update(neighborhood["key"] for neighborhood in parsed["neighborhoods"])

    total = len(parsed_posts)
    return {
        "total_posts": total,
        "model_ready_posts": model_ready,
        "model_ready_rate": round(model_ready / total, 3) if total else 0,
        "contact_exposed_posts": contact_exposed,
        "property_type_counts": dict(sorted(property_types.items())),
        "intent_counts": dict(sorted(intents.items())),
        "source_counts": dict(sorted(sources.items())),
        "collection_status_counts": dict(sorted(collection_statuses.items())),
        "quality_grade_counts": dict(sorted(quality_grades.items())),
        "neighborhood_counts": dict(sorted(neighborhoods.items())),
        "missing_field_counts": dict(sorted(missing_fields.items())),
        "warning_counts": dict(sorted(warnings.items())),
    }


if __name__ == "__main__":
    main()
