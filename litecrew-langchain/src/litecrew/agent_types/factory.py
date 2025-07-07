"""Factory for creating typed agents."""

from typing import Any, Dict, Optional, Type

from .base import AgentType, AgentTypeConfig
from .types import (
    ConversationalAgent,
    CriticAgent,
    ModeratorAgent,
    ThinkingAgent,
)


class AgentTypeFactory:
    """Factory for creating and managing agent types."""
    
    # Registry of available agent types
    _registry: Dict[str, Type[AgentType]] = {
        "conversational": ConversationalAgent,
        "thinking": ThinkingAgent,
        "moderator": ModeratorAgent,
        "critic": CriticAgent,
    }
    
    # Default configurations for each type
    _default_configs: Dict[str, AgentTypeConfig] = {}
    
    @classmethod
    def register_type(cls, name: str, agent_type_class: Type[AgentType], default_config: Optional[AgentTypeConfig] = None) -> None:
        """Register a new agent type."""
        cls._registry[name.lower()] = agent_type_class
        if default_config:
            cls._default_configs[name.lower()] = default_config
    
    @classmethod
    def create(cls, type_name: str, config: Optional[Dict[str, Any]] = None) -> AgentType:
        """Create an agent type instance."""
        type_name = type_name.lower()
        
        if type_name not in cls._registry:
            raise ValueError(f"Unknown agent type: {type_name}. Available types: {list(cls._registry.keys())}")
        
        agent_type_class = cls._registry[type_name]
        
        # Get default config if available
        if type_name in cls._default_configs:
            type_config = cls._default_configs[type_name]
            # Override with provided config
            if config:
                for key, value in config.items():
                    if hasattr(type_config, key):
                        setattr(type_config, key, value)
        else:
            # Create config from provided dict or use class default
            type_config = agent_type_class.get_default_config()
            if config:
                for key, value in config.items():
                    if hasattr(type_config, key):
                        setattr(type_config, key, value)
        
        return agent_type_class(type_config)
    
    @classmethod
    def list_types(cls) -> list[str]:
        """List all available agent types."""
        return list(cls._registry.keys())
    
    @classmethod
    def get_type_info(cls, type_name: str) -> Dict[str, Any]:
        """Get information about an agent type."""
        type_name = type_name.lower()
        
        if type_name not in cls._registry:
            raise ValueError(f"Unknown agent type: {type_name}")
        
        agent_type_class = cls._registry[type_name]
        default_config = agent_type_class.get_default_config()
        
        return {
            "name": type_name,
            "description": default_config.description,
            "configurable_options": [
                attr for attr in dir(default_config) 
                if not attr.startswith('_') and attr not in ['name', 'description']
            ],
            "default_config": {
                attr: getattr(default_config, attr) 
                for attr in dir(default_config) 
                if not attr.startswith('_')
            }
        }