import re
from dataclasses import dataclass, field
from enum import Enum


class ListingIntent(str, Enum):
    sale = "sale"
    rent = "rent"
    unknown = "unknown"


class HousingAudience(str, Enum):
    students = "students"
    families = "families"
    singles = "singles"


@dataclass(frozen=True)
class LandmarkSignal:
    key: str
    display_name: str
    latitude: float
    longitude: float
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class NeighborhoodSignal:
    key: str
    display_name: str
    aliases: tuple[str, ...]


@dataclass
class ParsedListingText:
    original_text: str
    normalized_text: str
    city: str | None = None
    intent: ListingIntent = ListingIntent.unknown
    property_type: str | None = None
    price_jod: int | None = None
    price_period: str | None = None
    price_per_sqm_jod: float | None = None
    price_per_dunum_jod: float | None = None
    negotiable: bool = False
    area_sqm: int | None = None
    land_area_dunum: float | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    floor_number: int | None = None
    building_age_years: int | None = None
    furnished: bool | None = None
    has_phone_number: bool = False
    contact_exposure: bool = False
    audiences: list[HousingAudience] = field(default_factory=list)
    motivated_seller: bool = False
    neighborhoods: list[NeighborhoodSignal] = field(default_factory=list)
    landmarks: list[LandmarkSignal] = field(default_factory=list)
    location_signals: list[str] = field(default_factory=list)
    extracted_terms: list[str] = field(default_factory=list)


LANDMARKS = (
    LandmarkSignal(
        key="yarmouk_university_north_gate",
        display_name="Yarmouk University North Gate",
        latitude=32.5386,
        longitude=35.8578,
        aliases=("البوابة الشمالية", "بوابة الشمال", "بوابة اليرموك الشمالية", "قريبة من البوابة"),
    ),
    LandmarkSignal(
        key="yarmouk_university",
        display_name="Yarmouk University",
        latitude=32.5359,
        longitude=35.8575,
        aliases=("جامعة اليرموك", "اليرموك", "قرب اليرموك"),
    ),
    LandmarkSignal(
        key="just",
        display_name="Jordan University of Science and Technology",
        latitude=32.495,
        longitude=35.9912,
        aliases=("جامعة العلوم والتكنولوجيا", "التكنو", "just", "جست", "بوابة التكنو"),
    ),
    LandmarkSignal(
        key="kauh",
        display_name="King Abdullah University Hospital",
        latitude=32.4958,
        longitude=35.9884,
        aliases=("مستشفى الملك عبدالله", "مستشفى الملك عبد الله", "مستشفى الجامعة"),
    ),
    LandmarkSignal(
        key="university_street",
        display_name="University Street",
        latitude=32.5372,
        longitude=35.8519,
        aliases=("شارع الجامعة", "شارع جامعة اليرموك"),
    ),
    LandmarkSignal(
        key="irbid_city_center",
        display_name="Irbid City Center",
        latitude=32.5556,
        longitude=35.85,
        aliases=("وسط البلد", "وسط اربد", "دوار الساعه", "دوار الساعة"),
    ),
)

NEIGHBORHOODS = (
    NeighborhoodSignal(key="al_husn", display_name="Al Husn", aliases=("الحصن", "حكما الحصن")),
    NeighborhoodSignal(key="aidoun", display_name="Aidoun", aliases=("ايدون", "ايدون")),
    NeighborhoodSignal(key="al_nuzha", display_name="Al Nuzha", aliases=("النزهه", "النزهة")),
    NeighborhoodSignal(key="eastern_district", display_name="Eastern District", aliases=("الحي الشرقي",)),
    NeighborhoodSignal(key="hay_al_jameaa", display_name="University District", aliases=("حي الجامعه", "حي الجامعة")),
    NeighborhoodSignal(key="sarih", display_name="Sarih", aliases=("الصريح", "صريح")),
    NeighborhoodSignal(key="bushra", display_name="Bushra", aliases=("بشرى", "بشري")),
    NeighborhoodSignal(key="hakama", display_name="Hakama", aliases=("حكما", "حكما اربد")),
    NeighborhoodSignal(key="southern_irbid", display_name="Southern Irbid", aliases=("جنوب اربد", "جنوب إربد")),
    NeighborhoodSignal(key="al_barha", display_name="Al Barha", aliases=("البارحه", "البارحة")),
)

PROPERTY_TYPE_PATTERNS = (
    ("apartment", ("شقة", "شقه", "شقق")),
    ("villa", ("فيلا", "فلة", "فلل")),
    ("studio", ("ستوديو", "استوديو", "استديو", "سكن استوديو")),
    ("land", ("ارض", "أرض", "قطعة")),
    ("commercial", ("محل", "مخزن", "تجاري", "معرض")),
)

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
BEDROOM_WORDS = {
    "غرفه": 1,
    "غرفة": 1,
    "غرفتين": 2,
    "غرفتان": 2,
    "ثلاث غرف": 3,
    "ثلاثه غرف": 3,
    "ثلاثة غرف": 3,
    "اربع غرف": 4,
    "اربعه غرف": 4,
    "أربع غرف": 4,
    "خمس غرف": 5,
}
BATHROOM_WORDS = {
    "حمام": 1,
    "حمامين": 2,
    "حمام واحد": 1,
    "حمامين اثنين": 2,
    "ثلاث حمامات": 3,
    "ثلاثه حمامات": 3,
}


def parse_listing_text(text: str) -> ParsedListingText:
    normalized = normalize_arabic_text(text)
    parsed = ParsedListingText(original_text=text, normalized_text=normalized)
    parsed.city = "Irbid" if _contains_any(normalized, ("اربد", "إربد")) else None
    parsed.intent = _extract_intent(normalized)
    parsed.property_type = _extract_property_type(normalized)
    parsed.price_jod = _extract_price_jod(normalized)
    parsed.price_period = _extract_price_period(normalized)
    parsed.negotiable = _extract_negotiable(normalized)
    parsed.area_sqm = _extract_area_sqm(normalized)
    parsed.land_area_dunum = _extract_land_area_dunum(normalized)
    parsed.price_per_sqm_jod = _price_per_unit(parsed.price_jod, parsed.area_sqm)
    parsed.price_per_dunum_jod = _price_per_unit(parsed.price_jod, parsed.land_area_dunum)
    parsed.bedrooms = _extract_count(normalized, ("غرف", "غرفة", "نوم"))
    parsed.bathrooms = _extract_count(normalized, ("حمام", "حمامات"))
    parsed.floor_number = _extract_floor_number(normalized)
    parsed.building_age_years = _extract_building_age_years(normalized)
    parsed.furnished = _extract_furnished(normalized)
    parsed.has_phone_number = _has_phone_number(normalized)
    parsed.contact_exposure = _extract_contact_exposure(normalized, parsed.has_phone_number)
    parsed.audiences = _extract_audiences(normalized)
    parsed.motivated_seller = _contains_any(
        normalized,
        ("بداعي السفر", "لدواعي السفر", "للسفر", "مستعجل", "سعر مغري", "لقطة"),
    )
    parsed.neighborhoods = _extract_neighborhoods(normalized)
    parsed.landmarks = _extract_landmarks(normalized)
    parsed.location_signals = _extract_location_signals(normalized, parsed.landmarks)
    parsed.extracted_terms = _extract_terms(normalized)
    return parsed


def normalize_arabic_text(text: str) -> str:
    normalized = text.strip().lower().translate(ARABIC_DIGITS)
    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
        "ؤ": "و",
        "ئ": "ي",
        "ـ": "",
    }
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    normalized = re.sub(r"[،,:;|/\\()\[\]{}]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _extract_intent(text: str) -> ListingIntent:
    if _contains_any(text, ("للايجار", "ايجار", "اجار", "للإيجار", "للاستئجار")):
        return ListingIntent.rent
    if _contains_any(text, ("للبيع", "بيع", "تمليك")):
        return ListingIntent.sale
    return ListingIntent.unknown


def _extract_property_type(text: str) -> str | None:
    for property_type, aliases in PROPERTY_TYPE_PATTERNS:
        if _contains_any(text, aliases):
            return property_type
    return None


def _extract_price_jod(text: str) -> int | None:
    thousand_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:الف|ألف|k)\s*(?:دينار|د\.?ا|jod|jd)?", text)
    if thousand_match:
        return int(float(thousand_match.group(1)) * 1000)

    patterns = (
        r"(\d{2,7})\s*(?:دينار|د\.?ا|jod|jd)",
        r"(?:السعر|بسعر|مطلوب|المطلوب)\s*(\d{2,7})",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return None


def _extract_negotiable(text: str) -> bool:
    return _contains_any(text, ("قابل للتفاوض", "قابل للنقاش", "في مجال", "قابل للمفاوضه"))


def _extract_price_period(text: str) -> str | None:
    if _contains_any(text, ("شهري", "بالشهر", "كل شهر", "اجار شهري")):
        return "monthly"
    if _contains_any(text, ("سنوي", "بالسنه", "بالسنة", "كل سنة", "اجار سنوي")):
        return "yearly"
    return None


def _extract_area_sqm(text: str) -> int | None:
    patterns = (
        r"(?:مساحه|المساحه)\s*(\d{2,5})",
        r"(\d{2,5})\s*(?:متر|م2|متر مربع)",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return None


def _extract_land_area_dunum(text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:دونم|دونمات)", text)
    if match:
        return float(match.group(1))
    return None


def _price_per_unit(price_jod: int | None, area: int | float | None) -> float | None:
    if price_jod is None or area in (None, 0):
        return None
    return round(price_jod / float(area), 2)


def _extract_count(text: str, labels: tuple[str, ...]) -> int | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    patterns = (
        rf"(\d+)\s*(?:{label_pattern})",
        rf"(?:{label_pattern})\s*(\d+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    word_map = BEDROOM_WORDS if any(label in ("غرف", "غرفة", "نوم") for label in labels) else BATHROOM_WORDS
    for word, value in sorted(word_map.items(), key=lambda item: len(item[0]), reverse=True):
        if word in text:
            return value
    return None


def _extract_floor_number(text: str) -> int | None:
    floor_words = {
        "ارضي": 0,
        "الارضي": 0,
        "اول": 1,
        "الاول": 1,
        "ثاني": 2,
        "الثاني": 2,
        "ثالث": 3,
        "الثالث": 3,
        "رابع": 4,
        "الرابع": 4,
    }
    match = re.search(r"(?:طابق|الطابق|دور|الدور)\s*(\d+)", text)
    if match:
        return int(match.group(1))
    for word, value in floor_words.items():
        if _contains_any(text, (f"طابق {word}", f"الطابق {word}", f"دور {word}", f"الدور {word}")):
            return value
    return None


def _extract_building_age_years(text: str) -> int | None:
    patterns = (
        r"(?:عمر البناء|عمر البنا|عمر العماره|عمر العمارة)\s*(\d{1,3})",
        r"(\d{1,3})\s*(?:سنوات|سنه|سنة)\s*(?:عمر|بناء|البناء)",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    if _contains_any(text, ("بناء جديد", "جديده لم تسكن", "جديدة لم تسكن", "اول ساكن")):
        return 0
    return None


def _has_phone_number(text: str) -> bool:
    compact = re.sub(r"\D", "", text)
    return bool(re.search(r"(?:9627|07)\d{7,8}", compact))


def _extract_contact_exposure(text: str, has_phone_number: bool) -> bool:
    return has_phone_number or _contains_any(text, ("واتساب", "whatsapp", "اتصال", "للتواصل", "تواصل"))


def _extract_furnished(text: str) -> bool | None:
    if _contains_any(text, ("غير مفروش", "بدون فرش", "فاضي")):
        return False
    if _contains_any(text, ("مفروش", "فرش كامل", "مع فرش", "فرش جديد")):
        return True
    return None


def _extract_audiences(text: str) -> list[HousingAudience]:
    audiences: list[HousingAudience] = []
    if _contains_any(text, ("طلاب", "طالبات", "سكن طلاب", "سكن طالبات")):
        audiences.append(HousingAudience.students)
    if _contains_any(text, ("عائلات", "عوائل", "سكن عائلي", "للعائلات")):
        audiences.append(HousingAudience.families)
    if _contains_any(text, ("شباب", "سكن شباب", "عزاب")):
        audiences.append(HousingAudience.singles)
    return audiences


def _extract_landmarks(text: str) -> list[LandmarkSignal]:
    matches = []
    for landmark in LANDMARKS:
        if _contains_any(text, tuple(normalize_arabic_text(alias) for alias in landmark.aliases)):
            matches.append(landmark)
    return matches


def _extract_neighborhoods(text: str) -> list[NeighborhoodSignal]:
    matches = []
    for neighborhood in NEIGHBORHOODS:
        if _contains_any(text, tuple(normalize_arabic_text(alias) for alias in neighborhood.aliases)):
            matches.append(neighborhood)
    return matches


def _extract_location_signals(text: str, landmarks: list[LandmarkSignal]) -> list[str]:
    signals = [f"near_{landmark.key}" for landmark in landmarks]
    if _contains_any(text, ("قريب", "قريبه", "قرب", "بجانب", "خلف", "مقابل")):
        signals.append("proximity_phrase")
    return sorted(set(signals))


def _extract_terms(text: str) -> list[str]:
    tracked_terms = (
        "بداعي السفر",
        "سكن شباب",
        "سكن طلاب",
        "سكن طالبات",
        "قريبه من البوابه",
        "البوابه الشماليه",
        "شارع الجامعه",
        "وسط البلد",
        "الحصن",
        "ايدون",
        "النزهه",
        "الحي الشرقي",
        "حي الجامعه",
        "الصريح",
        "بشرى",
        "حكما",
        "جنوب اربد",
        "البارحه",
        "مفروش",
        "غير مفروش",
        "شهري",
        "سنوي",
        "قابل للتفاوض",
        "للتواصل",
        "واتساب",
        "اول ساكن",
        "بناء جديد",
    )
    return [term for term in tracked_terms if term in text]


def _contains_any(text: str, candidates: tuple[str, ...]) -> bool:
    normalized_candidates = (normalize_arabic_text(candidate) for candidate in candidates)
    return any(candidate in text for candidate in normalized_candidates)
