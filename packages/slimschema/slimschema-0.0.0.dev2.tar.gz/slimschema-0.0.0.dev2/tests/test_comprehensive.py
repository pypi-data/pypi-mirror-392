"""Comprehensive tests for all type conversions and edge cases."""

from typing import Annotated

from pydantic import BaseModel
from pydantic import Field as PydanticField

from slimschema import parse_slimschema, to_data, to_schema


class TestCommentPreservation:
    """Test that comments are preserved in round-trip."""

    def test_field_comments_preserved(self):
        """Comments from YAML preserved in Schema IR."""
        yaml_str = """
name: str  # Full name
age: int   # Age in years
email?: email  # Contact email
"""
        schema = parse_slimschema(yaml_str)

        # Check descriptions extracted from comments
        assert schema.fields[0].description == "Full name"
        assert schema.fields[1].description == "Age in years"
        assert schema.fields[2].description == "Contact email"

    def test_schema_name_from_comment(self):
        """Schema name extracted from top comment."""
        yaml_str = """# Person
name: str
age: int
"""
        schema = parse_slimschema(yaml_str)
        assert schema.name == "Person"

    def test_yaml_round_trip_with_comments(self):
        """YAML round-trip preserves structure and descriptions."""
        yaml_str = """# User
name: str  # Full name
age: int
"""
        schema = parse_slimschema(yaml_str)
        yaml_out = str(schema)

        # Should have schema name
        assert "# User" in yaml_out
        # Should have field with description as comment
        assert "name: str" in yaml_out
        # Parse back
        schema2 = parse_slimschema(yaml_out)
        assert schema2.name == "User"


class TestPydanticTypeConversions:
    """Test all Pydantic type conversions."""

    def test_basic_types(self):
        """All basic Pydantic types convert correctly."""
        class AllTypes(BaseModel):
            s: str
            i: int
            f: float
            b: bool
            d: dict

        schema = to_schema(AllTypes)
        types = {f.name: f.type for f in schema.fields}

        assert types["s"] == "str"
        assert types["i"] == "int"
        assert types["f"] == "float"
        assert types["b"] == "bool"
        assert types["d"] == "obj"

    def test_string_length_constraints(self):
        """String length constraints from Pydantic."""
        class User(BaseModel):
            username: Annotated[str, PydanticField(min_length=3, max_length=20)]

        schema = to_schema(User)
        assert schema.fields[0].type == "str{3..20}"

    def test_numeric_range_constraints(self):
        """Numeric range constraints from Pydantic."""
        class Person(BaseModel):
            age: Annotated[int, PydanticField(ge=18, le=120)]

        schema = to_schema(Person)
        assert schema.fields[0].type == "18..120"

    def test_list_types(self):
        """List types convert correctly."""
        class Data(BaseModel):
            tags: list[str]
            nums: list[int]

        schema = to_schema(Data)
        types = {f.name: f.type for f in schema.fields}
        assert types["tags"] == "[str]"
        assert types["nums"] == "[int]"

    def test_set_types(self):
        """Set types convert correctly."""
        class Data(BaseModel):
            tags: set[str]
            ids: set[int]

        schema = to_schema(Data)
        fields = {f.name: f for f in schema.fields}
        assert fields["tags"].type == "[str]"
        assert fields["tags"].annotation == "Set[str]"
        assert fields["ids"].type == "[int]"
        assert fields["ids"].annotation == "Set[int]"

    def test_tuple_and_frozenset_annotations(self):
        """Tuple and FrozenSet gain :: annotations for round-trip."""

        class Geo(BaseModel):
            coords: tuple[float, float]
            labels: frozenset[str]

        schema = to_schema(Geo)
        fields = {f.name: f for f in schema.fields}

        assert fields["coords"].type == "[float]"
        assert fields["coords"].annotation == "Tuple[float, float]"
        assert fields["labels"].type == "[str]"
        assert fields["labels"].annotation == "FrozenSet[str]"


class TestMsgspecTypeConversions:
    """Test all SlimSchema type string → msgspec conversions."""

    def test_string_length(self):
        """String length constraints."""
        data, error = to_data('<json>{"username": "alice"}</json>', "username: str{3..20}")
        assert error is None
        assert data["username"] == "alice"

        # Too short
        data, error = to_data('<json>{"username": "ab"}</json>', "username: str{3..20}")
        assert error is not None
        assert data is None

    def test_numeric_ranges(self):
        """Numeric range validation."""
        # Int range
        data, error = to_data('<json>{"age": 30}</json>', "age: 18..120")
        assert error is None

        # Float range
        data, error = to_data('<json>{"ratio": 0.5}</json>', "ratio: 0.0..1.0")
        assert error is None

    def test_format_types(self):
        """All format types validate correctly."""
        # Email
        data, error = to_data('<json>{"email": "test@example.com"}</json>', "email: email")
        assert error is None

        data, error = to_data('<json>{"email": "notanemail"}</json>', "email: email")
        assert error is not None

        # URL
        data, error = to_data('<json>{"url": "https://example.com"}</json>', "url: url")
        assert error is None

        # Date
        data, error = to_data('<json>{"date": "2025-01-15"}</json>', "date: date")
        assert error is None

        # DateTime
        data, error = to_data('<json>{"dt": "2025-01-15T10:30:00"}</json>', "dt: datetime")
        assert error is None

        # UUID
        data, error = to_data(
            '<json>{"id": "550e8400-e29b-41d4-a716-446655440000"}</json>', "id: uuid"
        )
        assert error is None

    def test_regex_patterns(self):
        """Custom regex patterns validate."""
        data, error = to_data('<json>{"slug": "my-slug-123"}</json>', "slug: /^[a-z0-9-]+$/")
        assert error is None

        data, error = to_data('<json>{"slug": "Invalid Slug!"}</json>', "slug: /^[a-z0-9-]+$/")
        assert error is not None

    def test_enums(self):
        """Enum validation."""
        data, error = to_data('<json>{"status": "active"}</json>', "status: active | pending | done")
        assert error is None

        data, error = to_data('<json>{"status": "invalid"}</json>', "status: active | pending | done")
        assert error is not None

    def test_arrays(self):
        """Array type validation."""
        data, error = to_data('<json>{"tags": ["a", "b", "c"]}</json>', "tags: [str]")
        assert error is None

        data, error = to_data('<json>{"nums": [1, 2, 3]}</json>', "nums: [int]")
        assert error is None

    def test_sets(self):
        """Set (unique array) validation."""
        data, error = to_data('<json>{"ids": [1, 2, 3]}</json>', "ids: {int}")
        assert error is None

        data, error = to_data('<json>{"tags": ["a", "b", "c"]}</json>', "tags: {str}")
        assert error is None

    def test_type_annotation_round_trip(self):
        """:: annotations are parsed and enforced."""
        yaml = "ids: [int]  # unique ids  :: Set[int]"
        schema = parse_slimschema(yaml)
        field = schema.fields[0]

        assert field.description == "unique ids"
        assert field.annotation == "Set[int]"

        yaml_out = str(schema)
        assert ":: Set[int]" in yaml_out

    def test_tuple_annotation_validation(self):
        """Tuple annotations enforce tuple length."""
        schema = to_schema("coords: [float]  # :: Tuple[float, float]")

        data, error = to_data('<json>{"coords": [1.0, 2.0]}</json>', schema)
        assert error is None
        assert isinstance(data["coords"], tuple)

        data, error = to_data('<json>{"coords": [1.0, 2.0, 3.0]}</json>', schema)
        assert data is None
        assert error is not None

    def test_frozenset_annotation_validation(self):
        """FrozenSet annotations preserve container type."""
        schema = to_schema("tags: [str]  # :: FrozenSet[str]")

        data, error = to_data('<json>{"tags": ["a", "b"]}</json>', schema)
        assert error is None
        assert isinstance(data["tags"], frozenset)


class TestExtractJsonEdgeCases:
    """Test JSON extraction edge cases."""

    def test_json_tags_case_insensitive(self):
        """<JSON> and <json> both work."""
        data, error = to_data('<JSON>{"name": "Alice"}</JSON>', "name: str")
        assert error is None

    def test_output_tags(self):
        """<output> tags work."""
        data, error = to_data('<output>{"name": "Bob"}</output>', "name: str")
        assert error is None

    def test_code_fence_with_language(self):
        """Code fence with json language marker."""
        response = '```json\n{"name": "Charlie"}\n```'
        data, error = to_data(response, "name: str")
        assert error is None

    def test_code_fence_without_language(self):
        """Code fence without language marker."""
        response = '```\n{"name": "Dave"}\n```'
        data, error = to_data(response, "name: str")
        assert error is None

    def test_raw_json(self):
        """Raw JSON without tags."""
        data, error = to_data('{"name": "Eve"}', "name: str")
        assert error is None

    def test_no_json_found(self):
        """No JSON in response."""
        data, error = to_data("just plain text", "name: str")
        assert data is None
        assert "json" in error.lower()

    def test_malformed_json(self):
        """Malformed JSON."""
        data, error = to_data('<json>{invalid json}</json>', "name: str")
        assert data is None
        assert error is not None


class TestValidationResultTupleUnpacking:
    """Test ValidationResult tuple unpacking."""

    def test_tuple_unpacking_valid(self):
        """Valid result unpacks to (data, None)."""
        from slimschema import validate_response

        schema = parse_slimschema("name: str")
        result = validate_response('<json>{"name": "Alice"}</json>', schema)

        data, error = result
        assert data == {"name": "Alice"}
        assert error is None

    def test_tuple_unpacking_invalid(self):
        """Invalid result unpacks to (None, error)."""
        from slimschema import validate_response

        schema = parse_slimschema("name: str\nage: int")
        result = validate_response('<json>{"name": "Bob"}</json>', schema)

        data, error = result
        assert data is None
        assert error is not None
        assert "age" in error.lower()


class TestAllTypesCoverage:
    """Ensure all documented types are tested."""

    def test_all_primitives(self):
        """All primitive types work."""
        for typ in ["str", "int", "float", "bool", "obj"]:
            schema = to_schema(f"field: {typ}")
            assert schema.fields[0].type == typ

    def test_all_formats(self):
        """All format types work."""
        for fmt in ["email", "url", "date", "datetime", "uuid"]:
            schema = to_schema(f"field: {fmt}")
            assert schema.fields[0].type == fmt

    def test_optional_fields(self):
        """Optional field syntax."""
        schema = to_schema("email?: str")
        assert schema.fields[0].optional is True
        assert schema.fields[0].name == "email"
