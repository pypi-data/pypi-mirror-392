"""SlimSchema: Token-efficient schema language for LLMs.

A concise, human-friendly schema format that:
- Reduces token usage by ~75% vs JSON Schema
- Supports validation, conversion, and code generation
- Integrates with Pydantic, JSON Schema, and more

Example:
    >>> from slimschema import to_schema, to_data, to_yaml
    >>> from pydantic import BaseModel
    >>>
    >>> class Person(BaseModel):
    ...     name: str
    ...     age: int
    >>>
    >>> schema = to_schema(Person)
    >>> prompt = f"Return JSON:\\n{to_yaml(schema)}"
    >>>
    >>> person, error = to_data(llm_response, Person)
    >>> if not error:
    ...     print(person.name)
"""

from .api import to_data, to_schema
from .core import Field, Schema, ValidationResult
from .extract import extract_json, validate_response
from .parser import parse_slimschema
from .validate import validate

__version__ = "0.1.0"

__all__ = [
    # Core types
    "Schema",
    "Field",
    "ValidationResult",
    # Main API
    "to_schema",
    "to_data",
    # Lower-level (rarely needed)
    "parse_slimschema",
    "extract_json",
    "validate_response",
    "validate",
]
