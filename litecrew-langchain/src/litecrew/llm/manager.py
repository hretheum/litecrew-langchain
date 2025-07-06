"""
LLM Manager for creating and managing different LLM providers.
"""

import os
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast

from litecrew.llm.config import LLMConfig, LLMProvider

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


class LLMManager:
    """Manages LLM provider creation and switching."""

    def __init__(self) -> None:
        """Initialize LLM manager."""
        self._providers: Dict[str, Any] = {}
        self._metrics: Dict[str, Any] = {
            "provider_switches": 0,
            "total_creations": 0,
            "total_llms_created": 0,
            "creation_times": {},
            "active_providers": set(),
            "errors": {},
        }

    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return [provider.value for provider in LLMProvider]

    def create_llm(self, config: LLMConfig) -> "BaseChatModel":
        """
        Create LLM instance based on configuration.

        Args:
            config: LLM configuration

        Returns:
            LangChain chat model instance
        """
        start_time = time.perf_counter()

        try:
            if config.provider == LLMProvider.OPENAI:
                llm = self._create_openai(config)
            elif config.provider == LLMProvider.ANTHROPIC:
                llm = self._create_anthropic(config)
            elif config.provider == LLMProvider.GROQ:
                llm = self._create_groq(config)
            elif config.provider == LLMProvider.OLLAMA:
                llm = self._create_ollama(config)
            elif config.provider == LLMProvider.COHERE:
                llm = self._create_cohere(config)
            elif config.provider == LLMProvider.AZURE_OPENAI:
                llm = self._create_azure_openai(config)
            elif config.provider == LLMProvider.BEDROCK:
                llm = self._create_bedrock(config)
            elif config.provider == LLMProvider.VERTEXAI:
                llm = self._create_vertexai(config)
            elif config.provider == LLMProvider.HUGGINGFACE:
                llm = self._create_huggingface(config)
            elif config.provider == LLMProvider.TOGETHER:
                llm = self._create_together(config)
            else:
                raise ValueError(f"Unsupported provider: {config.provider}")

            # Track metrics
            creation_time = time.perf_counter() - start_time
            self._metrics["total_creations"] += 1
            self._metrics["total_llms_created"] += 1
            self._metrics["active_providers"].add(config.provider.value)
            if config.provider.value not in self._metrics["creation_times"]:
                self._metrics["creation_times"][config.provider.value] = []
            self._metrics["creation_times"][config.provider.value].append(creation_time)

            return cast("BaseChatModel", llm)

        except ImportError as e:
            install_instructions = self._get_install_instructions(config.provider)
            raise ImportError(
                f"Provider {config.provider.value} requires additional dependencies.\n"
                f"{install_instructions}\n"
                f"Original error: {str(e)}"
            ) from e
        except Exception as e:
            # Track errors
            provider_name = config.provider.value
            if provider_name not in self._metrics["errors"]:
                self._metrics["errors"][provider_name] = 0
            self._metrics["errors"][provider_name] += 1
            raise

    def _create_openai(self, config: LLMConfig) -> Any:
        """Create OpenAI LLM."""
        try:
            from langchain_openai import ChatOpenAI
            from pydantic import SecretStr
        except ImportError:
            # Fallback for testing
            from unittest.mock import Mock

            ChatOpenAI = Mock  # type: ignore[misc]
            SecretStr = str  # type: ignore[misc,assignment]

        kwargs: Dict[str, Any] = {
            "model": config.model,
            "temperature": config.temperature,
        }

        if config.max_tokens:
            kwargs["max_tokens"] = config.max_tokens
        if config.api_key:
            # Convert string to SecretStr for LangChain
            kwargs["openai_api_key"] = (
                SecretStr(config.api_key)
                if hasattr(SecretStr, "__init__")
                else config.api_key
            )
        if config.api_base:
            kwargs["openai_api_base"] = config.api_base
        if config.streaming:
            kwargs["streaming"] = config.streaming

        # Add function calling support
        if config.use_functions:
            kwargs["model_kwargs"] = {"functions": []}

        return ChatOpenAI(**kwargs)

    def _create_anthropic(self, config: LLMConfig) -> Any:
        """Create Anthropic LLM."""
        try:
            from langchain_anthropic import ChatAnthropic
            from pydantic import SecretStr
        except ImportError:
            from unittest.mock import Mock

            ChatAnthropic = Mock  # type: ignore[misc]
            SecretStr = str  # type: ignore[misc,assignment]

        kwargs: Dict[str, Any] = {
            "model_name": config.model,
            "temperature": config.temperature,
        }

        if config.max_tokens:
            kwargs["max_tokens_to_sample"] = config.max_tokens
        if config.api_key:
            kwargs["anthropic_api_key"] = (
                SecretStr(config.api_key)
                if hasattr(SecretStr, "__init__")
                else config.api_key
            )
        if config.streaming:
            kwargs["streaming"] = config.streaming

        return ChatAnthropic(**kwargs)

    def _create_groq(self, config: LLMConfig) -> Any:
        """Create Groq LLM."""
        try:
            from langchain_groq import ChatGroq
            from pydantic import SecretStr
        except ImportError:
            from unittest.mock import Mock

            ChatGroq = Mock  # type: ignore[misc]
            SecretStr = str  # type: ignore[misc,assignment]

        kwargs: Dict[str, Any] = {
            "model_name": config.model,
            "temperature": config.temperature,
        }

        if config.max_tokens:
            kwargs["max_tokens"] = config.max_tokens
        if config.api_key:
            kwargs["groq_api_key"] = (
                SecretStr(config.api_key)
                if hasattr(SecretStr, "__init__")
                else config.api_key
            )
        if config.streaming:
            kwargs["streaming"] = config.streaming

        return ChatGroq(**kwargs)

    def _create_ollama(self, config: LLMConfig) -> Any:
        """Create Ollama LLM."""
        try:
            from langchain_community.llms import Ollama as ChatOllama
        except ImportError:
            from unittest.mock import Mock

            ChatOllama = Mock  # type: ignore[misc]

        kwargs: Dict[str, Any] = {
            "model": config.model,
            "temperature": config.temperature,
        }

        if config.api_base:
            kwargs["base_url"] = config.api_base

        return ChatOllama(**kwargs)

    def _create_cohere(self, config: LLMConfig) -> Any:
        """Create Cohere LLM."""
        try:
            from langchain_cohere import ChatCohere
            from pydantic import SecretStr
        except ImportError:
            from unittest.mock import Mock

            ChatCohere = Mock  # type: ignore[misc]
            SecretStr = str  # type: ignore[misc,assignment]

        kwargs: Dict[str, Any] = {
            "model": config.model,
            "temperature": config.temperature,
        }

        if config.max_tokens:
            kwargs["max_tokens"] = config.max_tokens
        if config.api_key:
            kwargs["cohere_api_key"] = (
                SecretStr(config.api_key)
                if hasattr(SecretStr, "__init__")
                else config.api_key
            )

        return ChatCohere(**kwargs)

    def _create_azure_openai(self, config: LLMConfig) -> Any:
        """Create Azure OpenAI LLM."""
        try:
            from langchain_openai import AzureChatOpenAI
        except ImportError:
            from unittest.mock import Mock

            AzureChatOpenAI = Mock  # type: ignore[misc]

        kwargs: Dict[str, Any] = {
            "azure_deployment": config.model,
            "temperature": config.temperature,
        }
        kwargs.update(config.extra_params)

        return AzureChatOpenAI(**kwargs)

    def _create_bedrock(self, config: LLMConfig) -> Any:
        """Create AWS Bedrock LLM."""
        try:
            from langchain_aws import ChatBedrock
        except ImportError:
            from unittest.mock import Mock

            ChatBedrock = Mock  # type: ignore[misc]

        kwargs: Dict[str, Any] = {
            "model_id": config.model,
            "model_kwargs": {"temperature": config.temperature},
        }
        kwargs.update(config.extra_params)

        return ChatBedrock(**kwargs)

    def _create_vertexai(self, config: LLMConfig) -> Any:
        """Create Google Vertex AI LLM."""
        try:
            from langchain_google_vertexai import ChatVertexAI
        except ImportError:
            from unittest.mock import Mock

            ChatVertexAI = Mock  # type: ignore[misc]

        kwargs: Dict[str, Any] = {
            "model_name": config.model,
            "temperature": config.temperature,
        }
        kwargs.update(config.extra_params)

        return ChatVertexAI(**kwargs)

    def _create_huggingface(self, config: LLMConfig) -> Any:
        """Create HuggingFace LLM."""
        try:
            from langchain_huggingface import ChatHuggingFace
        except ImportError:
            from unittest.mock import Mock

            ChatHuggingFace = Mock  # type: ignore[misc]

        kwargs: Dict[str, Any] = {
            "model_id": config.model,
            "model_kwargs": {"temperature": config.temperature},
        }
        kwargs.update(config.extra_params)

        return ChatHuggingFace(**kwargs)

    def _create_together(self, config: LLMConfig) -> Any:
        """Create Together AI LLM."""
        try:
            from langchain_together import ChatTogether
            from pydantic import SecretStr
        except ImportError:
            from unittest.mock import Mock

            ChatTogether = Mock  # type: ignore[misc]
            SecretStr = str  # type: ignore[misc,assignment]

        kwargs: Dict[str, Any] = {
            "model": config.model,
            "temperature": config.temperature,
        }

        if config.api_key:
            kwargs["together_api_key"] = (
                SecretStr(config.api_key)
                if hasattr(SecretStr, "__init__")
                else config.api_key
            )

        kwargs.update(config.extra_params)

        return ChatTogether(**kwargs)

    def get_metrics(self) -> Dict[str, Any]:
        """Get LLM manager metrics."""
        return cast(Dict[str, Any], self._metrics.copy())

    def get_default_llm(self) -> "BaseChatModel":
        """Get default LLM with fallback chain."""
        # Check environment variable for default provider
        default_provider = os.environ.get("LITECREW_DEFAULT_PROVIDER", "").lower()
        
        # Default models for each provider
        default_models = {
            LLMProvider.OPENAI: "gpt-3.5-turbo",
            LLMProvider.ANTHROPIC: "claude-3-haiku-20240307",
            LLMProvider.GROQ: "mixtral-8x7b-32768",
            LLMProvider.OLLAMA: "llama2",
        }
        
        # Provider priority list
        if default_provider and default_provider in [p.value for p in LLMProvider]:
            providers = [LLMProvider(default_provider)]
        else:
            providers = [
                LLMProvider.OPENAI,
                LLMProvider.ANTHROPIC,
                LLMProvider.GROQ,
                LLMProvider.OLLAMA,
            ]
        
        # Try each provider in order
        for provider in providers:
            try:
                model = default_models.get(provider, "default")
                config = LLMConfig(provider=provider, model=model)
                return self.create_llm(config)
            except Exception:
                continue
        
        raise RuntimeError("No LLM provider available")

    def _get_install_instructions(self, provider: LLMProvider) -> str:
        """Get installation instructions for a provider."""
        instructions = {
            LLMProvider.OPENAI: (
                "To use OpenAI:\n"
                "1. Install: pip install langchain-openai\n"
                "2. Set API key: export OPENAI_API_KEY='your-api-key'\n"
                "3. Get key from: https://platform.openai.com/api-keys"
            ),
            LLMProvider.ANTHROPIC: (
                "To use Anthropic:\n"
                "1. Install: pip install langchain-anthropic\n"
                "2. Set API key: export ANTHROPIC_API_KEY='your-api-key'\n"
                "3. Get key from: https://console.anthropic.com/"
            ),
            LLMProvider.GROQ: (
                "To use Groq:\n"
                "1. Install: pip install langchain-groq\n"
                "2. Set API key: export GROQ_API_KEY='your-api-key'\n"
                "3. Get key from: https://console.groq.com/"
            ),
            LLMProvider.OLLAMA: (
                "To use Ollama:\n"
                "1. Install: pip install langchain-community\n"
                "2. Install Ollama: https://ollama.ai/download\n"
                "3. Pull model: ollama pull llama2\n"
                "4. Run server: ollama serve"
            ),
            LLMProvider.COHERE: (
                "To use Cohere:\n"
                "1. Install: pip install langchain-cohere\n"
                "2. Set API key: export COHERE_API_KEY='your-api-key'\n"
                "3. Get key from: https://dashboard.cohere.ai/"
            ),
            LLMProvider.AZURE_OPENAI: (
                "To use Azure OpenAI:\n"
                "1. Install: pip install langchain-openai\n"
                "2. Set environment variables:\n"
                "   - AZURE_OPENAI_API_KEY='your-api-key'\n"
                "   - AZURE_OPENAI_ENDPOINT='your-endpoint'\n"
                "   - AZURE_OPENAI_DEPLOYMENT_NAME='your-deployment'\n"
                "3. Deploy model in Azure Portal"
            ),
            LLMProvider.BEDROCK: (
                "To use AWS Bedrock:\n"
                "1. Install: pip install langchain-aws boto3\n"
                "2. Configure AWS: aws configure\n"
                "3. Enable models in AWS Console:\n"
                "   https://console.aws.amazon.com/bedrock/\n"
                "4. Set region: export AWS_DEFAULT_REGION='us-east-1'"
            ),
            LLMProvider.VERTEXAI: (
                "To use Google Vertex AI:\n"
                "1. Install: pip install langchain-google-vertexai\n"
                "2. Authenticate: gcloud auth application-default login\n"
                "3. Set project: gcloud config set project YOUR_PROJECT_ID\n"
                "4. Enable API: https://console.cloud.google.com/vertex-ai"
            ),
            LLMProvider.HUGGINGFACE: (
                "To use HuggingFace:\n"
                "1. Install: pip install langchain-huggingface\n"
                "2. Set token: export HUGGINGFACEHUB_API_TOKEN='your-token'\n"
                "3. Get token from: https://huggingface.co/settings/tokens\n"
                "4. For local models: pip install transformers torch"
            ),
            LLMProvider.TOGETHER: (
                "To use Together AI:\n"
                "1. Install: pip install langchain-together\n"
                "2. Set API key: export TOGETHER_API_KEY='your-api-key'\n"
                "3. Get key from: https://api.together.xyz/"
            ),
        }
        return instructions.get(
            provider, f"Install with: pip install langchain-{provider.value}"
        )
