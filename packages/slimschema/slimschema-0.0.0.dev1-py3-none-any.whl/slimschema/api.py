"""Public API for SlimSchema."""

from typing import Any

from .core import Schema
from .extract import validate_response
from .parser import parse_slimschema
from .utils import format_slim_error


def to_schema(obj: Any) -> Schema:
    """Convert any format to SlimSchema IR."""
    if isinstance(obj, Schema):
        return obj

    if isinstance(obj, str):
        return parse_slimschema(obj)

    if isinstance(obj, type) and hasattr(obj, "model_fields"):
        from .adapters.pydantic import from_pydantic
        return from_pydantic(obj)

    raise TypeError(f"Cannot convert {type(obj).__name__} to Schema")


def to_data(response: str, schema_obj: Any) -> tuple[Any, str | None]:
    """Extract and validate LLM response, return (data, error)."""
    # Check if Pydantic model
    pydantic_model = None
    if isinstance(schema_obj, type) and hasattr(schema_obj, "model_fields"):
        pydantic_model = schema_obj

    # Convert to Schema IR
    schema = to_schema(schema_obj)

    # Extract and validate
    result = validate_response(response, schema)

    if not result.valid:
        return None, format_slim_error(result.errors)

    # Convert to Pydantic if needed, otherwise return dict
    if pydantic_model:
        return pydantic_model(**result.data), None

    return result.data, None
