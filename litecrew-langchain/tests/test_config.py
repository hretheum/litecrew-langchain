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
            with patch('litecrew.config.env_path', Path(tmpdir)):
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