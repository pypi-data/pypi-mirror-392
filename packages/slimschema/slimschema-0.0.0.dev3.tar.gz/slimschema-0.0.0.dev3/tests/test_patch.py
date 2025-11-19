"""Tests for JSON Patch functionality (RFC 6902)."""

import pytest

from slimschema import PatchError, apply_patch


class TestBasicOperations:
    """Test basic patch operations."""

    def test_replace_simple_field(self):
        """Test replacing a simple field value."""
        data = {"name": "Bob", "age": 30}
        patch = {"op": "replace", "path": "/name", "value": "Alice"}
        result = apply_patch(data, patch)

        assert result == {"name": "Alice", "age": 30}
        # Original data unchanged
        assert data == {"name": "Bob", "age": 30}

    def test_replace_nested_field(self):
        """Test replacing a nested field value."""
        data = {"user": {"name": "Bob", "age": 30}}
        patch = {"op": "replace", "path": "/user/name", "value": "Alice"}
        result = apply_patch(data, patch)

        assert result == {"user": {"name": "Alice", "age": 30}}

    def test_add_new_field(self):
        """Test adding a new field."""
        data = {"name": "Alice"}
        patch = {"op": "add", "path": "/email", "value": "alice@example.com"}
        result = apply_patch(data, patch)

        assert result == {"name": "Alice", "email": "alice@example.com"}

    def test_add_nested_field(self):
        """Test adding a nested field."""
        data = {"user": {"name": "Alice"}}
        patch = {"op": "add", "path": "/user/email", "value": "alice@example.com"}
        result = apply_patch(data, patch)

        assert result == {"user": {"name": "Alice", "email": "alice@example.com"}}

    def test_remove_field(self):
        """Test removing a field."""
        data = {"name": "Alice", "email": "alice@example.com", "age": 30}
        patch = {"op": "remove", "path": "/email"}
        result = apply_patch(data, patch)

        assert result == {"name": "Alice", "age": 30}

    def test_remove_nested_field(self):
        """Test removing a nested field."""
        data = {"user": {"name": "Alice", "email": "alice@example.com"}}
        patch = {"op": "remove", "path": "/user/email"}
        result = apply_patch(data, patch)

        assert result == {"user": {"name": "Alice"}}


class TestArrayOperations:
    """Test array-specific operations."""

    def test_append_to_array(self):
        """Test appending to an array using '-' notation."""
        data = {"tags": ["user", "beta"]}
        patch = {"op": "add", "path": "/tags/-", "value": "admin"}
        result = apply_patch(data, patch)

        assert result == {"tags": ["user", "beta", "admin"]}

    def test_insert_at_index(self):
        """Test inserting at a specific array index."""
        data = {"tags": ["user", "beta"]}
        patch = {"op": "add", "path": "/tags/1", "value": "pro"}
        result = apply_patch(data, patch)

        assert result == {"tags": ["user", "pro", "beta"]}

    def test_replace_array_element(self):
        """Test replacing an array element."""
        data = {"tags": ["user", "beta"]}
        patch = {"op": "replace", "path": "/tags/0", "value": "admin"}
        result = apply_patch(data, patch)

        assert result == {"tags": ["admin", "beta"]}

    def test_remove_array_element(self):
        """Test removing an array element."""
        data = {"tags": ["user", "beta", "admin"]}
        patch = {"op": "remove", "path": "/tags/1"}
        result = apply_patch(data, patch)

        assert result == {"tags": ["user", "admin"]}

    def test_nested_array_operations(self):
        """Test operations on nested arrays."""
        data = {"items": [{"name": "item1"}, {"name": "item2"}]}
        patch = {"op": "replace", "path": "/items/0/name", "value": "updated"}
        result = apply_patch(data, patch)

        assert result == {"items": [{"name": "updated"}, {"name": "item2"}]}


class TestMoveAndCopy:
    """Test move and copy operations."""

    def test_move_field(self):
        """Test moving a field (effectively renaming)."""
        data = {"oldName": "value", "other": "data"}
        patch = {"op": "move", "from": "/oldName", "path": "/newName"}
        result = apply_patch(data, patch)

        assert result == {"newName": "value", "other": "data"}
        assert "oldName" not in result

    def test_move_nested_field(self):
        """Test moving a nested field."""
        data = {"settings": {"theme": "light"}, "config": {}}
        patch = {"op": "move", "from": "/settings/theme", "path": "/config/displayTheme"}
        result = apply_patch(data, patch)

        assert result == {"settings": {}, "config": {"displayTheme": "light"}}

    def test_move_array_element(self):
        """Test moving an array element."""
        data = {"tags": ["a", "b", "c"]}
        patch = {"op": "move", "from": "/tags/0", "path": "/tags/2"}
        result = apply_patch(data, patch)

        # Element 0 is removed first, then inserted at position 2
        # After removing 'a': ["b", "c"]
        # After inserting at 2: ["b", "c", "a"]
        assert result == {"tags": ["b", "c", "a"]}

    def test_copy_field(self):
        """Test copying a field."""
        data = {"original": "value"}
        patch = {"op": "copy", "from": "/original", "path": "/duplicate"}
        result = apply_patch(data, patch)

        assert result == {"original": "value", "duplicate": "value"}

    def test_copy_nested_object(self):
        """Test copying a nested object."""
        data = {"settings": {"theme": "light", "notifications": True}}
        patch = {"op": "copy", "from": "/settings", "path": "/backup"}
        result = apply_patch(data, patch)

        assert result["settings"] == result["backup"]
        assert result["backup"] == {"theme": "light", "notifications": True}

    def test_move_into_own_child_forbidden(self):
        """Test that moving a location into its own child is forbidden (RFC 6902)."""
        data = {"a": {"b": {"c": 1}}}
        patch = {"op": "move", "from": "/a", "path": "/a/b/d"}

        with pytest.raises(PatchError, match="Cannot move .* into its own child"):
            apply_patch(data, patch)

    def test_move_into_same_level_allowed(self):
        """Test that moving to same level is allowed."""
        data = {"a": {"b": 1}, "x": {}}
        patch = {"op": "move", "from": "/a", "path": "/x/a"}
        result = apply_patch(data, patch)

        assert result == {"x": {"a": {"b": 1}}}
        assert "a" not in result


class TestTestOperation:
    """Test the 'test' operation."""

    def test_test_passes(self):
        """Test that 'test' operation passes when value matches."""
        data = {"name": "Alice", "age": 30}
        patch = {"op": "test", "path": "/name", "value": "Alice"}
        result = apply_patch(data, patch)

        # Data unchanged when test passes
        assert result == data

    def test_test_fails(self):
        """Test that 'test' operation fails when value doesn't match."""
        data = {"name": "Alice", "age": 30}
        patch = {"op": "test", "path": "/name", "value": "Bob"}

        with pytest.raises(PatchError, match="Test failed"):
            apply_patch(data, patch)

    def test_test_with_subsequent_operations(self):
        """Test using 'test' as a guard for subsequent operations."""
        data = {"settings": {"notifications": True}}
        patches = [
            {"op": "test", "path": "/settings/notifications", "value": True},
            {"op": "copy", "from": "/settings/notifications", "path": "/settings/emailNotifications"}
        ]
        result = apply_patch(data, patches)

        assert result["settings"]["emailNotifications"] is True


class TestMultiplePatches:
    """Test applying multiple patches in sequence."""

    def test_sequential_patches(self):
        """Test applying multiple patches in order."""
        data = {"name": "Bob", "age": 30, "tags": ["user"]}
        patches = [
            {"op": "replace", "path": "/name", "value": "Alice"},
            {"op": "add", "path": "/email", "value": "alice@example.com"},
            {"op": "add", "path": "/tags/-", "value": "admin"},
            {"op": "remove", "path": "/age"}
        ]
        result = apply_patch(data, patches)

        assert result == {
            "name": "Alice",
            "email": "alice@example.com",
            "tags": ["user", "admin"]
        }

    def test_patch_order_matters(self):
        """Test that patch order affects the result."""
        data = {"value": 1}

        # First scenario: move then modify
        patches1 = [
            {"op": "move", "from": "/value", "path": "/oldValue"},
            {"op": "add", "path": "/value", "value": 2}
        ]
        result1 = apply_patch(data, patches1)
        assert result1 == {"oldValue": 1, "value": 2}

        # Second scenario: modify then move (different result)
        patches2 = [
            {"op": "replace", "path": "/value", "value": 2},
            {"op": "move", "from": "/value", "path": "/oldValue"}
        ]
        result2 = apply_patch(data, patches2)
        assert result2 == {"oldValue": 2}

    def test_empty_patch_list(self):
        """Test applying an empty list of patches."""
        data = {"name": "Alice"}
        result = apply_patch(data, [])

        assert result == data


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_path_format(self):
        """Test that invalid path format raises error."""
        data = {"name": "Alice"}
        patch = {"op": "replace", "path": "name", "value": "Bob"}  # Missing leading /

        with pytest.raises(PatchError, match="must start with /"):
            apply_patch(data, patch)

    def test_missing_op_field(self):
        """Test that missing 'op' field raises error."""
        data = {"name": "Alice"}
        patch = {"path": "/name", "value": "Bob"}

        with pytest.raises(PatchError, match="Missing 'op' field"):
            apply_patch(data, patch)

    def test_missing_path_field(self):
        """Test that missing 'path' field raises error."""
        data = {"name": "Alice"}
        patch = {"op": "replace", "value": "Bob"}

        with pytest.raises(PatchError, match="Missing 'path' field"):
            apply_patch(data, patch)

    def test_missing_value_for_add(self):
        """Test that 'add' without 'value' raises error."""
        data = {"name": "Alice"}
        patch = {"op": "add", "path": "/age"}

        with pytest.raises(PatchError, match="requires 'value' field"):
            apply_patch(data, patch)

    def test_missing_value_for_replace(self):
        """Test that 'replace' without 'value' raises error."""
        data = {"name": "Alice"}
        patch = {"op": "replace", "path": "/name"}

        with pytest.raises(PatchError, match="requires 'value' field"):
            apply_patch(data, patch)

    def test_missing_from_for_move(self):
        """Test that 'move' without 'from' raises error."""
        data = {"name": "Alice"}
        patch = {"op": "move", "path": "/newName"}

        with pytest.raises(PatchError, match="requires 'from' field"):
            apply_patch(data, patch)

    def test_missing_from_for_copy(self):
        """Test that 'copy' without 'from' raises error."""
        data = {"name": "Alice"}
        patch = {"op": "copy", "path": "/duplicate"}

        with pytest.raises(PatchError, match="requires 'from' field"):
            apply_patch(data, patch)

    def test_path_not_found(self):
        """Test that operating on non-existent path raises error."""
        data = {"name": "Alice"}
        patch = {"op": "replace", "path": "/age", "value": 30}

        with pytest.raises(PatchError, match="Path not found"):
            apply_patch(data, patch)

    def test_array_index_out_of_bounds(self):
        """Test that out-of-bounds array index raises error."""
        data = {"tags": ["a", "b"]}
        patch = {"op": "replace", "path": "/tags/5", "value": "c"}

        with pytest.raises(PatchError, match="out of bounds"):
            apply_patch(data, patch)

    def test_invalid_array_index(self):
        """Test that non-numeric array index raises error."""
        data = {"tags": ["a", "b"]}
        patch = {"op": "replace", "path": "/tags/invalid", "value": "c"}

        with pytest.raises(PatchError, match="Invalid array index"):
            apply_patch(data, patch)

    def test_unknown_operation(self):
        """Test that unknown operation raises error."""
        data = {"name": "Alice"}
        patch = {"op": "unknown", "path": "/name", "value": "Bob"}

        with pytest.raises(PatchError, match="Unknown operation"):
            apply_patch(data, patch)

    def test_cannot_remove_root(self):
        """Test that removing root document raises error."""
        data = {"name": "Alice"}
        patch = {"op": "remove", "path": ""}

        with pytest.raises(PatchError, match="Cannot modify root"):
            apply_patch(data, patch)

    def test_cannot_replace_root(self):
        """Test that replacing root document raises error."""
        data = {"name": "Alice"}
        patch = {"op": "replace", "path": "", "value": {"name": "Bob"}}

        with pytest.raises(PatchError, match="Cannot modify root"):
            apply_patch(data, patch)

    def test_patch_not_dict_or_list(self):
        """Test that invalid patch type raises error."""
        data = {"name": "Alice"}

        with pytest.raises(PatchError, match="must be a dict or list"):
            apply_patch(data, "invalid")

    def test_patch_list_contains_non_dict(self):
        """Test that patch list containing non-dict raises error."""
        data = {"name": "Alice"}
        patches = [
            {"op": "replace", "path": "/name", "value": "Bob"},
            "invalid"
        ]

        with pytest.raises(PatchError, match="not a dict"):
            apply_patch(data, patches)

    def test_partial_failure_does_not_modify_original(self):
        """Test that failed patch doesn't modify original data."""
        data = {"name": "Alice", "age": 30}
        patches = [
            {"op": "replace", "path": "/name", "value": "Bob"},
            {"op": "replace", "path": "/invalid", "value": "fail"}  # This will fail
        ]

        with pytest.raises(PatchError):
            apply_patch(data, patches)

        # Original data should be unchanged
        assert data == {"name": "Alice", "age": 30}


class TestJSONPointerEscaping:
    """Test JSON Pointer escaping rules (~ and /)."""

    def test_escaped_tilde(self):
        """Test handling of escaped tilde (~0 -> ~)."""
        data = {"a~b": "value"}
        patch = {"op": "replace", "path": "/a~0b", "value": "new"}
        result = apply_patch(data, patch)

        assert result == {"a~b": "new"}

    def test_escaped_slash(self):
        """Test handling of escaped slash (~1 -> /)."""
        data = {"a/b": "value"}
        patch = {"op": "replace", "path": "/a~1b", "value": "new"}
        result = apply_patch(data, patch)

        assert result == {"a/b": "new"}

    def test_combined_escaping(self):
        """Test combined tilde and slash escaping."""
        data = {"a~/b": "value"}
        patch = {"op": "replace", "path": "/a~0~1b", "value": "new"}
        result = apply_patch(data, patch)

        assert result == {"a~/b": "new"}


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_user_settings_update(self):
        """Test updating user settings (realistic scenario)."""
        data = {
            "user": {
                "name": "Alice",
                "settings": {
                    "theme": "light",
                    "notifications": True
                },
                "tags": ["user", "beta"]
            }
        }

        patches = [
            {"op": "replace", "path": "/user/settings/theme", "value": "dark"},
            {"op": "add", "path": "/user/settings/language", "value": "en-US"},
            {"op": "add", "path": "/user/tags/-", "value": "admin"},
            {"op": "remove", "path": "/user/tags/1"}  # Remove "beta"
        ]

        result = apply_patch(data, patches)

        assert result == {
            "user": {
                "name": "Alice",
                "settings": {
                    "theme": "dark",
                    "notifications": True,
                    "language": "en-US"
                },
                "tags": ["user", "admin"]
            }
        }

    def test_data_migration(self):
        """Test data migration scenario using move operations."""
        data = {
            "deprecated_field": "value1",
            "old_name": "value2",
            "current": "value3"
        }

        patches = [
            {"op": "move", "from": "/deprecated_field", "path": "/new_field"},
            {"op": "move", "from": "/old_name", "path": "/new_name"},
        ]

        result = apply_patch(data, patches)

        assert result == {
            "new_field": "value1",
            "new_name": "value2",
            "current": "value3"
        }
        assert "deprecated_field" not in result
        assert "old_name" not in result

    def test_conditional_update_with_test(self):
        """Test conditional update using test operation."""
        data = {
            "version": 1,
            "config": {"feature_x": False}
        }

        # Only update if version is 1
        patches = [
            {"op": "test", "path": "/version", "value": 1},
            {"op": "replace", "path": "/version", "value": 2},
            {"op": "replace", "path": "/config/feature_x", "value": True}
        ]

        result = apply_patch(data, patches)

        assert result["version"] == 2
        assert result["config"]["feature_x"] is True

    def test_deep_nested_structure(self):
        """Test operations on deeply nested structures."""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "value": "deep"
                        }
                    }
                }
            }
        }

        patch = {"op": "replace", "path": "/level1/level2/level3/level4/value", "value": "updated"}
        result = apply_patch(data, patch)

        assert result["level1"]["level2"]["level3"]["level4"]["value"] == "updated"


class TestRootPathHandling:
    """Test handling of root path ('')."""

    def test_get_root_value(self):
        """Test getting value at root path."""
        data = {"name": "Alice"}
        patch = {"op": "test", "path": "", "value": {"name": "Alice"}}
        result = apply_patch(data, patch)

        assert result == data

    def test_add_to_root_object(self):
        """Test adding fields to root object."""
        data = {"existing": "value"}
        patch = {"op": "add", "path": "/new", "value": "added"}
        result = apply_patch(data, patch)

        assert result == {"existing": "value", "new": "added"}


class TestListDataPatching:
    """Test patching list data (not just objects)."""

    def test_patch_list_root(self):
        """Test patching operations on a list at root."""
        data = [1, 2, 3]
        patch = {"op": "add", "path": "/-", "value": 4}
        result = apply_patch(data, patch)

        assert result == [1, 2, 3, 4]

    def test_replace_list_element(self):
        """Test replacing list element at root."""
        data = [1, 2, 3]
        patch = {"op": "replace", "path": "/1", "value": 10}
        result = apply_patch(data, patch)

        assert result == [1, 10, 3]

    def test_remove_from_list_root(self):
        """Test removing from list at root."""
        data = [1, 2, 3]
        patch = {"op": "remove", "path": "/1"}
        result = apply_patch(data, patch)

        assert result == [1, 3]


class TestAdditionalEdgeCases:
    """Test additional edge cases for complete coverage."""

    def test_navigate_through_non_object_or_array(self):
        """Test error when trying to navigate through primitive values."""
        data = {"field": {"nested": "string_value"}}
        # Try to navigate through "nested" (a string) to get to "deeper"
        patch = {"op": "replace", "path": "/field/nested/deeper/value", "value": "new"}

        with pytest.raises(PatchError, match="Cannot navigate through non-object/array"):
            apply_patch(data, patch)

    def test_set_on_non_object_or_array(self):
        """Test error when trying to set value on primitive."""
        data = {"value": 42}
        patch = {"op": "add", "path": "/value/subfield", "value": "new"}

        with pytest.raises(PatchError, match="Cannot set value on non-object/array"):
            apply_patch(data, patch)

    def test_remove_from_non_object_or_array(self):
        """Test error when trying to remove from primitive."""
        data = {"value": 42}
        patch = {"op": "remove", "path": "/value/subfield"}

        with pytest.raises(PatchError, match="Cannot remove from non-object/array"):
            apply_patch(data, patch)

    def test_add_with_dash_on_replace(self):
        """Test that '-' cannot be used with replace operation."""
        data = {"items": [1, 2, 3]}
        patch = {"op": "replace", "path": "/items/-", "value": 4}

        with pytest.raises(PatchError, match="Cannot use '-' with replace"):
            apply_patch(data, patch)

    def test_add_at_invalid_insert_position(self):
        """Test adding at invalid array position."""
        data = {"items": [1, 2, 3]}
        # Try to insert at position 10 (out of bounds for insert)
        patch = {"op": "add", "path": "/items/10", "value": 4}

        with pytest.raises(PatchError, match="out of bounds"):
            apply_patch(data, patch)

    def test_add_at_negative_index(self):
        """Test adding at negative array index."""
        data = {"items": [1, 2, 3]}
        patch = {"op": "add", "path": "/items/-1", "value": 4}

        with pytest.raises(PatchError, match="out of bounds"):
            apply_patch(data, patch)

    def test_move_from_non_existent_path(self):
        """Test moving from a path that doesn't exist."""
        data = {"field": "value"}
        patch = {"op": "move", "from": "/nonexistent", "path": "/destination"}

        with pytest.raises(PatchError, match="Path not found"):
            apply_patch(data, patch)

    def test_copy_from_non_existent_path(self):
        """Test copying from a path that doesn't exist."""
        data = {"field": "value"}
        patch = {"op": "copy", "from": "/nonexistent", "path": "/destination"}

        with pytest.raises(PatchError, match="Path not found"):
            apply_patch(data, patch)

    def test_test_on_non_existent_path(self):
        """Test 'test' operation on a path that doesn't exist."""
        data = {"field": "value"}
        patch = {"op": "test", "path": "/nonexistent", "value": "expected"}

        with pytest.raises(PatchError, match="Path not found"):
            apply_patch(data, patch)

    def test_replace_missing_field_in_object(self):
        """Test replacing a field that doesn't exist in object."""
        data = {"existing": "value"}
        patch = {"op": "replace", "path": "/missing", "value": "new"}

        with pytest.raises(PatchError, match="Path not found"):
            apply_patch(data, patch)

    def test_remove_missing_field_in_object(self):
        """Test removing a field that doesn't exist in object."""
        data = {"existing": "value"}
        patch = {"op": "remove", "path": "/missing"}

        with pytest.raises(PatchError, match="Path not found"):
            apply_patch(data, patch)

    def test_get_value_with_out_of_bounds_index(self):
        """Test getting value with out of bounds index."""
        data = {"items": [1, 2, 3]}
        patch = {"op": "test", "path": "/items/10", "value": 1}

        with pytest.raises(PatchError, match="out of bounds"):
            apply_patch(data, patch)

    def test_get_value_with_negative_index(self):
        """Test getting value with negative index."""
        data = {"items": [1, 2, 3]}
        patch = {"op": "test", "path": "/items/-1", "value": 1}

        with pytest.raises(PatchError, match="out of bounds"):
            apply_patch(data, patch)

    def test_remove_with_out_of_bounds_index(self):
        """Test removing with out of bounds index."""
        data = {"items": [1, 2, 3]}
        patch = {"op": "remove", "path": "/items/10"}

        with pytest.raises(PatchError, match="out of bounds"):
            apply_patch(data, patch)

    def test_remove_with_negative_index(self):
        """Test removing with negative index."""
        data = {"items": [1, 2, 3]}
        patch = {"op": "remove", "path": "/items/-1"}

        with pytest.raises(PatchError, match="out of bounds"):
            apply_patch(data, patch)

    def test_set_with_intermediate_creation(self):
        """Test adding with intermediate path creation."""
        data = {"root": {}}
        patch = {"op": "add", "path": "/root/nested/deep", "value": "value"}

        # This should create intermediate paths
        result = apply_patch(data, patch)
        assert result == {"root": {"nested": {"deep": "value"}}}

    def test_complex_types_in_values(self):
        """Test patching with complex data types as values."""
        data = {"simple": "value"}

        # Add nested object
        patch1 = {"op": "add", "path": "/complex", "value": {"nested": {"deep": [1, 2, 3]}}}
        result = apply_patch(data, patch1)
        assert result["complex"]["nested"]["deep"] == [1, 2, 3]

        # Replace with array
        patch2 = {"op": "replace", "path": "/complex", "value": [1, 2, 3]}
        result2 = apply_patch(result, patch2)
        assert result2["complex"] == [1, 2, 3]
