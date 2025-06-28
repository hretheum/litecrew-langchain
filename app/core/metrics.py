"""
LiteCrewAI Metrics Collection
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_client import generate_latest
from typing import Dict
import psutil
import time

# Application info
app_info = Info("litecrewai_info", "Application information")
app_info.info({"version": "0.1.0", "environment": "production"})

# Request metrics
request_count = Counter(
    "litecrewai_requests_total", "Total requests", ["method", "endpoint", "status"]
)

request_duration = Histogram(
    "litecrewai_request_duration_seconds", "Request duration", ["method", "endpoint"]
)

# Agent metrics
active_agents = Gauge("litecrewai_active_agents", "Number of active agents")

agent_tasks_total = Counter(
    "litecrewai_agent_tasks_total",
    "Total tasks executed by agents",
    ["agent_name", "status"],
)

agent_task_duration = Histogram(
    "litecrewai_agent_task_duration_seconds",
    "Agent task execution time",
    ["agent_name", "task_type"],
)

# LLM metrics
llm_requests = Counter(
    "litecrewai_llm_requests_total",
    "Total LLM API requests",
    ["provider", "model", "status"],
)

llm_tokens = Counter(
    "litecrewai_llm_tokens_total",
    "Total tokens used",
    ["provider", "model", "type"],  # type: prompt/completion
)

llm_latency = Histogram(
    "litecrewai_llm_latency_seconds", "LLM API latency", ["provider", "model"]
)

# System metrics
cpu_usage = Gauge("litecrewai_cpu_usage_percent", "CPU usage percentage")
memory_usage = Gauge("litecrewai_memory_usage_bytes", "Memory usage in bytes")
disk_usage = Gauge("litecrewai_disk_usage_percent", "Disk usage percentage")


class MetricsCollector:
    """Collect system and application metrics"""

    def __init__(self):
        self.start_time = time.time()

    def collect_system_metrics(self):
        """Collect system resource metrics"""
        # CPU
        cpu_usage.set(psutil.cpu_percent(interval=1))

        # Memory
        memory = psutil.virtual_memory()
        memory_usage.set(memory.used)

        # Disk
        disk = psutil.disk_usage("/")
        disk_usage.set(disk.percent)

    def track_request(self, method: str, endpoint: str, status: int, duration: float):
        """Track HTTP request metrics"""
        request_count.labels(method=method, endpoint=endpoint, status=str(status)).inc()
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def track_agent_task(
        self, agent_name: str, task_type: str, status: str, duration: float
    ):
        """Track agent task execution"""
        agent_tasks_total.labels(agent_name=agent_name, status=status).inc()
        agent_task_duration.labels(agent_name=agent_name, task_type=task_type).observe(
            duration
        )

    def track_llm_request(
        self,
        provider: str,
        model: str,
        status: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency: float,
    ):
        """Track LLM API usage"""
        llm_requests.labels(provider=provider, model=model, status=status).inc()
        llm_tokens.labels(provider=provider, model=model, type="prompt").inc(
            prompt_tokens
        )
        llm_tokens.labels(provider=provider, model=model, type="completion").inc(
            completion_tokens
        )
        llm_latency.labels(provider=provider, model=model).observe(latency)

    def get_metrics(self) -> bytes:
        """Generate Prometheus metrics"""
        self.collect_system_metrics()
        return generate_latest()


# Global metrics collector instance
metrics_collector = MetricsCollector()


# Cost tracking utilities
class CostTracker:
    """Track LLM API costs"""

    # Cost per 1K tokens (in USD)
    COSTS = {
        "openai": {
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-3.5-turbo": {"prompt": 0.001, "completion": 0.002},
        },
        "anthropic": {
            "claude-3-opus": {"prompt": 0.015, "completion": 0.075},
            "claude-3-sonnet": {"prompt": 0.003, "completion": 0.015},
        },
        "groq": {
            "llama-3-70b": {"prompt": 0.0007, "completion": 0.0008},
            "mixtral-8x7b": {"prompt": 0.0005, "completion": 0.0005},
        },
        "ollama": {
            "mistral:7b": {"prompt": 0, "completion": 0},
            "phi3:mini": {"prompt": 0, "completion": 0},
        },
    }

    def __init__(self):
        self.total_cost = 0.0
        self.cost_by_model: Dict[str, float] = {}

    def add_usage(
        self, provider: str, model: str, prompt_tokens: int, completion_tokens: int
    ):
        """Add token usage and calculate cost"""
        if provider not in self.COSTS or model not in self.COSTS[provider]:
            return

        costs = self.COSTS[provider][model]
        prompt_cost = (prompt_tokens / 1000) * costs["prompt"]
        completion_cost = (completion_tokens / 1000) * costs["completion"]
        total = prompt_cost + completion_cost

        self.total_cost += total
        model_key = f"{provider}/{model}"
        self.cost_by_model[model_key] = self.cost_by_model.get(model_key, 0) + total

    def get_daily_cost(self) -> float:
        """Estimate daily cost based on current usage"""
        uptime_hours = (time.time() - metrics_collector.start_time) / 3600
        if uptime_hours < 1:
            return 0
        return (self.total_cost / uptime_hours) * 24

    def get_monthly_estimate(self) -> float:
        """Estimate monthly cost"""
        return self.get_daily_cost() * 30


# Global cost tracker
cost_tracker = CostTracker()
