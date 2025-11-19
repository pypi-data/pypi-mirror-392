"""Test examples for README - comprehensive API showcase."""

from typing import Literal

import msgspec
from pydantic import BaseModel, Field

from slimschema import from_data, to_data, to_msgspec, to_pydantic, to_schema, to_yaml


def test_complete_api_showcase():
    """Single test showcasing all 5 main API functions."""

    # ============================================================
    # 1. Define schema in YAML
    # ============================================================
    yaml_schema = """
name: str{1..100}
email: email
age: 18..120
country: str{2..2}
status: active | inactive | pending
"""

    # ============================================================
    # 2. OR define same schema with Pydantic
    # ============================================================
    class UserPydantic(BaseModel):
        name: str = Field(min_length=1, max_length=100)
        email: str
        age: int = Field(ge=18, le=120)
        country: str = Field(min_length=2, max_length=2)
        status: Literal["active", "inactive", "pending"]

    # ============================================================
    # 3. OR define same schema with msgspec
    # ============================================================
    class UserMsgspec(msgspec.Struct):
        name: str
        email: str
        age: int
        country: str
        status: Literal["active", "inactive", "pending"]

    # ============================================================
    # API FUNCTION 1: to_data() - Validate JSON responses
    # ============================================================

    # Valid JSON
    valid_json = """
<json>
{
    "name": "Alice",
    "email": "alice@example.com",
    "age": 30,
    "country": "US",
    "status": "active"
}
</json>
"""

    user, error = to_data(valid_json, yaml_schema)
    assert error is None
    assert user["name"] == "Alice"

    # Invalid JSON - shows first validation error
    invalid_json = """
{
    "name": "Bob",
    "email": "not-an-email",
    "age": 150,
    "country": "USA",
    "status": "unknown"
}
"""

    user, error = to_data(invalid_json, yaml_schema)
    assert error is not None
    assert "email" in error  # First error: bad email format

    # ============================================================
    # API FUNCTION 2: from_data() - Infer schema from examples
    # ============================================================

    # Enums detected by repetition (status has repeated values)
    examples = [
        {"name": "Alice", "status": "active"},
        {"name": "Bob", "status": "inactive"},
        {"name": "Charlie", "status": "active"},
        {"name": "Diana", "status": "inactive"},
    ]

    inferred = from_data(examples, name="User")
    yaml_output = to_yaml(inferred)

    assert "# User" in yaml_output
    assert "name: str" in yaml_output  # many unique strings stay str
    assert "active | inactive" in yaml_output  # repeated values become enum

    # ============================================================
    # API FUNCTION 3: to_schema() - Normalize any format to IR
    # ============================================================
    schema_yaml = to_schema(yaml_schema)
    schema_pydantic = to_schema(UserPydantic)
    schema_msgspec = to_schema(UserMsgspec)

    # All produce equivalent Schema IR
    assert schema_yaml.name is None  # YAML had no comment
    assert schema_pydantic.name == "UserPydantic"
    assert schema_msgspec.name == "UserMsgspec"
    assert len(schema_yaml.fields) == 5
    assert len(schema_pydantic.fields) == 5

    # ============================================================
    # API FUNCTION 4: to_pydantic() - Convert to Pydantic model
    # ============================================================
    pydantic_model = to_pydantic(yaml_schema)

    # Use it for validation
    validated = pydantic_model(
        name="Diana",
        email="diana@example.com",
        age=28,
        country="US",
        status="pending"
    )
    assert validated.name == "Diana"

    # ============================================================
    # API FUNCTION 5: to_msgspec() - Convert to msgspec Struct
    # ============================================================
    msgspec_struct = to_msgspec(yaml_schema)

    # Use it for fast validation (functional API)
    validated_msgspec = msgspec.convert({
        "name": "Eve",
        "email": "eve@example.com",
        "age": 32,
        "country": "US",
        "status": "active"
    }, type=msgspec_struct)
    assert validated_msgspec.name == "Eve"

    # ============================================================
    # BONUS: All formats are interchangeable
    # ============================================================

    # Convert between formats
    schema = to_schema(UserPydantic)
    yaml_str = to_yaml(schema)
    assert "18..120" in yaml_str
    assert "active | inactive | pending" in yaml_str


if __name__ == "__main__":
    test_complete_api_showcase()
    print("✓ All examples pass!")
