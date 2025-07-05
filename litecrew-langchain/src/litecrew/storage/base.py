"""
Base classes for storage backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class StorageError(Exception):
    """Base exception for storage errors."""

    pass


@dataclass
class StorageMetrics:
    """Storage performance metrics."""

    total_writes: int = 0
    total_reads: int = 0
    total_size_bytes: int = 0
    average_write_time_ms: float = 0.0
    average_read_time_ms: float = 0.0
    compression_ratio: float = 1.0


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def read(self, key: str, version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Read data by key."""
        pass

    @abstractmethod
    def write(self, key: str, data: Dict[str, Any], compress: bool = False) -> None:
        """Write data with key."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete data by key."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """List all keys, optionally filtered by pattern."""
        pass

    @abstractmethod
    def get_size(self, key: str) -> int:
        """Get size of stored data in bytes."""
        pass

    def read_batch(self, keys: List[str]) -> Dict[str, Any]:
        """Read multiple keys at once."""
        return {key: self.read(key) for key in keys if self.exists(key)}

    def write_batch(self, items: Dict[str, Any]) -> None:
        """Write multiple items at once."""
        for key, data in items.items():
            self.write(key, data)

    def search(self, pattern: str) -> List[Dict[str, Any]]:
        """Search for keys matching pattern."""
        keys = self.list_keys(pattern)
        return [result for result in (self.read(key) for key in keys) if result is not None]

    @abstractmethod
    def get_metrics(self) -> StorageMetrics:
        """Get storage metrics."""
        pass
