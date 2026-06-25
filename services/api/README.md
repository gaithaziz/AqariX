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
2. Set up virtual environment and install dependencies (e.g. using `uv` or `poetry`).
3. Run migrations:
   ```bash
   alembic upgrade head
   ```
4. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

## Development Commands
- Run tests: `pytest`
- Format & lint: `ruff check .`
