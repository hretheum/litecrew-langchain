"""
Utility functions for LLM handling.
"""

from typing import Any


def unify_response(response: Any, provider: str) -> str:
    """
    Unify response format across different providers.

    Args:
        response: Raw response from provider
        provider: Provider name

    Returns:
        Unified string response
    """
    if isinstance(response, str):
        return response

    # Handle different provider response formats
    if provider == "openai":
        if isinstance(response, dict) and "choices" in response:
            try:
                return str(response["choices"][0]["message"]["content"])
            except (KeyError, IndexError):
                pass
        elif hasattr(response, "content"):
            return str(response.content)

    elif provider == "anthropic":
        if isinstance(response, dict) and "content" in response:
            try:
                return str(response["content"][0]["text"])
            except (KeyError, IndexError):
                pass
        elif hasattr(response, "content"):
            return str(response.content)

    elif provider in ["groq", "together"]:
        # Similar to OpenAI format
        if isinstance(response, dict) and "choices" in response:
            try:
                return str(response["choices"][0]["message"]["content"])
            except (KeyError, IndexError):
                pass
        elif hasattr(response, "content"):
            return str(response.content)

    elif provider == "cohere":
        if isinstance(response, dict) and "text" in response:
            return str(response["text"])
        elif hasattr(response, "text"):
            return str(response.text)

    elif provider == "ollama":
        if isinstance(response, dict) and "response" in response:
            return str(response["response"])
        elif hasattr(response, "content"):
            return str(response.content)

    # Fallback to string conversion
    return str(response)


def estimate_tokens(text: str, method: str = "simple") -> int:
    """
    Estimate token count for text.

    Args:
        text: Text to estimate
        method: Estimation method ("simple", "tiktoken")

    Returns:
        Estimated token count
    """
    if method == "simple":
        # Simple estimation: ~4 characters per token
        return len(text) // 4

    elif method == "tiktoken":
        try:
            import tiktoken

            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            # Fallback to simple method
            return len(text) // 4

    else:
        raise ValueError(f"Unknown token estimation method: {method}")


def get_model_context_length(provider: str, model: str) -> int:
    """
    Get context length for a model.

    Args:
        provider: Provider name
        model: Model name

    Returns:
        Maximum context length in tokens
    """
    # Common model context lengths
    context_lengths = {
        "openai": {
            "gpt-4": 8192,
            "gpt-4-turbo": 128000,
            "gpt-4-turbo-preview": 128000,
            "gpt-3.5-turbo": 16384,
        },
        "anthropic": {
            "claude-3-opus": 200000,
            "claude-3-opus-20240229": 200000,
            "claude-opus-4": 200000,  # Support partial match
            "claude-opus-4-20250514": 200000,
            "claude-3-sonnet": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku": 200000,
            "claude-3-haiku-20240307": 200000,
            "claude-2.1": 200000,
            "claude-2": 100000,
        },
        "groq": {
            "mixtral-8x7b": 32768,
            "mixtral-8x7b-32768": 32768,
            "llama2-70b": 4096,
        },
        "ollama": {
            "llama2": 4096,
            "mistral": 8192,
            "mixtral": 32768,
        },
    }

    provider_contexts = context_lengths.get(provider, {})

    # Try exact match first
    if model in provider_contexts:
        return provider_contexts[model]

    # Try partial match (for versioned models)
    for key, value in provider_contexts.items():
        if model.startswith(key) or key in model:
            return value

    return 4096  # Default to 4k
