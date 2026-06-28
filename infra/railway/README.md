# Railway Setup

Use Railway for the staging FastAPI API only.

Deploy settings:

- Repository: `gaithaziz/AqariX`.
- Branch: `Ghaith`.
- Config file: `railway.json` at the repo root.
- Dockerfile: `Dockerfile.railway` at the repo root.
- Health check: `/health`.

## Railway Steps

1. Create a Railway project.
2. Choose **Deploy from GitHub repo**.
3. Select `gaithaziz/AqariX`.
4. Select branch `Ghaith`.
5. Let Railway use the root `railway.json`.
6. Add the variables below.
7. Deploy.
8. Open `/health` on the Railway domain.

Expected response:

```json
{"status":"ok","env":"staging"}
```

If `/health` returns `"env":"local"`, add or fix `APP_ENV=staging` in Railway variables, click **Apply changes**, and redeploy.

## Variables

Use the real values from local `services/api/.env` for `DATABASE_URL`, `CLERK_JWKS_URL`, `CLERK_ISSUER`, and `CLERK_SECRET_KEY`.

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
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://aqari-x.vercel.app
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET=
SENTRY_DSN=
```

For the free/minimal staging path, leave `REDIS_URL`, R2, and Sentry empty. The API fails open without Redis, and media/Sentry are not required for Phase 0 staging.

Do not commit real Railway, Neon, Clerk, R2, or Sentry secrets to the repo.
