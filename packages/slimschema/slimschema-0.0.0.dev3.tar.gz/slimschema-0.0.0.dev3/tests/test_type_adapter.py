"""TypeAdapter tests: List-based schemas at root level."""

import json

import msgspec
from pydantic import BaseModel, Field, TypeAdapter

from slimschema import to_data, to_schema

# ============================================================================
# SCHEMA DEFINITIONS
# ============================================================================

class User(BaseModel):
    """User model."""
    name: str = Field(min_length=2)
    email: str
    age: int = Field(ge=18, le=120)


class UserMsgspec(msgspec.Struct):
    """User model."""
    name: str
    email: str
    age: int


# YAML schema for list of users (root is a list)
YAML_SCHEMA = """
- # User
  name: str{2..}
  email: email
  age: 18..120
"""


# Sample data (list at root)
SAMPLE_JSON = """
<json>
[
  {"name": "Alice", "email": "alice@example.com", "age": 30},
  {"name": "Bob", "email": "bob@example.com", "age": 25},
  {"name": "Charlie", "email": "charlie@example.com", "age": 35}
]
</json>
"""

# Sample data (JSON-ND: newline-delimited with commas inside <json> tags)
SAMPLE_JSONL = """
<json>
  {"name": "Alice", "email": "alice@example.com", "age": 30},
  {"name": "Bob", "email": "bob@example.com", "age": 25},
  {"name": "Charlie", "email": "charlie@example.com", "age": 35}
</json>
"""


# ============================================================================
# TESTS
# ============================================================================

def test_pydantic_type_adapter():
    """Pydantic TypeAdapter validates list of objects."""
    # Pydantic requires TypeAdapter for root list types
    users_adapter = TypeAdapter(list[User])

    # Extract JSON
    from slimschema.extract import extract_json
    json_data = extract_json(SAMPLE_JSON)
    assert json_data is not None
    assert isinstance(json_data, list)

    # Validate with TypeAdapter
    users = users_adapter.validate_python(json_data)

    assert len(users) == 3
    assert all(isinstance(u, User) for u in users)
    assert users[0].name == "Alice"
    assert users[1].email == "bob@example.com"
    assert users[2].age == 35


def test_msgspec_list_validation():
    """msgspec validates list of Structs."""
    # msgspec handles list types natively
    from slimschema.extract import extract_json
    json_data = extract_json(SAMPLE_JSON)
    assert json_data is not None

    # Validate with msgspec
    users = msgspec.convert(json_data, type=list[UserMsgspec])

    assert len(users) == 3
    assert all(isinstance(u, UserMsgspec) for u in users)
    assert users[0].name == "Alice"
    assert users[1].email == "bob@example.com"
    assert users[2].age == 35


def test_yaml_list_schema():
    """YAML schema with list at root."""
    # For now, SlimSchema doesn't have special list-at-root syntax
    # So we validate individual items
    from slimschema.extract import extract_json
    json_data = extract_json(SAMPLE_JSON)
    assert json_data is not None
    assert isinstance(json_data, list)

    # Validate each item against the schema (without list wrapper)
    item_schema = """
# User
name: str{2..}
email: email
age: 18..120
"""

    for item_json in json_data:
        item_json_str = f"<json>{json.dumps(item_json)}</json>"
        user_data, error = to_data(item_json_str, item_schema)
        assert error is None
        assert "name" in user_data
        assert "email" in user_data
        assert "age" in user_data


def test_type_adapter_schema_conversion():
    """TypeAdapter schemas convert to SlimSchema."""
    # Get schema for User model
    user_schema = to_schema(User)

    # Verify it has the expected fields
    field_names = {f.name for f in user_schema.fields}
    assert field_names == {"name", "email", "age"}

    # Verify schema generates correctly
    schema_str = str(user_schema)
    assert "name: str" in schema_str
    assert "email: str" in schema_str
    assert "age: 18..120" in schema_str  # age range constraint present


def test_jsonl_format():
    """JSONL (newline-delimited JSON) format handling."""
    # JSONL format - each line is a separate JSON object
    jsonl_data = """
{"name": "Alice", "email": "alice@example.com", "age": 30}
{"name": "Bob", "email": "bob@example.com", "age": 25}
{"name": "Charlie", "email": "charlie@example.com", "age": 35}
"""

    # Parse JSONL
    users = []
    for line in jsonl_data.strip().split("\n"):
        json_str = f"<json>{line}</json>"
        user_data, error = to_data(json_str, User)
        assert error is None
        assert isinstance(user_data, User)
        users.append(user_data)

    assert len(users) == 3
    assert users[0].name == "Alice"
    assert users[1].email == "bob@example.com"
    assert users[2].age == 35


def test_jsonl_format_with_tags():
    """JSON-ND format with <json> tags and commas."""
    from slimschema.extract import extract_json

    content = extract_json(SAMPLE_JSONL)

    assert content is not None
    assert isinstance(content, list)
    assert len(content) == 3

    # Validate with Pydantic TypeAdapter
    users_adapter = TypeAdapter(list[User])
    users = users_adapter.validate_python(content)

    assert len(users) == 3
    assert users[0].name == "Alice"
    assert users[1].email == "bob@example.com"
    assert users[2].age == 35


def test_jsonl_pure_format():
    """Pure JSONL format (no commas, one object per line)."""
    pure_jsonl = """
<json>
{"name": "Alice", "email": "alice@example.com", "age": 30}
{"name": "Bob", "email": "bob@example.com", "age": 25}
{"name": "Charlie", "email": "charlie@example.com", "age": 35}
</json>
"""

    # Parse JSONL - each line is a separate object
    import re
    match = re.search(r"<json>(.*?)</json>", pure_jsonl, re.DOTALL)
    lines = match.group(1).strip().split("\n")

    users = []
    for line in lines:
        if line.strip():
            user_dict = json.loads(line.strip())
            user = User.model_validate(user_dict)
            users.append(user)

    assert len(users) == 3
    assert users[0].name == "Alice"
    assert users[1].email == "bob@example.com"
    assert users[2].age == 35


def test_list_validation_equivalence():
    """Same list validates correctly with Pydantic TypeAdapter and msgspec."""
    from slimschema.extract import extract_json
    json_data = extract_json(SAMPLE_JSON)

    # Validate with Pydantic TypeAdapter
    pydantic_adapter = TypeAdapter(list[User])
    pydantic_users = pydantic_adapter.validate_python(json_data)

    # Validate with msgspec
    msgspec_users = msgspec.convert(json_data, type=list[UserMsgspec])

    # Verify equivalence
    assert len(pydantic_users) == len(msgspec_users)
    for p_user, m_user in zip(pydantic_users, msgspec_users):
        assert p_user.name == m_user.name
        assert p_user.email == m_user.email
        assert p_user.age == m_user.age
