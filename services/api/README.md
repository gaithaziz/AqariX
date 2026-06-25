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

AI valuation, forecasting, and model-backed recommendation work is intentionally not implemented here.

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
