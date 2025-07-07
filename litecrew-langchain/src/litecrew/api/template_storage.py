"""Template storage for saving and loading custom templates."""

import json
import os
from typing import Any, Dict, List, Optional


class TemplateStorage:
    """Storage for custom process templates."""

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize template storage."""
        self.storage_path = storage_path or os.path.join(
            os.path.expanduser("~"), ".litecrew", "templates"
        )
        os.makedirs(self.storage_path, exist_ok=True)

    def save_template(self, name: str, template_data: Dict[str, Any]) -> None:
        """Save a custom template."""
        file_path = os.path.join(self.storage_path, f"{name}.json")

        # Validate required fields
        required_fields = ["description", "agents", "tasks", "process_type"]
        for field in required_fields:
            if field not in template_data:
                raise ValueError(f"Template missing required field: {field}")

        # Add metadata
        template_data["name"] = name
        template_data["custom"] = True
        template_data["created_at"] = (
            os.path.getmtime(file_path) if os.path.exists(file_path) else None
        )

        with open(file_path, "w") as f:
            json.dump(template_data, f, indent=2)

    def load_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a custom template."""
        file_path = os.path.join(self.storage_path, f"{name}.json")

        if not os.path.exists(file_path):
            return None

        with open(file_path, "r") as f:
            return json.load(f)

    def list_custom_templates(self) -> List[Dict[str, Any]]:
        """List all custom templates."""
        templates = []

        if not os.path.exists(self.storage_path):
            return templates

        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                template_name = filename[:-5]  # Remove .json extension
                template_data = self.load_template(template_name)
                if template_data:
                    templates.append(
                        {
                            "name": template_name,
                            "description": template_data.get("description", ""),
                            "process_type": template_data.get(
                                "process_type", "sequential"
                            ),
                            "custom": True,
                        }
                    )

        return templates

    def delete_template(self, name: str) -> bool:
        """Delete a custom template."""
        file_path = os.path.join(self.storage_path, f"{name}.json")

        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def export_template(self, name: str) -> Optional[str]:
        """Export template as JSON string."""
        template_data = self.load_template(name)
        if template_data:
            return json.dumps(template_data, indent=2)
        return None

    def import_template(self, template_json: str, name: Optional[str] = None) -> str:
        """Import template from JSON string."""
        template_data = json.loads(template_json)

        # Use provided name or extract from data
        template_name = name or template_data.get("name")
        if not template_name:
            raise ValueError("Template name is required")

        # Save the template
        self.save_template(template_name, template_data)
        return template_name


# Global instance
_storage_instance: Optional[TemplateStorage] = None


def get_template_storage() -> TemplateStorage:
    """Get the global template storage instance."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = TemplateStorage()
    return _storage_instance
