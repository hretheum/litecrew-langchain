"""
Tests for Testing Framework.
"""

import time
from unittest.mock import MagicMock, patch

import pytest

from litecrew.testing.framework import (
    CrewTestRunner,
    MockLLMProvider,
    PerformanceTracker,
    TestCase,
    TestStatus,
    TestSuite,
    create_test_crew,
)


class TestTestCase:
    """Test the TestCase class."""
    
    def test_output_validation(self):
        """Test output validation logic."""
        test_case = TestCase(
            name="Test validation",
            description="Test output validation",
            crew_config={},
            expected_outputs={
                "result": "expected result",
                "metrics": {"accuracy": 0.95, "speed": 100}
            }
        )
        
        # Test exact match
        test_case.actual_outputs = {
            "result": "expected result",
            "metrics": {"accuracy": 0.95, "speed": 100}
        }
        valid, issues = test_case.validate_outputs()
        assert valid
        assert len(issues) == 0
        
        # Test mismatch
        test_case.actual_outputs = {
            "result": "different result",
            "metrics": {"accuracy": 0.90, "speed": 100}
        }
        valid, issues = test_case.validate_outputs()
        assert not valid
        assert len(issues) > 0
        assert any("result" in issue for issue in issues)
        assert any("accuracy" in issue for issue in issues)
    
    def test_performance_validation(self):
        """Test performance metric validation."""
        test_case = TestCase(
            name="Test performance",
            description="Test performance validation",
            crew_config={},
            performance_thresholds={
                "execution_time": 1.0,  # Max 1 second
                "throughput": 10.0,     # Min 10 ops/sec
                "memory_delta_mb": 50.0  # Max 50MB increase
            }
        )
        
        # Test passing metrics
        test_case.performance_metrics = {
            "execution_time": 0.5,
            "throughput": 15.0,
            "memory_delta_mb": 30.0
        }
        valid, issues = test_case.validate_performance()
        assert valid
        assert len(issues) == 0
        
        # Test failing metrics
        test_case.performance_metrics = {
            "execution_time": 1.5,  # Too slow
            "throughput": 5.0,      # Too low
            "memory_delta_mb": 60.0  # Too much memory
        }
        valid, issues = test_case.validate_performance()
        assert not valid
        assert len(issues) == 3


class TestTestSuite:
    """Test the TestSuite class."""
    
    def test_suite_summary(self):
        """Test suite summary generation."""
        suite = TestSuite(
            name="Test Suite",
            description="Test suite description"
        )
        
        # Add test cases with different statuses
        for status in [TestStatus.PASSED, TestStatus.PASSED, TestStatus.FAILED]:
            test = TestCase(
                name=f"Test {status.value}",
                description="Test",
                crew_config={}
            )
            test.status = status
            test.execution_time = 1.0
            suite.add_test(test)
        
        summary = suite.get_summary()
        
        assert summary["total_tests"] == 3
        assert summary["passed"] == 2
        assert summary["failed"] == 1
        assert summary["pass_rate"] == 2/3
        assert summary["total_execution_time"] == 3.0


class TestCrewTestRunner:
    """Test the CrewTestRunner class."""
    
    @pytest.fixture
    def runner(self):
        """Create test runner."""
        return CrewTestRunner(verbose=False)
    
    def test_run_test_case_success(self, runner):
        """Test running a successful test case."""
        test_case = TestCase(
            name="Success test",
            description="Should pass",
            crew_config=create_test_crew(num_agents=1, num_tasks=1),
            expected_outputs={"crew_output": ""}
        )
        
        # Mock crew execution
        with patch('litecrew.crew.Crew.kickoff', return_value="Success"):
            result = runner.run_test_case(test_case)
        
        assert result.status == TestStatus.PASSED
        assert result.execution_time > 0
        assert "result" in result.actual_outputs
    
    def test_run_test_case_failure(self, runner):
        """Test running a failing test case."""
        test_case = TestCase(
            name="Failure test",
            description="Should fail",
            crew_config=create_test_crew(),
            expected_outputs={"result": "Expected"}
        )
        
        # Mock crew execution with different output
        with patch('litecrew.crew.Crew.kickoff', return_value="Different"):
            result = runner.run_test_case(test_case)
        
        assert result.status == TestStatus.FAILED
    
    def test_run_test_case_error(self, runner):
        """Test handling execution errors."""
        test_case = TestCase(
            name="Error test",
            description="Should error",
            crew_config=create_test_crew()
        )
        
        # Mock crew execution with error
        with patch('litecrew.crew.Crew.kickoff', side_effect=Exception("Test error")):
            result = runner.run_test_case(test_case)
        
        assert result.status == TestStatus.FAILED
        assert result.error is not None
        assert "Test error" in str(result.error)
    
    def test_parallel_execution(self):
        """Test parallel test execution."""
        runner = CrewTestRunner(verbose=False, parallel=True, max_workers=2)
        
        suite = TestSuite(
            name="Parallel Suite",
            description="Test parallel execution"
        )
        
        # Add multiple test cases
        for i in range(4):
            test = TestCase(
                name=f"Test {i}",
                description="Parallel test",
                crew_config=create_test_crew(num_agents=1, num_tasks=1)
            )
            suite.add_test(test)
        
        # Mock crew execution with delay
        def mock_kickoff():
            time.sleep(0.1)
            return "Done"
        
        with patch('litecrew.crew.Crew.kickoff', side_effect=mock_kickoff):
            start_time = time.perf_counter()
            result_suite = runner.run_test_suite(suite)
            execution_time = time.perf_counter() - start_time
        
        # Should be faster than sequential (4 * 0.1 = 0.4s)
        assert execution_time < 0.3  # Some overhead allowed
        
        summary = result_suite.get_summary()
        assert summary["total_tests"] == 4


class TestPerformanceTracker:
    """Test the PerformanceTracker class."""
    
    def test_performance_tracking(self):
        """Test performance metric tracking."""
        tracker = PerformanceTracker()
        
        # Start tracking
        tracker.start_tracking()
        assert tracker._start_time is not None
        assert tracker._start_memory is not None
        
        # Simulate some work
        time.sleep(0.1)
        
        # Stop tracking
        metrics = tracker.stop_tracking()
        
        assert "execution_time" in metrics
        assert metrics["execution_time"] >= 0.1
        assert "memory_delta_mb" in metrics
        assert "cpu_percent" in metrics
        assert "throughput" in metrics
        assert metrics["throughput"] <= 10  # Max 10 ops/sec for 0.1s execution


class TestMockLLMProvider:
    """Test the MockLLMProvider class."""
    
    def test_mock_responses(self):
        """Test mock LLM responses."""
        mock_llm = MockLLMProvider(
            responses={
                "hello": "Hi there!",
                "analyze": "Analysis complete"
            },
            response_time=0.01
        )
        
        # Test pattern matching
        assert mock_llm.generate("Say hello") == "Hi there!"
        assert mock_llm.generate("Please analyze this") == "Analysis complete"
        assert "Mock response" in mock_llm.generate("Unknown prompt")
        
        # Check metrics
        metrics = mock_llm.get_metrics()
        assert metrics["call_count"] == 3
        assert metrics["avg_response_time"] == 0.01
    
    def test_mock_errors(self):
        """Test mock error simulation."""
        mock_llm = MockLLMProvider(
            error_rate=1.0  # Always error
        )
        
        with pytest.raises(Exception, match="Mock LLM error"):
            mock_llm.generate("Test prompt")
    
    def test_response_time_simulation(self):
        """Test response time simulation."""
        mock_llm = MockLLMProvider(response_time=0.05)
        
        start_time = time.perf_counter()
        mock_llm.generate("Test")
        elapsed = time.perf_counter() - start_time
        
        assert elapsed >= 0.05


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_create_test_crew(self):
        """Test test crew creation."""
        config = create_test_crew(
            name="Custom Crew",
            num_agents=3,
            num_tasks=5
        )
        
        assert len(config["agents"]) == 3
        assert len(config["tasks"]) == 5
        assert config["crew"]["name"] == "Custom Crew"
        
        # Check agent assignment
        for i, task in enumerate(config["tasks"]):
            expected_agent = f"Test Agent {i % 3}"
            assert task["agent_role"] == expected_agent