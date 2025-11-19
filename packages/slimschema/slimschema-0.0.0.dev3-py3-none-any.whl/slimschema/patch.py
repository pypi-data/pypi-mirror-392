"""JSON Patch (RFC 6902) support for SlimSchema.

Implements apply_patch() to mutate data using JSON Patch operations.
"""

import copy
from typing import Any, overload

# YAML schema for use in LLM prompts (compact)
PATCH_SCHEMA_YAML = """# PatchOperation
op: add | remove | replace | move | copy | test
path: str
value?: obj
from?: str"""


class PatchError(Exception):
    """Error applying a JSON Patch operation."""
    pass


def _unescape_json_pointer(token: str) -> str:
    """Unescape JSON Pointer token (RFC 6901)."""
    return token.replace("~1", "/").replace("~0", "~")


def _parse_json_pointer(path: str) -> list[str]:
    """Parse JSON Pointer path into tokens.

    Args:
        path: JSON Pointer string (e.g., "/foo/bar/0")

    Returns:
        List of token strings (array indices are converted to int later)

    Examples:
        >>> _parse_json_pointer("/foo/bar")
        ['foo', 'bar']
        >>> _parse_json_pointer("/items/0")
        ['items', '0']
        >>> _parse_json_pointer("")
        []
    """
    if path == "":
        return []

    if not path.startswith("/"):
        raise PatchError(f"Invalid JSON Pointer (must start with /): {path}")

    tokens = path[1:].split("/")
    result = []

    for token in tokens:
        unescaped = _unescape_json_pointer(token)
        result.append(unescaped)

    return result


def _get_value(data: Any, path: str) -> Any:
    """Get value at JSON Pointer path.

    Args:
        data: The data structure to navigate
        path: JSON Pointer path

    Returns:
        Value at the specified path

    Raises:
        PatchError: If path is invalid or doesn't exist
    """
    tokens = _parse_json_pointer(path)
    current = data

    for i, token in enumerate(tokens):
        if isinstance(current, dict):
            if token not in current:
                raise PatchError(f"Path not found: {path}")
            current = current[token]
        elif isinstance(current, list):
            try:
                index = int(token)
                if index < 0 or index >= len(current):
                    raise PatchError(f"Array index out of bounds: {path}")
                current = current[index]
            except ValueError:
                raise PatchError(f"Invalid array index '{token}' at {path}")
        else:
            raise PatchError(f"Cannot navigate through non-object/array at {path}")

    return current


def _set_value(data: Any, path: str, value: Any, create: bool = False) -> None:
    """Set value at JSON Pointer path (mutates data in-place).

    Args:
        data: The data structure to modify
        path: JSON Pointer path
        value: Value to set
        create: If True, create intermediate paths (for 'add'); if False, path must exist (for 'replace')

    Raises:
        PatchError: If path is invalid or doesn't exist (when create=False)
    """
    tokens = _parse_json_pointer(path)

    if not tokens:
        raise PatchError("Cannot modify root document")

    # Navigate to parent
    parent = data
    for token in tokens[:-1]:
        if isinstance(parent, dict):
            if token not in parent:
                if create:
                    parent[token] = {}
                else:
                    raise PatchError(f"Path not found: {path}")
            parent = parent[token]
        elif isinstance(parent, list):
            try:
                index = int(token)
                if index < 0 or index >= len(parent):
                    raise PatchError(f"Array index out of bounds: {path}")
                parent = parent[index]
            except ValueError:
                raise PatchError(f"Invalid array index '{token}' at {path}")
        else:
            raise PatchError(f"Cannot navigate through non-object/array at {path}")

    # Set value at final token
    final_token = tokens[-1]

    if isinstance(parent, dict):
        if not create and final_token not in parent:
            raise PatchError(f"Path not found: {path}")
        parent[final_token] = value
    elif isinstance(parent, list):
        try:
            if final_token == "-":
                # Special case: append to array
                if not create:
                    raise PatchError("Cannot use '-' with replace operation")
                parent.append(value)
            else:
                index = int(final_token)
                if create:
                    # For 'add', insert at index
                    if index < 0 or index > len(parent):
                        raise PatchError(f"Array index out of bounds: {path}")
                    parent.insert(index, value)
                else:
                    # For 'replace', set existing index
                    if index < 0 or index >= len(parent):
                        raise PatchError(f"Array index out of bounds: {path}")
                    parent[index] = value
        except ValueError:
            raise PatchError(f"Invalid array index '{final_token}' at {path}")
    else:
        raise PatchError(f"Cannot set value on non-object/array at {path}")


def _is_prefix(from_tokens: list[str], to_tokens: list[str]) -> bool:
    """Check if from_tokens is a proper prefix of to_tokens.

    Args:
        from_tokens: Source path tokens
        to_tokens: Destination path tokens

    Returns:
        True if from_tokens is a proper prefix of to_tokens

    Examples:
        >>> _is_prefix(['a'], ['a', 'b'])
        True
        >>> _is_prefix(['a', 'b'], ['a'])
        False
        >>> _is_prefix(['a'], ['a'])
        False
    """
    if len(from_tokens) >= len(to_tokens):
        return False
    return to_tokens[:len(from_tokens)] == from_tokens


def _remove_value(data: Any, path: str) -> None:
    """Remove value at JSON Pointer path (mutates data in-place).

    Args:
        data: The data structure to modify
        path: JSON Pointer path

    Raises:
        PatchError: If path is invalid or doesn't exist
    """
    tokens = _parse_json_pointer(path)

    if not tokens:
        raise PatchError("Cannot modify root document")

    # Navigate to parent
    parent = data
    for token in tokens[:-1]:
        if isinstance(parent, dict):
            if token not in parent:
                raise PatchError(f"Path not found: {path}")
            parent = parent[token]
        elif isinstance(parent, list):
            try:
                index = int(token)
                if index < 0 or index >= len(parent):
                    raise PatchError(f"Array index out of bounds: {path}")
                parent = parent[index]
            except ValueError:
                raise PatchError(f"Invalid array index '{token}' at {path}")
        else:
            raise PatchError(f"Cannot navigate through non-object/array at {path}")

    # Remove value at final token
    final_token = tokens[-1]

    if isinstance(parent, dict):
        if final_token not in parent:
            raise PatchError(f"Path not found: {path}")
        del parent[final_token]
    elif isinstance(parent, list):
        try:
            index = int(final_token)
            if index < 0 or index >= len(parent):
                raise PatchError(f"Array index out of bounds: {path}")
            parent.pop(index)
        except ValueError:
            raise PatchError(f"Invalid array index '{final_token}' at {path}")
    else:
        raise PatchError(f"Cannot remove from non-object/array at {path}")


def _apply_operation(data: Any, operation: dict) -> None:
    """Apply a single JSON Patch operation (mutates data in-place).

    Args:
        data: The data structure to modify
        operation: Patch operation dict with 'op', 'path', and optional 'value'/'from'

    Raises:
        PatchError: If operation is invalid or cannot be applied
    """
    op = operation.get("op")
    path = operation.get("path")

    if not op:
        raise PatchError("Missing 'op' field in patch operation")
    if path is None:
        raise PatchError("Missing 'path' field in patch operation")

    if op == "add":
        if "value" not in operation:
            raise PatchError("'add' operation requires 'value' field")
        _set_value(data, path, operation["value"], create=True)

    elif op == "remove":
        _remove_value(data, path)

    elif op == "replace":
        if "value" not in operation:
            raise PatchError("'replace' operation requires 'value' field")
        _set_value(data, path, operation["value"], create=False)

    elif op == "move":
        if "from" not in operation:
            raise PatchError("'move' operation requires 'from' field")
        from_path = operation["from"]

        # RFC 6902: "from" must not be a proper prefix of "path"
        from_tokens = _parse_json_pointer(from_path)
        to_tokens = _parse_json_pointer(path)
        if _is_prefix(from_tokens, to_tokens):
            raise PatchError(f"Cannot move '{from_path}' into its own child '{path}'")

        value = _get_value(data, from_path)
        _remove_value(data, from_path)
        _set_value(data, path, value, create=True)

    elif op == "copy":
        if "from" not in operation:
            raise PatchError("'copy' operation requires 'from' field")
        from_path = operation["from"]
        value = _get_value(data, from_path)
        _set_value(data, path, value, create=True)

    elif op == "test":
        if "value" not in operation:
            raise PatchError("'test' operation requires 'value' field")
        actual = _get_value(data, path)
        expected = operation["value"]
        if actual != expected:
            raise PatchError(f"Test failed at {path}: expected {expected}, got {actual}")

    else:
        raise PatchError(f"Unknown operation: {op}")


@overload
def apply_patch(data: dict | list, patch: dict) -> dict | list: ...


@overload
def apply_patch(data: dict | list, patch: list[dict]) -> dict | list: ...


def apply_patch(data: dict | list, patch: dict | list[dict]) -> dict | list:
    """Apply JSON Patch operations to data (RFC 6902).

    Args:
        data: The data to patch (dict or list)
        patch: Single patch operation (dict) or list of patch operations

    Returns:
        Patched data (new copy, original is not modified)

    Raises:
        PatchError: If patch is invalid or cannot be applied

    Examples:
        >>> data = {"name": "Bob", "age": 30}
        >>> patch = {"op": "replace", "path": "/name", "value": "Alice"}
        >>> apply_patch(data, patch)
        {'name': 'Alice', 'age': 30}

        >>> patches = [
        ...     {"op": "replace", "path": "/name", "value": "Alice"},
        ...     {"op": "add", "path": "/email", "value": "alice@example.com"}
        ... ]
        >>> apply_patch(data, patches)
        {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}
    """
    # Make a deep copy to avoid mutating original data
    result = copy.deepcopy(data)

    # Normalize patch to list
    operations = [patch] if isinstance(patch, dict) else patch

    # Validate that we have a list
    if not isinstance(operations, list):
        raise PatchError("Patch must be a dict or list of dicts")

    # Apply each operation in order
    for i, operation in enumerate(operations):
        if not isinstance(operation, dict):
            raise PatchError(f"Operation {i} is not a dict")

        try:
            _apply_operation(result, operation)
        except PatchError as e:
            raise PatchError(f"Failed to apply operation {i}: {e}")

    return result
