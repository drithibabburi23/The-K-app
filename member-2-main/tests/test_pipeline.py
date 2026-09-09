import pytest

from artisan_catalog.ai import LocalAIProvider
from artisan_catalog.pipeline import CatalogPipeline


@pytest.mark.asyncio
async def test_pipeline_keeps_only_facts_present_in_source():
    result = await CatalogPipeline(LocalAIProvider()).run(
        "This is a handmade cotton saree in blue."
    )

    assert result.facts.facts.material == "cotton"
    assert result.facts.facts.craft == "handmade"
    assert result.facts.facts.color == "blue"
    assert result.facts.facts.price is None
    assert "price" in result.facts.omitted_fields
    assert result.backend_payload["product"]["material"] == "cotton"


@pytest.mark.asyncio
async def test_unknown_product_does_not_get_invented_details():
    result = await CatalogPipeline(LocalAIProvider()).run("It is made with care.")

    assert result.facts.facts.model_dump(exclude_none=True) == {}
    assert result.facts.omitted_fields == [
        "product_name", "category", "material", "craft", "color",
        "dimensions", "price", "description",
    ]
