from collections import Counter
from uuid import UUID, uuid4

from app.schemas import (
    BehaviorEvent,
    BehaviorEventIn,
    BuyerInvestorProfile,
    BuyerInvestorProfileIn,
    ComparableListing,
    EvidenceSource,
    LeadRoom,
    LeadRoomIn,
    Listing,
    ListingFeedback,
    ListingFeedbackIn,
    ListingFeedbackSummary,
    OfferingAnalysis,
    PropertyType,
    Recommendation,
)


LISTINGS = [
    Listing(
        id=UUID("00000000-0000-4000-8000-000000000001"),
        title="Irbid Hills Limestone Residence",
        city="Irbid",
        neighborhood="Al Hay Al Sharqi",
        property_type=PropertyType.villa,
        asking_price_jod=420000,
        area_sqm=480,
        bedrooms=5,
        bathrooms=4,
        aqari_score=9.1,
        confidence="high",
        price_signal="fair_price",
        image_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
    ),
    Listing(
        id=UUID("00000000-0000-4000-8000-000000000002"),
        title="University District Apartment",
        city="Irbid",
        neighborhood="University District",
        property_type=PropertyType.apartment,
        asking_price_jod=125000,
        area_sqm=165,
        bedrooms=3,
        bathrooms=3,
        aqari_score=8.0,
        confidence="medium",
        price_signal="fair_price",
        image_url="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00",
    ),
    Listing(
        id=UUID("00000000-0000-4000-8000-000000000003"),
        title="City Center Retail Space",
        city="Irbid",
        neighborhood="City Center",
        property_type=PropertyType.commercial,
        asking_price_jod=540000,
        area_sqm=310,
        bedrooms=None,
        bathrooms=None,
        aqari_score=8.5,
        confidence="high",
        price_signal="high_demand",
        image_url="https://images.unsplash.com/photo-1494526585095-c41746248156",
    ),
]

profiles: dict[str, BuyerInvestorProfile] = {}
behavior_events: list[BehaviorEvent] = []
listing_feedback: list[ListingFeedback] = []
lead_rooms: list[LeadRoom] = []
analysis_snapshots: dict[UUID, OfferingAnalysis] = {}


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


def get_listing(listing_id: UUID) -> Listing | None:
    return next((listing for listing in LISTINGS if listing.id == listing_id), None)


def get_comparable_listings(listing_id: UUID, limit: int = 3) -> list[ComparableListing]:
    target = get_listing(listing_id)
    if not target:
        return []

    comparables: list[ComparableListing] = []
    target_price_per_sqm = target.asking_price_jod / target.area_sqm

    for listing in LISTINGS:
        if listing.id == target.id:
            continue

        score = 0.0
        reason_codes: list[str] = []

        if listing.city == target.city:
            score += 0.3
            reason_codes.append("same_city")
        if listing.neighborhood == target.neighborhood:
            score += 0.25
            reason_codes.append("same_neighborhood")
        if listing.property_type == target.property_type:
            score += 0.25
            reason_codes.append("same_property_type")

        area_gap = abs(listing.area_sqm - target.area_sqm) / max(target.area_sqm, 1)
        if area_gap <= 0.35:
            score += 0.1
            reason_codes.append("similar_area")

        listing_price_per_sqm = listing.asking_price_jod / listing.area_sqm
        price_gap = abs(listing_price_per_sqm - target_price_per_sqm) / max(target_price_per_sqm, 1)
        if price_gap <= 0.35:
            score += 0.1
            reason_codes.append("similar_price_per_sqm")

        comparables.append(
            ComparableListing(
                listing=listing,
                similarity_score=round(score, 2),
                price_per_sqm_jod=round(listing_price_per_sqm),
                reason_codes=reason_codes or ["same_demo_market"],
            )
        )

    return sorted(comparables, key=lambda comparable: comparable.similarity_score, reverse=True)[:limit]


def get_or_create_offering_analysis(listing_id: UUID) -> OfferingAnalysis | None:
    if listing_id in analysis_snapshots:
        snapshot = analysis_snapshots[listing_id].model_copy(update={"reused_snapshot": True})
        analysis_snapshots[listing_id] = snapshot
        return snapshot

    listing = get_listing(listing_id)
    if not listing:
        return None

    comparables = get_comparable_listings(listing_id)
    prices_per_sqm = [item.price_per_sqm_jod for item in comparables]
    target_price_per_sqm = round(listing.asking_price_jod / listing.area_sqm)
    if prices_per_sqm:
        benchmark_price_per_sqm = round(sum(prices_per_sqm) / len(prices_per_sqm))
    else:
        benchmark_price_per_sqm = target_price_per_sqm

    fair_value = benchmark_price_per_sqm * listing.area_sqm
    listed_price_gap_pct = round(((listing.asking_price_jod - fair_value) / listing.asking_price_jod) * 100, 2)
    confidence = "medium" if len(comparables) >= 2 else "low"
    recommendation = "review" if abs(listed_price_gap_pct) <= 10 else ("watch" if listed_price_gap_pct > 10 else "opportunity")

    analysis = OfferingAnalysis(
        id=uuid4(),
        listing_id=listing_id,
        fair_value_jod=round(fair_value),
        fair_value_confidence=confidence,
        listed_price_gap_pct=listed_price_gap_pct,
        bargain_min_jod=round(fair_value * 0.96),
        bargain_max_jod=round(fair_value * 1.02),
        forecast_horizon_years=0,
        location_momentum_score=None,
        liquidity_score=None,
        recommendation_label=recommendation,
        comparable_evidence=comparables,
        evidence_sources=[
            EvidenceSource(source_type="demo_listing", label="Irbid demo listing set"),
            EvidenceSource(source_type="user_feedback", label="Aggregated listing feedback summary"),
        ],
        caveats=[
            "Deterministic non-AI shell for Phase 1 API integration.",
            "No AVM, forecast, or model-backed valuation has been run.",
            "Demo comparables are based on the current seeded listing set only.",
        ],
        model_version="deterministic-phase1-shell-v1",
    )
    analysis_snapshots[listing_id] = analysis
    return analysis


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
