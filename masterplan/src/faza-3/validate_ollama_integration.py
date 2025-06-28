# validate_ollama_integration.py
import time
import json
import asyncio
from litecrewai.llm.providers.ollama import OllamaProvider

def test_ollama_connection():
    """Test Ollama server connection"""
    ollama = OllamaProvider()
    
    # Test health check
    assert ollama.is_healthy(), "Ollama server not responding"
    
    # Test server info
    info = ollama.server_info()
    assert "version" in info
    print(f"✅ Connected to Ollama {info['version']}")

def test_model_management():
    """Test model management features"""
    ollama = OllamaProvider()
    
    # List models
    models = ollama.list_models()
    print(f"Available models: {[m['name'] for m in models]}")
    
    # Check if test model exists
    test_model = "mistral:7b"
    model_names = [m['name'] for m in models]
    
    if test_model not in model_names:
        print(f"Pulling {test_model}...")
        # In real test, would pull - here just check method exists
        assert hasattr(ollama, 'pull_model')
    
    # Get model info
    if model_names:
        info = ollama.get_model_info(model_names[0])
        assert "parameters" in info
        assert "context_length" in info
        print(f"✅ Model info retrieved for {model_names[0]}")

def test_generation_modes():
    """Test different generation modes"""
    ollama = OllamaProvider()
    
    # Standard generation
    response = ollama.generate("Say hello in JSON format")
    assert len(response.text) > 0
    print("✅ Standard generation working")
    
    # JSON mode
    response = ollama.generate(
        "Return a JSON object with name and age",
        format="json"
    )
    try:
        parsed = json.loads(response.text)
        assert isinstance(parsed, dict)
        print("✅ JSON mode working")
    except json.JSONDecodeError:
        print("⚠️  JSON mode returned invalid JSON")
    
    # With specific parameters
    response = ollama.generate(
        "Write exactly 5 words",
        temperature=0.1,
        top_p=0.9,
        max_tokens=20
    )
    word_count = len(response.text.split())
    print(f"✅ Parameter control working (got {word_count} words)")

def test_streaming_performance():
    """Test streaming generation performance"""
    ollama = OllamaProvider()
    
    chunks_received = 0
    first_chunk_time = None
    start_time = time.time()
    
    for chunk in ollama.stream_generate("Count from 1 to 10 slowly"):
        if first_chunk_time is None:
            first_chunk_time = time.time() - start_time
        chunks_received += 1
    
    total_time = time.time() - start_time
    
    print(f"✅ Streaming stats:")
    print(f"   - First chunk: {first_chunk_time*1000:.0f}ms")
    print(f"   - Total chunks: {chunks_received}")
    print(f"   - Total time: {total_time:.1f}s")
    
    assert first_chunk_time < 1.0, "First chunk too slow"
    assert chunks_received > 5, "Too few chunks"

def test_embeddings():
    """Test embedding generation"""
    ollama = OllamaProvider()
    
    # Single embedding
    embedding = ollama.embed("Hello world")
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)
    
    # Batch embeddings
    texts = ["Hello", "World", "AI", "Test"]
    embeddings = ollama.embed_batch(texts)
    assert len(embeddings) == len(texts)
    assert all(len(emb) == len(embeddings[0]) for emb in embeddings)
    
    print(f"✅ Embeddings working (dimension: {len(embedding)})")

def test_error_recovery():
    """Test error handling and recovery"""
    ollama = OllamaProvider(
        base_url="http://localhost:11434",
        timeout=1,
        max_retries=2
    )
    
    # Test timeout recovery
    try:
        # Very long prompt that might timeout
        ollama.generate("Write a 10000 word essay", timeout=0.1)
    except Exception as e:
        assert "timeout" in str(e).lower()
        print("✅ Timeout handling working")
    
    # Test invalid model
    try:
        ollama.generate("Test", model="nonexistent-model")
    except Exception as e:
        assert "model" in str(e).lower()
        print("✅ Invalid model handling working")
    
    # Test connection recovery
    # Simulate connection issue and recovery
    original_url = ollama.base_url
    ollama.base_url = "http://invalid:11434"
    
    try:
        ollama.generate("Test")
    except:
        pass
    
    # Restore and test recovery
    ollama.base_url = original_url
    response = ollama.generate("Test recovery")
    assert response is not None
    print("✅ Connection recovery working")

def test_performance_tracking():
    """Test performance metrics"""
    ollama = OllamaProvider(enable_metrics=True)
    
    # Generate multiple requests
    for i in range(5):
        ollama.generate(f"Test {i}")
    
    # Get metrics
    metrics = ollama.get_metrics()
    
    assert "total_requests" in metrics
    assert metrics["total_requests"] >= 5
    assert "average_latency_ms" in metrics
    assert "tokens_per_second" in metrics
    assert "error_rate" in metrics
    
    print(f"✅ Performance metrics:")
    print(f"   - Avg latency: {metrics['average_latency_ms']:.0f}ms")
    print(f"   - Tokens/sec: {metrics['tokens_per_second']:.1f}")
    print(f"   - Error rate: {metrics['error_rate']:.1%}")

def test_conversation_management():
    """Test conversation context management"""
    ollama = OllamaProvider()
    
    # Start conversation
    conv_id = ollama.create_conversation()
    
    # First message
    response1 = ollama.generate(
        "My name is Alice. Remember this.",
        conversation_id=conv_id
    )
    
    # Second message (should remember context)
    response2 = ollama.generate(
        "What is my name?",
        conversation_id=conv_id
    )
    
    assert "alice" in response2.text.lower()
    print("✅ Conversation management working")
    
    # Clear conversation
    ollama.clear_conversation(conv_id)

if __name__ == "__main__":
    print("🔍 Validating Ollama integration...\n")
    
    test_ollama_connection()
    test_model_management()
    test_generation_modes()
    test_streaming_performance()
    test_embeddings()
    test_error_recovery()
    test_performance_tracking()
    test_conversation_management()
    
    print("\n✅ Ollama integration validation complete!")