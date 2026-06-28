import sys
import tempfile
from pathlib import Path


JOBS_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = JOBS_ROOT.parent / "api"
for path in (JOBS_ROOT, API_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from scraper.parse_sample_posts import DEFAULT_INPUT  # noqa: E402
from modeling.export_modeling_dataset import build_modeling_rows, load_parsed_posts, write_modeling_dataset  # noqa: E402
from modeling.train_valuation_ml_model import ensure_dataset  # noqa: E402
from modeling.valuation_ml import (  # noqa: E402
    MODEL_VERSION,
    load_model_bundle,
    predict_price_from_text,
    run_valuation_ml_experiment,
)


def test_train_valuation_ml_model_from_seed_dataset() -> None:
    rows = build_modeling_rows(load_parsed_posts(DEFAULT_INPUT), model_ready_only=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        dataset_path = tmp_path / "valuation_modeling_dataset.csv"
        model_output = tmp_path / "valuation_ml_model.joblib"
        report_output = tmp_path / "valuation_ml_experiment.json"
        write_modeling_dataset(rows, dataset_path)

        report = run_valuation_ml_experiment(
            dataset_path,
            model_output=model_output,
            report_output=report_output,
        )

        assert model_output.exists()
        assert report_output.exists()

    assert report["model_name"] == "sklearn_ridge_text_regressor"
    assert report["model_version"] == MODEL_VERSION
    assert report["dataset"]["usable_rows"] == len(rows)
    assert report["readiness"]["status"] == "collect_more_data"


def test_train_wrapper_bootstraps_dataset_from_raw_input() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        dataset_path = tmp_path / "valuation_modeling_dataset.csv"

        built_dataset = ensure_dataset(dataset_path, DEFAULT_INPUT)

        assert built_dataset == dataset_path
        assert dataset_path.exists()

        rows = build_modeling_rows(load_parsed_posts(DEFAULT_INPUT), model_ready_only=True)
        content = dataset_path.read_text(encoding="utf-8")
        assert "target_price_jod" in content
        assert len(content.splitlines()) == len(rows) + 1


def test_predict_valuation_ml_model_on_seed_listing() -> None:
    rows = build_modeling_rows(load_parsed_posts(DEFAULT_INPUT), model_ready_only=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        dataset_path = tmp_path / "valuation_modeling_dataset.csv"
        model_output = tmp_path / "valuation_ml_model.joblib"
        report_output = tmp_path / "valuation_ml_experiment.json"
        write_modeling_dataset(rows, dataset_path)
        run_valuation_ml_experiment(
            dataset_path,
            model_output=model_output,
            report_output=report_output,
        )

        bundle = load_model_bundle(model_output)
        prediction = predict_price_from_text(rows[0]["raw_text"], model_output)

    assert bundle["model_version"] == MODEL_VERSION
    assert prediction["estimated_price_jod"] is not None
    assert prediction["reason"] == "ml_ridge_text_regressor"
    assert prediction["method"] == "sklearn_ridge_text_regressor"
    assert prediction["training_rows"] == len(rows)
    assert prediction["confidence"] in {"low", "medium"}
    assert prediction["feature_completeness"] > 0


def test_predict_valuation_ml_model_rejects_empty_text() -> None:
    rows = build_modeling_rows(load_parsed_posts(DEFAULT_INPUT), model_ready_only=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        dataset_path = tmp_path / "valuation_modeling_dataset.csv"
        model_output = tmp_path / "valuation_ml_model.joblib"
        report_output = tmp_path / "valuation_ml_experiment.json"
        write_modeling_dataset(rows, dataset_path)
        run_valuation_ml_experiment(
            dataset_path,
            model_output=model_output,
            report_output=report_output,
        )

        prediction = predict_price_from_text("hello world", model_output)

    assert prediction["estimated_price_jod"] is None
    assert prediction["confidence"] == "low"
    assert prediction["reason"] == "missing_required_prediction_fields"
