from __future__ import annotations

import re
from dataclasses import dataclass

from .models import ProductFacts, ValidatedProduct


FIELDS = tuple(ProductFacts.model_fields)


@dataclass
class ValidationResult:
    product: ValidatedProduct


def validate_facts(source_text: str, candidate: ProductFacts) -> ValidationResult:
    """Keep only values traceable to the spoken text.

    Exact phrase matching is intentionally conservative: uncertain facts become null
    and are surfaced in warnings instead of reaching the catalog.
    """
    normalized_source = _normalize(source_text)
    accepted: dict[str, str | None] = {}
    warnings: list[str] = []
    supported: list[str] = []
    omitted: list[str] = []

    for field in FIELDS:
        value = getattr(candidate, field)
        if value is None:
            accepted[field] = None
            omitted.append(field)
            continue
        if field == "description":
            accepted[field] = value if _has_supported_words(value, normalized_source) else None
        elif _normalize(value) in normalized_source:
            accepted[field] = value
        else:
            accepted[field] = None
        if accepted[field] is None:
            omitted.append(field)
            warnings.append(f"Omitted unsupported AI value for {field}.")
        else:
            supported.append(field)

    return ValidationResult(ValidatedProduct(
        facts=ProductFacts(**accepted),
        supported_fields=supported,
        omitted_fields=omitted,
        warnings=warnings,
    ))


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", value.lower())).strip()


def _has_supported_words(value: str, source: str) -> bool:
    words = [word for word in _normalize(value).split() if len(word) > 3]
    return bool(words) and all(word in source for word in words)
