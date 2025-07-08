"""Tests for crew to improve coverage."""

import pytest
from unittest.mock import Mock, patch
from litecrew.crew import LiteCrew
from litecrew.agent import LiteAgent
from litecrew.task import LiteTask
from litecrew.processes import SequentialProcess


class TestLiteCrewCoverage:
    """Tests for LiteCrew to improve coverage."""
    
    def test_crew_alias(self):
        """Test that Crew alias works correctly."""
        from litecrew.crew import Crew
        
        # Should be able to import Crew alias
        assert Crew is LiteCrew
    
    def test_process_config_with_dict(self):
        """Test process config handling with dict."""
        agent = LiteAgent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory"
        )
        
        task = LiteTask(
            description="Test task",
            agent=agent
        )
        
        # Create crew with dict process config
        crew = LiteCrew(
            agents=[agent],
            tasks=[task],
            process=SequentialProcess(),
            process_config={"max_iterations": 5, "timeout": 60}
        )
        
        # Should accept dict config
        assert crew.process_config == {"max_iterations": 5, "timeout": 60}
    
    def test_process_config_with_object(self):
        """Test process config handling with object."""
        agent = LiteAgent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory"
        )
        
        task = LiteTask(
            description="Test task",
            agent=agent
        )
        
        # Create mock config object
        config_obj = Mock()
        config_obj.max_iterations = 10
        config_obj.timeout = 120
        
        # Create crew with object process config
        crew = LiteCrew(
            agents=[agent],
            tasks=[task],
            process=SequentialProcess(),
            process_config=config_obj
        )
        
        # Should accept object config
        assert crew.process_config == config_obj
    
    def test_crew_str_method(self):
        """Test __str__ method."""
        agent = LiteAgent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory"
        )
        
        task = LiteTask(
            description="Test task",
            agent=agent
        )
        
        crew = LiteCrew(
            agents=[agent],
            tasks=[task],
            process=SequentialProcess()
        )
        
        str_repr = str(crew)
        assert "LiteCrew" in str_repr
        assert "agents=1" in str_repr
        assert "tasks=1" in str_repr