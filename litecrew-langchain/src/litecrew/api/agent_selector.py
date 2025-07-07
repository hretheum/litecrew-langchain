"""Automatic agent selection logic for crews."""

from typing import Any, Dict, List, Optional


class AgentSelector:
    """Automatically select appropriate agents based on task requirements."""

    # Default agent configurations for common roles
    DEFAULT_AGENTS = {
        "analyst": {
            "role": "Data Analyst",
            "goal": "Analyze data and provide insights",
            "backstory": "Expert in data analysis and interpretation",
            "type": "thinking",
        },
        "writer": {
            "role": "Content Writer",
            "goal": "Create clear and engaging content",
            "backstory": "Skilled writer with expertise in various formats",
            "type": "conversational",
        },
        "developer": {
            "role": "Software Developer",
            "goal": "Design and implement technical solutions",
            "backstory": "Experienced developer with broad technical knowledge",
            "type": "thinking",
        },
        "reviewer": {
            "role": "Quality Reviewer",
            "goal": "Ensure quality and identify improvements",
            "backstory": "Detail-oriented reviewer focused on excellence",
            "type": "critic",
            "type_config": {"criticism_level": "balanced"},
        },
        "manager": {
            "role": "Project Manager",
            "goal": "Coordinate efforts and ensure successful outcomes",
            "backstory": "Experienced manager skilled in orchestration",
            "type": "moderator",
        },
        "researcher": {
            "role": "Research Specialist",
            "goal": "Conduct thorough research and gather information",
            "backstory": "Methodical researcher with deep investigative skills",
            "type": "thinking",
        },
        "strategist": {
            "role": "Strategic Planner",
            "goal": "Develop strategies and long-term plans",
            "backstory": "Strategic thinker focused on optimal outcomes",
            "type": "thinking",
        },
        "communicator": {
            "role": "Communication Expert",
            "goal": "Facilitate clear communication and understanding",
            "backstory": "Expert in interpersonal and written communication",
            "type": "conversational",
        },
    }

    # Keywords that suggest specific agent types
    TASK_KEYWORDS = {
        "analyze": ["analyst", "reviewer"],
        "write": ["writer", "communicator"],
        "develop": ["developer", "strategist"],
        "review": ["reviewer", "analyst"],
        "manage": ["manager", "strategist"],
        "research": ["researcher", "analyst"],
        "plan": ["strategist", "manager"],
        "communicate": ["communicator", "writer"],
        "code": ["developer", "reviewer"],
        "test": ["developer", "reviewer"],
        "design": ["developer", "strategist"],
        "evaluate": ["analyst", "reviewer"],
        "create": ["writer", "developer"],
        "coordinate": ["manager", "communicator"],
        "investigate": ["researcher", "analyst"],
        "optimize": ["analyst", "developer"],
        "document": ["writer", "communicator"],
        "present": ["communicator", "writer"],
        "implement": ["developer", "manager"],
        "assess": ["analyst", "reviewer"],
    }

    @classmethod
    def select_agents(
        cls,
        task_description: str,
        num_agents: int = 3,
        required_roles: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Select appropriate agents based on task description.

        Args:
            task_description: Description of the task
            num_agents: Number of agents to select (default: 3)
            required_roles: List of required agent roles

        Returns:
            List of agent configurations
        """
        if required_roles:
            # Use specific required roles
            agents = []
            for role in required_roles[:num_agents]:
                if role.lower() in cls.DEFAULT_AGENTS:
                    agents.append(cls.DEFAULT_AGENTS[role.lower()].copy())
                else:
                    # Create custom agent for unknown role
                    agents.append(
                        {
                            "role": role,
                            "goal": f"Fulfill responsibilities as {role}",
                            "backstory": f"Experienced professional in {role} role",
                            "type": "conversational",
                        }
                    )
            return agents

        # Analyze task description to determine agent types
        task_lower = task_description.lower()
        suggested_types = set()

        # Find matching keywords
        for keyword, agent_types in cls.TASK_KEYWORDS.items():
            if keyword in task_lower:
                suggested_types.update(agent_types)

        # If no matches, use default set
        if not suggested_types:
            suggested_types = {"analyst", "developer", "reviewer"}

        # Convert to list and ensure we have enough agents
        agent_types = list(suggested_types)

        # Add more agents if needed
        all_types = list(cls.DEFAULT_AGENTS.keys())
        while len(agent_types) < num_agents:
            for agent_type in all_types:
                if agent_type not in agent_types:
                    agent_types.append(agent_type)
                    break
            if len(agent_types) >= num_agents:
                break

        # Create agent configurations
        agents = []
        for agent_type in agent_types[:num_agents]:
            agent_config = cls.DEFAULT_AGENTS[agent_type].copy()
            # Customize goal based on task
            agent_config["goal"] = (
                f"{agent_config['goal']} for: {task_description[:100]}"
            )
            agents.append(agent_config)

        # Always include a manager/coordinator if we have 3+ agents
        if num_agents >= 3 and not any(a["type"] == "moderator" for a in agents):
            # Replace the last agent with a manager
            agents[-1] = cls.DEFAULT_AGENTS["manager"].copy()
            agents[-1][
                "goal"
            ] = f"Coordinate team efforts for: {task_description[:100]}"

        return agents

    @classmethod
    def suggest_process_type(cls, task_description: str, num_agents: int) -> str:
        """
        Suggest an appropriate process type based on task and team size.

        Args:
            task_description: Description of the task
            num_agents: Number of agents

        Returns:
            Suggested process type
        """
        task_lower = task_description.lower()

        # Check for specific keywords that suggest process types
        if any(
            word in task_lower
            for word in ["debate", "discuss", "argue", "pros and cons"]
        ):
            return "debate"
        elif any(
            word in task_lower
            for word in ["decide", "choose", "select", "evaluate options"]
        ):
            return "panel"
        elif any(
            word in task_lower
            for word in ["brainstorm", "ideas", "creative", "innovate"]
        ):
            return "conversational"
        elif any(
            word in task_lower
            for word in ["step by step", "sequential", "ordered", "phases"]
        ):
            return "sequential"
        elif num_agents > 3 and any(
            word in task_lower for word in ["coordinate", "manage", "lead"]
        ):
            return "hierarchical"

        # Default based on team size
        if num_agents <= 2:
            return "conversational"
        elif num_agents <= 4:
            return "sequential"
        else:
            return "hierarchical"

    @classmethod
    def estimate_execution_time(cls, task_description: str, num_agents: int) -> int:
        """
        Estimate execution time in seconds based on task complexity.

        Args:
            task_description: Description of the task
            num_agents: Number of agents

        Returns:
            Estimated time in seconds
        """
        base_time = 60  # 1 minute base

        # Add time based on task complexity (word count as proxy)
        word_count = len(task_description.split())
        complexity_time = min(word_count * 2, 120)  # Max 2 minutes for complexity

        # Add time based on number of agents
        agent_time = num_agents * 30  # 30 seconds per agent

        # Add time for specific keywords
        task_lower = task_description.lower()
        if any(word in task_lower for word in ["research", "analyze", "investigate"]):
            complexity_time += 60
        if any(
            word in task_lower for word in ["comprehensive", "detailed", "thorough"]
        ):
            complexity_time += 60

        return base_time + complexity_time + agent_time
