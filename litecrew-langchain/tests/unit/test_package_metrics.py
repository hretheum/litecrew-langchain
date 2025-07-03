"""
Test package import time and memory usage.
"""

import time
import sys
import psutil
import pytest


class TestPackageMetrics:
    """Test that package meets performance requirements."""
    
    def test_import_time(self):
        """Test that package imports in less than 10ms."""
        # Remove litecrew from modules if already imported
        modules_to_remove = [m for m in sys.modules if m.startswith('litecrew')]
        for module in modules_to_remove:
            del sys.modules[module]
        
        # Measure import time
        start = time.perf_counter()
        import litecrew
        duration = time.perf_counter() - start
        
        # Should import in less than 10ms
        assert duration < 0.01, f"Import took {duration:.3f}s, expected <0.01s"
        
    def test_memory_usage(self):
        """Test that package uses less than 30MB of memory."""
        process = psutil.Process()
        
        # Get baseline memory
        baseline_mb = process.memory_info().rss / 1024 / 1024
        
        # Import package
        import litecrew
        
        # Get memory after import
        after_import_mb = process.memory_info().rss / 1024 / 1024
        
        # Calculate increase
        memory_increase_mb = after_import_mb - baseline_mb
        
        # Should use less than 30MB total
        assert after_import_mb < 30, f"Total memory {after_import_mb:.1f}MB, expected <30MB"
        
    def test_version(self):
        """Test that version is properly set."""
        import litecrew
        
        assert hasattr(litecrew, '__version__')
        assert litecrew.__version__ == "0.1.0"
        
    def test_exports(self):
        """Test that all expected exports are available."""
        import litecrew
        
        # Core classes should be exported
        assert hasattr(litecrew, 'LiteAgent')
        assert hasattr(litecrew, 'LiteTask')
        assert hasattr(litecrew, 'LiteCrew')
        
        # CrewAI compatibility aliases
        assert hasattr(litecrew, 'Agent')
        assert hasattr(litecrew, 'Task')
        assert hasattr(litecrew, 'Crew')
        
    def test_python_version_check(self):
        """Test that package enforces Python 3.12+."""
        # This test runs on 3.12+, so it should pass
        # The check happens during import
        import litecrew  # Should not raise
        
        # Verify we're on 3.12+
        assert sys.version_info >= (3, 12)