#!/usr/bin/env python3
"""
Aggregate metrics at regular intervals
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.metrics_storage import MetricsStorage


def main():
    """Run metric aggregation"""
    storage = MetricsStorage()
    
    print("Starting metrics aggregation...")
    
    # Aggregate 1-minute metrics
    storage.aggregate_metrics(1)
    print("✓ 1-minute metrics aggregated")
    
    # Aggregate 5-minute metrics
    storage.aggregate_metrics(5)
    print("✓ 5-minute metrics aggregated")
    
    # Aggregate 1-hour metrics
    storage.aggregate_metrics(60)
    print("✓ 1-hour metrics aggregated")
    
    # Cleanup old data
    storage.cleanup_old_data(days_to_keep=7)
    print("✓ Old data cleaned up")
    
    # Show stats
    stats = storage.get_system_stats()
    print("\nDatabase Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()