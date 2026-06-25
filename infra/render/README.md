# Render Setup

Planned services:

- `aqarix-api`: FastAPI web service.
- `aqarix-jobs`: background worker or cron service when needed.
- Managed Redis-compatible cache: shared cache, rate-limit, quota, and idempotency store for API/jobs.

Required environment variables are listed in `services/api/.env.example`.
