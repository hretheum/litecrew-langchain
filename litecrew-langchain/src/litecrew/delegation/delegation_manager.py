"""
Delegation Manager

Core orchestration for delegation operations in LiteCrew.
Manages delegation flow, context preservation, and result aggregation.
"""

import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from .delegation_context import DelegationContext, DelegationResult
from .delegation_validators import DelegationValidator
from .delegation_strategies import DelegationStrategy, DelegationStrategyType, create_delegation_strategy


class DelegationManager:
    """
    Central manager for all delegation operations.
    
    Coordinates agent-to-agent delegation with context preservation,
    validation, and result tracking. Maintains CrewAI API compatibility
    while providing enhanced delegation capabilities.
    """
    
    def __init__(self, 
                 available_agents: Dict[str, Any] = None,
                 validator: Optional[DelegationValidator] = None,
                 strategy: Optional[DelegationStrategy] = None,
                 max_depth: int = 3,
                 allowed_agents: Optional[List[str]] = None):
        """
        Initialize delegation manager.
        
        Args:
            available_agents: Dictionary of available agents for delegation
            validator: Delegation validator instance
            strategy: Delegation strategy instance
            max_depth: Maximum delegation depth
            allowed_agents: List of allowed agent roles
        """
        self.available_agents = available_agents or {}
        self.validator = validator or DelegationValidator(max_depth, allowed_agents)
        self.strategy = strategy or create_delegation_strategy(DelegationStrategyType.ROUND_ROBIN)
        
        # Delegation tracking
        self.active_delegations: Dict[str, DelegationContext] = {}
        self.delegation_history: List[DelegationResult] = []
        self.delegation_metrics = {
            'total_delegations': 0,
            'successful_delegations': 0,
            'failed_delegations': 0,
            'average_execution_time': 0.0,
            'delegation_depths': []
        }
    
    def delegate_task(self, 
                     from_agent: str,
                     task: str,
                     context: Dict[str, Any] = None,
                     target_agent: Optional[str] = None) -> DelegationResult:
        """
        Delegate a task from one agent to another.
        
        Args:
            from_agent: Name/role of delegating agent
            task: Task description to delegate
            context: Additional context for the task
            target_agent: Specific target agent (optional, uses strategy if not provided)
            
        Returns:
            DelegationResult: Result of the delegation operation
        """
        # Create delegation context
        delegation_context = self._create_delegation_context(from_agent, context)
        
        # Determine target agent
        if target_agent is None:
            target_agent = self.strategy.select_agent(task, self.available_agents, context)
        
        # Validate delegation
        is_valid, error_message = self.validator.validate_delegation(
            delegation_context, target_agent, task
        )
        
        if not is_valid:
            return self._create_error_result(delegation_context, error_message)
        
        # Validate agent availability
        is_available, availability_error = self.validator.validate_agent_availability(
            target_agent, self.available_agents
        )
        
        if not is_available:
            return self._create_error_result(delegation_context, availability_error)
        
        # Execute delegation
        return self._execute_delegation(delegation_context, target_agent, task, context)
    
    def _create_delegation_context(self, 
                                  from_agent: str,
                                  context: Dict[str, Any] = None) -> DelegationContext:
        """Create delegation context for tracking."""
        delegation_context = DelegationContext(
            original_agent=from_agent,
            context_data=context or {}
        )
        delegation_context.add_to_chain(from_agent)
        
        self.active_delegations[delegation_context.delegation_id] = delegation_context
        return delegation_context
    
    def _execute_delegation(self, 
                           delegation_context: DelegationContext,
                           target_agent: str,
                           task: str,
                           context: Dict[str, Any] = None) -> DelegationResult:
        """Execute the actual delegation operation."""
        start_time = time.time()
        
        try:
            # Get target agent
            agent = self.available_agents[target_agent]
            
            # Add target agent to delegation chain
            delegation_context.add_to_chain(target_agent)
            
            # Prepare context with delegation metadata
            enhanced_context = self._prepare_enhanced_context(delegation_context, context)
            
            # Execute task on target agent
            result = agent.execute(task, enhanced_context)
            
            # Create success result
            execution_time = time.time() - start_time
            delegation_result = DelegationResult(
                delegation_id=delegation_context.delegation_id,
                success=True,
                result=result,
                execution_time=execution_time,
                final_agent=target_agent,
                delegation_chain=delegation_context.delegation_chain.copy()
            )
            
            # Update metrics
            self._update_metrics(delegation_result)
            
            # Clean up active delegation
            self.active_delegations.pop(delegation_context.delegation_id, None)
            
            return delegation_result
            
        except Exception as e:
            # Create error result
            execution_time = time.time() - start_time
            delegation_result = DelegationResult(
                delegation_id=delegation_context.delegation_id,
                success=False,
                result=None,
                error=str(e),
                execution_time=execution_time,
                final_agent=target_agent,
                delegation_chain=delegation_context.delegation_chain.copy()
            )
            
            # Update metrics
            self._update_metrics(delegation_result)
            
            # Clean up active delegation
            self.active_delegations.pop(delegation_context.delegation_id, None)
            
            return delegation_result
    
    def _prepare_enhanced_context(self, 
                                 delegation_context: DelegationContext,
                                 original_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prepare enhanced context with delegation metadata."""
        enhanced_context = original_context.copy() if original_context else {}
        
        # Add delegation metadata
        enhanced_context['delegation_metadata'] = {
            'delegation_id': delegation_context.delegation_id,
            'original_agent': delegation_context.original_agent,
            'delegation_chain': delegation_context.delegation_chain,
            'delegation_depth': delegation_context.delegation_depth,
            'timestamp': delegation_context.timestamp.isoformat()
        }
        
        return enhanced_context
    
    def _create_error_result(self, 
                            delegation_context: DelegationContext,
                            error_message: str) -> DelegationResult:
        """Create error result for failed delegation."""
        delegation_result = DelegationResult(
            delegation_id=delegation_context.delegation_id,
            success=False,
            result=None,
            error=error_message,
            execution_time=0.0,
            final_agent="",
            delegation_chain=delegation_context.delegation_chain.copy()
        )
        
        # Update metrics
        self._update_metrics(delegation_result)
        
        # Clean up active delegation
        self.active_delegations.pop(delegation_context.delegation_id, None)
        
        return delegation_result
    
    def _update_metrics(self, result: DelegationResult):
        """Update delegation metrics."""
        self.delegation_metrics['total_delegations'] += 1
        
        if result.success:
            self.delegation_metrics['successful_delegations'] += 1
        else:
            self.delegation_metrics['failed_delegations'] += 1
        
        # Update average execution time
        total_time = (
            self.delegation_metrics['average_execution_time'] * 
            (self.delegation_metrics['total_delegations'] - 1) + 
            result.execution_time
        )
        self.delegation_metrics['average_execution_time'] = (
            total_time / self.delegation_metrics['total_delegations']
        )
        
        # Track delegation depths
        self.delegation_metrics['delegation_depths'].append(len(result.delegation_chain))
        
        # Store in history
        self.delegation_history.append(result)
    
    def get_delegation_metrics(self) -> Dict[str, Any]:
        """Get current delegation metrics."""
        metrics = self.delegation_metrics.copy()
        
        # Calculate additional metrics
        if metrics['delegation_depths']:
            metrics['max_delegation_depth'] = max(metrics['delegation_depths'])
            metrics['avg_delegation_depth'] = sum(metrics['delegation_depths']) / len(metrics['delegation_depths'])
        else:
            metrics['max_delegation_depth'] = 0
            metrics['avg_delegation_depth'] = 0
        
        metrics['success_rate'] = (
            metrics['successful_delegations'] / metrics['total_delegations']
            if metrics['total_delegations'] > 0 else 0
        )
        
        return metrics
    
    def get_active_delegations(self) -> Dict[str, DelegationContext]:
        """Get currently active delegations."""
        return self.active_delegations.copy()
    
    def get_delegation_history(self, limit: Optional[int] = None) -> List[DelegationResult]:
        """Get delegation history."""
        if limit is None:
            return self.delegation_history.copy()
        return self.delegation_history[-limit:]
    
    def clear_history(self):
        """Clear delegation history and reset metrics."""
        self.delegation_history.clear()
        self.delegation_metrics = {
            'total_delegations': 0,
            'successful_delegations': 0,
            'failed_delegations': 0,
            'average_execution_time': 0.0,
            'delegation_depths': []
        }
    
    def set_strategy(self, strategy: DelegationStrategy):
        """Change delegation strategy."""
        self.strategy = strategy
    
    def add_agent(self, role: str, agent: Any):
        """Add an agent to available agents."""
        self.available_agents[role] = agent
    
    def remove_agent(self, role: str):
        """Remove an agent from available agents."""
        self.available_agents.pop(role, None)