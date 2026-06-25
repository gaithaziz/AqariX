from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


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
