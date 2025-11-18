"""Pydantic adapter - convert Pydantic models to Schema IR."""

from ..core import Field, Schema
from ..types import from_pydantic_field


def from_pydantic(model):
    """Convert Pydantic model to Schema IR."""
    from pydantic import BaseModel

    if not issubclass(model, BaseModel):
        raise TypeError(f"Expected Pydantic model, got {type(model)}")

    fields = [
        Field(
            name=name,
            type=from_pydantic_field(field_info),
            optional=not field_info.is_required(),
            description=field_info.description,
        )
        for name, field_info in model.model_fields.items()
    ]

    return Schema(fields=fields, name=model.__name__)
