# Railway Setup

Use Railway for the staging FastAPI API only.

Deploy settings:

- Repository: `gaithaziz/AqariX`.
- Branch: `Ghaith`.
- Config file: `railway.json` at the repo root.
- Dockerfile: `Dockerfile.railway` at the repo root.
- Health check: `/health`.

Required variables:

```bash
APP_ENV=staging
DATABASE_URL=
CLERK_JWKS_URL=
CLERK_ISSUER=
CLERK_SECRET_KEY=
REDIS_URL=
RATE_LIMIT_PUBLIC_PER_MINUTE=60
RATE_LIMIT_USER_PER_MINUTE=120
QUOTA_WRITES_PER_DAY=1000
QUOTA_LEAD_ROOMS_PER_DAY=25
COST_ALERT_REQUESTS_PER_DAY=1000
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET=
SENTRY_DSN=
```

For the free/minimal staging path, leave `REDIS_URL`, R2, and Sentry empty. The API fails open without Redis, and media/Sentry are not required for Phase 0 staging.
