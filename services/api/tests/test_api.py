import sys
import tempfile
from pathlib import Path
from uuid import UUID


API_ROOT = Path(__file__).resolve().parents[1]
JOBS_ROOT = API_ROOT.parent / "jobs"
for path in (API_ROOT, JOBS_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import limits
from app.main import app
from app.nlp import valuation_ml as learned_valuation
from modeling.export_modeling_dataset import build_modeling_rows, load_parsed_posts, write_modeling_dataset
from modeling.valuation_ml import run_valuation_ml_experiment
from scraper.parse_sample_posts import DEFAULT_INPUT

client = TestClient(app)


@pytest.fixture(autouse=True)
def disable_redis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(limits, "get_redis_client", lambda: None)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_listing_search() -> None:
    response = client.get("/listings", params={"city": "Amman"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert body["items"][0]["city"] == "Amman"


def test_parse_listing_text_endpoint() -> None:
    response = client.post(
        "/ai/parse-listing-text",
        json={"text": "ارض للبيع في الحصن مساحة 2 دونم السعر 70 الف دينار قابل للتفاوض"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "sale"
    assert body["property_type"] == "land"
    assert body["price_jod"] == 70000
    assert body["land_area_dunum"] == 2.0
    assert body["negotiable"] is True
    assert body["neighborhoods"][0]["key"] == "al_husn"
    assert body["quality"]["is_model_ready"] is True


def test_parse_listing_text_batch_endpoint() -> None:
    response = client.post(
        "/ai/parse-listing-text/batch",
        json={
            "items": [
                {"text": "سكن شباب قريب من جامعة اليرموك اجار شهري 120 دينار بدون فرش"},
                {"text": "محل تجاري للايجار في الحي الشرقي مساحة 45 متر اجار شهري 350 دينار"},
            ]
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["items"][0]["audiences"] == ["singles"]
    assert body["items"][0]["landmarks"][0]["key"] == "yarmouk_university"
    assert body["items"][1]["property_type"] == "commercial"
    assert body["items"][1]["neighborhoods"][0]["key"] == "eastern_district"


def test_baseline_valuation_endpoint_estimates_from_listing_text() -> None:
    response = client.post(
        "/ai/baseline-valuation",
        json={
            "text": "\u0627\u0631\u0636 \u0644\u0644\u0628\u064a\u0639 \u0641\u064a \u0627\u0644\u062d\u0635\u0646 \u0645\u0633\u0627\u062d\u0629 2 \u062f\u0648\u0646\u0645 \u0627\u0644\u0633\u0639\u0631 70 \u0627\u0644\u0641 \u062f\u064a\u0646\u0627\u0631"
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["estimated_price_jod"] == 70000
    assert body["confidence"] == "medium"
    assert body["reason"] == "matched_neighborhood_unit_price"
    assert body["method"] == "median_unit_price_baseline"
    assert body["unit_metric"] == "dunum"
    assert body["unit_area"] == 2.0
    assert body["matched_unit_price_jod"] == 35000.0
    assert body["matched_count"] == 1
    assert body["model_version"] == "api-baseline-median-unit-price-v0.1"
    assert body["parsed"]["property_type"] == "land"
    assert body["quality"]["is_model_ready"] is True


def test_baseline_valuation_endpoint_returns_reason_when_missing_fields() -> None:
    response = client.post(
        "/ai/baseline-valuation",
        json={
            "text": "\u0634\u0642\u0629 \u0644\u0644\u0627\u064a\u062c\u0627\u0631 \u0642\u0631\u0628 \u062c\u0627\u0645\u0639\u0629 \u0627\u0644\u064a\u0631\u0645\u0648\u0643 \u0627\u0644\u0633\u0639\u0631 200 \u062f\u064a\u0646\u0627\u0631"
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["estimated_price_jod"] is None
    assert body["confidence"] == "low"
    assert body["reason"] == "missing_required_prediction_fields"
    assert body["matched_count"] == 0
    assert body["parsed"]["property_type"] == "apartment"
    assert "area_sqm" in body["quality"]["missing_fields"]


def test_ai_valuation_endpoint_uses_learned_model_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    rows = build_modeling_rows(load_parsed_posts(DEFAULT_INPUT), model_ready_only=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        dataset_path = tmp_path / "valuation_modeling_dataset.csv"
        model_output = tmp_path / "valuation_ml_model.joblib"
        report_output = tmp_path / "valuation_ml_experiment.json"
        write_modeling_dataset(rows, dataset_path)
        run_valuation_ml_experiment(
            dataset_path,
            model_output=model_output,
            report_output=report_output,
        )

        monkeypatch.setattr(learned_valuation, "MODEL_ARTIFACT", model_output)
        response = client.post("/ai/valuation", json={"text": rows[0]["raw_text"]})

    assert response.status_code == 200
    body = response.json()
    assert body["method"] == "sklearn_ridge_text_regressor"
    assert body["model_version"] == "sklearn-ridge-text-v0.1"
    assert body["estimated_price_jod"] is not None
    assert body["training_rows"] == len(rows)
    assert body["feature_completeness"] > 0


def test_ingest_raw_listing_posts_endpoint() -> None:
    response = client.post(
        "/ai/ingest-raw-listing-posts",
        json={
            "items": [
                {
                    "source": "manual_seed",
                    "external_id": "api-ingest-001",
                    "text": "ارض للبيع في الحصن مساحة 2 دونم السعر 70 الف دينار قابل للتفاوض",
                }
            ]
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    record = body["items"][0]
    assert record["source"] == "manual_seed"
    assert record["external_id"] == "api-ingest-001"
    assert record["ingest_status"] == "created"
    assert len(record["raw_text_fingerprint"]) == 64
    assert record["parser_version"] == "irbid-dialect-parser-v0.1"
    assert record["parsed"]["property_type"] == "land"
    assert record["parsed"]["price_jod"] == 70000
    assert record["parsed"]["neighborhoods"][0]["key"] == "al_husn"
    assert record["parsed"]["quality"]["grade"] == "high"


def test_ingest_raw_listing_posts_marks_duplicates() -> None:
    payload = {
        "items": [
            {
                "source": "manual_seed",
                "external_id": "api-duplicate-001",
                "text": "شقة للايجار قرب جامعة اليرموك السعر 200 دينار",
            },
            {
                "source": "manual_seed",
                "external_id": "api-duplicate-001",
                "text": "شقة للايجار قرب جامعة اليرموك السعر 200 دينار",
            },
        ]
    }

    response = client.post("/ai/ingest-raw-listing-posts", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["items"][0]["ingest_status"] == "created"
    assert body["items"][1]["ingest_status"] == "duplicate"
    assert body["items"][0]["id"] == body["items"][1]["id"]


def test_profile_behavior_recommendation_feedback_and_lead_room_flow() -> None:
    headers = {"x-demo-user": "test-user"}

    profile_response = client.put(
        "/profiles/buyer-investor",
        headers=headers,
        json={
            "budget_max_jod": 900000,
            "preferred_cities": ["Amman"],
            "preferred_neighborhoods": ["Abdoun"],
            "property_types": ["villa"],
            "purpose": "investment",
        },
    )
    assert profile_response.status_code == 200

    listings_response = client.get("/listings", headers=headers)
    listing_id = listings_response.json()["items"][0]["id"]
    UUID(listing_id)

    behavior_response = client.post(
        "/behavior-events",
        headers=headers,
        json={"event_type": "listing_viewed", "listing_id": listing_id},
    )
    assert behavior_response.status_code == 200

    recommendations_response = client.get("/recommendations", headers=headers)
    assert recommendations_response.status_code == 200
    recommendations = recommendations_response.json()
    assert recommendations[0]["reason_codes"]
    assert "placeholder" in recommendations[0]["explanation"].lower()

    feedback_response = client.post(
        f"/listings/{listing_id}/feedback",
        headers=headers,
        json={
            "clarity_rating": 4,
            "photo_quality_rating": 3,
            "price_trust_rating": 4,
            "location_confidence_rating": 4,
            "interest_level": "interested",
            "missing_information": ["floor_plan"],
        },
    )
    assert feedback_response.status_code == 200

    feedback_summary_response = client.get(f"/listings/{listing_id}/feedback-summary", headers=headers)
    assert feedback_summary_response.status_code == 200
    assert feedback_summary_response.json()["top_missing_information"] == ["floor_plan"]

    lead_room_response = client.post(
        "/lead-rooms",
        headers=headers,
        json={
            "listing_id": listing_id,
            "intent": "viewing",
            "budget_fit": "inside_budget",
            "preferred_contact_method": "lead_room",
        },
    )
    assert lead_room_response.status_code == 200
    assert lead_room_response.json()["stage"] == "new_inquiry"


def test_limit_counter_blocks_after_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeRedis:
        def __init__(self) -> None:
            self.counts: dict[str, int] = {}

        def incr(self, key: str) -> int:
            self.counts[key] = self.counts.get(key, 0) + 1
            return self.counts[key]

        def expire(self, key: str, seconds: int) -> None:
            return None

    fake = FakeRedis()
    monkeypatch.setattr(limits, "get_redis_client", lambda: fake)

    limits.enforce_limit("test", "user-1", limit=2, seconds=60)
    limits.enforce_limit("test", "user-1", limit=2, seconds=60)

    with pytest.raises(HTTPException) as exc:
        limits.enforce_limit("test", "user-1", limit=2, seconds=60)

    assert exc.value.status_code == 429
