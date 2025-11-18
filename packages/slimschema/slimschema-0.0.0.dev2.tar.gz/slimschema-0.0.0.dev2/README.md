# SlimSchema

Compact schema language and data extraction utilities for LLMs.

```python
from slimschema import to_data

schema = """
name: str
age: 18..120
email: email
"""

response = '<json>{"name": "Ace", "age": 30, "email": "a@g.com"}</json>'
data, error = to_data(response, schema)

assert error is None
assert data == {'name': 'Ace', 'age': 30, 'email': 'a@g.com'}
```

## Install

```bash
uv add slimschema
# or: pip install slimschema
```

## API

```python
to_schema(obj) -> Schema                     # YAML/Pydantic → SlimSchema
to_data(response, obj) -> (data, error)      # Validate
str(schema)                                  # SlimSchema → YAML
```

## With msgspec (Dynamic Validation)

No class definition needed. SlimSchema creates msgspec Struct dynamically:

```python
from slimschema import to_data

schema = """
name: str
age: 18..120
email: email
tags: [str]
"""

# SlimSchema creates this msgspec Struct internally:
# class DynamicStruct(msgspec.Struct):
#     name: str
#     age: Annotated[int, msgspec.Meta(ge=18, le=120)]
#     email: Annotated[str, msgspec.Meta(pattern=r"^[^@]+@...")]
#     tags: list[str]

data, error = to_data(llm_response, schema)
# Returns dict validated by msgspec (117x faster)
```

## With Pydantic

Convert models to SlimSchema, get instances back:

```python
from pydantic import BaseModel, Field
from slimschema import to_schema, to_data

class User(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    age: int = Field(ge=18, le=120)
    tags: set[str]

# Pydantic → SlimSchema YAML
schema = to_schema(User)

assert str(schema) == """# User
username: str{3..20}
age: 18..120
tags: {str}"""

# Validate → Pydantic instance
user, error = to_data(llm_response, User)
assert isinstance(user, User)
```

## With msgspec Struct

Pass msgspec Structs directly:

```python
import msgspec
from slimschema import to_data, to_schema

# Define your msgspec Struct
class User(msgspec.Struct):
    name: str
    age: int
    groups: set[str] = set()
    email: str | None = None

# Pass Struct directly - returns Struct instance
response = '<json>{"name": "alice", "age": 30, "groups": ["admin"]}</json>'
user, error = to_data(response, User)

assert error is None
assert isinstance(user, User)
assert user.name == "alice"
assert user.groups == {"admin"}

# Also works: convert to SlimSchema for prompts
schema = to_schema(User)
assert str(schema) == """# User
name: str
age: int
groups: {str}
email?: str"""
```

## Types

```yaml
# Primitives
name: str
age: int
price: float
active: bool
data: obj

# Constraints
username: str{3..20}
age: 18..120
ratio: 0.0..1.0

# Formats
email: email
url: url
birthday: date
timestamp: datetime
id: uuid

# Regex
slug: /^[a-z0-9-]+$/

# Enums
status: active | pending | done

# Collections
tags: [str]
ids: {int}

# Optional
bio?: str
```

## Complete Example

```python
from slimschema import to_data

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

response = '''
<json>
{
  "name": "Laptop Pro",
  "sku": "ELC-1234",
  "price": 1299.99,
  "status": "active",
  "tags": ["laptop", "computer"],
  "ids": [101, 202, 303],
  "in_stock": true,
  "metadata": {"warranty": "2 years"},
  "supplier": {
    "name": "TechCorp",
    "country": "USA"
  },
  "created": "2025-01-15T10:30:00"
}
</json>
'''

product, error = to_data(response, schema)

assert error is None
assert product["name"] == "Laptop Pro"
assert product["supplier"]["name"] == "TechCorp"
```

## Error Handling

Concise, LLM-friendly error messages:

```python
from slimschema import to_data

# Missing required field
_, err = to_data('<json>{"name": "Al"}</json>', """
name: str
age: int
""")
assert err == "Object missing required field `age`"

# Out of range
_, err = to_data('<json>{"age": 10}</json>', "age: 18..120")
assert "Expected `int` >= 18" in err

# Invalid email
_, err = to_data('<json>{"email": "bad"}</json>', "email: email")
assert "matching regex" in err

# Nested object error
_, err = to_data('<json>{"user": "not-an-object"}</json>', "user: obj")
assert "Expected `object`" in err

# Multiple errors (reports first)
_, err = to_data('<json>{}</json>', """
name: str
age: int
email: email
""")
assert "name" in err  # First missing field reported
```

msgspec reports one error at a time - perfect for LLM retry loops.

## JSON Extraction

Extracts from: `<json>`, `<output>`, ` ```json `, or raw JSON automatically.

## Comments (Round-Trip)

Comments flow through: **YAML ↔ SlimSchema ↔ Pydantic**

```python
from slimschema import to_schema

# YAML comments
yaml_in = """
# User
name: str       # Full name
email: email    # Contact
age?: int
"""

schema = to_schema(yaml_in)
assert schema.name == "User"
assert schema.fields[0].description == "Full name"

# Convert back
yaml_out = str(schema)
assert yaml_out == """# User
name: str       # Full name
email: email    # Contact
age?: int"""

# Pydantic descriptions → comments
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str = Field(description="Full name")
    email: str = Field(description="Contact email")

schema2 = to_schema(Person)
assert "# Full name" in str(schema2)
assert "# Contact email" in str(schema2)
```

---

## Why SlimSchema?

**Token-efficient schemas** - 5-10x smaller than JSON Schema
**Fast validation** - msgspec is 117x faster than alternatives
**LLM-friendly** - Unambiguous notation, clear constraints
**Seamless integration** - Works with Pydantic & msgspec

**For developers:** See [CLAUDE.md](CLAUDE.md) for comprehensive testing results, token economics analysis, and development guidelines.

