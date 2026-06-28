# AqariX API Service

This directory contains the FastAPI backend REST API.

## Tech Stack
- **Framework**: FastAPI
- **Server**: Uvicorn
- **ORM**: SQLAlchemy or SQLModel
- **Database**: PostgreSQL (PostGIS + pgvector)
- **Migrations**: Alembic

## Getting Started

1. Copy `.env.example` to `.env` and configure your credentials.
2. If you want the learned valuation endpoint to use a trained artifact, set `VALUATION_MODEL_ARTIFACT_PATH` to the `valuation_ml_model.joblib` file.
3. Set up virtual environment and install dependencies (e.g. using `uv` or `poetry`).
4. Run migrations:
   ```bash
   alembic upgrade head
   ```
5. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

## Development Commands
- Run tests: `pytest`
- Format & lint: `ruff check .`

## AI Valuation

- `POST /ai/baseline-valuation` returns the deterministic comparable-price baseline.
- `POST /ai/valuation` uses the trained learned model when `VALUATION_MODEL_ARTIFACT_PATH` is set and the artifact exists, otherwise it falls back to the baseline.
