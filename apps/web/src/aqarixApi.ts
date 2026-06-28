export type PropertyType = 'apartment' | 'villa' | 'commercial' | 'land'

export type Listing = {
  id: string
  title: string
  city: string
  neighborhood: string
  property_type: PropertyType
  asking_price_jod: number
  area_sqm: number
  bedrooms: number | null
  bathrooms: number | null
  aqari_score: number
  confidence: string
  price_signal: string
  image_url: string
}

export type ListingSearchResponse = {
  items: Listing[]
  total: number
}

export type BuyerInvestorProfileIn = {
  budget_min_jod: number | null
  budget_max_jod: number | null
  preferred_cities: string[]
  preferred_neighborhoods: string[]
  property_types: PropertyType[]
  purpose: string
  risk_tolerance: string
  investment_horizon_years: number | null
}

export type BuyerInvestorProfile = BuyerInvestorProfileIn & {
  id: string
  user_id: string
  updated_at: string
}

export type Recommendation = {
  listing: Listing
  recommendation_score: number
  reason_codes: string[]
  explanation: string
  personalization_confidence: string
}

export type ListingFeedbackIn = {
  clarity_rating: number | null
  photo_quality_rating: number | null
  price_trust_rating: number | null
  location_confidence_rating: number | null
  interest_level: string | null
  missing_information: string[]
  free_text: string | null
}

export type ListingFeedback = ListingFeedbackIn & {
  id: string
  listing_id: string
  user_id: string
  created_at: string
}

export type ListingFeedbackSummary = {
  listing_id: string
  feedback_count: number
  top_missing_information: string[]
  seller_improvement_notes: string[]
  investor_note: string | null
}

export type LeadRoomIn = {
  listing_id: string
  intent: string
  budget_fit: string
  preferred_contact_method: string
}

export type LeadRoom = {
  id: string
  listing_id: string
  buyer_user_id: string
  stage: string
  qualification_status: string
  created_at: string
}

export type ParsedListingQuality = {
  score: number
  grade: string
  is_model_ready: boolean
  missing_fields: string[]
  warnings: string[]
}

export type ParsedListingTextResponse = {
  original_text: string
  normalized_text: string
  city: string | null
  intent: string
  property_type: string | null
  price_jod: number | null
  price_period: string | null
  price_per_sqm_jod: number | null
  price_per_dunum_jod: number | null
  negotiable: boolean
  area_sqm: number | null
  land_area_dunum: number | null
  bedrooms: number | null
  bathrooms: number | null
  floor_number: number | null
  building_age_years: number | null
  furnished: boolean | null
  has_phone_number: boolean
  contact_exposure: boolean
  audiences: string[]
  motivated_seller: boolean
  neighborhoods: Array<{ key: string; display_name: string }>
  landmarks: Array<{
    key: string
    display_name: string
    latitude: number
    longitude: number
  }>
  location_signals: string[]
  extracted_terms: string[]
  quality: ParsedListingQuality
}

export type BaselineValuationResponse = {
  estimated_price_jod: number | null
  confidence: string
  reason: string | null
  method: string
  unit_metric: string | null
  unit_area: number | null
  matched_unit_price_jod: number | null
  matched_count: number
  model_version: string
  quality: ParsedListingQuality
  parsed: ParsedListingTextResponse
}

export type BehaviorEventIn = {
  event_type: string
  listing_id?: string | null
  search_filters?: Record<string, unknown> | null
  metadata?: Record<string, unknown>
}

const DEFAULT_API_BASE = 'http://127.0.0.1:8000'
const DEMO_USER_STORAGE_KEY = 'aqarix-demo-user'
export const DEFAULT_DEMO_USER_ID = 'demo-buyer-irbid'

export function getApiBase(): string {
  return (import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE).replace(/\/$/, '')
}

export function getStoredDemoUserId(): string {
  if (typeof window === 'undefined') {
    return DEFAULT_DEMO_USER_ID
  }

  return window.localStorage.getItem(DEMO_USER_STORAGE_KEY) ?? DEFAULT_DEMO_USER_ID
}

export function setStoredDemoUserId(value: string): string {
  const next = value.trim() || DEFAULT_DEMO_USER_ID

  if (typeof window !== 'undefined') {
    window.localStorage.setItem(DEMO_USER_STORAGE_KEY, next)
  }

  return next
}

function baseHeaders(): HeadersInit {
  return {
    'x-demo-user': getStoredDemoUserId(),
  }
}

function jsonHeaders(): HeadersInit {
  return {
    ...baseHeaders(),
    'Content-Type': 'application/json',
  }
}

function buildQuery(params: Record<string, string | undefined | null>): string {
  const query = new URLSearchParams()

  for (const [key, value] of Object.entries(params)) {
    if (value) {
      query.set(key, value)
    }
  }

  const suffix = query.toString()
  return suffix ? `?${suffix}` : ''
}

async function requestJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${getApiBase()}${path}`, {
    ...init,
    headers: {
      ...(init.body === undefined ? baseHeaders() : jsonHeaders()),
      ...(init.headers ?? {}),
    },
  })

  const text = await response.text()
  if (!response.ok) {
    throw new Error(text || `Request failed with status ${response.status}`)
  }

  if (!text.trim()) {
    return undefined as T
  }

  return JSON.parse(text) as T
}

export function loadListings(filters: {
  city?: string
  neighborhood?: string
  propertyType?: PropertyType | ''
}): Promise<ListingSearchResponse> {
  return requestJson<ListingSearchResponse>(
    `/listings${buildQuery({
      city: filters.city || undefined,
      neighborhood: filters.neighborhood || undefined,
      property_type: filters.propertyType || undefined,
    })}`,
  )
}

export function loadProfile(): Promise<BuyerInvestorProfile | null> {
  return requestJson<BuyerInvestorProfile | null>('/profiles/buyer-investor')
}

export function saveProfile(payload: BuyerInvestorProfileIn): Promise<BuyerInvestorProfile> {
  return requestJson<BuyerInvestorProfile>('/profiles/buyer-investor', {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function loadRecommendations(): Promise<Recommendation[]> {
  return requestJson<Recommendation[]>('/recommendations')
}

export function recordBehaviorEvent(payload: BehaviorEventIn): Promise<void> {
  return requestJson<void>('/behavior-events', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function loadFeedbackSummary(listingId: string): Promise<ListingFeedbackSummary> {
  return requestJson<ListingFeedbackSummary>(`/listings/${listingId}/feedback-summary`)
}

export function submitFeedback(listingId: string, payload: ListingFeedbackIn): Promise<ListingFeedback> {
  return requestJson<ListingFeedback>(`/listings/${listingId}/feedback`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function startLeadRoom(payload: LeadRoomIn): Promise<LeadRoom> {
  return requestJson<LeadRoom>('/lead-rooms', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function parseListingText(text: string): Promise<ParsedListingTextResponse> {
  return requestJson<ParsedListingTextResponse>('/ai/parse-listing-text', {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
}

export function estimateBaselineValue(text: string): Promise<BaselineValuationResponse> {
  return requestJson<BaselineValuationResponse>('/ai/baseline-valuation', {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
}
