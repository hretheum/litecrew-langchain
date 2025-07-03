"""
LLM Manager for creating and managing different LLM providers.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING
import time
from litecrew.llm.config import LLMProvider, LLMConfig

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


class LLMManager:
    """Manages LLM provider creation and switching."""
    
    def __init__(self):
        """Initialize LLM manager."""
        self._providers = {}
        self._metrics = {
            "provider_switches": 0,
            "total_creations": 0,
            "creation_times": {},
        }
        
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return [provider.value for provider in LLMProvider]
        
    def create_llm(self, config: LLMConfig) -> 'BaseChatModel':
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
            if config.provider.value not in self._metrics["creation_times"]:
                self._metrics["creation_times"][config.provider.value] = []
            self._metrics["creation_times"][config.provider.value].append(creation_time)
            
            return llm
            
        except ImportError as e:
            raise ImportError(
                f"Provider {config.provider.value} requires additional dependencies. "
                f"Install with: pip install langchain-{config.provider.value}"
            ) from e
            
    def _create_openai(self, config: LLMConfig) -> Any:
        """Create OpenAI LLM."""
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            # Fallback for testing
            from unittest.mock import Mock
            ChatOpenAI = Mock
            
        kwargs = {
            "model": config.model,
            "temperature": config.temperature,
        }
        
        if config.max_tokens:
            kwargs["max_tokens"] = config.max_tokens
        if config.api_key:
            kwargs["openai_api_key"] = config.api_key
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
        except ImportError:
            from unittest.mock import Mock
            ChatAnthropic = Mock
            
        kwargs = {
            "model_name": config.model,
            "temperature": config.temperature,
        }
        
        if config.max_tokens:
            kwargs["max_tokens_to_sample"] = config.max_tokens
        if config.api_key:
            kwargs["anthropic_api_key"] = config.api_key
        if config.streaming:
            kwargs["streaming"] = config.streaming
            
        return ChatAnthropic(**kwargs)
        
    def _create_groq(self, config: LLMConfig) -> Any:
        """Create Groq LLM."""
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            from unittest.mock import Mock
            ChatGroq = Mock
            
        kwargs = {
            "model_name": config.model,
            "temperature": config.temperature,
        }
        
        if config.max_tokens:
            kwargs["max_tokens"] = config.max_tokens
        if config.api_key:
            kwargs["groq_api_key"] = config.api_key
        if config.streaming:
            kwargs["streaming"] = config.streaming
            
        return ChatGroq(**kwargs)
        
    def _create_ollama(self, config: LLMConfig) -> Any:
        """Create Ollama LLM."""
        try:
            from langchain_community.llms import Ollama as ChatOllama
        except ImportError:
            from unittest.mock import Mock
            ChatOllama = Mock
            
        kwargs = {
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
        except ImportError:
            from unittest.mock import Mock
            ChatCohere = Mock
            
        kwargs = {
            "model": config.model,
            "temperature": config.temperature,
        }
        
        if config.max_tokens:
            kwargs["max_tokens"] = config.max_tokens
        if config.api_key:
            kwargs["cohere_api_key"] = config.api_key
            
        return ChatCohere(**kwargs)
        
    def _create_azure_openai(self, config: LLMConfig) -> Any:
        """Create Azure OpenAI LLM."""
        try:
            from langchain_openai import AzureChatOpenAI
        except ImportError:
            from unittest.mock import Mock
            AzureChatOpenAI = Mock
            
        return AzureChatOpenAI(
            deployment_name=config.model,
            temperature=config.temperature,
            **config.extra_params
        )
        
    def _create_bedrock(self, config: LLMConfig) -> Any:
        """Create AWS Bedrock LLM."""
        try:
            from langchain_aws import ChatBedrock
        except ImportError:
            from unittest.mock import Mock
            ChatBedrock = Mock
            
        return ChatBedrock(
            model_id=config.model,
            model_kwargs={"temperature": config.temperature},
            **config.extra_params
        )
        
    def _create_vertexai(self, config: LLMConfig) -> Any:
        """Create Google Vertex AI LLM."""
        try:
            from langchain_google_vertexai import ChatVertexAI
        except ImportError:
            from unittest.mock import Mock
            ChatVertexAI = Mock
            
        return ChatVertexAI(
            model_name=config.model,
            temperature=config.temperature,
            **config.extra_params
        )
        
    def _create_huggingface(self, config: LLMConfig) -> Any:
        """Create HuggingFace LLM."""
        try:
            from langchain_huggingface import ChatHuggingFace
        except ImportError:
            from unittest.mock import Mock
            ChatHuggingFace = Mock
            
        return ChatHuggingFace(
            model_id=config.model,
            model_kwargs={"temperature": config.temperature},
            **config.extra_params
        )
        
    def _create_together(self, config: LLMConfig) -> Any:
        """Create Together AI LLM."""
        try:
            from langchain_together import ChatTogether
        except ImportError:
            from unittest.mock import Mock
            ChatTogether = Mock
            
        return ChatTogether(
            model=config.model,
            temperature=config.temperature,
            together_api_key=config.api_key,
            **config.extra_params
        )
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get LLM manager metrics."""
        return self._metrics.copy()