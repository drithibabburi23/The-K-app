from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from .ai import AIProvider
from .models import CatalogResult, CatalogTranslations, ProductFacts
from .validation import validate_facts


@dataclass
class CatalogPipeline:
    provider: AIProvider

    async def run(self, source_text: str, regional_language: str | None = None) -> CatalogResult:
        candidate = await self.provider.extract(source_text)
        validated = validate_facts(source_text, candidate).product
        descriptions = await self.provider.describe(source_text, validated.facts, regional_language)
        descriptions = _apply_regional_label(descriptions, regional_language)
        warnings = list(validated.warnings)
        payload = {
            "source_text": source_text,
            "product": validated.facts.model_dump(),
            "descriptions": descriptions.model_dump(),
            "validation": {
                "supported_fields": validated.supported_fields,
                "omitted_fields": validated.omitted_fields,
                "warnings": warnings,
            },
        }
        return CatalogResult(
            source_text=source_text,
            facts=validated,
            descriptions=descriptions,
            backend_payload=payload,
            warnings=warnings,
        )

    async def send_to_backend(self, callback_url: str, result: CatalogResult) -> None:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(callback_url, json=result.backend_payload)
            response.raise_for_status()


def _apply_regional_label(descriptions: CatalogTranslations, language: str | None) -> CatalogTranslations:
    # The provider can return a regional translation; absent one remains explicit null.
    return descriptions
