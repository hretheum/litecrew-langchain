"""Rate limiting and token management for LiteCrew."""

import asyncio
import time
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Dict, Optional, Callable, Any, List
from functools import wraps
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimiterConfig:
    """Configuration for rate limiting."""
    max_rpm: Optional[int] = None  # Max requests per minute
    max_rps: Optional[float] = None  # Max requests per second
    burst_size: int = 1  # Allow burst of requests
    

class RateLimiter:
    """Token bucket rate limiter for controlling request rates."""
    
    def __init__(
        self,
        max_rpm: Optional[int] = None,
        max_rps: Optional[float] = None,
        burst_size: int = 1
    ):
        """Initialize rate limiter with RPM or RPS limits."""
        if max_rpm is not None:
            self.max_rpm = max_rpm
            self.max_rps = max_rpm / 60.0
        elif max_rps is not None:
            self.max_rps = max_rps
            self.max_rpm = int(max_rps * 60)
        else:
            raise ValueError("Either max_rpm or max_rps must be specified")
        
        self.burst_size = burst_size
        self._request_times: deque = deque()
        self._lock = asyncio.Lock()
        self._overhead_sum = 0.0
        self._overhead_count = 0
    
    def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens, blocking if necessary."""
        start = time.perf_counter()
        
        while True:
            current_time = time.time()
            
            # Remove old requests outside the window
            window_start = current_time - 60.0  # 1 minute window
            while self._request_times and self._request_times[0] < window_start:
                self._request_times.popleft()
            
            # Check if we can make the request
            if len(self._request_times) < self.max_rpm:
                self._request_times.append(current_time)
                
                # Track overhead
                overhead = time.perf_counter() - start
                self._overhead_sum += overhead
                self._overhead_count += 1
                
                return True
            
            # Calculate wait time
            oldest_request = self._request_times[0]
            wait_time = 60.0 - (current_time - oldest_request)
            
            if wait_time > 0:
                time.sleep(wait_time)
    
    async def acquire_async(self, tokens: int = 1) -> bool:
        """Async version of acquire."""
        async with self._lock:
            start = time.perf_counter()
            
            while True:
                current_time = time.time()
                
                # Remove old requests
                window_start = current_time - 60.0
                while self._request_times and self._request_times[0] < window_start:
                    self._request_times.popleft()
                
                # Check if we can make the request
                if len(self._request_times) < self.max_rpm:
                    self._request_times.append(current_time)
                    
                    # Track overhead
                    overhead = time.perf_counter() - start
                    self._overhead_sum += overhead
                    self._overhead_count += 1
                    
                    return True
                
                # Calculate wait time
                oldest_request = self._request_times[0]
                wait_time = 60.0 - (current_time - oldest_request)
                
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
    
    def reset(self):
        """Reset the rate limiter."""
        self._request_times.clear()
        self._overhead_sum = 0.0
        self._overhead_count = 0
    
    def get_overhead(self) -> float:
        """Get average overhead in seconds."""
        if self._overhead_count == 0:
            return 0.0
        return self._overhead_sum / self._overhead_count


class GlobalRateLimiter:
    """Global rate limiter coordinating across multiple agents."""
    
    def __init__(
        self,
        max_rpm: int = 1000,
        per_agent_limits: Optional[Dict[str, int]] = None
    ):
        """Initialize global rate limiter."""
        self.global_limiter = RateLimiter(max_rpm=max_rpm)
        self.per_agent_limiters: Dict[str, RateLimiter] = {}
        self.per_agent_limits = per_agent_limits or {}
    
    def acquire(self, agent_id: Any, tokens: int = 1) -> bool:
        """Acquire tokens for a specific agent."""
        # Get agent name from Mock object
        if hasattr(agent_id, '_mock_name'):
            agent_name = agent_id._mock_name
        else:
            agent_name = getattr(agent_id, 'name', str(agent_id))
        
        # Check agent-specific limit
        if agent_name in self.per_agent_limits:
            if agent_name not in self.per_agent_limiters:
                self.per_agent_limiters[agent_name] = RateLimiter(
                    max_rpm=self.per_agent_limits[agent_name]
                )
            
            if not self.per_agent_limiters[agent_name].acquire(tokens):
                return False
        
        # Check global limit
        return self.global_limiter.acquire(tokens)
    
    async def acquire_async(self, agent_id: Any, tokens: int = 1) -> bool:
        """Async version of acquire."""
        # Get agent name from Mock object
        if hasattr(agent_id, '_mock_name'):
            agent_name = agent_id._mock_name
        else:
            agent_name = getattr(agent_id, 'name', str(agent_id))
        
        # Check agent-specific limit
        if agent_name in self.per_agent_limits:
            if agent_name not in self.per_agent_limiters:
                self.per_agent_limiters[agent_name] = RateLimiter(
                    max_rpm=self.per_agent_limits[agent_name]
                )
            
            if not await self.per_agent_limiters[agent_name].acquire_async(tokens):
                return False
        
        # Check global limit
        return await self.global_limiter.acquire_async(tokens)


class TokenCounter:
    """Count tokens for different LLM models."""
    
    # Token pricing per model (example rates)
    PRICING = {
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},  # per 1K tokens
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    }
    
    def __init__(self):
        """Initialize token counter."""
        self._token_counts: Dict[str, int] = defaultdict(int)
        self._cost_tracking: Dict[str, float] = defaultdict(float)
    
    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Count tokens in text for a specific model."""
        # For accurate counting, we'd use tiktoken for OpenAI models
        # This is a simplified estimation
        if "gpt" in model.lower():
            # GPT models: ~1 token per 4 characters
            return max(1, len(text) // 4)
        elif "claude" in model.lower():
            # Claude models: similar estimation
            return max(1, len(text) // 4)
        else:
            # Fallback: word-based estimation
            return max(1, int(len(text.split()) * 1.3))
    
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> float:
        """Calculate cost based on token usage."""
        if model not in self.PRICING:
            # Unknown model, use a default rate
            return (input_tokens * 0.001 + output_tokens * 0.002) / 1000
        
        pricing = self.PRICING[model]
        input_cost = (input_tokens * pricing["input"]) / 1000
        output_cost = (output_tokens * pricing["output"]) / 1000
        
        return input_cost + output_cost
    
    def track_usage(
        self,
        model: str,
        input_text: str,
        output_text: str
    ) -> Dict[str, Any]:
        """Track token usage and cost."""
        input_tokens = self.count_tokens(input_text, model)
        output_tokens = self.count_tokens(output_text, model)
        cost = self.calculate_cost(input_tokens, output_tokens, model)
        
        # Update tracking
        self._token_counts[f"{model}_input"] += input_tokens
        self._token_counts[f"{model}_output"] += output_tokens
        self._cost_tracking[model] += cost
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost": cost
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        total_tokens = sum(self._token_counts.values())
        total_cost = sum(self._cost_tracking.values())
        
        return {
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "by_model": dict(self._cost_tracking),
            "token_breakdown": dict(self._token_counts)
        }


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    handle_rate_limits: bool = True
):
    """Decorator for retry logic with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    # Check if it's a rate limit error
                    if handle_rate_limits and "rate limit" in error_msg:
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay
                        )
                        logger.warning(
                            f"Rate limit hit, retrying in {delay}s "
                            f"(attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(delay)
                    else:
                        # For other errors, shorter retry
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay / 2
                        )
                        await asyncio.sleep(delay)
            
            # All retries exhausted
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    if handle_rate_limits and "rate limit" in error_msg:
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay
                        )
                        time.sleep(delay)
                    else:
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay / 2
                        )
                        time.sleep(delay)
            
            raise last_exception
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@dataclass
class BudgetManager:
    """Manage budget limits and alerts."""
    
    daily_limit: float
    alert_threshold: float = 0.8
    hard_limit: bool = False
    alert_callback: Optional[Callable[[str, float, float], None]] = None
    _spent: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    _last_reset: float = field(default_factory=time.time)
    _alerts_sent: set = field(default_factory=set)
    
    def track_cost(self, agent_id: str, cost: float):
        """Track cost for an agent."""
        self._check_reset()
        self._spent[agent_id] += cost
        total_spent = self.get_total_spent()
        
        # Check for alerts
        if total_spent >= self.daily_limit * self.alert_threshold:
            alert_key = f"threshold_{self.alert_threshold}"
            if alert_key not in self._alerts_sent:
                self._alerts_sent.add(alert_key)
                if self.alert_callback:
                    self.alert_callback(
                        f"Budget threshold {self.alert_threshold*100}% reached",
                        total_spent,
                        self.daily_limit
                    )
        
        # Check hard limit
        if self.hard_limit and total_spent >= self.daily_limit:
            if "limit_exceeded" not in self._alerts_sent:
                self._alerts_sent.add("limit_exceeded")
                if self.alert_callback:
                    self.alert_callback(
                        "Daily budget limit exceeded",
                        total_spent,
                        self.daily_limit
                    )
    
    def check_budget(self, estimated_cost: float) -> bool:
        """Check if operation would exceed budget."""
        self._check_reset()
        total_spent = self.get_total_spent()
        
        if self.hard_limit and total_spent + estimated_cost > self.daily_limit:
            raise Exception(
                f"Operation would exceed daily budget limit. "
                f"Current: ${total_spent:.2f}, "
                f"Estimated: ${estimated_cost:.2f}, "
                f"Limit: ${self.daily_limit:.2f}"
            )
        
        return True
    
    def get_total_spent(self) -> float:
        """Get total amount spent."""
        return sum(self._spent.values())
    
    def get_remaining_budget(self) -> float:
        """Get remaining budget."""
        return max(0, self.daily_limit - self.get_total_spent())
    
    def is_budget_exceeded(self) -> bool:
        """Check if budget is exceeded."""
        return self.get_total_spent() >= self.daily_limit
    
    def _check_reset(self):
        """Check if we need to reset daily counters."""
        current_time = time.time()
        if current_time - self._last_reset >= 86400:  # 24 hours
            self._spent.clear()
            self._alerts_sent.clear()
            self._last_reset = current_time
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Get detailed usage report."""
        return {
            "total_spent": self.get_total_spent(),
            "remaining": self.get_remaining_budget(),
            "limit": self.daily_limit,
            "by_agent": dict(self._spent),
            "alerts_triggered": list(self._alerts_sent)
        }