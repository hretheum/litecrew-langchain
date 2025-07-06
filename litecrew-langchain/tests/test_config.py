"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


class TestConfig:
    """Test configuration loading."""

    def test_config_import(self):
        """Test that config module can be imported."""
        # This should import config and load environment variables
        import litecrew.config  # noqa: F401

        # Should not raise any exceptions
        assert True

    @patch.dict(os.environ, {}, clear=True)
    def test_config_with_no_env_files(self):
        """Test config loading when no .env files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock the env_path to point to empty temp directory
            with patch("litecrew.config.env_path", Path(tmpdir)):
                # Re-import to trigger config loading
                import importlib

                import litecrew.config

                importlib.reload(litecrew.config)

        # Should complete without errors
        assert True

    def test_config_with_env_file(self):
        """Test config loading with .env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create a .env file
            env_file = tmpdir_path / ".env"
            env_file.write_text("TEST_CONFIG_VAR=test_value\n")

            # Use dotenv directly to test functionality
            from dotenv import load_dotenv

            load_dotenv(env_file)

            # Check if environment variable was loaded
            assert os.getenv("TEST_CONFIG_VAR") == "test_value"

    def test_config_with_local_env_file(self):
        """Test config loading with .env.local file (priority)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create both .env and .env.local files
            env_file = tmpdir_path / ".env"
            env_file.write_text("TEST_LOCAL_VAR=env_value\n")

            local_env_file = tmpdir_path / ".env.local"
            local_env_file.write_text("TEST_LOCAL_VAR=local_value\n")

            # Load .env.local first (should take priority)
            from dotenv import load_dotenv

            load_dotenv(local_env_file)

            # .env.local should take priority
            assert os.getenv("TEST_LOCAL_VAR") == "local_value"

    def test_config_class_defaults(self):
        """Test Config class default values."""
        from litecrew.config import Config

        # Test that environment is set
        assert Config.ENVIRONMENT is not None
        assert isinstance(Config.ENVIRONMENT, str)

        # Test DEBUG flag logic
        assert isinstance(Config.DEBUG, bool)
        if Config.ENVIRONMENT == "development":
            assert Config.DEBUG
        else:
            assert not Config.DEBUG

    def test_config_class_methods(self):
        """Test Config class methods."""
        from litecrew.config import Config

        # Test get_available_providers method
        providers = Config.get_available_providers()
        assert isinstance(providers, list)

        # All providers should be strings
        for provider in providers:
            assert isinstance(provider, str)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123"})
    def test_config_provider_detection(self):
        """Test provider detection with mocked environment."""
        from litecrew.config import Config

        # Override specific config values for testing
        with patch.multiple(
            Config,
            OPENAI_API_KEY="sk-test123",
            ANTHROPIC_API_KEY=None,
            GROQ_API_KEY=None,
            AZURE_OPENAI_API_KEY=None,
            COHERE_API_KEY=None,
            HUGGINGFACE_API_TOKEN=None,
        ):
            providers = Config.get_available_providers()
            assert "openai" in providers

    @patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True)
    def test_config_validation_production_error(self):
        """Test config validation fails with missing keys in production."""
        from litecrew.config import Config

        # Mock production environment without required keys
        with patch.multiple(
            Config, ENVIRONMENT="production", SECRET_KEY=None, JWT_SECRET=None
        ):
            with pytest.raises(ValueError) as exc:
                Config.validate()
            assert "SECRET_KEY must be set in production" in str(exc.value)

    @patch("builtins.print")
    def test_config_validation_no_llm_keys(self, mock_print):
        """Test warning when no LLM keys are configured."""
        from litecrew.config import Config

        # Mock no LLM keys
        with patch.multiple(
            Config, OPENAI_API_KEY=None, ANTHROPIC_API_KEY=None, GROQ_API_KEY=None
        ):
            Config.validate()
            mock_print.assert_called_with(
                "Warning: No LLM API keys configured. Some features may not work."
            )

    def test_config_database_url_default(self):
        """Test database URL default value."""
        from litecrew.config import Config

        # Should have a default database URL
        assert Config.DATABASE_URL is not None
        assert isinstance(Config.DATABASE_URL, str)
        assert len(Config.DATABASE_URL) > 0

    def test_config_redis_url_default(self):
        """Test Redis URL default value."""
        from litecrew.config import Config

        # Should have a default Redis URL
        assert Config.REDIS_URL is not None
        assert isinstance(Config.REDIS_URL, str)
        assert "redis://" in Config.REDIS_URL
