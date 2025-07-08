"""
Testing Framework for LiteCrew.

Provides utilities for testing crews, agents, and tasks with performance benchmarking.
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from litecrew.agent import Agent as LiteAgent
from litecrew.crew import Crew as LiteCrew
from litecrew.task import LiteTask, TaskOutput


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TestCase:
    """A single test case for crew testing."""
    
    name: str
    description: str
    crew_config: Dict[str, Any]
    expected_outputs: Dict[str, Any] = field(default_factory=dict)
    performance_thresholds: Dict[str, float] = field(default_factory=dict)
    timeout: float = 60.0
    
    # Test execution state
    status: TestStatus = TestStatus.PENDING
    actual_outputs: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    error: Optional[Exception] = None
    execution_time: float = 0.0
    
    def validate_outputs(self) -> Tuple[bool, List[str]]:
        """Validate actual outputs against expected."""
        issues = []
        
        for key, expected in self.expected_outputs.items():
            if key not in self.actual_outputs:
                issues.append(f"Missing output: {key}")
                continue
            
            actual = self.actual_outputs[key]
            
            # Type validation
            if type(expected) != type(actual):
                issues.append(f"Type mismatch for {key}: expected {type(expected)}, got {type(actual)}")
                continue
            
            # Value validation
            if isinstance(expected, dict):
                # Recursive validation for dicts
                for sub_key, sub_expected in expected.items():
                    if sub_key not in actual:
                        issues.append(f"Missing key {key}.{sub_key}")
                    elif actual[sub_key] != sub_expected:
                        issues.append(f"Value mismatch for {key}.{sub_key}")
            elif isinstance(expected, list):
                # List validation
                if len(expected) != len(actual):
                    issues.append(f"List length mismatch for {key}: expected {len(expected)}, got {len(actual)}")
            else:
                # Direct comparison
                if actual != expected:
                    issues.append(f"Value mismatch for {key}: expected {expected}, got {actual}")
        
        return len(issues) == 0, issues
    
    def validate_performance(self) -> Tuple[bool, List[str]]:
        """Validate performance metrics against thresholds."""
        issues = []
        
        for metric, threshold in self.performance_thresholds.items():
            if metric not in self.performance_metrics:
                issues.append(f"Missing performance metric: {metric}")
                continue
            
            actual_value = self.performance_metrics[metric]
            
            # Handle different threshold types
            if metric.endswith("_time") or metric in ["execution_time", "latency"]:
                # Lower is better for time metrics
                if actual_value > threshold:
                    issues.append(f"{metric}: {actual_value:.3f}s exceeds threshold {threshold:.3f}s")
            elif metric.endswith("_rate") or metric in ["throughput", "success_rate"]:
                # Higher is better for rate metrics
                if actual_value < threshold:
                    issues.append(f"{metric}: {actual_value:.2f} below threshold {threshold:.2f}")
        
        return len(issues) == 0, issues


@dataclass
class TestSuite:
    """A collection of test cases."""
    
    name: str
    description: str
    test_cases: List[TestCase] = field(default_factory=list)
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None
    
    def add_test(self, test_case: TestCase) -> None:
        """Add a test case to the suite."""
        self.test_cases.append(test_case)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test suite summary."""
        status_counts = {status: 0 for status in TestStatus}
        total_time = 0.0
        
        for test in self.test_cases:
            status_counts[test.status] += 1
            total_time += test.execution_time
        
        return {
            "name": self.name,
            "total_tests": len(self.test_cases),
            "passed": status_counts[TestStatus.PASSED],
            "failed": status_counts[TestStatus.FAILED],
            "skipped": status_counts[TestStatus.SKIPPED],
            "pending": status_counts[TestStatus.PENDING],
            "total_execution_time": total_time,
            "pass_rate": (
                status_counts[TestStatus.PASSED] / len(self.test_cases)
                if self.test_cases else 0
            )
        }


class CrewTestRunner:
    """Test runner for crew testing."""
    
    def __init__(
        self,
        verbose: bool = True,
        parallel: bool = False,
        max_workers: int = 4
    ):
        """Initialize test runner.
        
        Args:
            verbose: Enable verbose output
            parallel: Run tests in parallel
            max_workers: Max parallel test executions
        """
        self.verbose = verbose
        self.parallel = parallel
        self.max_workers = max_workers
        self._performance_tracker = PerformanceTracker()
    
    def run_test_case(self, test_case: TestCase) -> TestCase:
        """Run a single test case.
        
        Args:
            test_case: Test case to run
            
        Returns:
            Updated test case with results
        """
        if self.verbose:
            print(f"\nRunning test: {test_case.name}")
            print(f"Description: {test_case.description}")
        
        test_case.status = TestStatus.RUNNING
        start_time = time.perf_counter()
        
        try:
            # Create crew from config
            crew = self._create_crew_from_config(test_case.crew_config)
            
            # Start performance tracking
            self._performance_tracker.start_tracking()
            
            # Execute crew
            result = crew.kickoff()
            
            # Stop tracking and get metrics
            metrics = self._performance_tracker.stop_tracking()
            
            # Store results
            test_case.actual_outputs = {
                "result": result,
                "crew_output": str(result) if result else ""
            }
            test_case.performance_metrics = metrics
            test_case.execution_time = time.perf_counter() - start_time
            
            # Validate outputs
            output_valid, output_issues = test_case.validate_outputs()
            perf_valid, perf_issues = test_case.validate_performance()
            
            if output_valid and perf_valid:
                test_case.status = TestStatus.PASSED
                if self.verbose:
                    print(f"✅ Test PASSED in {test_case.execution_time:.3f}s")
            else:
                test_case.status = TestStatus.FAILED
                if self.verbose:
                    print(f"❌ Test FAILED")
                    for issue in output_issues + perf_issues:
                        print(f"   - {issue}")
            
        except Exception as e:
            test_case.status = TestStatus.FAILED
            test_case.error = e
            test_case.execution_time = time.perf_counter() - start_time
            
            if self.verbose:
                print(f"❌ Test FAILED with error: {str(e)}")
        
        return test_case
    
    def run_test_suite(self, test_suite: TestSuite) -> TestSuite:
        """Run a complete test suite.
        
        Args:
            test_suite: Test suite to run
            
        Returns:
            Updated test suite with results
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Running Test Suite: {test_suite.name}")
            print(f"Description: {test_suite.description}")
            print(f"Total tests: {len(test_suite.test_cases)}")
            print(f"{'='*60}")
        
        # Run setup if provided
        if test_suite.setup:
            if self.verbose:
                print("\nRunning setup...")
            test_suite.setup()
        
        # Run tests
        if self.parallel and len(test_suite.test_cases) > 1:
            # Parallel execution
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [
                    executor.submit(self.run_test_case, test)
                    for test in test_suite.test_cases
                ]
                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    test_suite.test_cases[i] = future.result()
        else:
            # Sequential execution
            for i, test in enumerate(test_suite.test_cases):
                test_suite.test_cases[i] = self.run_test_case(test)
        
        # Run teardown if provided
        if test_suite.teardown:
            if self.verbose:
                print("\nRunning teardown...")
            test_suite.teardown()
        
        # Print summary
        if self.verbose:
            summary = test_suite.get_summary()
            print(f"\n{'='*60}")
            print(f"Test Suite Summary: {test_suite.name}")
            print(f"{'='*60}")
            print(f"Total tests: {summary['total_tests']}")
            print(f"Passed: {summary['passed']} ✅")
            print(f"Failed: {summary['failed']} ❌")
            print(f"Skipped: {summary['skipped']} ⏭️")
            print(f"Pass rate: {summary['pass_rate']*100:.1f}%")
            print(f"Total time: {summary['total_execution_time']:.3f}s")
        
        return test_suite
    
    def _create_crew_from_config(self, config: Dict[str, Any]) -> LiteCrew:
        """Create a crew instance from configuration."""
        # Create agents
        agents = []
        for agent_config in config.get("agents", []):
            agent = LiteAgent(**agent_config)
            agents.append(agent)
        
        # Create tasks
        tasks = []
        for task_config in config.get("tasks", []):
            # Find agent by role
            agent_role = task_config.pop("agent_role", None)
            agent = next((a for a in agents if a.role == agent_role), agents[0])
            
            task = LiteTask(agent=agent, **task_config)
            tasks.append(task)
        
        # Create crew
        crew_params = config.get("crew", {})
        crew = LiteCrew(agents=agents, tasks=tasks, **crew_params)
        
        return crew


class PerformanceTracker:
    """Track performance metrics during test execution."""
    
    def __init__(self):
        """Initialize performance tracker."""
        self._start_time = None
        self._start_memory = None
        self._metrics = {}
    
    def start_tracking(self) -> None:
        """Start tracking performance metrics."""
        import psutil
        import os
        
        self._start_time = time.perf_counter()
        
        # Get memory usage
        process = psutil.Process(os.getpid())
        self._start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Reset metrics
        self._metrics = {
            "start_time": self._start_time,
            "start_memory_mb": self._start_memory
        }
    
    def stop_tracking(self) -> Dict[str, float]:
        """Stop tracking and return metrics."""
        import psutil
        import os
        
        if not self._start_time:
            return {}
        
        # Calculate execution time
        execution_time = time.perf_counter() - self._start_time
        
        # Get final memory usage
        process = psutil.Process(os.getpid())
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = end_memory - self._start_memory
        
        # Update metrics
        self._metrics.update({
            "execution_time": execution_time,
            "end_memory_mb": end_memory,
            "memory_delta_mb": memory_delta,
            "cpu_percent": process.cpu_percent(),
            "throughput": 1.0 / execution_time if execution_time > 0 else 0
        })
        
        return self._metrics


class MockLLMProvider:
    """Mock LLM provider for testing."""
    
    def __init__(
        self,
        responses: Optional[Dict[str, str]] = None,
        response_time: float = 0.1,
        error_rate: float = 0.0
    ):
        """Initialize mock LLM provider.
        
        Args:
            responses: Predefined responses by prompt pattern
            response_time: Simulated response time
            error_rate: Probability of error (0-1)
        """
        self.responses = responses or {}
        self.response_time = response_time
        self.error_rate = error_rate
        self._call_count = 0
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a mock response."""
        import random
        
        self._call_count += 1
        
        # Simulate response time
        time.sleep(self.response_time)
        
        # Simulate errors
        if random.random() < self.error_rate:
            raise Exception("Mock LLM error")
        
        # Find matching response
        for pattern, response in self.responses.items():
            if pattern in prompt:
                return response
        
        # Default response
        return f"Mock response for prompt: {prompt[:50]}..."
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get mock provider metrics."""
        return {
            "call_count": self._call_count,
            "avg_response_time": self.response_time,
            "error_rate": self.error_rate
        }


def create_test_crew(
    name: str = "Test Crew",
    num_agents: int = 2,
    num_tasks: int = 3
) -> Dict[str, Any]:
    """Create a test crew configuration.
    
    Args:
        name: Crew name
        num_agents: Number of agents
        num_tasks: Number of tasks
        
    Returns:
        Crew configuration dict
    """
    config = {
        "agents": [],
        "tasks": [],
        "crew": {
            "name": name,
            "verbose": False
        }
    }
    
    # Create agents
    for i in range(num_agents):
        config["agents"].append({
            "role": f"Test Agent {i}",
            "goal": f"Complete test tasks assigned to agent {i}",
            "backstory": f"A test agent created for testing purposes"
        })
    
    # Create tasks
    for i in range(num_tasks):
        config["tasks"].append({
            "description": f"Test task {i}",
            "expected_output": f"Output from task {i}",
            "agent_role": f"Test Agent {i % num_agents}"
        })
    
    return config