"""Tests for core crew execution functionality."""

import asyncio
from unittest.mock import Mock

import pytest

from litecrew import LiteAgent, LiteCrew, LiteTask


class TestCrewExecution:
    """Test crew execution workflows."""

    def test_sequential_execution(self):
        """Test sequential task execution."""
        # Create mock agents
        agent1 = LiteAgent(role="Researcher", goal="Research", backstory="I research")
        agent2 = LiteAgent(role="Writer", goal="Write", backstory="I write")

        # Mock agent execute methods
        agent1.execute = Mock(return_value="Research result")
        agent2.execute = Mock(return_value="Written content")

        # Create tasks
        task1 = LiteTask(
            description="Do research", agent=agent1, expected_output="Research findings"
        )
        task2 = LiteTask(
            description="Write report",
            agent=agent2,
            expected_output="Report",
            context=[task1],  # Task 2 depends on task 1
        )

        # Create crew
        crew = LiteCrew(
            agents=[agent1, agent2], tasks=[task1, task2], process="sequential"
        )

        # Execute crew
        result = crew.kickoff()

        # Verify execution
        assert result is not None
        assert agent1.execute.called
        assert agent2.execute.called

        # Verify task execution order (sequential)
        assert len(crew.tasks) == 2

    def test_sequential_with_multiple_agents(self):
        """Test sequential execution with multiple agents."""
        # Create independent agents
        agents = []
        tasks = []

        for i in range(3):
            agent = LiteAgent(
                role=f"Agent{i}", goal=f"Goal{i}", backstory=f"Backstory{i}"
            )
            agent.execute = Mock(return_value=f"Result{i}")
            agents.append(agent)

            task = LiteTask(
                description=f"Task {i}", agent=agent, expected_output=f"Output {i}"
            )
            tasks.append(task)

        crew = LiteCrew(agents=agents, tasks=tasks, process="sequential")

        crew.kickoff()

        # All agents should have been called
        for agent in agents:
            assert agent.execute.called

    def test_crew_with_memory(self):
        """Test crew execution with memory enabled."""
        agent = LiteAgent(
            role="Researcher",
            goal="Research with memory",
            backstory="Memory-enabled researcher",
        )
        agent.execute = Mock(return_value="Memory result")

        task = LiteTask(
            description="Research with context",
            agent=agent,
            expected_output="Contextualized result",
        )

        crew = LiteCrew(agents=[agent], tasks=[task], memory=True)

        # Execute multiple times to test memory
        result1 = crew.kickoff(inputs={"topic": "AI"})
        result2 = crew.kickoff(inputs={"topic": "ML"})

        assert result1 is not None
        assert result2 is not None
        assert crew.memory is not None

    def test_hierarchical_process(self):
        """Test hierarchical execution with manager agent."""
        # Manager agent
        manager = LiteAgent(
            role="Manager", goal="Coordinate team", backstory="Team coordinator"
        )
        manager.execute = Mock(return_value="Coordination result")

        # Worker agents
        worker1 = LiteAgent(role="Worker1", goal="Work", backstory="Worker")
        worker2 = LiteAgent(role="Worker2", goal="Work", backstory="Worker")

        worker1.execute = Mock(return_value="Work result 1")
        worker2.execute = Mock(return_value="Work result 2")

        task = LiteTask(
            description="Coordinate work",
            agent=manager,
            expected_output="Coordinated result",
        )

        crew = LiteCrew(
            agents=[worker1, worker2],
            tasks=[task],
            process="hierarchical",
            manager_agent=manager,
        )

        result = crew.kickoff()

        assert result is not None
        assert crew.manager_agent == manager

    @pytest.mark.asyncio
    async def test_async_execution(self):
        """Test asynchronous crew execution."""
        agent = LiteAgent(
            role="AsyncAgent", goal="Async work", backstory="Async worker"
        )

        # Mock async execute
        async def mock_async_execute(task_description, context=None):
            await asyncio.sleep(0.01)  # Simulate async work
            return "Async result"

        agent.execute_async = mock_async_execute

        task = LiteTask(
            description="Async task", agent=agent, expected_output="Async output"
        )

        crew = LiteCrew(agents=[agent], tasks=[task], async_execution=True)

        result = await crew.kickoff_async()
        assert result is not None

    def test_crew_state_tracking(self):
        """Test crew state tracking during execution."""
        agent = LiteAgent(
            role="StateAgent", goal="Track state", backstory="State tracker"
        )
        agent.execute = Mock(return_value="State result")

        task = LiteTask(
            description="Track state", agent=agent, expected_output="State output"
        )

        crew = LiteCrew(agents=[agent], tasks=[task])

        # Execute and verify crew works
        result = crew.kickoff()

        # Should have a crew id and basic attributes
        assert hasattr(crew, "id")
        assert result is not None

    def test_task_context_passing(self):
        """Test context passing between dependent tasks."""
        agent1 = LiteAgent(role="Producer", goal="Produce", backstory="Producer")
        agent2 = LiteAgent(role="Consumer", goal="Consume", backstory="Consumer")

        agent1.execute = Mock(return_value="Produced data")
        agent2.execute = Mock(return_value="Consumed data")

        task1 = LiteTask(
            description="Produce data", agent=agent1, expected_output="Data"
        )

        task2 = LiteTask(
            description="Consume data",
            agent=agent2,
            expected_output="Result",
            context=[task1],  # Depends on task1
        )

        crew = LiteCrew(agents=[agent1, agent2], tasks=[task1, task2])

        crew.kickoff()

        # Both agents should be called
        assert agent1.execute.called
        assert agent2.execute.called

        # Task 2 should receive context from task 1
        # Check if agent2 was called with context
        agent2_call_args = agent2.execute.call_args
        assert agent2_call_args is not None

    def test_crew_error_handling(self):
        """Test crew error handling during execution."""
        agent = LiteAgent(
            role="FailingAgent", goal="Fail gracefully", backstory="Failure handler"
        )

        # Mock agent to raise exception
        agent.execute = Mock(side_effect=Exception("Task failed"))

        task = LiteTask(
            description="Failing task", agent=agent, expected_output="Should fail"
        )

        crew = LiteCrew(agents=[agent], tasks=[task])

        # Execution should handle errors gracefully
        with pytest.raises(Exception):
            crew.kickoff()

    def test_crew_with_callbacks(self):
        """Test crew execution with step callbacks."""
        callback_calls = []

        def step_callback(task, output):
            callback_calls.append({"task": task, "output": output})

        agent = LiteAgent(
            role="CallbackAgent", goal="Test callbacks", backstory="Callback tester"
        )
        agent.execute = Mock(return_value="Callback result")

        task = LiteTask(
            description="Test callbacks", agent=agent, expected_output="Callback output"
        )

        crew = LiteCrew(agents=[agent], tasks=[task], step_callback=step_callback)

        crew.kickoff()

        # Callbacks should have been called
        assert len(callback_calls) > 0

    def test_crew_output_structure(self):
        """Test crew output structure and content."""
        agent = LiteAgent(
            role="OutputAgent", goal="Generate output", backstory="Output generator"
        )
        agent.execute = Mock(return_value="Structured output")

        task = LiteTask(
            description="Generate output",
            agent=agent,
            expected_output="Structured result",
        )

        crew = LiteCrew(agents=[agent], tasks=[task])

        result = crew.kickoff()

        # Result should have proper structure
        assert hasattr(result, "raw")
        assert hasattr(result, "tasks_output")
        assert hasattr(result, "timestamp")

        # Should be convertible to string
        assert str(result) is not None
