"""Comprehensive tests for structured data extraction from LLM responses."""

import pytest

from slimschema.extract import extract_json, extract_structured_data


class TestJSONExtraction:
    """Test JSON extraction with various tagging strategies."""

    def test_json_in_xml_tag(self):
        """Test: <json>...</json>"""
        text = '<json>{"name": "Alice", "age": 30}</json>'
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data == {"name": "Alice", "age": 30}

    def test_json_in_output_tag(self):
        """Test: <output>...</output>"""
        text = '<output>{"name": "Bob", "age": 25}</output>'
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data == {"name": "Bob", "age": 25}

    def test_json_in_json_output_tag(self):
        """Test: <json_output>...</json_output>"""
        text = '<json_output>{"name": "Charlie", "age": 35}</json_output>'
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data == {"name": "Charlie", "age": 35}

    def test_json_in_output_json_tag(self):
        """Test: <output_json>...</output_json>"""
        text = '<output_json>{"name": "Dave", "age": 40}</output_json>'
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data == {"name": "Dave", "age": 40}

    def test_json_in_uppercase_tag(self):
        """Test: <JSON>...</JSON> (case insensitive)"""
        text = '<JSON>{"name": "Eve", "age": 28}</JSON>'
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data == {"name": "Eve", "age": 28}

    def test_json_in_code_fence(self):
        """Test: ```json\n...\n```"""
        text = '```json\n{"name": "Frank", "age": 33}\n```'
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data == {"name": "Frank", "age": 33}

    def test_json_in_code_fence_no_label(self):
        """Test: ```\n...\n``` (no format label)"""
        text = '```\n{"name": "Grace", "age": 27}\n```'
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data == {"name": "Grace", "age": 27}

    def test_json_in_quadruple_fence(self):
        """Test: ````json\n...\n```` (4 backticks)"""
        text = '````json\n{"name": "Henry", "age": 45}\n````'
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data == {"name": "Henry", "age": 45}

    def test_json_xml_wrapped_fence(self):
        """Test: <output>```json\n...\n```</output> (Priority 1)"""
        text = '<output>```json\n{"name": "Iris", "age": 31}\n```</output>'
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data == {"name": "Iris", "age": 31}

    def test_json_with_explanation(self):
        """Test: JSON with surrounding explanation text"""
        text = """
        Here is the user data you requested:

        ```json
        {"name": "Jack", "age": 29}
        ```

        This data was extracted from the database.
        """
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data == {"name": "Jack", "age": 29}

    def test_json_array(self):
        """Test: JSON array extraction"""
        text = '<json>[1, 2, 3, 4, 5]</json>'
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data == [1, 2, 3, 4, 5]

    def test_raw_json(self):
        """Test: Raw JSON (no tags/fences)"""
        text = '{"name": "Kate", "age": 26}'
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data == {"name": "Kate", "age": 26}

    def test_backward_compat_extract_json(self):
        """Test: Backward compatibility with extract_json()"""
        text = '```json\n{"name": "Leo", "age": 38}\n```'
        data = extract_json(text)
        assert data == {"name": "Leo", "age": 38}


class TestCSVExtraction:
    """Test CSV extraction with various formats."""

    def test_csv_in_tag(self):
        """Test: <csv>...</csv>"""
        text = """<csv>
name,age,city
Alice,30,NYC
Bob,25,LA
</csv>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "csv"
        assert len(data) == 2
        assert data[0]["name"] == "Alice"
        assert data[0]["age"] == "30"
        assert data[0]["city"] == "NYC"

    def test_csv_in_fence(self):
        """Test: ```csv\n...\n```"""
        text = """```csv
name,age,city
Charlie,35,SF
Dave,40,Seattle
```"""
        data, fmt = extract_structured_data(text)
        assert fmt == "csv"
        assert len(data) == 2
        assert data[0]["name"] == "Charlie"

    def test_csv_xml_wrapped_fence(self):
        """Test: <output>```csv\n...\n```</output>"""
        text = """<output>```csv
name,age
Eve,28
Frank,33
```</output>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "csv"
        assert len(data) == 2

    def test_csv_semicolon_delimiter(self):
        """Test: CSV with semicolon delimiter (Sniffer should detect)"""
        text = """<csv>
name;age;city
Grace;27;Boston
Henry;45;Austin
</csv>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "csv"
        assert len(data) == 2
        assert data[0]["name"] == "Grace"

    def test_csv_tab_delimiter(self):
        """Test: CSV with tab delimiter"""
        text = "<csv>\nname\tage\tcity\nIris\t31\tDenver\nJack\t29\tMiami\n</csv>"
        data, fmt = extract_structured_data(text)
        assert fmt == "csv"
        assert len(data) == 2

    def test_csv_output_tag_variation(self):
        """Test: <csv_output>...</csv_output>"""
        text = """<csv_output>
product,price
Widget,9.99
Gadget,19.99
</csv_output>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "csv"
        assert len(data) == 2


class TestXMLExtraction:
    """Test XML extraction with various formats."""

    def test_xml_in_tag(self):
        """Test: <xml>...</xml> with XML content"""
        text = """<xml>
<person>
  <name>Alice</name>
  <age>30</age>
</person>
</xml>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "xml"
        assert "person" in data

    def test_xml_in_fence(self):
        """Test: ```xml\n...\n```"""
        text = """```xml
<user>
  <name>Bob</name>
  <email>bob@example.com</email>
</user>
```"""
        data, fmt = extract_structured_data(text)
        assert fmt == "xml"
        assert "user" in data

    def test_xml_wrapped_fence(self):
        """Test: <output>```xml\n...\n```</output>"""
        text = """<output>```xml
<product>
  <name>Widget</name>
  <price>9.99</price>
</product>
```</output>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "xml"
        assert "product" in data

    def test_xml_output_tag_variation(self):
        """Test: <xml_output>...</xml_output>"""
        text = """<xml_output>
<item>
  <id>123</id>
  <name>Gadget</name>
</item>
</xml_output>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "xml"
        assert "item" in data

    def test_raw_xml(self):
        """Test: Raw XML (starts with <)"""
        text = """<root>
  <data>value</data>
</root>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "xml"
        assert "root" in data


class TestYAMLExtraction:
    """Test YAML extraction with various formats."""

    def test_yaml_in_tag(self):
        """Test: <yaml>...</yaml>"""
        text = """<yaml>
name: Alice
age: 30
city: NYC
</yaml>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "yaml"
        assert data["name"] == "Alice"
        assert data["age"] == 30

    def test_yaml_in_fence(self):
        """Test: ```yaml\n...\n```"""
        text = """```yaml
name: Bob
age: 25
hobbies:
  - reading
  - coding
```"""
        data, fmt = extract_structured_data(text)
        assert fmt == "yaml"
        assert data["name"] == "Bob"
        assert len(data["hobbies"]) == 2

    def test_yaml_wrapped_fence(self):
        """Test: <output>```yaml\n...\n```</output>"""
        text = """<output>```yaml
product:
  name: Widget
  price: 9.99
```</output>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "yaml"
        assert data["product"]["name"] == "Widget"

    def test_yml_tag(self):
        """Test: <yml>...</yml> (alternative extension)"""
        text = """<yml>
user: charlie
email: charlie@example.com
</yml>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "yaml"
        assert data["user"] == "charlie"

    def test_yaml_with_comments(self):
        """Test: YAML with comments (ruamel.yaml supports this)"""
        text = """```yaml
# User configuration
name: Dave  # Full name
age: 40     # In years
```"""
        data, fmt = extract_structured_data(text)
        assert fmt == "yaml"
        assert data["name"] == "Dave"
        assert data["age"] == 40

    def test_yaml_output_tag_variation(self):
        """Test: <yaml_output>...</yaml_output>"""
        text = """<yaml_output>
settings:
  theme: dark
  notifications: true
</yaml_output>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "yaml"
        assert data["settings"]["theme"] == "dark"


class TestPriorityOrdering:
    """Test that extraction priority is correct."""

    def test_priority_xml_wrapped_fence_over_fence(self):
        """Priority 1 (XML wrapped fence) should beat Priority 2 (fence)"""
        text = """
        <output>```json
        {"priority": 1}
        ```</output>

        ```json
        {"priority": 2}
        ```
        """
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data["priority"] == 1

    def test_priority_fence_over_xml_tag(self):
        """Priority 2 (fence) should beat Priority 3 (XML tag)"""
        text = """
        ```json
        {"priority": 2}
        ```

        <json>{"priority": 3}</json>
        """
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data["priority"] == 2

    def test_priority_xml_tag_over_raw(self):
        """Priority 3 (XML tag) should beat Priority 4 (raw)"""
        text = """
        <json>{"priority": 3}</json>

        {"priority": 4}
        """
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data["priority"] == 3


class TestEdgeCases:
    """Test edge cases and confusing scenarios."""

    def test_code_example_in_explanation(self):
        """Should ignore code examples in explanations, extract actual output"""
        text = """
        Here's how to format your output: ```json {"example": "format"} ```

        Now here's the actual data:
        <json>{"actual": "data"}</json>
        """
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data["actual"] == "data"

    def test_multiple_json_outputs(self):
        """Should return first valid output (priority ordering)"""
        text = """
        <json>{"first": 1}</json>
        <json>{"second": 2}</json>
        """
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data["first"] == 1

    def test_mixed_formats(self):
        """Should respect priority: JSON fence should beat XML tag"""
        text = """
        ```json
        {"format": "json"}
        ```

        <xml>
        <root>
          <format>xml</format>
        </root>
        </xml>
        """
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data["format"] == "json"

    def test_nested_tags_ignored(self):
        """Nested tags inside content should be ignored"""
        text = """<json>
        {"content": "<fake>not a tag</fake>"}
        </json>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert "<fake>" in data["content"]

    def test_invalid_json_returns_none(self):
        """Invalid JSON should return None"""
        text = "<json>{invalid json}</json>"
        result = extract_structured_data(text)
        assert result is None

    def test_empty_response(self):
        """Empty or whitespace-only response should return None"""
        text = "   \n\n   "
        result = extract_structured_data(text)
        assert result is None

    def test_no_structured_data(self):
        """Plain text with no structured data should return None"""
        text = "This is just plain text without any structured data."
        result = extract_structured_data(text)
        assert result is None

    def test_case_insensitive_tags(self):
        """Tags should be case insensitive"""
        test_cases = [
            '<JSON>{"a": 1}</JSON>',
            '<Json>{"a": 1}</Json>',
            '<json>{"a": 1}</json>',
            '<OUTPUT>{"a": 1}</OUTPUT>',
        ]
        for text in test_cases:
            data, fmt = extract_structured_data(text)
            assert fmt == "json"
            assert data["a"] == 1

    def test_case_insensitive_fence_labels(self):
        """Fence labels should be case insensitive"""
        test_cases = [
            '```JSON\n{"a": 1}\n```',
            '```Json\n{"a": 1}\n```',
            '```json\n{"a": 1}\n```',
        ]
        for text in test_cases:
            data, fmt = extract_structured_data(text)
            assert fmt == "json"
            assert data["a"] == 1

    def test_five_backtick_fence(self):
        """Should handle 5+ backticks"""
        text = '`````json\n{"a": 1}\n`````'
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data["a"] == 1

    def test_xml_tag_with_fence_skipped_in_priority_3(self):
        """XML tag containing fence should skip in priority 3 (caught in priority 1)"""
        text = """<output>
        ```json
        {"priority": 1}
        ```
        </output>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data["priority"] == 1


class TestJSONLSupport:
    """Test JSONL/JSON-ND format support."""

    def test_jsonl_pure_newline_delimited(self):
        """JSONL: Pure newline-delimited (no commas)"""
        text = """<json>
{"name": "Alice", "age": 30}
{"name": "Bob", "age": 25}
{"name": "Charlie", "age": 35}
</json>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["name"] == "Alice"
        assert data[1]["name"] == "Bob"

    def test_jsonl_with_commas(self):
        """JSON-ND: Comma-separated objects (already supported)"""
        text = """<json>
{"name": "Alice", "age": 30},
{"name": "Bob", "age": 25},
{"name": "Charlie", "age": 35}
</json>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert isinstance(data, list)
        assert len(data) == 3

    def test_jsonl_in_fence(self):
        """JSONL in code fence"""
        text = """```json
{"name": "Alice", "age": 30}
{"name": "Bob", "age": 25}
```"""
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert isinstance(data, list)
        assert len(data) == 2

    def test_jsonl_single_line_not_array(self):
        """Single-line JSON should not be treated as JSONL"""
        text = '<json>{"name": "Alice", "age": 30}</json>'
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert isinstance(data, dict)  # Not a list
        assert data["name"] == "Alice"


class TestFormatSpecificFeatures:
    """Test format-specific parsing features."""

    def test_csv_quoted_fields(self):
        """CSV with quoted fields should parse correctly"""
        text = """<csv>
name,description
"Widget","A useful item, with commas"
"Gadget","Another item"
</csv>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "csv"
        assert "commas" in data[0]["description"]

    def test_yaml_nested_structure(self):
        """YAML with nested structures should parse correctly"""
        text = """```yaml
user:
  name: Alice
  contact:
    email: alice@example.com
    phone: 555-1234
```"""
        data, fmt = extract_structured_data(text)
        assert fmt == "yaml"
        assert data["user"]["contact"]["email"] == "alice@example.com"

    def test_xml_attributes(self):
        """XML with attributes should parse correctly"""
        text = """<xml>
<user id="123" active="true">
  <name>Bob</name>
</user>
</xml>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "xml"
        # Note: attribute handling depends on xmltodict implementation

    def test_json_nested_objects(self):
        """JSON with deeply nested objects should parse correctly"""
        text = """<json>
{
  "level1": {
    "level2": {
      "level3": {
        "value": "deep"
      }
    }
  }
}
</json>"""
        data, fmt = extract_structured_data(text)
        assert fmt == "json"
        assert data["level1"]["level2"]["level3"]["value"] == "deep"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
