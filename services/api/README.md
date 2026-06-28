# AqariX API

FastAPI service for the MVP shell.

This service currently implements provider-agnostic product contracts:

- Health check
- Listing search
- Public Irbid demo zone catalog
- Protected manual listing ingestion for demo/data batches
- Buyer/investor intake
- Behavior events
- Rules-based recommendation placeholder
- Rules-based comparable listing candidates
- Offering-analysis shell with reusable Redis/PostgreSQL snapshots, evidence sources, confidence labels, and caveats
- Saved offerings and saved searches as recommendation inputs
- Listing feedback
- Lead-room creation
- Idempotency-key replay for offering analysis and lead-room creation
- Redis-backed caching for read-heavy endpoints when `REDIS_URL` is configured
- Redis-backed rate limits, write quotas, and request-volume cost alerts when `REDIS_URL` is configured

Production valuation, forecasting, and advanced ranking engines are intentionally not coupled to this API shell yet. They can be added later behind the same contracts.

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
