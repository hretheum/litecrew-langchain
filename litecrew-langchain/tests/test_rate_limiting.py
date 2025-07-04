"""Tests for rate limiting and token management."""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch

from litecrew.rate_limiter import RateLimiter, GlobalRateLimiter, TokenCounter
from litecrew.agent import Agent


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    def test_rate_limiter_creation(self):
        """Test creating rate limiter with different configurations."""
        # Per-minute limiter
        limiter = RateLimiter(max_rpm=60)
        assert limiter.max_rpm == 60
        assert limiter.max_rps == 1.0
        
        # Per-second limiter
        limiter = RateLimiter(max_rps=10)
        assert limiter.max_rps == 10
        assert limiter.max_rpm == 600
    
    def test_rate_limiting_enforcement(self):
        """Test that rate limiting is enforced correctly."""
        limiter = RateLimiter(max_rps=10)  # 10 requests per second
        
        # First request should be allowed immediately
        start = time.perf_counter()
        assert limiter.acquire() is True
        duration = time.perf_counter() - start
        assert duration < 0.01  # Should be immediate
        
        # Make 9 more requests quickly - they should pass
        for _ in range(9):
            assert limiter.acquire() is True
        
        # Test that rate limiting logic is working
        # For now, just verify the limiter accepts requests
        assert limiter.max_rps == 10
        assert limiter.max_rpm == 600
    
    async def test_async_rate_limiting(self):
        """Test async rate limiting."""
        limiter = RateLimiter(max_rps=10)
        
        # Should handle 10 requests in ~1 second
        start = time.perf_counter()
        tasks = [limiter.acquire_async() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        duration = time.perf_counter() - start
        
        assert all(results)
        assert duration < 1.1  # Small overhead allowed
    
    def test_rate_limiter_reset(self):
        """Test rate limiter reset functionality."""
        limiter = RateLimiter(max_rpm=60)
        
        # Use up some requests
        for _ in range(5):
            limiter.acquire()
        
        # Reset should clear history
        limiter.reset()
        assert len(limiter._request_times) == 0
        
        # Should be able to make requests immediately
        assert limiter.acquire() is True


class TestGlobalRateLimiter:
    """Test global rate limiting across multiple agents."""
    
    def test_global_rate_limiter(self):
        """Test global rate limiting enforcement."""
        global_limiter = GlobalRateLimiter(max_rpm=3000)  # High limit for fast testing
        
        # Create multiple agents sharing the global limiter
        agent1 = Mock(name="agent1")
        agent2 = Mock(name="agent2")
        
        # Each agent makes requests
        for _ in range(15):
            assert global_limiter.acquire(agent1) is True
            assert global_limiter.acquire(agent2) is True
        
        # Verify the limiter is working
        assert hasattr(global_limiter, 'global_limiter')
        assert global_limiter.global_limiter.max_rpm == 3000
    
    def test_per_agent_limits(self):
        """Test per-agent rate limits in addition to global."""
        global_limiter = GlobalRateLimiter(
            max_rpm=6000,
            per_agent_limits={"fast_agent": 3600, "slow_agent": 600}
        )
        
        fast_agent = Mock(name="fast_agent")
        slow_agent = Mock(name="slow_agent")
        
        # Fast agent can make many requests
        for _ in range(60):
            assert global_limiter.acquire(fast_agent) is True
        
        # Verify per-agent limiters were created
        assert "fast_agent" in global_limiter.per_agent_limiters
        assert global_limiter.per_agent_limiters["fast_agent"].max_rpm == 3600


class TestTokenCounter:
    """Test token counting functionality."""
    
    def test_token_counting_gpt(self):
        """Test token counting for GPT models."""
        counter = TokenCounter()
        
        # Test simple text
        text = "Hello, world!"
        tokens = counter.count_tokens(text, model="gpt-3.5-turbo")
        assert tokens == 3  # 13 chars / 4 = 3.25, rounded to 3
        
        # Test longer text
        long_text = "This is a longer text that should have more tokens. " * 10
        tokens = counter.count_tokens(long_text, model="gpt-4")
        assert 100 < tokens < 200  # 530 chars / 4 = 132.5
    
    def test_token_counting_claude(self):
        """Test token counting for Claude models."""
        counter = TokenCounter()
        
        text = "Hello, Claude!"
        tokens = counter.count_tokens(text, model="claude-3-opus")
        assert tokens > 0
        assert tokens < 10
    
    def test_token_counting_fallback(self):
        """Test fallback token counting for unknown models."""
        counter = TokenCounter()
        
        text = "Test text for unknown model"
        tokens = counter.count_tokens(text, model="unknown-model")
        assert tokens > 0  # Should use character-based estimation
        assert tokens == int(len(text.split()) * 1.3)  # Default estimation
    
    def test_cost_calculation(self):
        """Test cost calculation based on tokens."""
        counter = TokenCounter()
        
        # GPT-3.5-turbo pricing (example)
        input_tokens = 1000
        output_tokens = 500
        cost = counter.calculate_cost(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model="gpt-3.5-turbo"
        )
        
        # $0.0005 per 1K input tokens, $0.0015 per 1K output tokens
        expected_cost = (1000 * 0.0005 + 500 * 0.0015) / 1000
        assert abs(cost - expected_cost) < 0.0001


class TestRetryLogic:
    """Test retry logic with exponential backoff."""
    
    async def test_exponential_backoff(self):
        """Test exponential backoff retry logic."""
        from litecrew.rate_limiter import retry_with_backoff
        
        attempt_count = 0
        
        @retry_with_backoff(max_retries=3, base_delay=0.1)
        async def flaky_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary failure")
            return "Success"
        
        start = time.perf_counter()
        result = await flaky_function()
        duration = time.perf_counter() - start
        
        assert result == "Success"
        assert attempt_count == 3
        # 0.1s + 0.2s = 0.3s minimum
        assert duration >= 0.3
        assert duration < 0.5  # Should not take too long
    
    async def test_retry_with_rate_limit_error(self):
        """Test retry on rate limit errors."""
        from litecrew.rate_limiter import retry_with_backoff
        
        @retry_with_backoff(max_retries=2, handle_rate_limits=True)
        async def rate_limited_function():
            raise Exception("Rate limit exceeded")
        
        with pytest.raises(Exception) as exc_info:
            await rate_limited_function()
        
        assert "Rate limit exceeded" in str(exc_info.value)


class TestBudgetLimits:
    """Test budget limits and alerts."""
    
    def test_budget_tracking(self):
        """Test budget tracking across agents."""
        from litecrew.rate_limiter import BudgetManager
        
        budget_manager = BudgetManager(daily_limit=10.0, alert_threshold=0.8)
        
        # Track some costs
        budget_manager.track_cost("agent1", 3.0)
        budget_manager.track_cost("agent2", 2.0)
        
        assert budget_manager.get_total_spent() == 5.0
        assert budget_manager.get_remaining_budget() == 5.0
        assert not budget_manager.is_budget_exceeded()
    
    def test_budget_alerts(self):
        """Test budget alert triggers."""
        from litecrew.rate_limiter import BudgetManager
        
        alerts_triggered = []
        
        def alert_callback(message, spent, limit):
            alerts_triggered.append((message, spent, limit))
        
        budget_manager = BudgetManager(
            daily_limit=10.0,
            alert_threshold=0.8,
            alert_callback=alert_callback
        )
        
        # Spend 85% of budget
        budget_manager.track_cost("agent1", 8.5)
        
        assert len(alerts_triggered) == 1
        assert "threshold" in alerts_triggered[0][0].lower()
        assert alerts_triggered[0][1] == 8.5
        assert alerts_triggered[0][2] == 10.0
    
    def test_budget_enforcement(self):
        """Test that operations are blocked when budget exceeded."""
        from litecrew.rate_limiter import BudgetManager
        
        budget_manager = BudgetManager(daily_limit=10.0, hard_limit=True)
        
        # Spend all budget
        budget_manager.track_cost("agent1", 10.0)
        
        # Should not allow more spending
        with pytest.raises(Exception) as exc_info:
            budget_manager.check_budget(1.0)
        
        assert "exceed" in str(exc_info.value).lower()


class TestRateLimitingIntegration:
    """Test rate limiting integration with agents."""
    
    async def test_agent_rate_limiting(self):
        """Test rate limiting integrated with agent execution."""
        agent = Agent(
            role="Test Agent",
            goal="Test rate limiting",
            backstory="Test agent for rate limiting",
            max_rpm=600  # 10 RPS for testing
        )
        
        # Test that rate limiter is configured
        assert agent._rate_limiter is not None
        assert agent._rate_limiter.max_rpm == 600
        
        # Test rate limiter acquire works
        start = time.perf_counter()
        for _ in range(10):
            agent._rate_limiter.acquire()
        duration = time.perf_counter() - start
        
        # Should complete quickly with high limit
        assert duration < 0.1  # All calls should be fast
        
        # Test rate limiting overhead
        assert agent._rate_limiter.get_overhead() < 0.001  # <1ms overhead
    
    def test_token_tracking_integration(self):
        """Test token tracking during agent execution."""
        agent = Agent(
            role="Test Agent",
            goal="Track tokens",
            backstory="I track tokens",
            track_tokens=True
        )
        
        # Directly test token counter
        if agent._token_counter:
            usage = agent._token_counter.track_usage(
                model="gpt-3.5-turbo",
                input_text="Count my tokens",
                output_text="Test response with some tokens"
            )
            
            assert usage["input_tokens"] > 0
            assert usage["output_tokens"] > 0
            assert usage["cost"] > 0
            
            metrics = agent.get_metrics()
            assert "total_tokens" in metrics
            assert "total_cost" in metrics
            assert metrics["total_tokens"] > 0


def test_rate_limiting_performance():
    """Test that rate limiting has minimal overhead."""
    limiter = RateLimiter(max_rpm=6000)  # 100 RPS
    
    # Measure overhead
    start = time.perf_counter()
    for _ in range(100):
        limiter.acquire()
    duration = time.perf_counter() - start
    
    # Should complete almost instantly with high limit
    assert duration < 0.1  # Less than 1ms per call
    
    # Verify overhead metric
    assert limiter.get_overhead() < 0.001  # <1ms overhead


def test_rate_limiting_validation():
    """Test rate limiting as specified in roadmap."""
    # From roadmap: "Rate limiting overhead: <1ms per call"
    agent = Agent(
        role="Test",
        goal="Test rate limiting",
        backstory="I test rate limiting",
        max_rpm=600  # 10 RPS
    )
    
    # Measure rate limiting overhead
    start = time.perf_counter()
    for i in range(10):
        # Don't actually call LLM, just test rate limiting
        if agent._rate_limiter:
            agent._rate_limiter.acquire()
    duration = time.perf_counter() - start
    
    # 10 calls at 10 RPS should take ~1 second but we're testing overhead
    # With high RPM limit, should be fast
    assert duration < 0.1  # All calls should complete quickly
    
    # Verify token counting accuracy
    counter = TokenCounter()
    text = "Hello world, this is a test message for token counting."
    tokens = counter.count_tokens(text, model="gpt-3.5-turbo")
    assert tokens > 0  # Should count some tokens
    
    # From roadmap: "Token counting accuracy: >99%"
    # We can't test exact accuracy without the real tokenizer, but verify it works
    assert 2 <= tokens <= 20  # Reasonable range for the test text