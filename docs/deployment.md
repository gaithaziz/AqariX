# Deployment

## Environments

Required environments:

- Local development
- Staging
- Production

Each environment must have separate:

- Neon database
- Object storage
- API keys
- Clerk project
- Analytics project
- Error monitoring project
- AI/model configuration

Supabase must not be used for MVP auth or hosting.

## Release Flow

1. Develop on a branch.
2. Run formatting, linting, type checks, and tests.
3. Review schema and migration changes.
4. Deploy to staging.
5. Run staging smoke tests.
6. Confirm backup status.
7. Promote to production.
8. Run production smoke tests.
9. Monitor errors, latency, and key events.

## Infrastructure Components

- Render-hosted FastAPI backend service.
- Neon PostgreSQL database with PostGIS and pgvector enabled.
- Cloudflare R2 object storage for listing media and agency assets.
- PostgreSQL/pgvector for MVP vector matching unless scale proves otherwise.
- Render background worker for jobs.
- Render cron jobs or simple scheduled Python jobs for ingestion, alerts, retraining, and maintenance tasks.
- Flutter mobile app build pipeline.
- Vercel-hosted React + Vite web dashboard for seller/dealer, admin, and agency surfaces.
- Clerk for authentication and organization-aware role access.
- Docker Compose for local service separation across API, jobs, and database.

Do not add a separate vector search service, Airflow, Kubernetes, or microservice split during MVP unless the proof-of-fit checks in [tech-stack.md](./tech-stack.md) show a real need.

## Local Docker Policy

Use Docker Compose locally so developers can run separated services without hand-configuring every dependency.

Expected services:

- `api`: FastAPI backend.
- `jobs`: Python jobs/worker.
- `db`: local PostgreSQL with PostGIS and pgvector for development fallback.

Production should stay on the approved managed providers unless requirements change: Render, Neon, Vercel, Clerk, and Cloudflare R2.

## Monitoring

Track:

- API error rate.
- API latency.
- Database query performance.
- Lead-room creation and message failures.
- AI analysis failures.
- Upload failures.
- Payment/subscription failures when added.
- Background job failures.
- Model output volume and cost.

Recommended tools from proposal:

- Sentry for error monitoring.
- Mixpanel for funnel and behavioral analytics.

## Backups and Recovery

- Automate database backups.
- Store backups away from the production account.
- Test restore into a separate environment.
- Back up object storage metadata and critical assets.
- Keep migration rollback notes.
- Add disaster recovery runbook before public launch.

## Production Release Gates

Do not release if:

- Staging and production share the same database.
- Backup restore has never been tested.
- Auth or role checks are incomplete.
- AI outputs lack caveats and confidence.
- Critical flows lack smoke tests.
- Error monitoring is not configured.
- Environment variables are undocumented.

## Cost Controls

- Set alerts for Render, Neon, Cloudflare R2, Clerk, email/SMS, maps, vector search, and AI API spend.
- Cache repeated expensive AI outputs.
- Rate-limit AI analysis and assistant usage.
- Track usage by user role, organization, and endpoint.

## MVP Provider Defaults

- Auth: Clerk.
- Database: Neon Postgres.
- Backend/API/jobs: Render.
- Web dashboard: Vercel.
- Object storage: Cloudflare R2.
- Mobile app distribution: local builds first; add Codemagic or GitHub Actions when repeated mobile builds become painful.

## Deployment Guardrail

One-click deploys are acceptable for demos, not for production. Production must have staging, rollback, backups, monitoring, and release checks.
