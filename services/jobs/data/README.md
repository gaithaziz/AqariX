# Real Irbid Listing Collection

Use `real_irbid_posts_template.csv` as the collection format for real public or approved Irbid listing examples.

See `collection_checklist.md` while collecting rows.
Use `source_log_template.csv` to track approved source categories.

## Columns

- `source`: where the listing came from, such as `manual_collection`, `dealer_partner`, or an approved classifieds source.
- `external_id`: stable ID you assign or copy from the source if available.
- `text`: raw listing text exactly as collected.
- `source_url`: optional public URL if allowed to store.
- `captured_at`: collection date in `YYYY-MM-DD` format.
- `collection_status`: `public`, `approved`, or `needs_review`.

## Privacy And Compliance

- Do not commit private phone numbers, names, or private group content without approval.
- Prefer public listings, partner-provided listings, or manual examples approved for project use.
- Keep raw collected files local unless the team agrees they can be shared.

## Suggested Workflow

1. Copy the template to a local ignored file:

```bash
copy services\jobs\data\real_irbid_posts_template.csv services\jobs\data\collected_irbid_posts.csv
```

2. Add real listing rows.

You can append one listing safely with:

```bash
uv run python services/jobs/data/append_collected_post.py --text "شقة للبيع في اربد مساحة 150 متر السعر 90 الف دينار"
```

The helper writes to `collected_irbid_posts.csv`, generates an `external_id`, and blocks duplicate IDs.
It also validates `source` against `source_log_template.csv` by default.

For public sources:

```bash
uv run python services/jobs/data/append_collected_post.py --source facebook_public --collection-status public --source-url "PUBLIC_URL" --text "LISTING_TEXT"
```

For dealer/friend approved examples:

```bash
uv run python services/jobs/data/append_collected_post.py --source dealer_partner --collection-status approved --text "LISTING_TEXT"
```

To append a whole prepared file:

```bash
uv run python services/jobs/data/append_collected_posts.py --input prepared_listings.csv --source facebook_public --collection-status public
```

The batch importer accepts `.csv` or `.json` input and fills missing `external_id` values automatically.
It also validates source keys against the approved source log.

3. Convert to ingest JSON:

```bash
python services/jobs/data/csv_to_ingest_posts.py --input services/jobs/data/collected_irbid_posts.csv
```

4. Or ingest the CSV directly through the API:

```bash
python services/jobs/data/ingest_collected_posts.py --input services/jobs/data/collected_irbid_posts.csv --api-base-url http://127.0.0.1:8000
```

5. Audit modeling readiness locally:

```bash
python services/jobs/data/audit_collected_posts.py --input services/jobs/data/collected_irbid_posts.csv
```

This writes `collected_irbid_posts.audit.json`.

6. Check collection progress:

```bash
uv run python services/jobs/data/collection_progress.py --input services/jobs/data/collected_irbid_posts.csv
```

This writes `collection_progress.json` and shows how many model-ready rows remain before the 30, 100, and 300 row targets, plus source and status mix.

7. Audit sources against the approved source log:

```bash
uv run python services/jobs/data/audit_collection_sources.py --input services/jobs/data/collected_irbid_posts.csv
```

This writes `collection_source_audit.json` and flags unknown source keys.

8. Export a modeling table after parsing enough rows:

```bash
python services/jobs/modeling/export_modeling_dataset.py --input services/jobs/data/collected_irbid_posts.csv --model-ready-only
```

9. Run the full collection-to-modeling pipeline:

```bash
uv run python services/jobs/data/run_collection_pipeline.py --input services/jobs/data/collected_irbid_posts.csv
```

This writes `collection_pipeline_report.json`, `valuation_modeling_dataset.csv`, and `valuation_experiment.json` for the current collection file.

10. Generate a collection backlog:

```bash
uv run python services/jobs/data/collection_backlog.py --input services/jobs/data/collected_irbid_posts.csv
```

This writes `collection_backlog.json` and highlights the next source, property type, and quality gaps to fill.

The exporter accepts the collected CSV directly and writes `services/jobs/modeling/valuation_modeling_dataset.csv`.
