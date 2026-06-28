from uuid import UUID

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import cache
from app import limits
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def disable_redis(monkeypatch: pytest.MonkeyPatch) -> None:
    cache.get_redis_client.cache_clear()
    monkeypatch.setattr(cache, "get_redis_client", lambda: None)
    monkeypatch.setattr(limits, "get_redis_client", lambda: None)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_index() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "AqariX API"
    assert "/health" in response.json()["endpoints"]


def test_api_index() -> None:
    response = client.get("/api")

    assert response.status_code == 200
    assert response.json()["name"] == "AqariX API"


def test_listing_search() -> None:
    response = client.get("/listings", params={"city": "Irbid"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert body["items"][0]["city"] == "Irbid"


def test_zone_catalog_and_listing_ingestion() -> None:
    headers = {"x-demo-user": "ingestion-user"}

    zones_response = client.get("/zones", params={"city": "Irbid"})
    assert zones_response.status_code == 200
    assert zones_response.json()[0]["city"] == "Irbid"

    ingestion_response = client.post(
        "/listings/ingest",
        headers=headers,
        json={
            "source": "test-fixture",
            "listings": [
                {
                    "title": "Irbid Test Garden Flat",
                    "city": "Irbid",
                    "neighborhood": "Al Huson",
                    "property_type": "apartment",
                    "asking_price_jod": 88000,
                    "area_sqm": 120,
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "aqari_score": 7.2,
                    "confidence": "medium",
                    "price_signal": "unreviewed",
                    "image_url": "https://example.com/irbid-test.jpg",
                }
            ],
        },
    )
    assert ingestion_response.status_code == 200
    assert ingestion_response.json()["imported_count"] == 1

    search_response = client.get("/listings", params={"neighborhood": "Al Huson"})
    assert search_response.status_code == 200
    assert search_response.json()["items"][0]["title"] == "Irbid Test Garden Flat"


def test_cors_allows_vercel_web_origin() -> None:
    response = client.options(
        "/listings",
        headers={
            "origin": "https://aqari-x.vercel.app",
            "access-control-request-method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://aqari-x.vercel.app"


def test_profile_behavior_recommendation_feedback_and_lead_room_flow() -> None:
    headers = {"x-demo-user": "test-user"}

    profile_response = client.put(
        "/profiles/buyer-investor",
        headers=headers,
        json={
            "budget_max_jod": 900000,
            "preferred_cities": ["Irbid"],
            "preferred_neighborhoods": ["Al Hay Al Sharqi"],
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

    comparables_response = client.get(f"/listings/{listing_id}/comparables", headers=headers)
    assert comparables_response.status_code == 200
    assert comparables_response.json()[0]["price_per_sqm_jod"] > 0

    analysis_response = client.post(f"/listings/{listing_id}/analysis", headers=headers)
    assert analysis_response.status_code == 200
    analysis = analysis_response.json()
    assert analysis["fair_value_confidence"] in {"low", "medium"}
    assert analysis["comparable_evidence"]
    assert analysis["caveats"]
    assert analysis["model_version"] == "deterministic-phase1-shell-v1"

    reused_analysis_response = client.post(f"/listings/{listing_id}/analysis", headers=headers)
    assert reused_analysis_response.status_code == 200
    assert reused_analysis_response.json()["reused_snapshot"] is True

    idempotent_analysis_headers = {**headers, "Idempotency-Key": "analysis-key-1"}
    idempotent_analysis_response = client.post(
        f"/listings/{listing_id}/analysis",
        headers=idempotent_analysis_headers,
    )
    replayed_analysis_response = client.post(
        f"/listings/{listing_id}/analysis",
        headers=idempotent_analysis_headers,
    )
    assert idempotent_analysis_response.status_code == 200
    assert replayed_analysis_response.status_code == 200
    assert replayed_analysis_response.json()["id"] == idempotent_analysis_response.json()["id"]

    saved_offering_response = client.post(
        "/saved-offerings",
        headers=headers,
        json={"listing_id": listing_id},
    )
    assert saved_offering_response.status_code == 200
    saved_offering = saved_offering_response.json()

    saved_offerings_response = client.get("/saved-offerings", headers=headers)
    assert saved_offerings_response.status_code == 200
    assert saved_offerings_response.json()[0]["listing_id"] == listing_id

    saved_search_response = client.post(
        "/saved-searches",
        headers=headers,
        json={
            "name": "Irbid villas under 900k",
            "filters": {"city": "Irbid", "property_type": "villa", "budget_max_jod": 900000},
            "alerts_enabled": True,
        },
    )
    assert saved_search_response.status_code == 200

    saved_searches_response = client.get("/saved-searches", headers=headers)
    assert saved_searches_response.status_code == 200
    assert saved_searches_response.json()[0]["name"] == "Irbid villas under 900k"

    delete_saved_response = client.delete(
        f"/saved-offerings/{saved_offering['id']}",
        headers=headers,
    )
    assert delete_saved_response.status_code == 204

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
        headers={**headers, "Idempotency-Key": "lead-room-key-1"},
        json={
            "listing_id": listing_id,
            "intent": "viewing",
            "budget_fit": "inside_budget",
            "preferred_contact_method": "lead_room",
        },
    )
    assert lead_room_response.status_code == 200
    assert lead_room_response.json()["stage"] == "new_inquiry"

    replayed_lead_room_response = client.post(
        "/lead-rooms",
        headers={**headers, "Idempotency-Key": "lead-room-key-1"},
        json={
            "listing_id": listing_id,
            "intent": "viewing",
            "budget_fit": "inside_budget",
            "preferred_contact_method": "lead_room",
        },
    )
    assert replayed_lead_room_response.status_code == 200
    assert replayed_lead_room_response.json()["id"] == lead_room_response.json()["id"]


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
