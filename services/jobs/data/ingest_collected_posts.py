import argparse
import json
import sys
from pathlib import Path


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from data.csv_to_ingest_posts import DEFAULT_INPUT, csv_to_ingest_payload  # noqa: E402
from scraper.ingest_sample_posts import DEFAULT_API_BASE_URL, post_ingest_payload  # noqa: E402


DEFAULT_OUTPUT = Path(__file__).with_name("collected_irbid_posts.response.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest collected Irbid CSV rows through the AqariX API.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--api-base-url", default=DEFAULT_API_BASE_URL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = csv_to_ingest_payload(args.input)
    response = post_ingest_payload(args.api_base_url, payload)
    args.output.write_text(json.dumps(response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Ingested {response['total']} collected rows through {args.api_base_url}")


if __name__ == "__main__":
    main()
