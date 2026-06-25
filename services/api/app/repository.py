from collections import Counter
from uuid import UUID, uuid4

from app.schemas import (
    BehaviorEvent,
    BehaviorEventIn,
    BuyerInvestorProfile,
    BuyerInvestorProfileIn,
    LeadRoom,
    LeadRoomIn,
    Listing,
    ListingFeedback,
    ListingFeedbackIn,
    ListingFeedbackSummary,
    PropertyType,
    Recommendation,
)


LISTINGS = [
    Listing(
        id=UUID("00000000-0000-4000-8000-000000000001"),
        title="Stately Limestone Residence",
        city="Amman",
        neighborhood="Abdoun",
        property_type=PropertyType.villa,
        asking_price_jod=850000,
        area_sqm=602,
        bedrooms=5,
        bathrooms=4,
        aqari_score=9.2,
        confidence="high",
        price_signal="fair_price",
        image_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
    ),
    Listing(
        id=UUID("00000000-0000-4000-8000-000000000002"),
        title="Skyline View Penthouse",
        city="Amman",
        neighborhood="5th Circle",
        property_type=PropertyType.apartment,
        asking_price_jod=245000,
        area_sqm=200,
        bedrooms=3,
        bathrooms=3,
        aqari_score=7.8,
        confidence="medium",
        price_signal="slight_premium",
        image_url="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00",
    ),
    Listing(
        id=UUID("00000000-0000-4000-8000-000000000003"),
        title="Village Prime Retail Space",
        city="Amman",
        neighborhood="Sweifieh",
        property_type=PropertyType.commercial,
        asking_price_jod=1200000,
        area_sqm=420,
        bedrooms=None,
        bathrooms=None,
        aqari_score=8.6,
        confidence="high",
        price_signal="high_demand",
        image_url="https://images.unsplash.com/photo-1494526585095-c41746248156",
    ),
]

profiles: dict[str, BuyerInvestorProfile] = {}
behavior_events: list[BehaviorEvent] = []
listing_feedback: list[ListingFeedback] = []
lead_rooms: list[LeadRoom] = []


def search_listings(
    city: str | None = None,
    neighborhood: str | None = None,
    property_type: PropertyType | None = None,
) -> list[Listing]:
    results = LISTINGS
    if city:
        results = [item for item in results if item.city.lower() == city.lower()]
    if neighborhood:
        results = [item for item in results if item.neighborhood.lower() == neighborhood.lower()]
    if property_type:
        results = [item for item in results if item.property_type == property_type]
    return results


def save_profile(user_id: str, payload: BuyerInvestorProfileIn) -> BuyerInvestorProfile:
    profile = BuyerInvestorProfile(user_id=user_id, **payload.model_dump())
    profiles[user_id] = profile
    return profile


def get_profile(user_id: str) -> BuyerInvestorProfile | None:
    return profiles.get(user_id)


def record_behavior(user_id: str, payload: BehaviorEventIn) -> BehaviorEvent:
    event = BehaviorEvent(user_id=user_id, **payload.model_dump())
    behavior_events.append(event)
    return event


def get_recommendations(user_id: str) -> list[Recommendation]:
    profile = profiles.get(user_id)
    viewed_listing_ids = {event.listing_id for event in behavior_events if event.user_id == user_id}
    recommendations: list[Recommendation] = []

    for listing in LISTINGS:
        score = listing.aqari_score
        reason_codes = ["strong_aqari_score"]

        if profile:
            if listing.city in profile.preferred_cities:
                score += 0.4
                reason_codes.append("matches_city")
            if listing.neighborhood in profile.preferred_neighborhoods:
                score += 0.5
                reason_codes.append("matches_neighborhood")
            if listing.property_type in profile.property_types:
                score += 0.4
                reason_codes.append("matches_property_type")
            if profile.budget_max_jod and listing.asking_price_jod <= profile.budget_max_jod:
                score += 0.3
                reason_codes.append("inside_budget")

        if listing.id in viewed_listing_ids:
            score += 0.2
            reason_codes.append("similar_to_recent_activity")

        recommendations.append(
            Recommendation(
                listing=listing,
                recommendation_score=round(score, 2),
                reason_codes=reason_codes,
                explanation="Deterministic MVP placeholder based on intake and local behavior events.",
                personalization_confidence="medium" if profile else "low",
            )
        )

    return sorted(recommendations, key=lambda item: item.recommendation_score, reverse=True)


def submit_feedback(user_id: str, listing_id: UUID, payload: ListingFeedbackIn) -> ListingFeedback:
    feedback = ListingFeedback(user_id=user_id, listing_id=listing_id, **payload.model_dump())
    listing_feedback.append(feedback)
    record_behavior(
        user_id,
        BehaviorEventIn(
            event_type="listing_feedback_submitted",
            listing_id=listing_id,
            metadata={"feedback_id": str(feedback.id)},
        ),
    )
    return feedback


def get_feedback_summary(listing_id: UUID) -> ListingFeedbackSummary:
    feedback_for_listing = [item for item in listing_feedback if item.listing_id == listing_id]
    missing_counter = Counter(
        tag for feedback in feedback_for_listing for tag in feedback.missing_information
    )
    top_missing = [tag for tag, _count in missing_counter.most_common(3)]
    notes = [f"Improve ad detail for: {tag.replace('_', ' ')}" for tag in top_missing]

    return ListingFeedbackSummary(
        listing_id=listing_id,
        feedback_count=len(feedback_for_listing),
        top_missing_information=top_missing,
        seller_improvement_notes=notes,
        investor_note=(
            "Users are asking for clearer listing details before starting a lead room."
            if len(feedback_for_listing) >= 2
            else None
        ),
    )


def create_lead_room(user_id: str, payload: LeadRoomIn) -> LeadRoom:
    room = LeadRoom(id=uuid4(), buyer_user_id=user_id, **payload.model_dump())
    lead_rooms.append(room)
    record_behavior(
        user_id,
        BehaviorEventIn(
            event_type="lead_room_started",
            listing_id=payload.listing_id,
            metadata={"lead_room_id": str(room.id)},
        ),
    )
    return room
