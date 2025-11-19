"""Generate LLM prompts with embedded schemas for structured output."""

from typing import Literal

from .api import to_schema
from .generator import to_yaml

TagStrategy = Literal["xml", "none"]
FenceStrategy = Literal["fenced", "none"]
FormatLabel = Literal["json", "xml", "csv", "yaml"]


def to_prompt(
    schema,
    *,
    instruction: str = "Generate valid structured data matching this:",
    tag: TagStrategy = "xml",
    tag_name: str = "output",
    fence: FenceStrategy = "fenced",
    format_label: FormatLabel = "json",
) -> str:
    """Generate an LLM prompt with embedded schema for structured output.

    Args:
        schema: Schema in any supported format (YAML string, Pydantic, msgspec, Schema IR)
        instruction: Custom instruction text for the LLM
        tag: Tagging strategy - "xml" for XML tags, "none" for no tags
        tag_name: Name of the XML tag (default: "output")
        fence: Fencing strategy - "fenced" for code fences, "none" for no fences
        format_label: Format label for code fence (default: "json")

    Returns:
        Complete LLM prompt string

    Examples:
        >>> # Default: <output>```json...```</output>
        >>> to_prompt(schema)

        >>> # No tags, fence only: ```json...```
        >>> to_prompt(schema, tag="none")

        >>> # Tag only, no fence: <json>...</json>
        >>> to_prompt(schema, fence="none", tag_name="json")

        >>> # Neither: just the instruction
        >>> to_prompt(schema, tag="none", fence="none")
    """
    # Convert schema to YAML format
    schema_ir = to_schema(schema)
    schema_str = to_yaml(schema_ir).strip()

    # Build prompt parts
    parts = []

    # Add instruction
    if instruction:
        parts.append(instruction)

    # Add schema (always in slimschema fence, never wrapped in tags)
    parts.append("```slimschema")
    parts.append(schema_str)
    parts.append("```")

    # Add output instruction
    parts.append("")
    parts.append("Wrap your response in:")
    if tag == "xml" and fence == "fenced":
        parts.append(f"<{tag_name}>")
        parts.append(f"```{format_label}")
        parts.append("```")
        parts.append(f"</{tag_name}>")
    elif tag == "xml" and fence == "none":
        parts.append(f"<{tag_name}>")
        parts.append("```")
        parts.append(f"</{tag_name}>")
    elif tag == "none" and fence == "fenced":
        parts.append(f"```{format_label}")
        parts.append("```")

    return "\n".join(parts)


def to_prompt_compact(
    schema,
    *,
    tag_name: str = "output",
    format_label: FormatLabel = "json",
) -> str:
    """Generate a compact LLM prompt (no instruction text, just schema).

    Uses the most robust tagging strategy: <output>```json...```</output>

    Args:
        schema: Schema in any supported format
        tag_name: Name of the XML tag (default: "output")
        format_label: Format label for code fence (default: "json")

    Returns:
        Compact prompt string

    Example:
        >>> to_prompt_compact(schema)
        '<output>```json\\nname: str\\n...\\n```</output>'
    """
    schema_ir = to_schema(schema)
    schema_str = to_yaml(schema_ir).strip()

    return f"<{tag_name}>```{format_label}\n{schema_str}\n```</{tag_name}>"
