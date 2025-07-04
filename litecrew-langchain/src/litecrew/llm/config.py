"""
LLM configuration and provider definitions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class LLMProvider(Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    OLLAMA = "ollama"
    COHERE = "cohere"
    AZURE_OPENAI = "azure_openai"
    BEDROCK = "bedrock"
    VERTEXAI = "vertexai"
    HUGGINGFACE = "huggingface"
    TOGETHER = "together"


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""

    provider: LLMProvider
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3

    # Provider-specific options
    use_functions: bool = False
    streaming: bool = False

    # Additional parameters
    extra_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        config = {
            "provider": self.provider.value,
            "model": self.model,
            "temperature": self.temperature,
        }

        if self.max_tokens:
            config["max_tokens"] = self.max_tokens
        if self.api_key:
            config["api_key"] = self.api_key
        if self.api_base:
            config["api_base"] = self.api_base

        config.update(self.extra_params)
        return config
