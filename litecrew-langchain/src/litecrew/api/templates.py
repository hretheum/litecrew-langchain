"""Process templates for quick start API."""

from typing import Any, Dict, List


class ProcessTemplate:
    """Base class for process templates."""

    def __init__(self, name: str, description: str, process_type: str):
        self.name = name
        self.description = description
        self.process_type = process_type

    def generate_agents(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """Generate agents configuration for the template."""
        raise NotImplementedError

    def generate_tasks(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """Generate tasks configuration for the template."""
        raise NotImplementedError

    def get_process_config(self, **kwargs: Any) -> Dict[str, Any]:
        """Get process configuration for the template."""
        return {}

    def get_default_inputs(self) -> Dict[str, Any]:
        """Get default inputs for the template."""
        return {}

    def estimated_time(self) -> int:
        """Get estimated execution time in seconds."""
        return 300  # 5 minutes default


class QuickDebateTemplate(ProcessTemplate):
    """Quick debate template for discussing topics."""

    def __init__(self) -> None:
        super().__init__(
            name="quick-debate",
            description="A quick debate between proponent and critic on any topic",
            process_type="debate",
        )

    def generate_agents(self, **kwargs: Any) -> List[Dict[str, Any]]:
        topic = kwargs.get("topic", "AI Safety")
        return [
            {
                "role": "Proponent",
                "goal": f"Present strong arguments in favor of {topic}",
                "backstory": f"You are an expert advocate who believes strongly in {topic}",
                "type": "conversational",
                "verbose": True,
            },
            {
                "role": "Critic",
                "goal": f"Present thoughtful counterarguments about {topic}",
                "backstory": f"You are a critical thinker who questions aspects of {topic}",
                "type": "critic",
                "type_config": {"criticism_level": "balanced"},
                "verbose": True,
            },
            {
                "role": "Moderator",
                "goal": "Guide the debate and ensure both sides are heard",
                "backstory": "You are an impartial moderator ensuring productive discussion",
                "type": "moderator",
                "verbose": False,
            },
        ]

    def generate_tasks(self, **kwargs: Any) -> List[Dict[str, Any]]:
        topic = kwargs.get("topic", "AI Safety")
        return [
            {
                "description": f"Debate the pros and cons of {topic}",
                "expected_output": f"A balanced discussion exploring different perspectives on {topic}",
                "priority": "high",
                "agent_role": "Moderator",  # Moderator leads the debate
            }
        ]

    def get_process_config(self, **kwargs: Any) -> Dict[str, Any]:
        return {
            "rounds": kwargs.get("rounds", 3),
            "allow_critic_first": False,
            "require_consensus": False,
        }

    def estimated_time(self) -> int:
        return 180  # 3 minutes


class DecisionPanelTemplate(ProcessTemplate):
    """Decision panel template for making group decisions."""

    def __init__(self) -> None:
        super().__init__(
            name="decision-panel",
            description="A panel of experts making a decision through discussion",
            process_type="panel",
        )

    def generate_agents(self, **kwargs: Any) -> List[Dict[str, Any]]:
        decision = kwargs.get("decision", "technology choice")
        return [
            {
                "role": "Technical Expert",
                "goal": f"Evaluate technical aspects of {decision}",
                "backstory": "You are a senior technical architect with deep expertise",
                "type": "thinking",
                "verbose": True,
            },
            {
                "role": "Business Analyst",
                "goal": f"Analyze business implications of {decision}",
                "backstory": "You focus on ROI, costs, and business value",
                "type": "conversational",
                "verbose": True,
            },
            {
                "role": "Risk Assessor",
                "goal": f"Identify and evaluate risks in {decision}",
                "backstory": "You are cautious and thorough in identifying potential issues",
                "type": "critic",
                "type_config": {"criticism_level": "careful"},
                "verbose": True,
            },
        ]

    def generate_tasks(self, **kwargs: Any) -> List[Dict[str, Any]]:
        decision = kwargs.get("decision", "technology choice")
        options = kwargs.get("options", ["Option A", "Option B"])
        return [
            {
                "description": f"Evaluate and decide on {decision} between: {', '.join(options)}",
                "expected_output": "A well-reasoned decision with rationale",
                "priority": "high",
                "agent_role": "Technical Expert",  # Tech expert leads the evaluation
            }
        ]

    def get_process_config(self, **kwargs: Any) -> Dict[str, Any]:
        return {"require_consensus": kwargs.get("require_consensus", True)}

    def estimated_time(self) -> int:
        return 300  # 5 minutes


class BrainstormingTemplate(ProcessTemplate):
    """Brainstorming template for generating ideas."""

    def __init__(self) -> None:
        super().__init__(
            name="brainstorming",
            description="Creative brainstorming session with multiple perspectives",
            process_type="conversational",
        )

    def generate_agents(self, **kwargs: Any) -> List[Dict[str, Any]]:
        topic = kwargs.get("topic", "new product features")
        return [
            {
                "role": "Creative Thinker",
                "goal": f"Generate innovative ideas for {topic}",
                "backstory": "You think outside the box and love unconventional ideas",
                "type": "conversational",
                "verbose": True,
            },
            {
                "role": "Practical Implementer",
                "goal": f"Refine ideas for {topic} into actionable concepts",
                "backstory": "You excel at making ideas practical and implementable",
                "type": "thinking",
                "verbose": True,
            },
            {
                "role": "User Advocate",
                "goal": f"Ensure ideas for {topic} meet user needs",
                "backstory": "You always consider the end user's perspective",
                "type": "conversational",
                "verbose": True,
            },
        ]

    def generate_tasks(self, **kwargs: Any) -> List[Dict[str, Any]]:
        topic = kwargs.get("topic", "new product features")
        return [
            {
                "description": f"Brainstorm creative ideas for {topic}",
                "expected_output": "A list of innovative and practical ideas",
                "priority": "medium",
                "agent_role": "Creative Thinker",  # Creative thinker starts brainstorming
            }
        ]

    def get_process_config(self, **kwargs: Any) -> Dict[str, Any]:
        return {
            "min_turns": kwargs.get("min_turns", 3),
            "max_turns": kwargs.get("max_turns", 10),
        }

    def estimated_time(self) -> int:
        return 240  # 4 minutes


class CodeReviewTemplate(ProcessTemplate):
    """Code review template for reviewing code changes."""

    def __init__(self) -> None:
        super().__init__(
            name="code-review",
            description="Thorough code review with multiple expert perspectives",
            process_type="sequential",
        )

    def generate_agents(self, **kwargs: Any) -> List[Dict[str, Any]]:
        language = kwargs.get("language", "Python")
        return [
            {
                "role": "Security Reviewer",
                "goal": f"Identify security vulnerabilities in {language} code",
                "backstory": "You are a security expert who spots potential vulnerabilities",
                "type": "critic",
                "type_config": {"criticism_level": "strict"},
                "verbose": True,
            },
            {
                "role": "Performance Analyst",
                "goal": f"Analyze performance implications of {language} code",
                "backstory": "You optimize code for speed and efficiency",
                "type": "thinking",
                "verbose": True,
            },
            {
                "role": "Code Quality Expert",
                "goal": f"Ensure {language} code follows best practices",
                "backstory": "You champion clean code and maintainability",
                "type": "critic",
                "type_config": {"criticism_level": "balanced"},
                "verbose": True,
            },
        ]

    def generate_tasks(self, **kwargs: Any) -> List[Dict[str, Any]]:
        code_snippet = kwargs.get("code", "# Code to review")
        return [
            {
                "description": f"Review security aspects of the code:\n{code_snippet}",
                "expected_output": "Security analysis with identified vulnerabilities",
                "agent_role": "Security Reviewer",
            },
            {
                "description": "Analyze performance implications",
                "expected_output": "Performance analysis with optimization suggestions",
                "agent_role": "Performance Analyst",
            },
            {
                "description": "Review code quality and best practices",
                "expected_output": "Code quality assessment with improvement suggestions",
                "agent_role": "Code Quality Expert",
            },
        ]

    def estimated_time(self) -> int:
        return 360  # 6 minutes


class ResearchTeamTemplate(ProcessTemplate):
    """Research team template for investigating topics."""

    def __init__(self) -> None:
        super().__init__(
            name="research-team",
            description="Comprehensive research team investigating a topic",
            process_type="hierarchical",
        )

    def generate_agents(self, **kwargs: Any) -> List[Dict[str, Any]]:
        topic = kwargs.get("topic", "climate change")
        return [
            {
                "role": "Lead Researcher",
                "goal": f"Coordinate research efforts on {topic}",
                "backstory": "You are an experienced research director",
                "type": "moderator",
                "allow_delegation": True,
                "verbose": True,
            },
            {
                "role": "Data Analyst",
                "goal": f"Analyze data and statistics related to {topic}",
                "backstory": "You excel at finding and interpreting data",
                "type": "thinking",
                "verbose": True,
            },
            {
                "role": "Literature Reviewer",
                "goal": f"Review existing research on {topic}",
                "backstory": "You have deep knowledge of academic literature",
                "type": "conversational",
                "verbose": True,
            },
            {
                "role": "Synthesis Expert",
                "goal": f"Synthesize findings about {topic} into insights",
                "backstory": "You connect disparate information into coherent narratives",
                "type": "thinking",
                "verbose": True,
            },
        ]

    def generate_tasks(self, **kwargs: Any) -> List[Dict[str, Any]]:
        topic = kwargs.get("topic", "climate change")
        aspects = kwargs.get("aspects", ["causes", "effects", "solutions"])

        tasks = [
            {
                "description": f"Plan the research approach for {topic}",
                "expected_output": "Research plan with task assignments",
                "agent_role": "Lead Researcher",
            }
        ]

        for i, aspect in enumerate(aspects):
            # Rotate between the three research agents
            agent_roles = ["Data Analyst", "Literature Reviewer", "Synthesis Expert"]
            tasks.append(
                {
                    "description": f"Research {aspect} of {topic}",
                    "expected_output": f"Detailed findings on {aspect}",
                    "agent_role": agent_roles[i % 3],
                }
            )

        tasks.append(
            {
                "description": "Synthesize all findings into a comprehensive report",
                "expected_output": "Complete research report with key insights",
                "agent_role": "Synthesis Expert",
            }
        )

        return tasks

    def estimated_time(self) -> int:
        return 600  # 10 minutes


class AutoTemplate(ProcessTemplate):
    """Auto template that selects agents based on task description."""

    def __init__(self) -> None:
        super().__init__(
            name="auto",
            description="Automatically selects agents and process based on your task",
            process_type="auto",  # Will be determined dynamically
        )

    def generate_agents(self, **kwargs: Any) -> List[Dict[str, Any]]:
        try:
            from .agent_selector import AgentSelector
        except ImportError:
            # If relative import fails, use absolute
            from litecrew.api.agent_selector import AgentSelector

        task = kwargs.get("task", "Complete the assigned task")
        num_agents = kwargs.get("num_agents", 3)
        required_roles = kwargs.get("required_roles")

        return AgentSelector.select_agents(task, num_agents, required_roles)

    def generate_tasks(self, **kwargs: Any) -> List[Dict[str, Any]]:
        task = kwargs.get("task", "Complete the assigned task")
        agents = self.generate_agents(**kwargs)

        # Create main task assigned to the first agent
        return [
            {
                "description": task,
                "expected_output": kwargs.get(
                    "expected_output", "Task completed successfully"
                ),
                "priority": kwargs.get("priority", "medium"),
                "agent_role": agents[0]["role"] if agents else "Data Analyst",
            }
        ]

    def get_process_config(self, **kwargs: Any) -> Dict[str, Any]:
        try:
            from .agent_selector import AgentSelector
        except ImportError:
            # If relative import fails, use absolute
            from litecrew.api.agent_selector import AgentSelector

        task = kwargs.get("task", "Complete the assigned task")
        num_agents = kwargs.get("num_agents", 3)

        # Update process type based on task
        self.process_type = AgentSelector.suggest_process_type(task, num_agents)

        # Return appropriate config based on process type
        if self.process_type == "conversational":
            return {"min_turns": 3, "max_turns": 10}
        elif self.process_type == "debate":
            return {"rounds": 3}
        elif self.process_type == "panel":
            return {"require_consensus": True}
        else:
            return {}

    def estimated_time(self) -> int:
        """Get estimated execution time in seconds."""
        # This will be overridden during generation
        return 300  # 5 minutes default


# Template registry
TEMPLATES: Dict[str, ProcessTemplate] = {
    "quick-debate": QuickDebateTemplate(),
    "decision-panel": DecisionPanelTemplate(),
    "brainstorming": BrainstormingTemplate(),
    "code-review": CodeReviewTemplate(),
    "research-team": ResearchTeamTemplate(),
    "auto": AutoTemplate(),
}


def get_template(name: str) -> ProcessTemplate:
    """Get a template by name."""
    if name not in TEMPLATES:
        raise ValueError(f"Template '{name}' not found")
    return TEMPLATES[name]


def list_templates() -> List[Dict[str, Any]]:
    """List all available templates."""
    return [
        {
            "name": template.name,
            "description": template.description,
            "process_type": template.process_type,
            "estimated_time": template.estimated_time(),
        }
        for template in TEMPLATES.values()
    ]
