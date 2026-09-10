from collections.abc import Mapping
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session


ModelType = TypeVar("ModelType")


def get_or_404(db: Session, model: type[ModelType], item_id: int) -> ModelType:
    item = db.get(model, item_id)
    if item is None:
        raise ValueError(f"{model.__name__} with id {item_id} was not found")
    return item


def create_item(db: Session, model: type[ModelType], data: Mapping[str, Any]) -> ModelType:
    item = model(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_items(db: Session, model: type[ModelType]) -> list[ModelType]:
    return list(db.scalars(select(model)).all())


def update_item(db: Session, item: ModelType, data: Mapping[str, Any]) -> ModelType:
    for field, value in data.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item: ModelType) -> None:
    db.delete(item)
    db.commit()
