"""
Delegation Context Management

Handles context preservation and metadata tracking for delegation chains.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import uuid4


@dataclass
class DelegationContext:
    """
    Tracks delegation context and metadata through delegation chains.
    
    Maintains compatibility with CrewAI's context passing while adding
    enhanced tracking capabilities.
    """
    
    delegation_id: str = field(default_factory=lambda: str(uuid4()))
    original_agent: str = ""
    delegation_chain: List[str] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)
    delegation_depth: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    parent_delegation_id: Optional[str] = None
    
    def add_to_chain(self, agent_role: str) -> None:
        """Add an agent to the delegation chain."""
        self.delegation_chain.append(agent_role)
        self.delegation_depth = len(self.delegation_chain) - 1
    
    def can_delegate_to(self, target_agent: str, allowed_agents: List[str]) -> bool:
        """Check if delegation to target agent is allowed."""
        if allowed_agents and target_agent not in allowed_agents:
            return False
        
        # Prevent circular delegation
        if target_agent in self.delegation_chain:
            return False
            
        return True
    
    def create_child_context(self, new_agent: str) -> "DelegationContext":
        """Create a child context for sub-delegation."""
        child_context = DelegationContext(
            original_agent=self.original_agent,
            delegation_chain=self.delegation_chain.copy(),
            context_data=self.context_data.copy(),
            delegation_depth=self.delegation_depth,
            parent_delegation_id=self.delegation_id
        )
        child_context.add_to_chain(new_agent)
        return child_context


@dataclass
class DelegationResult:
    """
    Result of a delegation operation with metadata.
    """
    
    delegation_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    final_agent: str = ""
    delegation_chain: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "delegation_id": self.delegation_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "final_agent": self.final_agent,
            "delegation_chain": self.delegation_chain,
            "timestamp": self.timestamp.isoformat()
        }