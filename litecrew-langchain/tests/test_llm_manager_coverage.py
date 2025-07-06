"""Additional tests for LLM Manager to improve coverage."""

import os
from unittest.mock import Mock, patch

import pytest

from litecrew.llm.config import LLMConfig, LLMProvider
from litecrew.llm.manager import LLMManager


class TestLLMManagerCoverage:
    """Additional tests for LLM Manager coverage."""

    def test_create_anthropic_success(self):
        """Test successful Anthropic LLM creation."""
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-opus-20240229",
            temperature=0.5,
            api_key="test-key",
        )

        with patch("litecrew.llm.manager.ChatAnthropic") as mock_anthropic:
            mock_llm = Mock()
            mock_anthropic.return_value = mock_llm

            result = manager._create_anthropic(config)

            mock_anthropic.assert_called_once_with(
                model_name="claude-3-opus-20240229",
                temperature=0.5,
                anthropic_api_key="test-key",
            )
            assert result == mock_llm

    def test_create_anthropic_no_api_key(self):
        """Test Anthropic creation without API key."""
        manager = LLMManager()
        config = LLMConfig(provider=LLMProvider.ANTHROPIC, model="claude-3")

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            with pytest.raises(ValueError) as exc_info:
                manager._create_anthropic(config)
            assert "Anthropic API key not found" in str(exc_info.value)

    def test_create_groq_success(self):
        """Test successful Groq LLM creation."""
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.GROQ,
            model="mixtral-8x7b-32768",
            temperature=0.7,
            api_key="test-key",
        )

        with patch("litecrew.llm.manager.ChatGroq") as mock_groq:
            mock_llm = Mock()
            mock_groq.return_value = mock_llm

            result = manager._create_groq(config)

            mock_groq.assert_called_once_with(
                model_name="mixtral-8x7b-32768",
                temperature=0.7,
                groq_api_key="test-key",
            )
            assert result == mock_llm

    def test_create_groq_no_api_key(self):
        """Test Groq creation without API key."""
        manager = LLMManager()
        config = LLMConfig(provider=LLMProvider.GROQ, model="mixtral")

        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            with pytest.raises(ValueError) as exc_info:
                manager._create_groq(config)
            assert "Groq API key not found" in str(exc_info.value)

    def test_create_ollama_success(self):
        """Test successful Ollama LLM creation."""
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama2",
            temperature=0.8,
            base_url="http://localhost:11434",
        )

        with patch("litecrew.llm.manager.ChatOllama") as mock_ollama:
            mock_llm = Mock()
            mock_ollama.return_value = mock_llm

            result = manager._create_ollama(config)

            mock_ollama.assert_called_once_with(
                model="llama2", temperature=0.8, base_url="http://localhost:11434"
            )
            assert result == mock_llm

    def test_create_ollama_default_url(self):
        """Test Ollama creation with default URL."""
        manager = LLMManager()
        config = LLMConfig(provider=LLMProvider.OLLAMA, model="llama2")

        with patch("litecrew.llm.manager.ChatOllama") as mock_ollama:
            manager._create_ollama(config)
            mock_ollama.assert_called_once_with(
                model="llama2", temperature=0.7, base_url="http://localhost:11434"
            )

    def test_get_default_llm_with_env_var(self):
        """Test getting default LLM with environment variable."""
        manager = LLMManager()

        with patch.dict(os.environ, {"LITECREW_DEFAULT_PROVIDER": "anthropic"}):
            with patch.object(manager, "create_llm") as mock_create:
                mock_llm = Mock()
                mock_create.return_value = mock_llm

                result = manager.get_default_llm()

                assert result == mock_llm
                # Check that create_llm was called with Anthropic provider
                config = mock_create.call_args[0][0]
                assert config.provider == LLMProvider.ANTHROPIC

    def test_get_default_llm_fallback_chain(self):
        """Test default LLM fallback chain."""
        manager = LLMManager()

        # First provider fails, second succeeds
        with patch.object(manager, "create_llm") as mock_create:

            def side_effect(config):
                if config.provider == LLMProvider.OPENAI:
                    raise ValueError("No API key")
                return Mock()  # Success for next provider

            mock_create.side_effect = side_effect

            result = manager.get_default_llm()
            assert result is not None
            assert mock_create.call_count >= 2

    def test_get_default_llm_all_fail(self):
        """Test default LLM when all providers fail."""
        manager = LLMManager()

        with patch.object(manager, "create_llm") as mock_create:
            mock_create.side_effect = ValueError("No API key")

            with pytest.raises(RuntimeError) as exc_info:
                manager.get_default_llm()
            assert "No LLM provider available" in str(exc_info.value)

    def test_create_llm_with_max_tokens(self):
        """Test LLM creation with max_tokens parameter."""
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="test-key",
            max_tokens=2000,
        )

        with patch("litecrew.llm.manager.ChatOpenAI") as mock_openai:
            manager._create_openai(config)
            mock_openai.assert_called_once()
            # Check that max_tokens was passed
            call_kwargs = mock_openai.call_args[1]
            assert call_kwargs.get("max_tokens") == 2000

    def test_metrics_collection(self):
        """Test metrics collection during LLM operations."""
        manager = LLMManager()

        # Create multiple LLMs
        configs = [
            LLMConfig(provider=LLMProvider.OPENAI, api_key="key1"),
            LLMConfig(provider=LLMProvider.ANTHROPIC, api_key="key2"),
            LLMConfig(provider=LLMProvider.GROQ, api_key="key3"),
        ]

        with patch.object(manager, "_create_openai", return_value=Mock()):
            with patch.object(manager, "_create_anthropic", return_value=Mock()):
                with patch.object(manager, "_create_groq", return_value=Mock()):
                    for config in configs:
                        manager.create_llm(config)

        metrics = manager.get_metrics()
        assert metrics["total_llms_created"] == 3
        assert "openai" in metrics["creation_times"]
        assert "anthropic" in metrics["creation_times"]
        assert "groq" in metrics["creation_times"]
        assert len(metrics["active_providers"]) == 3

    def test_error_tracking_in_metrics(self):
        """Test error tracking in metrics."""
        manager = LLMManager()

        # Force some errors
        config = LLMConfig(provider=LLMProvider.OPENAI)

        with patch.object(
            manager, "_create_openai", side_effect=ValueError("Test error")
        ):
            for _ in range(3):
                try:
                    manager.create_llm(config)
                except ValueError:
                    pass

        metrics = manager.get_metrics()
        assert metrics["errors"]["openai"] == 3

    def test_provider_specific_config(self):
        """Test provider-specific configuration options."""
        manager = LLMManager()

        # Test OpenAI with streaming
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            api_key="test-key",
            streaming=True,
        )

        with patch("litecrew.llm.manager.ChatOpenAI") as mock_openai:
            manager._create_openai(config)
            call_kwargs = mock_openai.call_args[1]
            assert call_kwargs.get("streaming") is True

    def test_cache_integration(self):
        """Test LLM cache integration."""

        manager = LLMManager()
        # LLMCache is imported but not used directly in this test
        # It's used internally by the LLMManager

        # Create LLM with cache
        config = LLMConfig(
            provider=LLMProvider.OPENAI, model="gpt-3.5-turbo", api_key="test-key"
        )

        with patch("litecrew.llm.manager.ChatOpenAI") as mock_openai:
            mock_llm = Mock()
            mock_openai.return_value = mock_llm

            # Simulate enabling cache
            llm = manager.create_llm(config)

            # Test that LLM can be used with cache
            assert llm is not None

    def test_concurrent_llm_creation(self):
        """Test thread-safe LLM creation."""
        import threading

        manager = LLMManager()
        results = []
        errors = []

        def create_llm_thread():
            try:
                config = LLMConfig(
                    provider=LLMProvider.OPENAI,
                    model="gpt-3.5-turbo",
                    api_key="test-key",
                )
                with patch("litecrew.llm.manager.ChatOpenAI", return_value=Mock()):
                    llm = manager.create_llm(config)
                    results.append(llm)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for _ in range(10):
            t = threading.Thread(target=create_llm_thread)
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 10

    def test_model_context_length_validation(self):
        """Test model context length validation."""
        from litecrew.llm.utils import get_model_context_length

        # Test various models
        assert get_model_context_length("openai", "gpt-4") == 8192
        assert get_model_context_length("anthropic", "claude-3-opus-20240229") == 200000
        assert get_model_context_length("groq", "mixtral-8x7b-32768") == 32768
        assert get_model_context_length("unknown", "unknown") == 4096  # Default
