"""Round-trip tests: YAML ↔ Pydantic ↔ msgspec interoperability."""

import msgspec
from pydantic import BaseModel, Field, field_validator

from slimschema import to_data, to_schema

# Sample data (reused across tests)
SAMPLE_JSON = """
<json>
{
  "name": "Wireless Bluetooth Headphones",
  "sku": "WBH-2024",
  "price": 89.99,
  "status": "active",
  "tags": ["electronics", "audio"],
  "in_stock": true,
  "supplier": {
    "name": "TechCorp",
    "country": "USA"
  },
  "reviews": [
    {"rating": 5, "comment": "Great product"},
    {"rating": 4, "comment": "Good value"}
  ],
  "created": "2024-01-15T10:30:00Z"
}
</json>
"""


# ============================================================================
# SCHEMA DEFINITIONS (Pydantic, msgspec, YAML)
# ============================================================================

class Supplier(BaseModel):
    """Nested object."""
    name: str
    country: str


class Review(BaseModel):
    """Nested object in array."""
    rating: int = Field(ge=1, le=5)
    comment: str


class Product(BaseModel):
    """Product with nested objects."""
    name: str = Field(min_length=3, max_length=100)
    sku: str = Field(pattern=r"^[A-Z]{3}-\d{4}$")
    price: float = Field(ge=0.01, le=99999.99)
    status: str
    tags: list[str]
    in_stock: bool
    supplier: Supplier
    reviews: list[Review]
    created: str

    @field_validator("status")
    def validate_status(cls, v):
        if v not in ["draft", "active", "archived"]:
            raise ValueError("status must be draft, active, or archived")
        return v


class SupplierMsgspec(msgspec.Struct):
    """Nested object."""
    name: str
    country: str


class ReviewMsgspec(msgspec.Struct):
    """Nested object in array."""
    rating: int
    comment: str


class ProductMsgspec(msgspec.Struct):
    """Product with nested objects."""
    name: str
    sku: str
    price: float
    status: str
    tags: list[str]
    in_stock: bool
    supplier: SupplierMsgspec
    reviews: list[ReviewMsgspec]
    created: str


YAML_SCHEMA = r"""
# Product
name: str{3..100}
sku: /^[A-Z]{3}-\d{4}$/
price: 0.01..99999.99
status: draft | active | archived
tags: [str]
in_stock: bool
supplier: obj
reviews: [obj]
created: datetime
"""


# ============================================================================
# TESTS
# ============================================================================

def test_schema_conversions():
    """All three formats convert to equivalent SlimSchema IR."""
    yaml_schema = to_schema(YAML_SCHEMA)
    pydantic_schema = to_schema(Product)
    msgspec_schema = to_schema(ProductMsgspec)

    # Verify same field names
    yaml_fields = {f.name for f in yaml_schema.fields}
    pydantic_fields = {f.name for f in pydantic_schema.fields}
    msgspec_fields = {f.name for f in msgspec_schema.fields}

    assert yaml_fields == pydantic_fields == msgspec_fields


def test_pydantic_validation():
    """Pydantic validation with nested objects."""
    product, error = to_data(SAMPLE_JSON, Product)

    assert error is None
    assert isinstance(product, Product)
    assert product.name == "Wireless Bluetooth Headphones"
    assert isinstance(product.supplier, Supplier)
    assert product.supplier.name == "TechCorp"
    assert len(product.reviews) == 2
    assert isinstance(product.reviews[0], Review)
    assert product.reviews[0].rating == 5


def test_msgspec_validation():
    """msgspec validation with nested objects."""
    product, error = to_data(SAMPLE_JSON, ProductMsgspec)

    assert error is None
    assert isinstance(product, ProductMsgspec)
    assert product.name == "Wireless Bluetooth Headphones"
    assert isinstance(product.supplier, SupplierMsgspec)
    assert product.supplier.name == "TechCorp"
    assert len(product.reviews) == 2
    assert isinstance(product.reviews[0], ReviewMsgspec)
    assert product.reviews[0].rating == 5


def test_yaml_validation():
    """YAML schema validation with nested objects."""
    data, error = to_data(SAMPLE_JSON, YAML_SCHEMA)

    assert error is None
    assert isinstance(data, dict)
    assert data["name"] == "Wireless Bluetooth Headphones"
    assert isinstance(data["supplier"], dict)
    assert data["supplier"]["name"] == "TechCorp"
    assert isinstance(data["reviews"], list)
    assert len(data["reviews"]) == 2
    assert data["reviews"][0]["rating"] == 5


def test_pydantic_custom_validators():
    """Pydantic custom validators execute correctly."""
    invalid_json = """
    <json>
    {
      "name": "Test",
      "sku": "TST-0001",
      "price": 10.00,
      "status": "invalid_status",
      "tags": [],
      "in_stock": true,
      "supplier": {"name": "Test", "country": "US"},
      "reviews": [],
      "created": "2024-01-01T00:00:00Z"
    }
    </json>
    """

    product, error = to_data(invalid_json, Product)

    assert product is None
    assert error is not None
    assert "status" in error.lower()


def test_cross_format_data_exchange():
    """Data validated by one format works with another."""
    # Validate with Pydantic
    pydantic_instance, error = to_data(SAMPLE_JSON, Product)
    assert error is None

    # Extract dict
    pydantic_dict = pydantic_instance.model_dump()

    # Re-validate with msgspec using the dict
    import json
    json_str = f"<json>{json.dumps(pydantic_dict)}</json>"

    msgspec_instance, error = to_data(json_str, ProductMsgspec)
    assert error is None
    assert msgspec_instance.name == pydantic_instance.name

    # Re-validate with YAML
    yaml_data, error = to_data(json_str, YAML_SCHEMA)
    assert error is None
    assert yaml_data["name"] == pydantic_instance.name


def test_nested_object_validation():
    """Nested objects validate correctly."""
    product, error = to_data(SAMPLE_JSON, Product)
    assert error is None

    # Single nested object
    assert hasattr(product.supplier, "name")
    assert hasattr(product.supplier, "country")

    # List of nested objects
    assert all(hasattr(r, "rating") for r in product.reviews)
    assert all(hasattr(r, "comment") for r in product.reviews)


def test_literal_enum_roundtrip():
    """Pydantic Literal enums roundtrip correctly to pipe-delimited syntax."""
    from typing import Literal

    class Status(BaseModel):
        """Model with Literal enum."""
        state: Literal["ready", "open", "closed"]

    # Convert Pydantic → SlimSchema IR
    schema = to_schema(Status)

    # Check that the enum field is converted to pipe-delimited syntax
    state_field = next(f for f in schema.fields if f.name == "state")
    assert "|" in state_field.type, f"Expected enum syntax, got: {state_field.type}"
    assert "ready" in state_field.type
    assert "open" in state_field.type
    assert "closed" in state_field.type

    # Convert to YAML and back
    from slimschema.generator import to_yaml
    from slimschema.parser import parse_slimschema

    yaml_output = to_yaml(schema)
    schema_roundtrip = parse_slimschema(yaml_output)

    # Verify enum syntax is preserved
    state_field_rt = next(f for f in schema_roundtrip.fields if f.name == "state")
    assert state_field_rt.type == state_field.type

    # Verify validation works with enum values
    valid_json = '<json>{"state": "ready"}</json>'
    data, error = to_data(valid_json, Status)
    assert error is None
    assert data.state == "ready"

    # Verify invalid enum values are rejected
    invalid_json = '<json>{"state": "invalid"}</json>'
    data, error = to_data(invalid_json, Status)
    assert data is None
    assert error is not None
