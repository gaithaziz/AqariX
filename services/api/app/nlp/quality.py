from dataclasses import dataclass, field

from app.nlp.dialect_parser import ParsedListingText


@dataclass
class ListingQuality:
    score: int
    grade: str
    is_model_ready: bool
    missing_fields: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def assess_listing_quality(parsed: ParsedListingText) -> ListingQuality:
    score = 0
    missing_fields: list[str] = []
    warnings: list[str] = []

    score += _score_field(parsed.intent.value != "unknown", "intent", missing_fields, 15)
    score += _score_field(parsed.property_type is not None, "property_type", missing_fields, 15)
    score += _score_field(parsed.price_jod is not None, "price_jod", missing_fields, 20)

    has_location = bool(parsed.city or parsed.neighborhoods or parsed.landmarks)
    score += _score_field(has_location, "location_signal", missing_fields, 20)

    if parsed.property_type == "land":
        has_area = parsed.land_area_dunum is not None or parsed.area_sqm is not None
        score += _score_field(has_area, "land_area", missing_fields, 20)
    else:
        score += _score_field(parsed.area_sqm is not None, "area_sqm", missing_fields, 20)

    detail_points = _residential_detail_points(parsed)
    score += detail_points
    if detail_points < 5 and parsed.property_type in {"apartment", "villa", "studio"}:
        warnings.append("residential_details_incomplete")

    if parsed.price_jod is not None and parsed.price_jod <= 0:
        warnings.append("invalid_price")
    if parsed.price_jod is not None and parsed.intent.value == "rent" and parsed.price_jod > 10_000:
        warnings.append("rent_price_may_be_sale_price")
    if parsed.price_jod is not None and parsed.intent.value == "sale" and parsed.price_jod < 10_000:
        warnings.append("sale_price_may_be_rent_price")

    score = min(score, 100)
    grade = _grade(score)
    is_model_ready = score >= 75 and not {"intent", "property_type", "price_jod"} & set(missing_fields)

    return ListingQuality(
        score=score,
        grade=grade,
        is_model_ready=is_model_ready,
        missing_fields=missing_fields,
        warnings=warnings,
    )


def _score_field(condition: bool, field_name: str, missing_fields: list[str], points: int) -> int:
    if condition:
        return points
    missing_fields.append(field_name)
    return 0


def _residential_detail_points(parsed: ParsedListingText) -> int:
    if parsed.property_type not in {"apartment", "villa", "studio"}:
        return 10

    points = 0
    if parsed.bedrooms is not None or parsed.property_type == "studio":
        points += 4
    if parsed.bathrooms is not None:
        points += 3
    if parsed.furnished is not None:
        points += 3
    return points


def _grade(score: int) -> str:
    if score >= 85:
        return "high"
    if score >= 65:
        return "medium"
    return "low"
