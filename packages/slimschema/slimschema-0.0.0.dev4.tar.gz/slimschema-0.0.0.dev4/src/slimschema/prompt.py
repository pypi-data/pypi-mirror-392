"""Generate LLM prompts with embedded schemas for structured output."""

from .api import to_schema
from .generator import to_yaml


def to_prompt(
    schema,
    *,
    errors: str | None = None,
    xml_tag: str | None = "output",
    fence_language: str | None = "json",
    show_defaults: bool = False,
) -> str:
    """Generate an LLM prompt with schema for structured output.

    Args:
        schema: Your schema (YAML string, Pydantic model, msgspec Struct, or Schema object)
        errors: Optional error message from previous validation attempt
        xml_tag: XML tag name (default: "output"). Set to None to skip XML wrapper.
        fence_language: Fence language (default: "json"). Set to None to skip fence wrapper.
        show_defaults: Whether to show default values in schema (default: False)

    Returns:
        Complete prompt string ready for LLM

    Examples:
        >>> # Default: <output>```json...```</output> (most robust)
        >>> prompt = to_prompt("name: str\\nage: 18..120")
        >>> print(prompt)
        Follow this schema:
        ```slimschema
        name: str
        age: 18..120
        ```
        <BLANKLINE>
        To generate `JSON`:
        <output>```json
        ```</output>

        >>> # With validation errors for retry
        >>> prompt = to_prompt(schema, errors="Missing required fields: age")
        >>> # Errors shown first

        >>> # Just code fence, no XML tags
        >>> to_prompt(schema, xml_tag=None)

        >>> # Just XML tags, no code fence
        >>> to_prompt(schema, fence_language=None, xml_tag="data")

        >>> # CSV format with custom tag
        >>> to_prompt(schema, xml_tag="data", fence_language="csv")

        >>> # Show defaults (not recommended for LLM prompts)
        >>> to_prompt("age: int = 0", show_defaults=True)
    """
    # Validate at least one wrapper is provided
    if xml_tag is None and fence_language is None:
        raise ValueError("Must provide at least one of xml_tag or fence_language")

    # Convert schema to YAML format
    schema_ir = to_schema(schema)
    schema_str = to_yaml(schema_ir, show_defaults=show_defaults).strip()

    # Build prompt parts
    parts = []

    # Add errors if present (first!)
    if errors:
        parts.append("Errors found, please correct the output below:")
        parts.append(errors)
        parts.append("")

    # Add schema instruction and schema
    parts.append("Follow this schema:")
    parts.append("```slimschema")
    parts.append(schema_str)
    parts.append("```")
    parts.append("")

    # Add output format instruction
    format_name = fence_language.upper() if fence_language else "OUTPUT"
    parts.append(f"To generate `{format_name}`:")

    # Build the output wrapper
    if xml_tag and fence_language:
        # Both: <output>```json...```</output>
        parts.append(f"<{xml_tag}>```{fence_language}")
        parts.append(f"```</{xml_tag}>")
    elif xml_tag:
        # Just XML: <output>...</output>
        parts.append(f"<{xml_tag}>")
        parts.append(f"</{xml_tag}>")
    elif fence_language:
        # Just fence: ```json...```
        parts.append(f"```{fence_language}")
        parts.append("```")

    return "\n".join(parts)


def to_prompt_compact(
    schema,
    *,
    errors: str | None = None,
    xml_tag: str = "output",
    fence_language: str = "json",
) -> str:
    """Generate a compact prompt - just calls to_prompt() with defaults.

    This is a convenience function that ensures both xml_tag and fence_language
    are always provided (most robust wrapper).

    Args:
        schema: Your schema (YAML string, Pydantic model, etc.)
        errors: Optional error message from previous validation
        xml_tag: XML tag name (default: "output")
        fence_language: Fence language (default: "json")

    Returns:
        Compact prompt string

    Examples:
        >>> prompt = to_prompt_compact("name: str\\nage: int")
        >>> print(prompt)
        Follow this schema:
        ```slimschema
        name: str
        age: int
        ```
        <BLANKLINE>
        To generate `JSON`:
        <output>```json
        ```</output>

        >>> # With errors
        >>> to_prompt_compact(schema, errors="Missing required fields: name")
    """
    return to_prompt(schema, errors=errors, xml_tag=xml_tag, fence_language=fence_language)
