# API Spec

Initial API style: REST over HTTPS with JSON, implemented with FastAPI. FastAPI should expose OpenAPI documentation for internal development.

## API Principles

- Every endpoint must enforce authentication unless explicitly public.
- Every object endpoint must enforce ownership, organization membership, or admin permission.
- Every public, expensive, or repeated endpoint must have server-side rate limits and abuse controls.
- Duplicate-prone writes must support idempotency or server-side duplicate protection.
- AI output endpoints must return confidence and caveats.
- Recommendation endpoints must return reason codes or "why recommended" explanations.
- Lead-room endpoints must preserve structured workflow state.
- Public listing search must avoid exposing sensitive seller/dealer details.

## Auth

### POST `/auth/session`

Create or refresh a session.

### GET `/me`

Return current user, roles, organization memberships, and onboarding status.

## Intake and Profiles

### GET `/profiles/buyer-investor`

Return current buyer/investor intake profile.

### PUT `/profiles/buyer-investor`

Create or update intake data:

- Budget
- Cities/neighborhoods
- Property type
- Purpose
- Risk tolerance
- Investment horizon
- Financing status
- Rental use
- Lifestyle needs

## Search and Listings

### GET `/listings`

Search active listings.

Filters:

- City
- Neighborhood
- Price range
- Area range
- Property type
- Bedrooms
- Investment purpose
- Expected yield
- Listing freshness
- Verified status
- Map bounding box

### POST `/listings/ingest`

Protected manual ingestion endpoint for pre-AI and demo listing batches.

Returns:

- Source name
- Imported count
- Listing IDs

Rules:

- Must be authenticated.
- Must be rate-limited and daily quota-limited.
- Must reject invalid listing shape and protect against duplicate imports.
- Production source integrations should replace manual/demo imports later.

### GET `/zones`

Return public launch-zone catalog entries.

Filters:

- City

Returns:

- Zone ID
- City
- Name
- Launch priority
- Dataset status

### GET `/recommendations`

Return personalized listing recommendations for the current buyer/investor.

Inputs:

- Current intake profile
- Saved searches
- Recent behavior events
- Hard constraints such as budget, city, property type, and risk tolerance

Returns:

- Ranked listings
- Recommendation score
- Reason codes
- "Why recommended" explanation
- Personalization confidence
- Sponsored compatibility flag where applicable

### POST `/behavior-events`

Record in-app behavior used for analytics and recommendation quality.

Allowed events:

- Search performed
- Filter applied
- Map area viewed
- Listing viewed
- Listing saved or unsaved
- Listing compared
- Analysis opened
- Nearby opportunity clicked
- Lead room started
- Listing dismissed
- Recommendation clicked

Rules:

- Events must be scoped to the current user or anonymous session.
- Server must validate event type and entity access.
- Sensitive message content must not be sent as behavior metadata.
- Client should batch or debounce high-frequency events.
- Server must rate-limit event ingestion by user/session/IP and drop or sample noisy duplicates.

### POST `/listings/{listing_id}/feedback`

Submit lightweight feedback after reviewing a listing.

Fields:

- Clarity rating
- Photo quality rating
- Price trust rating
- Location confidence rating
- Interest level
- Missing information tags
- Optional free-text note

Rules:

- Feedback is private by default.
- Seller/dealer and investor-facing outputs must use aggregated summaries.
- Free text must be moderated or filtered before it influences public notes.

### GET `/listings/{listing_id}/feedback-summary`

Return aggregated listing feedback summary when enough signals exist.

Returns:

- Feedback count
- Top missing information
- Seller/dealer ad-improvement notes when caller owns the listing
- Investor-facing note when caller is a buyer/investor
- Listing quality caveats

Rules:

- Feedback submission and summary reads must be rate-limited.
- Free-text feedback must have length caps and abuse/spam checks.

### POST `/listings`

Create a seller/dealer listing.

### GET `/listings/{listing_id}`

Return listing detail with public-safe property information.

### PATCH `/listings/{listing_id}`

Update a listing. Requires seller/dealer ownership or admin permission.

### POST `/listings/{listing_id}/media`

Upload or attach listing media.

## Offering Analysis

### POST `/listings/{listing_id}/analysis`

Generate or retrieve offering analysis for a listing.

Returns:

- Fair value
- Confidence
- Listed-price gap
- Bargain range
- Forecast scenarios
- Location momentum
- Liquidity estimate
- Comparable evidence
- Recommendation label
- Caveats

Rules:

- Analysis generation must be rate-limited and quota-aware by user, organization, listing, and endpoint where practical.
- Duplicate client retries should send `Idempotency-Key`.
- Reuse existing analysis snapshots when inputs and model version have not materially changed.
- Persist reusable analysis snapshots to PostgreSQL in staging/production when database access is configured.
- Cap prompt, context, and output size.

For the pre-AI implementation, this endpoint may return a deterministic shell with comparable evidence, caveats, a fixed `model_version`, and no AVM/forecast model output.

### GET `/listings/{listing_id}/comparables`

Return deterministic comparable listing candidates for a listing.

Returns:

- Comparable listing
- Similarity score
- Price per sqm
- Reason codes
- Source type

Rules:

- Comparables must be explainable and filterable before any model ranking is introduced.
- Demo comparables are not valuation advice.

### GET `/listings/{listing_id}/nearby-opportunities`

Return nearby alternatives when the listing is weak, overpriced, or mismatched.

## Saved Items

### GET `/saved-offerings`

Return saved listings.

### POST `/saved-offerings`

Save a listing.

Rules:

- Must emit a `listing_saved` behavior event.
- Repeated saves for the same user/listing should return the existing saved item.

### DELETE `/saved-offerings/{saved_id}`

Remove a saved listing.

Rules:

- Must emit a `listing_unsaved` behavior event.

### GET `/saved-searches`

Return saved searches.

### POST `/saved-searches`

Create a saved search and optional alerts.

Rules:

- Must emit a `saved_search_created` behavior event.

## Seller and Dealer

### POST `/seller-trials`

Start a seller/dealer free trial.

### GET `/seller-trials/current`

Return trial limits, usage, upgrade prompts, and eligibility.

### POST `/seller/pricing-assistant`

Generate suggested listing price, bargain range, comparable evidence, and pricing strategy.

### POST `/seller/marketing-assistant`

Generate listing copy, photo checklist, captions, video script ideas, and campaign suggestions.

### GET `/dealer/crm`

Return pipeline entries, lead rooms, tasks, appointments, and performance summary.

### PATCH `/dealer/crm/{entry_id}`

Update pipeline stage, next action, notes, or task status.

## Managed Lead Rooms

### POST `/lead-rooms`

Start a managed lead room for a listing.

Required:

- `listing_id`
- buyer/investor intent
- budget fit
- preferred contact method

Rules:

- Duplicate client retries should send `Idempotency-Key`.

### GET `/lead-rooms`

Return lead rooms for current user role.

### GET `/lead-rooms/{room_id}`

Return room detail, messages, tasks, appointments, offers, and allowed actions.

### POST `/lead-rooms/{room_id}/messages`

Send a message.

Rules:

- Message submission must be rate-limited and checked for room participation.
- Duplicate sends should be guarded with an idempotency key or message client token.

### POST `/lead-rooms/{room_id}/qualify`

Update qualification status.

### POST `/lead-rooms/{room_id}/appointments`

Schedule a viewing.

### POST `/lead-rooms/{room_id}/offers`

Record an offer.

### PATCH `/lead-rooms/{room_id}/stage`

Move room through allowed workflow stages.

### POST `/lead-rooms/{room_id}/close`

Capture final outcome, final price if applicable, satisfaction, and reason.

## Agency

### GET `/agency/packages`

Return active agency packages.

### POST `/agency/orders`

Create an agency order.

### GET `/agency/orders`

Return orders visible to seller/dealer or agency operator.

### PATCH `/agency/orders/{order_id}`

Update status, assignment, requirements, or delivery date.

### POST `/agency/orders/{order_id}/assets`

Attach asset, copy, or delivery item.

### PATCH `/agency/assets/{asset_id}/approval`

Approve or request revision.

## Admin

### GET `/admin/lead-rooms`

List supervised rooms with risk flags.

### GET `/admin/flags`

List trust and safety flags.

### PATCH `/admin/flags/{flag_id}`

Resolve, escalate, or annotate flag.

### GET `/admin/kpis`

Return marketplace KPIs, lead-room conversion, listing quality, agency queue, and model quality summaries.

### POST `/admin/listings/{listing_id}/review`

Approve, reject, or request listing correction.

## API Guardrails

- Never expose private contact details by default.
- Return allowed actions per resource to simplify role-based UI.
- Add idempotency keys for lead-room creation, offer creation, payments, and agency orders.
- Rate-limit public search, auth, AI analysis, assistants, uploads, behavior events, feedback, lead-room messages/actions, webhooks, and high-volume reporting endpoints.
- Debounce/throttle client calls for search, autocomplete, map bounds changes, autosave, behavior events, and assistant draft generation.
- Paginate and cap list, search, admin, analytics, and report responses.
- Cache expensive search, geospatial, comparable, recommendation, analysis, feedback-summary, and AI assistant responses in backend Redis when freshness allows.
- Track cost-heavy endpoint usage by user, organization, role, endpoint, and feature.
- Log request IDs for support and incident response.
