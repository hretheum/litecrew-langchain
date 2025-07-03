"""
Delegation Strategies

Implements different delegation patterns and routing strategies
for agent-to-agent task delegation.
"""

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from enum import Enum
import random
from collections import defaultdict


class DelegationStrategyType(Enum):
    """Available delegation strategies."""
    ROUND_ROBIN = "round_robin"
    SKILL_BASED = "skill_based"
    LOAD_BALANCED = "load_balanced"
    RANDOM = "random"
    HIERARCHICAL = "hierarchical"


class DelegationStrategy(ABC):
    """
    Abstract base class for delegation strategies.
    
    Defines the interface for implementing different delegation
    routing patterns.
    """
    
    @abstractmethod
    def select_agent(self, 
                    task: str,
                    available_agents: Dict[str, Any],
                    context: Dict[str, Any] = None) -> str:
        """
        Select the best agent for delegating the given task.
        
        Args:
            task: Task description
            available_agents: Dictionary of available agents
            context: Additional context for decision making
            
        Returns:
            str: Selected agent role/name
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        pass


class RoundRobinStrategy(DelegationStrategy):
    """
    Round-robin delegation strategy.
    
    Cycles through agents in order, ensuring even distribution
    of delegated tasks.
    """
    
    def __init__(self):
        self.agent_index = 0
        self.agent_order = []
    
    def select_agent(self, 
                    task: str,
                    available_agents: Dict[str, Any],
                    context: Dict[str, Any] = None) -> str:
        """Select next agent in round-robin order."""
        if not available_agents:
            raise ValueError("No agents available for delegation")
        
        # Update agent order if agents changed
        current_agents = list(available_agents.keys())
        if self.agent_order != current_agents:
            self.agent_order = current_agents
            self.agent_index = 0
        
        # Select next agent
        selected_agent = self.agent_order[self.agent_index]
        self.agent_index = (self.agent_index + 1) % len(self.agent_order)
        
        return selected_agent
    
    def get_strategy_name(self) -> str:
        return "round_robin"


class SkillBasedStrategy(DelegationStrategy):
    """
    Skill-based delegation strategy.
    
    Selects agents based on their skills and the task requirements.
    """
    
    def __init__(self, skill_keywords: Optional[Dict[str, List[str]]] = None):
        """
        Initialize skill-based strategy.
        
        Args:
            skill_keywords: Dictionary mapping agent roles to skill keywords
        """
        self.skill_keywords = skill_keywords or {}
    
    def select_agent(self, 
                    task: str,
                    available_agents: Dict[str, Any],
                    context: Dict[str, Any] = None) -> str:
        """Select agent based on skill matching."""
        if not available_agents:
            raise ValueError("No agents available for delegation")
        
        task_lower = task.lower()
        best_agent = None
        best_score = -1
        
        for agent_role, agent in available_agents.items():
            score = self._calculate_skill_match(agent_role, task_lower)
            if score > best_score:
                best_score = score
                best_agent = agent_role
        
        return best_agent or list(available_agents.keys())[0]
    
    def _calculate_skill_match(self, agent_role: str, task: str) -> int:
        """Calculate skill match score for an agent."""
        if agent_role not in self.skill_keywords:
            return 0
        
        keywords = self.skill_keywords[agent_role]
        score = sum(1 for keyword in keywords if keyword.lower() in task)
        
        # Bonus for role name matching
        if agent_role.lower() in task:
            score += 2
        
        return score
    
    def get_strategy_name(self) -> str:
        return "skill_based"


class LoadBalancedStrategy(DelegationStrategy):
    """
    Load-balanced delegation strategy.
    
    Distributes tasks based on current agent workload.
    """
    
    def __init__(self):
        self.agent_workload = defaultdict(int)
    
    def select_agent(self, 
                    task: str,
                    available_agents: Dict[str, Any],
                    context: Dict[str, Any] = None) -> str:
        """Select agent with lowest current workload."""
        if not available_agents:
            raise ValueError("No agents available for delegation")
        
        # Find agent with minimum workload
        min_workload = float('inf')
        selected_agent = None
        
        for agent_role in available_agents.keys():
            workload = self.agent_workload[agent_role]
            if workload < min_workload:
                min_workload = workload
                selected_agent = agent_role
        
        # Increment workload for selected agent
        if selected_agent:
            self.agent_workload[selected_agent] += 1
        
        return selected_agent or list(available_agents.keys())[0]
    
    def task_completed(self, agent_role: str):
        """Mark task as completed for an agent."""
        if self.agent_workload[agent_role] > 0:
            self.agent_workload[agent_role] -= 1
    
    def get_strategy_name(self) -> str:
        return "load_balanced"


class RandomStrategy(DelegationStrategy):
    """
    Random delegation strategy.
    
    Randomly selects agents for delegation.
    """
    
    def select_agent(self, 
                    task: str,
                    available_agents: Dict[str, Any],
                    context: Dict[str, Any] = None) -> str:
        """Randomly select an agent."""
        if not available_agents:
            raise ValueError("No agents available for delegation")
        
        return random.choice(list(available_agents.keys()))
    
    def get_strategy_name(self) -> str:
        return "random"


class HierarchicalStrategy(DelegationStrategy):
    """
    Hierarchical delegation strategy.
    
    Routes tasks through a manager-worker hierarchy.
    """
    
    def __init__(self, manager_role: str, worker_roles: List[str]):
        """
        Initialize hierarchical strategy.
        
        Args:
            manager_role: Role of the manager agent
            worker_roles: List of worker agent roles
        """
        self.manager_role = manager_role
        self.worker_roles = worker_roles
    
    def select_agent(self, 
                    task: str,
                    available_agents: Dict[str, Any],
                    context: Dict[str, Any] = None) -> str:
        """Select agent based on hierarchical rules."""
        if not available_agents:
            raise ValueError("No agents available for delegation")
        
        # Check if this is a management task
        if self._is_management_task(task):
            if self.manager_role in available_agents:
                return self.manager_role
        
        # Route to appropriate worker
        available_workers = [role for role in self.worker_roles if role in available_agents]
        if available_workers:
            return available_workers[0]  # Could be enhanced with skill matching
        
        # Fallback to any available agent
        return list(available_agents.keys())[0]
    
    def _is_management_task(self, task: str) -> bool:
        """Check if task requires management/coordination."""
        management_keywords = ['coordinate', 'manage', 'organize', 'plan', 'review', 'oversee']
        task_lower = task.lower()
        return any(keyword in task_lower for keyword in management_keywords)
    
    def get_strategy_name(self) -> str:
        return "hierarchical"


def create_delegation_strategy(strategy_type: DelegationStrategyType, 
                              **kwargs) -> DelegationStrategy:
    """
    Factory function to create delegation strategies.
    
    Args:
        strategy_type: Type of strategy to create
        **kwargs: Strategy-specific parameters
        
    Returns:
        DelegationStrategy: Configured strategy instance
    """
    if strategy_type == DelegationStrategyType.ROUND_ROBIN:
        return RoundRobinStrategy()
    elif strategy_type == DelegationStrategyType.SKILL_BASED:
        return SkillBasedStrategy(kwargs.get('skill_keywords'))
    elif strategy_type == DelegationStrategyType.LOAD_BALANCED:
        return LoadBalancedStrategy()
    elif strategy_type == DelegationStrategyType.RANDOM:
        return RandomStrategy()
    elif strategy_type == DelegationStrategyType.HIERARCHICAL:
        return HierarchicalStrategy(
            kwargs.get('manager_role', 'manager'),
            kwargs.get('worker_roles', [])
        )
    else:
        raise ValueError(f"Unknown delegation strategy: {strategy_type}")