"""Extract and validate JSON from LLM responses."""

import json
import re

from .core import Schema, ValidationResult
from .validate import validate


def extract_json(text: str) -> dict | list | None:
    """Extract JSON from LLM response text.

    Tries in order:
    1. <json> or <output> tags
    2. Code fences (```json or ```)
    3. Raw JSON

    Args:
        text: LLM response text

    Returns:
        Parsed JSON dict/list or None
    """
    # Try XML-style tags
    if match := re.search(r"<(?:json|output)>(.*?)</(?:json|output)>", text, re.DOTALL | re.IGNORECASE):
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try code fence
    if match := re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL):
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try raw JSON
    if text.strip().startswith(("{", "[")):
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

    return None


def validate_response(response: str, schema: Schema) -> ValidationResult:
    """Extract JSON from LLM response and validate against schema.

    Args:
        response: LLM response text
        schema: Schema IR

    Returns:
        ValidationResult
    """
    data = extract_json(response)

    if data is None:
        return ValidationResult(
            valid=False, data=None, errors=["No valid JSON found in response"], schema=schema
        )

    return validate(data, schema)
