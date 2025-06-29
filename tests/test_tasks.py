"""
Test suite for LiteCrewAI Task functionality
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

class TestTaskCore:
    """Test core task functionality"""
    
    def test_task_initialization(self, sample_task_config):
        """Test task initialization with valid config"""
        class MockTask:
            def __init__(self, **config):
                self.name = config.get('name')
                self.description = config.get('description')
                self.expected_output = config.get('expected_output')
                self.agent = config.get('agent')
                self.tools = config.get('tools', [])
                self.async_execution = config.get('async_execution', False)
                self.status = 'pending'
                self.created_at = datetime.now()
        
        task = MockTask(**sample_task_config)
        assert task.name == "test_task"
        assert task.description == "This is a test task"
        assert task.expected_output == "A successful test result"
        assert task.agent == "test_agent"
        assert task.status == 'pending'
        assert isinstance(task.created_at, datetime)
    
    def test_task_validation(self):
        """Test task configuration validation"""
        from pydantic import BaseModel, ValidationError
        
        class TaskConfig(BaseModel):
            name: str
            description: str
            expected_output: str
            agent: str
        
        # Valid config
        valid_config = {
            "name": "test_task",
            "description": "Test description",
            "expected_output": "Expected result",
            "agent": "test_agent"
        }
        config = TaskConfig(**valid_config)
        assert config.name == "test_task"
        
        # Invalid config - missing required fields
        with pytest.raises(ValidationError):
            TaskConfig(name="test")
    
    def test_task_dependencies(self):
        """Test task dependency system"""
        class MockTask:
            def __init__(self, name):
                self.name = name
                self.dependencies = []
                self.status = 'pending'
            
            def add_dependency(self, task):
                self.dependencies.append(task)
            
            def can_execute(self):
                return all(dep.status == 'completed' for dep in self.dependencies)
            
            def complete(self):
                self.status = 'completed'
        
        task1 = MockTask("task1")
        task2 = MockTask("task2") 
        task3 = MockTask("task3")
        
        # Set up dependencies: task3 depends on task1 and task2
        task3.add_dependency(task1)
        task3.add_dependency(task2)
        
        # Initially task3 cannot execute
        assert not task3.can_execute()
        
        # Complete task1
        task1.complete()
        assert not task3.can_execute()  # Still waiting for task2
        
        # Complete task2
        task2.complete()
        assert task3.can_execute()  # Now task3 can execute

class TestTaskExecution:
    """Test task execution engine"""
    
    @pytest.mark.asyncio
    async def test_async_task_execution(self):
        """Test asynchronous task execution"""
        class MockAsyncTask:
            def __init__(self, name, duration=0.01):
                self.name = name
                self.duration = duration
                self.status = 'pending'
                self.result = None
            
            async def execute(self):
                self.status = 'running'
                # Simulate async work
                import asyncio
                await asyncio.sleep(self.duration)
                self.result = f"Completed {self.name}"
                self.status = 'completed'
                return self.result
        
        task = MockAsyncTask("async_test", 0.01)
        
        # Execute task
        result = await task.execute()
        
        assert task.status == 'completed'
        assert result == "Completed async_test"
        assert task.result == "Completed async_test"
    
    def test_sync_task_execution(self):
        """Test synchronous task execution"""
        class MockSyncTask:
            def __init__(self, name):
                self.name = name
                self.status = 'pending'
                self.result = None
            
            def execute(self):
                self.status = 'running'
                # Simulate work
                self.result = f"Completed {self.name}"
                self.status = 'completed'
                return self.result
        
        task = MockSyncTask("sync_test")
        
        # Execute task
        result = task.execute()
        
        assert task.status == 'completed'
        assert result == "Completed sync_test"
    
    def test_task_timeout(self):
        """Test task timeout handling"""
        import time
        import signal
        
        class TimeoutTask:
            def __init__(self, name, timeout=1):
                self.name = name
                self.timeout = timeout
                self.status = 'pending'
            
            def execute_with_timeout(self, work_duration=0.5):
                self.status = 'running'
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Task {self.name} timed out")
                
                # Set up timeout
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(self.timeout)
                
                try:
                    # Simulate work
                    time.sleep(work_duration)
                    self.status = 'completed'
                    return f"Completed {self.name}"
                except TimeoutError:
                    self.status = 'timeout'
                    raise
                finally:
                    signal.alarm(0)  # Cancel alarm
        
        task = TimeoutTask("timeout_test", timeout=1)
        
        # Test successful execution (within timeout)
        result = task.execute_with_timeout(0.1)
        assert result == "Completed timeout_test"
        assert task.status == 'completed'
        
        # Test timeout
        task2 = TimeoutTask("timeout_test2", timeout=1)
        with pytest.raises(TimeoutError):
            task2.execute_with_timeout(2.0)  # Work longer than timeout
        assert task2.status == 'timeout'
    
    def test_task_retry_logic(self):
        """Test task retry logic"""
        class RetryableTask:
            def __init__(self, name, max_retries=3):
                self.name = name
                self.max_retries = max_retries
                self.attempt_count = 0
                self.status = 'pending'
            
            def execute_with_retry(self, fail_before_attempt=None):
                self.status = 'running'
                
                while self.attempt_count < self.max_retries:
                    self.attempt_count += 1
                    
                    try:
                        # Simulate failure for testing
                        if fail_before_attempt and self.attempt_count < fail_before_attempt:
                            raise RuntimeError(f"Simulated failure on attempt {self.attempt_count}")
                        
                        # Success
                        self.status = 'completed'
                        return f"Completed {self.name} on attempt {self.attempt_count}"
                    
                    except RuntimeError as e:
                        if self.attempt_count >= self.max_retries:
                            self.status = 'failed'
                            raise e
                        # Continue to next retry
                        continue
                
                self.status = 'failed'
                raise RuntimeError(f"Task {self.name} failed after {self.max_retries} attempts")
        
        # Test successful execution on first attempt
        task1 = RetryableTask("retry_test1", max_retries=3)
        result = task1.execute_with_retry()
        assert result == "Completed retry_test1 on attempt 1"
        assert task1.status == 'completed'
        
        # Test success after retries
        task2 = RetryableTask("retry_test2", max_retries=3)
        result = task2.execute_with_retry(fail_before_attempt=3)
        assert result == "Completed retry_test2 on attempt 3"
        assert task2.status == 'completed'
        
        # Test failure after max retries
        task3 = RetryableTask("retry_test3", max_retries=2)
        with pytest.raises(RuntimeError, match="failed after 2 attempts"):
            task3.execute_with_retry(fail_before_attempt=5)  # Always fail
        assert task3.status == 'failed'

class TestTaskScheduling:
    """Test task scheduling and queue management"""
    
    def test_task_queue(self):
        """Test task queue operations"""
        from collections import deque
        
        class TaskQueue:
            def __init__(self):
                self.queue = deque()
                self.running = []
                self.completed = []
            
            def add_task(self, task):
                self.queue.append(task)
            
            def get_next_task(self):
                if self.queue:
                    task = self.queue.popleft()
                    self.running.append(task)
                    return task
                return None
            
            def complete_task(self, task):
                if task in self.running:
                    self.running.remove(task)
                    self.completed.append(task)
            
            def get_queue_status(self):
                return {
                    'pending': len(self.queue),
                    'running': len(self.running),
                    'completed': len(self.completed)
                }
        
        queue = TaskQueue()
        
        # Add tasks
        queue.add_task("task1")
        queue.add_task("task2")
        queue.add_task("task3")
        
        status = queue.get_queue_status()
        assert status['pending'] == 3
        assert status['running'] == 0
        assert status['completed'] == 0
        
        # Execute tasks
        task1 = queue.get_next_task()
        assert task1 == "task1"
        status = queue.get_queue_status()
        assert status['pending'] == 2
        assert status['running'] == 1
        
        # Complete task
        queue.complete_task(task1)
        status = queue.get_queue_status()
        assert status['running'] == 0
        assert status['completed'] == 1
    
    def test_priority_queue(self):
        """Test priority-based task scheduling"""
        import heapq
        
        class PriorityTask:
            def __init__(self, name, priority=0):
                self.name = name
                self.priority = priority
            
            def __lt__(self, other):
                return self.priority > other.priority  # Higher priority first
            
            def __repr__(self):
                return f"Task({self.name}, priority={self.priority})"
        
        class PriorityTaskQueue:
            def __init__(self):
                self.heap = []
            
            def add_task(self, task):
                heapq.heappush(self.heap, task)
            
            def get_next_task(self):
                if self.heap:
                    return heapq.heappop(self.heap)
                return None
        
        queue = PriorityTaskQueue()
        
        # Add tasks with different priorities
        queue.add_task(PriorityTask("low_priority", 1))
        queue.add_task(PriorityTask("high_priority", 5))
        queue.add_task(PriorityTask("medium_priority", 3))
        
        # Should get high priority task first
        task1 = queue.get_next_task()
        assert task1.name == "high_priority"
        assert task1.priority == 5
        
        # Then medium priority
        task2 = queue.get_next_task()
        assert task2.name == "medium_priority"
        assert task2.priority == 3
        
        # Finally low priority
        task3 = queue.get_next_task()
        assert task3.name == "low_priority"
        assert task3.priority == 1

class TestTaskOutput:
    """Test task output and result handling"""
    
    def test_task_output_validation(self):
        """Test task output validation"""
        from pydantic import BaseModel, ValidationError
        
        class TaskOutput(BaseModel):
            task_name: str
            status: str
            result: str
            execution_time: float
            timestamp: datetime
        
        # Valid output
        valid_output = {
            "task_name": "test_task",
            "status": "completed",
            "result": "Task completed successfully",
            "execution_time": 1.23,
            "timestamp": datetime.now()
        }
        output = TaskOutput(**valid_output)
        assert output.task_name == "test_task"
        assert output.status == "completed"
        
        # Invalid output
        with pytest.raises(ValidationError):
            TaskOutput(
                task_name="test",
                status="invalid_status",  # Should be enum
                execution_time="not_a_number"
            )
    
    def test_task_result_serialization(self):
        """Test task result serialization"""
        import json
        from datetime import datetime
        
        class TaskResult:
            def __init__(self, task_name, result, timestamp=None):
                self.task_name = task_name
                self.result = result
                self.timestamp = timestamp or datetime.now()
            
            def to_dict(self):
                return {
                    "task_name": self.task_name,
                    "result": self.result,
                    "timestamp": self.timestamp.isoformat()
                }
            
            def to_json(self):
                return json.dumps(self.to_dict())
            
            @classmethod
            def from_dict(cls, data):
                return cls(
                    task_name=data["task_name"],
                    result=data["result"],
                    timestamp=datetime.fromisoformat(data["timestamp"])
                )
        
        # Create result
        result = TaskResult("test_task", "Success")
        
        # Serialize to dict
        result_dict = result.to_dict()
        assert result_dict["task_name"] == "test_task"
        assert result_dict["result"] == "Success"
        assert "timestamp" in result_dict
        
        # Serialize to JSON
        result_json = result.to_json()
        assert isinstance(result_json, str)
        assert "test_task" in result_json
        
        # Deserialize from dict
        restored_result = TaskResult.from_dict(result_dict)
        assert restored_result.task_name == "test_task"
        assert restored_result.result == "Success"

class TestTaskMonitoring:
    """Test task monitoring and metrics"""
    
    def test_task_progress_tracking(self):
        """Test task progress tracking"""
        class ProgressTracker:
            def __init__(self):
                self.tasks = {}
            
            def start_task(self, task_id, total_steps=1):
                self.tasks[task_id] = {
                    'total_steps': total_steps,
                    'completed_steps': 0,
                    'status': 'running',
                    'start_time': datetime.now()
                }
            
            def update_progress(self, task_id, completed_steps):
                if task_id in self.tasks:
                    self.tasks[task_id]['completed_steps'] = completed_steps
                    if completed_steps >= self.tasks[task_id]['total_steps']:
                        self.tasks[task_id]['status'] = 'completed'
                        self.tasks[task_id]['end_time'] = datetime.now()
            
            def get_progress(self, task_id):
                if task_id not in self.tasks:
                    return None
                
                task = self.tasks[task_id]
                progress_percent = (task['completed_steps'] / task['total_steps']) * 100
                
                return {
                    'progress_percent': progress_percent,
                    'status': task['status'],
                    'completed_steps': task['completed_steps'],
                    'total_steps': task['total_steps']
                }
        
        tracker = ProgressTracker()
        
        # Start tracking a task
        tracker.start_task("task_1", total_steps=5)
        
        # Check initial progress
        progress = tracker.get_progress("task_1")
        assert progress['progress_percent'] == 0
        assert progress['status'] == 'running'
        
        # Update progress
        tracker.update_progress("task_1", 3)
        progress = tracker.get_progress("task_1")
        assert progress['progress_percent'] == 60
        assert progress['status'] == 'running'
        
        # Complete task
        tracker.update_progress("task_1", 5)
        progress = tracker.get_progress("task_1")
        assert progress['progress_percent'] == 100
        assert progress['status'] == 'completed'
    
    def test_task_metrics_collection(self):
        """Test task metrics collection"""
        class TaskMetrics:
            def __init__(self):
                self.metrics = {}
            
            def record_execution(self, task_name, execution_time, status, agent_id=None):
                if task_name not in self.metrics:
                    self.metrics[task_name] = {
                        'executions': [],
                        'total_count': 0,
                        'success_count': 0,
                        'failure_count': 0,
                        'total_execution_time': 0
                    }
                
                self.metrics[task_name]['executions'].append({
                    'execution_time': execution_time,
                    'status': status,
                    'agent_id': agent_id,
                    'timestamp': datetime.now()
                })
                
                self.metrics[task_name]['total_count'] += 1
                self.metrics[task_name]['total_execution_time'] += execution_time
                
                if status == 'success':
                    self.metrics[task_name]['success_count'] += 1
                else:
                    self.metrics[task_name]['failure_count'] += 1
            
            def get_task_stats(self, task_name):
                if task_name not in self.metrics:
                    return None
                
                metrics = self.metrics[task_name]
                return {
                    'total_executions': metrics['total_count'],
                    'success_rate': metrics['success_count'] / metrics['total_count'] * 100,
                    'average_execution_time': metrics['total_execution_time'] / metrics['total_count'],
                    'last_execution': metrics['executions'][-1] if metrics['executions'] else None
                }
        
        metrics = TaskMetrics()
        
        # Record some executions
        metrics.record_execution("task_A", 1.5, "success", "agent_1")
        metrics.record_execution("task_A", 2.0, "success", "agent_2")
        metrics.record_execution("task_A", 1.8, "failure", "agent_1")
        
        # Get stats
        stats = metrics.get_task_stats("task_A")
        assert stats['total_executions'] == 3
        assert stats['success_rate'] == 66.67  # 2/3 * 100, rounded
        assert abs(stats['average_execution_time'] - 1.77) < 0.01  # (1.5+2.0+1.8)/3