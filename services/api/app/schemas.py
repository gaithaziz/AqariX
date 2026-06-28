from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class PropertyType(StrEnum):
    apartment = "apartment"
    villa = "villa"
    commercial = "commercial"
    land = "land"


class Listing(BaseModel):
    id: UUID
    title: str
    city: str
    neighborhood: str
    property_type: PropertyType
    asking_price_jod: int
    area_sqm: int
    bedrooms: int | None = None
    bathrooms: int | None = None
    aqari_score: float
    confidence: str
    price_signal: str
    image_url: str


class ListingIn(BaseModel):
    title: str
    city: str
    neighborhood: str
    property_type: PropertyType
    asking_price_jod: int = Field(gt=0)
    area_sqm: int = Field(gt=0)
    bedrooms: int | None = None
    bathrooms: int | None = None
    aqari_score: float = Field(default=7.0, ge=0, le=10)
    confidence: str = "medium"
    price_signal: str = "unreviewed"
    image_url: str = ""


class ListingIngestionRequest(BaseModel):
    source: str = "manual"
    listings: list[ListingIn]


class ListingIngestionResult(BaseModel):
    source: str
    imported_count: int
    listing_ids: list[UUID]


class ListingSearchResponse(BaseModel):
    items: list[Listing]
    total: int


class Zone(BaseModel):
    id: str
    city: str
    name: str
    launch_priority: int
    status: str


class BuyerInvestorProfileIn(BaseModel):
    budget_min_jod: int | None = None
    budget_max_jod: int | None = None
    preferred_cities: list[str] = Field(default_factory=list)
    preferred_neighborhoods: list[str] = Field(default_factory=list)
    property_types: list[PropertyType] = Field(default_factory=list)
    purpose: str = "buy"
    risk_tolerance: str = "medium"
    investment_horizon_years: int | None = None


class BuyerInvestorProfile(BuyerInvestorProfileIn):
    id: UUID = Field(default_factory=uuid4)
    user_id: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BehaviorEventIn(BaseModel):
    event_type: str
    listing_id: UUID | None = None
    search_filters: dict[str, object] | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class BehaviorEvent(BehaviorEventIn):
    id: UUID = Field(default_factory=uuid4)
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Recommendation(BaseModel):
    listing: Listing
    recommendation_score: float
    reason_codes: list[str]
    explanation: str
    personalization_confidence: str


class ComparableListing(BaseModel):
    listing: Listing
    similarity_score: float
    price_per_sqm_jod: int
    reason_codes: list[str]
    source_type: str = "demo_listing"


class EvidenceSource(BaseModel):
    source_type: str
    label: str
    url: str | None = None


class OfferingAnalysis(BaseModel):
    id: UUID
    listing_id: UUID
    fair_value_jod: int
    fair_value_confidence: str
    listed_price_gap_pct: float
    bargain_min_jod: int
    bargain_max_jod: int
    forecast_horizon_years: int
    forecast_conservative_jod: int | None = None
    forecast_base_jod: int | None = None
    forecast_optimistic_jod: int | None = None
    location_momentum_score: float | None = None
    liquidity_score: float | None = None
    recommendation_label: str
    comparable_evidence: list[ComparableListing]
    evidence_sources: list[EvidenceSource]
    caveats: list[str]
    model_version: str
    reused_snapshot: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SavedOfferingIn(BaseModel):
    listing_id: UUID


class SavedOffering(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: str
    listing_id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SavedSearchIn(BaseModel):
    name: str
    filters: dict[str, object] = Field(default_factory=dict)
    alerts_enabled: bool = False


class SavedSearch(SavedSearchIn):
    id: UUID = Field(default_factory=uuid4)
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ListingFeedbackIn(BaseModel):
    clarity_rating: int | None = Field(default=None, ge=1, le=5)
    photo_quality_rating: int | None = Field(default=None, ge=1, le=5)
    price_trust_rating: int | None = Field(default=None, ge=1, le=5)
    location_confidence_rating: int | None = Field(default=None, ge=1, le=5)
    interest_level: str | None = None
    missing_information: list[str] = Field(default_factory=list)
    free_text: str | None = None


class ListingFeedback(ListingFeedbackIn):
    id: UUID = Field(default_factory=uuid4)
    listing_id: UUID
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ListingFeedbackSummary(BaseModel):
    listing_id: UUID
    feedback_count: int
    top_missing_information: list[str]
    seller_improvement_notes: list[str]
    investor_note: str | None


class LeadRoomIn(BaseModel):
    listing_id: UUID
    intent: str
    budget_fit: str
    preferred_contact_method: str


class LeadRoom(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    listing_id: UUID
    buyer_user_id: str
    stage: str = "new_inquiry"
    qualification_status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
