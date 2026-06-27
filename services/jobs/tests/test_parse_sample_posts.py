import sys
from pathlib import Path


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from scraper.ingest_sample_posts import build_ingest_payload  # noqa: E402
from scraper.parse_sample_posts import DEFAULT_INPUT, parse_posts_file  # noqa: E402
from scraper.summarize_sample_posts import summarize_parsed_posts  # noqa: E402

from modeling.baseline_valuation import build_baseline_report  # noqa: E402


def test_parse_sample_irbid_posts() -> None:
    parsed_posts = parse_posts_file(DEFAULT_INPUT)

    assert len(parsed_posts) == 12
    first = parsed_posts[0]["parsed"]
    assert first["intent"] == "rent"
    assert first["property_type"] == "apartment"
    assert first["price_per_sqm_jod"] == 2.78
    assert first["landmarks"][0]["key"] == "yarmouk_university_north_gate"
    assert first["quality"]["is_model_ready"] is True

    land_post = parsed_posts[3]["parsed"]
    assert land_post["property_type"] == "land"
    assert land_post["price_jod"] == 70000
    assert land_post["land_area_dunum"] == 2.0
    assert land_post["price_per_dunum_jod"] == 35000.0
    assert land_post["neighborhoods"][0]["key"] == "al_husn"
    assert land_post["quality"]["grade"] == "high"

    southern_villa = parsed_posts[5]["parsed"]
    assert southern_villa["property_type"] == "villa"
    assert southern_villa["price_jod"] == 210000
    assert southern_villa["neighborhoods"][0]["key"] == "southern_irbid"


def test_build_ingest_payload_from_sample_posts() -> None:
    payload = build_ingest_payload(DEFAULT_INPUT)

    assert len(payload["items"]) == 12
    assert payload["items"][0]["source"] == "manual_seed"
    assert payload["items"][0]["external_id"] == "irbid-seed-001"
    assert "text" in payload["items"][0]
    assert payload["items"][0]["source_url"] is None


def test_summarize_sample_irbid_posts() -> None:
    summary = summarize_parsed_posts(parse_posts_file(DEFAULT_INPUT))

    assert summary["total_posts"] == 12
    assert summary["model_ready_posts"] >= 10
    assert summary["property_type_counts"]["apartment"] >= 6
    assert summary["property_type_counts"]["land"] == 2
    assert summary["intent_counts"] == {"rent": 6, "sale": 6}
    assert summary["contact_exposed_posts"] == 1


def test_build_baseline_valuation_report() -> None:
    report = build_baseline_report(parse_posts_file(DEFAULT_INPUT))

    assert report["dataset"]["total_posts"] == 12
    assert report["dataset"]["model_ready_posts"] >= 10
    assert report["readiness"]["training_ready"] is False
    assert report["readiness"]["next_step"] == "collect_real_irbid_posts"
    assert report["baseline_evaluation"]["method"] == "leave_one_out_median_unit_price"
    assert report["group_unit_price_stats"]
