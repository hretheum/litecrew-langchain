# validate_quality_selector.py
import numpy as np
from dataclasses import dataclass
from litecrewai.routing.quality import (
    QualityBasedSelector, TaskRequirements,
    ModelCapabilities, QualityMetrics
)

def test_capability_matrix():
    """Test model capability scoring"""
    selector = QualityBasedSelector()
    
    # Check all models have capabilities defined
    models = selector.get_all_models()
    assert len(models) > 0
    
    for model in models:
        caps = model.capabilities
        assert isinstance(caps.accuracy, float)
        assert 0 <= caps.accuracy <= 1
        assert isinstance(caps.creativity, float)
        assert isinstance(caps.reasoning, float)
        assert isinstance(caps.language_quality, float)
        assert isinstance(caps.instruction_following, float)
        
        print(f"✅ {model.name}: accuracy={caps.accuracy:.2f}, "
              f"reasoning={caps.reasoning:.2f}")

def test_task_matching():
    """Test task requirement matching"""
    selector = QualityBasedSelector()
    
    # High accuracy requirement
    req1 = TaskRequirements(
        min_accuracy=0.95,
        domain="medical"
    )
    model1 = selector.select_best_model(
        "Diagnose symptoms", req1
    )
    assert model1.capabilities.accuracy >= 0.95
    assert "gpt-4" in model1.name or "claude" in model1.name
    print(f"✅ High accuracy task → {model1.name}")
    
    # Creative task
    req2 = TaskRequirements(
        min_creativity=0.8,
        domain="creative_writing"
    )
    model2 = selector.select_best_model(
        "Write a poem", req2
    )
    assert model2.capabilities.creativity >= 0.8
    print(f"✅ Creative task → {model2.name}")
    
    # Reasoning task
    req3 = TaskRequirements(
        min_reasoning=0.85,
        domain="mathematics"
    )
    model3 = selector.select_best_model(
        "Solve complex equation", req3
    )
    assert model3.capabilities.reasoning >= 0.85
    print(f"✅ Reasoning task → {model3.name}")

def test_constraint_satisfaction():
    """Test multiple constraint handling"""
    selector = QualityBasedSelector()
    
    # Multiple constraints
    requirements = TaskRequirements(
        min_accuracy=0.8,
        min_creativity=0.7,
        min_reasoning=0.8,
        max_cost_per_1k_tokens=0.01,  # Budget constraint
        needs_citations=True,
        output_format="json",
        max_latency_ms=2000
    )
    
    model = selector.select_best_model(
        "Research and summarize with citations",
        requirements
    )
    
    # Check all constraints met
    assert model.capabilities.accuracy >= 0.8
    assert model.capabilities.creativity >= 0.7
    assert model.capabilities.reasoning >= 0.8
    assert model.cost_per_1k_tokens <= 0.01
    assert model.supports_citations
    assert "json" in model.supported_formats
    
    print(f"✅ Multi-constraint satisfied by: {model.name}")

def test_quality_validation():
    """Test output quality validation"""
    selector = QualityBasedSelector()
    
    # Mock response
    @dataclass
    class MockResponse:
        text: str
        model: str
        
    # Good response
    good_response = MockResponse(
        text="The capital of France is Paris. This is a well-known fact.",
        model="gpt-3.5-turbo"
    )
    
    score = selector.validate_quality(
        good_response,
        task="What is the capital of France?",
        requirements=TaskRequirements(min_accuracy=0.8)
    )
    
    assert score.accuracy >= 0.8
    assert score.completeness >= 0.8
    print(f"✅ Good response score: {score.overall:.2f}")
    
    # Poor response
    poor_response = MockResponse(
        text="I don't know.",
        model="gpt-3.5-turbo"
    )
    
    score = selector.validate_quality(
        poor_response,
        task="What is the capital of France?",
        requirements=TaskRequirements(min_accuracy=0.8)
    )
    
    assert score.accuracy < 0.5
    assert score.completeness < 0.5
    print(f"✅ Poor response score: {score.overall:.2f}")

def test_learning_system():
    """Test quality learning from feedback"""
    selector = QualityBasedSelector()
    
    # Initial selection
    model1 = selector.select_best_model(
        "Technical documentation task",
        TaskRequirements(min_accuracy=0.85)
    )
    initial_score = model1.expected_quality
    
    # Simulate feedback
    feedback_data = [
        (model1.name, "Technical documentation task", 0.7),  # Lower than expected
        (model1.name, "Technical documentation task", 0.72),
        (model1.name, "Technical documentation task", 0.71),
    ]
    
    for model, task, actual_quality in feedback_data:
        selector.record_feedback(model, task, actual_quality)
    
    # Select again - should adapt
    model2 = selector.select_best_model(
        "Technical documentation task",
        TaskRequirements(min_accuracy=0.85)
    )
    
    # Should select different model or adjust expectations
    if model2.name == model1.name:
        assert model2.expected_quality < initial_score
        print(f"✅ Adjusted expectations: {initial_score:.2f} → {model2.expected_quality:.2f}")
    else:
        print(f"✅ Switched models: {model1.name} → {model2.name}")

def test_domain_expertise():
    """Test domain-specific model selection"""
    selector = QualityBasedSelector()
    
    domains = [
        ("medical", "Explain MRI results"),
        ("legal", "Draft a contract clause"),
        ("coding", "Write a Python function"),
        ("creative", "Write a haiku"),
        ("scientific", "Explain quantum entanglement")
    ]
    
    selected_models = {}
    
    for domain, task in domains:
        req = TaskRequirements(domain=domain)
        model = selector.select_best_model(task, req)
        selected_models[domain] = model.name
        
        # Check domain expertise
        domain_score = model.capabilities.domain_expertise.get(domain, 0)
        assert domain_score > 0.7, f"Low expertise for {domain}"
        
        print(f"✅ {domain}: {model.name} (expertise: {domain_score:.2f})")
    
    # Different domains should potentially use different models
    unique_models = len(set(selected_models.values()))
    assert unique_models > 1, "Should use varied models for different domains"

def test_performance_monitoring():
    """Test model performance tracking"""
    selector = QualityBasedSelector()
    
    # Simulate performance data
    model_name = "gpt-3.5-turbo"
    
    # Record successful uses
    for _ in range(10):
        selector.record_performance(
            model_name,
            task_type="general",
            latency_ms=800,
            quality_score=0.85,
            success=True
        )
    
    # Record some failures
    for _ in range(2):
        selector.record_performance(
            model_name,
            task_type="general", 
            latency_ms=5000,
            quality_score=0.4,
            success=False
        )
    
    # Get performance stats
    stats = selector.get_model_performance(model_name)
    
    assert stats["success_rate"] == 10/12
    assert stats["avg_quality"] > 0.7
    assert stats["avg_latency_ms"] < 2000
    assert stats["total_uses"] == 12
    
    print(f"✅ Performance tracking:")
    print(f"   - Success rate: {stats['success_rate']:.1%}")
    print(f"   - Avg quality: {stats['avg_quality']:.2f}")
    print(f"   - Avg latency: {stats['avg_latency_ms']:.0f}ms")

def test_escalation_strategy():
    """Test automatic escalation to better models"""
    selector = QualityBasedSelector()
    
    # Start with minimum requirements
    req = TaskRequirements(
        min_accuracy=0.9,
        escalation_enabled=True
    )
    
    # Mock poor quality response
    @dataclass
    class MockResponse:
        text: str
        model: str
    
    poor_response = MockResponse(
        text="Incomplete answer...",
        model="gpt-3.5-turbo"
    )
    
    # Validate and escalate
    escalated = selector.escalate_if_needed(
        poor_response,
        task="Complex medical diagnosis",
        requirements=req,
        measured_quality=0.6  # Below requirement
    )
    
    assert escalated.model != poor_response.model
    assert "gpt-4" in escalated.model or "claude" in escalated.model
    print(f"✅ Escalated from {poor_response.model} → {escalated.model}")

if __name__ == "__main__":
    print("🔍 Validating quality-based selector...\n")
    
    test_capability_matrix()
    test_task_matching()
    test_constraint_satisfaction()
    test_quality_validation()
    test_learning_system()
    test_domain_expertise()
    test_performance_monitoring()
    test_escalation_strategy()
    
    print("\n✅ Quality selector validation complete!")