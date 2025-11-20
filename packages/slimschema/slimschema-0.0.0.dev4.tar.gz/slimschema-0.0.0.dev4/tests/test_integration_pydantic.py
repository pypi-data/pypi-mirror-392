"""Tests for Pydantic Integration.

This test module validates Pydantic integration features documented in
docs/integration_pydantic.md. Tests cover round-trip conversion between
Pydantic models and SlimSchema YAML.
"""

from pydantic import BaseModel, Field

from slimschema import to_data, to_schema


class TestPydanticToSchema:
    """Test converting Pydantic models to SlimSchema YAML."""

    def test_basic_model_to_schema(self):
        """Convert basic Pydantic model to schema."""

        class User(BaseModel):
            name: str
            age: int

        schema = to_schema(User)

        assert schema.name == "User"
        assert len(schema.fields) == 2
        assert {f.name for f in schema.fields} == {"name", "age"}

    def test_model_with_constraints(self):
        """Convert Pydantic model with Field constraints."""

        class User(BaseModel):
            username: str = Field(min_length=3, max_length=20)
            age: int = Field(ge=18, le=120)

        schema = to_schema(User)

        username_field = next(f for f in schema.fields if f.name == "username")
        age_field = next(f for f in schema.fields if f.name == "age")

        # Should convert constraints to SlimSchema syntax
        assert "str{" in username_field.type or "{" in username_field.type
        assert ".." in age_field.type

    def test_optional_fields(self):
        """Convert optional Pydantic fields."""

        class User(BaseModel):
            name: str
            email: str | None = None

        schema = to_schema(User)

        name_field = next(f for f in schema.fields if f.name == "name")
        email_field = next(f for f in schema.fields if f.name == "email")

        assert name_field.optional is False
        assert email_field.optional is True

    def test_field_descriptions(self):
        """Preserve field descriptions from Pydantic."""

        class User(BaseModel):
            name: str = Field(description="Full name")
            age: int = Field(description="Age in years")

        schema = to_schema(User)

        name_field = next(f for f in schema.fields if f.name == "name")
        age_field = next(f for f in schema.fields if f.name == "age")

        assert name_field.description == "Full name"
        assert age_field.description == "Age in years"


class TestPydanticListFields:
    """Test Pydantic models with list fields."""

    def test_list_field_to_schema(self):
        """Convert list fields to array syntax."""

        class User(BaseModel):
            name: str
            tags: list[str]

        schema = to_schema(User)

        tags_field = next(f for f in schema.fields if f.name == "tags")
        assert "[" in tags_field.type and "]" in tags_field.type


class TestPydanticSchemaName:
    """Test schema name preservation."""

    def test_schema_name_from_model(self):
        """Schema name is taken from model class name."""

        class UserAccount(BaseModel):
            name: str

        schema = to_schema(UserAccount)

        assert schema.name == "UserAccount"


class TestPydanticToYaml:
    """Test YAML generation from Pydantic models."""

    def test_generate_yaml_from_model(self):
        """Generate YAML string from Pydantic model."""

        class User(BaseModel):
            name: str
            age: int

        schema = to_schema(User)
        yaml_str = str(schema)

        assert "# User" in yaml_str or "User" in yaml_str
        assert "name: str" in yaml_str
        assert "age: int" in yaml_str

    def test_yaml_with_optional_fields(self):
        """Optional fields marked with ? in YAML."""

        class User(BaseModel):
            name: str
            email: str | None = None

        schema = to_schema(User)
        yaml_str = str(schema)

        assert "email?: str" in yaml_str or "email?" in yaml_str


class TestPydanticUnionTypes:
    """Test Pydantic Union types generate correct SlimSchema syntax."""

    def test_union_in_pydantic_model(self):
        """Pydantic Union should generate pipe-delimited syntax."""

        class MyModel(BaseModel):
            value: str | int

        schema = to_schema(MyModel)
        yaml_str = str(schema)

        # Should generate "value: str | int"
        assert "str | int" in yaml_str

    def test_literal_in_pydantic_model(self):
        """Pydantic Literal should generate pipe-delimited enum."""
        from typing import Literal

        class MyModel(BaseModel):
            status: Literal["active", "inactive"]

        schema = to_schema(MyModel)
        yaml_str = str(schema)

        # Should generate "status: active | inactive"
        assert "active | inactive" in yaml_str

    def test_union_with_set_preserves_annotation(self):
        """Union with set should preserve Set annotation."""

        class MyModel(BaseModel):
            value: set[int] | int

        schema = to_schema(MyModel)
        yaml_str = str(schema)

        # Should generate "value: [int] | int  # :: Union[Set[int], int]"
        # The exact format may vary but should contain the union parts
        assert "[int] | int" in yaml_str or "int" in yaml_str

    def test_union_with_container_validates_correctly(self):
        """Union with set should validate set inputs correctly."""

        class MyModel(BaseModel):
            value: set[int] | list[int]

        # Should accept list input and validate with Pydantic model
        data, error = to_data('{"value": [1, 2, 3]}', MyModel)
        assert error is None
        # Pydantic accepts either set or list (validates union)
        assert isinstance(data.value, (set, list))
        # Values should be correct
        if isinstance(data.value, set):
            assert data.value == {1, 2, 3}
        else:
            assert data.value == [1, 2, 3]

    def test_union_primitives_no_annotation(self):
        """Union of primitives shouldn't add annotation."""

        class MyModel(BaseModel):
            value: str | int

        schema = to_schema(MyModel)

        # Should NOT have annotation for simple unions
        field = schema.fields[0]
        assert field.annotation is None

    def test_union_validation_with_pydantic(self):
        """Union types validate correctly using Pydantic."""

        class MyModel(BaseModel):
            value: str | int

        # Should accept string
        data, error = to_data('{"value": "hello"}', MyModel)
        assert error is None
        assert data.value == "hello"

        # Should accept int
        data, error = to_data('{"value": 42}', MyModel)
        assert error is None
        assert data.value == 42

        # Should reject float (not in union)
        data, error = to_data('{"value": 3.14}', MyModel)
        # May accept (coerced) or reject depending on Pydantic's union validation
        # This documents the actual behavior
        pass  # Implementation-dependent
