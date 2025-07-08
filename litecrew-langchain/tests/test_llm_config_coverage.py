"""Tests for LLM config to improve coverage."""

from litecrew.llm.config import LLMConfig, LLMProvider


class TestLLMConfigCoverage:
    """Tests for LLMConfig to improve coverage."""
    
    def test_to_dict_with_optional_fields(self):
        """Test to_dict method with optional fields."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            temperature=0.8,
            max_tokens=2000,
            api_key="test-key",
            api_base="https://api.openai.com/v1",
            extra_params={"top_p": 0.9}
        )
        
        result = config.to_dict()
        
        # Check that all fields are included
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4"
        assert result["temperature"] == 0.8
        assert result["max_tokens"] == 2000
        assert result["api_key"] == "test-key"
        assert result["api_base"] == "https://api.openai.com/v1"
        assert result["top_p"] == 0.9
    
    def test_to_dict_without_optional_fields(self):
        """Test to_dict method without optional fields."""
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-opus",
            temperature=0.5
        )
        
        result = config.to_dict()
        
        # Check that only required fields are included
        assert result["provider"] == "anthropic"
        assert result["model"] == "claude-3-opus"
        assert result["temperature"] == 0.5
        assert "max_tokens" not in result
        assert "api_key" not in result
        assert "api_base" not in result