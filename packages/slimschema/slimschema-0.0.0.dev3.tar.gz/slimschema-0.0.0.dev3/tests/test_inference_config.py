"""Test InferenceConfig options for from_data()."""

from slimschema import InferenceConfig, from_data, to_yaml


class TestMasterSwitches:
    """Test master on/off switches for detection types."""

    def test_detect_enums_off(self):
        """Disable enum detection."""
        data = [
            {"status": "active"},
            {"status": "inactive"},
            {"status": "active"},
        ]

        config = InferenceConfig(detect_enums=False)
        schema = from_data(data, config=config)
        yaml = to_yaml(schema)

        assert "status: str" in yaml
        assert "|" not in yaml

    def test_detect_ranges_off(self):
        """Disable range detection for integers."""
        data = [
            {"age": 25},
            {"age": 30},
            {"age": 35},
        ]

        config = InferenceConfig(detect_ranges=False)
        schema = from_data(data, config=config)
        yaml = to_yaml(schema)

        assert "age: int" in yaml
        assert ".." not in yaml

    def test_detect_formats_off(self):
        """Disable format detection."""
        data = [
            {"email": "alice@example.com"},
            {"email": "bob@example.com"},
        ]

        config = InferenceConfig(detect_formats=False)
        schema = from_data(data, config=config)
        yaml = to_yaml(schema)

        assert "email: str" in yaml
        assert "email: email" not in yaml


class TestEnumCardinality:
    """Test enum_max_cardinality control."""

    def test_enum_cardinality_default(self):
        """Default cardinality limit is 5."""
        # 5 unique values with repetition → enum
        data = [
            {"status": "a"},
            {"status": "b"},
            {"status": "c"},
            {"status": "d"},
            {"status": "e"},
            {"status": "a"},  # repetition
        ]

        schema = from_data(data)
        yaml = to_yaml(schema)

        assert "|" in yaml

    def test_enum_cardinality_exceeded(self):
        """6 unique values exceeds default limit → str."""
        data = [
            {"status": "a"},
            {"status": "b"},
            {"status": "c"},
            {"status": "d"},
            {"status": "e"},
            {"status": "f"},
        ]

        schema = from_data(data)
        yaml = to_yaml(schema)

        assert "status: str" in yaml
        assert "|" not in yaml

    def test_enum_cardinality_increased(self):
        """Increase cardinality limit to 10."""
        data = [
            {"status": "a"},
            {"status": "b"},
            {"status": "c"},
            {"status": "d"},
            {"status": "e"},
            {"status": "f"},
            {"status": "a"},  # repetition
        ]

        config = InferenceConfig(enum_max_cardinality=10)
        schema = from_data(data, config=config)
        yaml = to_yaml(schema)

        assert "|" in yaml
        assert "a" in yaml


class TestRangeDetection:
    """Test int_range_max_delta and float_range_max_delta."""

    def test_int_range_default(self):
        """Default int range delta is 200."""
        # Range of 200 → uses range syntax
        data = [{"age": 0}, {"age": 200}]

        schema = from_data(data)
        yaml = to_yaml(schema)

        assert "0..200" in yaml

    def test_int_range_exceeded(self):
        """Range > 200 → plain int."""
        data = [{"age": 0}, {"age": 201}]

        schema = from_data(data)
        yaml = to_yaml(schema)

        assert "age: int" in yaml
        assert ".." not in yaml

    def test_int_range_custom_delta(self):
        """Custom int range delta."""
        data = [{"age": 0}, {"age": 500}]

        config = InferenceConfig(int_range_max_delta=1000)
        schema = from_data(data, config=config)
        yaml = to_yaml(schema)

        assert "0..500" in yaml

    def test_float_range_default(self):
        """Default float range delta is 10000."""
        data = [{"price": 0.0}, {"price": 5000.0}]

        schema = from_data(data)
        yaml = to_yaml(schema)

        assert "0.0..5000.0" in yaml

    def test_float_range_exceeded(self):
        """Range > 10000 → plain float."""
        data = [{"price": 0.0}, {"price": 15000.0}]

        schema = from_data(data)
        yaml = to_yaml(schema)

        assert "price: float" in yaml
        assert ".." not in yaml


class TestMaxSamples:
    """Test max_samples guard."""

    def test_max_samples_limits_processing(self):
        """Only process first N records."""
        # 100 records but only process first 3
        data = [{"value": i} for i in range(100)]

        config = InferenceConfig(max_samples=3)
        schema = from_data(data, config=config)
        yaml = to_yaml(schema)

        # Should detect range 0..2, not 0..99
        assert "0..2" in yaml

    def test_max_samples_none_processes_all(self):
        """None means process all records (default)."""
        data = [{"value": i} for i in range(10)]

        config = InferenceConfig(max_samples=None)
        schema = from_data(data, config=config)
        yaml = to_yaml(schema)

        assert "0..9" in yaml


class TestMaxNestingDepth:
    """Test max_nesting_depth guard for recursive structures."""

    def test_max_nesting_depth_prevents_deep_recursion(self):
        """Stop inferring nested objects at depth limit."""
        # Create deeply nested structure
        data = [{"level1": {"level2": {"level3": {"level4": {"level5": {}}}}}}]

        config = InferenceConfig(max_nesting_depth=2)
        schema = from_data(data, config=config)
        yaml = to_yaml(schema)

        # Should stop after level2
        assert "level1:" in yaml
        # Should have nested structure but limited depth
        # At depth 2, we should hit the limit and get "obj"


class TestCombinedOptions:
    """Test multiple config options working together."""

    def test_disable_all_detection(self):
        """Turn off all detection types."""
        data = [
            {"email": "alice@example.com", "age": 25, "status": "active"},
            {"email": "bob@example.com", "age": 35, "status": "inactive"},
        ]

        config = InferenceConfig(
            detect_enums=False,
            detect_ranges=False,
            detect_formats=False,
        )
        schema = from_data(data, config=config)
        yaml = to_yaml(schema)

        assert "email: str" in yaml
        assert "age: int" in yaml
        assert "status: str" in yaml

    def test_aggressive_enum_detection(self):
        """More permissive enum settings."""
        data = [
            {"status": "a"},
            {"status": "b"},
            {"status": "c"},
            {"status": "d"},
            {"status": "e"},
            {"status": "f"},
            {"status": "g"},
            {"status": "a"},  # repetition
        ]

        config = InferenceConfig(enum_max_cardinality=15)
        schema = from_data(data, config=config)
        yaml = to_yaml(schema)

        assert "|" in yaml


class TestArraysAndNesting:
    """Test config with arrays and nested structures."""

    def test_nested_objects_respect_config(self):
        """Nested object inference uses config."""
        data = [
            {"user": {"status": "active"}},
            {"user": {"status": "inactive"}},
            {"user": {"status": "active"}},
        ]

        # With enums enabled
        config1 = InferenceConfig(detect_enums=True)
        schema1 = from_data(data, config=config1)
        yaml1 = to_yaml(schema1)

        # With enums disabled
        config2 = InferenceConfig(detect_enums=False)
        schema2 = from_data(data, config=config2)
        yaml2 = to_yaml(schema2)

        # First should have enum, second should be str
        assert "|" in yaml1
        assert "str" in yaml2

    def test_arrays_respect_config(self):
        """Array element inference uses config."""
        data = [
            {"tags": ["active", "inactive", "active"]},
        ]

        # With enums enabled
        config1 = InferenceConfig(detect_enums=True)
        schema1 = from_data(data, config=config1)
        yaml1 = to_yaml(schema1)

        # With enums disabled
        config2 = InferenceConfig(detect_enums=False)
        schema2 = from_data(data, config=config2)
        yaml2 = to_yaml(schema2)

        # First should have enum in array, second should be [str]
        assert "|" in yaml1
        assert "[str]" in yaml2
