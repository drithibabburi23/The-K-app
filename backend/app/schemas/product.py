from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ProductBase(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = None
    material: str | None = Field(default=None, max_length=120)
    craft_type: str | None = Field(default=None, max_length=120)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    image_url: HttpUrl | None = None
    language: str = Field(default="en", min_length=2, max_length=20)
    status: str = Field(default="draft", min_length=1, max_length=30)
    artisan_id: int = Field(gt=0)
    category_id: int = Field(gt=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    material: str | None = Field(default=None, max_length=120)
    craft_type: str | None = Field(default=None, max_length=120)
    price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    image_url: HttpUrl | None = None
    language: str | None = Field(default=None, min_length=2, max_length=20)
    status: str | None = Field(default=None, min_length=1, max_length=30)
    artisan_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
