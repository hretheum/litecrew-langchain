"""Agent behavior modifiers and implementations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AgentBehavior(ABC):
    """Abstract base class for agent behaviors."""

    @abstractmethod
    def modify_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Modify the prompt based on behavior."""
        pass

    @abstractmethod
    def modify_response(self, response: str, context: Dict[str, Any]) -> str:
        """Modify the response based on behavior."""
        pass


class BehaviorModifier:
    """Applies multiple behaviors to agent interactions."""

    def __init__(self, behaviors: Optional[List[AgentBehavior]] = None):
        self.behaviors = behaviors or []

    def add_behavior(self, behavior: AgentBehavior) -> None:
        """Add a behavior to the modifier."""
        self.behaviors.append(behavior)

    def apply_to_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Apply all behaviors to modify the prompt."""
        modified_prompt = prompt
        for behavior in self.behaviors:
            modified_prompt = behavior.modify_prompt(modified_prompt, context)
        return modified_prompt

    def apply_to_response(self, response: str, context: Dict[str, Any]) -> str:
        """Apply all behaviors to modify the response."""
        modified_response = response
        for behavior in self.behaviors:
            modified_response = behavior.modify_response(modified_response, context)
        return modified_response


class CriticalThinkingBehavior(AgentBehavior):
    """Adds critical thinking elements to agent responses."""

    def __init__(self, level: str = "moderate"):
        self.level = level  # mild, moderate, harsh

    def modify_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Add critical thinking instructions."""
        critical_instructions = {
            "mild": "Consider potential improvements and alternatives.",
            "moderate": "Analyze strengths and weaknesses. Point out areas for improvement.",
            "harsh": "Be highly critical. Identify all flaws and shortcomings rigorously.",
        }

        instruction = critical_instructions.get(
            self.level, critical_instructions["moderate"]
        )
        return f"{prompt}\n\n{instruction}"

    def modify_response(self, response: str, context: Dict[str, Any]) -> str:
        """Ensure response includes critical elements."""
        critical_phrases = [
            "however",
            "but",
            "although",
            "on the other hand",
            "could be improved",
        ]

        # Check if response already has critical elements
        has_criticism = any(phrase in response.lower() for phrase in critical_phrases)

        if not has_criticism and self.level != "mild":
            # Add a critical perspective
            addition = "\n\nHowever, it's important to consider potential limitations and areas for improvement in this approach."
            response += addition

        return response


class VerboseThinkingBehavior(AgentBehavior):
    """Makes agent explain thinking process in detail."""

    def __init__(self, verbosity: int = 5):
        self.verbosity = max(1, min(10, verbosity))  # 1-10 scale

    def modify_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Add verbose thinking instructions."""
        verbosity_instructions = {
            1: "Be concise in your response.",
            3: "Explain your reasoning briefly.",
            5: "Provide detailed reasoning for your conclusions.",
            7: "Think through the problem step-by-step, explaining each part.",
            10: "Provide exhaustive analysis with detailed reasoning for every aspect.",
        }

        # Get closest instruction
        closest_key = min(
            verbosity_instructions.keys(), key=lambda x: abs(x - self.verbosity)
        )
        instruction = verbosity_instructions[closest_key]

        return f"{prompt}\n\n{instruction} Show your thought process."

    def modify_response(self, response: str, context: Dict[str, Any]) -> str:
        """Ensure response meets verbosity requirements."""
        words = response.split()
        target_length = self.verbosity * 100  # Rough approximation

        if len(words) < target_length * 0.7:
            # Response is too short, add elaboration prompt
            addition = "\n\nTo elaborate further on this analysis..."
            response += addition

        return response


class ModerationBehavior(AgentBehavior):
    """Adds moderation capabilities to agent."""

    def __init__(self, style: str = "balanced"):
        self.style = style  # strict, balanced, permissive

    def modify_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Add moderation instructions."""
        moderation_instructions = {
            "strict": "Maintain strict order and ensure all participants follow rules precisely.",
            "balanced": "Guide the discussion while allowing natural flow and some flexibility.",
            "permissive": "Facilitate gently, allowing maximum freedom of expression.",
        }

        instruction = moderation_instructions.get(
            self.style, moderation_instructions["balanced"]
        )
        return f"{prompt}\n\nAs a moderator: {instruction}"

    def modify_response(self, response: str, context: Dict[str, Any]) -> str:
        """Add moderation elements to response."""
        if self.style == "strict" and "next" not in response.lower():
            response += "\n\nNow, let's move to the next point in our agenda."
        elif self.style == "balanced" and context.get("needs_redirection", False):
            response += "\n\nPerhaps we could refocus on the main topic at hand."

        return response


class ConversationalBehavior(AgentBehavior):
    """Makes agent more conversational and engaging."""

    def __init__(self, style: str = "friendly"):
        self.style = style  # formal, friendly, casual, adaptive

    def modify_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Add conversational style instructions."""
        style_instructions = {
            "formal": "Maintain a professional and formal tone throughout.",
            "friendly": "Be warm, approachable, and encouraging in your responses.",
            "casual": "Use a relaxed, conversational tone as if talking to a colleague.",
            "adaptive": "Match the tone and style of other participants.",
        }

        instruction = style_instructions.get(self.style, style_instructions["friendly"])
        return f"{prompt}\n\nCommunication style: {instruction}"

    def modify_response(self, response: str, context: Dict[str, Any]) -> str:
        """Add conversational elements."""
        if self.style == "friendly" and not any(
            word in response.lower() for word in ["great", "excellent", "interesting"]
        ):
            # Add encouraging element
            response = f"That's an interesting point! {response}"
        elif self.style == "casual" and "I think" not in response:
            # Add personal touch
            response = response.replace("It is", "I think it's", 1)

        return response
