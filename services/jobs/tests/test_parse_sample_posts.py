import sys
from pathlib import Path


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from scraper.ingest_sample_posts import build_ingest_payload  # noqa: E402
from scraper.parse_sample_posts import DEFAULT_INPUT, parse_posts_file  # noqa: E402


def test_parse_sample_irbid_posts() -> None:
    parsed_posts = parse_posts_file(DEFAULT_INPUT)

    assert len(parsed_posts) == 5
    first = parsed_posts[0]["parsed"]
    assert first["intent"] == "rent"
    assert first["property_type"] == "apartment"
    assert first["landmarks"][0]["key"] == "yarmouk_university_north_gate"

    land_post = parsed_posts[3]["parsed"]
    assert land_post["property_type"] == "land"
    assert land_post["price_jod"] == 70000
    assert land_post["land_area_dunum"] == 2.0
    assert land_post["neighborhoods"][0]["key"] == "al_husn"


def test_build_ingest_payload_from_sample_posts() -> None:
    payload = build_ingest_payload(DEFAULT_INPUT)

    assert len(payload["items"]) == 5
    assert payload["items"][0]["source"] == "manual_seed"
    assert payload["items"][0]["external_id"] == "irbid-seed-001"
    assert "text" in payload["items"][0]
    assert payload["items"][0]["source_url"] is None
