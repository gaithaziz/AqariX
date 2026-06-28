from uuid import UUID

from fastapi import Depends, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from app.auth import CurrentUser, get_current_user
from app.cache import cache_get_json, cache_key, cache_set_json
from app.limits import enforce_limit, record_usage, request_identity
from app.nlp.baseline_valuation import estimate_baseline_valuation
from app.nlp.dialect_parser import parse_listing_text
from app.repository import (
    create_lead_room,
    get_feedback_summary,
    get_profile,
    get_recommendations,
    ingest_raw_listing_posts,
    parsed_to_response,
    record_behavior,
    save_profile,
    search_listings,
    submit_feedback,
)
from app.schemas import (
    BaselineValuationResponse,
    BehaviorEvent,
    BehaviorEventIn,
    BuyerInvestorProfile,
    BuyerInvestorProfileIn,
    LeadRoom,
    LeadRoomIn,
    ListingFeedback,
    ListingFeedbackIn,
    ListingFeedbackSummary,
    ListingSearchResponse,
    ParsedListingTextBatchResponse,
    ParsedListingTextResponse,
    ParsedListingQuality,
    PropertyType,
    RawListingPostBatchIn,
    RawListingTextBatchIn,
    RawListingTextIn,
    Recommendation,
    StoredParsedListingBatchResponse,
)
from app.settings import get_settings

app = FastAPI(
    title="AqariX API",
    version="0.1.0",
    description="MVP API shell. AI valuation and forecasting are intentionally not implemented.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "env": settings.app_env}


@app.get("/listings", response_model=ListingSearchResponse)
def listings(
    request: Request,
    city: str | None = None,
    neighborhood: str | None = None,
    property_type: PropertyType | None = Query(default=None),
) -> ListingSearchResponse:
    settings = get_settings()
    enforce_limit(
        "listing-search",
        request_identity(request),
        settings.rate_limit_public_per_minute,
        60,
    )
    record_usage("listing-search", settings.cost_alert_requests_per_day)

    key = cache_key(
        "listing-search",
        {"city": city, "neighborhood": neighborhood, "property_type": property_type},
    )
    cached = cache_get_json(key)
    if cached is not None:
        return ListingSearchResponse.model_validate(cached)

    items = search_listings(city=city, neighborhood=neighborhood, property_type=property_type)
    response = ListingSearchResponse(items=items, total=len(items))
    cache_set_json(key, response.model_dump(mode="json"), ttl_seconds=60)
    return response


@app.post("/ai/parse-listing-text", response_model=ParsedListingTextResponse)
def parse_raw_listing_text(request: Request, payload: RawListingTextIn) -> ParsedListingTextResponse:
    settings = get_settings()
    enforce_limit(
        "ai-parse-listing-text",
        request_identity(request),
        settings.rate_limit_public_per_minute,
        60,
    )
    record_usage("ai-parse-listing-text", settings.cost_alert_requests_per_day)
    return parsed_to_response(parse_listing_text(payload.text))


@app.post("/ai/parse-listing-text/batch", response_model=ParsedListingTextBatchResponse)
def parse_raw_listing_text_batch(
    request: Request,
    payload: RawListingTextBatchIn,
) -> ParsedListingTextBatchResponse:
    settings = get_settings()
    enforce_limit(
        "ai-parse-listing-text-batch",
        request_identity(request),
        settings.rate_limit_public_per_minute,
        60,
    )
    record_usage("ai-parse-listing-text-batch", settings.cost_alert_requests_per_day)
    items = [parsed_to_response(parse_listing_text(item.text)) for item in payload.items]
    return ParsedListingTextBatchResponse(items=items, total=len(items))


@app.post("/ai/baseline-valuation", response_model=BaselineValuationResponse)
def estimate_raw_listing_value(
    request: Request,
    payload: RawListingTextIn,
) -> BaselineValuationResponse:
    settings = get_settings()
    enforce_limit(
        "ai-baseline-valuation",
        request_identity(request),
        settings.rate_limit_public_per_minute,
        60,
    )
    record_usage("ai-baseline-valuation", settings.cost_alert_requests_per_day)
    valuation = estimate_baseline_valuation(payload.text)
    return BaselineValuationResponse(
        estimated_price_jod=valuation.estimated_price_jod,
        confidence=valuation.confidence,
        reason=valuation.reason,
        method=valuation.method,
        unit_metric=valuation.unit_metric,
        unit_area=valuation.unit_area,
        matched_unit_price_jod=valuation.matched_unit_price_jod,
        matched_count=valuation.matched_count,
        model_version=valuation.model_version,
        quality=ParsedListingQuality(
            score=valuation.quality.score,
            grade=valuation.quality.grade,
            is_model_ready=valuation.quality.is_model_ready,
            missing_fields=valuation.quality.missing_fields,
            warnings=valuation.quality.warnings,
        ),
        parsed=parsed_to_response(valuation.parsed),
    )


@app.post("/ai/ingest-raw-listing-posts", response_model=StoredParsedListingBatchResponse)
def ingest_raw_listing_posts_endpoint(
    request: Request,
    payload: RawListingPostBatchIn,
) -> StoredParsedListingBatchResponse:
    settings = get_settings()
    enforce_limit(
        "ai-ingest-raw-listing-posts",
        request_identity(request),
        settings.rate_limit_public_per_minute,
        60,
    )
    record_usage("ai-ingest-raw-listing-posts", settings.cost_alert_requests_per_day)
    return ingest_raw_listing_posts(payload)


@app.get("/profiles/buyer-investor", response_model=BuyerInvestorProfile | None)
def read_profile(current_user: CurrentUser = Depends(get_current_user)) -> BuyerInvestorProfile | None:
    return get_profile(current_user.id)


@app.put("/profiles/buyer-investor", response_model=BuyerInvestorProfile)
def upsert_profile(
    payload: BuyerInvestorProfileIn,
    current_user: CurrentUser = Depends(get_current_user),
) -> BuyerInvestorProfile:
    settings = get_settings()
    enforce_limit("profile-write", current_user.id, settings.rate_limit_user_per_minute, 60)
    enforce_limit("profile-write-daily", current_user.id, settings.quota_writes_per_day, 86_400)
    record_usage("profile-write", settings.cost_alert_requests_per_day)
    return save_profile(current_user.id, payload)


@app.post("/behavior-events", response_model=BehaviorEvent)
def create_behavior_event(
    payload: BehaviorEventIn,
    current_user: CurrentUser = Depends(get_current_user),
) -> BehaviorEvent:
    settings = get_settings()
    enforce_limit("behavior-event", current_user.id, settings.rate_limit_user_per_minute, 60)
    enforce_limit("behavior-event-daily", current_user.id, settings.quota_writes_per_day, 86_400)
    record_usage("behavior-event", settings.cost_alert_requests_per_day)
    return record_behavior(current_user.id, payload)


@app.get("/recommendations", response_model=list[Recommendation])
def recommendations(
    current_user: CurrentUser = Depends(get_current_user),
) -> list[Recommendation]:
    settings = get_settings()
    enforce_limit("recommendations", current_user.id, settings.rate_limit_user_per_minute, 60)
    record_usage("recommendations", settings.cost_alert_requests_per_day)
    return get_recommendations(current_user.id)


@app.post("/listings/{listing_id}/feedback", response_model=ListingFeedback)
def create_listing_feedback(
    listing_id: UUID,
    payload: ListingFeedbackIn,
    current_user: CurrentUser = Depends(get_current_user),
) -> ListingFeedback:
    settings = get_settings()
    enforce_limit("listing-feedback", current_user.id, settings.rate_limit_user_per_minute, 60)
    enforce_limit("listing-feedback-daily", current_user.id, settings.quota_writes_per_day, 86_400)
    record_usage("listing-feedback", settings.cost_alert_requests_per_day)
    return submit_feedback(current_user.id, listing_id, payload)


@app.get("/listings/{listing_id}/feedback-summary", response_model=ListingFeedbackSummary)
def listing_feedback_summary(request: Request, listing_id: UUID) -> ListingFeedbackSummary:
    settings = get_settings()
    enforce_limit(
        "feedback-summary",
        request_identity(request),
        settings.rate_limit_public_per_minute,
        60,
    )
    record_usage("feedback-summary", settings.cost_alert_requests_per_day)

    key = cache_key("feedback-summary", {"listing_id": listing_id})
    cached = cache_get_json(key)
    if cached is not None:
        return ListingFeedbackSummary.model_validate(cached)

    response = get_feedback_summary(listing_id)
    cache_set_json(key, response.model_dump(mode="json"), ttl_seconds=30)
    return response


@app.post("/lead-rooms", response_model=LeadRoom)
def start_lead_room(
    payload: LeadRoomIn,
    current_user: CurrentUser = Depends(get_current_user),
) -> LeadRoom:
    settings = get_settings()
    enforce_limit("lead-room", current_user.id, settings.rate_limit_user_per_minute, 60)
    enforce_limit("lead-room-daily", current_user.id, settings.quota_lead_rooms_per_day, 86_400)
    record_usage("lead-room", settings.cost_alert_requests_per_day)
    return create_lead_room(current_user.id, payload)
