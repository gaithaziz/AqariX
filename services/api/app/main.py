from uuid import UUID

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.auth import CurrentUser, get_current_user
from app.repository import (
    create_lead_room,
    get_feedback_summary,
    get_profile,
    get_recommendations,
    record_behavior,
    save_profile,
    search_listings,
    submit_feedback,
)
from app.schemas import (
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
    PropertyType,
    Recommendation,
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
    city: str | None = None,
    neighborhood: str | None = None,
    property_type: PropertyType | None = Query(default=None),
) -> ListingSearchResponse:
    items = search_listings(city=city, neighborhood=neighborhood, property_type=property_type)
    return ListingSearchResponse(items=items, total=len(items))


@app.get("/profiles/buyer-investor", response_model=BuyerInvestorProfile | None)
def read_profile(current_user: CurrentUser = Depends(get_current_user)) -> BuyerInvestorProfile | None:
    return get_profile(current_user.id)


@app.put("/profiles/buyer-investor", response_model=BuyerInvestorProfile)
def upsert_profile(
    payload: BuyerInvestorProfileIn,
    current_user: CurrentUser = Depends(get_current_user),
) -> BuyerInvestorProfile:
    return save_profile(current_user.id, payload)


@app.post("/behavior-events", response_model=BehaviorEvent)
def create_behavior_event(
    payload: BehaviorEventIn,
    current_user: CurrentUser = Depends(get_current_user),
) -> BehaviorEvent:
    return record_behavior(current_user.id, payload)


@app.get("/recommendations", response_model=list[Recommendation])
def recommendations(current_user: CurrentUser = Depends(get_current_user)) -> list[Recommendation]:
    return get_recommendations(current_user.id)


@app.post("/listings/{listing_id}/feedback", response_model=ListingFeedback)
def create_listing_feedback(
    listing_id: UUID,
    payload: ListingFeedbackIn,
    current_user: CurrentUser = Depends(get_current_user),
) -> ListingFeedback:
    return submit_feedback(current_user.id, listing_id, payload)


@app.get("/listings/{listing_id}/feedback-summary", response_model=ListingFeedbackSummary)
def listing_feedback_summary(listing_id: UUID) -> ListingFeedbackSummary:
    return get_feedback_summary(listing_id)


@app.post("/lead-rooms", response_model=LeadRoom)
def start_lead_room(
    payload: LeadRoomIn,
    current_user: CurrentUser = Depends(get_current_user),
) -> LeadRoom:
    return create_lead_room(current_user.id, payload)
