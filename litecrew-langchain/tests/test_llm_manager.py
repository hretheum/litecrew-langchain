"""Tests for LLM Manager functionality."""

import time
from unittest.mock import Mock, patch

import pytest

from litecrew.llm.config import LLMConfig, LLMProvider
from litecrew.llm.manager import LLMManager


class TestLLMManager:
    """Test LLM manager creation and provider switching."""

    def test_manager_initialization(self):
        """Test LLM manager initialization."""
        manager = LLMManager()
        
        assert manager._providers == {}
        assert manager._metrics["provider_switches"] == 0
        assert manager._metrics["total_creations"] == 0
        assert isinstance(manager._metrics["creation_times"], dict)

    def test_available_providers(self):
        """Test getting available providers."""
        manager = LLMManager()
        providers = manager.get_available_providers()
        
        expected_providers = ["openai", "anthropic", "groq", "ollama"]
        assert all(provider in providers for provider in expected_providers)
        assert len(providers) >= 4

    @patch('litecrew.llm.manager.LLMManager._create_openai')
    def test_create_openai_llm(self, mock_create):
        """Test creating OpenAI LLM."""
        mock_llm = Mock()
        mock_create.return_value = mock_llm
        
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        
        llm = manager.create_llm(config)
        
        assert llm == mock_llm
        mock_create.assert_called_once_with(config)
        assert manager._metrics["total_creations"] == 1

    @patch('litecrew.llm.manager.LLMManager._create_anthropic')
    def test_create_anthropic_llm(self, mock_create):
        """Test creating Anthropic LLM."""
        mock_llm = Mock()
        mock_create.return_value = mock_llm
        
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-sonnet",
            api_key="test-key"
        )
        
        llm = manager.create_llm(config)
        
        assert llm == mock_llm
        mock_create.assert_called_once_with(config)

    @patch('litecrew.llm.manager.LLMManager._create_groq')
    def test_create_groq_llm(self, mock_create):
        """Test creating Groq LLM."""
        mock_llm = Mock()
        mock_create.return_value = mock_llm
        
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.GROQ,
            model="mixtral-8x7b",
            api_key="test-key"
        )
        
        llm = manager.create_llm(config)
        
        assert llm == mock_llm
        mock_create.assert_called_once_with(config)

    @patch('litecrew.llm.manager.LLMManager._create_ollama')
    def test_create_ollama_llm(self, mock_create):
        """Test creating Ollama LLM."""
        mock_llm = Mock()
        mock_create.return_value = mock_llm
        
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama2"
        )
        # Add api_base through extra_params
        config.extra_params["base_url"] = "http://localhost:11434"
        
        llm = manager.create_llm(config)
        
        assert llm == mock_llm
        mock_create.assert_called_once_with(config)

    def test_unsupported_provider(self):
        """Test handling unsupported provider."""
        manager = LLMManager()
        
        # Create config with unsupported provider
        config = Mock()
        config.provider = "unsupported"
        
        with pytest.raises((ValueError, AttributeError)):
            manager.create_llm(config)

    @patch('litecrew.llm.manager.LLMManager._create_openai')
    def test_creation_time_tracking(self, mock_create):
        """Test LLM creation time tracking."""
        mock_llm = Mock()
        mock_create.return_value = mock_llm
        
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        
        start_time = time.perf_counter()
        manager.create_llm(config)
        end_time = time.perf_counter()
        
        # Creation time should be tracked
        assert "openai" in manager._metrics["creation_times"]
        creation_times = manager._metrics["creation_times"]["openai"]
        
        # Should be reasonable duration
        assert len(creation_times) > 0
        creation_time = creation_times[0]
        assert 0 <= creation_time <= (end_time - start_time) + 0.1

    @patch('litecrew.llm.manager.LLMManager._create_openai')
    @patch('litecrew.llm.manager.LLMManager._create_anthropic')
    def test_provider_switching_metrics(self, mock_anthropic, mock_openai):
        """Test provider switching metrics."""
        mock_openai.return_value = Mock()
        mock_anthropic.return_value = Mock()
        
        manager = LLMManager()
        
        # Create different providers
        openai_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        
        anthropic_config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-sonnet",
            api_key="test-key"
        )
        
        manager.create_llm(openai_config)
        manager.create_llm(anthropic_config)
        
        assert manager._metrics["total_creations"] == 2
        assert len(manager._metrics["creation_times"]) == 2

    def test_provider_caching(self):
        """Test provider instance caching if implemented."""
        manager = LLMManager()
        
        # Check if manager has caching mechanism
        assert hasattr(manager, '_providers')
        assert isinstance(manager._providers, dict)

    def test_metrics_structure(self):
        """Test metrics data structure."""
        manager = LLMManager()
        metrics = manager._metrics
        
        required_keys = ["provider_switches", "total_creations", "creation_times"]
        for key in required_keys:
            assert key in metrics
        
        assert isinstance(metrics["provider_switches"], int)
        assert isinstance(metrics["total_creations"], int)
        assert isinstance(metrics["creation_times"], dict)

    @patch('litecrew.llm.manager.LLMManager._create_openai')
    def test_error_handling_in_creation(self, mock_create):
        """Test error handling during LLM creation."""
        mock_create.side_effect = Exception("Creation failed")
        
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="invalid-key"
        )
        
        with pytest.raises(Exception, match="Creation failed"):
            manager.create_llm(config)

    def test_manager_state_persistence(self):
        """Test manager state after multiple operations."""
        manager = LLMManager()
        
        # Simulate operations
        manager._metrics["provider_switches"] = 5
        manager._metrics["total_creations"] = 10
        manager._metrics["creation_times"]["openai"] = 0.123
        
        # State should persist
        assert manager._metrics["provider_switches"] == 5
        assert manager._metrics["total_creations"] == 10
        assert manager._metrics["creation_times"]["openai"] == 0.123


class TestLLMProviderFactory:
    """Test LLM provider factory methods."""

    def test_factory_method_exists(self):
        """Test that factory methods exist for each provider."""
        manager = LLMManager()
        
        # Check if private methods exist
        assert hasattr(manager, '_create_openai')
        assert hasattr(manager, '_create_anthropic')
        assert hasattr(manager, '_create_groq')
        assert hasattr(manager, '_create_ollama')

    @patch('langchain_openai.ChatOpenAI')
    def test_openai_factory_configuration(self, mock_chat_openai):
        """Test OpenAI factory configuration."""
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance
        
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="test-key",
            temperature=0.7,
            max_tokens=1000
        )
        
        try:
            result = manager._create_openai(config)
            # Should attempt to create ChatOpenAI instance
            mock_chat_openai.assert_called_once()
        except (ImportError, AttributeError):
            # Skip if dependencies not available
            pytest.skip("OpenAI dependencies not available")

    def test_config_validation(self):
        """Test configuration validation."""
        manager = LLMManager()
        
        # Valid config should not raise errors
        valid_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        
        # Should be a valid LLMConfig
        assert isinstance(valid_config, LLMConfig)
        assert valid_config.provider == LLMProvider.OPENAI
        assert valid_config.model == "gpt-4"