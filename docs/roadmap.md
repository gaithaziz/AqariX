# Roadmap

## Phase 0 - Foundation

Timeline: Weeks 1-4
Status: Complete

Outcomes:

- Data schema: initial Alembic migration exists and has run on the Neon development database for users, roles, properties, listings, behavior events, listing feedback, recommendation snapshots, offering analyses, and lead rooms.
- PostGIS setup: migration enables PostGIS on the Neon development database.
- Behavior event model: API schema and route exist.
- Listing feedback and ad-improvement loop: API schema, feedback route, and aggregated summary route exist.
- Listing ingestion plan: seed/demo listing data and protected manual ingestion endpoint exist; production source integrations are still pending.
- Initial zones: Irbid-centered demo zone catalog exists; real GIS-backed zone dataset is still pending.
- Auth roles: Clerk JWT boundary, local demo-user fallback, and local Clerk development env values exist.
- Baseline rate limits, quotas, debounce patterns, and cost/spend alerts: Redis-backed API counters and debounced web listing search exist; provider spend alerts expand when paid integrations are connected.
- Design system: web shell has Arabic/RTL, light/dark, and role-oriented MVP surfaces.
- Docker verification: `docker compose build` passes and the API returns `/health` through Docker.
- Staging API deployment: Railway service is live at `https://aqarix-production.up.railway.app`; `/health` responds successfully with the staging environment, and `/api` exposes the API index.
- Staging web deployment: Vercel production deployment exists at `https://aqari-x.vercel.app`, but `.vercel.app` edge access is unreliable; Railway now serves the built React web app from `/` as the working staging fallback.
- Web-to-API wiring: listing search, listing-view behavior events, listing feedback submission/summary, and lead-room creation call the FastAPI staging API.
- Documentation baseline: core docs, guardrails, deployment notes, and roadmap phase status exist.

Left:

- Phase 0 is complete. Production listing source integrations and real GIS-backed zone datasets move into later data work.

## Phase 1 - Data and Decision Core

Timeline: Weeks 5-12
Status: In progress - provider-agnostic API shell expanded

Outcomes:

- Valuation engine baseline.
- Comparable logic: rules-based demo comparable endpoint exists; advanced ranking remains pending.
- Recommendation baseline using intake and behavior events: rules-based placeholder endpoint exists; advanced ranking remains pending.
- Forecast engine prototype.
- Offering-analysis API: rules-based shell endpoint exists with Redis/idempotency reuse and PostgreSQL snapshot persistence when staging/prod database access is configured; production analysis engine remains pending.
- Evidence and confidence object: API contract exists with evidence sources, comparable evidence, confidence label, caveats, and engine/source version.
- Recommendation snapshot persistence: rules-based recommendation snapshots append to PostgreSQL when staging/prod database access is configured.
- Saved offerings/searches: API routes exist and emit behavior events for recommendation inputs.
- Redis-cached output snapshots and cost tracking: offering-analysis shell is Redis-cacheable and rate/cost counted; provider-specific usage tracking remains pending.
- Listing ingestion and zones: protected manual listing ingestion and public Irbid demo zones exist; production source integrations and GIS datasets remain pending.
- Duplicate-write protection: idempotency keys are supported for offering analysis and lead-room creation.

Left:

- Keep all contracts analysis-engine agnostic until the advanced-engine owner starts implementation.
- Replace rules-based comparable/analysis placeholders with approved valuation, forecast, and ranking engines later.
- Replace manual/demo ingestion and zone data with approved production sources and GIS-backed market zones.

## Phase 2 - Role-Complete MVP

Timeline: Weeks 9-20
Status: Not started

Outcomes:

- Buyer/investor app.
- Seller/dealer portal.
- Managed lead room.
- Admin dashboard.
- Agency order flow.
- Role-specific dashboards.

Left:

- All Phase 2 outcomes are pending.
- Current web surfaces are shells only, not role-complete product workflows.

## Phase 3 - Closed Beta

Timeline: Weeks 21-28
Status: Not started

Outcomes:

- 200-500 beta users.
- Seller/dealer trial.
- Supervised lead-room testing.
- Agency pilot.
- Model calibration.
- User feedback loop.

Left:

- All Phase 3 outcomes are pending.
- Requires Phase 0 foundation and Phase 2 role-complete workflows first.

## Phase 4 - Public Launch

Timeline: Weeks 29-36
Status: Not started

Outcomes:

- Irbid-centered launch, with Amman expansion after validation.
- Paid campaigns.
- Dealer CRM subscriptions.
- Smart Boosts.
- Premium reports.
- B2B outreach.

Left:

- All Phase 4 outcomes are pending.
- Requires closed beta validation, operations readiness, monitoring, backups, and rollback.

## Post-MVP Expansion

Status: Deferred

- Verified Listing Badge.
- Mortgage and affordability calculator.
- AqariX Score.
- Price-drop and opportunity alerts.
- Rental yield calculator.
- Off-plan project tracker.
- Diaspora mode.
- API access for institutions.

## Roadmap Guardrail

Launch all major roles early, but keep depth focused on the highest-value loops:

- Matched offerings.
- Offering analysis.
- Seller pricing.
- Managed lead rooms.
- Dealer CRM.
- Agency add-ons.
