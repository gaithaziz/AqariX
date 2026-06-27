# Baseline Valuation Modeling

This folder contains the first modeling-ready checks for AqariX Irbid data.

The current script is intentionally simple. It does not train a real ML model yet. It creates a baseline report from parsed seed posts so we can decide when the data is ready for real AVM modeling.

## Run

From the repository root:

```bash
python services/jobs/modeling/baseline_valuation.py
```

This writes `baseline_valuation_report.json`, which is ignored by Git.

## Current Gate

Real modeling should start after at least 300 model-ready Irbid listings.

Until then, use the parser, quality scoring, deduplication, and summary scripts to grow a clean dataset.
