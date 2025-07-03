"""
Unit tests for LiteAgent.
"""

import time
import pytest
from unittest.mock import Mock, patch

from litecrew.agent import LiteAgent
from litecrew.types import AgentConfig


class TestLiteAgent:
    """Test LiteAgent functionality and performance."""
    
    def test_agent_creation(self, sample_agent_config):
        """Test basic agent creation."""
        agent = LiteAgent(**sample_agent_config)
        
        assert agent.role == "Test Analyst"
        assert agent.goal == "Analyze test data"
        assert agent.backstory == "Expert in testing and analysis"
        assert agent.verbose is False
        assert agent.allow_delegation is False
        
    def test_agent_creation_performance(self):
        """Test that agent creation is fast (<10ms)."""
        start = time.perf_counter()
        
        agent = LiteAgent(
            role="Fast Agent",
            goal="Be quick",
            backstory="Born to be fast",
            verbose=False
        )
        
        creation_time = time.perf_counter() - start
        
        # Should create in less than 10ms
        assert creation_time < 0.01, f"Agent creation took {creation_time*1000:.2f}ms"
        
    def test_multiple_agents_performance(self):
        """Test creating multiple agents quickly."""
        agents = []
        start = time.perf_counter()
        
        for i in range(100):
            agent = LiteAgent(
                role=f"Agent {i}",
                goal=f"Goal {i}",
                backstory=f"Story {i}",
                verbose=False
            )
            agents.append(agent)
            
        total_time = time.perf_counter() - start
        avg_time = total_time / 100
        
        # Average creation time should be <5ms
        assert avg_time < 0.005, f"Average creation time: {avg_time*1000:.2f}ms"
        assert len(agents) == 100
        
    def test_system_message_generation(self):
        """Test system message is properly generated."""
        agent = LiteAgent(
            role="Researcher",
            goal="Find information",
            backstory="Expert researcher with 10 years experience",
            allow_delegation=True
        )
        
        assert "Researcher" in agent.system_message
        assert "Find information" in agent.system_message
        assert "Expert researcher" in agent.system_message
        assert "delegate tasks" in agent.system_message
        
    def test_default_llm(self):
        """Test default LLM is set correctly."""
        agent = LiteAgent(
            role="Test",
            goal="Test",
            backstory="Test"
        )
        
        # Should have an LLM set
        assert agent.llm is not None
        
    @patch('litecrew.agent.LiteAgent._create_agent_executor')
    def test_execute_with_mock(self, mock_executor):
        """Test execute method with mocked LLM."""
        # Setup mock
        mock_agent_executor = Mock()
        mock_agent_executor.invoke.return_value = {"output": "Task completed successfully"}
        mock_executor.return_value = mock_agent_executor
        
        agent = LiteAgent(
            role="Test Agent",
            goal="Complete tasks",
            backstory="A test agent",
            verbose=True
        )
        
        result = agent.execute("Do something")
        
        assert result == "Task completed successfully"
        mock_agent_executor.invoke.assert_called_once()
        
    def test_execute_with_context(self):
        """Test execute with context."""
        agent = LiteAgent(
            role="Contextual Agent",
            goal="Use context",
            backstory="Good at using context"
        )
        
        # Mock the executor
        with patch.object(agent, '_create_agent_executor') as mock:
            mock_executor = Mock()
            mock_executor.invoke.return_value = {"output": "Done with context"}
            mock.return_value = mock_executor
            
            result = agent.execute("New task", context="Previous context")
            
            # Check that context was included
            call_args = mock_executor.invoke.call_args[0][0]
            assert "Previous context" in call_args["input"]
            assert "New task" in call_args["input"]
            
    def test_execute_error_handling(self):
        """Test error handling in execute."""
        agent = LiteAgent(
            role="Error Agent",
            goal="Handle errors",
            backstory="Good at error handling",
            verbose=True
        )
        
        # Mock executor to raise error
        with patch.object(agent, '_create_agent_executor') as mock:
            mock_executor = Mock()
            mock_executor.invoke.side_effect = Exception("Test error")
            mock.return_value = mock_executor
            
            result = agent.execute("Cause error")
            
            assert "Error executing task" in result
            assert "Test error" in result
            
    def test_metrics_property(self):
        """Test metrics property returns correct data."""
        agent = LiteAgent(
            role="Metrics Agent",
            goal="Track metrics",
            backstory="Good at metrics",
            memory=True
        )
        
        metrics = agent.metrics
        
        assert "creation_time_ms" in metrics
        assert "execution_count" in metrics
        assert metrics["memory_enabled"] is True
        assert metrics["tools_count"] == 0
        
        # Execute once and check counter
        with patch.object(agent, '_create_agent_executor'):
            agent.execute("Test")
            
        assert agent.metrics["execution_count"] == 1
        
    def test_from_config(self):
        """Test creating agent from config."""
        config = {
            "role": "Config Agent",
            "goal": "Load from config",
            "backstory": "Created from configuration",
            "max_iter": 10,
            "verbose": True
        }
        
        agent = LiteAgent.from_config(config)
        
        assert agent.role == "Config Agent"
        assert agent.goal == "Load from config"
        assert agent.max_iter == 10
        assert agent.verbose is True
        
    def test_from_agent_config_type(self):
        """Test creating agent from AgentConfig type."""
        config = AgentConfig(
            role="Typed Agent",
            goal="Use typed config",
            backstory="Strongly typed"
        )
        
        agent = LiteAgent.from_config(config)
        
        assert agent.role == "Typed Agent"
        assert agent.goal == "Use typed config"
        
    def test_repr(self):
        """Test string representation."""
        agent = LiteAgent(
            role="Display Agent",
            goal="Show a very long goal that should be truncated in the representation",
            backstory="Test"
        )
        
        repr_str = repr(agent)
        
        assert "Display Agent" in repr_str
        assert "Show a very long goal that should be truncated" in repr_str
        assert "..." in repr_str
        
    @pytest.mark.asyncio
    async def test_async_execute(self):
        """Test async execution."""
        agent = LiteAgent(
            role="Async Agent",
            goal="Execute asynchronously",
            backstory="Async expert"
        )
        
        with patch.object(agent, 'execute') as mock_execute:
            mock_execute.return_value = "Async result"
            
            result = await agent.aexecute("Async task")
            
            assert result == "Async result"
            mock_execute.assert_called_once_with("Async task", None)