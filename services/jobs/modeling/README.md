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

## Export Modeling Dataset

```bash
python services/jobs/modeling/export_modeling_dataset.py --model-ready-only
```

This writes `valuation_modeling_dataset.csv`, which is ignored by Git.

Use this CSV as the first Colab/sklearn/XGBoost input table. The target column is `target_price_jod`; the main baseline feature is `unit_price_jod`, and the other columns carry parsed property, location, quality, and text signals.

## Train Valuation Experiment

```bash
python services/jobs/modeling/train_valuation_experiment.py
```

This writes `valuation_experiment.json`, which is ignored by Git.

The experiment trains a deterministic median-comparable model from `valuation_modeling_dataset.csv` and reports holdout MAE/MAPE. It is a workflow gate before heavier ML, not the final AVM.

## Colab ML Starter

Upload `valuation_modeling_dataset.csv` to Colab, then run:

```bash
pip install -r colab_requirements.txt
python colab_valuation_starter.py --input valuation_modeling_dataset.csv
```

This trains a scikit-learn gradient boosting starter model and writes `valuation_ml_experiment.json`. Start using this after the dataset has at least 100 model-ready rows.

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
