"""Utility functions for SlimSchema."""


def format_slim_error(errors: list[str]) -> str:
    """Format validation errors into a slim, LLM-friendly message.

    msgspec returns single errors, so this just cleans up the message.

    Args:
        errors: List of validation error messages (typically one)

    Returns:
        Single concise error string for LLM consumption

    Examples:
        >>> format_slim_error(["Field 'age' must be >= 18"])
        "age: must be >= 18"
        >>> format_slim_error(["Object missing required field `name`"])
        "Object missing required field `name`"
    """
    if not errors:
        return ""

    # msgspec returns single errors, just return the first one
    # Already clean and concise
    return errors[0]
