"""
LiteCrew Context Management System

This module provides shared context management for LiteCrew agents,
including context merging, size limits, compression, and persistence.
"""

# Lazy imports to improve startup time
__all__ = [
    "SharedContextStore",
    "ContextMetadata", 
    "ContextMerger",
    "ContextMergeStrategy",
    "ContextSizeLimiter",
    "ContextPersistence",
    "ContextConfig"
]

def __getattr__(name):
    """Lazy loading of context components."""
    if name == "SharedContextStore":
        from .shared_context import SharedContextStore
        return SharedContextStore
    elif name == "ContextMetadata":
        from .shared_context import ContextMetadata
        return ContextMetadata
    elif name == "ContextMerger":
        from .context_merger import ContextMerger
        return ContextMerger
    elif name == "ContextMergeStrategy":
        from .context_merger import ContextMergeStrategy
        return ContextMergeStrategy
    elif name == "ContextSizeLimiter":
        from .context_limiter import ContextSizeLimiter
        return ContextSizeLimiter
    elif name == "ContextPersistence":
        from .context_persistence import ContextPersistence
        return ContextPersistence
    elif name == "ContextConfig":
        from .context_config import ContextConfig
        return ContextConfig
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")