from dataclasses import dataclass

from app.nlp.dialect_parser import ParsedListingText, parse_listing_text
from app.nlp.quality import ListingQuality, assess_listing_quality


MODEL_VERSION = "api-baseline-median-unit-price-v0.1"


@dataclass(frozen=True)
class UnitPriceComparable:
    median_unit_price_jod: float
    count: int


@dataclass(frozen=True)
class BaselineValuation:
    parsed: ParsedListingText
    quality: ListingQuality
    estimated_price_jod: int | None
    confidence: str
    reason: str | None
    unit_metric: str | None
    unit_area: float | None
    matched_unit_price_jod: float | None
    matched_count: int
    model_version: str = MODEL_VERSION
    method: str = "median_unit_price_baseline"


GROUP_UNIT_PRICE_LOOKUP = {
    "sale|land|al_husn|dunum": UnitPriceComparable(35000.0, 1),
    "sale|land|al_sareeh|dunum": UnitPriceComparable(36666.67, 1),
    "sale|apartment|aydoun|sqm": UnitPriceComparable(586.67, 1),
    "sale|apartment|eastern_district|sqm": UnitPriceComparable(593.75, 1),
    "sale|villa|aydoun|sqm": UnitPriceComparable(500.0, 1),
    "rent|apartment|yarmouk_university|sqm": UnitPriceComparable(2.36, 1),
    "rent|apartment|eastern_district|sqm": UnitPriceComparable(2.78, 1),
    "rent|commercial|eastern_district|sqm": UnitPriceComparable(7.78, 1),
}

FALLBACK_UNIT_PRICE_LOOKUP = {
    "sale|land|dunum": UnitPriceComparable(35833.34, 2),
    "sale|apartment|sqm": UnitPriceComparable(590.21, 2),
    "sale|villa|sqm": UnitPriceComparable(500.0, 1),
    "rent|apartment|sqm": UnitPriceComparable(2.57, 2),
    "rent|commercial|sqm": UnitPriceComparable(7.78, 1),
}


def estimate_baseline_valuation(text: str) -> BaselineValuation:
    parsed = parse_listing_text(text)
    quality = assess_listing_quality(parsed)
    unit_metric = "dunum" if parsed.property_type == "land" else "sqm"
    unit_area = parsed.land_area_dunum if unit_metric == "dunum" else parsed.area_sqm
    neighborhood = parsed.neighborhoods[0].key if parsed.neighborhoods else "unknown"

    if parsed.intent.value == "unknown" or not parsed.property_type or not unit_area:
        return BaselineValuation(
            parsed=parsed,
            quality=quality,
            estimated_price_jod=None,
            confidence="low",
            reason="missing_required_prediction_fields",
            unit_metric=unit_metric,
            unit_area=float(unit_area) if unit_area else None,
            matched_unit_price_jod=None,
            matched_count=0,
        )

    matched = GROUP_UNIT_PRICE_LOOKUP.get(
        model_key(parsed.intent.value, parsed.property_type, neighborhood, unit_metric)
    )
    confidence = "medium"
    reason = "matched_neighborhood_unit_price"
    if matched is None:
        matched = FALLBACK_UNIT_PRICE_LOOKUP.get(
            fallback_key(parsed.intent.value, parsed.property_type, unit_metric)
        )
        confidence = "low"
        reason = "matched_market_fallback_unit_price"

    if matched is None:
        return BaselineValuation(
            parsed=parsed,
            quality=quality,
            estimated_price_jod=None,
            confidence="low",
            reason="no_comparable_unit_price",
            unit_metric=unit_metric,
            unit_area=float(unit_area),
            matched_unit_price_jod=None,
            matched_count=0,
        )

    estimate = round(matched.median_unit_price_jod * float(unit_area))
    return BaselineValuation(
        parsed=parsed,
        quality=quality,
        estimated_price_jod=estimate,
        confidence=confidence,
        reason=reason,
        unit_metric=unit_metric,
        unit_area=float(unit_area),
        matched_unit_price_jod=matched.median_unit_price_jod,
        matched_count=matched.count,
    )


def model_key(intent: str, property_type: str, neighborhood: str, unit_metric: str) -> str:
    return "|".join([intent, property_type, neighborhood, unit_metric])


def fallback_key(intent: str, property_type: str, unit_metric: str) -> str:
    return "|".join([intent, property_type, unit_metric])
