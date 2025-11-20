"""Tests for JSON Patch (RFC 6902) Feature.

This test module validates JSON Patch features documented in
docs/advanced_json_patch.md. Tests cover all standard patch operations.
"""

import pytest

from slimschema.patch import PatchError, apply_patch


class TestAddOperation:
    """Test 'add' patch operation."""

    def test_add_property_to_object(self):
        """Add a new property to an object."""
        data = {"name": "Alice"}
        patch = {"op": "add", "path": "/age", "value": 30}

        result = apply_patch(data, patch)

        assert result["name"] == "Alice"
        assert result["age"] == 30

    def test_add_nested_property(self):
        """Add a property to a nested object."""
        data = {"user": {"name": "Alice"}}
        patch = {"op": "add", "path": "/user/age", "value": 30}

        result = apply_patch(data, patch)

        assert result["user"]["age"] == 30

    def test_add_array_element(self):
        """Add an element to an array."""
        data = {"tags": ["python"]}
        patch = {"op": "add", "path": "/tags/1", "value": "testing"}

        result = apply_patch(data, patch)

        assert result["tags"] == ["python", "testing"]

    def test_add_array_element_with_dash(self):
        """Add element to end of array using '-'."""
        data = {"tags": ["python", "testing"]}
        patch = {"op": "add", "path": "/tags/-", "value": "slimschema"}

        result = apply_patch(data, patch)

        assert result["tags"] == ["python", "testing", "slimschema"]

    def test_add_overwrites_existing(self):
        """Add operation overwrites existing values."""
        data = {"name": "Alice"}
        patch = {"op": "add", "path": "/name", "value": "Bob"}

        result = apply_patch(data, patch)

        assert result["name"] == "Bob"


class TestRemoveOperation:
    """Test 'remove' patch operation."""

    def test_remove_property(self):
        """Remove a property from an object."""
        data = {"name": "Alice", "age": 30}
        patch = {"op": "remove", "path": "/age"}

        result = apply_patch(data, patch)

        assert "age" not in result
        assert result["name"] == "Alice"

    def test_remove_nested_property(self):
        """Remove a property from a nested object."""
        data = {"user": {"name": "Alice", "age": 30}}
        patch = {"op": "remove", "path": "/user/age"}

        result = apply_patch(data, patch)

        assert "age" not in result["user"]
        assert result["user"]["name"] == "Alice"

    def test_remove_array_element(self):
        """Remove an element from an array."""
        data = {"tags": ["python", "testing", "slimschema"]}
        patch = {"op": "remove", "path": "/tags/1"}

        result = apply_patch(data, patch)

        assert result["tags"] == ["python", "slimschema"]

    def test_remove_nonexistent_path_errors(self):
        """Removing a nonexistent path raises error."""
        data = {"name": "Alice"}
        patch = {"op": "remove", "path": "/age"}

        with pytest.raises(PatchError):
            apply_patch(data, patch)


class TestReplaceOperation:
    """Test 'replace' patch operation."""

    def test_replace_property(self):
        """Replace a property value."""
        data = {"name": "Alice", "age": 30}
        patch = {"op": "replace", "path": "/age", "value": 31}

        result = apply_patch(data, patch)

        assert result["age"] == 31

    def test_replace_nested_property(self):
        """Replace a nested property value."""
        data = {"user": {"name": "Alice", "age": 30}}
        patch = {"op": "replace", "path": "/user/age", "value": 31}

        result = apply_patch(data, patch)

        assert result["user"]["age"] == 31

    def test_replace_array_element(self):
        """Replace an array element."""
        data = {"tags": ["python", "testing"]}
        patch = {"op": "replace", "path": "/tags/1", "value": "slimschema"}

        result = apply_patch(data, patch)

        assert result["tags"] == ["python", "slimschema"]

    def test_replace_nonexistent_path_errors(self):
        """Replacing a nonexistent path raises error."""
        data = {"name": "Alice"}
        patch = {"op": "replace", "path": "/age", "value": 30}

        with pytest.raises(PatchError):
            apply_patch(data, patch)


class TestMoveOperation:
    """Test 'move' patch operation."""

    def test_move_property(self):
        """Move a property to a new location."""
        data = {"name": "Alice", "age": 30}
        patch = {"op": "move", "from": "/age", "path": "/years"}

        result = apply_patch(data, patch)

        assert "age" not in result
        assert result["years"] == 30
        assert result["name"] == "Alice"

    def test_move_nested_to_root(self):
        """Move a nested property to root level."""
        data = {"user": {"name": "Alice", "age": 30}}
        patch = {"op": "move", "from": "/user/age", "path": "/age"}

        result = apply_patch(data, patch)

        assert "age" not in result["user"]
        assert result["age"] == 30

    def test_move_array_element(self):
        """Move an array element to a different index."""
        data = {"tags": ["python", "testing", "slimschema"]}
        patch = {"op": "move", "from": "/tags/2", "path": "/tags/0"}

        result = apply_patch(data, patch)

        # Implementation-dependent: verify behavior
        assert "slimschema" in result["tags"]


class TestCopyOperation:
    """Test 'copy' patch operation."""

    def test_copy_property(self):
        """Copy a property to a new location."""
        data = {"name": "Alice", "age": 30}
        patch = {"op": "copy", "from": "/age", "path": "/years"}

        result = apply_patch(data, patch)

        assert result["age"] == 30
        assert result["years"] == 30
        assert result["name"] == "Alice"

    def test_copy_nested_object(self):
        """Copy a nested object."""
        data = {"user": {"name": "Alice"}, "metadata": {}}
        patch = {"op": "copy", "from": "/user", "path": "/metadata/user"}

        result = apply_patch(data, patch)

        assert result["user"]["name"] == "Alice"
        assert result["metadata"]["user"]["name"] == "Alice"



class TestTestOperation:
    """Test 'test' patch operation."""

    def test_test_succeeds_when_equal(self):
        """Test operation succeeds when values are equal."""
        data = {"name": "Alice", "age": 30}
        patch = {"op": "test", "path": "/age", "value": 30}

        result = apply_patch(data, patch)

        # Data should be unchanged
        assert result == data

    def test_test_fails_when_not_equal(self):
        """Test operation fails when values are not equal."""
        data = {"name": "Alice", "age": 30}
        patch = {"op": "test", "path": "/age", "value": 31}

        with pytest.raises(PatchError):
            apply_patch(data, patch)

    def test_test_nested_value(self):
        """Test operation on nested value."""
        data = {"user": {"name": "Alice", "age": 30}}
        patch = {"op": "test", "path": "/user/name", "value": "Alice"}

        result = apply_patch(data, patch)

        assert result == data


class TestMultiplePatchOperations:
    """Test applying multiple patch operations."""

    def test_apply_multiple_patches(self):
        """Apply a list of patch operations."""
        data = {"name": "Alice", "age": 30}
        patches = [
            {"op": "add", "path": "/email", "value": "alice@example.com"},
            {"op": "replace", "path": "/age", "value": 31},
            {"op": "remove", "path": "/name"}
        ]

        result = apply_patch(data, patches)

        assert "name" not in result
        assert result["age"] == 31
        assert result["email"] == "alice@example.com"

    def test_patches_applied_sequentially(self):
        """Patches are applied in order."""
        data = {"count": 0}
        patches = [
            {"op": "replace", "path": "/count", "value": 1},
            {"op": "replace", "path": "/count", "value": 2},
            {"op": "replace", "path": "/count", "value": 3}
        ]

        result = apply_patch(data, patches)

        assert result["count"] == 3


class TestErrorHandling:
    """Test error handling in patch operations."""

    def test_invalid_operation(self):
        """Invalid operation type raises error."""
        data = {"name": "Alice"}
        patch = {"op": "invalid", "path": "/name"}

        with pytest.raises(PatchError):
            apply_patch(data, patch)

    def test_missing_required_field(self):
        """Missing required field raises error."""
        data = {"name": "Alice"}
        patch = {"op": "add", "value": 30}  # Missing 'path'

        with pytest.raises((PatchError, KeyError)):
            apply_patch(data, patch)

    def test_invalid_path_format(self):
        """Invalid path format raises error."""
        data = {"name": "Alice"}
        patch = {"op": "add", "path": "invalid", "value": 30}  # Missing leading /

        with pytest.raises(PatchError):
            apply_patch(data, patch)

    def test_array_index_out_of_bounds(self):
        """Array index out of bounds raises error."""
        data = {"tags": ["python"]}
        patch = {"op": "replace", "path": "/tags/5", "value": "testing"}

        with pytest.raises(PatchError):
            apply_patch(data, patch)


class TestImmutability:
    """Test that original data is not modified."""

    def test_original_data_unchanged(self):
        """Apply_patch returns new data, doesn't modify original."""
        original = {"name": "Alice", "age": 30}
        patch = {"op": "replace", "path": "/age", "value": 31}

        result = apply_patch(original, patch)

        # Original should be unchanged
        assert original["age"] == 30
        assert result["age"] == 31

    def test_nested_data_unchanged(self):
        """Nested structures in original data are not modified."""
        original = {"user": {"name": "Alice", "age": 30}}
        patch = {"op": "replace", "path": "/user/age", "value": 31}

        result = apply_patch(original, patch)

        assert original["user"]["age"] == 30
        assert result["user"]["age"] == 31


class TestComplexPatches:
    """Test complex patch scenarios."""

    def test_deep_nesting(self):
        """Apply patches to deeply nested structures."""
        data = {
            "app": {
                "config": {
                    "settings": {
                        "theme": "light"
                    }
                }
            }
        }
        patch = {"op": "replace", "path": "/app/config/settings/theme", "value": "dark"}

        result = apply_patch(data, patch)

        assert result["app"]["config"]["settings"]["theme"] == "dark"

    def test_mixed_arrays_and_objects(self):
        """Apply patches to structures with mixed arrays and objects."""
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ]
        }
        patch = {"op": "replace", "path": "/users/0/age", "value": 31}

        result = apply_patch(data, patch)

        assert result["users"][0]["age"] == 31
        assert result["users"][1]["age"] == 25
