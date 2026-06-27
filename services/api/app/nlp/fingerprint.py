import hashlib

from app.nlp.dialect_parser import normalize_arabic_text


def listing_text_fingerprint(text: str) -> str:
    normalized = normalize_arabic_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
