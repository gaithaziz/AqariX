# Vercel Setup

Deploy `apps/web` as the React + Vite dashboard.

## Project Settings

- Repository: `gaithaziz/AqariX`.
- Branch: `Ghaith`.
- Framework preset: Vite.
- Root directory: leave as repository root.
- Install command: `pnpm install --frozen-lockfile`.
- Build command: `pnpm --dir apps/web build`.
- Output directory: `apps/web/dist`.

Required environment variables:

```bash
VITE_API_BASE_URL=https://aqarix-production.up.railway.app
VITE_CLERK_PUBLISHABLE_KEY=pk_test_bm90YWJsZS1oZW4tOTcuY2xlcmsuYWNjb3VudHMuZGV2JA
VITE_SENTRY_DSN=
VITE_APP_ENV=staging
```

The root `vercel.json` builds `apps/web` and serves the Vite `dist` output. Set `VITE_API_BASE_URL` to the deployed Railway API URL for staging.

## Vercel Steps

1. Create a Vercel project from `gaithaziz/AqariX`.
2. Select branch `Ghaith`.
3. Use the project settings above.
4. Add the environment variables above for Preview and Production.
5. Deploy.
6. Open the Vercel URL and confirm the listing search can load from Railway.

Do not add backend-only secrets such as `DATABASE_URL` or `CLERK_SECRET_KEY` to the Vercel web project.
