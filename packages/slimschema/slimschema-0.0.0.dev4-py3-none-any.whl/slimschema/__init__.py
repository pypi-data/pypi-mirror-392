"""SlimSchema - Compact schemas for LLM-generated JSON."""

from .api import to_data, to_msgspec, to_pydantic, to_schema
from .core import Field, Schema, ValidationResult
from .defaults import DefaultValueError
from .extract import extract_json, extract_structured_data, validate_response
from .generator import to_yaml
from .inference import InferenceConfig, from_data
from .parser import parse_slimschema
from .patch import PATCH_SCHEMA_YAML, PatchError, apply_patch
from .prompt import to_prompt, to_prompt_compact
from .validate import validate

__all__ = [
    # Core API
    "to_schema",
    "to_data",
    "to_yaml",
    "to_pydantic",
    "to_msgspec",
    # Inference
    "from_data",
    "InferenceConfig",
    # Extraction
    "extract_json",
    "extract_structured_data",
    "validate_response",
    "validate",
    # Prompt generation
    "to_prompt",
    "to_prompt_compact",
    # Core types
    "Schema",
    "Field",
    "ValidationResult",
    # Errors
    "DefaultValueError",
    "PatchError",
    # Parser
    "parse_slimschema",
    "extract_json",
    "validate_response",
    "validate",
    "apply_patch",
    "PATCH_SCHEMA_YAML",
]
