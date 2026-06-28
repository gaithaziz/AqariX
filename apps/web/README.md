# AqariX Web Shell

React + Vite implementation for the AqariX web experience.

## Scope

- Arabic-first interface with RTL as the default direction.
- Light/dark theme toggle.
- Listing discovery shell.
- Behavior-aware matching context.
- Listing feedback prompt.
- Dealer CRM and managed lead-room shells.
- Optional Clerk provider wiring through `VITE_CLERK_PUBLISHABLE_KEY`.

The app shell is analysis-engine agnostic. It shows stable product flows and can accept rules-based, human-reviewed, ML, or AI-backed outputs later without changing the user journey.

## Commands

From the repository root:

```bash
pnpm web:dev
pnpm web:build
pnpm web:lint
```

Local environment values live in `.env.example`.
