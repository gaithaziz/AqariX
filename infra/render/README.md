# Render Setup

Planned services:

- `aqarix-api`: FastAPI web service.
- `aqarix-jobs`: background worker or cron service when needed.
- Managed Redis-compatible cache: shared cache, rate-limit, quota, and idempotency store for API/jobs.

Required environment variables are listed in `services/api/.env.example`.

The root `render.yaml` defines the staging API, worker, and Redis-compatible Key Value service. Neon remains external, so set `DATABASE_URL` manually in Render.
