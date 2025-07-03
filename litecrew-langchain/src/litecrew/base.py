"""
Base classes and mixins for LiteCrew models.

Provides Pydantic-compatible API for dataclasses to ensure
backward compatibility during migration.
"""

from dataclasses import asdict, fields, replace
from typing import Dict, Any, Optional, Type, TypeVar, get_type_hints
import json
from datetime import datetime
from enum import Enum

T = TypeVar('T')


class PydanticCompatible:
    """
    Mixin that provides Pydantic-like methods for dataclasses.
    
    Enables drop-in replacement of Pydantic models with dataclasses
    while maintaining API compatibility for the most common methods.
    """
    
    def model_dump(self, 
                   *, 
                   mode: str = 'python',
                   exclude: Optional[set] = None,
                   exclude_unset: bool = False,
                   exclude_defaults: bool = False,
                   exclude_none: bool = False) -> Dict[str, Any]:
        """
        Generate a dictionary representation of the model.
        
        Args:
            mode: The mode to use for serialization ('python' or 'json')
            exclude: Fields to exclude from the output
            exclude_unset: Whether to exclude fields that weren't explicitly set
            exclude_defaults: Whether to exclude fields with default values
            exclude_none: Whether to exclude fields with None values
            
        Returns:
            Dictionary representation of the model
        """
        data = asdict(self)
        
        # Handle exclusions
        if exclude:
            data = {k: v for k, v in data.items() if k not in exclude}
            
        # Exclude private fields (start with _)
        data = {k: v for k, v in data.items() if not k.startswith('_')}
        
        # Exclude None values if requested
        if exclude_none:
            data = {k: v for k, v in data.items() if v is not None}
            
        # Handle JSON mode - convert non-serializable types
        if mode == 'json':
            data = self._make_json_serializable(data)
            
        return data
    
    def model_dump_json(self, 
                        *, 
                        indent: Optional[int] = None,
                        exclude: Optional[set] = None,
                        exclude_none: bool = False) -> str:
        """
        Generate a JSON representation of the model.
        
        Args:
            indent: Indentation for pretty printing
            exclude: Fields to exclude from the output
            exclude_none: Whether to exclude None values
            
        Returns:
            JSON string representation
        """
        data = self.model_dump(mode='json', exclude=exclude, exclude_none=exclude_none)
        return json.dumps(data, indent=indent, default=str)
    
    @classmethod
    def model_validate(cls: Type[T], obj: Any) -> T:
        """
        Validate and create an instance from a dictionary or object.
        
        Args:
            obj: Dictionary or object to validate and convert
            
        Returns:
            Instance of the class
            
        Raises:
            TypeError: If the input cannot be converted
            ValueError: If validation fails
        """
        if isinstance(obj, dict):
            # Filter out any extra fields not in the dataclass
            hints = get_type_hints(cls)
            valid_fields = {f.name for f in fields(cls)}
            filtered_data = {k: v for k, v in obj.items() if k in valid_fields}
            return cls(**filtered_data)
        elif isinstance(obj, cls):
            return obj
        else:
            raise TypeError(f"Cannot validate {type(obj)} as {cls.__name__}")
    
    @classmethod
    def model_validate_json(cls: Type[T], json_data: str) -> T:
        """
        Validate and create an instance from JSON string.
        
        Args:
            json_data: JSON string to parse and validate
            
        Returns:
            Instance of the class
        """
        data = json.loads(json_data)
        return cls.model_validate(data)
    
    def model_copy(self: T, *, update: Optional[Dict[str, Any]] = None, deep: bool = True) -> T:
        """
        Create a copy of the model, optionally with updated values.
        
        Args:
            update: Dictionary of values to update
            deep: Whether to deep copy (not fully implemented)
            
        Returns:
            New instance with updated values
        """
        if update:
            # Filter out private fields from update
            update = {k: v for k, v in update.items() if not k.startswith('_')}
            return replace(self, **update)
        return replace(self)
    
    @classmethod
    def model_fields(cls) -> Dict[str, Any]:
        """
        Get information about model fields.
        
        Returns:
            Dictionary of field information
        """
        return {f.name: {
            'type': f.type,
            'default': f.default if f.default is not f.default_factory else None,
            'default_factory': f.default_factory if f.default_factory is not f.default else None,
            'required': f.default is f.default_factory is None
        } for f in fields(cls) if not f.name.startswith('_')}
    
    @classmethod
    def model_config(cls) -> Dict[str, Any]:
        """
        Get model configuration (empty for dataclasses).
        
        Returns:
            Empty dict for compatibility
        """
        return {}
    
    def dict(self, **kwargs) -> Dict[str, Any]:
        """Alias for model_dump() for backward compatibility."""
        return self.model_dump(**kwargs)
    
    def json(self, **kwargs) -> str:
        """Alias for model_dump_json() for backward compatibility."""
        return self.model_dump_json(**kwargs)
    
    @classmethod
    def parse_obj(cls: Type[T], obj: Any) -> T:
        """Alias for model_validate() for backward compatibility."""
        return cls.model_validate(obj)
    
    @classmethod
    def parse_raw(cls: Type[T], b: str) -> T:
        """Alias for model_validate_json() for backward compatibility."""
        return cls.model_validate_json(b)
    
    def copy(self: T, **kwargs) -> T:
        """Alias for model_copy() for backward compatibility."""
        return self.model_copy(**kwargs)
    
    def _make_json_serializable(self, data: Any) -> Any:
        """
        Recursively convert non-JSON-serializable types.
        
        Args:
            data: Data to convert
            
        Returns:
            JSON-serializable version of the data
        """
        if isinstance(data, dict):
            return {k: self._make_json_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._make_json_serializable(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, Enum):
            return data.value
        elif hasattr(data, 'model_dump'):
            # Handle nested Pydantic-compatible objects
            return data.model_dump(mode='json')
        else:
            return data


# For backward compatibility
BaseModel = PydanticCompatible


def Field(
    default: Any = ...,
    *,
    default_factory: Optional[Any] = None,
    alias: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[bool] = None,
    include: Optional[bool] = None,
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
    **extra: Any,
) -> Any:
    """
    Compatibility wrapper for Pydantic Field().
    
    In dataclasses, most of these parameters are ignored,
    but we accept them for backward compatibility.
    
    Returns:
        The default value or a field with default_factory
    """
    from dataclasses import field, MISSING
    
    if default is not ...:
        return default
    elif default_factory is not None:
        return field(default_factory=default_factory)
    else:
        return MISSING