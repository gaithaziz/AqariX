# Tech Stack Decision

Status: Approved for MVP

## Decision

AqariX will use the following MVP stack:

| Layer | Approved Choice | Notes |
| --- | --- | --- |
| Mobile app | Flutter | One high-performance iOS/Android codebase with Arabic/RTL support. |
| Seller/dealer/admin web | React + Vite | Private dashboards should stay fast and simple. Use Next.js only for public SEO pages if needed. |
| Backend API | FastAPI | Python-native backend for APIs, AI/ML integration, async workflows, and OpenAPI docs. |
| Database | PostgreSQL + PostGIS | Main system of record with strong relational and geospatial support. |
| Vector search | PostgreSQL/pgvector first | Add Pinecone or Milvus only if scale, latency, or matching quality proves the need. |
| ML/AI | XGBoost, LightGBM, Prophet, PyTorch as needed | Use the simplest model that meets accuracy and explainability requirements. |
| Data jobs | Python jobs first | Add Airflow only when orchestration complexity requires it. |
| Auth | Clerk | Approved auth provider for MVP. Do not use Supabase Auth. |
| Monitoring | Sentry + product analytics | Track errors, latency, key events, lead-room funnel, model quality, and cost. |
| Local service separation | Docker Compose | Run local API, jobs, and database consistently without adding Kubernetes or microservice complexity. |

## Approved MVP Hosting Plan

| Need | Default Choice | Why |
| --- | --- | --- |
| Auth | Clerk | Simple managed auth, generous free starting point, organization support path. |
| Database | Neon Postgres | Managed Postgres with PostGIS and pgvector support; keeps database separate from Supabase. |
| Backend API and jobs | Render | Simple Git-based deploys for FastAPI services and workers without heavy DevOps. |
| Web dashboard | Vercel | Simple React/Vite static hosting and preview deployments. |
| Object/media storage | Cloudflare R2 | Cost-effective object storage for listing photos and agency assets. |
| Mobile builds | Local first, then Codemagic or GitHub Actions | Avoid mobile CI cost until app builds need automation. |

Supabase is intentionally not part of the MVP hosting/auth plan.

## Why This Stack

The stack is selected for speed, reliability, scalability, and maintainability, not popularity.

It fits AqariX because:

- The core product needs geospatial search, nearby alternatives, comparable properties, and zone analytics.
- The AI/data layer benefits from Python-native tooling.
- The MVP needs fast mobile delivery without two native teams.
- Seller, dealer, admin, and agency dashboards are private tools, so they do not need server rendering by default.
- PostgreSQL can carry relational data, geospatial data, transactional workflows, and initial vector search before adding specialized infrastructure.
- Managed services reduce operational risk while the product is still validating demand.

## Decision Rules

- Do not add a service because it is fashionable.
- Do not add a second database until PostgreSQL is proven insufficient.
- Do not add Pinecone, Milvus, Kafka, Airflow, Kubernetes, or microservices during MVP unless a proof-of-fit shows a real need.
- Prefer boring, debuggable infrastructure.
- Keep AI/model serving close to FastAPI until load or reliability requirements justify separation.
- Keep public marketing pages separate from private dashboards if their needs diverge.
- Keep hosting away from Supabase unless this decision is explicitly reopened.
- Use Docker Compose for local service separation, not Kubernetes.

## Required Proof-of-Fit Before Deep Build

Build small spikes for:

- Map search over 10k-100k listings.
- PostGIS nearby alternatives and comparable-property queries.
- pgvector matching for buyer/investor profiles and listings.
- Offering analysis API latency.
- Lead-room concurrent messaging and stage updates.
- Dealer CRM dashboard with realistic data volume.
- Arabic/RTL mobile and web forms, tables, maps, and dashboards.
- Backup and restore for database plus media assets.
- Staging-to-production deployment with rollback and monitoring.

## Upgrade Triggers

### Move beyond pgvector when:

- Query latency is consistently too high after indexing and query tuning.
- Vector matching volume becomes a bottleneck.
- The recommendation system needs specialized approximate nearest-neighbor behavior PostgreSQL cannot provide reliably.

### Add Airflow when:

- Data ingestion jobs become interdependent.
- Retraining and validation jobs need scheduling, retry, and dependency visibility.
- Manual Python job orchestration becomes fragile.

### Split AI services when:

- Model inference creates unacceptable API latency.
- Model workloads need independent scaling.
- Reliability requires isolating AI failures from core marketplace APIs.

### Use Next.js when:

- AqariX needs public SEO-heavy pages.
- Server-rendered public content becomes a growth requirement.
- The marketing/content site needs a different deployment lifecycle from private dashboards.

## Agent Guardrail

Agents must not change the approved stack without updating this file, [architecture.md](./architecture.md), [deployment.md](./deployment.md), and any affected implementation docs.
