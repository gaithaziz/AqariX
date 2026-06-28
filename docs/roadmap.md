# Roadmap

## Phase 0 - Foundation

Timeline: Weeks 1-4
Status: In progress

Outcomes:

- Data schema: initial Alembic migration exists and has run on the Neon development database for users, roles, properties, listings, behavior events, listing feedback, recommendation snapshots, offering analyses, and lead rooms.
- PostGIS setup: migration enables PostGIS on the Neon development database.
- Behavior event model: API schema and route exist.
- Listing feedback and ad-improvement loop: API schema, feedback route, and aggregated summary route exist.
- Listing ingestion plan: seed/demo listing data exists; real ingestion is still pending.
- Initial zones: Amman-first demo data exists; real zone dataset is still pending.
- Auth roles: Clerk JWT boundary, local demo-user fallback, and local Clerk development env values exist.
- Baseline rate limits, quotas, debounce patterns, and cost/spend alerts: Redis-backed API counters and debounced web listing search exist; provider spend alerts expand when paid integrations are connected.
- Design system: web shell has Arabic/RTL, light/dark, and role-oriented MVP surfaces.
- Docker verification: `docker compose build` passes and the API returns `/health` through Docker.
- Staging API deployment: Railway service is live at `https://aqarix-production.up.railway.app`; `/health` responds successfully. Railway still needs `APP_ENV=staging` applied because the current health payload reports `env` as `local`.
- Staging web deployment: Vercel production deployment is ready at `https://aqari-x.vercel.app` with Railway API and Clerk public env values configured; browser smoke test passed.
- Documentation baseline: core docs, guardrails, deployment notes, and roadmap phase status exist.

Left:

- Expand web-to-API wiring beyond listing search when the next non-AI workflow is ready.

## Phase 1 - AI/Data Core

Timeline: Weeks 5-12
Status: Not started

Outcomes:

- AVM baseline.
- Comparable logic.
- Recommendation baseline using intake and behavior events.
- Forecast prototype.
- Offering-analysis API.
- Evidence and confidence object.
- Redis-cached AI output snapshots and token/cost tracking.

Left:

- All Phase 1 outcomes are pending.
- AI-owned features stay deferred until the AI teammate begins this phase.

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

- Amman/Irbid launch.
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
