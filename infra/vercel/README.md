# Vercel Setup

Deploy `apps/web` as the React + Vite dashboard.

Required environment variables:

```bash
VITE_API_BASE_URL=
VITE_CLERK_PUBLISHABLE_KEY=
VITE_SENTRY_DSN=
VITE_APP_ENV=
```

The root `vercel.json` builds `apps/web` and serves the Vite `dist` output. Set `VITE_API_BASE_URL` to the deployed Railway API URL for staging.
