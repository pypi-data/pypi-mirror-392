"""Validation using msgspec."""

import msgspec

from .core import Schema, ValidationResult
from .types import to_msgspec_type


def validate(data: dict | list, schema: Schema) -> ValidationResult:
    """Validate data against schema using msgspec."""
    # Build msgspec Struct dynamically
    annotations = {}
    defaults = {}

    for field in schema.fields:
        field_type = to_msgspec_type(field.type)

        if field.optional:
            annotations[field.name] = field_type | None
            defaults[field.name] = None
        else:
            annotations[field.name] = field_type

    # Create Struct
    struct_name = schema.name or "DynamicStruct"

    if defaults:
        struct_type = msgspec.defstruct(
            struct_name,
            [(name, annotations[name], defaults.get(name, msgspec.NODEFAULT)) for name in annotations],
        )
    else:
        struct_type = msgspec.defstruct(
            struct_name,
            [(name, annotations[name]) for name in annotations],
        )

    # Validate with msgspec
    try:
        validated = msgspec.convert(data, type=struct_type)
        validated_dict = msgspec.structs.asdict(validated)
        return ValidationResult(valid=True, data=validated_dict, errors=[], schema=schema)
    except (msgspec.ValidationError, TypeError, ValueError) as e:
        return ValidationResult(valid=False, data=None, errors=[str(e)], schema=schema)
