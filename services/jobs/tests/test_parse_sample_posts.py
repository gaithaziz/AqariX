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
from modeling.predict_baseline_model import predict_price  # noqa: E402
from modeling.evaluate_model_promotion import build_model_card  # noqa: E402
from modeling.export_modeling_dataset import (  # noqa: E402
    build_modeling_rows,
    load_parsed_posts,
    write_modeling_dataset,
)
from modeling.train_baseline_model import MODEL_VERSION, train_baseline_model  # noqa: E402
from modeling.train_valuation_experiment import (  # noqa: E402
    MODEL_VERSION as EXPERIMENT_MODEL_VERSION,
)
from modeling.train_valuation_experiment import load_modeling_dataset, train_valuation_experiment  # noqa: E402
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


def test_train_and_predict_baseline_model() -> None:
    model = train_baseline_model(parse_posts_file(DEFAULT_INPUT))

    assert model["model_version"] == MODEL_VERSION
    assert model["group_unit_price_lookup"]
    assert model["fallback_unit_price_lookup"]

    prediction = predict_price("شقة للبيع في ايدون ثلاث غرف حمامين مساحة 150 متر", model)

    assert prediction["estimated_price_jod"] is not None
    assert prediction["model_version"] == MODEL_VERSION
    assert prediction["confidence"] in {"low", "medium"}


def test_model_promotion_is_blocked_for_seed_dataset() -> None:
    model = train_baseline_model(parse_posts_file(DEFAULT_INPUT))
    model_card = build_model_card(model)

    assert model_card["promotion"]["status"] == "blocked"
    assert "not_enough_model_ready_records" in model_card["promotion"]["blocking_reasons"]
    assert model_card["usage_guidance"]["requires_human_review"] is True


def test_export_modeling_dataset_rows() -> None:
    rows = build_modeling_rows(parse_posts_file(DEFAULT_INPUT), model_ready_only=True)

    assert len(rows) >= 10
    assert rows[0]["target_price_jod"] is not None
    assert rows[0]["unit_price_jod"] is not None
    assert rows[0]["is_model_ready"] is True
    assert "raw_text" in rows[0]

    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "valuation_modeling_dataset.csv"
        write_modeling_dataset(rows, output)

        content = output.read_text(encoding="utf-8")
        assert "target_price_jod" in content
        assert "quality_score" in content


def test_export_modeling_dataset_loads_real_csv_template() -> None:
    rows = build_modeling_rows(load_parsed_posts(REAL_DATA_TEMPLATE), model_ready_only=True)

    assert len(rows) == 2
    assert rows[0]["external_id"] == "real-irbid-001"
    assert rows[0]["target_price_jod"] is not None
    assert rows[0]["raw_text"]


def test_train_valuation_experiment_from_exported_dataset() -> None:
    rows = build_modeling_rows(parse_posts_file(DEFAULT_INPUT), model_ready_only=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        dataset = Path(tmpdir) / "valuation_modeling_dataset.csv"
        write_modeling_dataset(rows, dataset)

        artifact = train_valuation_experiment(load_modeling_dataset(dataset))

    assert artifact["model_version"] == EXPERIMENT_MODEL_VERSION
    assert artifact["dataset"]["usable_records"] >= 10
    assert artifact["model"]["fallback_unit_price_lookup"]
    assert artifact["evaluation"]["method"] == "holdout_median_comparable_unit_price"
    assert artifact["promotion"]["status"] == "blocked"
    assert "not_enough_promotion_records" in artifact["promotion"]["blocking_reasons"]


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
