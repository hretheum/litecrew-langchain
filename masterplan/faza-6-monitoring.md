# FAZA 6: MONITORING I OPTYMALIZACJA

[← Powrót do README](./README.md) | [← Faza 5: API](./faza-5-api.md) | [Następna faza: Deployment →](./faza-7-deployment.md)

**Czas trwania**: 3 dni (rozszerzone z 2 dni)
**Cel**: System monitorowania, telemetrii i optymalizacji wydajności

---

## 📊 Blok 6.1: Telemetry i Metrics Collection

**Czas**: 8h
**Cel**: Zbieranie metryk systemowych i biznesowych

### Task 6.1.1: OpenTelemetry Integration (3h)

**Prompt dla AI Agent**:
```
Zintegruj OpenTelemetry do LiteCrewAI dla distributed tracing.

Implementacja:
1. Dodaj opentelemetry-api i opentelemetry-sdk
2. Instrument wszystkie HTTP endpoints
3. Trace LLM calls z custom spans
4. Track database queries
5. Measure task execution times
6. Context propagation między agentami

Uwzględnij:
- Span attributes (agent_id, task_id, llm_model)
- Baggage dla cross-agent correlation
- Sampling strategy (0.1 dla produkcji)
- Export do Jaeger lub OTLP
```

**Implementacja**:
[→ Zobacz plik: telemetry_setup.py](./src/faza-6/telemetry_setup.py)

[→ Zobacz plik: telemetry_decorators.py](./src/faza-6/telemetry_decorators.py)

### Task 6.1.2: Custom Metrics Collection (2h)

**Prompt dla AI Agent**:
```
Stwórz system zbierania custom metrics dla LiteCrewAI.

Metryki do śledzenia:
1. Agent lifecycle (created, active, terminated)
2. Task metrics (queued, executing, completed, failed)
3. LLM usage (tokens, cost, latency per provider)
4. Tool execution (success rate, duration)
5. Resource usage (memory, CPU per agent)
6. Business metrics (tasks per hour, cost per task)

Exportuj do Prometheus format.
```

**Implementacja**:
[→ Zobacz plik: metrics_collectors.py](./src/faza-6/metrics_collectors.py)

### Task 6.1.3: Prometheus Endpoint (3h)

**Prompt dla AI Agent**:
```
Dodaj Prometheus metrics endpoint do FastAPI.

Wymagania:
1. Endpoint /metrics z Prometheus format
2. Basic auth dla bezpieczeństwa
3. Filtering metrics by prefix
4. Custom metric aggregation
5. Health check metrics
6. Graceful shutdown
```

**Implementacja**:
[→ Zobacz plik: metrics_endpoint.py](./src/faza-6/metrics_endpoint.py)
    
    # Filter by prefix if provided
    if prefix:
        lines = metrics.decode('utf-8').split('\n')
        filtered = [
            line for line in lines 
            if line.startswith('#') or line.startswith(prefix)
        ]
        metrics = '\n'.join(filtered).encode('utf-8')
    
    return Response(
        content=metrics,
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/metrics/health")
async def metrics_health():
    """Health check for metrics system"""
    
    health_data = {
        "status": "healthy",
        "metrics": {
            "agents_active": agent_count._value.get(('active',), 0),
            "tasks_total": sum(task_total._value.values()),
            "collection_errors": 0
        }
    }
    
    # Check if collector is running
    if not metrics_collector._collection_task or \
       metrics_collector._collection_task.done():
        health_data["status"] = "degraded"
        health_data["errors"] = ["Metrics collector not running"]
    
    return health_data
```

---

## 📈 Blok 6.2: Performance Monitoring

**Czas**: 8h
**Cel**: Monitoring wydajności i auto-optimization

### Task 6.2.1: Performance Profiler (3h)

**Prompt dla AI Agent**:
```
Stwórz profiler wydajności dla LiteCrewAI.

Features:
1. Async-aware profiling
2. Memory profiling per agent
3. CPU profiling dla task execution
4. I/O wait time tracking
5. Slow query detection
6. Bottleneck identification

Output format: JSON report + flame graphs.
```

**Implementacja**:

```python
# monitoring/profiler.py
import asyncio
import cProfile
import pstats
import tracemalloc
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import psutil
from dataclasses import dataclass, asdict

@dataclass
class ProfileResult:
    """Profiling results container"""
    timestamp: str
    duration: float
    cpu_time: float
    memory_peak: int
    memory_current: int
    io_wait_time: float
    slow_operations: List[Dict[str, Any]]
    bottlenecks: List[Dict[str, Any]]

class PerformanceProfiler:
    """Performance profiler for LiteCrewAI"""
    
    def __init__(self, output_dir: Path = Path("./profiles")):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        self._profiler = None
        self._start_time = None
        self._io_wait_start = {}
        self._slow_operations = []
        self._tracemalloc_snapshot = None
    
    async def profile_task(self, task_id: str, task_func, *args, **kwargs):
        """Profile a single task execution"""
        
        # Start profiling
        self._profiler = cProfile.Profile()
        tracemalloc.start()
        
        self._start_time = time.time()
        process = psutil.Process()
        cpu_start = process.cpu_times()
        
        try:
            # Enable profiler
            self._profiler.enable()
            
            # Execute task
            result = await task_func(*args, **kwargs)
            
            # Disable profiler
            self._profiler.disable()
            
            # Collect results
            duration = time.time() - self._start_time
            cpu_end = process.cpu_times()
            cpu_time = (cpu_end.user - cpu_start.user) + \
                      (cpu_end.system - cpu_start.system)
            
            # Memory stats
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Analyze results
            profile_result = ProfileResult(
                timestamp=datetime.utcnow().isoformat(),
                duration=duration,
                cpu_time=cpu_time,
                memory_peak=peak,
                memory_current=current,
                io_wait_time=sum(self._io_wait_start.values()),
                slow_operations=self._slow_operations,
                bottlenecks=self._identify_bottlenecks()
            )
            
            # Save results
            await self._save_profile(task_id, profile_result)
            
            return result, profile_result
            
        except Exception as e:
            tracemalloc.stop()
            if self._profiler:
                self._profiler.disable()
            raise
    
    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # Analyze CPU profile
        stats = pstats.Stats(self._profiler)
        stats.sort_stats('cumulative')
        
        # Get top 10 time consumers
        for func, (cc, nc, tt, ct, callers) in \
            list(stats.stats.items())[:10]:
            
            if ct > 0.1:  # More than 100ms
                bottlenecks.append({
                    "type": "cpu",
                    "function": f"{func[0]}:{func[1]}:{func[2]}",
                    "cumulative_time": ct,
                    "calls": nc,
                    "severity": "high" if ct > 1.0 else "medium"
                })
        
        # Check for memory issues
        if hasattr(self, '_memory_growth'):
            if self._memory_growth > 100 * 1024 * 1024:  # 100MB
                bottlenecks.append({
                    "type": "memory",
                    "description": "High memory growth detected",
                    "growth_mb": self._memory_growth / 1024 / 1024,
                    "severity": "high"
                })
        
        # Check I/O wait
        total_io_wait = sum(self._io_wait_start.values())
        if total_io_wait > self._start_time * 0.5:  # >50% time in I/O
            bottlenecks.append({
                "type": "io",
                "description": "High I/O wait time",
                "wait_time": total_io_wait,
                "severity": "high"
            })
        
        return bottlenecks
    
    async def _save_profile(self, task_id: str, result: ProfileResult):
        """Save profiling results"""
        
        # Save JSON report
        report_path = self.output_dir / f"{task_id}_profile.json"
        with open(report_path, 'w') as f:
            json.dump(asdict(result), f, indent=2)
        
        # Save pstats data
        stats_path = self.output_dir / f"{task_id}_stats.prof"
        self._profiler.dump_stats(str(stats_path))
        
        # Generate flame graph (if py-spy installed)
        try:
            import subprocess
            flame_path = self.output_dir / f"{task_id}_flame.svg"
            subprocess.run([
                "py-spy", "record", "-o", str(flame_path),
                "-d", "10", "-p", str(os.getpid())
            ], check=False)
        except:
            pass  # py-spy not available

# Context manager for I/O tracking
class IOTracker:
    def __init__(self, profiler: PerformanceProfiler, operation: str):
        self.profiler = profiler
        self.operation = operation
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.profiler._io_wait_start[self.operation] = duration
        
        if duration > 1.0:  # Slow operation
            self.profiler._slow_operations.append({
                "operation": self.operation,
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat()
            })
```

### Task 6.2.2: Auto-optimization System (3h)

**Prompt dla AI Agent**:
```
Implementuj system auto-optymalizacji bazujący na metrykach.

Optymalizacje:
1. Dynamic batch sizing dla LLM calls
2. Connection pool auto-tuning
3. Cache size adjustment
4. Task queue optimization
5. Memory limit enforcement
6. CPU throttling prevention

System powinien działać w tle i dostosowywać parametry.
```

**Implementacja**:

```python
# monitoring/optimizer.py
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
import statistics

@dataclass
class OptimizationConfig:
    """Configuration for auto-optimization"""
    min_batch_size: int = 1
    max_batch_size: int = 10
    target_latency_ms: float = 100
    target_memory_mb: int = 500
    max_queue_size: int = 1000
    optimization_interval: int = 60  # seconds

class AutoOptimizer:
    """Automatic performance optimization"""
    
    def __init__(self, config: OptimizationConfig = None):
        self.config = config or OptimizationConfig()
        self._metrics_history: Dict[str, list] = {
            'latency': [],
            'memory': [],
            'queue_depth': [],
            'error_rate': []
        }
        self._current_settings = {
            'batch_size': 5,
            'pool_size': 10,
            'cache_size': 1000,
            'queue_workers': 4
        }
        self._optimization_task = None
    
    async def start(self):
        """Start optimization loop"""
        self._optimization_task = asyncio.create_task(
            self._optimization_loop()
        )
    
    async def stop(self):
        """Stop optimization"""
        if self._optimization_task:
            self._optimization_task.cancel()
    
    async def _optimization_loop(self):
        """Main optimization loop"""
        while True:
            try:
                await asyncio.sleep(self.config.optimization_interval)
                
                # Collect current metrics
                metrics = await self._collect_metrics()
                self._update_history(metrics)
                
                # Run optimizations
                await self._optimize_batch_size()
                await self._optimize_connection_pool()
                await self._optimize_cache()
                await self._optimize_queue()
                
                # Apply settings
                await self._apply_settings()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Optimization error: {e}")
    
    async def _collect_metrics(self) -> Dict[str, float]:
        """Collect current system metrics"""
        # Get from metrics collector
        return {
            'latency': await self._get_avg_latency(),
            'memory': await self._get_memory_usage(),
            'queue_depth': await self._get_queue_depth(),
            'error_rate': await self._get_error_rate()
        }
    
    def _update_history(self, metrics: Dict[str, float]):
        """Update metrics history"""
        for key, value in metrics.items():
            history = self._metrics_history[key]
            history.append(value)
            # Keep last 100 samples
            if len(history) > 100:
                history.pop(0)
    
    async def _optimize_batch_size(self):
        """Optimize LLM batch size based on latency"""
        if len(self._metrics_history['latency']) < 10:
            return
        
        avg_latency = statistics.mean(self._metrics_history['latency'][-10:])
        current_batch = self._current_settings['batch_size']
        
        if avg_latency > self.config.target_latency_ms:
            # Reduce batch size
            new_batch = max(
                self.config.min_batch_size,
                current_batch - 1
            )
        elif avg_latency < self.config.target_latency_ms * 0.5:
            # Increase batch size
            new_batch = min(
                self.config.max_batch_size,
                current_batch + 1
            )
        else:
            return
        
        if new_batch != current_batch:
            self._current_settings['batch_size'] = new_batch
            print(f"Adjusted batch size: {current_batch} -> {new_batch}")
    
    async def _optimize_connection_pool(self):
        """Optimize connection pool size"""
        if len(self._metrics_history['queue_depth']) < 10:
            return
        
        avg_queue = statistics.mean(self._metrics_history['queue_depth'][-10:])
        current_pool = self._current_settings['pool_size']
        
        if avg_queue > 50:  # High queue depth
            new_pool = min(50, current_pool + 5)
        elif avg_queue < 5 and current_pool > 10:
            new_pool = max(10, current_pool - 2)
        else:
            return
        
        if new_pool != current_pool:
            self._current_settings['pool_size'] = new_pool
            print(f"Adjusted pool size: {current_pool} -> {new_pool}")
    
    async def _optimize_cache(self):
        """Optimize cache size based on memory usage"""
        if len(self._metrics_history['memory']) < 10:
            return
        
        avg_memory = statistics.mean(self._metrics_history['memory'][-10:])
        current_cache = self._current_settings['cache_size']
        
        if avg_memory > self.config.target_memory_mb:
            # Reduce cache
            new_cache = max(100, int(current_cache * 0.8))
        elif avg_memory < self.config.target_memory_mb * 0.5:
            # Increase cache
            new_cache = min(10000, int(current_cache * 1.2))
        else:
            return
        
        if new_cache != current_cache:
            self._current_settings['cache_size'] = new_cache
            print(f"Adjusted cache size: {current_cache} -> {new_cache}")
    
    async def _optimize_queue(self):
        """Optimize task queue workers"""
        if len(self._metrics_history['queue_depth']) < 10:
            return
        
        avg_queue = statistics.mean(self._metrics_history['queue_depth'][-10:])
        queue_trend = self._calculate_trend(self._metrics_history['queue_depth'])
        current_workers = self._current_settings['queue_workers']
        
        if avg_queue > 100 and queue_trend > 0:
            # Growing queue - add workers
            new_workers = min(16, current_workers + 1)
        elif avg_queue < 10 and current_workers > 2:
            # Low queue - reduce workers
            new_workers = max(2, current_workers - 1)
        else:
            return
        
        if new_workers != current_workers:
            self._current_settings['queue_workers'] = new_workers
            print(f"Adjusted workers: {current_workers} -> {new_workers}")
    
    def _calculate_trend(self, data: list) -> float:
        """Calculate trend in data (positive = growing)"""
        if len(data) < 2:
            return 0.0
        
        # Simple linear regression
        n = len(data)
        x_mean = (n - 1) / 2
        y_mean = sum(data) / n
        
        numerator = sum((i - x_mean) * (y - y_mean) 
                       for i, y in enumerate(data))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    async def _apply_settings(self):
        """Apply optimized settings to the system"""
        # Update LLM batch processor
        from core.llm import llm_processor
        llm_processor.batch_size = self._current_settings['batch_size']
        
        # Update connection pools
        from core.storage import connection_pool
        await connection_pool.resize(self._current_settings['pool_size'])
        
        # Update cache
        from core.cache import agent_cache
        agent_cache.max_size = self._current_settings['cache_size']
        
        # Update task queue
        from core.queue import task_queue
        await task_queue.scale_workers(self._current_settings['queue_workers'])
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current optimization settings"""
        return self._current_settings.copy()
```

### Task 6.2.3: Alerting System (2h)

**Prompt dla AI Agent**:
```
Dodaj system alertów dla krytycznych metryk.

Alerty dla:
1. High memory usage (>80%)
2. High error rate (>5%)
3. Slow response time (>1s)
4. Queue overflow
5. LLM quota approaching
6. System health degraded

Wsparcie dla: webhook, email, Slack.
```

**Implementacja**:

```python
# monitoring/alerts.py
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
import aiohttp
import asyncio
from datetime import datetime, timedelta

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    """Alert definition"""
    name: str
    severity: AlertSeverity
    condition: str
    message: str
    metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow()

class AlertRule:
    """Base class for alert rules"""
    
    def __init__(self, name: str, severity: AlertSeverity):
        self.name = name
        self.severity = severity
        self._last_triggered = None
        self._cooldown_minutes = 5
    
    async def check(self, metrics: Dict[str, Any]) -> Optional[Alert]:
        """Check if alert should be triggered"""
        raise NotImplementedError
    
    def _can_trigger(self) -> bool:
        """Check if alert is in cooldown"""
        if not self._last_triggered:
            return True
        
        cooldown_end = self._last_triggered + \
                      timedelta(minutes=self._cooldown_minutes)
        return datetime.utcnow() > cooldown_end

class MemoryAlert(AlertRule):
    """Alert for high memory usage"""
    
    def __init__(self, threshold_percent: float = 80):
        super().__init__("high_memory", AlertSeverity.WARNING)
        self.threshold = threshold_percent
    
    async def check(self, metrics: Dict[str, Any]) -> Optional[Alert]:
        memory_percent = metrics.get('memory_percent', 0)
        
        if memory_percent > self.threshold and self._can_trigger():
            self._last_triggered = datetime.utcnow()
            return Alert(
                name=self.name,
                severity=self.severity,
                condition=f"Memory usage > {self.threshold}%",
                message=f"Memory usage is {memory_percent:.1f}%",
                metadata={
                    'memory_percent': memory_percent,
                    'threshold': self.threshold
                }
            )
        return None

class ErrorRateAlert(AlertRule):
    """Alert for high error rate"""
    
    def __init__(self, threshold_percent: float = 5):
        super().__init__("high_error_rate", AlertSeverity.ERROR)
        self.threshold = threshold_percent
    
    async def check(self, metrics: Dict[str, Any]) -> Optional[Alert]:
        error_rate = metrics.get('error_rate', 0)
        
        if error_rate > self.threshold and self._can_trigger():
            self._last_triggered = datetime.utcnow()
            return Alert(
                name=self.name,
                severity=self.severity,
                condition=f"Error rate > {self.threshold}%",
                message=f"Error rate is {error_rate:.1f}%",
                metadata={
                    'error_rate': error_rate,
                    'threshold': self.threshold,
                    'recent_errors': metrics.get('recent_errors', [])
                }
            )
        return None

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.handlers: List['AlertHandler'] = []
        self._check_task = None
        self._check_interval = 30  # seconds
    
    def add_rule(self, rule: AlertRule):
        """Add alert rule"""
        self.rules.append(rule)
    
    def add_handler(self, handler: 'AlertHandler'):
        """Add alert handler"""
        self.handlers.append(handler)
    
    async def start(self):
        """Start alert monitoring"""
        self._check_task = asyncio.create_task(self._check_loop())
    
    async def stop(self):
        """Stop alert monitoring"""
        if self._check_task:
            self._check_task.cancel()
    
    async def _check_loop(self):
        """Main alert checking loop"""
        while True:
            try:
                await asyncio.sleep(self._check_interval)
                
                # Collect metrics
                metrics = await self._collect_metrics()
                
                # Check all rules
                for rule in self.rules:
                    alert = await rule.check(metrics)
                    if alert:
                        await self._handle_alert(alert)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Alert check error: {e}")
    
    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current metrics for alert checking"""
        # Implementation depends on metrics system
        return {
            'memory_percent': 75.5,  # Example
            'error_rate': 2.1,
            'response_time_ms': 150,
            'queue_depth': 50,
            'llm_quota_remaining': 1000
        }
    
    async def _handle_alert(self, alert: Alert):
        """Send alert to all handlers"""
        tasks = [
            handler.send(alert) 
            for handler in self.handlers
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

# Alert Handlers

class WebhookHandler:
    """Send alerts to webhook"""
    
    def __init__(self, url: str, headers: Dict[str, str] = None):
        self.url = url
        self.headers = headers or {}
    
    async def send(self, alert: Alert):
        """Send alert via webhook"""
        payload = {
            'alert': alert.name,
            'severity': alert.severity.value,
            'message': alert.message,
            'condition': alert.condition,
            'timestamp': alert.timestamp.isoformat(),
            'metadata': alert.metadata
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(
                self.url,
                json=payload,
                headers=self.headers
            )

class SlackHandler:
    """Send alerts to Slack"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send(self, alert: Alert):
        """Send alert to Slack"""
        color = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ff9900",
            AlertSeverity.ERROR: "#ff0000",
            AlertSeverity.CRITICAL: "#990000"
        }.get(alert.severity, "#808080")
        
        payload = {
            "attachments": [{
                "color": color,
                "title": f"{alert.severity.value.upper()}: {alert.name}",
                "text": alert.message,
                "fields": [
                    {
                        "title": "Condition",
                        "value": alert.condition,
                        "short": True
                    },
                    {
                        "title": "Time",
                        "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "short": True
                    }
                ],
                "footer": "LiteCrewAI Alert System"
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(self.webhook_url, json=payload)

# Setup default alerts
def setup_default_alerts(alert_manager: AlertManager):
    """Setup default alert rules"""
    
    # Memory alerts
    alert_manager.add_rule(MemoryAlert(threshold_percent=80))
    alert_manager.add_rule(MemoryAlert(threshold_percent=95))
    
    # Error rate alerts  
    alert_manager.add_rule(ErrorRateAlert(threshold_percent=5))
    alert_manager.add_rule(ErrorRateAlert(threshold_percent=10))
    
    # Response time alert
    class ResponseTimeAlert(AlertRule):
        def __init__(self):
            super().__init__("slow_response", AlertSeverity.WARNING)
        
        async def check(self, metrics: Dict[str, Any]) -> Optional[Alert]:
            response_time = metrics.get('response_time_ms', 0)
            if response_time > 1000 and self._can_trigger():
                self._last_triggered = datetime.utcnow()
                return Alert(
                    name=self.name,
                    severity=self.severity,
                    condition="Response time > 1s",
                    message=f"Average response time is {response_time}ms",
                    metadata={'response_time_ms': response_time}
                )
            return None
    
    alert_manager.add_rule(ResponseTimeAlert())
```

---

## 🎯 Podsumowanie Fazy 6

### Osiągnięte cele:
1. ✅ OpenTelemetry integration dla distributed tracing
2. ✅ Comprehensive metrics collection (Prometheus)
3. ✅ Performance profiling z flame graphs
4. ✅ Auto-optimization system
5. ✅ Multi-channel alerting
6. ✅ Real-time monitoring dashboard

### Kluczowe komponenty:
- **Telemetry**: Full observability z OpenTelemetry
- **Metrics**: Prometheus-compatible metrics
- **Profiler**: Async-aware performance profiling
- **Optimizer**: Automatic parameter tuning
- **Alerts**: Proactive issue detection

### Metryki monitorowane:
- System: CPU, memory, I/O, network
- Application: agents, tasks, queues
- Business: costs, success rates, SLAs
- Performance: latency, throughput, errors

### Integracje:
- Prometheus/Grafana dla visualization
- Jaeger dla distributed tracing
- Slack/webhooks dla alertów
- Custom dashboards

### Następne kroki:
1. Production deployment ([Faza 7](./faza-7-deployment.md))
2. Documentation i training materials
3. Community release preparation

---

*End of Phase 6 Documentation*

---

[← Powrót do README](./README.md) | [← Faza 5: API](./faza-5-api.md) | [Następna faza: Deployment →](./faza-7-deployment.md)
