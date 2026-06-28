from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.auth import CurrentUser, get_current_user
from app.cache import cache_get_json, cache_key, cache_set_json
from app.limits import enforce_limit, record_usage, request_identity
from app.repository import (
    ANALYSIS_ENGINE_VERSION,
    create_lead_room,
    get_comparable_listings,
    get_feedback_summary,
    get_listing,
    get_or_create_offering_analysis,
    get_profile,
    get_recommendations,
    ingest_listings,
    list_saved_offerings,
    list_saved_searches,
    list_zones,
    record_behavior,
    remove_saved_offering,
    save_profile,
    save_offering,
    save_search,
    search_listings,
    submit_feedback,
)
from app.schemas import (
    BehaviorEvent,
    BehaviorEventIn,
    BuyerInvestorProfile,
    BuyerInvestorProfileIn,
    ComparableListing,
    LeadRoom,
    LeadRoomIn,
    ListingIngestionRequest,
    ListingIngestionResult,
    ListingFeedback,
    ListingFeedbackIn,
    ListingFeedbackSummary,
    ListingSearchResponse,
    OfferingAnalysis,
    PropertyType,
    Recommendation,
    SavedOffering,
    SavedOfferingIn,
    SavedSearch,
    SavedSearchIn,
    Zone,
)
from app.settings import get_settings

app = FastAPI(
    title="AqariX API",
    version="0.1.0",
    description="MVP API shell. Analysis-engine outputs are provider agnostic.",
)

idempotency_responses: dict[str, dict[str, object]] = {}

settings = get_settings()
web_dist = Path(__file__).resolve().parent.parent / "web-dist"
web_index = web_dist / "index.html"

if (web_dist / "assets").exists():
    app.mount("/assets", StaticFiles(directory=web_dist / "assets"), name="assets")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "env": settings.app_env}


@app.get("/", response_model=None)
def root():
    if web_index.exists():
        return FileResponse(web_index)
    return api_index()


@app.get("/api")
def api_index() -> dict[str, object]:
    settings = get_settings()
    return {
        "name": "AqariX API",
        "status": "ok",
        "env": settings.app_env,
        "endpoints": ["/health", "/listings", "/docs"],
    }


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


@app.post("/listings/ingest", response_model=ListingIngestionResult)
def create_listing_ingestion(
    payload: ListingIngestionRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ListingIngestionResult:
    settings = get_settings()
    enforce_limit("listing-ingest", current_user.id, settings.rate_limit_user_per_minute, 60)
    enforce_limit("listing-ingest-daily", current_user.id, settings.quota_writes_per_day, 86_400)
    record_usage("listing-ingest", settings.cost_alert_requests_per_day)
    return ingest_listings(payload)


@app.get("/zones", response_model=list[Zone])
def zones(
    request: Request,
    city: str | None = None,
) -> list[Zone]:
    settings = get_settings()
    enforce_limit("zone-catalog", request_identity(request), settings.rate_limit_public_per_minute, 60)
    record_usage("zone-catalog", settings.cost_alert_requests_per_day)
    return list_zones(city)


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


@app.get("/saved-offerings", response_model=list[SavedOffering])
def read_saved_offerings(current_user: CurrentUser = Depends(get_current_user)) -> list[SavedOffering]:
    settings = get_settings()
    enforce_limit("saved-offerings-read", current_user.id, settings.rate_limit_user_per_minute, 60)
    record_usage("saved-offerings-read", settings.cost_alert_requests_per_day)
    return list_saved_offerings(current_user.id)


@app.post("/saved-offerings", response_model=SavedOffering)
def create_saved_offering(
    payload: SavedOfferingIn,
    current_user: CurrentUser = Depends(get_current_user),
) -> SavedOffering:
    settings = get_settings()
    enforce_limit("saved-offering-write", current_user.id, settings.rate_limit_user_per_minute, 60)
    enforce_limit("saved-offering-write-daily", current_user.id, settings.quota_writes_per_day, 86_400)
    record_usage("saved-offering-write", settings.cost_alert_requests_per_day)
    if not get_listing(payload.listing_id):
        raise HTTPException(status_code=404, detail="Listing not found")
    return save_offering(current_user.id, payload)


@app.delete("/saved-offerings/{saved_id}", status_code=204)
def delete_saved_offering(
    saved_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    settings = get_settings()
    enforce_limit("saved-offering-delete", current_user.id, settings.rate_limit_user_per_minute, 60)
    enforce_limit("saved-offering-delete-daily", current_user.id, settings.quota_writes_per_day, 86_400)
    record_usage("saved-offering-delete", settings.cost_alert_requests_per_day)
    if not remove_saved_offering(current_user.id, saved_id):
        raise HTTPException(status_code=404, detail="Saved offering not found")


@app.get("/saved-searches", response_model=list[SavedSearch])
def read_saved_searches(current_user: CurrentUser = Depends(get_current_user)) -> list[SavedSearch]:
    settings = get_settings()
    enforce_limit("saved-searches-read", current_user.id, settings.rate_limit_user_per_minute, 60)
    record_usage("saved-searches-read", settings.cost_alert_requests_per_day)
    return list_saved_searches(current_user.id)


@app.post("/saved-searches", response_model=SavedSearch)
def create_saved_search(
    payload: SavedSearchIn,
    current_user: CurrentUser = Depends(get_current_user),
) -> SavedSearch:
    settings = get_settings()
    enforce_limit("saved-search-write", current_user.id, settings.rate_limit_user_per_minute, 60)
    enforce_limit("saved-search-write-daily", current_user.id, settings.quota_writes_per_day, 86_400)
    record_usage("saved-search-write", settings.cost_alert_requests_per_day)
    return save_search(current_user.id, payload)


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


@app.get("/listings/{listing_id}/comparables", response_model=list[ComparableListing])
def listing_comparables(request: Request, listing_id: UUID) -> list[ComparableListing]:
    settings = get_settings()
    enforce_limit(
        "listing-comparables",
        request_identity(request),
        settings.rate_limit_public_per_minute,
        60,
    )
    record_usage("listing-comparables", settings.cost_alert_requests_per_day)
    return get_comparable_listings(listing_id)


@app.post("/listings/{listing_id}/analysis", response_model=OfferingAnalysis)
def create_offering_analysis(
    listing_id: UUID,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    current_user: CurrentUser = Depends(get_current_user),
) -> OfferingAnalysis:
    settings = get_settings()
    enforce_limit("offering-analysis", current_user.id, settings.rate_limit_user_per_minute, 60)
    enforce_limit("offering-analysis-daily", current_user.id, settings.quota_writes_per_day, 86_400)
    record_usage("offering-analysis", settings.cost_alert_requests_per_day)

    replay = _get_idempotent_response("offering-analysis", current_user.id, idempotency_key)
    if replay is not None:
        return OfferingAnalysis.model_validate(replay)

    key = cache_key("offering-analysis", {"listing_id": listing_id, "version": ANALYSIS_ENGINE_VERSION})
    cached = cache_get_json(key)
    if cached is not None:
        analysis = OfferingAnalysis.model_validate(cached).model_copy(update={"reused_snapshot": True})
        _save_idempotent_response("offering-analysis", current_user.id, idempotency_key, analysis.model_dump(mode="json"))
        return analysis

    analysis = get_or_create_offering_analysis(listing_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Listing not found")

    cache_set_json(key, analysis.model_dump(mode="json"), ttl_seconds=300)
    _save_idempotent_response("offering-analysis", current_user.id, idempotency_key, analysis.model_dump(mode="json"))
    return analysis


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
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    current_user: CurrentUser = Depends(get_current_user),
) -> LeadRoom:
    settings = get_settings()
    enforce_limit("lead-room", current_user.id, settings.rate_limit_user_per_minute, 60)
    enforce_limit("lead-room-daily", current_user.id, settings.quota_lead_rooms_per_day, 86_400)
    record_usage("lead-room", settings.cost_alert_requests_per_day)
    replay = _get_idempotent_response("lead-room", current_user.id, idempotency_key)
    if replay is not None:
        return LeadRoom.model_validate(replay)
    room = create_lead_room(current_user.id, payload)
    _save_idempotent_response("lead-room", current_user.id, idempotency_key, room.model_dump(mode="json"))
    return room


@app.get("/{path:path}", response_model=None)
def web_fallback(path: str):
    target = (web_dist / path).resolve()
    if web_dist.resolve() in target.parents and target.is_file():
        return FileResponse(target)
    if web_index.exists():
        return FileResponse(web_index)
    raise HTTPException(status_code=404, detail="Not Found")


def _idempotency_cache_key(scope: str, user_id: str, key: str) -> str:
    return cache_key("idempotency", {"scope": scope, "user_id": user_id, "key": key})


def _get_idempotent_response(scope: str, user_id: str, key: str | None) -> dict[str, object] | None:
    if not key:
        return None
    cache_id = _idempotency_cache_key(scope, user_id, key)
    cached = cache_get_json(cache_id)
    if cached is not None:
        return cached
    return idempotency_responses.get(cache_id)


def _save_idempotent_response(
    scope: str,
    user_id: str,
    key: str | None,
    response: dict[str, object],
) -> None:
    if not key:
        return
    cache_id = _idempotency_cache_key(scope, user_id, key)
    idempotency_responses[cache_id] = response
    cache_set_json(cache_id, response, ttl_seconds=86_400)
