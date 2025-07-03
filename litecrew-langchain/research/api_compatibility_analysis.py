#!/usr/bin/env python3
"""
Analyze API compatibility when migrating from Pydantic.
"""

from typing import List, Optional, Dict, Any
import inspect

# Current Pydantic usage patterns in LiteCrew

print("=== PYDANTIC API USAGE IN LITECREW ===\n")

# 1. BaseModel features we use
print("1. BaseModel Features Used:")
print("   - Field() with validators (ge, le, min_length)")
print("   - model_config with arbitrary_types_allowed")
print("   - field_validator decorators")
print("   - Optional fields with defaults")
print("   - List fields with default_factory")
print("   - model_dump() for serialization")
print("   - Automatic type conversion")

# 2. How each alternative handles these
print("\n2. Feature Support by Alternative:\n")

features = [
    "Type validation",
    "Field validators", 
    "Default values",
    "Default factories",
    "Serialization",
    "Deserialization",
    "Nested models",
    "Custom validators",
    "Type coercion",
    "Field aliases",
    "JSON Schema",
    "IDE support"
]

support_matrix = {
    "Pydantic": ["✅"] * len(features),
    "dataclasses": ["✅", "❌", "✅", "✅", "⚠️", "❌", "⚠️", "❌", "❌", "❌", "❌", "✅"],
    "attrs": ["✅", "✅", "✅", "✅", "✅", "⚠️", "✅", "✅", "⚠️", "✅", "⚠️", "✅"],
    "msgspec": ["✅", "⚠️", "✅", "✅", "✅", "✅", "✅", "⚠️", "✅", "❌", "✅", "⚠️"],
    "Plain Python": ["❌", "❌", "✅", "✅", "❌", "❌", "❌", "❌", "❌", "❌", "❌", "⚠️"]
}

# Print comparison table
print(f"{'Feature':<20} {'Pydantic':<12} {'dataclasses':<12} {'attrs':<12} {'msgspec':<12} {'Plain':<12}")
print("-" * 80)
for i, feature in enumerate(features):
    print(f"{feature:<20}", end="")
    for lib in ["Pydantic", "dataclasses", "attrs", "msgspec", "Plain Python"]:
        print(f"{support_matrix[lib][i]:<12}", end="")
    print()

# 3. Migration complexity assessment
print("\n3. Migration Complexity:\n")

# Example: Current LiteAgent with Pydantic
print("Current LiteAgent (Pydantic):")
print("""
class LiteAgent(BaseModel):
    role: str = Field(description="Agent role")
    goal: str = Field(description="Agent goal") 
    backstory: str = Field(default="", description="Agent backstory")
    max_iter: int = Field(default=25, ge=1, description="Max iterations")
    tools: List[Any] = Field(default_factory=list)
    llm: Optional[Any] = Field(default=None)
    
    model_config = {"arbitrary_types_allowed": True}
    
    @field_validator('role')
    def validate_role(cls, v):
        if not v.strip():
            raise ValueError("Role cannot be empty")
        return v
""")

print("\nEquivalent in each alternative:\n")

# Dataclasses version
print("dataclasses version:")
print("""
@dataclass
class LiteAgent:
    role: str
    goal: str
    backstory: str = ""
    max_iter: int = 25
    tools: List[Any] = field(default_factory=list)
    llm: Optional[Any] = None
    
    def __post_init__(self):
        if not self.role.strip():
            raise ValueError("Role cannot be empty")
        if self.max_iter < 1:
            raise ValueError("max_iter must be >= 1")
            
    def model_dump(self):
        return asdict(self)
""")

print("\nattrs version:")
print("""
@attrs.define
class LiteAgent:
    role: str = attrs.field(validator=attrs.validators.instance_of(str))
    goal: str
    backstory: str = ""
    max_iter: int = attrs.field(default=25, validator=attrs.validators.ge(1))
    tools: List[Any] = attrs.field(factory=list)
    llm: Optional[Any] = None
    
    @role.validator
    def _validate_role(self, attribute, value):
        if not value.strip():
            raise ValueError("Role cannot be empty")
            
    def model_dump(self):
        return attrs.asdict(self)
""")

print("\nmsgspec version:")
print("""
class LiteAgent(msgspec.Struct):
    role: str
    goal: str
    backstory: str = ""
    max_iter: int = 25
    tools: List[Any] = msgspec.field(default_factory=list)
    llm: Optional[Any] = None
    
    def __post_init__(self):
        if not self.role.strip():
            raise ValueError("Role cannot be empty")
        if self.max_iter < 1:
            raise ValueError("max_iter must be >= 1")
            
    def model_dump(self):
        return msgspec.structs.asdict(self)
""")

# 4. Breaking changes analysis
print("\n4. Breaking Changes Analysis:\n")

print("If we switch from Pydantic:")
print("- Field() syntax would need replacement")
print("- field_validator decorators need rewriting") 
print("- model_config needs alternative approach")
print("- model_dump() needs wrapper method")
print("- Automatic type coercion may be lost")
print("- JSON schema generation would need custom implementation")

# 5. Hybrid approach possibility
print("\n5. Hybrid Approach Analysis:\n")

print("Could we use Pydantic only where needed?")
print("- Keep Pydantic for external API models")
print("- Use dataclasses for internal models")
print("- This would reduce import overhead")
print("- But adds complexity")

print("\nExample hybrid approach:")
print("""
# Internal models - use dataclasses (no import overhead)
@dataclass 
class InternalConfig:
    max_size_mb: int = 10
    ttl_seconds: int = 3600
    
# External API models - keep Pydantic
class APIRequest(BaseModel):
    agents: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    process: str = "sequential"
""")