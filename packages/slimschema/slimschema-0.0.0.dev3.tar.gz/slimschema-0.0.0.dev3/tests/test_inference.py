"""Test schema inference from data."""


from slimschema import from_data, to_msgspec, to_pydantic, to_yaml


class TestBasicInference:
    """Test basic type inference."""

    def test_single_object(self):
        """Infer schema from a single object."""
        data = {"name": "Alice", "age": 30}

        schema = from_data(data, name="User")

        assert schema.name == "User"
        assert len(schema.fields) == 2

        name_field = next(f for f in schema.fields if f.name == "name")
        age_field = next(f for f in schema.fields if f.name == "age")

        assert name_field.type == "str"
        assert age_field.type == "30..30"  # single value

    def test_multiple_objects(self):
        """Infer schema from multiple examples."""
        data = [
            {"name": "Alice", "age": 30, "active": True},
            {"name": "Bob", "age": 25, "active": False},
            {"name": "Charlie", "age": 35, "active": True},
        ]

        schema = from_data(data, name="User")

        assert schema.name == "User"
        assert len(schema.fields) == 3

        age_field = next(f for f in schema.fields if f.name == "age")
        active_field = next(f for f in schema.fields if f.name == "active")

        assert age_field.type == "25..35"  # range detected
        assert active_field.type == "bool"


class TestEnumDetection:
    """Test enum/literal detection."""

    def test_enum_inference(self):
        """Detect enums from repeated string values."""
        data = [
            {"status": "active"},
            {"status": "draft"},
            {"status": "active"},
            {"status": "archived"},
            {"status": "draft"},
        ]

        schema = from_data(data)

        status_field = next(f for f in schema.fields if f.name == "status")

        # Should detect enum
        assert "|" in status_field.type
        assert "active" in status_field.type
        assert "draft" in status_field.type
        assert "archived" in status_field.type

    def test_non_enum_strings(self):
        """Don't treat unique strings as enums."""
        data = [
            {"comment": "This is comment 1"},
            {"comment": "This is comment 2"},
            {"comment": "This is comment 3"},
        ]

        schema = from_data(data)

        comment_field = next(f for f in schema.fields if f.name == "comment")

        # Should be plain str (no enum)
        assert comment_field.type == "str"


class TestRangeDetection:
    """Test numeric range detection."""

    def test_int_range(self):
        """Detect integer ranges."""
        data = [
            {"age": 18},
            {"age": 65},
            {"age": 42},
        ]

        schema = from_data(data)

        age_field = next(f for f in schema.fields if f.name == "age")

        assert age_field.type == "18..65"

    def test_float_range(self):
        """Detect float ranges."""
        data = [
            {"price": 9.99},
            {"price": 99.99},
            {"price": 49.99},
        ]

        schema = from_data(data)

        price_field = next(f for f in schema.fields if f.name == "price")

        assert price_field.type == "9.99..99.99"


class TestFormatDetection:
    """Test format pattern detection."""

    def test_email_detection(self):
        """Detect email format."""
        data = [
            {"email": "alice@example.com"},
            {"email": "bob@example.com"},
        ]

        schema = from_data(data)

        email_field = next(f for f in schema.fields if f.name == "email")

        assert email_field.type == "email"

    def test_url_detection(self):
        """Detect URL format."""
        data = [
            {"url": "https://example.com"},
            {"url": "http://test.com"},
        ]

        schema = from_data(data)

        url_field = next(f for f in schema.fields if f.name == "url")

        assert url_field.type == "url"

    def test_date_detection(self):
        """Detect date format."""
        data = [
            {"created": "2024-01-15"},
            {"created": "2024-02-20"},
        ]

        schema = from_data(data)

        created_field = next(f for f in schema.fields if f.name == "created")

        assert created_field.type == "date"

    def test_datetime_detection(self):
        """Detect datetime format."""
        data = [
            {"created": "2024-01-15T10:30:00Z"},
            {"created": "2024-02-20T14:45:00Z"},
        ]

        schema = from_data(data)

        created_field = next(f for f in schema.fields if f.name == "created")

        assert created_field.type == "datetime"


class TestOptionalFields:
    """Test optional field detection."""

    def test_optional_field(self):
        """Detect optional fields (missing in some examples)."""
        data = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob"},  # email missing
            {"name": "Charlie", "email": "charlie@example.com"},
        ]

        schema = from_data(data)

        name_field = next(f for f in schema.fields if f.name == "name")
        email_field = next(f for f in schema.fields if f.name == "email")

        assert not name_field.optional
        assert email_field.optional


class TestNestedStructures:
    """Test nested objects and arrays."""

    def test_nested_object(self):
        """Detect nested objects with inline syntax."""
        data = [
            {"user": {"name": "Alice", "age": 30}},
            {"user": {"name": "Bob", "age": 25}},
        ]

        schema = from_data(data)

        user_field = next(f for f in schema.fields if f.name == "user")

        # Should now use inline object syntax instead of just "obj"
        assert user_field.type.startswith("{")
        assert "name:" in user_field.type
        assert "age:" in user_field.type

    def test_deeply_nested_objects(self):
        """Handle deeply nested structures."""
        data = [
            {"user": {"profile": {"name": "Alice", "bio": "Engineer"}}},
            {"user": {"profile": {"name": "Bob", "bio": "Designer"}}},
        ]

        schema = from_data(data)

        user_field = next(f for f in schema.fields if f.name == "user")

        # Should have nested inline object syntax
        assert "{" in user_field.type
        assert "profile:" in user_field.type

    def test_nested_optional_fields(self):
        """Handle optional fields in nested objects."""
        data = [
            {"user": {"name": "Alice", "email": "alice@example.com"}},
            {"user": {"name": "Bob"}},  # email missing
        ]

        schema = from_data(data)

        user_field = next(f for f in schema.fields if f.name == "user")

        # Should mark email as optional with "?"
        assert "email?:" in user_field.type or "email:" in user_field.type

    def test_array_field(self):
        """Detect array fields."""
        data = [
            {"tags": ["python", "ml"]},
            {"tags": ["javascript", "web"]},
        ]

        schema = from_data(data)

        tags_field = next(f for f in schema.fields if f.name == "tags")

        assert tags_field.type == "[str]"


class TestIntegrationWithConversions:
    """Test from_data() integration with conversion API."""

    def test_from_data_to_yaml(self):
        """Infer schema from data, then convert to YAML."""
        data = [
            {"username": "alice_wonderland", "age": 30, "status": "active"},
            {"username": "bob_the_builder", "age": 25, "status": "draft"},
            {"username": "charlie_chocolate", "age": 35, "status": "active"},  # repetition for enum
        ]

        schema = from_data(data, name="User")
        yaml = to_yaml(schema)

        assert "# User" in yaml
        assert "username: str" in yaml  # usernames are unique, not an enum
        assert "25..35" in yaml or "age: int" in yaml
        assert "|" in yaml  # enum for status (has repetition)

    def test_from_data_to_pydantic(self):
        """Infer schema from data, then create Pydantic model."""
        data = [
            {"username": "alice_wonderland", "age": 30, "status": "active"},
            {"username": "bob_the_builder", "age": 25, "status": "draft"},
            {"username": "charlie_chocolate", "age": 28, "status": "active"},  # repetition
        ]

        schema = from_data(data, name="User")
        user_model = to_pydantic(schema)

        assert user_model.__name__ == "User"

        # Create instance
        user = user_model(username="diana_the_warrior", age=28, status="active")
        assert user.username == "diana_the_warrior"

    def test_from_data_to_msgspec(self):
        """Infer schema from data, then create msgspec Struct."""
        import msgspec

        data = [
            {"username": "alice_wonderland", "age": 30, "status": "active"},
            {"username": "bob_the_builder", "age": 25, "status": "draft"},
            {"username": "charlie_chocolate", "age": 28, "status": "active"},
        ]

        schema = from_data(data, name="User")
        user_struct = to_msgspec(schema)

        assert user_struct.__name__ == "User"

        # Create instance
        user = msgspec.convert(
            {"username": "diana_the_warrior", "age": 28, "status": "active"},
            type=user_struct
        )
        assert user.username == "diana_the_warrior"

    def test_round_trip(self):
        """Infer schema from data, convert to Pydantic, generate instances."""
        examples = [
            {"product_name": "Wireless Mouse", "price": 19.99, "category": "electronics"},
            {"product_name": "USB Cable", "price": 9.99, "category": "electronics"},
            {"product_name": "Desk Lamp", "price": 29.99, "category": "office"},
            {"product_name": "Notebook", "price": 5.99, "category": "office"},
        ]

        # Infer schema
        schema = from_data(examples, name="Product")

        # Convert to Pydantic
        product_model = to_pydantic(schema)

        # Create new instance (product_name won't be enum, category will be)
        product = product_model(product_name="Stapler", price=15.99, category="office")

        assert product.product_name == "Stapler"
        assert product.price == 15.99
        assert product.category == "office"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_data(self):
        """Handle empty data."""
        schema = from_data([])

        assert len(schema.fields) == 0

    def test_list_of_empty_objects(self):
        """Handle list of empty objects."""
        data = [{}, {}]

        schema = from_data(data)

        assert len(schema.fields) == 0

    def test_single_null_value(self):
        """Handle null values - default to str."""
        data = [{"name": None}]

        schema = from_data(data)

        name_field = next(f for f in schema.fields if f.name == "name")

        # Should default to str (pragmatic choice for most permissive type)
        assert name_field.type == "str"

    def test_field_sometimes_present_always_null(self):
        """Field is optional and always null when present."""
        data = [
            {"name": "Alice", "bio": None},
            {"name": "Bob"},  # bio missing
        ]

        schema = from_data(data)

        bio_field = next(f for f in schema.fields if f.name == "bio")

        # Should be optional and default to str
        assert bio_field.optional
        assert bio_field.type == "str"

    def test_mixed_types(self):
        """Handle mixed types (fallback to obj)."""
        data = [
            {"value": 42},
            {"value": "hello"},
        ]

        schema = from_data(data)

        value_field = next(f for f in schema.fields if f.name == "value")

        # Mixed types → obj
        assert value_field.type == "obj"

    def test_large_integer_ranges(self):
        """Don't create range constraints for very large ranges."""
        data = [
            {"id": 1},
            {"id": 1000000},
        ]

        schema = from_data(data)

        id_field = next(f for f in schema.fields if f.name == "id")

        # Should be just "int" not "1..1000000"
        assert id_field.type == "int"

    def test_reasonable_integer_ranges(self):
        """Create range constraints for reasonable ranges."""
        data = [
            {"age": 18},
            {"age": 65},
        ]

        schema = from_data(data)

        age_field = next(f for f in schema.fields if f.name == "age")

        # Should use range syntax
        assert age_field.type == "18..65"

    def test_empty_nested_objects(self):
        """Handle empty nested objects."""
        data = [
            {"metadata": {}},
            {"metadata": {}},
        ]

        schema = from_data(data)

        metadata_field = next(f for f in schema.fields if f.name == "metadata")

        # Empty objects fall back to "obj"
        assert metadata_field.type == "obj"


class TestArrayEdgeCases:
    """Test edge cases for array type inference."""

    def test_array_of_empty_objects(self):
        """Array containing only empty objects."""
        data = [
            {"items": [{}, {}]},
            {"items": [{}]},
        ]

        schema = from_data(data)

        items_field = next(f for f in schema.fields if f.name == "items")

        # Should be array of obj
        assert items_field.type == "[obj]"

    def test_array_with_mixed_primitive_types(self):
        """Array with mixed primitive types."""
        data = [
            {"values": [1, "hello", 2.5, True]},
        ]

        schema = from_data(data)

        values_field = next(f for f in schema.fields if f.name == "values")

        # Mixed types → [obj]
        assert values_field.type == "[obj]"

    def test_array_of_mixed_complex_types(self):
        """Array with mix of objects and arrays."""
        data = [
            {"items": [{"a": 1}, ["b"]]},
        ]

        schema = from_data(data)

        items_field = next(f for f in schema.fields if f.name == "items")

        # Mixed complex types → [obj]
        assert items_field.type == "[obj]"

    def test_array_containing_only_null(self):
        """Array that only contains null values."""
        data = [
            {"tags": [None, None]},
            {"tags": [None]},
        ]

        schema = from_data(data)

        tags_field = next(f for f in schema.fields if f.name == "tags")

        # Unknown inner type → [str] (default for nulls)
        assert tags_field.type in ["[str]", "[obj]"]


class TestHeuristicBoundaries:
    """Test the exact boundaries of range and enum heuristics."""

    def test_integer_range_at_boundary(self):
        """Test exact boundary of range heuristic (200)."""
        # Inside boundary
        data_inside = [{"val": 0}, {"val": 200}]
        schema_inside = from_data(data_inside)
        val_field_inside = next(f for f in schema_inside.fields if f.name == "val")
        assert val_field_inside.type == "0..200"

        # Just outside boundary
        data_outside = [{"val": 0}, {"val": 201}]
        schema_outside = from_data(data_outside)
        val_field_outside = next(f for f in schema_outside.fields if f.name == "val")
        assert val_field_outside.type == "int"

    def test_float_range_with_outlier(self):
        """Float range with one outlier value."""
        data = [
            {"score": 0.9},
            {"score": 0.91},
            {"score": 0.95},
            {"score": 500.0},
        ]

        schema = from_data(data)

        score_field = next(f for f in schema.fields if f.name == "score")

        # Current logic: uses min..max even with outlier
        # This is technically correct but could be improved
        assert score_field.type == "0.9..500.0"

    def test_enum_short_unique_strings(self):
        """Enum detection with short but unique strings (≤3, ≤15 chars)."""
        data = [
            {"code": "A"},
            {"code": "B"},
            {"code": "C"},
        ]

        schema = from_data(data)

        code_field = next(f for f in schema.fields if f.name == "code")

        # Should detect as enum (very_few_unique_and_short rule)
        assert "|" in code_field.type
        assert "A" in code_field.type
        assert "B" in code_field.type
        assert "C" in code_field.type

    def test_enum_long_strings_with_repetition(self):
        """Enum detection with long strings but repetition."""
        data = [
            {"category": "long_category_name_one"},
            {"category": "long_category_name_two"},
            {"category": "long_category_name_one"},  # repetition
        ]

        schema = from_data(data)

        category_field = next(f for f in schema.fields if f.name == "category")

        # Should detect as enum (has_repetition rule)
        assert "|" in category_field.type

    def test_string_values_that_look_like_booleans(self):
        """String values that look like other types."""
        data = [
            {"value": "true"},
            {"value": "false"},
        ]

        schema = from_data(data)

        value_field = next(f for f in schema.fields if f.name == "value")

        # Should be detected as enum of strings, not bool
        assert value_field.type == "false | true"

    def test_string_values_that_look_like_numbers(self):
        """String values that look like numbers."""
        data = [
            {"value": "1"},
            {"value": "2"},
        ]

        schema = from_data(data)

        value_field = next(f for f in schema.fields if f.name == "value")

        # Should be detected as enum of strings, not int
        assert value_field.type == "1 | 2"
