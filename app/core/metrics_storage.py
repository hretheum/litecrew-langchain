"""
SQLite-based metrics storage for LiteCrewAI
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import threading
from contextlib import contextmanager


class MetricsStorage:
    """Store and aggregate metrics in SQLite"""

    def __init__(self, db_path: str = "/opt/litecrewai/data/metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._init_db()

    @property
    def conn(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(
                self.db_path,
                timeout=10.0,
                isolation_level=None  # Autocommit mode
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    @contextmanager
    def transaction(self):
        """Context manager for transactions"""
        self.conn.execute("BEGIN")
        try:
            yield
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise

    def _init_db(self):
        """Initialize database schema"""
        with self.transaction():
            # Raw metrics table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    labels TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Aggregated metrics tables
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics_1min (
                    timestamp INTEGER NOT NULL,
                    metric_name TEXT NOT NULL,
                    labels TEXT,
                    count INTEGER,
                    sum REAL,
                    min REAL,
                    max REAL,
                    avg REAL,
                    PRIMARY KEY (timestamp, metric_name, labels)
                )
            """)
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics_5min (
                    timestamp INTEGER NOT NULL,
                    metric_name TEXT NOT NULL,
                    labels TEXT,
                    count INTEGER,
                    sum REAL,
                    min REAL,
                    max REAL,
                    avg REAL,
                    PRIMARY KEY (timestamp, metric_name, labels)
                )
            """)
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics_1hour (
                    timestamp INTEGER NOT NULL,
                    metric_name TEXT NOT NULL,
                    labels TEXT,
                    count INTEGER,
                    sum REAL,
                    min REAL,
                    max REAL,
                    avg REAL,
                    PRIMARY KEY (timestamp, metric_name, labels)
                )
            """)
            
            # Alerts table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    alert_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON alerts(resolved)")

    def record_metric(self, name: str, value: float, labels: Optional[Dict] = None):
        """Record a single metric"""
        timestamp = datetime.utcnow().timestamp()
        labels_json = json.dumps(labels) if labels else None
        
        self.conn.execute(
            "INSERT INTO metrics (timestamp, metric_name, metric_value, labels) VALUES (?, ?, ?, ?)",
            (timestamp, name, value, labels_json)
        )

    def record_metrics_batch(self, metrics: List[Tuple[str, float, Optional[Dict]]]):
        """Record multiple metrics in a batch"""
        timestamp = datetime.utcnow().timestamp()
        
        with self.transaction():
            for name, value, labels in metrics:
                labels_json = json.dumps(labels) if labels else None
                self.conn.execute(
                    "INSERT INTO metrics (timestamp, metric_name, metric_value, labels) VALUES (?, ?, ?, ?)",
                    (timestamp, name, value, labels_json)
                )

    def aggregate_metrics(self, interval_minutes: int = 1):
        """Aggregate raw metrics into time buckets"""
        if interval_minutes == 1:
            table = "metrics_1min"
            bucket_seconds = 60
        elif interval_minutes == 5:
            table = "metrics_5min"
            bucket_seconds = 300
        elif interval_minutes == 60:
            table = "metrics_1hour"
            bucket_seconds = 3600
        else:
            raise ValueError(f"Unsupported interval: {interval_minutes}")
        
        # Get the last aggregated timestamp
        cursor = self.conn.execute(
            f"SELECT MAX(timestamp) FROM {table}"
        )
        last_timestamp = cursor.fetchone()[0] or 0
        
        # Aggregate new metrics
        current_time = datetime.utcnow().timestamp()
        
        with self.transaction():
            cursor = self.conn.execute("""
                SELECT 
                    CAST(timestamp / ? AS INTEGER) * ? as bucket,
                    metric_name,
                    labels,
                    COUNT(*) as count,
                    SUM(metric_value) as sum,
                    MIN(metric_value) as min,
                    MAX(metric_value) as max,
                    AVG(metric_value) as avg
                FROM metrics
                WHERE timestamp > ?
                  AND timestamp < ?
                GROUP BY bucket, metric_name, labels
            """, (bucket_seconds, bucket_seconds, last_timestamp, current_time - bucket_seconds))
            
            for row in cursor:
                self.conn.execute(
                    f"""INSERT OR REPLACE INTO {table} 
                    (timestamp, metric_name, labels, count, sum, min, max, avg)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (row["bucket"], row["metric_name"], row["labels"],
                     row["count"], row["sum"], row["min"], row["max"], row["avg"])
                )

    def get_metrics(
        self, 
        metric_name: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interval: str = "raw",
        labels: Optional[Dict] = None
    ) -> List[Dict]:
        """Retrieve metrics data"""
        if interval == "raw":
            table = "metrics"
            time_col = "timestamp"
            value_col = "metric_value"
        elif interval == "1min":
            table = "metrics_1min"
            time_col = "timestamp"
            value_col = "avg"
        elif interval == "5min":
            table = "metrics_5min"
            time_col = "timestamp"
            value_col = "avg"
        elif interval == "1hour":
            table = "metrics_1hour"
            time_col = "timestamp"
            value_col = "avg"
        else:
            raise ValueError(f"Invalid interval: {interval}")
        
        # Build query
        query = f"SELECT * FROM {table} WHERE metric_name = ?"
        params = [metric_name]
        
        if start_time:
            query += f" AND {time_col} >= ?"
            params.append(start_time.timestamp())
            
        if end_time:
            query += f" AND {time_col} <= ?"
            params.append(end_time.timestamp())
            
        if labels:
            query += " AND labels = ?"
            params.append(json.dumps(labels))
            
        query += f" ORDER BY {time_col}"
        
        cursor = self.conn.execute(query, params)
        
        results = []
        for row in cursor:
            result = dict(row)
            # Convert timestamp to datetime
            result["timestamp"] = datetime.fromtimestamp(result["timestamp"])
            # Parse labels if present
            if result.get("labels"):
                result["labels"] = json.loads(result["labels"])
            results.append(result)
            
        return results

    def record_alert(
        self,
        alert_name: str,
        severity: str,
        message: str,
        metric_name: Optional[str] = None,
        metric_value: Optional[float] = None
    ):
        """Record an alert"""
        timestamp = datetime.utcnow().timestamp()
        
        self.conn.execute(
            """INSERT INTO alerts 
            (timestamp, alert_name, severity, message, metric_name, metric_value)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (timestamp, alert_name, severity, message, metric_name, metric_value)
        )

    def resolve_alert(self, alert_id: int):
        """Mark an alert as resolved"""
        self.conn.execute(
            "UPDATE alerts SET resolved = TRUE, resolved_at = CURRENT_TIMESTAMP WHERE id = ?",
            (alert_id,)
        )

    def get_active_alerts(self) -> List[Dict]:
        """Get all active (unresolved) alerts"""
        cursor = self.conn.execute(
            "SELECT * FROM alerts WHERE resolved = FALSE ORDER BY timestamp DESC"
        )
        
        results = []
        for row in cursor:
            result = dict(row)
            result["timestamp"] = datetime.fromtimestamp(result["timestamp"])
            results.append(result)
            
        return results

    def cleanup_old_data(self, days_to_keep: int = 7):
        """Clean up old metrics data"""
        cutoff_time = (datetime.utcnow() - timedelta(days=days_to_keep)).timestamp()
        
        with self.transaction():
            # Clean raw metrics
            self.conn.execute(
                "DELETE FROM metrics WHERE timestamp < ?",
                (cutoff_time,)
            )
            
            # Clean aggregated metrics (keep longer)
            long_cutoff = (datetime.utcnow() - timedelta(days=days_to_keep * 4)).timestamp()
            for table in ["metrics_1min", "metrics_5min", "metrics_1hour"]:
                self.conn.execute(
                    f"DELETE FROM {table} WHERE timestamp < ?",
                    (long_cutoff,)
                )
            
            # Clean old resolved alerts
            self.conn.execute(
                "DELETE FROM alerts WHERE resolved = TRUE AND resolved_at < datetime('now', '-30 days')"
            )

    def get_system_stats(self) -> Dict:
        """Get database statistics"""
        stats = {}
        
        # Get table sizes
        for table in ["metrics", "metrics_1min", "metrics_5min", "metrics_1hour", "alerts"]:
            cursor = self.conn.execute(f"SELECT COUNT(*) FROM {table}")
            stats[f"{table}_count"] = cursor.fetchone()[0]
        
        # Get database file size
        if self.db_path.exists():
            stats["db_size_mb"] = self.db_path.stat().st_size / 1024 / 1024
        
        return stats