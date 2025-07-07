"""Process Factory for creating different process types"""

from typing import Any, Dict, Optional, Type

from .base import BaseProcess, ProcessConfig


class ProcessFactory:
    """Factory for creating process instances"""
    
    _registry: Dict[str, Type[BaseProcess]] = {}
    
    @classmethod
    def register(cls, name: str, process_class: Type[BaseProcess]) -> None:
        """Register a process type"""
        cls._registry[name.lower()] = process_class
        
    @classmethod
    def create(
        cls, 
        process_type: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> BaseProcess:
        """Create a process instance"""
        process_type = process_type.lower()
        
        if process_type not in cls._registry:
            raise ValueError(
                f"Unknown process type: {process_type}. "
                f"Available types: {list(cls._registry.keys())}"
            )
            
        process_class = cls._registry[process_type]
        
        # Create config if provided
        if config:
            # Extract ProcessConfig fields
            config_fields = {
                'verbose', 'max_iterations', 'timeout', 'callbacks', 'metadata'
            }
            base_config = {k: v for k, v in config.items() if k in config_fields}
            process_config = ProcessConfig(**base_config)
            
            # Pass remaining fields as process-specific config
            specific_config = {k: v for k, v in config.items() if k not in config_fields}
            
            # Some process types might accept additional config
            if specific_config and hasattr(process_class, 'from_config'):
                return process_class.from_config(process_config, specific_config)
            else:
                return process_class(process_config)
        else:
            return process_class()
            
    @classmethod
    def list_types(cls) -> list[str]:
        """List available process types"""
        return list(cls._registry.keys())
        
    @classmethod
    def clear_registry(cls) -> None:
        """Clear the registry (mainly for testing)"""
        cls._registry.clear()