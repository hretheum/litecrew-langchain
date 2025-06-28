# validate_fallback_system.py
import time
import asyncio
from unittest.mock import Mock, patch
from litecrewai.routing.fallback import (
    FallbackChain, ModelConfig, FallbackTrigger,
    CircuitBreaker, HealthMonitor
)

def test_basic_fallback():
    """Test basic fallback functionality"""
    # Create chain with mocked models
    model1 = Mock()
    model1.generate.side_effect = Exception("Model 1 failed")
    
    model2 = Mock()
    model2.generate.side_effect = Exception("Model 2 failed")
    
    model3 = Mock()
    model3.generate.return_value = Mock(text="Success from model 3")
    
    chain = FallbackChain([
        ModelConfig("model1", provider=model1),
        ModelConfig("model2", provider=model2),
        ModelConfig("model3", provider=model3)
    ])
    
    result = chain.execute("Test task")
    
    assert result.success == True
    assert result.model_used == "model3"
    assert result.total_attempts == 3
    assert len(result.fallback_trail) == 2
    
    print("✅ Basic fallback working")
    print(f"   Trail: {' → '.join([f['from'] for f in result.fallback_trail])}")

def test_retry_with_backoff():
    """Test retry logic with exponential backoff"""
    model = Mock()
    model.generate.side_effect = [
        Exception("Attempt 1"),
        Exception("Attempt 2"),
        Mock(text="Success on attempt 3")
    ]
    
    chain = FallbackChain([
        ModelConfig("model1", provider=model, retry_times=3, backoff_base=0.1)
    ])
    
    start = time.time()
    result = chain.execute("Test task")
    duration = time.time() - start
    
    assert result.success == True
    assert result.total_attempts == 3
    # Should have delays: 0.1s, 0.2s
    assert duration >= 0.3
    
    print(f"✅ Retry with backoff working (took {duration:.2f}s)")

def test_timeout_fallback():
    """Test timeout-triggered fallback"""
    def slow_model(prompt):
        time.sleep(2)
        return Mock(text="Slow response")
    
    def fast_model(prompt):
        return Mock(text="Fast response")
    
    model1 = Mock()
    model1.generate = slow_model
    
    model2 = Mock()
    model2.generate = fast_model
    
    chain = FallbackChain([
        ModelConfig("slow_model", provider=model1),
        ModelConfig("fast_model", provider=model2)
    ], timeout=1.0)
    
    start = time.time()
    result = chain.execute("Test task")
    duration = time.time() - start
    
    assert result.success == True
    assert result.model_used == "fast_model"
    assert duration < 2
    assert any(f["reason"] == "timeout" for f in result.fallback_trail)
    
    print(f"✅ Timeout fallback working (switched in {duration:.2f}s)")

def test_quality_triggered_fallback():
    """Test quality-based fallback"""
    def low_quality_response(prompt):
        return Mock(text="Bad answer", quality_score=0.3)
    
    def high_quality_response(prompt):
        return Mock(text="Excellent answer", quality_score=0.95)
    
    model1 = Mock()
    model1.generate = low_quality_response
    
    model2 = Mock()
    model2.generate = high_quality_response
    
    chain = FallbackChain([
        ModelConfig("low_quality", provider=model1),
        ModelConfig("high_quality", provider=model2)
    ], min_quality=0.8)
    
    result = chain.execute("Test task")
    
    assert result.success == True
    assert result.model_used == "high_quality"
    assert result.quality_score >= 0.8
    assert any(f["reason"] == "quality_below_threshold" for f in result.fallback_trail)
    
    print("✅ Quality-triggered fallback working")

def test_circuit_breaker():
    """Test circuit breaker pattern"""
    model = Mock()
    model.generate.side_effect = Exception("Service down")
    
    breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=1.0,
        expected_exception=Exception
    )
    
    # Make requests until circuit opens
    for i in range(5):
        try:
            with breaker:
                model.generate("Test")
        except:
            pass
    
    assert breaker.current_state == "open"
    print("✅ Circuit breaker opened after failures")
    
    # Should fail fast when open
    start = time.time()
    try:
        with breaker:
            model.generate("Test")
        assert False, "Should fail immediately"
    except Exception as e:
        assert "Circuit breaker is open" in str(e)
        assert time.time() - start < 0.1
    
    print("✅ Circuit breaker fails fast when open")
    
    # Wait for recovery
    time.sleep(1.1)
    
    # Should be half-open now
    assert breaker.current_state == "half-open"
    
    # Successful request should close circuit
    model.generate.side_effect = None
    model.generate.return_value = Mock(text="Success")
    
    with breaker:
        result = model.generate("Test")
    
    assert breaker.current_state == "closed"
    print("✅ Circuit breaker recovery working")

def test_context_preservation():
    """Test context preserved across fallbacks"""
    conversation_state = {"messages": [], "user": "test_user"}
    
    def model_with_context(prompt, context=None):
        assert context is not None
        assert context["user"] == "test_user"
        return Mock(text=f"Response with context for {context['user']}")
    
    model1 = Mock()
    model1.generate.side_effect = Exception("Fail")
    
    model2 = Mock()
    model2.generate = model_with_context
    
    chain = FallbackChain([
        ModelConfig("model1", provider=model1),
        ModelConfig("model2", provider=model2)
    ])
    
    result = chain.execute("Test task", context=conversation_state)
    
    assert result.success == True
    assert "test_user" in result.text
    print("✅ Context preserved across fallback")

def test_health_monitoring():
    """Test health monitoring system"""
    monitor = HealthMonitor()
    
    # Record some events
    monitor.record_success("model1", latency_ms=100)
    monitor.record_success("model1", latency_ms=150)
    monitor.record_failure("model1", error="Timeout")
    monitor.record_success("model1", latency_ms=120)
    
    monitor.record_failure("model2", error="Rate limit")
    monitor.record_failure("model2", error="API error")
    
    # Get health status
    health = monitor.get_health_status()
    
    model1_health = health["model1"]
    assert model1_health.success_rate == 0.75  # 3/4
    assert model1_health.avg_latency_ms == 123.33  # (100+150+120)/3
    assert model1_health.state == "healthy"
    
    model2_health = health["model2"]
    assert model2_health.success_rate == 0.0
    assert model2_health.state == "unhealthy"
    
    print("✅ Health monitoring working")
    print(f"   Model1: {model1_health.state} ({model1_health.success_rate:.1%})")
    print(f"   Model2: {model2_health.state} ({model2_health.success_rate:.1%})")

def test_geographic_fallback():
    """Test geographic/region-based fallback"""
    # Mock latency testing
    def get_latency(endpoint):
        latencies = {
            "us-east": 50,
            "us-west": 150,
            "eu-west": 200,
            "asia": 300
        }
        return latencies.get(endpoint, 1000)
    
    chain = FallbackChain.create_geographic([
        ModelConfig("openai", regions=["us-east", "us-west"]),
        ModelConfig("anthropic", regions=["us-west", "eu-west"]),
        ModelConfig("local", regions=["local"])
    ])
    
    # Should select based on latency
    with patch('litecrewai.routing.fallback.test_latency', get_latency):
        result = chain.select_optimal_endpoint()
    
    assert result.region == "us-east"
    assert result.model == "openai"
    print(f"✅ Geographic fallback selected: {result.model} ({result.region})")

def test_fallback_logging():
    """Test comprehensive logging"""
    import logging
    from io import StringIO
    
    # Capture logs
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logger = logging.getLogger('litecrewai.fallback')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    # Create failing chain
    model1 = Mock()
    model1.generate.side_effect = Exception("Test error")
    
    model2 = Mock()
    model2.generate.return_value = Mock(text="Success")
    
    chain = FallbackChain([
        ModelConfig("failing_model", provider=model1),
        ModelConfig("working_model", provider=model2)
    ])
    
    result = chain.execute("Test task")
    
    # Check logs
    logs = log_capture.getvalue()
    assert "Attempting with model: failing_model" in logs
    assert "Test error" in logs
    assert "Falling back from failing_model to working_model" in logs
    assert "Success with model: working_model" in logs
    
    print("✅ Fallback logging comprehensive")

if __name__ == "__main__":
    print("🔍 Validating fallback system...\n")
    
    test_basic_fallback()
    test_retry_with_backoff()
    test_timeout_fallback()
    test_quality_triggered_fallback()
    test_circuit_breaker()
    test_context_preservation()
    test_health_monitoring()
    test_geographic_fallback()
    test_fallback_logging()
    
    print("\n✅ Fallback system validation complete!")