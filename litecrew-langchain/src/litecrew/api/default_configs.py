"""Default configurations for quick start."""

from typing import Any, Dict


class DefaultConfigs:
    """Default configurations for common scenarios."""

    # LLM configurations
    LLM_CONFIGS = {
        "fast": {
            "provider": "groq",
            "model": "llama-3.1-8b-instant",
            "temperature": 0.7,
        },
        "balanced": {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "temperature": 0.7,
        },
        "quality": {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.7,
        },
        "local": {
            "provider": "ollama",
            "model": "llama3.2",
            "temperature": 0.7,
        },
    }

    # Process configurations
    PROCESS_CONFIGS = {
        "quick": {
            "max_turns": 5,
            "timeout": 120,  # 2 minutes
        },
        "standard": {
            "max_turns": 10,
            "timeout": 300,  # 5 minutes
        },
        "thorough": {
            "max_turns": 20,
            "timeout": 600,  # 10 minutes
        },
    }

    # Agent configurations
    AGENT_CONFIGS = {
        "verbose": {
            "verbose": True,
            "max_iter": 5,
            "memory": True,
        },
        "quiet": {
            "verbose": False,
            "max_iter": 3,
            "memory": True,
        },
        "efficient": {
            "verbose": False,
            "max_iter": 2,
            "memory": False,
        },
    }

    @classmethod
    def get_llm_config(cls, preset: str = "balanced") -> Dict[str, Any]:
        """Get LLM configuration by preset name."""
        return cls.LLM_CONFIGS.get(preset, cls.LLM_CONFIGS["balanced"]).copy()

    @classmethod
    def get_process_config(cls, preset: str = "standard") -> Dict[str, Any]:
        """Get process configuration by preset name."""
        return cls.PROCESS_CONFIGS.get(preset, cls.PROCESS_CONFIGS["standard"]).copy()

    @classmethod
    def get_agent_config(cls, preset: str = "verbose") -> Dict[str, Any]:
        """Get agent configuration by preset name."""
        return cls.AGENT_CONFIGS.get(preset, cls.AGENT_CONFIGS["verbose"]).copy()

    @classmethod
    def merge_configs(cls, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple configurations, later ones override earlier ones."""
        result = {}
        for config in configs:
            if config:
                result.update(config)
        return result