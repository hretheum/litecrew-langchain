"""
Cache warming strategies.
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional

from litecrew.cache.multilevel import MultiLevelCache


class CacheWarmer:
    """Handles cache warming and preloading."""

    def __init__(self, cache: MultiLevelCache):
        self.cache = cache
        self._warming_tasks = []
        self._scheduler_running = False
        self._executor = ThreadPoolExecutor(max_workers=4)

    async def warm_cache(
        self, keys: List[str], compute_func: Callable[[str], Any], level: int = 2
    ) -> Dict[str, bool]:
        """
        Warm cache with computed values.

        Args:
            keys: List of keys to warm
            compute_func: Async function to compute value for key
            level: Cache level to warm (default L2)

        Returns:
            Dict of key -> success status
        """
        results = {}

        # Create tasks for all keys
        tasks = []
        for key in keys:
            task = self._warm_single_key(key, compute_func, level)
            tasks.append(task)

        # Execute concurrently
        statuses = await asyncio.gather(*tasks, return_exceptions=True)

        # Build results
        for key, status in zip(keys, statuses):
            results[key] = not isinstance(status, Exception)

        return results

    async def _warm_single_key(
        self, key: str, compute_func: Callable, level: int
    ) -> None:
        """Warm a single key."""
        try:
            # Check if already cached
            if self.cache.get(key) is not None:
                return

            # Compute value
            if asyncio.iscoroutinefunction(compute_func):
                value = await compute_func(key)
            else:
                # Run sync function in executor
                loop = asyncio.get_event_loop()
                value = await loop.run_in_executor(self._executor, compute_func, key)

            # Store in cache
            self.cache.set(key, value, level=level)

        except Exception as e:
            # Log error in production
            raise e

    def schedule_warming(
        self, warming_func: Callable[[], None], interval: int = 300
    ) -> None:
        """
        Schedule periodic cache warming.

        Args:
            warming_func: Function to execute for warming
            interval: Interval in seconds between warming runs
        """
        self._warming_tasks.append(
            {"func": warming_func, "interval": interval, "last_run": 0}
        )

    def warm_now(self, warming_func: Optional[Callable] = None) -> None:
        """
        Execute warming immediately.

        Args:
            warming_func: Specific function to run, or all scheduled if None
        """
        if warming_func:
            warming_func()
        else:
            # Run all scheduled warming tasks
            for task in self._warming_tasks:
                task["func"]()

    def start_scheduler(self) -> None:
        """Start the warming scheduler in background."""
        if self._scheduler_running:
            return

        self._scheduler_running = True

        def run_scheduler():
            while self._scheduler_running:
                current_time = time.time()
                for task in self._warming_tasks:
                    if current_time - task["last_run"] >= task["interval"]:
                        try:
                            task["func"]()
                            task["last_run"] = current_time
                        except (ValueError, RuntimeError, AttributeError) as e:
                            # Log warming failure but continue
                            import logging
                            logging.warning(f"Cache warming task failed: {e}")
                time.sleep(1)

        # Run in background thread
        self._executor.submit(run_scheduler)

    def stop_scheduler(self) -> None:
        """Stop the warming scheduler."""
        self._scheduler_running = False

    def warm_from_patterns(
        self, patterns: List[str], data_source: Callable[[str], Any]
    ) -> int:
        """
        Warm cache based on key patterns.

        Args:
            patterns: List of patterns to generate keys
            data_source: Function to get data for pattern

        Returns:
            Number of keys warmed
        """
        warmed = 0

        for pattern in patterns:
            # Generate keys from pattern
            keys = self._generate_keys_from_pattern(pattern)

            for key in keys:
                try:
                    value = data_source(key)
                    self.cache.set(key, value, level=2)
                    warmed += 1
                except (KeyError, ValueError, TypeError) as e:
                    # Skip key if warming fails
                    if self._verbose:
                        print(f"Failed to warm key {key}: {e}")
                    continue

        return warmed

    def _generate_keys_from_pattern(self, pattern: str) -> List[str]:
        """Generate keys from pattern (simplified version)."""
        # In production, this would be more sophisticated
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            # Generate some example keys
            return [f"{prefix}{i}" for i in range(10)]
        return [pattern]

    def __del__(self):
        """Cleanup resources."""
        self.stop_scheduler()
        self._executor.shutdown(wait=False)
