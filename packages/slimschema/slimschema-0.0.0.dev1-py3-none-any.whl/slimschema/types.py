"""Type conversion - consolidated with single compiled regex.

Converts between:
- Pydantic annotations → SlimSchema type strings
- SlimSchema type strings → msgspec types (ONE regex match)
"""

import re
from typing import Annotated, get_args, get_origin

import msgspec

# Single compiled regex with named groups (checked in priority order)
TYPE_PATTERN = re.compile(
    r"(?P<str_len>str\{(?P<str_min>\d+)\.\.(?P<str_max>\d+)\})"
    r"|(?P<num_range>(?P<num_min>\d+\.?\d*)\.\.(?P<num_max>\d+\.?\d*))"
    r"|(?P<regex>/(?P<pattern>[^/]+)/)"
    r"|(?P<enum>(?P<enum_values>.+\|.+))"
    r"|(?P<array>\[(?P<array_inner>.+)\])"
    r"|(?P<set>\{(?P<set_inner>[^:]+)\})"
    r"|(?P<format>email|url|date|datetime|uuid)"
    r"|(?P<primitive>str|int|float|bool|obj)"
)

FORMAT_PATTERNS = {
    "email": r"^[^@]+@[^@]+\.[^@]+$",
    "url": r"^https?://",
    "date": r"^\d{4}-\d{2}-\d{2}$",
    "datetime": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
    "uuid": r"^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$",
}

PRIMITIVE_TYPES = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "obj": dict,
}


def to_msgspec_type(type_expr: str):
    """Convert SlimSchema type string to msgspec type (single regex match)."""
    match = TYPE_PATTERN.fullmatch(type_expr.strip())

    if not match:
        return str  # Default fallback

    # String length
    if match.group("str_len"):
        min_len = int(match.group("str_min"))
        max_len = int(match.group("str_max"))
        return Annotated[str, msgspec.Meta(min_length=min_len, max_length=max_len)]

    # Numeric range
    if match.group("num_range"):
        min_val = match.group("num_min")
        max_val = match.group("num_max")
        is_float = "." in min_val or "." in max_val
        if is_float:
            return Annotated[float, msgspec.Meta(ge=float(min_val), le=float(max_val))]
        return Annotated[int, msgspec.Meta(ge=int(min_val), le=int(max_val))]

    # Regex pattern
    if match.group("regex"):
        pattern = match.group("pattern")
        return Annotated[str, msgspec.Meta(pattern=pattern)]

    # Format types
    if match.group("format"):
        fmt = match.group("format")
        return Annotated[str, msgspec.Meta(pattern=FORMAT_PATTERNS[fmt])]

    # Enum
    if match.group("enum"):
        from typing import Literal

        values = tuple(v.strip() for v in match.group("enum_values").split("|"))
        return Literal[values]  # type: ignore

    # Array
    if match.group("array"):
        inner = to_msgspec_type(match.group("array_inner"))
        return list[inner]  # type: ignore

    # Set
    if match.group("set"):
        inner = match.group("set_inner")
        if ":" in inner:
            return dict  # Inline object
        return list[to_msgspec_type(inner)]  # type: ignore

    # Primitive
    if match.group("primitive"):
        return PRIMITIVE_TYPES[match.group("primitive")]

    return str


def from_pydantic_field(field_info) -> str:
    """Convert Pydantic field to SlimSchema type string."""
    annotation = field_info.annotation

    # Check for constraints in metadata
    min_length = max_length = None
    ge = le = None

    if hasattr(field_info, "metadata"):
        for constraint in field_info.metadata:
            # String length constraints
            if hasattr(constraint, "min_length"):
                min_length = constraint.min_length
            if hasattr(constraint, "max_length"):
                max_length = constraint.max_length
            # Numeric constraints
            if hasattr(constraint, "ge"):
                ge = constraint.ge
            if hasattr(constraint, "le"):
                le = constraint.le

    # Return constraint types
    if min_length and max_length:
        return f"str{{{min_length}..{max_length}}}"
    if ge is not None and le is not None:
        return f"{ge}..{le}"

    # Basic types
    for name, typ in PRIMITIVE_TYPES.items():
        if annotation == typ:
            return name

    # Containers
    origin = get_origin(annotation)
    if origin is list:
        args = get_args(annotation)
        if args:
            inner = from_pydantic_field(type("_", (), {"annotation": args[0], "metadata": []})())
            return f"[{inner}]"
        return "[]"

    if origin is set:
        args = get_args(annotation)
        if args:
            inner = from_pydantic_field(type("_", (), {"annotation": args[0], "metadata": []})())
            return f"{{{inner}}}"
        return "{}"

    return "str"
