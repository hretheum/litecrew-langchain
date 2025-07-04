"""Structured outputs module for LiteCrew."""

import csv
import io
import json
import re
from dataclasses import fields, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union, get_type_hints
from xml.dom import minidom  # nosec B408 - Used for pretty printing only, not parsing untrusted input
from xml.etree import ElementTree as ET  # nosec B405 - Used for structured output, not untrusted input

import yaml


class OutputValidator:
    """Validate JSON output against a schema."""

    def __init__(self, schema: Dict[str, Any]):
        """Initialize validator with JSON schema."""
        self.schema = schema
        self._errors: List[str] = []

    def validate(self, data: Any) -> bool:
        """Validate data against schema."""
        self._errors = []
        return self._validate_value(data, self.schema, "root")

    def get_errors(self, data: Any) -> List[str]:
        """Get validation errors for data."""
        self._errors = []
        self._validate_value(data, self.schema, "root")
        return self._errors

    def _validate_value(self, value: Any, schema: Dict[str, Any], path: str) -> bool:
        """Recursively validate a value against schema."""
        schema_type = schema.get("type")

        if schema_type == "object":
            if not isinstance(value, dict):
                self._errors.append(
                    f"{path}: Expected object, got {type(value).__name__}"
                )
                return False

            # Check required properties
            required = schema.get("required", [])
            for req in required:
                if req not in value:
                    self._errors.append(f"{path}: Missing required property '{req}'")

            # Validate properties
            properties = schema.get("properties", {})
            for key, val in value.items():
                if key in properties:
                    self._validate_value(val, properties[key], f"{path}.{key}")

            return len(self._errors) == 0

        elif schema_type == "array":
            if not isinstance(value, list):
                self._errors.append(
                    f"{path}: Expected array, got {type(value).__name__}"
                )
                return False

            # Validate items
            item_schema = schema.get("items", {})
            for i, item in enumerate(value):
                self._validate_value(item, item_schema, f"{path}[{i}]")

            return len(self._errors) == 0

        elif schema_type == "string":
            if not isinstance(value, str):
                self._errors.append(
                    f"{path}: Expected string, got {type(value).__name__}"
                )
                return False

            # Check format
            if "format" in schema and schema["format"] == "email":
                if "@" not in value:
                    self._errors.append(f"{path}: Invalid email format")

            # Check enum
            if "enum" in schema and value not in schema["enum"]:
                self._errors.append(f"{path}: Value must be one of {schema['enum']}")

            return len(self._errors) == 0

        elif schema_type == "number":
            if not isinstance(value, (int, float)):
                self._errors.append(
                    f"{path}: Expected number, got {type(value).__name__}"
                )
                return False

            # Check range
            if "minimum" in schema and value < schema["minimum"]:
                self._errors.append(
                    f"{path}: Value {value} is below minimum {schema['minimum']}"
                )
            if "maximum" in schema and value > schema["maximum"]:
                self._errors.append(
                    f"{path}: Value {value} is above maximum {schema['maximum']}"
                )

            return len(self._errors) == 0

        elif schema_type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                self._errors.append(
                    f"{path}: Expected integer, got {type(value).__name__}"
                )
                return False

            # Check range
            if "minimum" in schema and value < schema["minimum"]:
                self._errors.append(
                    f"{path}: Value {value} is below minimum {schema['minimum']}"
                )

            return len(self._errors) == 0

        return True


class DataclassOutputParser:
    """Parse output to dataclass instances."""

    def __init__(self, dataclass_type: Type, auto_fix: bool = False):
        """Initialize parser with dataclass type."""
        if not is_dataclass(dataclass_type):
            raise ValueError(f"{dataclass_type} is not a dataclass")

        self.dataclass_type = dataclass_type
        self.auto_fix = auto_fix
        self._type_hints = get_type_hints(dataclass_type)

    def get_format_instructions(self) -> str:
        """Get format instructions for the LLM."""
        field_descriptions = []

        for field in fields(self.dataclass_type):
            field_type = self._type_hints.get(field.name, Any)
            field_desc = f"- {field.name}: {field_type.__name__ if hasattr(field_type, '__name__') else str(field_type)}"

            if field.default is not field.default_factory:
                field_desc += f" (optional, default: {field.default})"
            elif field.default_factory is not field.default_factory:
                field_desc += " (optional)"
            else:
                field_desc += " (required)"

            field_descriptions.append(field_desc)

        return f"""Please return a JSON object with the following fields:
{chr(10).join(field_descriptions)}

Example format:
{{
    "field1": "value1",
    "field2": 123,
    ...
}}"""

    def parse(self, text: str) -> Any:
        """Parse text output to dataclass instance."""
        try:
            # Try to parse as JSON
            data = json.loads(text)
        except json.JSONDecodeError:
            if self.auto_fix:
                # Try to fix and parse again
                fixer = OutputFixer()
                fixed_text = fixer.fix_json(text)
                data = json.loads(fixed_text)
            else:
                raise

        # Handle invalid values if auto_fix is enabled
        if self.auto_fix:
            data = self._fix_data_types(data)

        # Create dataclass instance
        return self.dataclass_type(**data)

    def _fix_data_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix data types to match dataclass fields."""
        fixed_data = {}

        for field in fields(self.dataclass_type):
            if field.name in data:
                value = data[field.name]
                field_type = self._type_hints.get(field.name, Any)

                # Handle special case for confidence_score clamping
                if field.name == "confidence_score" and isinstance(value, (int, float)):
                    if value > 1:
                        value = 1.0
                    elif value < 0:
                        value = 0.0

                # Try to convert types
                if field_type is int and isinstance(value, str):
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                elif field_type is float and isinstance(value, str):
                    try:
                        value = float(value)
                    except ValueError:
                        pass

                fixed_data[field.name] = value
            elif field.default is not field.default_factory:
                # Use default value
                fixed_data[field.name] = field.default
            elif field.default_factory is not field.default_factory:
                # Use default factory
                fixed_data[field.name] = field.default_factory()

        return fixed_data


class OutputFixer:
    """Fix common issues in output."""

    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """Initialize fixer with optional schema."""
        self.schema = schema

    def fix_json(self, text: str) -> str:
        """Fix common JSON formatting issues."""
        # Extract JSON from markdown code blocks
        if "```json" in text:
            text = self.extract_json(text)

        # Fix common issues
        fixed = text

        # Fix unquoted keys - improved regex that handles string values properly
        # First, protect already quoted keys
        import re

        # Pattern to match unquoted keys followed by colon
        # Negative lookbehind to avoid already quoted keys
        fixed = re.sub(r'(?<!["])\b(\w+)\b(?=\s*:)', r'"\1"', fixed)

        # Fix unquoted string values after keys
        # Match pattern: "key": value where value is not a number, boolean, null, or already quoted
        fixed = re.sub(r'("\w+"\s*:\s*)([A-Za-z_]\w*)(?=\s*[,}])', r'\1"\2"', fixed)

        # Fix single quotes around values
        # Replace single quotes that are value delimiters (not inside strings)
        fixed = re.sub(r"'([^']*)'(?=\s*[,}\]])", r'"\1"', fixed)

        # Fix trailing commas
        fixed = re.sub(r",\s*}", "}", fixed)
        fixed = re.sub(r",\s*\]", "]", fixed)

        # Try to fix incomplete JSON
        if fixed.count("{") > fixed.count("}"):
            fixed += "}" * (fixed.count("{") - fixed.count("}"))
        if fixed.count("[") > fixed.count("]"):
            fixed += "]" * (fixed.count("[") - fixed.count("]"))

        return fixed

    def extract_json(self, text: str) -> str:
        """Extract JSON from mixed text."""
        # Look for JSON in code blocks
        json_match = re.search(r"```(?:json)?\s*\n?({[\s\S]*?})\s*\n?```", text)
        if json_match:
            return json_match.group(1)

        # Look for JSON-like structure
        json_match = re.search(r"({[\s\S]*})", text)
        if json_match:
            return json_match.group(1)

        return text

    def fix_to_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix data to match schema."""
        if not self.schema:
            return data

        fixed = {}
        properties = self.schema.get("properties", {})

        for key, prop_schema in properties.items():
            if key in data:
                value = data[key]

                # Fix type
                if prop_schema.get("type") == "integer" and isinstance(value, str):
                    try:
                        value = int(value)
                    except ValueError:
                        value = 0

                # Fix enum
                if "enum" in prop_schema and value not in prop_schema["enum"]:
                    # Use first valid value
                    value = prop_schema["enum"][0]

                fixed[key] = value
            elif key in self.schema.get("required", []):
                # Add missing required field with default
                if prop_schema.get("type") == "string":
                    fixed[key] = ""
                elif prop_schema.get("type") == "integer":
                    fixed[key] = 0
                elif prop_schema.get("type") == "array":
                    fixed[key] = []
                elif prop_schema.get("type") == "object":
                    fixed[key] = {}

        return fixed


class OutputFormatter:
    """Format output in different formats."""

    def __init__(
        self, output_format: str = "json", custom_formatter: Optional[Any] = None
    ):
        """Initialize formatter."""
        self.output_format = output_format.lower()
        self.custom_formatter = custom_formatter

    def format(self, data: Any) -> str:
        """Format data according to specified format."""
        if self.output_format == "json":
            return json.dumps(data, indent=2)

        elif self.output_format == "yaml":
            return yaml.dump(data, default_flow_style=False)

        elif self.output_format == "csv":
            return self._format_csv(data)

        elif self.output_format == "markdown":
            return self._format_markdown(data)

        elif self.output_format == "xml":
            return self._format_xml(data)

        elif self.output_format == "custom" and self.custom_formatter:
            return self.custom_formatter(data)

        else:
            return str(data)

    def _format_csv(self, data: Any) -> str:
        """Format data as CSV."""
        if not isinstance(data, list):
            data = [data]

        if not data:
            return ""

        output = io.StringIO()

        # Get field names
        if isinstance(data[0], dict):
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        else:
            writer = csv.writer(output)
            for row in data:
                if isinstance(row, (list, tuple)):
                    writer.writerow(row)
                else:
                    writer.writerow([row])

        return output.getvalue()

    def _format_markdown(self, data: Any) -> str:
        """Format data as Markdown."""
        lines = []

        if isinstance(data, dict):
            # Title
            if "title" in data:
                lines.append(f"# {data['title']}")
                lines.append("")

            # Sections
            if "sections" in data and isinstance(data["sections"], list):
                for section in data["sections"]:
                    if isinstance(section, dict):
                        if "heading" in section:
                            lines.append(f"## {section['heading']}")
                            lines.append("")
                        if "content" in section:
                            lines.append(section["content"])
                            lines.append("")

            # Other fields
            for key, value in data.items():
                if key not in ["title", "sections"]:
                    lines.append(str(value))
                    lines.append("")
        else:
            lines.append(str(data))

        return "\n".join(lines)

    def _format_xml(self, data: Any) -> str:
        """Format data as XML."""
        root = ET.Element("root")
        self._dict_to_xml(data, root)

        # Pretty print
        xml_str = ET.tostring(root, encoding="unicode")
        dom = minidom.parseString(xml_str)  # nosec B318 - Parsing our own generated XML, not untrusted input
        return dom.toprettyxml(indent="  ").split("\n", 1)[1]  # Skip XML declaration

    def _dict_to_xml(self, data: Any, parent: ET.Element, name: str = None):
        """Convert dict to XML elements."""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    elem = ET.SubElement(parent, key)
                    self._dict_to_xml(value, elem)
                elif isinstance(value, list):
                    for item in value:
                        elem = ET.SubElement(parent, key)
                        if isinstance(item, dict):
                            self._dict_to_xml(item, elem)
                        else:
                            elem.text = str(item)
                else:
                    elem = ET.SubElement(parent, key)
                    elem.text = (
                        str(value).lower() if isinstance(value, bool) else str(value)
                    )
        else:
            parent.text = str(data)


class FileOutputHandler:
    """Handle saving outputs to files."""

    def __init__(self, base_dir: Union[str, Path], versioning: bool = False):
        """Initialize file handler."""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.versioning = versioning
        self._version_counters: Dict[str, int] = {}

    def save(
        self, data: Any, filename: Optional[str] = None, format: str = "json"
    ) -> Path:
        """Save data to file."""
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output_{timestamp}.{format}"

        # Ensure correct extension
        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix(f".{format}")

        # Handle versioning
        if self.versioning and path.stem in self._version_counters:
            self._version_counters[path.stem] += 1
            version = self._version_counters[path.stem]
            path = path.with_stem(f"{path.stem}_v{version}")
        elif self.versioning:
            self._version_counters[path.stem] = 1

        # Full path
        filepath = self.base_dir / path

        # Format data
        formatter = OutputFormatter(output_format=format)
        formatted_data = formatter.format(data)

        # Save to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(formatted_data)

        return filepath
