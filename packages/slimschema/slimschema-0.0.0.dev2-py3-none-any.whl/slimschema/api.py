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

    if isinstance(obj, type):
        # Pydantic model
        if hasattr(obj, "model_fields"):
            from .adapters.pydantic import from_pydantic
            return from_pydantic(obj)

        # msgspec Struct
        if hasattr(obj, "__struct_fields__"):
            from .adapters.msgspec_adapter import from_msgspec
            return from_msgspec(obj)

    raise TypeError(f"Cannot convert {type(obj).__name__} to Schema")


def to_data(response: str, schema_obj: Any) -> tuple[Any, str | None]:
    """Extract and validate LLM response, return (data, error)."""
    from .extract import extract_json

    # Extract JSON first
    json_data = extract_json(response)
    if json_data is None:
        return None, "No valid JSON found in response"

    # msgspec Struct - use msgspec directly
    if isinstance(schema_obj, type) and hasattr(schema_obj, "__struct_fields__"):
        try:
            import msgspec

            instance = msgspec.convert(json_data, type=schema_obj)
            return instance, None
        except (msgspec.ValidationError, TypeError, ValueError) as e:
            return None, str(e)

    # Pydantic model - convert through Schema, return instance
    if isinstance(schema_obj, type) and hasattr(schema_obj, "model_fields"):
        schema = to_schema(schema_obj)
        result = validate_response(response, schema)

        if not result.valid:
            return None, format_slim_error(result.errors)

        return schema_obj(**result.data), None

    # YAML string or Schema - validate and return dict
    schema = to_schema(schema_obj)
    result = validate_response(response, schema)

    if not result.valid:
        return None, format_slim_error(result.errors)

    return result.data, None
