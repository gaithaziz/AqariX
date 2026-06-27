import json
from pathlib import Path

import pytest

from app.nlp.dialect_parser import HousingAudience, ListingIntent, parse_listing_text


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "irbid_listing_examples.json"


def test_parse_student_housing_near_yarmouk_north_gate() -> None:
    parsed = parse_listing_text(
        "شقة مفروشة للايجار في اربد قريبة من البوابة الشمالية، سكن طلاب، "
        "غرفتين و حمام 1، المساحة 90 متر، السعر 250 دينار"
    )

    assert parsed.city == "Irbid"
    assert parsed.intent == ListingIntent.rent
    assert parsed.property_type == "apartment"
    assert parsed.furnished is True
    assert parsed.price_jod == 250
    assert parsed.price_period is None
    assert parsed.area_sqm == 90
    assert parsed.bedrooms == 2
    assert parsed.bathrooms == 1
    assert HousingAudience.students in parsed.audiences
    assert parsed.landmarks[0].key == "yarmouk_university_north_gate"
    assert "near_yarmouk_university_north_gate" in parsed.location_signals


def test_parse_motivated_sale_listing_with_arabic_digits() -> None:
    parsed = parse_listing_text("للبيع فيلا في إربد بداعي السفر مساحة ٣٥٠ متر بسعر ١٨٥٠٠٠ دينار")

    assert parsed.city == "Irbid"
    assert parsed.intent == ListingIntent.sale
    assert parsed.property_type == "villa"
    assert parsed.motivated_seller is True
    assert parsed.area_sqm == 350
    assert parsed.price_jod == 185000


def test_parse_just_and_family_unfurnished_signal() -> None:
    parsed = parse_listing_text(
        "شقه غير مفروش للايجار للعائلات قرب جامعة العلوم والتكنولوجيا ومستشفى الملك عبدالله"
    )

    assert parsed.intent == ListingIntent.rent
    assert parsed.property_type == "apartment"
    assert parsed.furnished is False
    assert HousingAudience.families in parsed.audiences
    assert {landmark.key for landmark in parsed.landmarks} == {"just", "kauh"}
    assert "proximity_phrase" in parsed.location_signals


def test_parse_monthly_studio_near_city_center() -> None:
    parsed = parse_listing_text("استديو مفروش للايجار الشهري وسط البلد اربد السعر 180 دينار")

    assert parsed.city == "Irbid"
    assert parsed.intent == ListingIntent.rent
    assert parsed.property_type == "studio"
    assert parsed.furnished is True
    assert parsed.price_jod == 180
    assert parsed.price_period == "monthly"
    assert {landmark.key for landmark in parsed.landmarks} == {"irbid_city_center"}


def test_parse_yearly_family_apartment_with_word_counts() -> None:
    parsed = parse_listing_text(
        "شقة للايجار السنوي للعائلات في شارع الجامعة ثلاث غرف حمامين مساحة 140 متر"
    )

    assert parsed.intent == ListingIntent.rent
    assert parsed.price_period == "yearly"
    assert parsed.bedrooms == 3
    assert parsed.bathrooms == 2
    assert parsed.area_sqm == 140
    assert HousingAudience.families in parsed.audiences
    assert {landmark.key for landmark in parsed.landmarks} == {"university_street"}


def load_fixture_examples() -> list[dict[str, object]]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("example", load_fixture_examples(), ids=lambda example: example["name"])
def test_irbid_listing_fixture_examples(example: dict[str, object]) -> None:
    parsed = parse_listing_text(str(example["text"]))
    expected = example["expected"]

    assert isinstance(expected, dict)

    for field in (
        "city",
        "intent",
        "property_type",
        "price_jod",
        "price_period",
        "negotiable",
        "area_sqm",
        "land_area_dunum",
        "bedrooms",
        "bathrooms",
        "furnished",
        "motivated_seller",
    ):
        if field in expected:
            value = getattr(parsed, field)
            if isinstance(value, ListingIntent):
                value = value.value
            assert value == expected[field]

    if "audiences" in expected:
        assert {audience.value for audience in parsed.audiences} == set(expected["audiences"])

    if "landmarks" in expected:
        assert {landmark.key for landmark in parsed.landmarks} == set(expected["landmarks"])

    if "neighborhoods" in expected:
        assert {neighborhood.key for neighborhood in parsed.neighborhoods} == set(expected["neighborhoods"])

    if "location_signals" in expected:
        assert set(expected["location_signals"]).issubset(set(parsed.location_signals))
