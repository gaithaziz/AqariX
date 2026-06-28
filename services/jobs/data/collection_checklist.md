# Irbid Data Collection Checklist

Use this checklist while filling `collected_irbid_posts.csv`.

## Daily Target

- Collect at least 30 public or approved listings for the first real experiment.
- Aim for 100 model-ready listings before trying the Colab ML starter.
- Aim for 300 model-ready listings before promoting any valuation model.

## Good Rows

Each row should include:

- `source`: where the listing came from, such as `manual_collection`, `dealer_partner`, or `public_classifieds`.
- `external_id`: stable ID, such as `irbid-2026-0001`.
- `text`: raw listing text exactly as posted.
- `source_url`: public URL only if allowed.
- `captured_at`: collection date in `YYYY-MM-DD` format.

## Model-Ready Listing Text

Try to collect posts that include:

- intent: sale or rent
- property type: apartment, villa, land, or commercial
- price
- area in square meters or dunums
- neighborhood or landmark
- bedrooms/bathrooms when residential

## Privacy Rules

- Do not collect private group posts unless approved.
- Do not commit `collected_irbid_posts.csv`.
- Avoid names and phone numbers when possible.
- If phone numbers exist in public text, keep the raw data local until reviewed.

## Run After Adding Rows

From the repository root:

```bash
uv run python services/jobs/data/audit_collected_posts.py --input services/jobs/data/collected_irbid_posts.csv
uv run python services/jobs/modeling/export_modeling_dataset.py --input services/jobs/data/collected_irbid_posts.csv --model-ready-only
uv run python services/jobs/modeling/train_valuation_experiment.py
```
