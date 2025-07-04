"""
Tools for LiteCrew agents
"""

from typing import TYPE_CHECKING, List

from langchain.tools import Tool

if TYPE_CHECKING:
    from litecrew.agent import LiteAgent


class DelegationTool(Tool):
    """Tool that allows agents to delegate tasks to other agents."""

    def __init__(self, agents: List["LiteAgent"]):
        """
        Initialize delegation tool.

        Args:
            agents: List of agents that can be delegated to
        """
        # Store agents in a way that works with Pydantic models
        agents_dict = {agent.role: agent for agent in agents}

        super().__init__(
            name="delegate_task",
            description=f"Delegate a task to another agent. Available agents: {', '.join(agents_dict.keys())}. Input format: 'Ask the [Role] to [task description]'",
            func=lambda query: self._delegate_with_agents(query, agents_dict),
        )

    def _delegate_with_agents(self, query: str, agents_dict: dict) -> str:
        """
        Delegate a task to another agent.

        Args:
            query: Delegation request like "Ask the Researcher to find information about X"
            agents_dict: Dictionary of agents by role

        Returns:
            Result from the delegated agent
        """
        # Parse delegation request
        role, task = self._parse_delegation(query)

        if role in agents_dict:
            agent = agents_dict[role]
            result = agent.execute(task)
            return f"Delegation result from {role}: {result}"
        else:
            available = ", ".join(agents_dict.keys())
            return f"Agent role '{role}' not found. Available agents: {available}"

    def _parse_delegation(self, query: str) -> tuple[str, str]:
        """Parse delegation query to extract role and task."""
        # Common patterns
        patterns = [
            r"ask the (\w+) to (.+)",
            r"delegate to (\w+): (.+)",
            r"have the (\w+) (.+)",
            r"get the (\w+) to (.+)",
        ]

        import re

        for pattern in patterns:
            match = re.match(pattern, query.lower())
            if match:
                role = match.group(1).title()
                task = match.group(2)
                return role, task

        # Fallback: assume first word is role
        parts = query.split(" ", 1)
        if len(parts) >= 2:
            return parts[0].title(), parts[1]
        else:
            return "Unknown", query
