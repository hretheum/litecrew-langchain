"""Base classes for agent type system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class PersonalityTrait(Enum):
    """Available personality traits for agents."""

    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    CRITICAL = "critical"
    SUPPORTIVE = "supportive"
    DETAIL_ORIENTED = "detail_oriented"
    BIG_PICTURE = "big_picture"
    COLLABORATIVE = "collaborative"
    INDEPENDENT = "independent"
    OPTIMISTIC = "optimistic"
    SKEPTICAL = "skeptical"
    METHODICAL = "methodical"
    SPONTANEOUS = "spontaneous"


@dataclass
class AgentPersonality:
    """Defines personality characteristics of an agent."""

    primary_traits: List[PersonalityTrait]
    communication_style: str = "professional"  # professional, casual, formal, friendly
    verbosity_level: str = "balanced"  # concise, balanced, verbose
    thinking_style: str = "analytical"  # analytical, creative, practical, theoretical
    response_tendency: str = "balanced"  # agreeable, challenging, balanced, neutral

    def get_trait_modifiers(self) -> Dict[str, float]:
        """Get behavior modifiers based on personality traits."""
        modifiers = {
            "creativity": 1.0,
            "criticism": 1.0,
            "detail": 1.0,
            "collaboration": 1.0,
            "optimism": 1.0,
        }

        for trait in self.primary_traits:
            if trait == PersonalityTrait.CREATIVE:
                modifiers["creativity"] *= 1.5
            elif trait == PersonalityTrait.CRITICAL:
                modifiers["criticism"] *= 1.5
            elif trait == PersonalityTrait.DETAIL_ORIENTED:
                modifiers["detail"] *= 1.5
            elif trait == PersonalityTrait.COLLABORATIVE:
                modifiers["collaboration"] *= 1.5
            elif trait == PersonalityTrait.OPTIMISTIC:
                modifiers["optimism"] *= 1.5
            elif trait == PersonalityTrait.SKEPTICAL:
                modifiers["criticism"] *= 1.3
                modifiers["optimism"] *= 0.7

        return modifiers


@dataclass
class AgentTypeConfig:
    """Configuration for agent type behavior."""

    # Basic config
    name: str
    description: str

    # Behavior config
    system_prompt_template: str
    response_format_instructions: Optional[str] = None

    # Personality
    default_personality: Optional[AgentPersonality] = None

    # Type-specific parameters
    criticism_level: Optional[str] = None  # mild, moderate, harsh
    thinking_verbosity: Optional[int] = None  # 1-10 scale
    moderation_style: Optional[str] = None  # strict, balanced, permissive
    conversation_style: Optional[str] = None  # formal, casual, adaptive

    # Performance hints
    min_response_length: Optional[int] = None
    max_response_length: Optional[int] = None
    require_reasoning: bool = False
    require_examples: bool = False


class AgentType(ABC):
    """Abstract base class for agent types."""

    def __init__(self, config: AgentTypeConfig):
        self.config = config
        self.personality = (
            config.default_personality or self._create_default_personality()
        )

    @abstractmethod
    def _create_default_personality(self) -> AgentPersonality:
        """Create default personality for this agent type."""
        pass

    @abstractmethod
    def enhance_prompt(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """Enhance the base prompt with type-specific instructions."""
        pass

    @abstractmethod
    def process_response(self, response: str, context: Dict[str, Any]) -> str:
        """Process the response according to type-specific rules."""
        pass

    def validate_response(self, response: str) -> bool:
        """Validate if response meets type requirements."""
        if (
            self.config.min_response_length
            and len(response) < self.config.min_response_length
        ):
            return False
        if (
            self.config.max_response_length
            and len(response) > self.config.max_response_length
        ):
            return False
        if self.config.require_reasoning and "because" not in response.lower():
            return False
        return True

    def get_system_prompt(self, role: str, goal: str, backstory: str) -> str:
        """Get the full system prompt for this agent type."""
        base_prompt = self.config.system_prompt_template.format(
            role=role,
            goal=goal,
            backstory=backstory,
            personality=self._describe_personality(),
        )

        if self.config.response_format_instructions:
            base_prompt += f"\n\n{self.config.response_format_instructions}"

        return base_prompt

    def _describe_personality(self) -> str:
        """Create a text description of the personality."""
        traits = ", ".join(trait.value for trait in self.personality.primary_traits)
        return (
            f"You have a {self.personality.communication_style} communication style, "
            f"with {traits} personality traits. "
            f"Your thinking style is {self.personality.thinking_style} and you tend to be "
            f"{self.personality.verbosity_level} in your responses."
        )
