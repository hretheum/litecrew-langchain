"""Tests for LLM utility functions."""

from unittest.mock import Mock

import pytest

from litecrew.llm.utils import estimate_tokens, get_model_context_length, unify_response


class TestUnifyResponse:
    """Test response unification across providers."""

    def test_string_response(self):
        """Test that string responses are returned as-is."""
        response = "Hello, world!"
        result = unify_response(response, "any_provider")
        assert result == "Hello, world!"

    def test_openai_dict_response(self):
        """Test OpenAI dictionary response format."""
        response = {
            "choices": [
                {
                    "message": {
                        "content": "OpenAI response"
                    }
                }
            ]
        }
        result = unify_response(response, "openai")
        assert result == "OpenAI response"

    def test_openai_object_response(self):
        """Test OpenAI object response format."""
        response = Mock()
        response.content = "OpenAI object response"
        result = unify_response(response, "openai")
        assert result == "OpenAI object response"

    def test_anthropic_dict_response(self):
        """Test Anthropic dictionary response format."""
        response = {
            "content": [
                {
                    "text": "Anthropic response"
                }
            ]
        }
        result = unify_response(response, "anthropic")
        assert result == "Anthropic response"

    def test_anthropic_object_response(self):
        """Test Anthropic object response format."""
        response = Mock()
        response.content = "Anthropic object response"
        result = unify_response(response, "anthropic")
        assert result == "Anthropic object response"

    def test_groq_response(self):
        """Test Groq response format (similar to OpenAI)."""
        response = {
            "choices": [
                {
                    "message": {
                        "content": "Groq response"
                    }
                }
            ]
        }
        result = unify_response(response, "groq")
        assert result == "Groq response"

    def test_together_response(self):
        """Test Together AI response format."""
        response = Mock()
        response.content = "Together response"
        result = unify_response(response, "together")
        assert result == "Together response"

    def test_cohere_dict_response(self):
        """Test Cohere dictionary response format."""
        response = {"text": "Cohere response"}
        result = unify_response(response, "cohere")
        assert result == "Cohere response"

    def test_cohere_object_response(self):
        """Test Cohere object response format."""
        response = Mock()
        response.text = "Cohere object response"
        result = unify_response(response, "cohere")
        assert result == "Cohere object response"

    def test_ollama_dict_response(self):
        """Test Ollama dictionary response format."""
        response = {"response": "Ollama response"}
        result = unify_response(response, "ollama")
        assert result == "Ollama response"

    def test_ollama_object_response(self):
        """Test Ollama object response format."""
        response = Mock()
        response.content = "Ollama object response"
        result = unify_response(response, "ollama")
        assert result == "Ollama object response"

    def test_fallback_response(self):
        """Test fallback to string conversion."""
        response = {"unknown": "format"}
        result = unify_response(response, "unknown_provider")
        assert result == "{'unknown': 'format'}"


class TestEstimateTokens:
    """Test token estimation functions."""

    def test_simple_estimation(self):
        """Test simple token estimation method."""
        text = "Hello world, this is a test message."
        tokens = estimate_tokens(text, method="simple")
        # 36 characters / 4 = 9 tokens
        assert tokens == 9

    def test_empty_text(self):
        """Test token estimation for empty text."""
        tokens = estimate_tokens("", method="simple")
        assert tokens == 0

    def test_long_text(self):
        """Test token estimation for longer text."""
        text = "A" * 1000  # 1000 characters
        tokens = estimate_tokens(text, method="simple")
        assert tokens == 250  # 1000 / 4 = 250

    def test_tiktoken_method_fallback(self):
        """Test tiktoken method works or falls back to simple."""
        text = "Test message"
        tokens = estimate_tokens(text, method="tiktoken")
        # Should return a reasonable number of tokens (either tiktoken result or simple fallback)
        assert tokens > 0
        assert tokens <= len(text)  # Should not exceed character count

    def test_invalid_method(self):
        """Test invalid estimation method raises error."""
        with pytest.raises(ValueError, match="Unknown token estimation method"):
            estimate_tokens("test", method="invalid_method")


class TestModelContextLength:
    """Test model context length retrieval."""

    def test_openai_models(self):
        """Test OpenAI model context lengths."""
        assert get_model_context_length("openai", "gpt-4") == 8192
        assert get_model_context_length("openai", "gpt-4-turbo") == 128000
        assert get_model_context_length("openai", "gpt-3.5-turbo") == 16384

    def test_anthropic_models(self):
        """Test Anthropic model context lengths."""
        assert get_model_context_length("anthropic", "claude-3-opus") == 200000
        assert get_model_context_length("anthropic", "claude-3-sonnet") == 200000
        assert get_model_context_length("anthropic", "claude-2") == 100000

    def test_groq_models(self):
        """Test Groq model context lengths."""
        assert get_model_context_length("groq", "mixtral-8x7b") == 32768
        assert get_model_context_length("groq", "llama2-70b") == 4096

    def test_ollama_models(self):
        """Test Ollama model context lengths."""
        assert get_model_context_length("ollama", "llama2") == 4096
        assert get_model_context_length("ollama", "mistral") == 8192
        assert get_model_context_length("ollama", "mixtral") == 32768

    def test_unknown_provider(self):
        """Test unknown provider returns default."""
        assert get_model_context_length("unknown_provider", "some_model") == 4096

    def test_unknown_model(self):
        """Test unknown model returns default."""
        assert get_model_context_length("openai", "unknown_model") == 4096

    def test_empty_strings(self):
        """Test empty provider/model strings."""
        assert get_model_context_length("", "") == 4096
        assert get_model_context_length("openai", "") == 4096