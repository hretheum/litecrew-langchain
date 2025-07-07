"""Agent type system for LiteCrew."""

from .base import AgentType, AgentPersonality, AgentTypeConfig, PersonalityTrait
from .factory import AgentTypeFactory
from .behaviors import AgentBehavior, BehaviorModifier
from .types import (
    ConversationalAgent,
    ThinkingAgent,
    ModeratorAgent,
    CriticAgent
)

__all__ = [
    "AgentType",
    "AgentPersonality", 
    "AgentTypeConfig",
    "PersonalityTrait",
    "AgentTypeFactory",
    "AgentBehavior",
    "BehaviorModifier",
    "ConversationalAgent",
    "ThinkingAgent",
    "ModeratorAgent",
    "CriticAgent"
]