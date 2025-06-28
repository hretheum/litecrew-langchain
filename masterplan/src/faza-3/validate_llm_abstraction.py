# validate_llm_abstraction.py
import time
import asyncio
from typing import List
from litecrewai.llm import LLMProvider, LLMResponse, LLMError

def test_provider_creation():
    """Test provider factory"""
    # Test various provider strings
    providers = [
        "ollama/mistral",
        "openai/gpt-3.5-turbo",
        "groq/mixtral-8x7b",
        "local/custom-model"
    ]
    
    for provider_string in providers:
        try:
            provider = LLMProvider.create(provider_string)
            assert provider is not None
            assert hasattr(provider, 'generate')
            assert hasattr(provider, 'stream_generate')
            print(f"✅ Created provider: {provider_string}")
        except NotImplementedError:
            print(f"⚠️  Provider not implemented: {provider_string}")

def test_unified_interface():
    """Test all providers implement same interface"""
    from litecrewai.llm.base import BaseLLMProvider
    
    # Get all provider classes
    providers = BaseLLMProvider.__subclasses__()
    
    required_methods = [
        'generate', 'stream_generate', 'embed',
        'count_tokens', 'get_model_info'
    ]
    
    for provider_class in providers:
        for method in required_methods:
            assert hasattr(provider_class, method), \
                f"{provider_class.__name__} missing {method}"
    
    print(f"✅ All {len(providers)} providers implement required interface")

def test_response_format():
    """Test unified response format"""
    provider = LLMProvider.create("ollama/mistral")
    
    response = provider.generate("Say hello")
    
    # Check response structure
    assert isinstance(response, LLMResponse)
    assert hasattr(response, 'text')
    assert hasattr(response, 'tokens_used')
    assert hasattr(response, 'latency_ms')
    assert hasattr(response, 'model')
    assert hasattr(response, 'provider')
    
    # Check values
    assert len(response.text) > 0
    assert response.tokens_used > 0
    assert response.latency_ms > 0
    assert response.model == "mistral"
    assert response.provider == "ollama"
    
    print("✅ Response format validated")

def test_streaming():
    """Test streaming generation"""
    provider = LLMProvider.create("ollama/mistral")
    
    chunks = []
    start = time.time()
    
    for chunk in provider.stream_generate("Count from 1 to 5"):
        assert hasattr(chunk, 'text')
        assert hasattr(chunk, 'is_final')
        chunks.append(chunk.text)
    
    stream_time = time.time() - start
    full_text = ''.join(chunks)
    
    assert len(chunks) > 1, "Should stream multiple chunks"
    assert any(str(i) in full_text for i in range(1, 6))
    print(f"✅ Streaming working ({len(chunks)} chunks in {stream_time:.1f}s)")

def test_error_handling():
    """Test error normalization"""
    provider = LLMProvider.create("ollama/mistral")
    
    # Test timeout
    try:
        provider.generate("Test prompt", timeout=0.001)
        assert False, "Should timeout"
    except LLMError as e:
        assert e.error_type == "timeout"
        assert e.provider == "ollama"
        print("✅ Timeout handling working")
    
    # Test invalid model
    try:
        bad_provider = LLMProvider.create("ollama/nonexistent")
        bad_provider.generate("Test")
        assert False, "Should fail"
    except LLMError as e:
        assert e.error_type == "model_not_found"
        print("✅ Model error handling working")

def test_token_counting():
    """Test token counting accuracy"""
    provider = LLMProvider.create("ollama/mistral")
    
    test_texts = [
        "Hello world",  # ~2 tokens
        "This is a longer sentence with more words.",  # ~10 tokens
        "🚀 Emoji test! 你好世界",  # Special characters
    ]
    
    for text in test_texts:
        count = provider.count_tokens(text)
        assert count > 0
        assert isinstance(count, int)
        print(f"Tokens in '{text[:20]}...': {count}")
    
    print("✅ Token counting working")

def test_context_management():
    """Test context window management"""
    provider = LLMProvider.create("ollama/mistral")
    
    # Get model info
    info = provider.get_model_info()
    assert "context_window" in info
    assert info["context_window"] > 0
    
    # Test with long prompt
    long_prompt = "Hello " * 10000  # Very long
    
    # Should handle gracefully
    response = provider.generate(
        long_prompt,
        truncate=True,  # Auto-truncate to fit
        max_tokens=10
    )
    
    assert response is not None
    assert len(response.text) > 0
    print("✅ Context window management working")

def test_caching():
    """Test response caching"""
    provider = LLMProvider.create(
        "ollama/mistral",
        enable_cache=True
    )
    
    prompt = "What is 2+2?"
    
    # First call
    start = time.time()
    response1 = provider.generate(prompt)
    first_time = time.time() - start
    
    # Second call (should be cached)
    start = time.time()
    response2 = provider.generate(prompt)
    cache_time = time.time() - start
    
    assert response1.text == response2.text
    assert cache_time < first_time / 10  # Much faster
    assert response2.from_cache == True
    
    print(f"✅ Caching working (cache {cache_time*1000:.1f}ms vs {first_time*1000:.1f}ms)")

if __name__ == "__main__":
    print("🔍 Validating LLM abstraction layer...\n")
    
    test_provider_creation()
    test_unified_interface()
    test_response_format()
    test_streaming()
    test_error_handling()
    test_token_counting()
    test_context_management()
    test_caching()
    
    print("\n✅ LLM abstraction validation complete!")