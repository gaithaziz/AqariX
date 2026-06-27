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


class ListingSearchResponse(BaseModel):
    items: list[Listing]
    total: int


class RawListingTextIn(BaseModel):
    text: str = Field(min_length=1, max_length=5_000)


class RawListingTextBatchIn(BaseModel):
    items: list[RawListingTextIn] = Field(min_length=1, max_length=100)


class ParsedLandmark(BaseModel):
    key: str
    display_name: str
    latitude: float
    longitude: float


class ParsedNeighborhood(BaseModel):
    key: str
    display_name: str


class ParsedListingQuality(BaseModel):
    score: int
    grade: str
    is_model_ready: bool
    missing_fields: list[str]
    warnings: list[str]


class ParsedListingTextResponse(BaseModel):
    original_text: str
    normalized_text: str
    city: str | None
    intent: str
    property_type: str | None
    price_jod: int | None
    price_period: str | None
    negotiable: bool
    area_sqm: int | None
    land_area_dunum: float | None
    bedrooms: int | None
    bathrooms: int | None
    furnished: bool | None
    audiences: list[str]
    motivated_seller: bool
    neighborhoods: list[ParsedNeighborhood]
    landmarks: list[ParsedLandmark]
    location_signals: list[str]
    extracted_terms: list[str]
    quality: ParsedListingQuality


class ParsedListingTextBatchResponse(BaseModel):
    items: list[ParsedListingTextResponse]
    total: int


class RawListingPostIn(BaseModel):
    source: str = Field(min_length=1, max_length=100)
    external_id: str | None = Field(default=None, max_length=200)
    text: str = Field(min_length=1, max_length=5_000)
    source_url: str | None = Field(default=None, max_length=2_000)


class RawListingPostBatchIn(BaseModel):
    items: list[RawListingPostIn] = Field(min_length=1, max_length=100)


class StoredParsedListingRecord(BaseModel):
    id: UUID
    raw_listing_post_id: UUID
    source: str
    external_id: str | None
    raw_text: str
    source_url: str | None
    parser_version: str
    parsed: ParsedListingTextResponse


class StoredParsedListingBatchResponse(BaseModel):
    items: list[StoredParsedListingRecord]
    total: int


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
