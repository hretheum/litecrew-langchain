"""
Tests for LiteCrew delegation system
"""

import pytest
import time
from unittest.mock import Mock, patch
from typing import Dict, Any

from litecrew.delegation import (
    DelegationManager,
    DelegationContext,
    DelegationResult,
    DelegationValidator
)
from litecrew.delegation.delegation_strategies import (
    DelegationStrategyType,
    create_delegation_strategy,
    RoundRobinStrategy,
    SkillBasedStrategy,
    LoadBalancedStrategy
)
from litecrew.tools import DelegationTool
from litecrew.agent import LiteAgent
from litecrew.crew import LiteCrew
from litecrew.task import LiteTask


class TestDelegationContext:
    """Test delegation context management."""
    
    def test_context_creation(self):
        """Test creating delegation context."""
        context = DelegationContext(
            original_agent="Researcher",
            context_data={"key": "value"}
        )
        
        assert context.original_agent == "Researcher"
        assert context.context_data == {"key": "value"}
        assert context.delegation_depth == 0
        assert len(context.delegation_chain) == 0
        assert context.delegation_id is not None
    
    def test_add_to_chain(self):
        """Test adding agents to delegation chain."""
        context = DelegationContext(original_agent="Manager")
        
        context.add_to_chain("Worker1")
        assert len(context.delegation_chain) == 1
        assert context.delegation_chain[0] == "Worker1"
        assert context.delegation_depth == 0
        
        context.add_to_chain("Worker2")
        assert len(context.delegation_chain) == 2
        assert context.delegation_chain == ["Worker1", "Worker2"]
        assert context.delegation_depth == 1
    
    def test_can_delegate_to(self):
        """Test delegation validation."""
        context = DelegationContext()
        context.add_to_chain("Agent1")
        context.add_to_chain("Agent2")
        
        # Should allow delegation to new agent
        assert context.can_delegate_to("Agent3", ["Agent3", "Agent4"])
        
        # Should prevent circular delegation
        assert not context.can_delegate_to("Agent1", ["Agent1", "Agent3"])
        
        # Should respect allowed agents list
        assert not context.can_delegate_to("Agent5", ["Agent3", "Agent4"])
    
    def test_create_child_context(self):
        """Test creating child context for sub-delegation."""
        parent = DelegationContext(original_agent="Manager")
        parent.add_to_chain("Worker1")
        parent.context_data = {"task": "analysis"}
        
        child = parent.create_child_context("Worker2")
        
        assert child.original_agent == "Manager"
        assert child.parent_delegation_id == parent.delegation_id
        assert child.context_data == {"task": "analysis"}
        assert len(child.delegation_chain) == 2
        assert child.delegation_chain == ["Worker1", "Worker2"]


class TestDelegationValidator:
    """Test delegation validation logic."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = DelegationValidator(
            max_depth=2,
            allowed_agents=["Agent1", "Agent2"],
            prevent_cycles=True
        )
        
        assert validator.max_depth == 2
        assert validator.allowed_agents == ["Agent1", "Agent2"]
        assert validator.prevent_cycles is True
    
    def test_validate_delegation_depth(self):
        """Test maximum delegation depth validation."""
        validator = DelegationValidator(max_depth=2)
        context = DelegationContext()
        
        # Depth 0 and 1 should be allowed
        context.delegation_depth = 0
        is_valid, error = validator.validate_delegation(context, "Agent1", "task")
        assert is_valid
        
        context.delegation_depth = 1
        is_valid, error = validator.validate_delegation(context, "Agent1", "task")
        assert is_valid
        
        # Depth 2 should be rejected (>= max_depth)
        context.delegation_depth = 2
        is_valid, error = validator.validate_delegation(context, "Agent1", "task")
        assert not is_valid
        assert "Maximum delegation depth" in error
    
    def test_validate_allowed_agents(self):
        """Test allowed agents validation."""
        validator = DelegationValidator(allowed_agents=["Agent1", "Agent2"])
        context = DelegationContext()
        
        # Allowed agent should pass
        is_valid, error = validator.validate_delegation(context, "Agent1", "task")
        assert is_valid
        
        # Disallowed agent should fail
        is_valid, error = validator.validate_delegation(context, "Agent3", "task")
        assert not is_valid
        assert "not allowed" in error
    
    def test_validate_circular_delegation(self):
        """Test circular delegation prevention."""
        validator = DelegationValidator(prevent_cycles=True)
        context = DelegationContext()
        context.delegation_chain = ["Agent1", "Agent2"]
        
        # Should prevent delegation back to Agent1
        is_valid, error = validator.validate_delegation(context, "Agent1", "task")
        assert not is_valid
        assert "Circular delegation detected" in error
        
        # Should allow delegation to new agent
        is_valid, error = validator.validate_delegation(context, "Agent3", "task")
        assert is_valid
    
    def test_validate_empty_task(self):
        """Test empty task validation."""
        validator = DelegationValidator()
        context = DelegationContext()
        
        # Empty task should fail
        is_valid, error = validator.validate_delegation(context, "Agent1", "")
        assert not is_valid
        assert "empty task" in error
        
        # Valid task should pass
        is_valid, error = validator.validate_delegation(context, "Agent1", "Do something")
        assert is_valid


class TestDelegationStrategies:
    """Test delegation strategy implementations."""
    
    def test_round_robin_strategy(self):
        """Test round-robin delegation strategy."""
        strategy = RoundRobinStrategy()
        agents = {"Agent1": Mock(), "Agent2": Mock(), "Agent3": Mock()}
        
        # Should cycle through agents
        selections = []
        for _ in range(6):
            selected = strategy.select_agent("task", agents)
            selections.append(selected)
        
        # Should have cycled through agents twice
        expected = ["Agent1", "Agent2", "Agent3", "Agent1", "Agent2", "Agent3"]
        assert selections == expected
    
    def test_skill_based_strategy(self):
        """Test skill-based delegation strategy."""
        skill_keywords = {
            "DataAnalyst": ["data", "analysis", "statistics"],
            "Writer": ["write", "content", "article"],
            "Researcher": ["research", "information", "study"]
        }
        
        strategy = SkillBasedStrategy(skill_keywords)
        agents = {"DataAnalyst": Mock(), "Writer": Mock(), "Researcher": Mock()}
        
        # Should select DataAnalyst for data task
        selected = strategy.select_agent("Analyze the data statistics", agents)
        assert selected == "DataAnalyst"
        
        # Should select Writer for writing task
        selected = strategy.select_agent("Write an article", agents)
        assert selected == "Writer"
        
        # Should select Researcher for research task
        selected = strategy.select_agent("Research information about topic", agents)
        assert selected == "Researcher"
    
    def test_load_balanced_strategy(self):
        """Test load-balanced delegation strategy."""
        strategy = LoadBalancedStrategy()
        agents = {"Agent1": Mock(), "Agent2": Mock()}
        
        # First two tasks should go to different agents
        agent1 = strategy.select_agent("task1", agents)
        agent2 = strategy.select_agent("task2", agents)
        assert agent1 != agent2
        
        # Mark one task as completed
        strategy.task_completed(agent1)
        
        # Next task should go to the agent with lower load
        agent3 = strategy.select_agent("task3", agents)
        assert agent3 == agent1  # Should have lower load now
    
    def test_strategy_factory(self):
        """Test delegation strategy factory."""
        # Test round robin
        strategy = create_delegation_strategy(DelegationStrategyType.ROUND_ROBIN)
        assert isinstance(strategy, RoundRobinStrategy)
        
        # Test skill based
        strategy = create_delegation_strategy(
            DelegationStrategyType.SKILL_BASED,
            skill_keywords={"Agent1": ["test"]}
        )
        assert isinstance(strategy, SkillBasedStrategy)
        
        # Test load balanced
        strategy = create_delegation_strategy(DelegationStrategyType.LOAD_BALANCED)
        assert isinstance(strategy, LoadBalancedStrategy)


class TestDelegationManager:
    """Test delegation manager functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        # Create mock agents
        self.agent1 = Mock()
        self.agent1.role = "Agent1"
        self.agent1.execute = Mock(return_value="Result from Agent1")
        
        self.agent2 = Mock()
        self.agent2.role = "Agent2" 
        self.agent2.execute = Mock(return_value="Result from Agent2")
        
        self.agents = {"Agent1": self.agent1, "Agent2": self.agent2}
        
        # Create delegation manager
        self.manager = DelegationManager(available_agents=self.agents)
    
    def test_successful_delegation(self):
        """Test successful delegation operation."""
        result = self.manager.delegate_task(
            from_agent="Agent1",
            task="Test task",
            target_agent="Agent2"
        )
        
        assert result.success is True
        assert result.result == "Result from Agent2"
        assert result.final_agent == "Agent2"
        assert result.delegation_chain == ["Agent1", "Agent2"]
        assert result.execution_time > 0
        
        # Verify agent was called
        self.agent2.execute.assert_called_once()
    
    def test_delegation_with_validation_error(self):
        """Test delegation with validation error."""
        # Create manager with strict validator
        validator = DelegationValidator(max_depth=0)
        manager = DelegationManager(available_agents=self.agents, validator=validator)
        
        result = manager.delegate_task(
            from_agent="Agent1",
            task="Test task",
            target_agent="Agent2"
        )
        
        assert result.success is False
        assert "Maximum delegation depth" in result.error
        assert result.final_agent == ""
    
    def test_delegation_to_nonexistent_agent(self):
        """Test delegation to non-existent agent."""
        result = self.manager.delegate_task(
            from_agent="Agent1",
            task="Test task",
            target_agent="NonExistentAgent"
        )
        
        assert result.success is False
        assert "not found" in result.error
    
    def test_delegation_metrics(self):
        """Test delegation metrics tracking."""
        # Initial metrics
        metrics = self.manager.get_delegation_metrics()
        assert metrics['total_delegations'] == 0
        assert metrics['successful_delegations'] == 0
        
        # Perform successful delegation
        self.manager.delegate_task("Agent1", "task1", target_agent="Agent2")
        
        # Check updated metrics
        metrics = self.manager.get_delegation_metrics()
        assert metrics['total_delegations'] == 1
        assert metrics['successful_delegations'] == 1
        assert metrics['failed_delegations'] == 0
        assert metrics['success_rate'] == 1.0
        assert metrics['average_execution_time'] > 0
    
    def test_delegation_history(self):
        """Test delegation history tracking."""
        # Perform delegations
        result1 = self.manager.delegate_task("Agent1", "task1", target_agent="Agent2")
        result2 = self.manager.delegate_task("Agent2", "task2", target_agent="Agent1")
        
        # Check history
        history = self.manager.get_delegation_history()
        assert len(history) == 2
        assert history[0].delegation_id == result1.delegation_id
        assert history[1].delegation_id == result2.delegation_id
        
        # Check limited history
        limited_history = self.manager.get_delegation_history(limit=1)
        assert len(limited_history) == 1
        assert limited_history[0].delegation_id == result2.delegation_id


class TestDelegationTool:
    """Test delegation tool integration."""
    
    def setup_method(self):
        """Setup test environment."""
        # Create simple mock agents without pydantic validation issues
        self.agent1 = Mock()
        self.agent1.role = "Researcher"
        self.agent1.allow_delegation = True
        self.agent1.execute = Mock(return_value="Research completed")
        
        self.agent2 = Mock()
        self.agent2.role = "Writer"
        self.agent2.allow_delegation = True
        self.agent2.execute = Mock(return_value="Article written")
        
        self.agents = [self.agent1, self.agent2]
        
        # Create delegation tool
        self.delegation_tool = DelegationTool(agents=self.agents)
        self.delegation_tool.set_current_agent(self.agent1)
    
    def test_delegation_tool_creation(self):
        """Test delegation tool creation."""
        assert self.delegation_tool.name == "delegate_task"
        assert "Researcher" in self.delegation_tool.description
        assert "Writer" in self.delegation_tool.description
    
    def test_successful_delegation_through_tool(self):
        """Test successful delegation through tool."""
        query = "Ask the Writer to create an article about AI"
        result = self.delegation_tool._delegate(query)
        
        assert "✅ Delegation successful" in result
        assert "Researcher" in result  # From agent
        assert "Writer" in result      # To agent
        assert "Article written" in result  # Result
    
    def test_delegation_parsing(self):
        """Test delegation query parsing."""
        # Test various patterns
        test_cases = [
            ("Ask the Writer to create content", ("Writer", "create content")),
            ("delegate to Researcher: find information", ("Researcher", "find information")),
            ("have the Writer analyze data", ("Writer", "analyze data")),
            ("get the Researcher to study topic", ("Researcher", "study topic"))
        ]
        
        for query, expected in test_cases:
            role, task = self.delegation_tool._parse_delegation(query)
            assert role == expected[0]
            assert task == expected[1]


class TestCrewDelegation:
    """Test delegation integration with LiteCrew."""
    
    def test_crew_delegation_setup(self):
        """Test delegation setup in crew."""
        # Create mock agents with delegation enabled
        agent1 = Mock(spec=LiteAgent)
        agent1.role = "Researcher"
        agent1.allow_delegation = True
        agent1.tools = []
        
        agent2 = Mock(spec=LiteAgent)
        agent2.role = "Writer"
        agent2.allow_delegation = True
        agent2.tools = []
        
        # Create mock task
        task1 = Mock(spec=LiteTask)
        task1.description = "Test task"
        task1.agent = None
        
        # Create crew
        crew = LiteCrew(agents=[agent1, agent2], tasks=[task1])
        
        # Check delegation setup
        assert hasattr(crew, '_delegation_manager')
        assert len(agent1.tools) > 0
        assert len(agent2.tools) > 0
        
        # Check that delegation tools were added
        delegation_tools = [tool for tool in agent1.tools if hasattr(tool, 'name') and tool.name == "delegate_task"]
        assert len(delegation_tools) == 1
    
    def test_crew_delegation_metrics(self):
        """Test crew delegation metrics access."""
        # Create mock agent and task
        agent1 = Mock(spec=LiteAgent)
        agent1.role = "TestAgent"
        agent1.allow_delegation = False
        
        task1 = Mock(spec=LiteTask)
        task1.description = "Test task"
        task1.agent = None
        
        # Create simple crew 
        crew = LiteCrew(agents=[agent1], tasks=[task1])
        
        # Test metrics access when no delegation manager exists
        metrics = crew.get_delegation_metrics()
        assert metrics['total_delegations'] == 0
        
        history = crew.get_delegation_history()
        assert len(history) == 0


class TestDelegationChains:
    """Test complex delegation chains and scenarios."""
    
    def test_delegation_depth_limiting(self):
        """Test delegation depth limiting."""
        # Create agents
        agents = {}
        for i in range(5):
            agent = Mock()
            agent.role = f"Agent{i}"
            agent.execute = Mock(return_value=f"Result from Agent{i}")
            agents[f"Agent{i}"] = agent
        
        # Create manager with max depth 2
        validator = DelegationValidator(max_depth=2)
        manager = DelegationManager(available_agents=agents, validator=validator)
        
        # First delegation should work
        result1 = manager.delegate_task("Agent0", "task1", target_agent="Agent1")
        assert result1.success is True
        assert result1.delegation_chain == ["Agent0", "Agent1"]
        
        # Second level delegation should work
        context = DelegationContext()
        context.delegation_chain = ["Agent0", "Agent1"]
        context.delegation_depth = 1
        
        is_valid, error = validator.validate_delegation(context, "Agent2", "task")
        assert is_valid
        
        # Third level should be rejected
        context.delegation_depth = 2
        is_valid, error = validator.validate_delegation(context, "Agent3", "task")
        assert not is_valid
    
    def test_circular_delegation_prevention(self):
        """Test prevention of circular delegation."""
        agents = {
            "Agent1": Mock(execute=Mock(return_value="Result1")),
            "Agent2": Mock(execute=Mock(return_value="Result2"))
        }
        
        for agent_name, agent in agents.items():
            agent.role = agent_name
        
        manager = DelegationManager(available_agents=agents)
        
        # Create context that simulates a delegation chain
        context = DelegationContext()
        context.delegation_chain = ["Agent1", "Agent2"]
        
        # Should prevent delegation back to Agent1
        is_valid, error = manager.validator.validate_delegation(context, "Agent1", "task")
        assert not is_valid
        assert "Circular delegation detected" in error
    
    def test_performance_metrics(self):
        """Test delegation performance metrics."""
        # Create fast and slow agents
        fast_agent = Mock()
        fast_agent.role = "FastAgent"
        fast_agent.execute = Mock(return_value="Fast result")
        
        slow_agent = Mock()
        slow_agent.role = "SlowAgent"
        
        def slow_execute(*args, **kwargs):
            time.sleep(0.1)  # Simulate slow operation
            return "Slow result"
        
        slow_agent.execute = slow_execute
        
        agents = {"FastAgent": fast_agent, "SlowAgent": slow_agent}
        manager = DelegationManager(available_agents=agents)
        
        # Perform delegations
        fast_result = manager.delegate_task("User", "fast task", target_agent="FastAgent")
        slow_result = manager.delegate_task("User", "slow task", target_agent="SlowAgent")
        
        # Check timing differences
        assert fast_result.execution_time < slow_result.execution_time
        assert slow_result.execution_time >= 0.1
        
        # Check metrics
        metrics = manager.get_delegation_metrics()
        assert metrics['total_delegations'] == 2
        assert metrics['successful_delegations'] == 2
        assert metrics['average_execution_time'] > 0


if __name__ == "__main__":
    pytest.main([__file__])