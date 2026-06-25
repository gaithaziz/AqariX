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

| Layer | Recommended Technology | Rationale |
| --- | --- | --- |
| Mobile app | Flutter | Single codebase for iOS and Android with native-feeling performance. |
| Backend | FastAPI | Python-native ML serving, async APIs, and clean OpenAPI documentation. |
| Database | PostgreSQL + PostGIS | Structured property data, geospatial queries, zones, and proximity features. |
| Vector search | Pinecone or Milvus | Matching between user profiles and property/offering embeddings. |
| ML stack | XGBoost, LightGBM, Prophet, PyTorch | AVM, forecasting, embeddings, assistant support. |
| Data pipelines | Scrapy, Airflow, validation jobs | Listing ingestion, cleaning, deduplication, scheduled retraining. |
| Analytics | Mixpanel + Sentry | Funnel metrics, behavior tracking, lead-room events, and error monitoring. |
| Auth | Firebase Auth or JWT-based auth | Role-aware access control, social login, admin/dealer separation. |

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
