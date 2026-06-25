# AqariX API

FastAPI service for the MVP shell.

This service currently implements non-AI product contracts only:

- Health check
- Listing search
- Buyer/investor intake
- Behavior events
- Deterministic recommendation placeholder
- Listing feedback
- Lead-room creation
- Redis-backed caching for read-heavy endpoints when `REDIS_URL` is configured

AI valuation, forecasting, and model-backed recommendation work is intentionally not implemented here.

Production caching belongs in the backend, not in individual clients. Web/mobile clients may keep short-lived UI cache for responsiveness, but shared cache entries, rate-limit counters, quota counters, and idempotency keys should use Redis through FastAPI/jobs.

## Local

```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload
pytest
```

With Docker:

```bash
docker compose up --build
```
