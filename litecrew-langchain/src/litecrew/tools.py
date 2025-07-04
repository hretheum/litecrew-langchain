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
        self._agents = {agent.role: agent for agent in agents}

        super().__init__(
            name="delegate_task",
            description=f"Delegate a task to another agent. Available agents: {', '.join(self._agents.keys())}. Input format: 'Ask the [Role] to [task description]'",
            func=self._delegate,
        )

    def _delegate(self, query: str) -> str:
        """
        Delegate a task to another agent.

        Args:
            query: Delegation request like "Ask the Researcher to find information about X"

        Returns:
            Result from the delegated agent
        """
        # Parse delegation request
        role, task = self._parse_delegation(query)

        if role in self._agents:
            agent = self._agents[role]
            result = agent.execute(task)
            return f"Delegation result from {role}: {result}"
        else:
            available = ", ".join(self._agents.keys())
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
