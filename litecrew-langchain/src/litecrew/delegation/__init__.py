"""
LiteCrew Delegation System

This module provides enhanced delegation capabilities for LiteCrew agents,
including context preservation, delegation history tracking, and validation.
"""

# Lazy imports to improve startup time
__all__ = [
    "DelegationManager",
    "DelegationContext", 
    "DelegationResult",
    "DelegationStrategy",
    "DelegationValidator"
]

def __getattr__(name):
    """Lazy loading of delegation components."""
    if name == "DelegationManager":
        from .delegation_manager import DelegationManager
        return DelegationManager
    elif name == "DelegationContext":
        from .delegation_context import DelegationContext
        return DelegationContext
    elif name == "DelegationResult":
        from .delegation_context import DelegationResult
        return DelegationResult
    elif name == "DelegationStrategy":
        from .delegation_strategies import DelegationStrategy
        return DelegationStrategy
    elif name == "DelegationValidator":
        from .delegation_validators import DelegationValidator
        return DelegationValidator
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")