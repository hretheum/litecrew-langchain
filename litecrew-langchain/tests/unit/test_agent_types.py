"""Tests for agent type system."""

import pytest
from unittest.mock import Mock, patch

from litecrew.agent import Agent
from litecrew.agent_types import (
    AgentTypeFactory,
    AgentPersonality,
    PersonalityTrait,
    BehaviorModifier,
    ConversationalAgent,
    ThinkingAgent,
    ModeratorAgent,
    CriticAgent
)
from litecrew.agent_types.behaviors import (
    CriticalThinkingBehavior,
    VerboseThinkingBehavior,
    ModerationBehavior,
    ConversationalBehavior
)


class TestAgentTypeFactory:
    """Test AgentTypeFactory functionality."""
    
    def test_list_available_types(self):
        """Test listing available agent types."""
        types = AgentTypeFactory.list_types()
        assert "conversational" in types
        assert "thinking" in types
        assert "moderator" in types
        assert "critic" in types
        assert len(types) == 4
    
    def test_create_agent_type(self):
        """Test creating agent types."""
        # Create conversational agent
        agent = AgentTypeFactory.create("conversational")
        assert isinstance(agent, ConversationalAgent)
        assert agent.config.name == "conversational"
        
        # Create thinking agent with config
        agent = AgentTypeFactory.create("thinking", {"thinking_verbosity": 8})
        assert isinstance(agent, ThinkingAgent)
        assert agent.config.thinking_verbosity == 8
    
    def test_invalid_agent_type(self):
        """Test creating invalid agent type."""
        with pytest.raises(ValueError, match="Unknown agent type"):
            AgentTypeFactory.create("invalid_type")
    
    def test_get_type_info(self):
        """Test getting type information."""
        info = AgentTypeFactory.get_type_info("critic")
        assert info["name"] == "critic"
        assert "description" in info
        assert "configurable_options" in info
        assert "default_config" in info
        assert "criticism_level" in info["configurable_options"]


class TestAgentPersonality:
    """Test AgentPersonality functionality."""
    
    def test_personality_traits(self):
        """Test personality trait modifiers."""
        personality = AgentPersonality(
            primary_traits=[PersonalityTrait.CREATIVE, PersonalityTrait.CRITICAL]
        )
        
        modifiers = personality.get_trait_modifiers()
        assert modifiers["creativity"] == 1.5
        assert modifiers["criticism"] == 1.5
        assert modifiers["detail"] == 1.0
    
    def test_mixed_traits(self):
        """Test mixed personality traits."""
        personality = AgentPersonality(
            primary_traits=[PersonalityTrait.OPTIMISTIC, PersonalityTrait.SKEPTICAL]
        )
        
        modifiers = personality.get_trait_modifiers()
        assert modifiers["optimism"] == 1.5 * 0.7  # Optimistic + Skeptical modifier
        assert modifiers["criticism"] == 1.3  # Skeptical increases criticism


class TestConversationalAgent:
    """Test ConversationalAgent functionality."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = ConversationalAgent.get_default_config()
        assert config.name == "conversational"
        assert config.conversation_style == "friendly"
        assert config.min_response_length == 50
    
    def test_enhance_prompt(self):
        """Test prompt enhancement."""
        agent = ConversationalAgent(ConversationalAgent.get_default_config())
        
        base_prompt = "Discuss the weather"
        context = {"conversation_history": ["Previous topic"], "current_speaker": "Alice"}
        
        enhanced = agent.enhance_prompt(base_prompt, context)
        assert "Previous conversation context" in enhanced
        assert "responding to Alice" in enhanced
    
    def test_process_response(self):
        """Test response processing."""
        agent = ConversationalAgent(ConversationalAgent.get_default_config())
        
        # Test short response enhancement
        short_response = "Yes"
        processed = agent.process_response(short_response, {})
        assert "What are your thoughts on this?" in processed
        
        # Test proper ending
        incomplete = "I think that's interesting"
        processed = agent.process_response(incomplete, {})
        assert processed.endswith(".") or processed.endswith("?")


class TestThinkingAgent:
    """Test ThinkingAgent functionality."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = ThinkingAgent.get_default_config()
        assert config.name == "thinking"
        assert config.thinking_verbosity == 7
        assert config.require_reasoning is True
        assert config.min_response_length == 200
    
    def test_enhance_prompt(self):
        """Test prompt enhancement."""
        agent = ThinkingAgent(ThinkingAgent.get_default_config())
        
        base_prompt = "Solve this problem"
        context = {"problem_complexity": "high"}
        
        enhanced = agent.enhance_prompt(base_prompt, context)
        assert "Thinking verbosity level: 7/10" in enhanced
        assert "Show ALL steps" in enhanced
        assert "complex problem" in enhanced
    
    def test_process_response(self):
        """Test response processing."""
        agent = ThinkingAgent(ThinkingAgent.get_default_config())
        
        # Test adding thinking markers
        simple_response = "The answer is 42."
        processed = agent.process_response(simple_response, {})
        assert "Let me think through this" in processed
        
        # Test structuring response
        unstructured = "We need to analyze. Then calculate. Finally verify."
        processed = agent.process_response(unstructured, {})
        assert "First," in processed
        assert "Next," in processed
        assert "Finally," in processed


class TestModeratorAgent:
    """Test ModeratorAgent functionality."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = ModeratorAgent.get_default_config()
        assert config.name == "moderator"
        assert config.moderation_style == "balanced"
        assert config.min_response_length == 75
    
    def test_enhance_prompt(self):
        """Test prompt enhancement."""
        agent = ModeratorAgent(ModeratorAgent.get_default_config())
        
        base_prompt = "Moderate the discussion"
        context = {
            "participants": ["Alice", "Bob", "Charlie"],
            "discussion_phase": "opening statements",
            "time_remaining": 15
        }
        
        enhanced = agent.enhance_prompt(base_prompt, context)
        assert "Current participants: Alice, Bob, Charlie" in enhanced
        assert "Discussion phase: opening statements" in enhanced
        assert "Time remaining: 15 minutes" in enhanced
    
    def test_process_response(self):
        """Test response processing."""
        agent = ModeratorAgent(ModeratorAgent.get_default_config())
        
        # Test summary addition
        response = "Good points made."
        context = {"turn_count": 10}
        processed = agent.process_response(response, context)
        assert "To summarize the key points" in processed
        
        # Test next speaker suggestion
        response = "Interesting perspective."
        context = {"participants": ["Alice", "Bob"], "next_speaker": "Bob"}
        processed = agent.process_response(response, context)
        assert "Let's hear from Bob" in processed


class TestCriticAgent:
    """Test CriticAgent functionality."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = CriticAgent.get_default_config()
        assert config.name == "critic"
        assert config.criticism_level == "moderate"
        assert config.require_reasoning is True
        assert config.min_response_length == 150
    
    def test_enhance_prompt(self):
        """Test prompt enhancement."""
        agent = CriticAgent(CriticAgent.get_default_config())
        
        base_prompt = "Review this code"
        context = {
            "focus_areas": ["performance", "security"],
            "criteria": "production readiness"
        }
        
        enhanced = agent.enhance_prompt(base_prompt, context)
        assert "Criticism level: moderate" in enhanced
        assert "Focus criticism on: performance, security" in enhanced
        assert "Evaluate against: production readiness" in enhanced
    
    def test_process_response(self):
        """Test response processing."""
        agent = CriticAgent(CriticAgent.get_default_config())
        
        # Test balance enforcement
        negative_only = "This has many issues and problems."
        processed = agent.process_response(negative_only, {})
        assert "While there are areas for improvement" in processed
        
        # Test suggestion addition
        no_suggestions = "The code could be better."
        processed = agent.process_response(no_suggestions, {})
        assert "suggest" in processed.lower()


class TestBehaviors:
    """Test behavior modifiers."""
    
    def test_critical_thinking_behavior(self):
        """Test CriticalThinkingBehavior."""
        behavior = CriticalThinkingBehavior(level="harsh")
        
        prompt = "Analyze this"
        enhanced = behavior.modify_prompt(prompt, {})
        assert "highly critical" in enhanced
        
        response = "This is good."
        modified = behavior.modify_response(response, {})
        assert "however" in modified.lower() or "limitations" in modified.lower()
    
    def test_verbose_thinking_behavior(self):
        """Test VerboseThinkingBehavior."""
        behavior = VerboseThinkingBehavior(verbosity=8)
        
        prompt = "Solve this"
        enhanced = behavior.modify_prompt(prompt, {})
        assert "step-by-step" in enhanced
        
        short_response = "The answer is X."
        modified = behavior.modify_response(short_response, {})
        assert "To elaborate further" in modified
    
    def test_moderation_behavior(self):
        """Test ModerationBehavior."""
        behavior = ModerationBehavior(style="strict")
        
        prompt = "Lead discussion"
        enhanced = behavior.modify_prompt(prompt, {})
        assert "strict order" in enhanced
        
        response = "Good discussion so far."
        modified = behavior.modify_response(response, {})
        assert "next point" in modified
    
    def test_conversational_behavior(self):
        """Test ConversationalBehavior."""
        behavior = ConversationalBehavior(style="friendly")
        
        prompt = "Discuss topic"
        enhanced = behavior.modify_prompt(prompt, {})
        assert "warm, approachable" in enhanced
        
        response = "The analysis shows..."
        modified = behavior.modify_response(response, {})
        assert "interesting point" in modified or response in modified


class TestAgentWithTypes:
    """Test Agent integration with type system."""
    
    @patch('litecrew.agent.LLMManager')
    def test_agent_with_type(self, mock_llm_manager):
        """Test creating agent with type."""
        mock_llm = Mock()
        mock_llm_manager.return_value.create_llm.return_value = mock_llm
        
        # Create conversational agent
        agent = Agent(
            role="Assistant",
            goal="Help users",
            backstory="Friendly AI",
            type="conversational",
            type_config={"conversation_style": "casual"}
        )
        
        assert agent.type == "conversational"
        assert agent.type_config["conversation_style"] == "casual"
        assert agent._agent_type is not None
        assert isinstance(agent._agent_type, ConversationalAgent)
    
    @patch('litecrew.agent.LLMManager')
    def test_invalid_agent_type(self, mock_llm_manager):
        """Test creating agent with invalid type."""
        mock_llm = Mock()
        mock_llm_manager.return_value.create_llm.return_value = mock_llm
        
        with pytest.raises(ValueError, match="Invalid agent type"):
            Agent(
                role="Assistant",
                goal="Help users",
                backstory="AI",
                type="invalid_type"
            )
    
    @patch('litecrew.agent.LLMManager')
    def test_agent_type_validation(self, mock_llm_manager):
        """Test agent type configuration validation."""
        mock_llm = Mock()
        mock_llm_manager.return_value.create_llm.return_value = mock_llm
        
        # Valid configuration
        agent = Agent(
            role="Critic",
            goal="Review code",
            backstory="Expert reviewer",
            type="critic",
            type_config={"criticism_level": "moderate"}
        )
        
        assert agent.validate_type_config() is True
        
        # Test invalid config (manually set for testing)
        agent._agent_type.config.criticism_level = "invalid"
        assert agent.validate_type_config() is False
    
    @patch('litecrew.agent.LLMManager')
    def test_agent_type_info(self, mock_llm_manager):
        """Test getting agent type information."""
        mock_llm = Mock()
        mock_llm_manager.return_value.create_llm.return_value = mock_llm
        
        agent = Agent(
            role="Thinker",
            goal="Analyze deeply",
            backstory="Analytical AI",
            type="thinking",
            type_config={"thinking_verbosity": 9}
        )
        
        info = agent.get_type_info()
        assert info["name"] == "thinking"
        assert info["current_config"]["thinking_verbosity"] == 9
        assert "personality" in info
        assert "analytical" in info["personality"]["traits"]
    
    @patch('litecrew.agent.LLMManager')
    def test_behavior_modifier_integration(self, mock_llm_manager):
        """Test behavior modifier integration."""
        mock_llm = Mock()
        mock_llm_manager.return_value.create_llm.return_value = mock_llm
        
        agent = Agent(
            role="Moderator",
            goal="Facilitate discussion",
            backstory="Expert facilitator",
            type="moderator",
            type_config={"moderation_style": "strict"}
        )
        
        # Check that behaviors are set up
        assert agent._behavior_modifier is not None
        assert len(agent._behavior_modifier.behaviors) > 0
        
        # Verify behavior is ModerationBehavior
        behavior = agent._behavior_modifier.behaviors[0]
        assert isinstance(behavior, ModerationBehavior)
        assert behavior.style == "strict"


class TestBehaviorModifier:
    """Test BehaviorModifier functionality."""
    
    def test_multiple_behaviors(self):
        """Test applying multiple behaviors."""
        modifier = BehaviorModifier()
        
        # Add multiple behaviors
        modifier.add_behavior(CriticalThinkingBehavior(level="moderate"))
        modifier.add_behavior(VerboseThinkingBehavior(verbosity=5))
        
        # Test prompt modification
        prompt = "Analyze this"
        modified = modifier.apply_to_prompt(prompt, {})
        assert "strengths and weaknesses" in modified  # From critical
        assert "detailed reasoning" in modified  # From verbose
        
        # Test response modification
        response = "The solution is simple."
        modified = modifier.apply_to_response(response, {})
        # Should have critical elements and elaboration
        assert len(modified) > len(response)