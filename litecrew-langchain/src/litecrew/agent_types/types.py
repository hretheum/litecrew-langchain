"""Specialized agent type implementations."""

from typing import Any, Dict

from .base import AgentPersonality, AgentType, AgentTypeConfig, PersonalityTrait


class ConversationalAgent(AgentType):
    """Agent optimized for natural conversations."""

    @classmethod
    def get_default_config(cls) -> AgentTypeConfig:
        """Get default configuration for conversational agent."""
        return AgentTypeConfig(
            name="conversational",
            description="Engages in natural, flowing conversations while maintaining context",
            system_prompt_template=(
                "You are {role}, a conversational agent.\n"
                "Your goal is: {goal}\n"
                "Background: {backstory}\n\n"
                "{personality}\n\n"
                "Engage naturally in conversation, building on previous topics and "
                "maintaining a coherent dialogue flow."
            ),
            response_format_instructions=(
                "Keep responses conversational and engaging. "
                "Reference previous topics when relevant. "
                "Ask clarifying questions when appropriate."
            ),
            conversation_style="friendly",
            min_response_length=50,
        )

    def _create_default_personality(self) -> AgentPersonality:
        """Create default personality for conversational agent."""
        return AgentPersonality(
            primary_traits=[
                PersonalityTrait.COLLABORATIVE,
                PersonalityTrait.SUPPORTIVE,
            ],
            communication_style="friendly",
            verbosity_level="balanced",
            thinking_style="practical",
            response_tendency="agreeable",
        )

    def enhance_prompt(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """Enhance prompt with conversational elements."""
        enhanced = base_prompt

        # Add conversation history awareness
        if context.get("conversation_history"):
            enhanced += "\n\nPrevious conversation context is available. Build upon it naturally."

        # Add turn-taking awareness
        if context.get("current_speaker"):
            enhanced += f"\n\nYou are responding to {context['current_speaker']}."

        return enhanced

    def process_response(self, response: str, context: Dict[str, Any]) -> str:
        """Process response to ensure conversational flow."""
        # Ensure response doesn't end abruptly
        if response and not response.rstrip().endswith((".", "?", "!", '"')):
            response += "."

        # Add conversational continuation if too short
        if len(response.split()) < 20:
            response += " What are your thoughts on this?"

        return response


class ThinkingAgent(AgentType):
    """Agent that shows detailed thinking process."""

    @classmethod
    def get_default_config(cls) -> AgentTypeConfig:
        """Get default configuration for thinking agent."""
        return AgentTypeConfig(
            name="thinking",
            description="Shows detailed reasoning and thought process",
            system_prompt_template=(
                "You are {role}, a thinking agent.\n"
                "Your goal is: {goal}\n"
                "Background: {backstory}\n\n"
                "{personality}\n\n"
                "IMPORTANT: Always show your thinking process step by step. "
                "Use 'Let me think through this...' format."
            ),
            response_format_instructions=(
                "Structure your response as:\n"
                "1. Initial thoughts\n"
                "2. Step-by-step reasoning\n"
                "3. Consideration of alternatives\n"
                "4. Final conclusion\n"
                "Show your work!"
            ),
            thinking_verbosity=7,
            require_reasoning=True,
            min_response_length=200,
        )

    def _create_default_personality(self) -> AgentPersonality:
        """Create default personality for thinking agent."""
        return AgentPersonality(
            primary_traits=[
                PersonalityTrait.ANALYTICAL,
                PersonalityTrait.METHODICAL,
                PersonalityTrait.DETAIL_ORIENTED,
            ],
            communication_style="professional",
            verbosity_level="verbose",
            thinking_style="analytical",
            response_tendency="neutral",
        )

    def enhance_prompt(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """Enhance prompt with thinking instructions."""
        verbosity = self.config.thinking_verbosity or 7

        enhanced = base_prompt + f"\n\nThinking verbosity level: {verbosity}/10"
        enhanced += "\nShow ALL steps of your reasoning process."

        if context.get("problem_complexity", "medium") == "high":
            enhanced += "\nThis is a complex problem - take extra care to think through all angles."

        return enhanced

    def process_response(self, response: str, context: Dict[str, Any]) -> str:
        """Ensure response shows thinking process."""
        thinking_markers = ["think", "consider", "analyze", "reason", "because"]

        has_thinking = any(marker in response.lower() for marker in thinking_markers)

        if not has_thinking:
            # Prepend thinking introduction
            response = "Let me think through this step by step...\n\n" + response

        # Ensure structured thinking if not present
        if "step" not in response.lower() and "first" not in response.lower():
            # Add structure markers
            parts = response.split(". ")
            if len(parts) > 2:
                structured = "First, " + parts[0] + ".\n"
                structured += "Next, " + parts[1] + ".\n"
                if len(parts) > 2:
                    structured += "Finally, " + ". ".join(parts[2:])
                response = structured

        return response


class ModeratorAgent(AgentType):
    """Agent specialized in moderating discussions."""

    @classmethod
    def get_default_config(cls) -> AgentTypeConfig:
        """Get default configuration for moderator agent."""
        return AgentTypeConfig(
            name="moderator",
            description="Facilitates discussions and ensures productive dialogue",
            system_prompt_template=(
                "You are {role}, a discussion moderator.\n"
                "Your goal is: {goal}\n"
                "Background: {backstory}\n\n"
                "{personality}\n\n"
                "As a moderator, you:\n"
                "- Keep discussions on track\n"
                "- Ensure all participants can contribute\n"
                "- Summarize key points\n"
                "- Manage time and flow\n"
                "- Resolve conflicts diplomatically"
            ),
            response_format_instructions=(
                "Be fair and balanced. "
                "Acknowledge all viewpoints. "
                "Guide towards productive outcomes."
            ),
            moderation_style="balanced",
            min_response_length=75,
        )

    def _create_default_personality(self) -> AgentPersonality:
        """Create default personality for moderator agent."""
        return AgentPersonality(
            primary_traits=[
                PersonalityTrait.COLLABORATIVE,
                PersonalityTrait.BIG_PICTURE,
                PersonalityTrait.METHODICAL,
            ],
            communication_style="professional",
            verbosity_level="balanced",
            thinking_style="practical",
            response_tendency="balanced",
        )

    def enhance_prompt(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """Enhance prompt with moderation instructions."""
        enhanced = base_prompt

        # Add participant awareness
        if context.get("participants"):
            names = ", ".join(context["participants"])
            enhanced += f"\n\nCurrent participants: {names}"

        # Add discussion state
        if context.get("discussion_phase"):
            enhanced += f"\n\nDiscussion phase: {context['discussion_phase']}"

        # Add time awareness
        if context.get("time_remaining"):
            enhanced += f"\n\nTime remaining: {context['time_remaining']} minutes"

        return enhanced

    def process_response(self, response: str, context: Dict[str, Any]) -> str:
        """Process response to include moderation elements."""
        # Ensure summary element if discussion is long
        if context.get("turn_count", 0) > 5 and "summary" not in response.lower():
            response += "\n\nTo summarize the key points so far..."

        # Add next speaker suggestion if not present
        if context.get("participants") and "next" not in response.lower():
            response += f"\n\nLet's hear from {context.get('next_speaker', 'the next participant')}."

        return response


class CriticAgent(AgentType):
    """Agent specialized in constructive criticism and analysis."""

    @classmethod
    def get_default_config(cls) -> AgentTypeConfig:
        """Get default configuration for critic agent."""
        return AgentTypeConfig(
            name="critic",
            description="Provides constructive criticism and identifies areas for improvement",
            system_prompt_template=(
                "You are {role}, a critical analyst.\n"
                "Your goal is: {goal}\n"
                "Background: {backstory}\n\n"
                "{personality}\n\n"
                "Provide constructive criticism that:\n"
                "- Identifies strengths and weaknesses\n"
                "- Offers specific improvements\n"
                "- Remains respectful and helpful\n"
                "- Backs claims with reasoning"
            ),
            response_format_instructions=(
                "Structure criticism as:\n"
                "1. Acknowledge positives\n"
                "2. Identify issues with explanations\n"
                "3. Suggest concrete improvements\n"
                "4. Prioritize feedback by importance"
            ),
            criticism_level="moderate",
            require_reasoning=True,
            min_response_length=150,
        )

    def _create_default_personality(self) -> AgentPersonality:
        """Create default personality for critic agent."""
        return AgentPersonality(
            primary_traits=[
                PersonalityTrait.CRITICAL,
                PersonalityTrait.ANALYTICAL,
                PersonalityTrait.DETAIL_ORIENTED,
                PersonalityTrait.SKEPTICAL,
            ],
            communication_style="professional",
            verbosity_level="balanced",
            thinking_style="analytical",
            response_tendency="challenging",
        )

    def enhance_prompt(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """Enhance prompt with criticism instructions."""
        criticism_level = self.config.criticism_level or "moderate"

        enhanced = base_prompt + f"\n\nCriticism level: {criticism_level}"

        # Add focus areas if specified
        if context.get("focus_areas"):
            areas = ", ".join(context["focus_areas"])
            enhanced += f"\n\nFocus criticism on: {areas}"

        # Add evaluation criteria
        if context.get("criteria"):
            enhanced += f"\n\nEvaluate against: {context['criteria']}"

        return enhanced

    def process_response(self, response: str, context: Dict[str, Any]) -> str:
        """Process response to ensure constructive criticism."""
        # Ensure balance - must have both positive and negative
        has_positive = any(
            word in response.lower()
            for word in ["good", "excellent", "strong", "effective", "well"]
        )
        has_negative = any(
            word in response.lower()
            for word in ["however", "but", "could", "should", "improve", "issue"]
        )

        if not has_positive:
            # Add positive acknowledgment
            response = "While there are areas for improvement, " + response

        if not has_negative and self.config.criticism_level != "mild":
            # Add critical element
            response += "\n\nHowever, there are opportunities for enhancement that should be considered."

        # Ensure suggestions are present
        if "suggest" not in response.lower() and "recommend" not in response.lower():
            response += (
                "\n\nI would suggest focusing on the most critical improvements first."
            )

        return response
