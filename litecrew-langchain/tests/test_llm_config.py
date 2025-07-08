"""Tests for LLM Config to improve coverage."""

import pytest
from litecrew.llm.config import LLMConfig, LLMProvider


class TestLLMConfig:
    """Tests for LLMConfig class."""
    
    def test_to_dict_basic(self):
        """Test basic to_dict functionality."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            temperature=0.5
        )
        
        result = config.to_dict()
        
        # Check basic fields
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4"
        assert result["temperature"] == 0.5
        
        # Optional fields should not be present if None
        assert "max_tokens" not in result
        assert "api_key" not in result
        assert "api_base" not in result
    
    def test_to_dict_with_max_tokens(self):
        """Test to_dict with max_tokens set."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            max_tokens=1000
        )
        
        result = config.to_dict()
        
        assert result["max_tokens"] == 1000
        assert "api_key" not in result
        assert "api_base" not in result
    
    def test_to_dict_with_api_key(self):
        """Test to_dict with api_key set."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="sk-test-key"
        )
        
        result = config.to_dict()
        
        assert result["api_key"] == "sk-test-key"
        assert "max_tokens" not in result
        assert "api_base" not in result
    
    def test_to_dict_with_api_base(self):
        """Test to_dict with api_base set."""
        config = LLMConfig(
            provider=LLMProvider.AZURE_OPENAI,
            model="gpt-4",
            api_base="https://example.openai.azure.com/"
        )
        
        result = config.to_dict()
        
        assert result["api_base"] == "https://example.openai.azure.com/"
        assert "max_tokens" not in result
        assert "api_key" not in result
    
    def test_to_dict_with_extra_params(self):
        """Test to_dict with extra_params."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            extra_params={"top_p": 0.9, "frequency_penalty": 0.1}
        )
        
        result = config.to_dict()
        
        # Extra params should be included
        assert result["top_p"] == 0.9
        assert result["frequency_penalty"] == 0.1
        
        # Basic fields should still be present
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4"
        assert result["temperature"] == 0.7  # default
    
    def test_to_dict_with_all_optional_fields(self):
        """Test to_dict with all optional fields set."""
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-opus",
            temperature=0.8,
            max_tokens=2000,
            api_key="sk-ant-key",
            api_base="https://api.anthropic.com",
            extra_params={"top_k": 40}
        )
        
        result = config.to_dict()
        
        # All fields should be present
        assert result["provider"] == "anthropic"
        assert result["model"] == "claude-3-opus"
        assert result["temperature"] == 0.8
        assert result["max_tokens"] == 2000
        assert result["api_key"] == "sk-ant-key"
        assert result["api_base"] == "https://api.anthropic.com"
        assert result["top_k"] == 40
    
    def test_to_dict_with_empty_extra_params(self):
        """Test to_dict with empty extra_params."""
        config = LLMConfig(
            provider=LLMProvider.GROQ,
            model="llama-3.1-70b",
            extra_params={}
        )
        
        result = config.to_dict()
        
        # Should not add anything from empty extra_params
        assert "provider" in result
        assert "model" in result
        assert "temperature" in result
        assert len(result) == 3  # Only basic fields
    
    def test_to_dict_extra_params_override(self):
        """Test that extra_params can override basic fields."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            temperature=0.5,
            extra_params={"temperature": 0.9, "custom_param": "value"}
        )
        
        result = config.to_dict()
        
        # extra_params should override basic fields
        assert result["temperature"] == 0.9
        assert result["custom_param"] == "value"
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4"
    
    def test_to_dict_with_zero_max_tokens(self):
        """Test to_dict with max_tokens set to 0."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            max_tokens=0
        )
        
        result = config.to_dict()
        
        # 0 is falsy, so max_tokens should not be included
        assert "max_tokens" not in result
    
    def test_to_dict_with_empty_string_api_key(self):
        """Test to_dict with api_key set to empty string."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key=""
        )
        
        result = config.to_dict()
        
        # Empty string is falsy, so api_key should not be included
        assert "api_key" not in result
    
    def test_to_dict_with_empty_string_api_base(self):
        """Test to_dict with api_base set to empty string."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_base=""
        )
        
        result = config.to_dict()
        
        # Empty string is falsy, so api_base should not be included
        assert "api_base" not in result
    
    def test_to_dict_different_providers(self):
        """Test to_dict with different providers."""
        providers_and_models = [
            (LLMProvider.OPENAI, "gpt-4"),
            (LLMProvider.ANTHROPIC, "claude-3-opus"),
            (LLMProvider.GROQ, "llama-3.1-70b"),
            (LLMProvider.OLLAMA, "llama2"),
            (LLMProvider.COHERE, "command-r"),
            (LLMProvider.AZURE_OPENAI, "gpt-4"),
            (LLMProvider.BEDROCK, "claude-3-sonnet"),
            (LLMProvider.VERTEXAI, "gemini-pro"),
            (LLMProvider.HUGGINGFACE, "microsoft/DialoGPT-medium"),
            (LLMProvider.TOGETHER, "meta-llama/Llama-2-70b-chat-hf"),
        ]
        
        for provider, model in providers_and_models:
            config = LLMConfig(provider=provider, model=model)
            result = config.to_dict()
            
            assert result["provider"] == provider.value
            assert result["model"] == model
            assert result["temperature"] == 0.7  # default
    
    def test_to_dict_with_complex_extra_params(self):
        """Test to_dict with complex extra_params."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            extra_params={
                "functions": [
                    {"name": "get_weather", "description": "Get weather info"}
                ],
                "function_call": "auto",
                "logit_bias": {1234: -100},
                "presence_penalty": 0.1,
                "response_format": {"type": "json_object"}
            }
        )
        
        result = config.to_dict()
        
        # All extra params should be included
        assert "functions" in result
        assert "function_call" in result
        assert "logit_bias" in result
        assert "presence_penalty" in result
        assert "response_format" in result
        
        # Verify complex structure is preserved
        assert result["functions"][0]["name"] == "get_weather"
        assert result["logit_bias"][1234] == -100
        assert result["response_format"]["type"] == "json_object"
    
    def test_config_defaults(self):
        """Test that config has correct default values."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4"
        )
        
        # Check defaults
        assert config.temperature == 0.7
        assert config.max_tokens is None
        assert config.api_key is None
        assert config.api_base is None
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.use_functions is False
        assert config.streaming is False
        assert config.extra_params == {}
    
    def test_config_custom_values(self):
        """Test config with custom values."""
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-opus",
            temperature=0.9,
            max_tokens=4000,
            api_key="test-key",
            api_base="https://test.api.com",
            timeout=60,
            max_retries=5,
            use_functions=True,
            streaming=True,
            extra_params={"custom": "value"}
        )
        
        # Check all values are set
        assert config.provider == LLMProvider.ANTHROPIC
        assert config.model == "claude-3-opus"
        assert config.temperature == 0.9
        assert config.max_tokens == 4000
        assert config.api_key == "test-key"
        assert config.api_base == "https://test.api.com"
        assert config.timeout == 60
        assert config.max_retries == 5
        assert config.use_functions is True
        assert config.streaming is True
        assert config.extra_params == {"custom": "value"}