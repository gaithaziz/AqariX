# AqariX Web Shell

React + Vite implementation for the AqariX web experience.

## Scope

- Arabic-first interface with RTL as the default direction.
- Light/dark theme toggle.
- Listing discovery shell.
- Behavior-aware recommendation context.
- Listing feedback prompt.
- Dealer CRM and managed lead-room shells.
- Optional Clerk provider wiring through `VITE_CLERK_PUBLISHABLE_KEY`.

AI valuation, forecasting, and model-backed recommendations are intentionally out of scope for this app shell.

## Commands

From the repository root:

```bash
pnpm web:dev
pnpm web:build
pnpm web:lint
```

Local environment values live in `.env.example`.
