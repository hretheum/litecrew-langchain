# validate_task_execution.py
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from litecrewai.task import Task, TaskExecutor

def test_basic_task():
    """Test basic task execution"""
    task = Task("Calculate 2+2")
    executor = TaskExecutor()
    
    start = time.time()
    result = executor.run_single(task)
    execution_time = time.time() - start
    
    print(f"Task executed in {execution_time:.2f}s")
    assert result.status == "completed"
    assert execution_time < 10
    
    return result

def test_dependencies():
    """Test task dependency resolution"""
    # Create dependent tasks
    task1 = Task("Step 1", id="task1")
    task2 = Task("Step 2", dependencies=["task1"])
    task3 = Task("Step 3", dependencies=["task1", "task2"])
    
    executor = TaskExecutor()
    
    # Test dependency resolution
    start = time.time()
    order = executor.resolve_dependencies([task3, task1, task2])
    resolution_time = time.time() - start
    
    print(f"Dependency resolution: {resolution_time*1000:.1f}ms")
    assert resolution_time < 0.1
    assert [t.id for t in order] == ["task1", "task2", "task3"]
    
    # Execute all
    results = executor.run(order)
    assert all(r.status == "completed" for r in results)

def test_parallel_execution():
    """Test parallel task execution"""
    # Create independent tasks
    tasks = [Task(f"Parallel task {i}") for i in range(5)]
    
    executor = TaskExecutor(max_workers=3)
    
    start = time.time()
    results = executor.run(tasks)
    total_time = time.time() - start
    
    # Should be faster than sequential
    print(f"Parallel execution time: {total_time:.2f}s")
    assert total_time < len(tasks) * 2  # Assuming each task ~2s
    assert all(r.status == "completed" for r in results)

def test_error_handling():
    """Test error recovery"""
    # Create task that will fail
    fail_task = Task("This will fail", will_fail=True)
    
    executor = TaskExecutor()
    result = executor.run_single(fail_task)
    
    assert result.status == "failed"
    assert result.error is not None
    assert result.retry_count > 0
    
    print(f"Task failed after {result.retry_count} retries")

def test_thread_safety():
    """Test concurrent task submission"""
    executor = TaskExecutor()
    results = []
    
    def submit_tasks():
        for i in range(10):
            task = Task(f"Concurrent task {i}")
            result = executor.run_single(task)
            results.append(result)
    
    # Run from multiple threads
    threads = []
    for _ in range(3):
        t = threading.Thread(target=submit_tasks)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # Check all completed
    assert len(results) == 30
    assert all(r.status == "completed" for r in results)
    print("✅ Thread safety verified")

def test_progress_tracking():
    """Test progress monitoring"""
    tasks = [Task(f"Progress task {i}") for i in range(10)]
    executor = TaskExecutor()
    
    progress_updates = []
    
    def progress_callback(completed, total):
        progress_updates.append((completed, total))
    
    executor.run(tasks, progress_callback=progress_callback)
    
    # Should have progress updates
    assert len(progress_updates) > 0
    assert progress_updates[-1] == (10, 10)
    print(f"Progress updates: {len(progress_updates)}")

if __name__ == "__main__":
    print("🔍 Validating task execution engine...\n")
    
    # Basic execution
    test_basic_task()
    print("✅ Basic task execution validated")
    
    # Dependencies
    test_dependencies()
    print("✅ Dependency resolution validated")
    
    # Parallel execution
    test_parallel_execution()
    print("✅ Parallel execution validated")
    
    # Error handling
    test_error_handling()
    print("✅ Error handling validated")
    
    # Thread safety
    test_thread_safety()
    
    # Progress tracking
    test_progress_tracking()
    print("✅ Progress tracking validated")
    
    print("\n✅ Task execution validation complete!")