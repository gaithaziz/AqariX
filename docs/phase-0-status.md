# Phase 0 Status

Status: In progress

Branch: `Ghaith`

## Completed

- Extracted and reviewed the Google Stitch UI package.
- Added Stitch source and screen references under `docs/design/stitch/`.
- Scaffolded `apps/web` with React + Vite.
- Implemented the first AqariX web shell:
  - Arabic-first default UI.
  - RTL/LTR language toggle.
  - Dark/light mode toggle.
  - Listing search/card UI.
  - Behavior-aware recommendation context.
  - Listing feedback prompt.
  - Static offering-analysis shell.
  - Managed lead-room shell.
  - Seller ad-improvement shell.
  - Dealer CRM pipeline shell.
- Added optional Clerk provider wiring in the web app.
- Added Docker Compose for local service separation.
- Scaffolded `services/api` with FastAPI.
- Added `/health`, `/listings`, buyer/investor profile, behavior event, deterministic recommendation placeholder, listing feedback, feedback summary, and lead-room routes.
- Added Clerk JWT verification boundary in the API when Clerk JWKS settings are configured.
- Added Alembic migration scaffold with PostGIS and pgvector extensions.
- Added local jobs worker placeholder.
- Added infra notes for Docker, Neon, Render, and Vercel.
- Added API smoke tests.
- Added root scripts for common web and API checks.
- Added Redis-backed baseline rate limits, write quotas, and request-volume cost alerts for existing API routes.
- Added debounced web listing search connected to the `/listings` API with static fallback when the API is unavailable.
- Chose MapLibre/OpenStreetMap as the default MVP map provider path.
- Added root `render.yaml` and `vercel.json` staging deployment configuration.

## Intentionally Not Implemented

- Real AI valuation.
- Real forecasting.
- Model-backed recommendations.
- AI-generated listing analysis.
- AI-generated seller marketing copy.

Those are owned by the AI teammate.

## Verification

Passed:

```bash
pnpm web:build
pnpm web:lint
pnpm api:test
pnpm api:lint
docker compose config
```

Latest local check:

```bash
pnpm web:build
pnpm web:lint
pnpm api:test
pnpm api:lint
docker compose config
```

Blocked locally:

```bash
docker compose build
```

Reason: Docker daemon is not running at the configured local socket.

## Next Phase 0 Tasks

- Start Docker daemon and verify `docker compose build`.
- Run the API through Docker.
- Create real Clerk development project and fill env values.
- Create Neon development database and run migrations.
- Deploy staging API to Render from `render.yaml`.
- Deploy staging web to Vercel from `vercel.json`.
- Add `.env.example` files for any new service folders.
- Expand web-to-API wiring beyond listing search when the next non-AI workflow is ready.
