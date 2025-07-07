"""Additional tests for API templates to increase coverage."""

import pytest
from unittest.mock import MagicMock, patch
from litecrew.api.templates import ProcessTemplates


class TestProcessTemplatesCoverage:
    """Additional tests for template functionality."""

    def test_template_validation(self):
        """Test template validation logic."""
        templates = ProcessTemplates()
        
        # Test valid template
        valid_template = templates.get_template("customer_support")
        assert valid_template is not None
        assert "name" in valid_template
        assert "agents" in valid_template
        
    def test_template_scenarios(self):
        """Test template scenario handling."""
        templates = ProcessTemplates()
        
        # Get research team template
        template = templates.get_template("research_team")
        
        # Test scenarios exist
        assert "scenarios" in template
        assert len(template["scenarios"]) > 0
        
        # Test scenario structure
        scenario = template["scenarios"][0]
        assert "id" in scenario
        assert "name" in scenario
        assert "description" in scenario
        
    def test_template_customization(self):
        """Test template customization options."""
        templates = ProcessTemplates()
        
        # Get brainstorming template
        template = templates.get_template("brainstorming_session")
        
        # Test process config exists
        assert "process_config" in template
        config = template["process_config"]
        
        # Test default values
        assert config.get("process") == "conversational"
        assert "max_rounds" in config
        
    def test_all_templates_valid(self):
        """Test all templates are properly structured."""
        templates = ProcessTemplates()
        all_templates = templates.list_templates()
        
        for template_id in all_templates:
            template = templates.get_template(template_id)
            
            # Basic structure validation
            assert "name" in template
            assert "description" in template
            assert "agents" in template
            assert "tasks" in template
            assert "estimated_time" in template
            
            # Validate agents
            for agent in template["agents"]:
                assert "role" in agent
                assert "goal" in agent
                assert "backstory" in agent
                
            # Validate tasks
            for task in template["tasks"]:
                assert "description" in task
                assert "expected_output" in task
                
    def test_template_metadata(self):
        """Test template metadata handling."""
        templates = ProcessTemplates()
        
        # Test getting template with metadata
        template = templates.get_template("code_review")
        
        # Check metadata fields
        assert "category" in template
        assert "difficulty" in template
        assert "tags" in template
        assert isinstance(template["tags"], list)