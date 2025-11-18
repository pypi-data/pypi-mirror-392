"""Verify all README examples work exactly as shown."""

import msgspec
from pydantic import BaseModel, Field

from slimschema import to_data, to_schema


def test_opening_example():
    """Opening example."""
    schema = """
name: str
age: 18..120
email: email
"""

    response = '<json>{"name": "Ace", "age": 30, "email": "a@g.com"}</json>'
    data, error = to_data(response, schema)

    assert error is None
    assert data == {"name": "Ace", "age": 30, "email": "a@g.com"}


def test_msgspec_dynamic():
    """msgspec dynamic."""
    schema = """
name: str
age: 18..120
email: email
tags: [str]
"""

    llm_response = '<json>{"name": "Bob", "age": 25, "email": "bob@example.com", "tags": ["python"]}</json>'
    data, error = to_data(llm_response, schema)

    assert error is None
    assert isinstance(data, dict)


def test_pydantic():
    """Pydantic example."""

    class User(BaseModel):
        username: str = Field(min_length=3, max_length=20)
        age: int = Field(ge=18, le=120)
        tags: set[str]

    schema = to_schema(User)
    yaml_str = str(schema)

    assert "# User" in yaml_str
    assert "username: str{3..20}" in yaml_str

    llm_response = '<json>{"username": "alice", "age": 30, "tags": ["python"]}</json>'
    user, error = to_data(llm_response, User)

    assert error is None
    assert isinstance(user, User)


def test_msgspec_struct():
    """msgspec Struct example."""

    class User(msgspec.Struct):
        name: str
        age: int
        groups: set[str] = set()
        email: str | None = None

    # Pass Struct directly
    response = '<json>{"name": "alice", "age": 30, "groups": ["admin"]}</json>'
    user, error = to_data(response, User)

    assert error is None
    assert isinstance(user, User)
    assert user.name == "alice"
    assert user.groups == {"admin"}

    # Convert to SlimSchema
    schema = to_schema(User)
    yaml_str = str(schema)
    assert "# User" in yaml_str
    assert "name: str" in yaml_str


def test_complete():
    """Complete example."""
    schema = r"""
# Product
name: str{3..100}
sku: /^[A-Z]{3}-\d{4}$/
price: 0.01..99999.99
status: draft | active | archived
tags: [str]
ids: {int}
in_stock: bool
metadata: obj
supplier: obj
created: datetime
updated?: datetime
"""

    response = '''<json>{
  "name": "Laptop Pro",
  "sku": "ELC-1234",
  "price": 1299.99,
  "status": "active",
  "tags": ["laptop", "computer"],
  "ids": [101, 202, 303],
  "in_stock": true,
  "metadata": {"warranty": "2 years"},
  "supplier": {"name": "TechCorp", "country": "USA"},
  "created": "2025-01-15T10:30:00"
}</json>'''

    product, error = to_data(response, schema)

    assert error is None
    assert product["supplier"]["name"] == "TechCorp"


def test_errors():
    """All error examples."""
    _, err = to_data('<json>{"name": "Al"}</json>', """
name: str
age: int
""")
    assert err == "Object missing required field `age`"

    _, err = to_data('<json>{"age": 10}</json>', "age: 18..120")
    assert "Expected `int` >= 18" in err

    _, err = to_data('<json>{"email": "bad"}</json>', "email: email")
    assert "matching regex" in err

    _, err = to_data('<json>{"user": "not-an-object"}</json>', "user: obj")
    assert "Expected `object`" in err

    _, err = to_data('<json>{}</json>', """
name: str
age: int
email: email
""")
    assert "name" in err


def test_comments():
    """Comments round-trip."""
    yaml_in = """
# User
name: str       # Full name
email: email    # Contact
age?: int
"""

    schema = to_schema(yaml_in)
    assert schema.name == "User"
    assert schema.fields[0].description == "Full name"

    yaml_out = str(schema)
    assert "# User" in yaml_out
    assert "# Full name" in yaml_out

    # Pydantic
    class Person(BaseModel):
        name: str = Field(description="Full name")
        email: str = Field(description="Contact email")

    schema2 = to_schema(Person)
    assert "# Full name" in str(schema2)
