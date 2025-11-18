"""Parser for SlimSchema YAML format.

Converts SlimSchema YAML to IR using functional approach.
"""

from io import StringIO
from typing import Any

from ruamel.yaml import YAML

from .core import Field, Schema


def parse_slimschema(yaml_str: str) -> Schema:
    """Parse SlimSchema YAML to IR.

    Args:
        yaml_str: YAML string in SlimSchema format

    Returns:
        Schema IR

    Examples:
        >>> schema = parse_slimschema('''
        ... # Person
        ... name: str
        ... age: 18..120
        ... email?: email  # Contact email
        ... ''')
        >>> schema.name
        'Person'
        >>> len(schema.fields)
        3
    """
    # Extract schema name from top comment
    name = _extract_name(yaml_str)

    # Extract field comments
    comments = _extract_comments(yaml_str)

    # Parse YAML structure
    yaml = YAML()
    yaml.preserve_quotes = True

    data = yaml.load(StringIO(yaml_str))

    if data is None:
        return Schema(fields=[], name=name)

    # Parse object fields
    fields = []
    for field_name, field_value in data.items():
        field = _parse_field(
            field_name, field_value, comments.get(field_name.rstrip("?"))
        )
        fields.append(field)

    return Schema(fields=fields, name=name)


def _parse_field(name: str, value: Any, comment: str | None) -> Field:
    """Parse a single field.

    Args:
        name: Field name (may end with ?)
        value: Field value from YAML
        comment: Optional inline comment

    Returns:
        Field IR
    """
    optional = name.endswith("?")
    clean_name = name.rstrip("?")

    type_expr = _parse_type(value)
    description, annotation = _split_comment(comment)

    return Field(
        name=clean_name,
        type=type_expr,
        optional=optional,
        description=description,
        annotation=annotation,
    )


def _split_comment(comment: str | None) -> tuple[str | None, str | None]:
    """Split comment into description and optional type annotation."""
    if not comment:
        return None, None

    if "::" not in comment:
        return comment.strip() or None, None

    text, _, annotation = comment.partition("::")
    description = text.strip() or None
    clean_annotation = annotation.strip() or None
    return description, clean_annotation


def _parse_type(value: Any) -> str:
    """Parse type expression from YAML value.

    Args:
        value: YAML value (string, list, dict, etc.)

    Returns:
        Type expression as string
    """
    if isinstance(value, str):
        return value.strip()

    if isinstance(value, list):
        if len(value) == 0:
            return "[]"
        item_type = _parse_type(value[0])
        return f"[{item_type}]"

    if isinstance(value, dict):
        # Check for set syntax: {type} parsed as dict with single key and None value
        if len(value) == 1:
            key, val = next(iter(value.items()))
            if val is None:
                return f"{{{key}}}"
        # Nested object type
        return _parse_object_type(value)

    return "obj"


def _parse_object_type(value: dict) -> str:
    """Parse nested object type to inline syntax.

    Args:
        value: Dictionary representing object fields

    Returns:
        Inline object type like '{name:str,age:int}'
    """
    parts = []
    for field_name, field_value in value.items():
        field_type = _parse_type(field_value)
        optional_marker = "?" if field_name.endswith("?") else ""
        clean_name = field_name.rstrip("?")
        parts.append(f"{clean_name}{optional_marker}:{field_type}")

    return "{" + ",".join(parts) + "}"


def _extract_name(yaml_str: str) -> str | None:
    """Extract schema name from first line comment."""
    for line in yaml_str.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            name = stripped[1:].strip()
            if name:
                return name.split()[0]  # First word only
            return None
        if stripped:
            break
    return None


def _extract_comments(yaml_str: str) -> dict[str, str]:
    """Extract inline comments for fields.

    Args:
        yaml_str: YAML string

    Returns:
        Dictionary mapping field names to comments

    Examples:
        >>> _extract_comments("name: str  # Full name\\nage: int")
        {'name': 'Full name'}
    """
    comments = {}

    for line in yaml_str.split("\n"):
        if "#" not in line:
            continue

        parts = line.split("#", 1)
        if len(parts) != 2:
            continue

        key_part = parts[0].strip()
        comment = parts[1].strip()

        if ":" not in key_part:
            continue

        field = key_part.split(":")[0].strip().rstrip("?")
        if field and comment:
            comments[field] = comment

    return comments


