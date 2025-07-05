"""Tests for structured outputs functionality."""

import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import pytest

from litecrew.agent import Agent
from litecrew.outputs import (
    DataclassOutputParser,
    FileOutputHandler,
    OutputFixer,
    OutputFormatter,
    OutputValidator,
)


class TestDataclassOutputs:
    """Test dataclass model output parsing."""

    @dataclass
    class ResearchResult:
        """Example research result model."""

        title: str
        summary: str
        key_findings: List[str]
        confidence_score: float  # Should be between 0 and 1
        sources: Optional[List[str]] = None

        def __post_init__(self):
            """Validate confidence score."""
            if not 0 <= self.confidence_score <= 1:
                raise ValueError(
                    f"confidence_score must be between 0 and 1, got {self.confidence_score}"
                )

    def test_dataclass_parser_creation(self):
        """Test creating a dataclass output parser."""
        parser = DataclassOutputParser(dataclass_type=self.ResearchResult)

        assert parser.dataclass_type == self.ResearchResult
        assert "title" in parser.get_format_instructions()
        assert "key_findings" in parser.get_format_instructions()

    def test_parse_valid_json(self):
        """Test parsing valid JSON to dataclass model."""
        parser = DataclassOutputParser(dataclass_type=self.ResearchResult)

        valid_json = {
            "title": "AI Research 2024",
            "summary": "Latest trends in AI",
            "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
            "confidence_score": 0.85,
            "sources": ["paper1.pdf", "paper2.pdf"],
        }

        result = parser.parse(json.dumps(valid_json))

        assert isinstance(result, self.ResearchResult)
        assert result.title == "AI Research 2024"
        assert len(result.key_findings) == 3
        assert result.confidence_score == 0.85

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON."""
        parser = DataclassOutputParser(dataclass_type=self.ResearchResult)

        # Missing required field
        invalid_json = {
            "summary": "Missing title",
            "key_findings": ["Finding 1"],
            "confidence_score": 0.5,
        }

        with pytest.raises(TypeError):  # Missing required argument
            parser.parse(json.dumps(invalid_json))

    def test_parse_with_fixing(self):
        """Test parsing with automatic fixing."""
        parser = DataclassOutputParser(
            dataclass_type=self.ResearchResult, auto_fix=True
        )

        # Invalid confidence score
        invalid_json = {
            "title": "Test",
            "summary": "Test summary",
            "key_findings": ["Finding"],
            "confidence_score": 1.5,  # Out of range
        }

        result = parser.parse(json.dumps(invalid_json))
        assert result.confidence_score == 1.0  # Should be clamped to max


class TestJSONValidation:
    """Test JSON output validation."""

    def test_json_validator_creation(self):
        """Test creating JSON validator."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["name", "age"],
        }

        validator = OutputValidator(schema=schema)
        assert validator.schema == schema

    def test_validate_valid_json(self):
        """Test validating valid JSON."""
        schema = {
            "type": "object",
            "properties": {
                "result": {"type": "string"},
                "score": {"type": "number", "minimum": 0, "maximum": 100},
            },
            "required": ["result"],
        }

        validator = OutputValidator(schema=schema)

        valid_data = {"result": "success", "score": 85}
        assert validator.validate(valid_data) is True

        # Missing optional field is OK
        valid_data2 = {"result": "success"}
        assert validator.validate(valid_data2) is True

    def test_validate_invalid_json(self):
        """Test validating invalid JSON."""
        schema = {
            "type": "object",
            "properties": {"count": {"type": "integer", "minimum": 0}},
            "required": ["count"],
        }

        validator = OutputValidator(schema=schema)

        # Wrong type
        assert validator.validate({"count": "five"}) is False

        # Out of range
        assert validator.validate({"count": -5}) is False

        # Missing required field
        assert validator.validate({}) is False

    def test_get_validation_errors(self):
        """Test getting detailed validation errors."""
        schema = {
            "type": "object",
            "properties": {"email": {"type": "string", "format": "email"}},
        }

        validator = OutputValidator(schema=schema)
        invalid_data = {"email": "not-an-email"}

        errors = validator.get_errors(invalid_data)
        assert len(errors) > 0
        assert any("email" in str(e) for e in errors)


class TestOutputFixer:
    """Test automatic output fixing."""

    def test_fix_json_formatting(self):
        """Test fixing common JSON formatting issues."""
        fixer = OutputFixer()

        # Missing quotes
        broken_json = "{name: John, age: 30}"
        fixed = fixer.fix_json(broken_json)
        parsed = json.loads(fixed)
        assert parsed["name"] == "John"
        assert parsed["age"] == 30

        # Trailing commas
        broken_json2 = '{"items": ["a", "b", "c",], "count": 3,}'
        fixed2 = fixer.fix_json(broken_json2)
        parsed2 = json.loads(fixed2)
        assert len(parsed2["items"]) == 3

    def test_fix_incomplete_json(self):
        """Test fixing incomplete JSON."""
        fixer = OutputFixer()

        # Missing closing brace
        incomplete = '{"status": "running", "progress": 75'
        fixed = fixer.fix_json(incomplete)
        parsed = json.loads(fixed)
        assert parsed["status"] == "running"
        assert parsed["progress"] == 75

    def test_extract_json_from_text(self):
        """Test extracting JSON from mixed text."""
        fixer = OutputFixer()

        mixed_text = """
        Here's the analysis result:

        ```json
        {
            "sentiment": "positive",
            "score": 0.8,
            "keywords": ["AI", "innovation", "future"]
        }
        ```

        That's the final output.
        """

        extracted = fixer.extract_json(mixed_text)
        parsed = json.loads(extracted)
        assert parsed["sentiment"] == "positive"
        assert len(parsed["keywords"]) == 3

    def test_fix_with_schema(self):
        """Test fixing output to match schema."""
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["success", "failure"]},
                "count": {"type": "integer", "minimum": 0},
            },
            "required": ["status", "count"],
        }

        fixer = OutputFixer(schema=schema)

        # Invalid enum value and wrong type
        broken_data = {"status": "ok", "count": "5"}
        fixed = fixer.fix_to_schema(broken_data)

        assert fixed["status"] in ["success", "failure"]
        assert isinstance(fixed["count"], int)
        assert fixed["count"] == 5


class TestOutputFormatters:
    """Test custom output formatters."""

    def test_csv_formatter(self):
        """Test CSV output formatting."""
        formatter = OutputFormatter(output_format="csv")

        data = [
            {"name": "Alice", "age": 30, "city": "NYC"},
            {"name": "Bob", "age": 25, "city": "LA"},
            {"name": "Charlie", "age": 35, "city": "Chicago"},
        ]

        csv_output = formatter.format(data)
        lines = csv_output.strip().split("\n")

        assert len(lines) == 4  # Header + 3 data rows
        assert "name,age,city" in lines[0]
        assert "Alice,30,NYC" in lines[1]

    def test_markdown_formatter(self):
        """Test Markdown output formatting."""
        formatter = OutputFormatter(output_format="markdown")

        data = {
            "title": "Research Report",
            "sections": [
                {"heading": "Introduction", "content": "This is the intro"},
                {"heading": "Findings", "content": "Key findings here"},
            ],
            "conclusion": "Final thoughts",
        }

        md_output = formatter.format(data)

        assert "# Research Report" in md_output
        assert "## Introduction" in md_output
        assert "## Findings" in md_output
        assert "Final thoughts" in md_output

    def test_xml_formatter(self):
        """Test XML output formatting."""
        formatter = OutputFormatter(output_format="xml")

        data = {"user": {"id": 123, "name": "John Doe", "active": True}}

        xml_output = formatter.format(data)

        assert "<user>" in xml_output
        assert "<id>123</id>" in xml_output
        assert "<name>John Doe</name>" in xml_output
        assert "<active>true</active>" in xml_output

    def test_custom_formatter(self):
        """Test custom formatter function."""

        def custom_format(data):
            return f"CUSTOM: {data.get('message', 'No message')}"

        formatter = OutputFormatter(
            output_format="custom", custom_formatter=custom_format
        )

        output = formatter.format({"message": "Hello World"})
        assert output == "CUSTOM: Hello World"


class TestFileOutputHandler:
    """Test file output handling."""

    def test_save_json_output(self):
        """Test saving JSON output to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = FileOutputHandler(base_dir=tmpdir)

            data = {"result": "success", "value": 42}
            filepath = handler.save(data, filename="output.json", format="json")

            assert filepath.exists()
            assert filepath.suffix == ".json"

            # Verify content
            with open(filepath) as f:
                loaded = json.load(f)
                assert loaded["result"] == "success"
                assert loaded["value"] == 42

    def test_save_with_auto_naming(self):
        """Test saving with automatic filename generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = FileOutputHandler(base_dir=tmpdir)

            data = {"task": "analysis"}
            filepath = handler.save(data)

            assert filepath.exists()
            assert filepath.stem.startswith("output_")
            assert filepath.suffix == ".json"

    def test_save_different_formats(self):
        """Test saving in different formats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = FileOutputHandler(base_dir=tmpdir)

            data = [{"col1": "a", "col2": 1}, {"col1": "b", "col2": 2}]

            # Save as CSV
            csv_path = handler.save(data, filename="data.csv", format="csv")
            assert csv_path.suffix == ".csv"

            # Save as YAML
            yaml_path = handler.save(data, filename="data.yaml", format="yaml")
            assert yaml_path.suffix == ".yaml"

    def test_versioning(self):
        """Test file versioning when saving multiple times."""
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = FileOutputHandler(base_dir=tmpdir, versioning=True)

            # Save same filename multiple times
            path1 = handler.save({"v": 1}, filename="data.json")
            path2 = handler.save({"v": 2}, filename="data.json")
            path3 = handler.save({"v": 3}, filename="data.json")

            assert path1.stem == "data"
            assert path2.stem == "data_v2"
            assert path3.stem == "data_v3"

            # All files should exist
            assert all(p.exists() for p in [path1, path2, path3])


class TestAgentIntegration:
    """Test structured outputs integration with agents."""

    def test_agent_with_dataclass_output(self):
        """Test agent using dataclass output."""

        @dataclass
        class TaskResult:
            task_id: str
            status: str
            output: str
            metadata: dict = field(default_factory=dict)

        agent = Agent(
            role="Task Processor",
            goal="Process tasks with structured output",
            backstory="I process tasks",
            output_dataclass=TaskResult,
        )

        # Verify parser is set up
        assert hasattr(agent, "_output_parser")
        assert agent._output_parser is not None

    def test_agent_with_json_schema(self):
        """Test agent using JSON schema validation."""
        schema = {
            "type": "object",
            "properties": {"analysis": {"type": "string"}, "score": {"type": "number"}},
            "required": ["analysis"],
        }

        agent = Agent(
            role="Analyst",
            goal="Analyze with structured output",
            backstory="I analyze data",
            output_schema=schema,
        )

        # Verify validator is set up
        assert hasattr(agent, "_output_validator")
        assert agent._output_validator is not None

    def test_agent_output_file_saving(self):
        """Test agent saving outputs to files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = Agent(
                role="Reporter",
                goal="Generate reports",
                backstory="I create reports",
                output_dir=tmpdir,
                save_outputs=True,
            )

            # Verify file handler is set up
            assert hasattr(agent, "_file_handler")
            assert agent._file_handler is not None
            assert agent._file_handler.base_dir == Path(tmpdir)


def test_output_validation_metrics():
    """Test output validation success metrics."""
    validator = OutputValidator(
        schema={
            "type": "object",
            "properties": {"result": {"type": "string"}},
            "required": ["result"],
        }
    )

    # Test 100 validations
    success_count = 0
    for i in range(100):
        if i < 95:  # 95% should be valid
            data = {"result": f"success_{i}"}
        else:  # 5% invalid
            data = {"wrong_field": "value"}

        if validator.validate(data):
            success_count += 1

    success_rate = success_count / 100
    assert success_rate >= 0.95  # JSON parsing success: >95%


def test_dataclass_validation_success():
    """Test dataclass validation success rate."""

    @dataclass
    class SimpleModel:
        name: str
        value: int

    parser = DataclassOutputParser(dataclass_type=SimpleModel)

    success_count = 0
    total_attempts = 100

    for i in range(total_attempts):
        try:
            # All should be valid
            data = {"name": f"item_{i}", "value": i}
            result = parser.parse(json.dumps(data))
            if isinstance(result, SimpleModel):
                success_count += 1
        except Exception:
            pass

    assert success_count == total_attempts  # Dataclass validation: 100%


def test_output_fixing_success():
    """Test automatic output fixing success rate."""
    fixer = OutputFixer()

    test_cases = [
        '{name: "John", age: 30}',  # Missing quotes
        '{"items": ["a", "b",], }',  # Trailing commas
        '{"status": "ok"',  # Missing closing brace
        "{'single': 'quotes'}",  # Single quotes
        '{"number": 42, }',  # Trailing comma
    ]

    fixed_count = 0
    for broken_json in test_cases:
        try:
            fixed = fixer.fix_json(broken_json)
            json.loads(fixed)  # Verify it's valid JSON
            fixed_count += 1
        except Exception:
            pass

    success_rate = fixed_count / len(test_cases)
    assert success_rate >= 0.8  # Output fixing success: >80%
