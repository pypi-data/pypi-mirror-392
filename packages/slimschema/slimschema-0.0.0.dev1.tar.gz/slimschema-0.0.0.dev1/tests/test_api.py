"""Tests for the public API (to_schema, to_data)."""

import pytest
from pydantic import BaseModel

from slimschema import Schema, to_data, to_schema


class Person(BaseModel):
    """Test Pydantic model."""

    name: str
    age: int
    email: str | None = None


class TestToSchema:
    """Test to_schema() conversion."""

    def test_from_pydantic_model(self):
        """Convert Pydantic model to Schema IR."""
        schema = to_schema(Person)
        assert schema.name == "Person"
        assert len(schema.fields) == 3
        assert [f.name for f in schema.fields] == ["name", "age", "email"]
        assert schema.fields[2].optional is True  # email is optional

    def test_from_yaml_string(self):
        """Convert YAML string to Schema IR."""
        schema = to_schema("name: str\nage: int")
        assert len(schema.fields) == 2
        assert schema.fields[0].name == "name"
        assert schema.fields[0].type == "str"
        assert schema.fields[1].name == "age"
        assert schema.fields[1].type == "int"

    def test_from_schema_passthrough(self):
        """Schema IR passes through unchanged."""
        original = Schema(fields=[])
        result = to_schema(original)
        assert result is original

    def test_invalid_type_raises(self):
        """Invalid type raises TypeError."""
        with pytest.raises(TypeError, match="Cannot convert"):
            to_schema(12345)


class TestToYaml:
    """Test to_yaml() generation."""

    def test_simple_schema(self):
        """Generate YAML from simple schema."""
        schema = to_schema("name: str\nage: int")
        yaml = str(schema)
        assert "name: str" in yaml
        assert "age: int" in yaml

    def test_with_optional_fields(self):
        """Optional fields marked with ?."""
        schema = to_schema(Person)
        yaml = str(schema)
        assert "name: str" in yaml
        assert "age: int" in yaml
        assert "email?: str" in yaml

    def test_with_schema_name(self):
        """Schema name appears as comment."""
        schema = to_schema(Person)
        yaml = str(schema)
        assert "# Person" in yaml


class TestToData:
    """Test to_data() validation and conversion."""

    def test_valid_pydantic_response(self):
        """Valid JSON returns Pydantic instance."""
        response = '<json>{"name": "Alice", "age": 30, "email": "alice@example.com"}</json>'
        person, error = to_data(response, Person)

        assert error is None
        assert isinstance(person, Person)
        assert person.name == "Alice"
        assert person.age == 30
        assert person.email == "alice@example.com"

    def test_valid_dict_response(self):
        """Valid JSON with YAML schema returns dict."""
        response = '<json>{"name": "Bob", "age": 25}</json>'
        data, error = to_data(response, "name: str\nage: int")

        assert error is None
        assert data == {"name": "Bob", "age": 25}

    def test_missing_required_field(self):
        """Missing field returns error."""
        response = '<json>{"name": "Charlie"}</json>'
        data, error = to_data(response, "name: str\nage: int")

        assert data is None
        assert error is not None
        assert "age" in error.lower()

    def test_invalid_range(self):
        """Out of range value returns error."""
        response = '<json>{"age": 10}</json>'
        data, error = to_data(response, "age: 18..120")

        assert data is None
        assert error is not None
        assert "18" in error  # msgspec reports the constraint

    def test_no_json_in_response(self):
        """No JSON found returns error."""
        response = "This is just text without JSON"
        data, error = to_data(response, "name: str")

        assert data is None
        assert error is not None
        assert "json" in error.lower()

    def test_extraction_from_code_fence(self):
        """Extract JSON from code fence."""
        response = '''
Here's the data:
```json
{"name": "Dave", "age": 35}
```
        '''
        data, error = to_data(response, "name: str\nage: int")

        assert error is None
        assert data["name"] == "Dave"

    def test_extraction_from_output_tags(self):
        """Extract JSON from <output> tags."""
        response = '<output>{"name": "Eve", "age": 40}</output>'
        data, error = to_data(response, "name: str\nage: int")

        assert error is None
        assert data["name"] == "Eve"

    def test_pydantic_optional_field_omitted(self):
        """Optional Pydantic field can be omitted."""
        response = '<json>{"name": "Frank", "age": 45}</json>'
        person, error = to_data(response, Person)

        assert error is None
        assert person.email is None

    def test_pydantic_optional_field_provided(self):
        """Optional Pydantic field can be provided."""
        response = '<json>{"name": "Grace", "age": 50, "email": "grace@example.com"}</json>'
        person, error = to_data(response, Person)

        assert error is None
        assert person.email == "grace@example.com"


class TestSlimErrors:
    """Test error message formatting."""

    def test_single_missing_field(self):
        """Single missing field error is concise."""
        response = '<json>{"name": "Alice"}</json>'
        _, error = to_data(response, "name: str\nage: int")

        assert error is not None
        # Should be slim, not verbose
        assert len(error) < 100
        assert "age" in error.lower()

    def test_invalid_value_error(self):
        """Invalid value error is clear."""
        response = '<json>{"age": 10}</json>'
        _, error = to_data(response, "age: 18..120")

        assert error is not None
        assert "age" in error.lower()
        # Should mention the constraint
        assert "18" in error or "range" in error.lower()


class TestArraysAndSets:
    """Test array and set validation."""

    def test_simple_array(self):
        """Validate simple array."""
        response = '<json>{"tags": ["python", "ai", "ml"]}</json>'
        data, error = to_data(response, "tags: [str]")

        assert error is None
        assert data["tags"] == ["python", "ai", "ml"]

    def test_unique_array_set(self):
        """Validate unique array (set)."""
        response = '<json>{"ids": [1, 2, 3]}</json>'
        data, error = to_data(response, "ids: {int}")

        assert error is None
        assert data["ids"] == [1, 2, 3]


class TestEnums:
    """Test enum validation."""

    def test_enum_validation(self):
        """Validate enum values."""
        response = '<json>{"status": "active"}</json>'
        data, error = to_data(response, "status: active | pending | done")

        assert error is None
        assert data["status"] == "active"

    def test_invalid_enum_value(self):
        """Reject invalid enum value."""
        response = '<json>{"status": "invalid"}</json>'
        data, error = to_data(response, "status: active | pending | done")

        assert data is None
        assert error is not None
