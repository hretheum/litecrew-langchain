"""
Parallel Execution system for advanced orchestration.
"""

import asyncio
import concurrent.futures
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from litecrew.agent import Agent as LiteAgent
from litecrew.task import LiteTask, TaskOutput


class ExecutionMode(Enum):
    """Execution modes for tasks."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ASYNC = "async"


@dataclass
class ParallelTask:
    """A task that can be executed in parallel."""
    
    id: str
    task: LiteTask
    agent: LiteAgent
    dependencies: Set[str] = field(default_factory=set)
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    priority: int = 0
    timeout: Optional[float] = None
    
    # Execution state
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[TaskOutput] = None
    error: Optional[Exception] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def is_ready(self, completed_tasks: Set[str]) -> bool:
        """Check if task is ready to execute."""
        return self.dependencies.issubset(completed_tasks)
    
    def execution_time(self) -> Optional[float]:
        """Get execution time in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


@dataclass
class ExecutionGroup:
    """A group of tasks that can execute in parallel."""
    
    id: str
    tasks: List[ParallelTask] = field(default_factory=list)
    mode: ExecutionMode = ExecutionMode.PARALLEL
    max_concurrent: int = 5
    
    def add_task(self, task: ParallelTask) -> None:
        """Add a task to the group."""
        self.tasks.append(task)
    
    def get_ready_tasks(self, completed_tasks: Set[str]) -> List[ParallelTask]:
        """Get tasks ready for execution."""
        return [
            task for task in self.tasks
            if task.status == "pending" and task.is_ready(completed_tasks)
        ]


class ParallelExecutor:
    """Executor for parallel task execution."""
    
    def __init__(
        self,
        max_workers: int = 5,
        enable_async: bool = True,
        timeout: float = 300.0
    ):
        """Initialize parallel executor.
        
        Args:
            max_workers: Maximum number of worker threads
            enable_async: Enable async/await support
            timeout: Default timeout for tasks
        """
        self.max_workers = max_workers
        self.enable_async = enable_async
        self.timeout = timeout
        
        # Thread pool for parallel execution
        self._thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers
        )
        
        # Async event loop (created when needed)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Execution metrics
        self._metrics = {
            "total_tasks": 0,
            "parallel_groups": 0,
            "async_tasks": 0,
            "execution_times": [],
            "speedup_ratios": []
        }
    
    def execute_tasks(
        self,
        tasks: List[ParallelTask],
        mode: ExecutionMode = ExecutionMode.PARALLEL
    ) -> Dict[str, TaskOutput]:
        """Execute a list of tasks.
        
        Args:
            tasks: Tasks to execute
            mode: Execution mode
            
        Returns:
            Dict mapping task ID to output
        """
        start_time = time.perf_counter()
        results = {}
        
        if mode == ExecutionMode.SEQUENTIAL:
            results = self._execute_sequential(tasks)
        elif mode == ExecutionMode.PARALLEL:
            results = self._execute_parallel(tasks)
        elif mode == ExecutionMode.ASYNC and self.enable_async:
            results = self._execute_async(tasks)
        else:
            # Fallback to parallel
            results = self._execute_parallel(tasks)
        
        # Calculate metrics
        execution_time = time.perf_counter() - start_time
        self._metrics["execution_times"].append(execution_time)
        self._metrics["total_tasks"] += len(tasks)
        
        # Calculate speedup
        if len(tasks) > 1:
            sequential_time = sum(t.execution_time() or 0 for t in tasks)
            if sequential_time > 0:
                speedup = sequential_time / execution_time
                self._metrics["speedup_ratios"].append(speedup)
        
        return results
    
    def _execute_sequential(self, tasks: List[ParallelTask]) -> Dict[str, TaskOutput]:
        """Execute tasks sequentially."""
        results = {}
        completed = set()
        
        while True:
            # Find next ready task
            ready_task = None
            for task in tasks:
                if task.status == "pending" and task.is_ready(completed):
                    ready_task = task
                    break
            
            if not ready_task:
                break
            
            # Execute task
            result = self._execute_single_task(ready_task)
            results[ready_task.id] = result
            completed.add(ready_task.id)
        
        return results
    
    def _execute_parallel(self, tasks: List[ParallelTask]) -> Dict[str, TaskOutput]:
        """Execute tasks in parallel using thread pool."""
        self._metrics["parallel_groups"] += 1
        
        results = {}
        completed = set()
        futures = {}
        
        while True:
            # Submit ready tasks
            ready_tasks = [
                task for task in tasks
                if task.status == "pending" and task.is_ready(completed)
            ]
            
            if not ready_tasks and not futures:
                break
            
            # Submit new tasks (up to max_workers)
            for task in ready_tasks[:self.max_workers - len(futures)]:
                task.status = "running"
                future = self._thread_pool.submit(self._execute_single_task, task)
                futures[future] = task
            
            # Wait for any task to complete
            if futures:
                done, pending = concurrent.futures.wait(
                    futures.keys(),
                    timeout=1.0,
                    return_when=concurrent.futures.FIRST_COMPLETED
                )
                
                for future in done:
                    task = futures.pop(future)
                    try:
                        result = future.result()
                        results[task.id] = result
                        completed.add(task.id)
                    except Exception as e:
                        task.error = e
                        task.status = "failed"
                        results[task.id] = None
        
        return results
    
    def _execute_async(self, tasks: List[ParallelTask]) -> Dict[str, TaskOutput]:
        """Execute tasks asynchronously."""
        self._metrics["async_tasks"] += len(tasks)
        
        # Create event loop if needed
        if not self._loop:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        
        # Run async execution
        return self._loop.run_until_complete(self._execute_async_tasks(tasks))
    
    async def _execute_async_tasks(self, tasks: List[ParallelTask]) -> Dict[str, TaskOutput]:
        """Execute tasks asynchronously (internal)."""
        results = {}
        completed = set()
        
        while True:
            # Find ready tasks
            ready_tasks = [
                task for task in tasks
                if task.status == "pending" and task.is_ready(completed)
            ]
            
            if not ready_tasks:
                break
            
            # Create async tasks
            async_tasks = []
            for task in ready_tasks:
                task.status = "running"
                async_tasks.append(self._execute_task_async(task))
            
            # Execute concurrently
            task_results = await asyncio.gather(*async_tasks, return_exceptions=True)
            
            # Process results
            for task, result in zip(ready_tasks, task_results):
                if isinstance(result, Exception):
                    task.error = result
                    task.status = "failed"
                    results[task.id] = None
                else:
                    results[task.id] = result
                    completed.add(task.id)
        
        return results
    
    async def _execute_task_async(self, task: ParallelTask) -> TaskOutput:
        """Execute a single task asynchronously."""
        # Wrap synchronous execution in async
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._thread_pool,
            self._execute_single_task,
            task
        )
    
    def _execute_single_task(self, task: ParallelTask) -> TaskOutput:
        """Execute a single task."""
        task.start_time = time.perf_counter()
        
        try:
            # Execute with timeout if specified
            if task.timeout:
                future = self._thread_pool.submit(
                    task.agent.execute_task,
                    task.task,
                    ""
                )
                result = future.result(timeout=task.timeout)
            else:
                result = task.agent.execute_task(task.task, "")
            
            task.status = "completed"
            task.result = result
            task.end_time = time.perf_counter()
            
            return result
            
        except Exception as e:
            task.status = "failed"
            task.error = e
            task.end_time = time.perf_counter()
            raise
    
    def execute_groups(
        self,
        groups: List[ExecutionGroup]
    ) -> Dict[str, Dict[str, TaskOutput]]:
        """Execute multiple groups of tasks.
        
        Args:
            groups: Execution groups
            
        Returns:
            Dict mapping group ID to task results
        """
        all_results = {}
        
        for group in groups:
            # Execute group based on its mode
            group_results = self.execute_tasks(group.tasks, group.mode)
            all_results[group.id] = group_results
        
        return all_results
    
    def shutdown(self) -> None:
        """Shutdown the executor."""
        self._thread_pool.shutdown(wait=True)
        if self._loop:
            self._loop.close()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics."""
        metrics = self._metrics.copy()
        
        if metrics["execution_times"]:
            metrics["avg_execution_time"] = sum(metrics["execution_times"]) / len(metrics["execution_times"])
            metrics["max_execution_time"] = max(metrics["execution_times"])
            metrics["min_execution_time"] = min(metrics["execution_times"])
        
        if metrics["speedup_ratios"]:
            metrics["avg_speedup"] = sum(metrics["speedup_ratios"]) / len(metrics["speedup_ratios"])
            metrics["max_speedup"] = max(metrics["speedup_ratios"])
        
        return metrics


class DependencyResolver:
    """Resolves task dependencies for optimal parallel execution."""
    
    @staticmethod
    def create_execution_groups(
        tasks: List[ParallelTask]
    ) -> List[ExecutionGroup]:
        """Create execution groups from tasks based on dependencies.
        
        Args:
            tasks: List of tasks with dependencies
            
        Returns:
            List of execution groups
        """
        groups = []
        task_map = {task.id: task for task in tasks}
        completed = set()
        group_counter = 0
        
        while len(completed) < len(tasks):
            # Find all tasks ready to execute
            ready_tasks = [
                task for task in tasks
                if task.id not in completed and task.is_ready(completed)
            ]
            
            if not ready_tasks:
                # Circular dependency or error
                break
            
            # Create group for ready tasks
            group = ExecutionGroup(
                id=f"group_{group_counter}",
                mode=ExecutionMode.PARALLEL
            )
            
            for task in ready_tasks:
                group.add_task(task)
                completed.add(task.id)
            
            groups.append(group)
            group_counter += 1
        
        return groups
    
    @staticmethod
    def optimize_groups(
        groups: List[ExecutionGroup],
        max_concurrent: int = 5
    ) -> List[ExecutionGroup]:
        """Optimize groups for better parallelism.
        
        Args:
            groups: Execution groups
            max_concurrent: Max concurrent tasks per group
            
        Returns:
            Optimized groups
        """
        optimized = []
        
        for group in groups:
            if len(group.tasks) <= max_concurrent:
                # Group is small enough
                optimized.append(group)
            else:
                # Split large group
                for i in range(0, len(group.tasks), max_concurrent):
                    sub_group = ExecutionGroup(
                        id=f"{group.id}_sub_{i // max_concurrent}",
                        mode=group.mode,
                        max_concurrent=max_concurrent
                    )
                    sub_group.tasks = group.tasks[i:i + max_concurrent]
                    optimized.append(sub_group)
        
        return optimized


class ParallelOrchestrator:
    """High-level orchestrator for parallel execution."""
    
    def __init__(
        self,
        executor: Optional[ParallelExecutor] = None,
        auto_optimize: bool = True
    ):
        """Initialize orchestrator.
        
        Args:
            executor: Parallel executor (creates default if None)
            auto_optimize: Automatically optimize execution groups
        """
        self.executor = executor or ParallelExecutor()
        self.auto_optimize = auto_optimize
    
    def execute_workflow(
        self,
        tasks: List[ParallelTask],
        optimize: Optional[bool] = None
    ) -> Dict[str, TaskOutput]:
        """Execute a workflow of tasks with automatic parallelization.
        
        Args:
            tasks: Tasks to execute
            optimize: Override auto_optimize setting
            
        Returns:
            Task results
        """
        # Create execution groups
        groups = DependencyResolver.create_execution_groups(tasks)
        
        # Optimize if requested
        if optimize or (optimize is None and self.auto_optimize):
            groups = DependencyResolver.optimize_groups(
                groups,
                max_concurrent=self.executor.max_workers
            )
        
        # Execute groups
        all_results = self.executor.execute_groups(groups)
        
        # Flatten results
        results = {}
        for group_results in all_results.values():
            results.update(group_results)
        
        return results
    
    def shutdown(self) -> None:
        """Shutdown the orchestrator."""
        self.executor.shutdown()