"""Tests for prompt generation API."""

from pydantic import BaseModel, Field

from slimschema import to_prompt, to_prompt_compact


class User(BaseModel):
    """User model for testing."""
    name: str = Field(min_length=2, max_length=50)
    age: int = Field(ge=18, le=120)
    email: str


YAML_SCHEMA = """
name: str{2..50}
age: 18..120
email: email
"""


def test_to_prompt_default():
    """Default prompt uses XML tag + fence (most robust)."""
    prompt = to_prompt(YAML_SCHEMA)

    assert "```slimschema" in prompt
    assert "name: str{2..50}" in prompt
    assert "Generate valid structured data matching this:" in prompt
    assert "Wrap your response in:" in prompt
    assert "<output>" in prompt
    assert "</output>" in prompt
    assert "```json" in prompt


def test_to_prompt_custom_instruction():
    """Custom instruction text."""
    prompt = to_prompt(YAML_SCHEMA, instruction="Extract user information.")

    assert "Extract user information." in prompt
    assert "Generate valid structured data matching this:" not in prompt


def test_to_prompt_tag_only():
    """Tag without fence."""
    prompt = to_prompt(YAML_SCHEMA, fence="none", tag_name="json")

    # Schema always has slimschema fence
    assert "```slimschema" in prompt
    # Output wrapping uses tag only (with fence markers but no format label)
    assert "<json>" in prompt
    assert "</json>" in prompt


def test_to_prompt_fence_only():
    """Fence without tag."""
    prompt = to_prompt(YAML_SCHEMA, tag="none")

    # Schema uses slimschema fence
    assert "```slimschema" in prompt
    # Output wrapping uses json fence only
    assert "```json" in prompt
    assert "<output>" not in prompt
    assert "</output>" not in prompt


def test_to_prompt_no_wrapping():
    """No tag, no fence."""
    prompt = to_prompt(YAML_SCHEMA, tag="none", fence="none")

    # Schema still has slimschema fence
    assert "```slimschema" in prompt
    assert "name: str{2..50}" in prompt
    # No output wrapping instruction (no tags)
    assert "<output>" not in prompt


def test_to_prompt_custom_format_label():
    """Custom format label."""
    prompt = to_prompt(YAML_SCHEMA, format_label="yaml")

    # Schema always uses slimschema
    assert "```slimschema" in prompt
    # Output wrapping uses custom format label
    assert "```yaml" in prompt
    assert "```json" not in prompt


def test_to_prompt_custom_tag_name():
    """Custom tag name."""
    prompt = to_prompt(YAML_SCHEMA, tag_name="data")

    # Schema uses slimschema
    assert "```slimschema" in prompt
    # Output wrapping uses custom tag name
    assert "<data>" in prompt
    assert "</data>" in prompt


def test_to_prompt_compact():
    """Compact prompt (no instruction)."""
    prompt = to_prompt_compact(YAML_SCHEMA)

    assert prompt.startswith("<output>```json")
    assert prompt.endswith("```</output>")
    assert "Generate" not in prompt
    assert "name: str{2..50}" in prompt


def test_to_prompt_compact_custom_tag():
    """Compact prompt with custom tag name."""
    prompt = to_prompt_compact(YAML_SCHEMA, tag_name="json")

    assert prompt.startswith("<json>```json")
    assert prompt.endswith("```</json>")


def test_to_prompt_compact_custom_format():
    """Compact prompt with custom format label."""
    prompt = to_prompt_compact(YAML_SCHEMA, format_label="yaml")

    assert "```yaml" in prompt


def test_to_prompt_from_pydantic():
    """Generate prompt from Pydantic model."""
    prompt = to_prompt(User)

    # Schema uses slimschema
    assert "```slimschema" in prompt
    assert "name:" in prompt
    assert "age:" in prompt
    assert "email:" in prompt
    # Output wrapping
    assert "<output>" in prompt
    assert "```json" in prompt


def test_to_prompt_xml_wrapped_fence():
    """XML wrapped fence strategy."""
    prompt = to_prompt(YAML_SCHEMA, tag="xml", fence="fenced")

    # Schema uses slimschema
    assert "```slimschema" in prompt

    # Output wrapping should have both tag and fence
    assert "<output>" in prompt
    assert "</output>" in prompt
    assert "```json" in prompt

    # Should have instruction to use both
    assert "Wrap your response in:" in prompt


def test_to_prompt_empty_instruction():
    """Empty instruction string."""
    prompt = to_prompt(YAML_SCHEMA, instruction="")

    # Should still have schema and wrapping
    assert "```slimschema" in prompt
    assert "name: str{2..50}" in prompt
    assert "<output>" in prompt


def test_to_prompt_multiline_schema():
    """Multi-field schema formats correctly."""
    schema = """
# User
name: str
age: int
email: email
tags: [str]
"""
    prompt = to_prompt(schema)

    # Schema should use slimschema
    assert "```slimschema" in prompt

    # All fields should be present
    assert "name: str" in prompt
    assert "age: int" in prompt
    assert "email: email" in prompt
    assert "tags: [str]" in prompt

    # Output wrapping should be properly formatted
    assert "<output>" in prompt
    assert "```json" in prompt
