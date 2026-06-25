# Implementation Plan

Status: Planned

## Decisions Already Made

- Auth provider: Clerk.
- Hosting should avoid Supabase.
- MVP database: Neon Postgres with PostGIS and pgvector.
- Backend: FastAPI on Render.
- Web dashboards: React + Vite on Vercel.
- Mobile: Flutter.
- Object storage: Cloudflare R2.
- Initial build strategy: one vertical slice before broad platform expansion.

## First Vertical Slice

Build this first:

1. Clerk authentication and role selection.
2. Buyer/investor intake.
3. Seeded listings in Neon Postgres/PostGIS.
4. Listing search with filters.
5. Basic map-ready geospatial query.
6. Offering detail page.
7. Placeholder offering analysis object with confidence/caveats.
8. Start managed lead room.
9. Admin-visible lead-room record.

This proves the AqariX core loop:

```text
user intent -> matched property -> evidence-backed analysis -> supervised lead room
```

## Repo Structure

Use this monorepo layout:

```text
apps/
  mobile/        # Flutter app
  web/           # React + Vite dashboards
services/
  api/           # FastAPI backend
  jobs/          # Python jobs and scheduled tasks
packages/
  shared/        # Shared schemas/types/docs helpers if needed
infra/
  render/        # Render service notes/config
  neon/          # Database setup and migrations notes
  vercel/        # Web deployment notes
docs/
```

## Phase 0 Tasks

1. Create monorepo folders.
2. Scaffold FastAPI service.
3. Add health endpoint and OpenAPI docs.
4. Add Neon connection settings.
5. Add initial migrations for users, roles, properties, listings, offering analyses, and lead rooms.
6. Enable PostGIS and pgvector.
7. Configure Clerk JWT verification in FastAPI.
8. Scaffold React + Vite dashboard.
9. Add Clerk web auth.
10. Add seed listings and neighborhoods.
11. Add search/listing API.
12. Add buyer/investor intake API.
13. Add lead-room creation API.
14. Add smoke tests.
15. Deploy staging API to Render.
16. Deploy staging web to Vercel.

## Phase 1 Tasks

1. Build buyer/investor intake UI.
2. Build listing search and detail UI.
3. Build basic lead-room UI.
4. Build admin lead-room list.
5. Add authorization tests for every user-owned object.
6. Add mobile Flutter shell after API and UX contracts stabilize.

## Keep Deferred

- Seller/dealer CRM depth.
- AqariX Agency order flow.
- Real AVM training.
- Airflow.
- Pinecone or Milvus.
- Kubernetes.
- Complex microservices.
- Payment/subscription implementation.
- Public SEO site.

## Definition of Ready for Implementation

- Clerk project created for development.
- Neon database created for development.
- Render service target chosen.
- Vercel project target chosen.
- Cloudflare R2 bucket created or deferred with local placeholder storage.
- Environment variables documented.
- First vertical slice accepted as the starting scope.
