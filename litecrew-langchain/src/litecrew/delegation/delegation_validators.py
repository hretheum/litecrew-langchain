"""
Delegation Validation and Constraints

Provides validation logic for delegation operations to ensure safe and
controlled delegation within configured constraints.
"""

from typing import List, Dict, Optional
from .delegation_context import DelegationContext


class DelegationValidator:
    """
    Validates delegation operations against configured constraints.
    
    Ensures delegation safety by checking:
    - Maximum delegation depth
    - Allowed agent lists
    - Circular delegation prevention
    - Resource constraints
    """
    
    def __init__(self, 
                 max_depth: int = 3,
                 allowed_agents: Optional[List[str]] = None,
                 prevent_cycles: bool = True):
        """
        Initialize delegation validator.
        
        Args:
            max_depth: Maximum delegation depth allowed
            allowed_agents: List of agents that can be delegated to
            prevent_cycles: Whether to prevent circular delegation
        """
        self.max_depth = max_depth
        self.allowed_agents = allowed_agents or []
        self.prevent_cycles = prevent_cycles
    
    def validate_delegation(self, 
                          context: DelegationContext,
                          target_agent: str,
                          task: str) -> tuple[bool, Optional[str]]:
        """
        Validate a delegation request.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check delegation depth
        if context.delegation_depth >= self.max_depth:
            return False, f"Maximum delegation depth ({self.max_depth}) exceeded"
        
        # Check allowed agents
        if self.allowed_agents and target_agent not in self.allowed_agents:
            return False, f"Delegation to '{target_agent}' not allowed. Allowed agents: {self.allowed_agents}"
        
        # Check for circular delegation
        if self.prevent_cycles and target_agent in context.delegation_chain:
            return False, f"Circular delegation detected. '{target_agent}' is already in delegation chain: {context.delegation_chain}"
        
        # Check task validity
        if not task or not task.strip():
            return False, "Cannot delegate empty task"
        
        return True, None
    
    def validate_agent_availability(self, 
                                  target_agent: str,
                                  available_agents: Dict[str, any]) -> tuple[bool, Optional[str]]:
        """
        Validate that target agent is available for delegation.
        
        Args:
            target_agent: Name/role of target agent
            available_agents: Dictionary of available agents
            
        Returns:
            tuple: (is_available, error_message)
        """
        if target_agent not in available_agents:
            return False, f"Agent '{target_agent}' not found in available agents: {list(available_agents.keys())}"
        
        agent = available_agents[target_agent]
        
        # Check if agent allows delegation
        if hasattr(agent, 'allow_delegation') and not agent.allow_delegation:
            return False, f"Agent '{target_agent}' does not allow delegation"
        
        return True, None
    
    def get_validation_summary(self) -> Dict[str, any]:
        """Get current validation configuration summary."""
        return {
            "max_depth": self.max_depth,
            "allowed_agents": self.allowed_agents,
            "prevent_cycles": self.prevent_cycles,
            "total_allowed_agents": len(self.allowed_agents) if self.allowed_agents else "unlimited"
        }