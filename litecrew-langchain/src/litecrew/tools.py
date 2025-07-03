"""
Tools for LiteCrew agents
"""

from typing import List, Any, Dict, Optional
from langchain.tools import Tool
from .delegation import DelegationManager, DelegationValidator, DelegationContext


class DelegationTool:
    """Tool that allows agents to delegate tasks to other agents."""
    
    def __init__(self, 
                 agents: List['LiteAgent'], 
                 delegation_manager: Optional[DelegationManager] = None,
                 max_depth: int = 3,
                 allowed_agents: Optional[List[str]] = None):
        """
        Initialize enhanced delegation tool with advanced capabilities.
        
        Args:
            agents: List of agents that can be delegated to
            delegation_manager: Optional delegation manager instance
            max_depth: Maximum delegation depth allowed
            allowed_agents: List of allowed agent roles for delegation
        """
        # Store data as regular attributes
        self.agents = {agent.role: agent for agent in agents}
        self.current_agent: Optional['LiteAgent'] = None
        self.name = "delegate_task"
        self.description = f"Delegate a task to another agent. Available agents: {', '.join(self.agents.keys())}. Input format: 'Ask the [Role] to [task description]'"
        
        # Initialize delegation manager
        if delegation_manager is None:
            validator = DelegationValidator(max_depth=max_depth, allowed_agents=allowed_agents)
            self.delegation_manager = DelegationManager(
                available_agents=self.agents,
                validator=validator
            )
        else:
            self.delegation_manager = delegation_manager
        
    def _delegate(self, query: str) -> str:
        """
        Delegate a task to another agent using enhanced delegation system.
        
        Args:
            query: Delegation request like "Ask the Researcher to find information about X"
            
        Returns:
            Result from the delegated agent with delegation metadata
        """
        # Parse delegation request
        role, task = self._parse_delegation(query)
        
        # Get current agent name
        from_agent = self.current_agent.role if self.current_agent else "Unknown"
        
        # Use delegation manager for enhanced delegation
        delegation_result = self.delegation_manager.delegate_task(
            from_agent=from_agent,
            task=task,
            target_agent=role,
            context={"original_query": query}
        )
        
        if delegation_result.success:
            return (f"✅ Delegation successful from {from_agent} to {role}:\n"
                   f"Task: {task}\n"
                   f"Result: {delegation_result.result}\n"
                   f"Execution time: {delegation_result.execution_time:.3f}s\n"
                   f"Delegation chain: {' → '.join(delegation_result.delegation_chain)}")
        else:
            return (f"❌ Delegation failed from {from_agent} to {role}:\n"
                   f"Task: {task}\n"
                   f"Error: {delegation_result.error}\n"
                   f"Delegation chain: {' → '.join(delegation_result.delegation_chain)}")
    
    def set_current_agent(self, agent: 'LiteAgent'):
        """Set the current agent using this delegation tool."""
        self.current_agent = agent
    
    def run(self, tool_input: str) -> str:
        """LangChain tool interface - run the delegation."""
        return self._delegate(tool_input)
            
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