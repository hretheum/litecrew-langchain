#!/usr/bin/env python3
"""
Complete benchmark suite for AI frameworks
Tests real-world scenarios with production metrics
"""

import time
import psutil
import asyncio
import statistics
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from memory_profiler import profile
import json
from pathlib import Path
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import threading
import gc

# Prometheus metrics
response_time = Histogram('framework_response_time_seconds', 'Response time', ['framework', 'test'])
memory_usage = Gauge('framework_memory_usage_mb', 'Memory usage in MB', ['framework', 'test'])
cpu_usage = Gauge('framework_cpu_usage_percent', 'CPU usage percentage', ['framework', 'test'])
success_rate = Counter('framework_test_success_total', 'Successful tests', ['framework', 'test'])
error_rate = Counter('framework_test_errors_total', 'Failed tests', ['framework', 'test'])

@dataclass
class TestResult:
    framework: str
    test_name: str
    success: bool
    duration_seconds: float
    memory_start_mb: float
    memory_peak_mb: float
    memory_end_mb: float
    cpu_percent: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

class FrameworkBenchmark:
    """Base class for framework benchmarks"""
    
    def __init__(self, framework_name: str, adapter):
        self.framework_name = framework_name
        self.adapter = adapter
        self.results: List[TestResult] = []
        self.process = psutil.Process()
        
    @contextmanager
    def measure_performance(self, test_name: str):
        """Context manager to measure performance metrics"""
        # Force garbage collection before test
        gc.collect()
        gc.collect()
        gc.collect()
        time.sleep(0.5)  # Let system stabilize
        
        # Start measurements
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        self.process.cpu_percent()  # First call to initialize
        
        # Track peak memory in background
        peak_memory = start_memory
        monitoring = True
        
        def monitor_memory():
            nonlocal peak_memory
            while monitoring:
                current = self.process.memory_info().rss / 1024 / 1024
                peak_memory = max(peak_memory, current)
                time.sleep(0.1)
        
        monitor_thread = threading.Thread(target=monitor_memory)
        monitor_thread.start()
        
        result = TestResult(
            framework=self.framework_name,
            test_name=test_name,
            success=False,
            duration_seconds=0,
            memory_start_mb=start_memory,
            memory_peak_mb=0,
            memory_end_mb=0,
            cpu_percent=0
        )
        
        try:
            yield result
            result.success = True
        except Exception as e:
            result.error = str(e)
            error_rate.labels(framework=self.framework_name, test=test_name).inc()
        finally:
            # Stop monitoring
            monitoring = False
            monitor_thread.join()
            
            # Final measurements
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024
            cpu_percent = self.process.cpu_percent(interval=0.5)
            
            # Update result
            result.duration_seconds = end_time - start_time
            result.memory_peak_mb = peak_memory
            result.memory_end_mb = end_memory
            result.cpu_percent = cpu_percent
            
            # Update Prometheus metrics
            response_time.labels(framework=self.framework_name, test=test_name).observe(result.duration_seconds)
            memory_usage.labels(framework=self.framework_name, test=test_name).set(peak_memory)
            cpu_usage.labels(framework=self.framework_name, test=test_name).set(cpu_percent)
            
            if result.success:
                success_rate.labels(framework=self.framework_name, test=test_name).inc()
            
            self.results.append(result)
            
    def test_single_agent(self):
        """Test 1: Basic single agent Q&A"""
        with self.measure_performance("single_agent") as result:
            agent = self.adapter.create_agent(
                role="Assistant",
                goal="Answer questions helpfully"
            )
            
            task = self.adapter.create_task(
                description="What is the capital of France?",
                agent=agent
            )
            
            response = self.adapter.execute([task])
            result.metadata = {"response_length": len(str(response))}
            
    def test_multi_agent(self):
        """Test 2: Multi-agent collaboration (3 agents)"""
        with self.measure_performance("multi_agent") as result:
            # Create 3 specialized agents
            researcher = self.adapter.create_agent(
                role="Researcher",
                goal="Find accurate information"
            )
            
            analyst = self.adapter.create_agent(
                role="Analyst", 
                goal="Analyze data and draw conclusions"
            )
            
            writer = self.adapter.create_agent(
                role="Writer",
                goal="Write clear summaries"
            )
            
            # Create collaborative tasks
            tasks = [
                self.adapter.create_task(
                    description="Research the top 3 programming languages in 2024",
                    agent=researcher
                ),
                self.adapter.create_task(
                    description="Analyze the pros and cons of each language",
                    agent=analyst
                ),
                self.adapter.create_task(
                    description="Write a summary report",
                    agent=writer
                )
            ]
            
            response = self.adapter.execute(tasks)
            result.metadata = {"num_agents": 3, "num_tasks": 3}
            
    def test_memory_persistence(self):
        """Test 3: Memory save/load operations"""
        with self.measure_performance("memory_persistence") as result:
            # Create agent with memory
            agent = self.adapter.create_agent(
                role="Memory Bot",
                goal="Remember conversations"
            )
            
            # First conversation
            task1 = self.adapter.create_task(
                description="Remember this: The secret code is ALPHA-7",
                agent=agent
            )
            self.adapter.execute([task1])
            
            # Save state
            state = self.adapter.save_state()
            
            # Clear and restore
            self.adapter.clear_state()
            self.adapter.load_state(state)
            
            # Verify memory
            task2 = self.adapter.create_task(
                description="What was the secret code?",
                agent=agent
            )
            response = self.adapter.execute([task2])
            
            result.metadata = {
                "state_size_bytes": len(json.dumps(state)) if state else 0,
                "memory_retained": "ALPHA-7" in str(response)
            }
            
    def test_concurrent_load(self):
        """Test 4: Concurrent task execution"""
        with self.measure_performance("concurrent_load") as result:
            agents = []
            tasks = []
            
            # Create 10 agents with tasks
            for i in range(10):
                agent = self.adapter.create_agent(
                    role=f"Worker-{i}",
                    goal="Process tasks quickly"
                )
                task = self.adapter.create_task(
                    description=f"Calculate fibonacci number {i+20}",
                    agent=agent
                )
                agents.append(agent)
                tasks.append(task)
            
            # Execute concurrently
            start = time.time()
            if hasattr(self.adapter, 'execute_concurrent'):
                responses = self.adapter.execute_concurrent(tasks)
            else:
                # Fallback to sequential
                responses = self.adapter.execute(tasks)
            
            execution_time = time.time() - start
            
            result.metadata = {
                "num_concurrent_tasks": 10,
                "total_execution_time": execution_time,
                "avg_time_per_task": execution_time / 10
            }
            
    def test_long_conversation(self):
        """Test 5: Long conversation (100 messages)"""
        with self.measure_performance("long_conversation") as result:
            agent = self.adapter.create_agent(
                role="Conversationalist",
                goal="Maintain context over long conversations"
            )
            
            message_times = []
            memory_checkpoints = []
            
            for i in range(100):
                start = time.time()
                
                task = self.adapter.create_task(
                    description=f"Message {i}: Tell me about item number {i}",
                    agent=agent
                )
                
                self.adapter.execute([task])
                
                message_time = time.time() - start
                message_times.append(message_time)
                
                # Memory checkpoint every 20 messages
                if i % 20 == 0:
                    memory_mb = self.process.memory_info().rss / 1024 / 1024
                    memory_checkpoints.append(memory_mb)
            
            result.metadata = {
                "num_messages": 100,
                "avg_message_time": statistics.mean(message_times),
                "p95_message_time": statistics.quantiles(message_times, n=20)[18],
                "memory_growth": memory_checkpoints[-1] - memory_checkpoints[0] if memory_checkpoints else 0,
                "memory_checkpoints": memory_checkpoints
            }
            
    def test_error_handling(self):
        """Test 6: Error handling and recovery"""
        with self.measure_performance("error_handling") as result:
            agent = self.adapter.create_agent(
                role="Error Handler",
                goal="Handle errors gracefully"
            )
            
            error_scenarios = []
            
            # Test various error scenarios
            test_cases = [
                "Divide by zero: calculate 1/0",
                "Invalid JSON: parse {invalid json}",
                "Network timeout: fetch data from http://invalid.url.test",
                "Memory limit: create list with 10^100 elements"
            ]
            
            for scenario in test_cases:
                try:
                    task = self.adapter.create_task(
                        description=scenario,
                        agent=agent
                    )
                    response = self.adapter.execute([task])
                    error_scenarios.append({
                        "scenario": scenario,
                        "handled": True,
                        "response": str(response)[:100]
                    })
                except Exception as e:
                    error_scenarios.append({
                        "scenario": scenario,
                        "handled": False,
                        "error": str(e)
                    })
            
            handled_count = sum(1 for s in error_scenarios if s["handled"])
            result.metadata = {
                "total_scenarios": len(test_cases),
                "handled_gracefully": handled_count,
                "error_rate": (len(test_cases) - handled_count) / len(test_cases),
                "scenarios": error_scenarios
            }
            
    def run_all_tests(self, iterations: int = 3):
        """Run all benchmark tests"""
        print(f"\n🧪 Testing {self.framework_name}")
        print("=" * 50)
        
        tests = [
            self.test_single_agent,
            self.test_multi_agent,
            self.test_memory_persistence,
            self.test_concurrent_load,
            self.test_long_conversation,
            self.test_error_handling
        ]
        
        for test_func in tests:
            test_name = test_func.__name__
            print(f"\n📊 Running {test_name}...")
            
            for i in range(iterations):
                print(f"  Iteration {i+1}/{iterations}...", end="", flush=True)
                
                try:
                    test_func()
                    print(" ✅")
                except Exception as e:
                    print(f" ❌ {e}")
                
                # Cool down between iterations
                time.sleep(2)
                gc.collect()
        
        return self.results
    
    def save_results(self, output_dir: Path):
        """Save benchmark results to file"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_dir / f"{self.framework_name}_{timestamp}.json"
        
        data = {
            "framework": self.framework_name,
            "timestamp": timestamp,
            "results": [asdict(r) for r in self.results],
            "summary": self._generate_summary()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        if not self.results:
            return {}
        
        # Group by test name
        test_groups = {}
        for result in self.results:
            if result.test_name not in test_groups:
                test_groups[result.test_name] = []
            test_groups[result.test_name].append(result)
        
        summary = {}
        for test_name, results in test_groups.items():
            successful = [r for r in results if r.success]
            
            if successful:
                summary[test_name] = {
                    "success_rate": len(successful) / len(results),
                    "avg_duration": statistics.mean(r.duration_seconds for r in successful),
                    "avg_memory_peak": statistics.mean(r.memory_peak_mb for r in successful),
                    "avg_cpu": statistics.mean(r.cpu_percent for r in successful),
                    "memory_growth": statistics.mean(r.memory_end_mb - r.memory_start_mb for r in successful)
                }
            else:
                summary[test_name] = {
                    "success_rate": 0,
                    "errors": [r.error for r in results if r.error]
                }
        
        return summary


if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8000)
    print("📊 Prometheus metrics available at http://localhost:8000")
    
    # Example usage (would be called with actual adapters)
    print("\n🚀 Full Benchmark Suite Ready!")
    print("This script requires framework adapters to run.")
    print("See framework-adapters/ directory for implementations."