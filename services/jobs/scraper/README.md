# Irbid Listing Ingestion Prototype

This folder contains the local prototype for the AqariX AI ingestion flow.

## Files

- `sample_irbid_posts.json`: manual seed posts that represent Irbid real estate listing text.
- `parse_sample_posts.py`: parses the sample posts locally without calling the API.
- `ingest_sample_posts.py`: sends the sample posts to the backend ingest endpoint.

Generated outputs are ignored by Git:

- `parsed_irbid_posts.json`
- `ingested_irbid_posts_response.json`

## Local Parse

From the repository root:

```bash
python services/jobs/scraper/parse_sample_posts.py
```

This writes `parsed_irbid_posts.json`.

## API Ingest

Start the API first:

```bash
cd services/api
uv run --extra dev uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then from the repository root:

```bash
python services/jobs/scraper/ingest_sample_posts.py --api-base-url http://127.0.0.1:8000
```

This writes `ingested_irbid_posts_response.json`.

## Tests

From the repository root:

```bash
python -m pytest services/jobs/tests
```
