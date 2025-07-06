"""
Tests for Claude Opus 4 support.
"""

import pytest

from litecrew.llm.config import LLMConfig, LLMProvider
from litecrew.llm.manager import LLMManager
from litecrew.llm.utils import get_model_context_length


class TestOpus4Support:
    """Test Claude Opus 4 model support."""

    def test_opus4_context_length(self):
        """Test that Opus 4 has correct context length."""
        length = get_model_context_length("anthropic", "claude-opus-4-20250514")
        assert length == 200000

    def test_opus4_partial_match(self):
        """Test that partial model names work."""
        # Should match "claude-opus-4-20250514"
        length = get_model_context_length("anthropic", "claude-opus-4")
        assert length == 200000

    @pytest.mark.skipif(
        not pytest.importorskip("langchain_anthropic", reason="langchain-anthropic not installed"),
        reason="Requires langchain-anthropic"
    )
    def test_create_opus4_llm(self):
        """Test creating Opus 4 LLM instance."""
        manager = LLMManager()
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-opus-4-20250514",
            temperature=0.7,
        )
        
        # Should not raise exception
        llm = manager.create_llm(config)
        assert llm is not None
        
        # Check if model name is set correctly
        if hasattr(llm, "model_name"):
            assert llm.model_name == "claude-opus-4-20250514"

    def test_all_anthropic_models_supported(self):
        """Test that all Anthropic models are recognized."""
        models = [
            "claude-3-opus-20240229",
            "claude-opus-4-20250514",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]
        
        for model in models:
            length = get_model_context_length("anthropic", model)
            assert length > 0, f"Model {model} should be supported"