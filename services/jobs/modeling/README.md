# Baseline Valuation Modeling

This folder contains the first modeling-ready checks for AqariX Irbid data.

The current model is intentionally simple. It uses median unit prices by intent, property type, neighborhood, and unit metric. This gives AqariX a working baseline before heavier ML.

## Baseline Report

From the repository root:

```bash
python services/jobs/modeling/baseline_valuation.py
```

This writes `baseline_valuation_report.json`, which is ignored by Git.

## Train Baseline Model

```bash
python services/jobs/modeling/train_baseline_model.py
```

This writes `baseline_valuation_model.json`, which is ignored by Git.

## Predict With Baseline Model

```bash
python services/jobs/modeling/predict_baseline_model.py --text "شقة للبيع في ايدون ثلاث غرف حمامين مساحة 150 متر"
```

Predictions are decision-support estimates only. They must show confidence and should not be presented as guaranteed market value.

## Promotion Check

```bash
python services/jobs/modeling/evaluate_model_promotion.py
```

This writes `baseline_valuation_model_card.json`, which is ignored by Git.

Promotion is blocked until there are at least 300 model-ready records and MAPE is at or below 20%.

## Current Gate

Real modeling should start after at least 300 model-ready Irbid listings.

Until then, use the parser, quality scoring, deduplication, and summary scripts to grow a clean dataset.
