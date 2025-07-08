"""Tests for template storage functionality."""

import json
import os
import tempfile
from unittest.mock import mock_open, patch

import pytest

from litecrew.api.template_storage import TemplateStorage, get_template_storage


class TestTemplateStorage:
    """Test template storage functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def storage(self, temp_dir):
        """Create a template storage instance with temp directory."""
        return TemplateStorage(temp_dir)

    @pytest.fixture
    def valid_template(self):
        """A valid template for testing."""
        return {
            "description": "Test template for development",
            "agents": [
                {
                    "role": "Developer",
                    "goal": "Write code",
                    "backstory": "Experienced developer",
                }
            ],
            "tasks": [{"description": "Implement feature", "agent": "Developer"}],
            "process_type": "sequential",
        }

    def test_init_default_path(self):
        """Test initialization with default path."""
        storage = TemplateStorage()
        expected_path = os.path.join(os.path.expanduser("~"), ".litecrew", "templates")
        assert storage.storage_path == expected_path

    def test_init_custom_path(self, temp_dir):
        """Test initialization with custom path."""
        storage = TemplateStorage(temp_dir)
        assert storage.storage_path == temp_dir

    def test_init_creates_directory(self, temp_dir):
        """Test that initialization creates the storage directory."""
        custom_path = os.path.join(temp_dir, "custom", "templates")
        storage = TemplateStorage(custom_path)
        assert os.path.exists(custom_path)
        assert storage.storage_path == custom_path

    def test_save_template_valid(self, storage, valid_template):
        """Test saving a valid template."""
        template_name = "test-template"
        storage.save_template(template_name, valid_template)

        # Check file was created
        file_path = os.path.join(storage.storage_path, f"{template_name}.json")
        assert os.path.exists(file_path)

        # Check content
        with open(file_path, "r") as f:
            saved_data = json.load(f)

        assert saved_data["name"] == template_name
        assert saved_data["custom"] is True
        assert saved_data["description"] == valid_template["description"]
        assert saved_data["agents"] == valid_template["agents"]
        assert saved_data["tasks"] == valid_template["tasks"]
        assert saved_data["process_type"] == valid_template["process_type"]

    def test_save_template_missing_description(self, storage):
        """Test saving template with missing description."""
        template_data = {"agents": [], "tasks": [], "process_type": "sequential"}

        with pytest.raises(
            ValueError, match="Template missing required field: description"
        ):
            storage.save_template("test", template_data)

    def test_save_template_missing_agents(self, storage):
        """Test saving template with missing agents."""
        template_data = {
            "description": "Test",
            "tasks": [],
            "process_type": "sequential",
        }

        with pytest.raises(ValueError, match="Template missing required field: agents"):
            storage.save_template("test", template_data)

    def test_save_template_missing_tasks(self, storage):
        """Test saving template with missing tasks."""
        template_data = {
            "description": "Test",
            "agents": [],
            "process_type": "sequential",
        }

        with pytest.raises(ValueError, match="Template missing required field: tasks"):
            storage.save_template("test", template_data)

    def test_save_template_missing_process_type(self, storage):
        """Test saving template with missing process_type."""
        template_data = {"description": "Test", "agents": [], "tasks": []}

        with pytest.raises(
            ValueError, match="Template missing required field: process_type"
        ):
            storage.save_template("test", template_data)

    def test_save_template_all_required_fields(self, storage):
        """Test that all required fields are validated."""
        required_fields = ["description", "agents", "tasks", "process_type"]

        for field in required_fields:
            # Create template missing one field
            template_data = {
                "description": "Test",
                "agents": [],
                "tasks": [],
                "process_type": "sequential",
            }
            del template_data[field]

            with pytest.raises(
                ValueError, match=f"Template missing required field: {field}"
            ):
                storage.save_template("test", template_data)

    def test_save_template_overwrites_existing(self, storage, valid_template):
        """Test that saving overwrites existing template."""
        template_name = "test-template"

        # Save first version
        storage.save_template(template_name, valid_template)

        # Save second version
        modified_template = valid_template.copy()
        modified_template["description"] = "Modified description"
        storage.save_template(template_name, modified_template)

        # Check it was overwritten
        loaded = storage.load_template(template_name)
        assert loaded["description"] == "Modified description"

    def test_load_template_exists(self, storage, valid_template):
        """Test loading an existing template."""
        template_name = "test-template"
        storage.save_template(template_name, valid_template)

        loaded = storage.load_template(template_name)
        assert loaded is not None
        assert loaded["name"] == template_name
        assert loaded["custom"] is True
        assert loaded["description"] == valid_template["description"]

    def test_load_template_not_exists(self, storage):
        """Test loading non-existent template."""
        result = storage.load_template("nonexistent")
        assert result is None

    def test_load_template_invalid_json(self, storage):
        """Test loading template with invalid JSON."""
        template_name = "invalid-template"
        file_path = os.path.join(storage.storage_path, f"{template_name}.json")

        # Create invalid JSON file
        with open(file_path, "w") as f:
            f.write("invalid json content")

        with pytest.raises(json.JSONDecodeError):
            storage.load_template(template_name)

    def test_list_custom_templates_empty(self, storage):
        """Test listing templates when none exist."""
        templates = storage.list_custom_templates()
        assert templates == []

    def test_list_custom_templates_multiple(self, storage, valid_template):
        """Test listing multiple custom templates."""
        # Save multiple templates
        templates_data = [
            ("template1", {"description": "First template", **valid_template}),
            ("template2", {"description": "Second template", **valid_template}),
            ("template3", {"description": "Third template", **valid_template}),
        ]

        for name, data in templates_data:
            storage.save_template(name, data)

        # List templates
        templates = storage.list_custom_templates()
        assert len(templates) == 3

        # Check structure
        for template in templates:
            assert "name" in template
            assert "description" in template
            assert "process_type" in template
            assert template["custom"] is True

        # Check specific templates
        names = [t["name"] for t in templates]
        assert "template1" in names
        assert "template2" in names
        assert "template3" in names

    def test_list_custom_templates_no_storage_path(self, temp_dir):
        """Test listing templates when storage path doesn't exist."""
        non_existent_path = os.path.join(temp_dir, "nonexistent")
        storage = TemplateStorage(non_existent_path)

        # Delete the directory after creation
        os.rmdir(non_existent_path)

        templates = storage.list_custom_templates()
        assert templates == []

    def test_list_custom_templates_ignores_non_json(self, storage, valid_template):
        """Test that non-JSON files are ignored."""
        # Save a template
        storage.save_template("valid-template", valid_template)

        # Create non-JSON files
        with open(os.path.join(storage.storage_path, "readme.txt"), "w") as f:
            f.write("Not a template")

        with open(os.path.join(storage.storage_path, "config.yaml"), "w") as f:
            f.write("key: value")

        templates = storage.list_custom_templates()
        assert len(templates) == 1
        assert templates[0]["name"] == "valid-template"

    def test_list_custom_templates_handles_corrupted_files(
        self, storage, valid_template
    ):
        """Test handling corrupted JSON files."""
        # Save a valid template
        storage.save_template("valid-template", valid_template)

        # Create corrupted JSON file
        with open(os.path.join(storage.storage_path, "corrupted.json"), "w") as f:
            f.write("invalid json")

        # Should only return valid templates
        templates = storage.list_custom_templates()
        assert len(templates) == 1
        assert templates[0]["name"] == "valid-template"

    def test_delete_template_exists(self, storage, valid_template):
        """Test deleting an existing template."""
        template_name = "test-template"
        storage.save_template(template_name, valid_template)

        # Verify it exists
        assert storage.load_template(template_name) is not None

        # Delete it
        result = storage.delete_template(template_name)
        assert result is True

        # Verify it's gone
        assert storage.load_template(template_name) is None

    def test_delete_template_not_exists(self, storage):
        """Test deleting non-existent template."""
        result = storage.delete_template("nonexistent")
        assert result is False

    def test_export_template_exists(self, storage, valid_template):
        """Test exporting an existing template."""
        template_name = "test-template"
        storage.save_template(template_name, valid_template)

        exported = storage.export_template(template_name)
        assert exported is not None

        # Parse the exported JSON
        parsed = json.loads(exported)
        assert parsed["name"] == template_name
        assert parsed["custom"] is True
        assert parsed["description"] == valid_template["description"]

    def test_export_template_not_exists(self, storage):
        """Test exporting non-existent template."""
        result = storage.export_template("nonexistent")
        assert result is None

    def test_export_template_formatting(self, storage, valid_template):
        """Test that exported template is properly formatted."""
        template_name = "test-template"
        storage.save_template(template_name, valid_template)

        exported = storage.export_template(template_name)

        # Should be indented (pretty-printed)
        assert "\n" in exported
        assert "  " in exported  # Indentation

    def test_import_template_with_name(self, storage, valid_template):
        """Test importing template with explicit name."""
        template_json = json.dumps(valid_template)
        template_name = "imported-template"

        result = storage.import_template(template_json, template_name)
        assert result == template_name

        # Verify it was saved
        loaded = storage.load_template(template_name)
        assert loaded is not None
        assert loaded["name"] == template_name
        assert loaded["description"] == valid_template["description"]

    def test_import_template_from_data_name(self, storage, valid_template):
        """Test importing template using name from data."""
        template_data = valid_template.copy()
        template_data["name"] = "data-template"
        template_json = json.dumps(template_data)

        result = storage.import_template(template_json)
        assert result == "data-template"

        # Verify it was saved
        loaded = storage.load_template("data-template")
        assert loaded is not None
        assert loaded["name"] == "data-template"

    def test_import_template_no_name(self, storage, valid_template):
        """Test importing template without name."""
        template_json = json.dumps(valid_template)

        with pytest.raises(ValueError, match="Template name is required"):
            storage.import_template(template_json)

    def test_import_template_invalid_json(self, storage):
        """Test importing invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            storage.import_template("invalid json")

    def test_import_template_overwrites_existing(self, storage, valid_template):
        """Test that importing overwrites existing template."""
        template_name = "test-template"

        # Save original
        storage.save_template(template_name, valid_template)

        # Import modified version
        modified_template = valid_template.copy()
        modified_template["description"] = "Imported description"
        modified_template["name"] = template_name

        result = storage.import_template(json.dumps(modified_template))
        assert result == template_name

        # Verify it was overwritten
        loaded = storage.load_template(template_name)
        assert loaded["description"] == "Imported description"

    def test_import_export_roundtrip(self, storage, valid_template):
        """Test that import/export roundtrip preserves data."""
        template_name = "roundtrip-template"
        storage.save_template(template_name, valid_template)

        # Export
        exported = storage.export_template(template_name)

        # Delete original
        storage.delete_template(template_name)

        # Import back
        imported_name = storage.import_template(exported)
        assert imported_name == template_name

        # Verify data is preserved
        loaded = storage.load_template(template_name)
        assert loaded["description"] == valid_template["description"]
        assert loaded["agents"] == valid_template["agents"]
        assert loaded["tasks"] == valid_template["tasks"]
        assert loaded["process_type"] == valid_template["process_type"]

    def test_created_at_metadata(self, storage, valid_template):
        """Test that created_at metadata is handled."""
        template_name = "metadata-template"

        # Save template
        storage.save_template(template_name, valid_template)

        # Load and check metadata
        loaded = storage.load_template(template_name)
        assert "created_at" in loaded
        # Should be None for new files in our test
        assert loaded["created_at"] is None

    def test_template_with_complex_data(self, storage):
        """Test template with complex nested data."""
        complex_template = {
            "description": "Complex template with nested data",
            "agents": [
                {
                    "role": "Manager",
                    "goal": "Oversee project",
                    "backstory": "Experienced manager",
                    "tools": ["email", "calendar"],
                    "config": {"verbose": True, "max_iterations": 5},
                }
            ],
            "tasks": [
                {
                    "description": "Complex task",
                    "agent": "Manager",
                    "context": ["previous_task"],
                    "output_file": "result.txt",
                }
            ],
            "process_type": "hierarchical",
            "config": {"max_rpm": 10, "memory": True},
        }

        template_name = "complex-template"
        storage.save_template(template_name, complex_template)

        # Load and verify
        loaded = storage.load_template(template_name)
        assert loaded["agents"][0]["tools"] == ["email", "calendar"]
        assert loaded["agents"][0]["config"]["verbose"] is True
        assert loaded["tasks"][0]["context"] == ["previous_task"]
        assert loaded["config"]["max_rpm"] == 10


class TestTemplateStorageSingleton:
    """Test template storage singleton pattern."""

    def test_get_template_storage_returns_singleton(self):
        """Test that get_template_storage returns same instance."""
        storage1 = get_template_storage()
        storage2 = get_template_storage()
        assert storage1 is storage2

    def test_singleton_preserves_state(self):
        """Test that singleton preserves state between calls."""
        storage1 = get_template_storage()

        # Mock the storage path to avoid filesystem operations
        with patch.object(storage1, "storage_path", "/tmp/test"):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch("os.path.exists", return_value=False):
                        template_data = {
                            "description": "Test",
                            "agents": [],
                            "tasks": [],
                            "process_type": "sequential",
                        }

                        # This would normally save to filesystem
                        # but we're mocking it to test singleton behavior
                        storage1.save_template("test-template", template_data)

                        # Get second reference
                        storage2 = get_template_storage()
                        assert storage1 is storage2
