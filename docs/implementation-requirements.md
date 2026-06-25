# Implementation Requirements

Status: Planned

This file lists what a developer needs before implementing AqariX.

## Required Local Tools

Install:

- Git
- Node.js 20 LTS or newer
- pnpm 9 or newer
- Python 3.11 or newer
- uv or Poetry for Python dependency management
- Flutter stable SDK
- Xcode for iOS builds on macOS
- Android Studio and Android SDK for Android builds
- PostgreSQL client tools: `psql`
- Docker Desktop, optional but useful for local Postgres and service parity
- GitHub CLI, optional but recommended

Recommended checks:

```bash
git --version
node --version
pnpm --version
python3 --version
flutter --version
flutter doctor
psql --version
```

## Flutter Requirements

Flutter is required for `apps/mobile`.

Required setup:

- Flutter stable channel.
- Dart version bundled with Flutter.
- iOS simulator configured through Xcode.
- Android emulator configured through Android Studio.
- Arabic/RTL rendering must be tested early.

Recommended checks:

```bash
flutter doctor
flutter devices
flutter create --platforms=ios,android apps/mobile
```

Do not start deep Flutter implementation until:

- API contracts for auth, listings, recommendations, behavior events, listing feedback, and lead rooms are stable enough for the first vertical slice.
- Clerk mobile auth approach is confirmed.

## Web Dashboard Requirements

Stack: React + Vite.

Used for:

- Seller/dealer portal
- Admin dashboard
- Agency operator dashboard
- Early buyer/investor web prototype if faster than mobile

Required setup:

- Node.js 20+
- pnpm
- Vite
- React
- TypeScript
- Clerk React SDK

Expected first scaffold:

```bash
pnpm create vite apps/web --template react-ts
```

## Backend Requirements

Stack: FastAPI.

Used for:

- REST API
- Clerk JWT verification
- Listings
- Search
- Recommendations
- Behavior events
- Listing feedback
- Offering analysis
- Lead rooms
- Admin APIs

Required setup:

- Python 3.11+
- FastAPI
- Uvicorn
- SQLAlchemy or SQLModel
- Alembic for migrations
- Pydantic
- psycopg or asyncpg
- pytest

Expected first scaffold:

```bash
mkdir -p services/api
```

Required backend checks:

- `/health` endpoint
- OpenAPI docs available in development
- Database connectivity
- Clerk JWT verification
- Authorization tests for user-owned records

## Database Requirements

Provider: Neon Postgres.

Required extensions:

```sql
create extension if not exists postgis;
create extension if not exists vector;
```

Required capabilities:

- Relational data for users, roles, properties, listings, lead rooms, and feedback.
- PostGIS geospatial queries for map search, nearby alternatives, and comparable properties.
- pgvector for MVP recommendation matching.
- Migrations through Alembic or another explicit migration tool.
- Separate local, staging, and production databases.

Do not use Supabase for MVP auth or hosting.

## Auth Requirements

Provider: Clerk.

Required setup:

- Clerk development project.
- Clerk staging/production project before public launch.
- Role metadata or internal role mapping for buyer, investor, seller, dealer, admin, and agency operator.
- Clerk JWT verification in FastAPI.
- Clerk React SDK in web dashboard.
- Clerk mobile auth approach confirmed before Flutter implementation.

Authorization rule:

Clerk authenticates identity. AqariX backend still owns authorization for records, roles, organizations, listings, lead rooms, behavior events, and listing feedback.

## Storage Requirements

Provider: Cloudflare R2.

Used for:

- Listing photos
- Agency assets
- Generated reports later

MVP fallback:

- Local file storage may be used for early development only.
- Production must use object storage.

Required controls:

- File type validation.
- File size limits.
- Private upload flow for seller/dealer media.
- Public-safe delivery URLs for approved listing media.

## Hosting Requirements

Approved MVP hosting:

- API and jobs: Render
- Web dashboard: Vercel
- Database: Neon
- Auth: Clerk
- Media storage: Cloudflare R2

Required environments:

- Local
- Staging
- Production

Each environment must have separate:

- Clerk project or app config
- Neon database
- R2 bucket or prefix
- API keys
- Sentry project
- Analytics config

## Maps Requirements

Map provider is still a decision point.

Compare before implementation:

- Google Maps
- Mapbox
- MapLibre/OpenStreetMap

Decision criteria:

- Jordan map quality
- Arabic labels
- Cost at expected usage
- Flutter support
- Web support
- Geocoding quality
- Terms for real estate use

Do not hard-code a provider abstraction too early, but keep map usage behind a small local adapter.

## Environment Variables

Expected backend variables:

```bash
DATABASE_URL=
CLERK_JWKS_URL=
CLERK_ISSUER=
CLERK_SECRET_KEY=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET=
SENTRY_DSN=
APP_ENV=local
```

Expected web variables:

```bash
VITE_API_BASE_URL=
VITE_CLERK_PUBLISHABLE_KEY=
VITE_SENTRY_DSN=
VITE_APP_ENV=local
```

Expected mobile variables:

```bash
API_BASE_URL=
CLERK_PUBLISHABLE_KEY=
APP_ENV=local
```

Never commit real secrets.

## First Implementation Readiness Checklist

Before coding Phase 0:

- Clerk development project exists.
- Neon development database exists.
- PostGIS and pgvector are enabled.
- Render account/project target exists.
- Vercel project target exists.
- Cloudflare R2 bucket exists or local storage fallback is approved.
- Local Flutter doctor passes for at least one target platform.
- Node, pnpm, Python, and psql are installed.
- `.env.example` files are created for API, web, and mobile.
- First vertical slice from [implementation-plan.md](./implementation-plan.md) is accepted.

## Verification Commands To Add During Implementation

Backend:

```bash
pytest
ruff check .
```

Web:

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Mobile:

```bash
flutter analyze
flutter test
flutter build apk --debug
```

Database:

```bash
alembic upgrade head
alembic downgrade -1
```

Use the repo's actual scripts once they exist.
