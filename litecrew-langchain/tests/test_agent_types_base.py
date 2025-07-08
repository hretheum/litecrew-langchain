"""Tests for AgentTypes Base to improve coverage."""

import pytest
from unittest.mock import Mock, patch
from litecrew.agent_types.base import AgentType, AgentTypeConfig, AgentPersonality, PersonalityTrait


class ConcreteAgentType(AgentType):
    """Concrete implementation of AgentType for testing."""
    
    def _create_default_personality(self) -> AgentPersonality:
        return AgentPersonality(primary_traits=[PersonalityTrait.ANALYTICAL])
    
    def enhance_prompt(self, base_prompt: str, context: dict) -> str:
        return f"Enhanced: {base_prompt}"
    
    def process_response(self, response: str, context: dict) -> str:
        return f"Processed: {response}"


class TestAgentTypeBase:
    """Tests for AgentType base class."""
    
    def test_personality_trait_detail_oriented(self):
        """Test DETAIL_ORIENTED personality trait modifier."""
        personality = AgentPersonality(primary_traits=[PersonalityTrait.DETAIL_ORIENTED])
        
        modifiers = personality.get_trait_modifiers()
        
        # DETAIL_ORIENTED should increase detail modifier by 1.5x
        assert modifiers["detail"] == 1.5
        # Other modifiers should remain at default
        assert modifiers["creativity"] == 1.0
        assert modifiers["criticism"] == 1.0
        assert modifiers["collaboration"] == 1.0
        assert modifiers["optimism"] == 1.0
    
    def test_personality_trait_collaborative(self):
        """Test COLLABORATIVE personality trait modifier."""
        personality = AgentPersonality(primary_traits=[PersonalityTrait.COLLABORATIVE])
        
        modifiers = personality.get_trait_modifiers()
        
        # COLLABORATIVE should increase collaboration modifier by 1.5x
        assert modifiers["collaboration"] == 1.5
        # Other modifiers should remain at default
        assert modifiers["detail"] == 1.0
        assert modifiers["creativity"] == 1.0
        assert modifiers["criticism"] == 1.0
        assert modifiers["optimism"] == 1.0
    
    def test_create_default_personality_abstract(self):
        """Test that _create_default_personality is abstract."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt"
        )
        
        # Should be able to create concrete instance
        agent_type = ConcreteAgentType(config)
        
        # The abstract method should return a personality
        result = agent_type._create_default_personality()
        assert isinstance(result, AgentPersonality)
        assert PersonalityTrait.ANALYTICAL in result.primary_traits
    
    def test_enhance_prompt_abstract(self):
        """Test that enhance_prompt is abstract and works in concrete class."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt"
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Should work with concrete implementation
        result = agent_type.enhance_prompt("base prompt", {})
        assert result == "Enhanced: base prompt"
    
    def test_process_response_abstract(self):
        """Test that process_response is abstract and works in concrete class."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt"
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Should work with concrete implementation
        result = agent_type.process_response("response", {})
        assert result == "Processed: response"
    
    def test_validate_response_min_length_pass(self):
        """Test response validation with minimum length requirement - pass."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt",
            min_response_length=10
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Response with sufficient length should pass
        result = agent_type.validate_response("This is a long enough response")
        assert result is True
    
    def test_validate_response_min_length_fail(self):
        """Test response validation with minimum length requirement - fail."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt",
            min_response_length=20
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Response too short should fail
        result = agent_type.validate_response("Short")
        assert result is False
    
    def test_validate_response_max_length_pass(self):
        """Test response validation with maximum length requirement - pass."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt",
            max_response_length=20
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Response within limit should pass
        result = agent_type.validate_response("Short response")
        assert result is True
    
    def test_validate_response_max_length_fail(self):
        """Test response validation with maximum length requirement - fail."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt",
            max_response_length=10
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Response too long should fail
        result = agent_type.validate_response("This is a very long response that exceeds the limit")
        assert result is False
    
    def test_validate_response_require_reasoning_pass(self):
        """Test response validation with reasoning requirement - pass."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt",
            require_reasoning=True
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Response with 'because' should pass
        result = agent_type.validate_response("I think this is correct because it follows the rules")
        assert result is True
    
    def test_validate_response_require_reasoning_pass_case_insensitive(self):
        """Test response validation with reasoning requirement - case insensitive."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt",
            require_reasoning=True
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Response with 'BECAUSE' in uppercase should pass
        result = agent_type.validate_response("I think this is correct BECAUSE it follows the rules")
        assert result is True
    
    def test_validate_response_require_reasoning_fail(self):
        """Test response validation with reasoning requirement - fail."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt",
            require_reasoning=True
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Response without 'because' should fail
        result = agent_type.validate_response("I think this is correct")
        assert result is False
    
    def test_validate_response_all_requirements_pass(self):
        """Test response validation with all requirements - pass."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt",
            min_response_length=10,
            max_response_length=100,
            require_reasoning=True
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Response meeting all requirements should pass
        result = agent_type.validate_response("This is a good response because it meets all the requirements")
        assert result is True
    
    def test_validate_response_all_requirements_fail_length(self):
        """Test response validation with all requirements - fail on length."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt",
            min_response_length=10,
            max_response_length=30,
            require_reasoning=True
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Response too long should fail despite having reasoning
        result = agent_type.validate_response("This is a very long response because it exceeds the maximum length limit")
        assert result is False
    
    def test_validate_response_all_requirements_fail_reasoning(self):
        """Test response validation with all requirements - fail on reasoning."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt",
            min_response_length=10,
            max_response_length=100,
            require_reasoning=True
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Response without reasoning should fail despite good length
        result = agent_type.validate_response("This is a good response with proper length")
        assert result is False
    
    def test_validate_response_no_requirements(self):
        """Test response validation with no requirements."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt"
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Any response should pass with no requirements
        result = agent_type.validate_response("Any response")
        assert result is True
        
        result = agent_type.validate_response("")
        assert result is True
    
    def test_validate_response_min_length_zero(self):
        """Test response validation with min_response_length of 0."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt",
            min_response_length=0
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Empty response should pass with min_length=0
        result = agent_type.validate_response("")
        assert result is True
    
    def test_validate_response_exact_min_length(self):
        """Test response validation with exact minimum length."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt",
            min_response_length=5
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Response with exactly min length should pass
        result = agent_type.validate_response("Hello")  # 5 characters
        assert result is True
        
        # Response with one less character should fail
        result = agent_type.validate_response("Hell")  # 4 characters
        assert result is False
    
    def test_validate_response_exact_max_length(self):
        """Test response validation with exact maximum length."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt",
            max_response_length=5
        )
        
        agent_type = ConcreteAgentType(config)
        
        # Response with exactly max length should pass
        result = agent_type.validate_response("Hello")  # 5 characters
        assert result is True
        
        # Response with one more character should fail
        result = agent_type.validate_response("Hello!")  # 6 characters
        assert result is False
    
    def test_personality_multiple_traits(self):
        """Test personality with multiple traits."""
        personality = AgentPersonality(traits=[
            PersonalityTrait.DETAIL_ORIENTED,
            PersonalityTrait.COLLABORATIVE
        ])
        
        modifiers = personality.get_modifiers()
        
        # Both traits should affect their respective modifiers
        assert modifiers["detail"] == 1.5
        assert modifiers["collaboration"] == 1.5
        # Other modifiers should remain at default
        assert modifiers["creativity"] == 1.0
        assert modifiers["criticism"] == 1.0
        assert modifiers["optimism"] == 1.0
    
    def test_personality_overlapping_traits(self):
        """Test personality with overlapping trait effects."""
        personality = AgentPersonality(traits=[
            PersonalityTrait.ANALYTICAL,  # affects criticism
            PersonalityTrait.SKEPTICAL    # also affects criticism
        ])
        
        modifiers = personality.get_modifiers()
        
        # Both traits should compound their effects on criticism
        # ANALYTICAL: criticism *= 1.5
        # SKEPTICAL: criticism *= 1.3
        expected_criticism = 1.0 * 1.5 * 1.3
        assert modifiers["criticism"] == expected_criticism
        
        # SKEPTICAL also affects optimism
        assert modifiers["optimism"] == 0.7
    
    def test_config_defaults(self):
        """Test AgentTypeConfig defaults."""
        config = AgentTypeConfig(
            name="test",
            description="Test agent",
            system_prompt_template="Test prompt"
        )
        
        assert config.name == "test"
        assert config.description == "Test agent"
        assert config.system_prompt_template == "Test prompt"
        assert config.min_response_length is None
        assert config.max_response_length is None
        assert config.require_reasoning is False
        assert config.personality_traits == []
        assert config.additional_instructions == ""