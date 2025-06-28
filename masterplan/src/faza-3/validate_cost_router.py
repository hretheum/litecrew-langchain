# validate_cost_router.py
import time
from datetime import datetime, timedelta
from litecrewai.routing import CostAwareRouter, RoutingStrategy

def test_cost_calculation():
    """Test accurate cost calculation"""
    router = CostAwareRouter()
    
    # Test known model costs
    test_cases = [
        ("openai/gpt-3.5-turbo", 100, 0.0001),  # $0.001 per 1K
        ("openai/gpt-4", 100, 0.003),            # $0.03 per 1K
        ("groq/mixtral-8x7b", 100, 0.00002),     # $0.0002 per 1K
        ("ollama/mistral", 100, 0.0),            # Free
    ]
    
    for model, tokens, expected_cost in test_cases:
        cost = router.calculate_cost(model, tokens)
        assert abs(cost - expected_cost) < 0.00001, \
            f"Wrong cost for {model}: {cost} vs {expected_cost}"
        print(f"✅ {model}: ${cost:.5f} for {tokens} tokens")

def test_complexity_analysis():
    """Test task complexity analysis"""
    router = CostAwareRouter()
    
    test_tasks = [
        ("What is 2+2?", "simple"),
        ("Explain quantum physics", "medium"),
        ("Write a research paper on AI ethics with citations", "complex"),
        ("Hi", "simple"),
        ("Analyze this 10-page document and create a summary", "complex")
    ]
    
    for task, expected_complexity in test_tasks:
        complexity = router.analyze_complexity(task)
        assert complexity == expected_complexity, \
            f"Wrong complexity for '{task[:30]}...': {complexity}"
        print(f"✅ Complexity '{expected_complexity}': {task[:30]}...")

def test_routing_strategies():
    """Test different routing strategies"""
    # Greedy strategy (always cheapest)
    router = CostAwareRouter(strategy=RoutingStrategy.GREEDY)
    model = router.select_model("Complex analysis task")
    assert "ollama" in model or "groq" in model
    print(f"✅ Greedy selected: {model}")
    
    # Quality-first strategy
    router = CostAwareRouter(
        strategy=RoutingStrategy.QUALITY_FIRST,
        monthly_budget=1000  # High budget
    )
    model = router.select_model("Write a novel chapter")
    assert "gpt-4" in model or "claude" in model
    print(f"✅ Quality-first selected: {model}")
    
    # Balanced strategy
    router = CostAwareRouter(strategy=RoutingStrategy.BALANCED)
    model = router.select_model("Summarize this article")
    assert model in ["groq/mixtral-8x7b", "openai/gpt-3.5-turbo"]
    print(f"✅ Balanced selected: {model}")

def test_budget_management():
    """Test budget tracking and limits"""
    router = CostAwareRouter(
        monthly_budget=1.0,  # $1 for testing
        strategy=RoutingStrategy.BALANCED
    )
    
    # Simulate spending
    router._spend(0.70)  # Spend 70% of budget
    
    # Should downgrade to cheaper models
    model = router.select_model("Complex task")
    assert "ollama" in model or "groq" in model, \
        "Should use cheap model when budget low"
    
    # Test budget alerts
    alerts = router.get_budget_alerts()
    assert len(alerts) > 0
    assert any("70%" in alert for alert in alerts)
    print("✅ Budget alerts working")
    
    # Test budget exceeded
    router._spend(0.35)  # Total 105%
    model = router.select_model("Any task")
    assert "ollama" in model, "Should only use free models when over budget"
    print("✅ Budget enforcement working")

def test_routing_performance():
    """Test routing decision performance"""
    router = CostAwareRouter()
    
    # Measure routing time
    times = []
    for _ in range(100):
        start = time.time()
        model = router.select_model("Test task for routing")
        times.append((time.time() - start) * 1000)
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    print(f"✅ Routing performance:")
    print(f"   - Average: {avg_time:.1f}ms")
    print(f"   - Max: {max_time:.1f}ms")
    
    assert avg_time < 50, f"Routing too slow: {avg_time}ms"
    assert max_time < 100, f"Max routing too slow: {max_time}ms"

def test_prompt_optimization():
    """Test prompt compression and optimization"""
    router = CostAwareRouter()
    
    # Long, redundant prompt
    original_prompt = """
    I need you to help me with something. What I want you to do is to 
    analyze the following text and provide a summary. The text is about 
    artificial intelligence. Please read it carefully and then write a 
    summary. Here is the text: AI is transforming the world...
    """ * 10  # Make it long
    
    # Optimize for expensive model
    optimized = router.optimize_prompt(original_prompt, "openai/gpt-4")
    
    assert len(optimized) < len(original_prompt) * 0.8
    assert "analyze" in optimized.lower()
    assert "summary" in optimized.lower()
    
    print(f"✅ Prompt optimization: {len(original_prompt)} → {len(optimized)} chars")
    print(f"   Cost reduction: {(1 - len(optimized)/len(original_prompt))*100:.1f}%")

def test_time_based_routing():
    """Test time-based routing strategies"""
    # Simulate different times
    from unittest.mock import patch
    with patch('datetime.datetime') as mock_datetime:
        # Business hours - normal routing
        mock_datetime.now.return_value = datetime(2024, 1, 1, 14, 0)  # 2 PM
        router = CostAwareRouter(strategy=RoutingStrategy.TIME_BASED)
        
        day_model = router.select_model("Business analysis")
        
        # Night hours - use cheaper models
        mock_datetime.now.return_value = datetime(2024, 1, 1, 3, 0)  # 3 AM
        night_model = router.select_model("Business analysis")
        
        # Night model should be cheaper
        day_cost = router.calculate_cost(day_model, 1000)
        night_cost = router.calculate_cost(night_model, 1000)
        
        assert night_cost <= day_cost
        print(f"✅ Time-based routing: day=${day_cost:.3f}, night=${night_cost:.3f}")

def test_caching_impact():
    """Test how caching affects routing decisions"""
    router = CostAwareRouter(enable_cache=True)
    
    prompt = "What is the capital of France?"
    
    # First call - routes to appropriate model
    model1 = router.select_model(prompt)
    response1 = router.execute(prompt)
    cost1 = response1.cost
    
    # Second call - should hit cache
    model2 = router.select_model(prompt)
    response2 = router.execute(prompt)
    cost2 = response2.cost
    
    assert cost2 == 0, "Cached response should be free"
    assert response1.text == response2.text
    print("✅ Cache-aware routing working")

if __name__ == "__main__":
    print("🔍 Validating cost-aware router...\n")
    
    test_cost_calculation()
    test_complexity_analysis() 
    test_routing_strategies()
    test_budget_management()
    test_routing_performance()
    test_prompt_optimization()
    
    # Mock required for time test
    from unittest.mock import patch
    test_time_based_routing()
    
    test_caching_impact()
    
    print("\n✅ Cost router validation complete!")