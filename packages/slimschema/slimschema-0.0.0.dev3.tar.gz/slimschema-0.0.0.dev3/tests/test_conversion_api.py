"""Test the public conversion API: to_schema, to_yaml, to_pydantic, to_msgspec."""

from typing import Literal

import msgspec
from pydantic import BaseModel, Field

from slimschema import to_data, to_msgspec, to_pydantic, to_schema, to_yaml


class TestToSchema:
    """Test to_schema() with all input types."""

    def test_from_yaml_string(self):
        """Convert YAML string → Schema IR."""
        yaml = """
# User
name: str
age: 18..120
"""
        schema = to_schema(yaml)
        assert schema.name == "User"
        assert len(schema.fields) == 2

    def test_from_pydantic(self):
        """Convert Pydantic model → Schema IR."""
        class User(BaseModel):
            name: str
            age: int

        schema = to_schema(User)
        assert schema.name == "User"
        assert len(schema.fields) == 2

    def test_from_msgspec(self):
        """Convert msgspec Struct → Schema IR."""
        class User(msgspec.Struct):
            name: str
            age: int

        schema = to_schema(User)
        assert schema.name == "User"
        assert len(schema.fields) == 2

    def test_from_schema_ir(self):
        """Convert Schema IR → Schema IR (passthrough)."""
        from slimschema.core import Field, Schema

        schema = Schema(fields=[Field(name="name", type="str", optional=False)])
        result = to_schema(schema)
        assert result is schema


class TestToYaml:
    """Test to_yaml() with all input types."""

    def test_from_yaml_string(self):
        """Convert YAML string → YAML string (via Schema IR)."""
        yaml = "# User\nname: str\nage: 18..120"
        schema = to_schema(yaml)
        output = to_yaml(schema)
        assert "# User" in output
        assert "name: str" in output

    def test_from_pydantic(self):
        """Convert Pydantic model → YAML."""
        class Product(BaseModel):
            name: str = Field(min_length=3, max_length=100)
            status: Literal["draft", "active", "archived"]

        schema = to_schema(Product)
        yaml = to_yaml(schema)
        assert "# Product" in yaml
        assert "name: str{3..100}" in yaml
        assert "draft | active | archived" in yaml

    def test_from_msgspec(self):
        """Convert msgspec Struct → YAML."""
        class Product(msgspec.Struct):
            name: str
            price: float

        schema = to_schema(Product)
        yaml = to_yaml(schema)
        assert "# Product" in yaml
        assert "name: str" in yaml
        assert "price: float" in yaml

    def test_from_schema_ir(self):
        """Convert Schema IR → YAML."""
        from slimschema.core import Field, Schema

        schema = Schema(
            name="User",
            fields=[Field(name="name", type="str", optional=False)]
        )
        yaml = to_yaml(schema)
        assert "# User" in yaml
        assert "name: str" in yaml


class TestToPydantic:
    """Test to_pydantic() with all input types."""

    def test_from_yaml_string(self):
        """Convert YAML string → Pydantic class."""
        yaml = """
# User
name: str{3..20}
age: 18..120
status: draft | active | archived
"""
        user_model = to_pydantic(yaml)

        # Check class name
        assert user_model.__name__ == "User"

        # Check fields exist
        assert "name" in user_model.model_fields
        assert "age" in user_model.model_fields
        assert "status" in user_model.model_fields

        # Create instance
        user = user_model(name="Alice", age=30, status="active")
        assert user.name == "Alice"
        assert user.age == 30
        assert user.status == "active"

        # Validate constraints
        try:
            user_model(name="AB", age=30, status="active")  # name too short
            assert False, "Should have raised validation error"
        except Exception:
            pass  # Expected

    def test_from_pydantic(self):
        """Convert Pydantic → Pydantic (passthrough)."""
        class User(BaseModel):
            name: str

        result = to_pydantic(User)
        assert result is User

    def test_from_msgspec(self):
        """Convert msgspec Struct → Pydantic class."""
        class Product(msgspec.Struct):
            name: str
            price: float

        product_model = to_pydantic(Product)

        assert product_model.__name__ == "Product"
        product = product_model(name="Widget", price=99.99)
        assert product.name == "Widget"

    def test_enum_validation(self):
        """Pydantic class validates enum values."""
        yaml = "status: ready | open | closed"
        status_model = to_pydantic(yaml)

        # Valid value
        obj = status_model(status="ready")
        assert obj.status == "ready"

        # Invalid value should fail
        try:
            status_model(status="invalid")
            assert False, "Should have raised validation error"
        except Exception as e:
            assert "status" in str(e).lower() or "literal" in str(e).lower()


class TestToMsgspec:
    """Test to_msgspec() with all input types."""

    def test_from_yaml_string(self):
        """Convert YAML string → msgspec Struct."""
        yaml = """
# User
name: str{3..20}
age: 18..120
status: draft | active | archived
"""
        user_struct = to_msgspec(yaml)

        # Check class name
        assert user_struct.__name__ == "User"

        # Create instance
        user = msgspec.convert(
            {"name": "Alice", "age": 30, "status": "active"},
            type=user_struct
        )
        assert user.name == "Alice"
        assert user.age == 30
        assert user.status == "active"

        # Validate constraints
        try:
            msgspec.convert(
                {"name": "AB", "age": 30, "status": "active"},  # name too short
                type=user_struct
            )
            assert False, "Should have raised validation error"
        except msgspec.ValidationError:
            pass  # Expected

    def test_from_pydantic(self):
        """Convert Pydantic → msgspec Struct."""
        class Product(BaseModel):
            name: str
            price: float

        product_struct = to_msgspec(Product)

        assert product_struct.__name__ == "Product"
        product = msgspec.convert({"name": "Widget", "price": 99.99}, type=product_struct)
        assert product.name == "Widget"

    def test_from_msgspec(self):
        """Convert msgspec → msgspec (passthrough)."""
        class User(msgspec.Struct):
            name: str

        result = to_msgspec(User)
        assert result is User

    def test_enum_validation(self):
        """msgspec Struct validates enum values."""
        yaml = "status: ready | open | closed"
        status_struct = to_msgspec(yaml)

        # Valid value
        obj = msgspec.convert({"status": "ready"}, type=status_struct)
        assert obj.status == "ready"

        # Invalid value should fail
        try:
            msgspec.convert({"status": "invalid"}, type=status_struct)
            assert False, "Should have raised validation error"
        except msgspec.ValidationError as e:
            assert "Invalid enum value" in str(e)


class TestRoundTripping:
    """Test round-trip conversions between formats."""

    def test_pydantic_yaml_pydantic(self):
        """Pydantic → YAML → Pydantic."""
        class Product(BaseModel):
            name: str = Field(min_length=3)
            status: Literal["draft", "active"]

        # Convert to YAML
        schema = to_schema(Product)
        yaml = to_yaml(schema)
        assert "draft | active" in yaml

        # Convert back to Pydantic
        product_model = to_pydantic(yaml)
        assert product_model.__name__ == "Product"

        # Validate it works
        product = product_model(name="Widget", status="active")
        assert product.status == "active"

    def test_msgspec_yaml_msgspec(self):
        """msgspec → YAML → msgspec."""
        class Product(msgspec.Struct):
            name: str
            price: float

        # Convert to YAML
        schema = to_schema(Product)
        yaml = to_yaml(schema)
        assert "name: str" in yaml

        # Convert back to msgspec
        product_struct = to_msgspec(yaml)
        assert product_struct.__name__ == "Product"

        # Validate it works
        product = msgspec.convert({"name": "Widget", "price": 99.99}, type=product_struct)
        assert product.price == 99.99

    def test_pydantic_yaml_msgspec(self):
        """Pydantic → YAML → msgspec."""
        class User(BaseModel):
            name: str
            age: int

        schema = to_schema(User)
        yaml = to_yaml(schema)
        user_struct = to_msgspec(yaml)

        user = msgspec.convert({"name": "Alice", "age": 30}, type=user_struct)
        assert user.name == "Alice"

    def test_msgspec_yaml_pydantic(self):
        """msgspec → YAML → Pydantic."""
        class User(msgspec.Struct):
            name: str
            age: int

        schema = to_schema(User)
        yaml = to_yaml(schema)
        user_model = to_pydantic(yaml)

        user = user_model(name="Alice", age=30)
        assert user.name == "Alice"


class TestIntegrationWithToData:
    """Test that new functions integrate with to_data()."""

    def test_yaml_to_pydantic_class_to_instance(self):
        """YAML → Pydantic class → validate JSON → Pydantic instance."""
        yaml = """
# Product
name: str
status: draft | active
"""
        # Create Pydantic class from YAML
        product_model = to_pydantic(yaml)

        # Use it to validate JSON
        json_response = '<json>{"name": "Widget", "status": "active"}</json>'
        product, error = to_data(json_response, product_model)

        assert error is None
        assert isinstance(product, product_model)
        assert product.name == "Widget"
        assert product.status == "active"

    def test_yaml_to_msgspec_struct_to_instance(self):
        """YAML → msgspec Struct → validate JSON → msgspec instance."""
        yaml = """
# Product
name: str
status: draft | active
"""
        # Create msgspec Struct from YAML
        product_struct = to_msgspec(yaml)

        # Use it to validate JSON
        json_response = '<json>{"name": "Widget", "status": "active"}</json>'
        product, error = to_data(json_response, product_struct)

        assert error is None
        assert isinstance(product, product_struct)
        assert product.name == "Widget"
        assert product.status == "active"
