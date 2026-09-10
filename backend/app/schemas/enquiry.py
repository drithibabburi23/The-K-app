from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EnquiryBase(BaseModel):
    message: str = Field(min_length=1)
    status: str = Field(default="open", min_length=1, max_length=30)
    product_id: int = Field(gt=0)
    buyer_id: int = Field(gt=0)


class EnquiryCreate(EnquiryBase):
    pass


class EnquiryUpdate(BaseModel):
    message: str | None = Field(default=None, min_length=1)
    status: str | None = Field(default=None, min_length=1, max_length=30)


class EnquiryRead(EnquiryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
