"""Tests for API default configurations module."""

from litecrew.api.default_configs import DefaultConfigs


class TestDefaultConfigs:
    """Test default configurations."""

    def test_llm_configs_exist(self):
        """Test that LLM configs are defined."""
        assert hasattr(DefaultConfigs, "LLM_CONFIGS")
        assert isinstance(DefaultConfigs.LLM_CONFIGS, dict)
        assert len(DefaultConfigs.LLM_CONFIGS) > 0

        # Test all presets exist
        assert "fast" in DefaultConfigs.LLM_CONFIGS
        assert "balanced" in DefaultConfigs.LLM_CONFIGS
        assert "quality" in DefaultConfigs.LLM_CONFIGS
        assert "local" in DefaultConfigs.LLM_CONFIGS

    def test_process_configs_exist(self):
        """Test that process configs are defined."""
        assert hasattr(DefaultConfigs, "PROCESS_CONFIGS")
        assert isinstance(DefaultConfigs.PROCESS_CONFIGS, dict)
        assert len(DefaultConfigs.PROCESS_CONFIGS) > 0

        # Test all presets exist
        assert "quick" in DefaultConfigs.PROCESS_CONFIGS
        assert "standard" in DefaultConfigs.PROCESS_CONFIGS
        assert "thorough" in DefaultConfigs.PROCESS_CONFIGS

    def test_agent_configs_exist(self):
        """Test that agent configs are defined."""
        assert hasattr(DefaultConfigs, "AGENT_CONFIGS")
        assert isinstance(DefaultConfigs.AGENT_CONFIGS, dict)
        assert len(DefaultConfigs.AGENT_CONFIGS) > 0

        # Test all presets exist
        assert "verbose" in DefaultConfigs.AGENT_CONFIGS
        assert "quiet" in DefaultConfigs.AGENT_CONFIGS
        assert "efficient" in DefaultConfigs.AGENT_CONFIGS

    def test_get_llm_config(self):
        """Test getting LLM configuration."""
        # Test default (balanced)
        config = DefaultConfigs.get_llm_config()
        assert config["provider"] == "openai"
        assert config["model"] == "gpt-4o-mini"
        assert config["temperature"] == 0.7

        # Test fast preset
        config = DefaultConfigs.get_llm_config("fast")
        assert config["provider"] == "groq"
        assert config["model"] == "llama-3.1-8b-instant"

        # Test quality preset
        config = DefaultConfigs.get_llm_config("quality")
        assert config["provider"] == "openai"
        assert config["model"] == "gpt-4o"

        # Test local preset
        config = DefaultConfigs.get_llm_config("local")
        assert config["provider"] == "ollama"
        assert config["model"] == "llama3.2"

        # Test invalid preset returns default
        config = DefaultConfigs.get_llm_config("invalid")
        assert config["provider"] == "openai"
        assert config["model"] == "gpt-4o-mini"

    def test_get_process_config(self):
        """Test getting process configuration."""
        # Test default (standard)
        config = DefaultConfigs.get_process_config()
        assert config["max_turns"] == 10
        assert config["timeout"] == 300

        # Test quick preset
        config = DefaultConfigs.get_process_config("quick")
        assert config["max_turns"] == 5
        assert config["timeout"] == 120

        # Test thorough preset
        config = DefaultConfigs.get_process_config("thorough")
        assert config["max_turns"] == 20
        assert config["timeout"] == 600

        # Test invalid preset returns default
        config = DefaultConfigs.get_process_config("invalid")
        assert config["max_turns"] == 10
        assert config["timeout"] == 300

    def test_get_agent_config(self):
        """Test getting agent configuration."""
        # Test default (verbose)
        config = DefaultConfigs.get_agent_config()
        assert config["verbose"] is True
        assert config["max_iter"] == 5
        assert config["memory"] is True

        # Test quiet preset
        config = DefaultConfigs.get_agent_config("quiet")
        assert config["verbose"] is False
        assert config["max_iter"] == 3
        assert config["memory"] is True

        # Test efficient preset
        config = DefaultConfigs.get_agent_config("efficient")
        assert config["verbose"] is False
        assert config["max_iter"] == 2
        assert config["memory"] is False

        # Test invalid preset returns default
        config = DefaultConfigs.get_agent_config("invalid")
        assert config["verbose"] is True
        assert config["max_iter"] == 5

    def test_merge_configs(self):
        """Test merging configurations."""
        # Test merging two configs
        config1 = {"a": 1, "b": 2}
        config2 = {"b": 3, "c": 4}
        result = DefaultConfigs.merge_configs(config1, config2)
        assert result == {"a": 1, "b": 3, "c": 4}

        # Test merging multiple configs
        config3 = {"c": 5, "d": 6}
        result = DefaultConfigs.merge_configs(config1, config2, config3)
        assert result == {"a": 1, "b": 3, "c": 5, "d": 6}

        # Test merging with None
        result = DefaultConfigs.merge_configs(config1, None, config2)
        assert result == {"a": 1, "b": 3, "c": 4}

        # Test merging empty configs
        result = DefaultConfigs.merge_configs({}, {})
        assert result == {}

    def test_configs_are_copied(self):
        """Test that configs are copied, not referenced."""
        # Get config
        config1 = DefaultConfigs.get_llm_config("fast")
        config2 = DefaultConfigs.get_llm_config("fast")

        # Modify one
        config1["temperature"] = 0.9

        # Other should not be affected
        assert config2["temperature"] == 0.7

        # Original should not be affected
        assert DefaultConfigs.LLM_CONFIGS["fast"]["temperature"] == 0.7
