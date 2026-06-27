import sys
from pathlib import Path
import tempfile


JOBS_ROOT = Path(__file__).resolve().parents[1]
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from scraper.ingest_sample_posts import build_ingest_payload  # noqa: E402
from scraper.parse_sample_posts import DEFAULT_INPUT, parse_posts_file  # noqa: E402
from scraper.summarize_sample_posts import summarize_parsed_posts  # noqa: E402

from modeling.baseline_valuation import build_baseline_report  # noqa: E402
from data.csv_to_ingest_posts import DEFAULT_INPUT as REAL_DATA_TEMPLATE  # noqa: E402
from data.csv_to_ingest_posts import csv_to_ingest_payload  # noqa: E402
from data.audit_collected_posts import audit_collected_posts  # noqa: E402
from data.ingest_collected_posts import DEFAULT_OUTPUT as COLLECTED_INGEST_RESPONSE  # noqa: E402


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


def test_convert_real_irbid_csv_template_to_ingest_payload() -> None:
    payload = csv_to_ingest_payload(REAL_DATA_TEMPLATE)

    assert len(payload["items"]) == 2
    assert payload["items"][0]["source"] == "manual_collection"
    assert payload["items"][0]["external_id"] == "real-irbid-001"
    assert "جامعة اليرموك" in payload["items"][0]["text"]


def test_convert_real_irbid_csv_rejects_missing_text() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "bad.csv"
        path.write_text("source,external_id,text\nmanual,x1,\n", encoding="utf-8")

        try:
            csv_to_ingest_payload(path)
        except ValueError as exc:
            assert "missing text" in str(exc)
        else:
            raise AssertionError("Expected missing text validation error")


def test_collected_ingest_response_default_is_ignored_output() -> None:
    assert COLLECTED_INGEST_RESPONSE.name == "collected_irbid_posts.response.json"


def test_audit_real_irbid_csv_template() -> None:
    audit = audit_collected_posts(REAL_DATA_TEMPLATE)

    assert audit["summary"]["total_posts"] == 2
    assert audit["summary"]["model_ready_posts"] == 2
    assert audit["baseline"]["readiness"]["training_ready"] is False
    assert audit["baseline"]["readiness"]["next_step"] == "collect_real_irbid_posts"
