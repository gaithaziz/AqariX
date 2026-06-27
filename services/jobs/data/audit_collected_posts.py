import argparse
import json
import sys
from pathlib import Path
from typing import Any


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from data.csv_to_ingest_posts import DEFAULT_INPUT, csv_to_ingest_payload  # noqa: E402
from modeling.baseline_valuation import build_baseline_report  # noqa: E402
from scraper.parse_sample_posts import parse_post  # noqa: E402
from scraper.summarize_sample_posts import summarize_parsed_posts  # noqa: E402


DEFAULT_OUTPUT = Path(__file__).with_name("collected_irbid_posts.audit.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit collected Irbid listing CSV rows for modeling readiness.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    audit = audit_collected_posts(args.input)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Audited {audit['summary']['total_posts']} rows: "
        f"{audit['summary']['model_ready_posts']} model-ready, "
        f"training_ready={audit['baseline']['readiness']['training_ready']}"
    )


def audit_collected_posts(path: Path) -> dict[str, Any]:
    payload = csv_to_ingest_payload(path)
    parsed_posts = [
        parse_post(
            {
                "source": item["source"],
                "external_id": item["external_id"],
                "text": item["text"],
                "source_url": item.get("source_url"),
            }
        )
        for item in payload["items"]
    ]
    return {
        "input": str(path),
        "summary": summarize_parsed_posts(parsed_posts),
        "baseline": build_baseline_report(parsed_posts),
    }


if __name__ == "__main__":
    main()
