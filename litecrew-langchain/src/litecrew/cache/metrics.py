"""
Cache metrics tracking and monitoring.
"""

import time
from dataclasses import dataclass, field
from statistics import mean, quantiles
from typing import Any, Dict, List, Optional


@dataclass
class CacheMetrics:
    """Cache performance metrics."""

    # Basic counters
    hits: int = 0
    misses: int = 0
    sets: int = 0
    evictions: int = 0

    # Level-specific counters
    l1_hits: int = 0
    l2_hits: int = 0
    l3_hits: int = 0

    # Size metrics
    l1_entries: int = 0
    l2_entries: int = 0
    l3_entries: int = 0
    total_size_bytes: int = 0

    # Latency tracking
    get_latencies: List[float] = field(default_factory=list)
    set_latencies: List[float] = field(default_factory=list)

    # Time window for metrics
    window_start: float = field(default_factory=time.time)

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def total_operations(self) -> int:
        """Total number of cache operations."""
        return self.hits + self.misses + self.sets

    @property
    def average_entry_size(self) -> float:
        """Average size of cache entries."""
        total_entries = self.l1_entries + self.l2_entries + self.l3_entries
        return self.total_size_bytes / total_entries if total_entries > 0 else 0

    @property
    def average_get_latency_ms(self) -> float:
        """Average GET operation latency in milliseconds."""
        return mean(self.get_latencies) * 1000 if self.get_latencies else 0

    @property
    def average_set_latency_ms(self) -> float:
        """Average SET operation latency in milliseconds."""
        return mean(self.set_latencies) * 1000 if self.set_latencies else 0

    @property
    def p95_get_latency_ms(self) -> float:
        """95th percentile GET latency."""
        if len(self.get_latencies) < 2:
            return 0
        return quantiles(self.get_latencies, n=20)[18] * 1000  # 95th percentile

    @property
    def p99_get_latency_ms(self) -> float:
        """99th percentile GET latency."""
        if len(self.get_latencies) < 2:
            return 0
        try:
            return quantiles(self.get_latencies, n=100)[98] * 1000  # 99th percentile
        except Exception:
            return max(self.get_latencies) * 1000

    def record_get(self, hit: bool, level: Optional[int], latency: float) -> None:
        """Record a GET operation."""
        if hit:
            self.hits += 1
            if level == 1:
                self.l1_hits += 1
            elif level == 2:
                self.l2_hits += 1
            elif level == 3:
                self.l3_hits += 1
        else:
            self.misses += 1

        self.get_latencies.append(latency)

        # Keep only recent latencies (last 1000)
        if len(self.get_latencies) > 1000:
            self.get_latencies.pop(0)

    def record_set(self, latency: float) -> None:
        """Record a SET operation."""
        self.sets += 1
        self.set_latencies.append(latency)

        # Keep only recent latencies
        if len(self.set_latencies) > 1000:
            self.set_latencies.pop(0)

    def record_eviction(self) -> None:
        """Record a cache eviction."""
        self.evictions += 1

    def update_sizes(self, l1: int, l2: int, l3: int, total_bytes: int) -> None:
        """Update size metrics."""
        self.l1_entries = l1
        self.l2_entries = l2
        self.l3_entries = l3
        self.total_size_bytes = total_bytes

    def reset(self) -> None:
        """Reset all metrics."""
        # Reset all fields to their defaults
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.evictions = 0
        self.l1_hits = 0
        self.l2_hits = 0
        self.l3_hits = 0
        self.l1_entries = 0
        self.l2_entries = 0
        self.l3_entries = 0
        self.total_size_bytes = 0
        self.get_latencies = []
        self.set_latencies = []
        self.window_start = time.time()

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        return {
            "hit_rate": f"{self.hit_rate:.1%}",
            "total_operations": self.total_operations,
            "average_get_latency_ms": f"{self.average_get_latency_ms:.2f}",
            "average_set_latency_ms": f"{self.average_set_latency_ms:.2f}",
            "p95_get_latency_ms": f"{self.p95_get_latency_ms:.2f}",
            "p99_get_latency_ms": f"{self.p99_get_latency_ms:.2f}",
            "cache_sizes": {
                "l1": self.l1_entries,
                "l2": self.l2_entries,
                "l3": self.l3_entries,
            },
            "total_size_mb": f"{self.total_size_bytes / (1024 * 1024):.2f}",
            "eviction_rate": (
                f"{self.evictions / self.sets:.1%}" if self.sets > 0 else "0%"
            ),
        }
