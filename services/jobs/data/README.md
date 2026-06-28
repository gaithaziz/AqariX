# Real Irbid Listing Collection

Use `real_irbid_posts_template.csv` as the collection format for real public or approved Irbid listing examples.

## Columns

- `source`: where the listing came from, such as `manual_collection`, `dealer_partner`, or an approved classifieds source.
- `external_id`: stable ID you assign or copy from the source if available.
- `text`: raw listing text exactly as collected.
- `source_url`: optional public URL if allowed to store.
- `captured_at`: collection date in `YYYY-MM-DD` format.

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

6. Export a modeling table after parsing enough rows:

```bash
python services/jobs/modeling/export_modeling_dataset.py --input services/jobs/data/collected_irbid_posts.csv --model-ready-only
```

The exporter accepts the collected CSV directly and writes `services/jobs/modeling/valuation_modeling_dataset.csv`.
