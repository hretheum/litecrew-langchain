"""Tests for automatic agent selection functionality."""

from litecrew.api.agent_selector import AgentSelector


class TestAgentSelector:
    """Test agent selector functionality."""

    def test_default_agents_exist(self):
        """Test that default agents are defined."""
        assert hasattr(AgentSelector, "DEFAULT_AGENTS")
        assert isinstance(AgentSelector.DEFAULT_AGENTS, dict)
        assert len(AgentSelector.DEFAULT_AGENTS) > 0

        # Check specific agents exist
        expected_agents = [
            "analyst",
            "writer",
            "developer",
            "reviewer",
            "manager",
            "researcher",
            "strategist",
            "communicator",
        ]
        for agent in expected_agents:
            assert agent in AgentSelector.DEFAULT_AGENTS

    def test_default_agent_structure(self):
        """Test structure of default agent configurations."""
        for agent_name, agent_config in AgentSelector.DEFAULT_AGENTS.items():
            # Required fields
            assert "role" in agent_config
            assert "goal" in agent_config
            assert "backstory" in agent_config
            assert "type" in agent_config

            # Check types
            assert isinstance(agent_config["role"], str)
            assert isinstance(agent_config["goal"], str)
            assert isinstance(agent_config["backstory"], str)
            assert isinstance(agent_config["type"], str)

            # Optional type_config
            if "type_config" in agent_config:
                assert isinstance(agent_config["type_config"], dict)

    def test_task_keywords_exist(self):
        """Test that task keywords are defined."""
        assert hasattr(AgentSelector, "TASK_KEYWORDS")
        assert isinstance(AgentSelector.TASK_KEYWORDS, dict)
        assert len(AgentSelector.TASK_KEYWORDS) > 0

        # Check structure
        for keyword, agent_types in AgentSelector.TASK_KEYWORDS.items():
            assert isinstance(keyword, str)
            assert isinstance(agent_types, list)
            assert all(isinstance(t, str) for t in agent_types)

    def test_select_agents_basic(self):
        """Test basic agent selection."""
        agents = AgentSelector.select_agents("Create a data analysis report")

        assert isinstance(agents, list)
        assert len(agents) == 3  # Default num_agents

        # Check agent structure
        for agent in agents:
            assert "role" in agent
            assert "goal" in agent
            assert "backstory" in agent
            assert "type" in agent

    def test_select_agents_with_num(self):
        """Test selecting specific number of agents."""
        # Test with different numbers
        for num in [1, 2, 4, 5]:
            agents = AgentSelector.select_agents("Test task", num_agents=num)
            assert len(agents) == num

    def test_select_agents_with_required_roles(self):
        """Test selecting agents with required roles."""
        required = ["analyst", "writer", "developer"]
        agents = AgentSelector.select_agents(
            "Build and document API", num_agents=3, required_roles=required
        )

        assert len(agents) == 3
        # Check roles match
        for i, agent in enumerate(agents):
            assert agent["role"] == AgentSelector.DEFAULT_AGENTS[required[i]]["role"]

    def test_select_agents_with_custom_required_role(self):
        """Test selecting agents with custom required role."""
        agents = AgentSelector.select_agents(
            "Special task", num_agents=2, required_roles=["analyst", "CustomRole"]
        )

        assert len(agents) == 2
        assert agents[0]["role"] == "Data Analyst"
        assert agents[1]["role"] == "CustomRole"
        assert agents[1]["type"] == "conversational"  # Default type

    def test_select_agents_keyword_matching(self):
        """Test agent selection based on keywords."""
        # Analyze keyword
        agents = AgentSelector.select_agents("Analyze the market data")
        roles = [a["role"] for a in agents]
        assert any("Analyst" in role for role in roles)

        # Write keyword
        agents = AgentSelector.select_agents("Write a blog post")
        roles = [a["role"] for a in agents]
        assert any("Writer" in role for role in roles)

        # Develop keyword
        agents = AgentSelector.select_agents("Develop a new feature")
        roles = [a["role"] for a in agents]
        assert any("Developer" in role for role in roles)

    def test_select_agents_includes_manager(self):
        """Test that manager is included for larger teams."""
        agents = AgentSelector.select_agents("Complex project", num_agents=3)

        # Should have a manager/moderator
        types = [a["type"] for a in agents]
        assert "moderator" in types

    def test_select_agents_custom_goal(self):
        """Test that goals are customized based on task."""
        task = "Build a machine learning model"
        agents = AgentSelector.select_agents(task)

        # All goals should reference the task
        for agent in agents:
            assert task in agent["goal"] or task[:100] in agent["goal"]

    def test_suggest_process_type_debate(self):
        """Test process type suggestion for debate tasks."""
        process = AgentSelector.suggest_process_type("Debate the pros and cons", 2)
        assert process == "debate"

        process = AgentSelector.suggest_process_type("Discuss different approaches", 3)
        assert process == "debate"

    def test_suggest_process_type_panel(self):
        """Test process type suggestion for decision tasks."""
        process = AgentSelector.suggest_process_type("Decide on the best option", 4)
        assert process == "panel"

        process = AgentSelector.suggest_process_type("Choose between alternatives", 3)
        assert process == "panel"

    def test_suggest_process_type_conversational(self):
        """Test process type suggestion for creative tasks."""
        process = AgentSelector.suggest_process_type("Brainstorm new ideas", 2)
        assert process == "conversational"

        process = AgentSelector.suggest_process_type("Creative solution needed", 2)
        assert process == "conversational"

    def test_suggest_process_type_sequential(self):
        """Test process type suggestion for ordered tasks."""
        process = AgentSelector.suggest_process_type("Step by step implementation", 3)
        assert process == "sequential"

        process = AgentSelector.suggest_process_type("Follow these phases", 3)
        assert process == "sequential"

    def test_suggest_process_type_hierarchical(self):
        """Test process type suggestion for management tasks."""
        process = AgentSelector.suggest_process_type("Coordinate the team effort", 5)
        assert process == "hierarchical"

        process = AgentSelector.suggest_process_type("Manage the project", 6)
        assert process == "hierarchical"

    def test_suggest_process_type_by_size(self):
        """Test process type defaults based on team size."""
        # Small team
        process = AgentSelector.suggest_process_type("Generic task", 2)
        assert process == "conversational"

        # Medium team
        process = AgentSelector.suggest_process_type("Generic task", 4)
        assert process == "sequential"

        # Large team
        process = AgentSelector.suggest_process_type("Generic task", 6)
        assert process == "hierarchical"

    def test_estimate_execution_time_basic(self):
        """Test basic execution time estimation."""
        time = AgentSelector.estimate_execution_time("Simple task", 2)

        assert isinstance(time, int)
        assert time > 0
        # Base (60) + agents (2*30) = 120 minimum
        assert time >= 120

    def test_estimate_execution_time_complex(self):
        """Test execution time for complex tasks."""
        # Long description
        long_task = " ".join(["word"] * 50)  # 50 words
        time = AgentSelector.estimate_execution_time(long_task, 3)

        # Should add complexity time
        assert time > 200  # Base + complexity + agents

        # Research task
        time_research = AgentSelector.estimate_execution_time("Research the market", 3)
        time_simple = AgentSelector.estimate_execution_time("Simple task here", 3)
        assert time_research > time_simple  # Research adds time

    def test_estimate_execution_time_keywords(self):
        """Test that specific keywords increase time estimate."""
        base_time = AgentSelector.estimate_execution_time("Task", 2)

        # Research keyword
        research_time = AgentSelector.estimate_execution_time("Research task", 2)
        assert research_time > base_time

        # Comprehensive keyword
        comprehensive_time = AgentSelector.estimate_execution_time(
            "Comprehensive task", 2
        )
        assert comprehensive_time > base_time

        # Both keywords
        both_time = AgentSelector.estimate_execution_time("Comprehensive research", 2)
        assert both_time > research_time
        assert both_time > comprehensive_time

    def test_agent_type_distribution(self):
        """Test that different agent types are selected."""
        agents = AgentSelector.select_agents(
            "Complex multi-faceted project", num_agents=5
        )

        types = [a["type"] for a in agents]
        # Should have some variety
        assert len(set(types)) >= 2  # At least 2 different types

    def test_empty_task_description(self):
        """Test handling of empty task description."""
        agents = AgentSelector.select_agents("", num_agents=3)

        assert len(agents) == 3
        # Should use defaults
        assert all("role" in agent for agent in agents)
