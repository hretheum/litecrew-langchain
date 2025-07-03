"""
Basic tests for LiteCrew functionality
"""

import pytest
from litecrew import LiteAgent, LiteCrew, LiteTask


def test_agent_creation():
    """Test basic agent creation."""
    agent = LiteAgent(
        role="Researcher",
        goal="Find information",
        backstory="Expert researcher"
    )
    
    assert agent.role == "Researcher"
    assert agent.goal == "Find information"
    assert agent.backstory == "Expert researcher"
    assert agent.tools == []
    assert agent.verbose == False
    assert agent.max_iter == 5


def test_task_creation():
    """Test basic task creation."""
    agent = LiteAgent(
        role="Writer",
        goal="Write content",
        backstory="Professional writer"
    )
    
    task = LiteTask(
        description="Write a blog post",
        agent=agent,
        expected_output="A blog post"
    )
    
    assert task.description == "Write a blog post"
    assert task.agent == agent
    assert task.expected_output == "A blog post"
    assert task.context is None
    assert task.output is None


def test_crew_creation():
    """Test basic crew creation."""
    researcher = LiteAgent(
        role="Researcher",
        goal="Research topics",
        backstory="Expert researcher"
    )
    
    writer = LiteAgent(
        role="Writer",
        goal="Write content",
        backstory="Professional writer"
    )
    
    research_task = LiteTask(
        description="Research AI frameworks",
        agent=researcher
    )
    
    write_task = LiteTask(
        description="Write blog post",
        agent=writer,
        context=[research_task]
    )
    
    crew = LiteCrew(
        agents=[researcher, writer],
        tasks=[research_task, write_task],
        process="sequential"
    )
    
    assert len(crew.agents) == 2
    assert len(crew.tasks) == 2
    assert crew.process == "sequential"
    assert write_task.context[0] == research_task


def test_task_context_building():
    """Test context building from dependent tasks."""
    task1 = LiteTask(description="First task")
    task1.output = type('obj', (object,), {'raw': 'First output'})()
    
    task2 = LiteTask(
        description="Second task",
        context=[task1]
    )
    
    context = task2._build_context()
    assert "First output" in context


def test_auto_task_assignment():
    """Test automatic task assignment in crew."""
    agent1 = LiteAgent(role="Agent1", goal="Goal1", backstory="Story1")
    agent2 = LiteAgent(role="Agent2", goal="Goal2", backstory="Story2")
    
    # Tasks without agents
    task1 = LiteTask(description="Task 1")
    task2 = LiteTask(description="Task 2")
    task3 = LiteTask(description="Task 3")
    
    crew = LiteCrew(
        agents=[agent1, agent2],
        tasks=[task1, task2, task3]
    )
    
    # Check round-robin assignment
    assert task1.agent == agent1
    assert task2.agent == agent2
    assert task3.agent == agent1  # Cycles back


def test_hierarchical_needs_manager():
    """Test that hierarchical process creates default manager if needed."""
    agent = LiteAgent(role="Worker", goal="Do work", backstory="Worker")
    task = LiteTask(description="Work task", agent=agent)
    
    crew = LiteCrew(
        agents=[agent],
        tasks=[task],
        process="hierarchical"
    )
    
    assert crew.manager_agent is not None
    assert crew.manager_agent.role == "Crew Manager"


@pytest.mark.skip(reason="Requires mock LLM for testing")
def test_crew_execution():
    """Test crew execution (requires mock LLM)."""
    # This would need a mock LLM to test without making real API calls
    pass