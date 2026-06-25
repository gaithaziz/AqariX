# Architecture

## System Overview

AqariX has six major product layers:

1. Mobile app for buyers and investors.
2. Seller/dealer web portal or role-specific app surfaces.
3. Admin supervision dashboard.
4. Agency operations dashboard.
5. Backend API and workflow engine.
6. AI/data layer for valuation, forecasting, recommendations, and CRM intelligence.

## Recommended Stack

The stack is not chosen because a tool is popular. AqariX should use boring, well-supported technology where reliability matters, and specialized tools only where the product genuinely needs them.

Selection criteria:

- Fast enough for search, maps, CRM dashboards, and AI analysis workflows.
- Reliable under real production traffic and operational incidents.
- Scalable without forcing a rewrite after the first launch zones.
- Strong geospatial support for property search, neighborhoods, zones, and proximity.
- Strong Python/ML fit for valuation, forecasting, recommendations, and data pipelines.
- Easy to hire for, debug, monitor, and maintain.
- Good ecosystem for auth, testing, observability, and deployment.
- Minimal custom infrastructure during MVP.

| Layer | Recommended Technology | Rationale |
| --- | --- | --- |
| Mobile app | Flutter | Single codebase for iOS and Android with native-feeling performance. |
| Seller/dealer/admin web | React + Vite first; Next.js only if public SEO/server rendering is needed | Fast private dashboards without unnecessary server-rendering complexity. |
| Backend | FastAPI | Python-native ML serving, async APIs, and clean OpenAPI documentation. |
| Database | PostgreSQL + PostGIS | Structured property data, geospatial queries, zones, and proximity features. |
| Vector search | PostgreSQL/pgvector first; Pinecone or Milvus only when scale/latency requires it | Avoid a separate vector system until matching volume proves the need. |
| ML stack | XGBoost, LightGBM, Prophet, PyTorch | AVM, forecasting, embeddings, assistant support. |
| Data pipelines | Python jobs first; Airflow only when orchestration complexity requires it | Keep MVP operations simple while preserving an upgrade path. |
| Analytics | Mixpanel + Sentry | Funnel metrics, behavior tracking, lead-room events, and error monitoring. |
| Auth | Clerk | Approved MVP auth provider. Auth must be reliable, secure, and role-aware from day one. |

## Stack Decision Rules

- Do not introduce a service until the app has a real need for it.
- Prefer PostgreSQL features before adding another database.
- Prefer managed infrastructure during MVP unless cost, compliance, or control requires self-hosting.
- Use Clerk for auth and keep hosting away from Supabase for MVP.
- Keep AI/model serving close to the Python backend until load requires isolation.
- Keep public marketing pages separate from private dashboards if their needs diverge.
- Run a short proof-of-fit before locking any major technology choice.

## Proof-of-Fit Checks

Before finalizing the stack, build small spikes for:

- Map search: filter 10k-100k listings by city, neighborhood, price, type, and bounding box.
- Geospatial proximity: nearby alternatives and comparable properties.
- Offering analysis API: valuation, comparable evidence, and explanation under acceptable latency.
- Lead room: concurrent messages, stage transitions, tasks, appointments, and offer history.
- Dealer CRM dashboard: pipeline, filters, tasks, and listing performance with realistic data.
- Arabic/RTL UI: mobile and web forms, tables, maps, and dashboards.
- Backup/restore: database plus media assets.
- Deployment: staging to production with rollback and monitoring.

If a candidate stack fails these checks, replace it before building deeper features.

## Core Domains

### Identity and Roles

Handles users, organizations, role assignments, sessions, and permissions.

Roles:

- Buyer
- Investor
- Seller
- Dealer/Broker
- AqariX Admin
- Agency Operator

### Marketplace

Handles listings, properties, media, comparable properties, search, filters, map results, saved offerings, and listing quality.

### Intelligence

Handles AVM estimates, forecasts, recommendation scoring, location momentum, liquidity estimates, and explanation objects.

### Managed Lead Room

Handles supervised communication, qualification, tasks, appointments, offers, negotiation, closing support, outcomes, and admin flags.

### CRM

Handles dealer pipeline stages, reminders, notes, next actions, lead summaries, listing performance, and conversion analytics.

### Agency

Handles content package orders, production tasks, asset approvals, campaign reporting, and listing/dealer performance feedback.

### Admin and Trust

Handles listing review, user review, dispute review, abuse flags, suspicious pricing, off-platform leakage, and marketplace KPIs.

## High-Level Data Flow

1. Seller/dealer creates a listing.
2. Listing is validated, enriched with geospatial data, and optionally reviewed.
3. AI modules generate valuation, confidence, comparable evidence, and listing quality signals.
4. Buyer/investor intake creates a user preference vector.
5. Recommendation engine ranks compatible offerings.
6. User opens an offering analysis.
7. User starts a managed lead room.
8. Lead room captures communication, tasks, appointments, offers, and outcome.
9. Outcome data feeds CRM analytics and model calibration.

## Key Product Objects

### Offering Analysis Object

- Fair value
- Listed-price gap
- Bargain range
- Forecast horizon
- Confidence level
- Comparable properties
- Location momentum
- Liquidity estimate
- Recommendation label
- Model version
- Evidence sources

### Lead Room Object

- Property/listing
- Buyer/investor
- Seller/dealer
- Stage
- Messages
- Tasks
- Appointments
- Offer history
- Admin flags
- Outcome

### Seller Trial Object

- Trial start/end
- Listing limit
- Assistant usage limit
- Upgrade status
- Agency add-on eligibility
- Conversion trigger

## Architecture Guardrails

- Keep marketplace, AI, CRM, lead-room, agency, and admin domains separate enough to evolve independently.
- Store AI outputs with model version, confidence, and evidence links.
- Use server-side authorization for every object access.
- Keep lead room events structured; they are core marketplace learning data.
- Prefer explicit workflow states over vague status strings.
- Treat off-platform contact exposure as a controlled business rule, not a default listing feature.
