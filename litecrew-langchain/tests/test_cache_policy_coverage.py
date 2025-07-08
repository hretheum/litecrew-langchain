"""Tests for cache policy to improve coverage."""

import pytest
from litecrew.cache.policy import CachePolicy


class TestCachePolicyCoverage:
    """Tests for CachePolicy to improve coverage."""
    
    def test_should_compress_above_threshold(self):
        """Test should_compress returns True when size is above threshold."""
        policy = CachePolicy()
        policy.compression_threshold = 1000
        
        # Should return True for size above threshold
        assert policy.should_compress(1001) is True
    
    def test_should_compress_below_threshold(self):
        """Test should_compress returns False when size is below threshold."""
        policy = CachePolicy()
        policy.compression_threshold = 1000
        
        # Should return False for size below threshold
        assert policy.should_compress(999) is False
    
    def test_should_compress_equal_threshold(self):
        """Test should_compress returns False when size equals threshold."""
        policy = CachePolicy()
        policy.compression_threshold = 1000
        
        # Should return False for size equal to threshold
        assert policy.should_compress(1000) is False