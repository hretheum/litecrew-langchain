# metrics/collectors.py
from prometheus_client import Counter, Gauge, Histogram, Info
from prometheus_client.core import CollectorRegistry
from typing import Dict, Any
import psutil
import asyncio

# Registry
registry = CollectorRegistry()

# Agent metrics
agent_count = Gauge(
    'litecrewai_agents_total',
    'Total number of agents by status',
    ['status'],
    registry=registry
)

agent_memory = Gauge(
    'litecrewai_agent_memory_bytes',
    'Memory usage per agent',
    ['agent_id'],
    registry=registry
)

# Task metrics
task_total = Counter(
    'litecrewai_tasks_total',
    'Total number of tasks',
    ['status', 'agent_id'],
    registry=registry
)

task_duration = Histogram(
    'litecrewai_task_duration_seconds',
    'Task execution duration',
    ['agent_id', 'task_type'],
    registry=registry
)

# LLM metrics
llm_requests = Counter(
    'litecrewai_llm_requests_total',
    'Total LLM API requests',
    ['provider', 'model', 'status'],
    registry=registry
)

llm_tokens = Counter(
    'litecrewai_llm_tokens_total',
    'Total tokens used',
    ['provider', 'model', 'type'],  # type: prompt/completion
    registry=registry
)

llm_cost = Counter(
    'litecrewai_llm_cost_dollars',
    'Total LLM API cost',
    ['provider', 'model'],
    registry=registry
)

llm_latency = Histogram(
    'litecrewai_llm_latency_seconds',
    'LLM API latency',
    ['provider', 'model'],
    registry=registry
)

# Tool metrics
tool_executions = Counter(
    'litecrewai_tool_executions_total',
    'Total tool executions',
    ['tool_name', 'status'],
    registry=registry
)

tool_duration = Histogram(
    'litecrewai_tool_duration_seconds',
    'Tool execution duration',
    ['tool_name'],
    registry=registry
)

# System metrics
system_info = Info(
    'litecrewai_system',
    'System information',
    registry=registry
)

class MetricsCollector:
    """Collects and updates metrics"""
    
    def __init__(self):
        self.agent_pids: Dict[str, int] = {}
        self._collection_task = None
    
    async def start(self):
        """Start background metrics collection"""
        self._collection_task = asyncio.create_task(
            self._collect_system_metrics()
        )
        
        # Set system info
        system_info.info({
            'version': '0.1.0',
            'python_version': '3.11',
            'platform': 'linux'
        })
    
    async def stop(self):
        """Stop metrics collection"""
        if self._collection_task:
            self._collection_task.cancel()
    
    async def _collect_system_metrics(self):
        """Collect system metrics every 30s"""
        while True:
            try:
                # Update agent memory
                for agent_id, pid in self.agent_pids.items():
                    try:
                        process = psutil.Process(pid)
                        memory = process.memory_info().rss
                        agent_memory.labels(agent_id=agent_id).set(memory)
                    except psutil.NoSuchProcess:
                        # Agent terminated
                        agent_memory.remove(agent_id)
                        del self.agent_pids[agent_id]
                
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error collecting metrics: {e}")
    
    def record_agent_created(self, agent_id: str, pid: int = None):
        """Record agent creation"""
        agent_count.labels(status='active').inc()
        if pid:
            self.agent_pids[agent_id] = pid
    
    def record_agent_terminated(self, agent_id: str):
        """Record agent termination"""
        agent_count.labels(status='active').dec()
        agent_count.labels(status='terminated').inc()
        
        if agent_id in self.agent_pids:
            agent_memory.remove(agent_id)
            del self.agent_pids[agent_id]
    
    def record_task(self, agent_id: str, task_type: str, 
                   duration: float, status: str):
        """Record task execution"""
        task_total.labels(
            status=status,
            agent_id=agent_id
        ).inc()
        
        if status == 'completed':
            task_duration.labels(
                agent_id=agent_id,
                task_type=task_type
            ).observe(duration)
    
    def record_llm_call(self, provider: str, model: str,
                       prompt_tokens: int, completion_tokens: int,
                       latency: float, cost: float, 
                       status: str = 'success'):
        """Record LLM API call"""
        llm_requests.labels(
            provider=provider,
            model=model,
            status=status
        ).inc()
        
        if status == 'success':
            llm_tokens.labels(
                provider=provider,
                model=model,
                type='prompt'
            ).inc(prompt_tokens)
            
            llm_tokens.labels(
                provider=provider,
                model=model,
                type='completion'
            ).inc(completion_tokens)
            
            llm_cost.labels(
                provider=provider,
                model=model
            ).inc(cost)
            
            llm_latency.labels(
                provider=provider,
                model=model
            ).observe(latency)
    
    def record_tool_execution(self, tool_name: str, 
                            duration: float, status: str):
        """Record tool execution"""
        tool_executions.labels(
            tool_name=tool_name,
            status=status
        ).inc()
        
        if status == 'success':
            tool_duration.labels(
                tool_name=tool_name
            ).observe(duration)

# Global collector instance
metrics_collector = MetricsCollector()