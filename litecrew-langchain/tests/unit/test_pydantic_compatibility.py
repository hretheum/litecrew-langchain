"""
Test Pydantic API compatibility after migration to dataclasses.
"""

import json
import pytest
from datetime import datetime

from litecrew.task import LiteTask, TaskOutput
from litecrew.crew import LiteCrew, CrewOutput, ProcessType
from litecrew.types import AgentConfig, TaskConfig, CrewConfig
from litecrew.agent import LiteAgent


class TestPydanticCompatibility:
    """Test that Pydantic-like API still works after migration."""
    
    def test_task_output_model_dump(self):
        """Test TaskOutput.model_dump() compatibility."""
        output = TaskOutput(
            raw="Test output",
            task_id="test-123",
            agent_role="Tester"
        )
        
        # Test model_dump
        data = output.model_dump()
        assert isinstance(data, dict)
        assert data["raw"] == "Test output"
        assert data["task_id"] == "test-123"
        assert data["agent_role"] == "Tester"
        assert "timestamp" in data
        
        # Test exclude parameter
        data_exclude = output.model_dump(exclude={"timestamp"})
        assert "timestamp" not in data_exclude
        assert "raw" in data_exclude
        
        # Test exclude_none
        output_with_none = TaskOutput(raw="Test", task_id=None)
        data_no_none = output_with_none.model_dump(exclude_none=True)
        assert "task_id" not in data_no_none
        assert "raw" in data_no_none
    
    def test_task_output_model_dump_json(self):
        """Test TaskOutput.model_dump_json() compatibility."""
        output = TaskOutput(
            raw="Test output",
            task_id="test-123",
            agent_role="Tester",
            timestamp=datetime(2025, 1, 1, 12, 0, 0)
        )
        
        # Test JSON serialization
        json_str = output.model_dump_json()
        assert isinstance(json_str, str)
        
        # Verify JSON is valid
        data = json.loads(json_str)
        assert data["raw"] == "Test output"
        assert data["task_id"] == "test-123"
        
        # Test with indent
        json_pretty = output.model_dump_json(indent=2)
        assert "\n" in json_pretty
    
    def test_lite_task_model_validate(self):
        """Test LiteTask.model_validate() compatibility."""
        # From dict
        task_data = {
            "description": "Test task",
            "expected_output": "Test output",
            "verbose": True,  # Extra field should be ignored
        }
        
        task = LiteTask.model_validate(task_data)
        assert task.description == "Test task"
        assert task.expected_output == "Test output"
        assert not hasattr(task, "verbose")  # Extra field ignored
        
        # From object (should return same object)
        task2 = LiteTask.model_validate(task)
        assert task2 is task
    
    def test_lite_task_model_copy(self):
        """Test LiteTask.model_copy() compatibility."""
        task = LiteTask(
            description="Original task",
            expected_output="Original output"
        )
        
        # Copy without changes
        copy1 = task.model_copy()
        assert copy1.description == "Original task"
        assert copy1 is not task
        
        # Copy with updates
        copy2 = task.model_copy(update={"description": "Updated task"})
        assert copy2.description == "Updated task"
        assert copy2.expected_output == "Original output"
        assert task.description == "Original task"  # Original unchanged
    
    def test_crew_output_compatibility(self):
        """Test CrewOutput Pydantic-like methods."""
        task_output = TaskOutput(raw="Task done", agent_role="Worker")
        crew_output = CrewOutput(
            raw="All done",
            tasks_output=[task_output],
            token_usage={"total": 100}
        )
        
        # Test model_dump
        data = crew_output.model_dump()
        assert data["raw"] == "All done"
        assert len(data["tasks_output"]) == 1
        assert data["token_usage"]["total"] == 100
        
        # Test nested serialization
        json_str = crew_output.model_dump_json()
        data = json.loads(json_str)
        assert data["tasks_output"][0]["raw"] == "Task done"
    
    def test_lite_crew_validation(self):
        """Test LiteCrew still validates properly."""
        agent = LiteAgent(
            role="Tester",
            goal="Test things",
            backstory="Born to test"
        )
        
        task = LiteTask(
            description="Test task",
            expected_output="Success"
        )
        
        # Test process validation
        crew = LiteCrew(
            agents=[agent],
            tasks=[task],
            process="sequential"  # String should be converted to enum
        )
        
        assert crew.process == ProcessType.SEQUENTIAL
        
        # Test invalid process
        with pytest.raises(ValueError, match="Invalid process type"):
            LiteCrew(
                agents=[agent],
                tasks=[task],
                process="invalid"
            )
    
    def test_agent_config_compatibility(self):
        """Test AgentConfig from types.py."""
        config = AgentConfig(
            role="Tester",
            goal="Test",
            backstory="Testing"
        )
        
        # Test model_fields
        fields = AgentConfig.model_fields()
        assert "role" in fields
        assert "goal" in fields
        assert "tools" in fields
        assert fields["tools"]["default_factory"] is not None
        assert fields["memory"]["default"] is False
        
        # Test model_validate from dict
        agent = AgentConfig.model_validate({
            "role": "New Tester",
            "goal": "New Goal",
            "backstory": "New Story",
            "extra_field": "ignored"
        })
        assert agent.role == "New Tester"
        assert not hasattr(agent, "extra_field")
    
    def test_backward_compatibility_aliases(self):
        """Test old Pydantic method aliases still work."""
        output = TaskOutput(raw="Test", agent_role="Tester")
        
        # Test dict() alias
        data = output.dict()
        assert data["raw"] == "Test"
        
        # Test json() alias  
        json_str = output.json()
        assert isinstance(json_str, str)
        
        # Test parse_obj() alias
        new_output = TaskOutput.parse_obj({"raw": "New", "agent_role": "New Tester"})
        assert new_output.raw == "New"
        
        # Test parse_raw() alias
        json_data = '{"raw": "From JSON", "agent_role": "JSON Tester"}'
        from_json = TaskOutput.parse_raw(json_data)
        assert from_json.raw == "From JSON"
        
        # Test copy() alias
        copy = output.copy(update={"raw": "Copied"})
        assert copy.raw == "Copied"
        assert output.raw == "Test"
    
    def test_lite_task_post_init_validation(self):
        """Test that validation still happens in __post_init__."""
        # Empty description should fail
        with pytest.raises(ValueError, match="description cannot be empty"):
            LiteTask(description="", expected_output="Test")
        
        # Whitespace-only description should fail
        with pytest.raises(ValueError, match="description cannot be empty"):
            LiteTask(description="   ", expected_output="Test")
        
        # Description should be stripped
        task = LiteTask(description="  Test task  ", expected_output="  Output  ")
        assert task.description == "Test task"
        assert task.expected_output == "Output"
    
    def test_model_config_compatibility(self):
        """Test model_config() returns empty dict for compatibility."""
        config = AgentConfig.model_config()
        assert isinstance(config, dict)
        assert len(config) == 0