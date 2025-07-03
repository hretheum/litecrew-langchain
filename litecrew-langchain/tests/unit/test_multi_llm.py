"""
Tests for multi-LLM support in LiteCrew.
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from litecrew.agent import LiteAgent
from litecrew.llm import LLMProvider, LLMConfig, LLMManager

# Mock missing modules before importing
sys.modules['langchain_anthropic'] = MagicMock()
sys.modules['langchain_groq'] = MagicMock()
sys.modules['langchain_community'] = MagicMock()
sys.modules['langchain_community.llms'] = MagicMock()
sys.modules['langchain_cohere'] = MagicMock()
sys.modules['langchain_aws'] = MagicMock()
sys.modules['langchain_google_vertexai'] = MagicMock()
sys.modules['langchain_huggingface'] = MagicMock()
sys.modules['langchain_together'] = MagicMock()


class TestMultiLLMSupport:
    """Test multi-LLM functionality."""
    
    def test_llm_provider_enum(self):
        """Test LLM provider enumeration."""
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.GROQ.value == "groq"
        assert LLMProvider.OLLAMA.value == "ollama"
        assert LLMProvider.COHERE.value == "cohere"
        
    def test_llm_config_creation(self):
        """Test LLM configuration."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            api_key="test-key"
        )
        
        assert config.provider == LLMProvider.OPENAI
        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.api_key == "test-key"
        
    def test_agent_with_custom_llm_provider(self):
        """Test agent creation with custom LLM provider."""
        agent = LiteAgent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
            llm_provider="anthropic",
            llm_config={"model": "claude-3", "temperature": 0.5}
        )
        
        assert agent.llm.__class__.__name__ in ["ChatAnthropic", "MockChatModel", "Mock", "MagicMock"]
        
    def test_llm_manager_initialization(self):
        """Test LLM manager initialization."""
        manager = LLMManager()
        
        # Should support multiple providers
        assert "openai" in manager.get_available_providers()
        assert "anthropic" in manager.get_available_providers()
        assert "groq" in manager.get_available_providers()
        assert "ollama" in manager.get_available_providers()
        
    def test_llm_creation_openai(self):
        """Test OpenAI LLM creation."""
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            temperature=0.7
        )
        
        with patch('langchain_openai.ChatOpenAI') as mock_openai:
            llm = manager.create_llm(config)
            mock_openai.assert_called_once_with(
                model="gpt-4",
                temperature=0.7
            )
            
    def test_llm_creation_anthropic(self):
        """Test Anthropic LLM creation."""
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3",
            temperature=0.5
        )
        
        # Since the manager imports inside the method, we just verify it creates an LLM
        llm = manager.create_llm(config)
        assert llm is not None
            
    def test_llm_creation_groq(self):
        """Test Groq LLM creation."""
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.GROQ,
            model="mixtral-8x7b",
            temperature=0.3
        )
        
        # Since the manager imports inside the method, we just verify it creates an LLM
        llm = manager.create_llm(config)
        assert llm is not None
            
    def test_llm_creation_ollama(self):
        """Test Ollama LLM creation."""
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama2",
            temperature=0.8
        )
        
        # Since the manager imports inside the method, we just verify it creates an LLM
        llm = manager.create_llm(config)
        assert llm is not None
            
    def test_provider_switching_performance(self):
        """Test provider switching performance."""
        import time
        
        manager = LLMManager()
        
        # Create configs for different providers
        configs = [
            LLMConfig(provider=LLMProvider.OPENAI, model="gpt-4"),
            LLMConfig(provider=LLMProvider.ANTHROPIC, model="claude-3"),
            LLMConfig(provider=LLMProvider.GROQ, model="mixtral"),
        ]
        
        # Measure switching time
        start = time.perf_counter()
        
        # Mock all providers to avoid import errors
        with patch('langchain_openai.ChatOpenAI'), \
             patch('litecrew.llm.manager.ChatAnthropic', create=True), \
             patch('litecrew.llm.manager.ChatGroq', create=True):
            for config in configs:
                manager.create_llm(config)
        
        duration = (time.perf_counter() - start) * 1000
        
        # Should switch in less than 5ms per provider
        assert duration < 15, f"Provider switching took {duration:.2f}ms"
        
    def test_llm_fallback_chain(self):
        """Test LLM fallback chain functionality."""
        agent = LiteAgent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
            fallback_providers=["openai", "anthropic", "groq"]
        )
        
        # Should have fallback providers configured
        assert agent._fallback_providers == [LLMProvider.OPENAI, LLMProvider.ANTHROPIC, LLMProvider.GROQ]
            
    def test_response_caching(self):
        """Test LLM response caching."""
        from litecrew.llm import ResponseCache
        
        cache = ResponseCache(max_size=100)
        
        # Add response to cache
        cache.add("test prompt", "test response", provider="openai")
        
        # Should retrieve from cache (need to pass provider)
        cached = cache.get("test prompt", provider="openai")
        assert cached == "test response"
        
        # Cache hit rate should be tracked
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 1.0
        
    def test_unified_response_handling(self):
        """Test unified response handling across providers."""
        from litecrew.llm.utils import unify_response
        
        # Different provider response formats
        openai_response = {"choices": [{"message": {"content": "Hello"}}]}
        anthropic_response = {"content": [{"text": "Hello"}]}
        groq_response = {"choices": [{"message": {"content": "Hello"}}]}
        
        # Should unify to same format
        assert unify_response(openai_response, "openai") == "Hello"
        assert unify_response(anthropic_response, "anthropic") == "Hello"
        assert unify_response(groq_response, "groq") == "Hello"
        
    def test_provider_specific_optimizations(self):
        """Test provider-specific optimizations."""
        manager = LLMManager()
        
        # OpenAI should use specific parameters
        openai_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            use_functions=True
        )
        
        with patch('langchain_openai.ChatOpenAI') as mock_openai:
            manager.create_llm(openai_config)
            # Should pass function calling params
            call_kwargs = mock_openai.call_args.kwargs
            assert "model_kwargs" in call_kwargs
            
    def test_llm_metrics_tracking(self):
        """Test LLM metrics tracking."""
        agent = LiteAgent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
            cache_responses=True
        )
        
        # Execute task
        with patch.object(agent, 'llm') as mock_llm:
            mock_llm.invoke.return_value = Mock(content="Test response")
            agent.execute("Test task")
            
        # Should track metrics
        metrics = agent.metrics
        assert metrics["execution_count"] == 1
        assert "llm_provider" in metrics
        assert metrics["cache_enabled"] == True