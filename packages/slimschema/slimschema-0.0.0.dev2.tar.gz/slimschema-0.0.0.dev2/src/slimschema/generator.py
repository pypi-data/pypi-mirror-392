"""Generator for SlimSchema YAML format.

Converts IR to SlimSchema YAML using functional approach.
"""

from .core import Schema


def to_yaml(schema: Schema) -> str:
    """Generate SlimSchema YAML from IR.

    Args:
        schema: Schema IR

    Returns:
        SlimSchema YAML string

    Examples:
        >>> from slimschema import Schema, Field
        >>> schema = Schema(fields=[
        ...     Field(name="name", type="str", description="Full name"),
        ...     Field(name="age", type="18..120"),
        ...     Field(name="email", type="email", optional=True),
        ... ], name="Person")
        >>> print(to_yaml(schema))
        # Person
        name: str  # Full name
        age: 18..120
        email?: email
    """
    lines = []

    # Add schema name as top comment
    if schema.name:
        lines.append(f"# {schema.name}")

    # Generate fields
    for field in schema.fields:
        name = field.name + ("?" if field.optional else "")

        comment_parts = []

        if field.description:
            comment_parts.append(field.description)
        if field.annotation:
            comment_parts.append(f":: {field.annotation}")

        if comment_parts:
            comment = "  ".join(comment_parts)
            lines.append(f"{name}: {field.type}  # {comment}")
        else:
            lines.append(f"{name}: {field.type}")

    return "\n".join(lines)
