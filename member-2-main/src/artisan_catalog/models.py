from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


Language = Literal["en", "hi", "regional"]


class ProductFacts(BaseModel):
    product_name: str | None = None
    category: str | None = None
    material: str | None = None
    craft: str | None = None
    color: str | None = None
    dimensions: str | None = None
    price: str | None = None
    description: str | None = None

    @field_validator("product_name", "category", "material", "craft", "color", "dimensions", "price", "description")
    @classmethod
    def trim_values(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = " ".join(value.split())
        return value or None


class ValidatedProduct(BaseModel):
    facts: ProductFacts
    supported_fields: list[str] = Field(default_factory=list)
    omitted_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class CatalogTranslations(BaseModel):
    en: str
    hi: str
    regional: str | None = None


class CatalogResult(BaseModel):
    source_text: str
    facts: ValidatedProduct
    descriptions: CatalogTranslations
    backend_payload: dict
    warnings: list[str] = Field(default_factory=list)


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)
    regional_language: str | None = Field(default=None, max_length=40)


class PipelineRequest(TextRequest):
    callback_url: str | None = None
