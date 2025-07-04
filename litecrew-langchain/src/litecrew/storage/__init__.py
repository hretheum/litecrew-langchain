"""
Storage layer for LiteCrew - handles persistence, caching, and state management.
"""

from litecrew.storage.base import StorageBackend, StorageError
from litecrew.storage.sqlite import SQLiteStorage
from litecrew.storage.cache import RedisCache, MemoryCache
from litecrew.storage.manager import StorageManager
from litecrew.storage.versioning import ResultVersion
from litecrew.storage.compression import CompressionType, Compressor

__all__ = [
    "StorageBackend",
    "StorageError",
    "SQLiteStorage",
    "RedisCache",
    "MemoryCache",
    "StorageManager",
    "ResultVersion",
    "CompressionType",
    "Compressor",
]
