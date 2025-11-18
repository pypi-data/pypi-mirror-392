"""Type conversion - consolidated with single compiled regex.

Converts between:
- Pydantic annotations → SlimSchema type strings
- SlimSchema type strings → msgspec types (ONE regex match)
"""

import re
from typing import Annotated, Any, get_args, get_origin

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


def to_msgspec_type(type_expr: str, annotation: str | None = None):
    """Convert SlimSchema type string to msgspec type (single regex match)."""
    annotated_type = _annotation_to_msgspec(annotation)
    if annotated_type is not None:
        return annotated_type

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

    # Set (legacy syntax)
    if match.group("set"):
        inner = match.group("set_inner")
        if ":" in inner:
            return dict  # Inline object
        return set[to_msgspec_type(inner)]  # type: ignore

    # Primitive
    if match.group("primitive"):
        return PRIMITIVE_TYPES[match.group("primitive")]

    return str


def from_pydantic_field(field_info) -> tuple[str, str | None]:
    """Convert Pydantic field to SlimSchema type string and annotation."""
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
        return f"str{{{min_length}..{max_length}}}", None
    if ge is not None and le is not None:
        return f"{ge}..{le}", None

    # Basic types
    for name, typ in PRIMITIVE_TYPES.items():
        if annotation == typ:
            return name, None

    origin = get_origin(annotation)
    if origin:
        return _from_container_annotation(origin, annotation)

    return "str", None


def _annotation_to_msgspec(annotation: str | None):
    """Convert optional :: annotation to msgspec type."""
    if not annotation:
        return None

    match = re.fullmatch(r"(Set|FrozenSet|Tuple)\[(.*)\]", annotation.strip())
    if not match:
        return None

    kind, inner = match.group(1), match.group(2)
    parts = _split_annotation_items(inner)

    if kind == "Set":
        if len(parts) != 1:
            return None
        inner_type = to_msgspec_type(parts[0])
        return set[inner_type]  # type: ignore

    if kind == "FrozenSet":
        if len(parts) != 1:
            return None
        inner_type = to_msgspec_type(parts[0])
        return frozenset[inner_type]  # type: ignore

    # Tuple
    if len(parts) == 2 and parts[1].strip() == "...":
        inner_type = to_msgspec_type(parts[0])
        return tuple[(inner_type, ...)]  # type: ignore

    inner_types = tuple(to_msgspec_type(part) for part in parts)
    return tuple[inner_types]  # type: ignore


def _from_container_annotation(origin, annotation) -> tuple[str, str | None]:
    """Convert container annotations to base type and :: annotation."""
    args = get_args(annotation)

    if origin is list:
        inner = args[0] if args else Any
        inner_type, _ = from_pydantic_field(type("_", (), {"annotation": inner, "metadata": []})())
        return f"[{inner_type}]", None

    if origin is set:
        inner = args[0] if args else Any
        inner_type, inner_ann = from_pydantic_field(type("_", (), {"annotation": inner, "metadata": []})())
        ann = f"Set[{inner_ann or inner_type}]"
        return f"[{inner_type}]", ann

    if origin is frozenset:
        inner = args[0] if args else Any
        inner_type, inner_ann = from_pydantic_field(type("_", (), {"annotation": inner, "metadata": []})())
        ann = f"FrozenSet[{inner_ann or inner_type}]"
        return f"[{inner_type}]", ann

    if origin is tuple:
        if not args:
            return "[]", "Tuple[]"

        if len(args) == 2 and args[1] is Ellipsis:
            inner = args[0]
            inner_type, inner_ann = from_pydantic_field(
                type("_", (), {"annotation": inner, "metadata": []})()
            )
            ann_inner = inner_ann or inner_type
            return f"[{inner_type}]", f"Tuple[{ann_inner}, ...]"

        tuple_items = []
        tuple_ann = []
        for item in args:
            item_type, item_ann = from_pydantic_field(
                type("_", (), {"annotation": item, "metadata": []})()
            )
            tuple_items.append(item_type)
            tuple_ann.append(item_ann or item_type)

        return f"[{tuple_items[0]}]", f"Tuple[{', '.join(tuple_ann)}]"

    return "str", None


def _split_annotation_items(annotation: str) -> list[str]:
    """Split annotation contents by commas while respecting nesting."""
    items: list[str] = []
    buf = []
    depth = 0

    for char in annotation:
        if char == "," and depth == 0:
            items.append("".join(buf).strip())
            buf = []
            continue

        if char in "[({":
            depth += 1
        elif char in "])}" and depth > 0:
            depth -= 1

        buf.append(char)

    if buf:
        items.append("".join(buf).strip())

    return [item for item in items if item]
