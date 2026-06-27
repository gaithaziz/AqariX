import argparse
import json
from pathlib import Path
from typing import Any
from urllib import request


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_INPUT = Path(__file__).with_name("sample_irbid_posts.json")
DEFAULT_OUTPUT = Path(__file__).with_name("ingested_irbid_posts_response.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Send sample Irbid posts to the AqariX ingest API.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--api-base-url", default=DEFAULT_API_BASE_URL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = build_ingest_payload(args.input)
    response = post_ingest_payload(args.api_base_url, payload)
    args.output.write_text(json.dumps(response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Ingested {response['total']} posts through {args.api_base_url}")


def build_ingest_payload(path: Path) -> dict[str, list[dict[str, Any]]]:
    raw_posts = json.loads(path.read_text(encoding="utf-8"))
    return {
        "items": [
            {
                "source": post["source"],
                "external_id": post.get("external_id"),
                "text": post["text"],
                "source_url": post.get("source_url"),
            }
            for post in raw_posts
        ]
    }


def post_ingest_payload(api_base_url: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{api_base_url.rstrip('/')}/ai/ingest-raw-listing-posts"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    http_request = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(http_request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    main()
