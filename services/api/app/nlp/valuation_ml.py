import sys
from pathlib import Path
from typing import Any


JOBS_ROOT = Path(__file__).resolve().parents[3] / "jobs"
if str(JOBS_ROOT) not in sys.path:
    sys.path.insert(0, str(JOBS_ROOT))

from app.nlp.baseline_valuation import estimate_baseline_valuation  # noqa: E402
from app.repository import parsed_to_response  # noqa: E402
from app.settings import get_settings  # noqa: E402
from modeling.valuation_ml import DEFAULT_MODEL_OUTPUT, predict_price_from_text  # noqa: E402


DEFAULT_MODEL_ARTIFACT = DEFAULT_MODEL_OUTPUT


def resolve_model_artifact() -> Path:
    configured = get_settings().valuation_model_artifact_path.strip()
    if configured:
        return Path(configured).expanduser()
    return DEFAULT_MODEL_ARTIFACT


MODEL_ARTIFACT = resolve_model_artifact()


def estimate_valuation(text: str) -> dict[str, Any]:
    if MODEL_ARTIFACT.exists():
        prediction = predict_price_from_text(text, MODEL_ARTIFACT)
        prediction.setdefault("unit_metric", None)
        prediction.setdefault("unit_area", None)
        prediction.setdefault("matched_unit_price_jod", None)
        prediction.setdefault("matched_count", None)
        return prediction

    valuation = estimate_baseline_valuation(text)
    parsed_response = parsed_to_response(valuation.parsed)
    return {
        "estimated_price_jod": valuation.estimated_price_jod,
        "confidence": valuation.confidence,
        "reason": valuation.reason,
        "method": valuation.method,
        "model_version": valuation.model_version,
        "unit_metric": valuation.unit_metric,
        "unit_area": valuation.unit_area,
        "matched_unit_price_jod": valuation.matched_unit_price_jod,
        "matched_count": valuation.matched_count,
        "feature_completeness": None,
        "training_rows": None,
        "quality": parsed_response.quality.model_dump(mode="json"),
        "parsed": parsed_response.model_dump(mode="json"),
    }
