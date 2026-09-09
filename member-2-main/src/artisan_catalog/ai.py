from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Protocol

from .models import CatalogTranslations, ProductFacts


class AIProvider(Protocol):
    async def extract(self, source_text: str) -> ProductFacts: ...
    async def describe(self, source_text: str, facts: ProductFacts, regional_language: str | None = None) -> CatalogTranslations: ...


@dataclass
class LocalAIProvider:
    """Offline fallback used for development and tests.

    It deliberately leaves unknown fields empty instead of guessing.
    """

    async def extract(self, source_text: str) -> ProductFacts:
        text = " ".join(source_text.split())
        patterns = {
            "material": r"\b(cotton|silk|wool|linen|jute|clay|wood|bamboo|leather)\b",
            "color": r"\b(red|blue|green|yellow|black|white|pink|purple|orange|brown|maroon)\b",
            "craft": r"\b(handwoven|hand[- ]?made|embroidered|block[- ]?printed|pottery|carved|woven)\b",
        }
        values: dict[str, str | None] = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            values[field] = match.group(1) if match else None
        name_match = re.search(r"(?:called|named) ([^.!,]+)", text, re.IGNORECASE)
        values["product_name"] = name_match.group(1).strip() if name_match else None
        values["category"] = self._category(text)
        return ProductFacts(**values)

    async def describe(self, source_text: str, facts: ProductFacts, regional_language: str | None = None) -> CatalogTranslations:
        known = [value for value in facts.model_dump().values() if value]
        subject = facts.product_name or facts.category or "Handcrafted product"
        details = ", ".join(known[1:] if facts.product_name else known)
        description = f"{subject} made by an artisan."
        if details:
            description += f" Details shared by the artisan: {details}."
        return CatalogTranslations(en=description, hi=description, regional=None)

    @staticmethod
    def _category(text: str) -> str | None:
        categories = {
            "saree": "Textiles",
            "textile": "Textiles",
            "shirt": "Textiles",
            "pottery": "Home decor",
            "basket": "Home decor",
            "jewellery": "Jewellery",
            "jewelry": "Jewellery",
        }
        for word, category in categories.items():
            if word in text.lower():
                return category
        return None


class OpenAIProvider:
    """OpenAI-compatible provider; imported only when an API key is configured."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def extract(self, source_text: str) -> ProductFacts:
        response = await self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Extract only facts explicitly stated by the artisan. Use null when absent. Return JSON matching product_name, category, material, craft, color, dimensions, price, description."},
                {"role": "user", "content": source_text},
            ],
        )
        return ProductFacts.model_validate(json.loads(response.choices[0].message.content or "{}"))

    async def describe(self, source_text: str, facts: ProductFacts, regional_language: str | None = None) -> CatalogTranslations:
        response = await self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Write concise product descriptions in English, Hindi, and the requested regional language. Never add facts not present in the source. Return JSON with en, hi, regional."},
                {"role": "user", "content": json.dumps({"source_text": source_text, "facts": facts.model_dump(), "regional_language": regional_language}, ensure_ascii=False)},
            ],
        )
        return CatalogTranslations.model_validate(json.loads(response.choices[0].message.content or "{}"))


def build_provider() -> AIProvider:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            return OpenAIProvider(api_key, os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
        except ImportError:
            pass
    return LocalAIProvider()
