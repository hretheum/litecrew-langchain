"""Tests for LLM utils to improve coverage."""

from unittest.mock import Mock
from litecrew.llm.utils import unify_response


class TestLLMUtilsCoverage:
    """Tests for LLM utils to improve coverage."""
    
    def test_unify_response_string_input(self):
        """Test unify_response with string input."""
        result = unify_response("simple text", "openai")
        assert result == "simple text"
    
    def test_unify_response_openai_dict(self):
        """Test unify_response with OpenAI dict format."""
        response = {
            "choices": [
                {"message": {"content": "OpenAI response"}}
            ]
        }
        result = unify_response(response, "openai")
        assert result == "OpenAI response"
    
    def test_unify_response_openai_invalid_dict(self):
        """Test unify_response with invalid OpenAI dict format."""
        response = {"invalid": "format"}
        result = unify_response(response, "openai")
        assert result == "{'invalid': 'format'}"
    
    def test_unify_response_openai_object_with_content(self):
        """Test unify_response with OpenAI object having content."""
        response = Mock()
        response.content = "OpenAI object content"
        result = unify_response(response, "openai")
        assert result == "OpenAI object content"
    
    def test_unify_response_anthropic_dict(self):
        """Test unify_response with Anthropic dict format."""
        response = {
            "content": [
                {"text": "Anthropic response"}
            ]
        }
        result = unify_response(response, "anthropic")
        assert result == "Anthropic response"
    
    def test_unify_response_anthropic_invalid_dict(self):
        """Test unify_response with invalid Anthropic dict format."""
        response = {"invalid": "format"}
        result = unify_response(response, "anthropic")
        assert result == "{'invalid': 'format'}"
    
    def test_unify_response_anthropic_object_with_content(self):
        """Test unify_response with Anthropic object having content."""
        response = Mock()
        response.content = "Anthropic object content"
        result = unify_response(response, "anthropic")
        assert result == "Anthropic object content"
    
    def test_unify_response_groq_dict(self):
        """Test unify_response with Groq dict format."""
        response = {
            "choices": [
                {"message": {"content": "Groq response"}}
            ]
        }
        result = unify_response(response, "groq")
        assert result == "Groq response"
    
    def test_unify_response_together_dict(self):
        """Test unify_response with Together dict format."""
        response = {
            "choices": [
                {"message": {"content": "Together response"}}
            ]
        }
        result = unify_response(response, "together")
        assert result == "Together response"
    
    def test_unify_response_cohere_dict(self):
        """Test unify_response with Cohere dict format."""
        response = {"text": "Cohere response"}
        result = unify_response(response, "cohere")
        assert result == "Cohere response"
    
    def test_unify_response_cohere_object_with_text(self):
        """Test unify_response with Cohere object having text."""
        response = Mock()
        response.text = "Cohere object text"
        result = unify_response(response, "cohere")
        assert result == "Cohere object text"
    
    def test_unify_response_ollama_dict(self):
        """Test unify_response with Ollama dict format."""
        response = {"response": "Ollama response"}
        result = unify_response(response, "ollama")
        assert result == "Ollama response"
    
    def test_unify_response_unknown_provider(self):
        """Test unify_response with unknown provider."""
        response = {"some": "data"}
        result = unify_response(response, "unknown_provider")
        assert result == "{'some': 'data'}"
    
    def test_unify_response_fallback_to_str(self):
        """Test unify_response fallback to str conversion."""
        class CustomObject:
            def __str__(self):
                return "custom object string"
        
        response = CustomObject()
        result = unify_response(response, "openai")
        assert result == "custom object string"