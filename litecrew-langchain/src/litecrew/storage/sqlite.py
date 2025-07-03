"""
SQLite storage backend implementation.
"""

import sqlite3
import json
import time
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager

from litecrew.storage.base import StorageBackend, StorageError, StorageMetrics


class SQLiteStorage(StorageBackend):
    """SQLite-based storage backend with versioning support."""
    
    def __init__(self, db_path: Path):
        """
        Initialize SQLite storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._metrics = StorageMetrics()
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS storage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    data TEXT NOT NULL,
                    compressed BOOLEAN DEFAULT FALSE,
                    version INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    size_bytes INTEGER,
                    metadata TEXT,
                    UNIQUE(key, version)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_key ON storage(key)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON storage(created_at)
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS storage_metadata (
                    key TEXT PRIMARY KEY,
                    latest_version INTEGER DEFAULT 1,
                    total_versions INTEGER DEFAULT 1,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(
            str(self.db_path),
            isolation_level=None,  # Autocommit mode
            timeout=30.0
        )
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def read(self, key: str, version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Read data by key and optional version."""
        start_time = time.perf_counter()
        
        try:
            with self._get_connection() as conn:
                if version is None:
                    # Get latest version
                    cursor = conn.execute(
                        "SELECT data, compressed FROM storage WHERE key = ? ORDER BY version DESC LIMIT 1",
                        (key,)
                    )
                else:
                    # Get specific version
                    cursor = conn.execute(
                        "SELECT data, compressed FROM storage WHERE key = ? AND version = ?",
                        (key, version)
                    )
                
                row = cursor.fetchone()
                if row is None:
                    return None
                
                # Decompress if needed
                data = row["data"]
                if row["compressed"]:
                    data = zlib.decompress(data.encode("latin-1")).decode("utf-8")
                
                result = json.loads(data)
                
                # Update metrics
                self._metrics.total_reads += 1
                read_time = (time.perf_counter() - start_time) * 1000
                self._metrics.average_read_time_ms = (
                    (self._metrics.average_read_time_ms * (self._metrics.total_reads - 1) + read_time) 
                    / self._metrics.total_reads
                )
                
                return result
                
        except Exception as e:
            raise StorageError(f"Failed to read key '{key}': {str(e)}")
    
    def write(self, key: str, data: Dict[str, Any], compress: bool = False) -> None:
        """Write data with key."""
        start_time = time.perf_counter()
        
        try:
            # Serialize data
            json_data = json.dumps(data)
            size_bytes = len(json_data.encode("utf-8"))
            
            # Compress if requested or if data is large
            if compress or size_bytes > 1024:  # Auto-compress if >1KB
                compressed_data = zlib.compress(json_data.encode("utf-8"))
                if len(compressed_data) < size_bytes:
                    json_data = compressed_data.decode("latin-1")
                    compress = True
                    size_bytes = len(compressed_data)
                else:
                    compress = False
            
            with self._get_connection() as conn:
                # Get current version
                cursor = conn.execute(
                    "SELECT latest_version FROM storage_metadata WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                
                if row is None:
                    version = 1
                    conn.execute(
                        "INSERT INTO storage_metadata (key, latest_version, total_versions) VALUES (?, ?, ?)",
                        (key, 1, 1)
                    )
                else:
                    version = row["latest_version"] + 1
                    conn.execute(
                        "UPDATE storage_metadata SET latest_version = ?, total_versions = total_versions + 1, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
                        (version, key)
                    )
                
                # Insert new version
                conn.execute(
                    "INSERT INTO storage (key, data, compressed, version, size_bytes) VALUES (?, ?, ?, ?, ?)",
                    (key, json_data, compress, version, size_bytes)
                )
                
                # Update metrics
                self._metrics.total_writes += 1
                self._metrics.total_size_bytes += size_bytes
                write_time = (time.perf_counter() - start_time) * 1000
                self._metrics.average_write_time_ms = (
                    (self._metrics.average_write_time_ms * (self._metrics.total_writes - 1) + write_time) 
                    / self._metrics.total_writes
                )
                
                if compress:
                    original_size = len(json.dumps(data).encode("utf-8"))
                    self._metrics.compression_ratio = (
                        self._metrics.compression_ratio * 0.9 + (size_bytes / original_size) * 0.1
                    )
                
        except Exception as e:
            raise StorageError(f"Failed to write key '{key}': {str(e)}")
    
    def delete(self, key: str) -> None:
        """Delete all versions of a key."""
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM storage WHERE key = ?", (key,))
                conn.execute("DELETE FROM storage_metadata WHERE key = ?", (key,))
        except Exception as e:
            raise StorageError(f"Failed to delete key '{key}': {str(e)}")
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM storage WHERE key = ? LIMIT 1",
                    (key,)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            raise StorageError(f"Failed to check existence of key '{key}': {str(e)}")
    
    def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """List all keys, optionally filtered by pattern."""
        try:
            with self._get_connection() as conn:
                if pattern:
                    # Convert glob pattern to SQL LIKE pattern
                    sql_pattern = pattern.replace("*", "%").replace("?", "_")
                    cursor = conn.execute(
                        "SELECT DISTINCT key FROM storage WHERE key LIKE ? ORDER BY key",
                        (sql_pattern,)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT DISTINCT key FROM storage ORDER BY key"
                    )
                
                return [row["key"] for row in cursor]
        except Exception as e:
            raise StorageError(f"Failed to list keys: {str(e)}")
    
    def get_size(self, key: str) -> int:
        """Get size of stored data in bytes."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT SUM(size_bytes) as total_size FROM storage WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                return row["total_size"] if row and row["total_size"] else 0
        except Exception as e:
            raise StorageError(f"Failed to get size of key '{key}': {str(e)}")
    
    def list_versions(self, key: str) -> List[Dict[str, Any]]:
        """List all versions of a key."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT version, created_at, size_bytes, compressed FROM storage WHERE key = ? ORDER BY version",
                    (key,)
                )
                
                return [
                    {
                        "version": row["version"],
                        "created_at": row["created_at"],
                        "size_bytes": row["size_bytes"],
                        "compressed": bool(row["compressed"])
                    }
                    for row in cursor
                ]
        except Exception as e:
            raise StorageError(f"Failed to list versions of key '{key}': {str(e)}")
    
    def search_by_metadata(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search by metadata criteria (not implemented in SQLite backend)."""
        # This would require parsing JSON in SQL, which is inefficient
        # For advanced search, use a different backend
        raise NotImplementedError("Metadata search not supported in SQLite backend")
    
    def get_metrics(self) -> StorageMetrics:
        """Get storage metrics."""
        return self._metrics