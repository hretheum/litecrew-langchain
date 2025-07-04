"""
Unified storage manager that coordinates backend and cache.
"""

import asyncio
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor

from litecrew.storage.base import StorageBackend, StorageError
from litecrew.storage.sqlite import SQLiteStorage
from litecrew.storage.cache import RedisCache, MemoryCache
from litecrew.storage.compression import Compressor, CompressionType
from litecrew.storage.versioning import ResultVersion


class StorageManager:
    """Manages storage operations with caching and compression."""

    def __init__(
        self,
        backend: str = "sqlite",
        cache_enabled: bool = True,
        cache_type: str = "memory",
        db_path: Optional[Path] = None,
        compression_threshold: int = 1024,
        compression_type: CompressionType = CompressionType.ZLIB,
        cache_ttl: int = 3600,
        max_cache_size: int = 1000,
    ):
        """
        Initialize storage manager.

        Args:
            backend: Storage backend type ("sqlite")
            cache_enabled: Enable caching layer
            cache_type: Cache type ("memory" or "redis")
            db_path: Path to database file (for SQLite)
            compression_threshold: Auto-compress data larger than this (bytes)
            compression_type: Type of compression to use
            cache_ttl: Default cache TTL in seconds
            max_cache_size: Maximum cache entries
        """
        self.cache_enabled = cache_enabled
        self.compression_threshold = compression_threshold
        self.compression_type = compression_type
        self.cache_ttl = cache_ttl

        # Initialize backend
        if backend == "sqlite":
            if db_path is None:
                db_path = Path("litecrew_storage.db")
            self._storage = SQLiteStorage(db_path)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

        # Initialize cache
        if cache_enabled:
            if cache_type == "redis":
                self._cache = RedisCache()
            else:
                self._cache = MemoryCache(max_size=max_cache_size)
        else:
            self._cache = None

        # Thread pool for async operations
        self._executor = ThreadPoolExecutor(max_workers=4)

    def store_result(self, result: Dict[str, Any], key: Optional[str] = None) -> str:
        """
        Store execution result.

        Args:
            result: Result data to store
            key: Optional key (generated if not provided)

        Returns:
            Result ID/key
        """
        if key is None:
            key = self._generate_key(result)

        # Add metadata
        result_with_metadata = {**result, "_stored_at": time.time(), "_id": key}

        # Check if compression needed
        compress = len(str(result)) > self.compression_threshold

        # Store in backend
        self._storage.write(key, result_with_metadata, compress=compress)

        # Update cache
        if self._cache:
            self._cache.set(key, result_with_metadata, ttl=self.cache_ttl)

        return key

    def get_result(
        self, key: str, version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve result by key.

        Args:
            key: Result key
            version: Optional version number

        Returns:
            Result data or None if not found
        """
        # Check cache first (only for latest version)
        if self._cache and version is None:
            cached = self._cache.get(key)
            if cached is not None:
                return cached

        # Read from storage
        result = self._storage.read(key, version=version)

        # Update cache
        if result and self._cache and version is None:
            self._cache.set(key, result, ttl=self.cache_ttl)

        return result

    def delete_result(self, key: str) -> None:
        """Delete result and all its versions."""
        self._storage.delete(key)

        if self._cache:
            self._cache.delete(key)

    def list_results(self, pattern: Optional[str] = None) -> List[str]:
        """List all result keys."""
        return self._storage.list_keys(pattern)

    def get_versions(self, key: str) -> List[Dict[str, Any]]:
        """Get all versions of a result."""
        return self._storage.list_versions(key)

    async def astore_result(
        self, result: Dict[str, Any], key: Optional[str] = None
    ) -> str:
        """Async version of store_result."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor, self.store_result, result, key
        )

    async def aget_result(
        self, key: str, version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Async version of get_result."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self.get_result, key, version)

    def get_metrics(self) -> Dict[str, Any]:
        """Get storage metrics."""
        storage_metrics = self._storage.get_metrics()

        metrics = {
            "total_stored": len(self._storage.list_keys()),
            "total_size_mb": storage_metrics.total_size_bytes / (1024 * 1024),
            "average_write_time_ms": storage_metrics.average_write_time_ms,
            "average_read_time_ms": storage_metrics.average_read_time_ms,
            "compression_ratio": storage_metrics.compression_ratio,
        }

        if self._cache:
            cache_stats = self._cache.get_stats()
            metrics["cache_hit_rate"] = cache_stats["hit_rate"]
            metrics["cache_size"] = cache_stats.get("size", 0)

        return metrics

    def _generate_key(self, result: Dict[str, Any]) -> str:
        """Generate unique key for result."""
        # Use combination of identifiers if available
        if "crew_id" in result and "task_id" in result:
            return f"{result['crew_id']}_{result['task_id']}_{int(time.time())}"
        elif "agent" in result and "task" in result:
            return f"{result['agent']}_{result['task']}_{int(time.time())}"
        else:
            return f"result_{uuid.uuid4().hex[:8]}_{int(time.time())}"

    def clear_cache(self) -> None:
        """Clear all cached entries."""
        if self._cache:
            self._cache.clear()

    def close(self) -> None:
        """Close storage manager and cleanup resources."""
        self._executor.shutdown(wait=True)
