"""Tests for API process templates."""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock

# Set test environment
os.environ["LITECREW_API_KEYS"] = "test-key-123,test-key-456"
os.environ["ENVIRONMENT"] = "test"

from litecrew.api.templates import (
    QuickDebateTemplate,
    DecisionPanelTemplate,
    BrainstormingTemplate,
    CodeReviewTemplate,
    ResearchTeamTemplate,
    get_template,
    list_templates,
)
from litecrew.api.models import QuickStartRequest


class TestProcessTemplates:
    """Test process template functionality."""

    def test_list_templates(self):
        """Test listing available templates."""
        templates = list_templates()
        assert len(templates) >= 5

        template_names = [t["name"] for t in templates]
        assert "quick-debate" in template_names
        assert "decision-panel" in template_names
        assert "brainstorming" in template_names
        assert "code-review" in template_names
        assert "research-team" in template_names

    def test_get_template(self):
        """Test getting specific templates."""
        template = get_template("quick-debate")
        assert isinstance(template, QuickDebateTemplate)
        assert template.name == "quick-debate"
        assert template.process_type == "debate"

    def test_get_invalid_template(self):
        """Test getting non-existent template."""
        with pytest.raises(ValueError, match="Template 'invalid' not found"):
            get_template("invalid")

    def test_quick_debate_template(self):
        """Test quick debate template generation."""
        template = QuickDebateTemplate()

        # Test agent generation
        agents = template.generate_agents(topic="AI Ethics")
        assert len(agents) == 3
        assert agents[0]["role"] == "Proponent"
        assert agents[1]["role"] == "Critic"
        assert agents[2]["role"] == "Moderator"
        assert "AI Ethics" in agents[0]["goal"]

        # Test task generation
        tasks = template.generate_tasks(topic="AI Ethics")
        assert len(tasks) == 1
        assert "AI Ethics" in tasks[0]["description"]
        assert tasks[0]["agent_role"] == "Moderator"

        # Test process config
        config = template.get_process_config(rounds=5)
        assert config["rounds"] == 5
        assert config["allow_critic_first"] is False

    def test_decision_panel_template(self):
        """Test decision panel template generation."""
        template = DecisionPanelTemplate()

        # Test with custom inputs
        agents = template.generate_agents(decision="database selection")
        assert len(agents) == 3
        assert "database selection" in agents[0]["goal"]

        tasks = template.generate_tasks(
            decision="database selection", options=["PostgreSQL", "MongoDB", "DynamoDB"]
        )
        assert len(tasks) == 1
        assert "PostgreSQL" in tasks[0]["description"]
        assert "MongoDB" in tasks[0]["description"]

    def test_brainstorming_template(self):
        """Test brainstorming template generation."""
        template = BrainstormingTemplate()

        agents = template.generate_agents(topic="marketing strategies")
        assert len(agents) == 3
        assert agents[0]["type"] == "conversational"
        assert agents[1]["type"] == "thinking"

        config = template.get_process_config(min_turns=5, max_turns=15)
        assert config["min_turns"] == 5
        assert config["max_turns"] == 15

    def test_code_review_template(self):
        """Test code review template generation."""
        template = CodeReviewTemplate()

        agents = template.generate_agents(language="JavaScript")
        assert len(agents) == 3
        assert "JavaScript" in agents[0]["goal"]
        assert agents[0]["type"] == "critic"

        code = "function add(a, b) { return a + b; }"
        tasks = template.generate_tasks(code=code, language="JavaScript")
        assert len(tasks) == 3
        assert code in tasks[0]["description"]
        assert tasks[0]["agent_role"] == "Security Reviewer"
        assert tasks[1]["agent_role"] == "Performance Analyst"
        assert tasks[2]["agent_role"] == "Code Quality Expert"

    def test_research_team_template(self):
        """Test research team template generation."""
        template = ResearchTeamTemplate()

        agents = template.generate_agents(topic="renewable energy")
        assert len(agents) == 4
        assert agents[0]["type"] == "moderator"
        assert agents[0]["allow_delegation"] is True

        tasks = template.generate_tasks(
            topic="renewable energy", aspects=["solar", "wind", "hydro", "geothermal"]
        )
        # Should have: 1 planning + 4 research + 1 synthesis = 6 tasks
        assert len(tasks) == 6
        assert tasks[0]["agent_role"] == "Lead Researcher"
        assert tasks[-1]["agent_role"] == "Synthesis Expert"

        # Check task distribution
        research_tasks = tasks[1:5]
        agent_roles = [t["agent_role"] for t in research_tasks]
        assert "Data Analyst" in agent_roles
        assert "Literature Reviewer" in agent_roles
        assert "Synthesis Expert" in agent_roles

    def test_template_estimated_times(self):
        """Test estimated times for templates."""
        templates = {
            "quick-debate": 180,  # 3 minutes
            "decision-panel": 300,  # 5 minutes
            "brainstorming": 240,  # 4 minutes
            "code-review": 360,  # 6 minutes
            "research-team": 600,  # 10 minutes
        }

        for name, expected_time in templates.items():
            template = get_template(name)
            assert template.estimated_time() == expected_time


@pytest.mark.asyncio
class TestTemplateAPI:
    """Test template API endpoints."""

    async def test_quick_start_request_model(self):
        """Test QuickStartRequest model validation."""
        # Valid request
        request = QuickStartRequest(
            template="quick-debate", topic="Climate Change", rounds=3, auto_execute=True
        )
        assert request.template == "quick-debate"
        assert request.topic == "Climate Change"
        assert request.rounds == 3
        assert request.auto_execute is True

        # Request with minimal fields
        minimal = QuickStartRequest(template="brainstorming")
        assert minimal.template == "brainstorming"
        assert minimal.auto_execute is False  # Default value
