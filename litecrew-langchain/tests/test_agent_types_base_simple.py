"""Simple tests for AgentTypes Base to improve coverage."""

import pytest
from litecrew.agent_types.base import AgentType, AgentTypeConfig, AgentPersonality, PersonalityTrait


class ConcreteAgentType(AgentType):
    """Concrete implementation of AgentType for testing."""
    
    def _create_default_personality(self) -> AgentPersonality:
        return AgentPersonality(primary_traits=[PersonalityTrait.ANALYTICAL])
    
    def enhance_prompt(self, base_prompt: str, context: dict) -> str:
        return f"Enhanced: {base_prompt}"
    
    def process_response(self, response: str, context: dict) -> str:
        return f"Processed: {response}"


class TestAgentTypeBaseSimple:
    """Simple tests for AgentType base class."""
    
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
    
    def test_validate_response_require_reasoning_case_insensitive(self):
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
        assert config.default_personality is None
        assert config.response_format_instructions is None