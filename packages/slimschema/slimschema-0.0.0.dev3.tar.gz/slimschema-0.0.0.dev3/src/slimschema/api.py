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
    """Extract and validate LLM response, return (data, error).

    Validation strategy:
    - Pydantic model: Use Pydantic's model_validate() directly (preserves custom validators)
    - msgspec Struct: Use msgspec.convert() directly (fast native validation)
    - YAML/string: Try msgspec first (faster), fallback to Pydantic if available
    """
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

    # Pydantic model - use Pydantic validation directly (preserves custom validators)
    if isinstance(schema_obj, type) and hasattr(schema_obj, "model_fields"):
        try:
            instance = schema_obj.model_validate(json_data)
            return instance, None
        except Exception as e:
            # Format Pydantic validation errors to be concise
            return None, str(e)

    # YAML string or Schema - try msgspec first, fallback to Pydantic
    schema = to_schema(schema_obj)

    # Try msgspec validation (faster)
    try:
        import msgspec
        result = validate_response(response, schema)

        if not result.valid:
            return None, format_slim_error(result.errors)

        return result.data, None
    except ImportError:
        # msgspec not available - this should be rare since it's a core dependency
        # but handle gracefully for edge cases
        return None, "msgspec is required for validation"


def to_pydantic(schema_input: Any) -> type:
    """Convert any schema format to a Pydantic BaseModel class.

    Args:
        schema_input: YAML string, Schema IR, Pydantic model, or msgspec Struct

    Returns:
        Pydantic BaseModel class (not an instance)

    Examples:
        >>> yaml = "# User\\nname: str\\nage: 18..120"
        >>> UserModel = to_pydantic(yaml)
        >>> user = UserModel(name="Alice", age=30)
        >>> user.name
        'Alice'
    """
    from pydantic import create_model

    from .types import to_msgspec_type

    # If already Pydantic, return as-is
    if isinstance(schema_input, type) and hasattr(schema_input, "model_fields"):
        return schema_input

    # Convert to Schema IR
    schema = to_schema(schema_input)

    # Build Pydantic field definitions
    fields = {}
    for field in schema.fields:
        py_type = to_msgspec_type(field.type, field.annotation)

        # Handle optional fields
        if field.optional:
            fields[field.name] = (py_type | None, None)
        else:
            fields[field.name] = (py_type, ...)

    # Create Pydantic model with schema name
    model_name = schema.name or "DynamicModel"
    return create_model(model_name, **fields)


def to_msgspec(schema_input: Any) -> type:
    """Convert any schema format to a msgspec Struct class.

    Args:
        schema_input: YAML string, Schema IR, Pydantic model, or msgspec Struct

    Returns:
        msgspec Struct class (not an instance)

    Examples:
        >>> yaml = "# User\\nname: str\\nage: 18..120"
        >>> UserStruct = to_msgspec(yaml)
        >>> user = msgspec.convert({"name": "Alice", "age": 30}, type=UserStruct)
        >>> user.name
        'Alice'
    """
    import msgspec

    from .types import to_msgspec_type

    # If already msgspec, return as-is
    if isinstance(schema_input, type) and hasattr(schema_input, "__struct_fields__"):
        return schema_input

    # Convert to Schema IR
    schema = to_schema(schema_input)

    # Build msgspec field annotations and defaults
    annotations = {}
    defaults = {}

    for field in schema.fields:
        field_type = to_msgspec_type(field.type, field.annotation)

        if field.optional:
            annotations[field.name] = field_type | None
            defaults[field.name] = None
        else:
            annotations[field.name] = field_type

    # Create msgspec Struct with schema name
    struct_name = schema.name or "DynamicStruct"
    return msgspec.defstruct(
        struct_name,
        [(name, annotations[name], defaults.get(name, msgspec.NODEFAULT))
         for name in annotations]
    )
