"""Tests for compression to improve coverage."""

import pytest
from unittest.mock import Mock, patch
from litecrew.storage.compression import Compressor, CompressionType


class TestCompressionCoverage:
    """Tests for Compressor to improve coverage."""
    
    def test_compress_unsupported_type(self):
        """Test compress with unsupported compression type."""
        test_data = b"test data to compress"
        
        # Create a mock compression type that doesn't exist
        unsupported_type = Mock()
        unsupported_type.name = "UNSUPPORTED"
        
        # Should raise ValueError for unsupported type
        with pytest.raises(ValueError, match="Unsupported compression type"):
            Compressor.compress(test_data, unsupported_type)
    
    def test_decompress_unsupported_type(self):
        """Test decompress with unsupported compression type."""
        test_data = b"test data"
        
        # Create a mock compression type that doesn't exist
        unsupported_type = Mock()
        unsupported_type.name = "UNSUPPORTED"
        
        # Should raise ValueError for unsupported type
        with pytest.raises(ValueError, match="Unsupported compression type"):
            Compressor.decompress(test_data, unsupported_type)
    
    def test_compress_bz2_type(self):
        """Test compress with BZ2 compression type."""
        test_data = b"test data to compress with bz2"
        
        compressed, original_size, compressed_size = Compressor.compress(
            test_data, CompressionType.BZ2
        )
        
        # Should return compressed data and sizes
        assert isinstance(compressed, bytes)
        assert original_size == len(test_data)
        assert compressed_size == len(compressed)
        assert compressed_size > 0
    
    def test_decompress_bz2_type(self):
        """Test decompress with BZ2 compression type."""
        test_data = b"test data to compress and decompress with bz2"
        
        # First compress
        compressed, _, _ = Compressor.compress(test_data, CompressionType.BZ2)
        
        # Then decompress
        decompressed = Compressor.decompress(compressed, CompressionType.BZ2)
        
        # Should return original data
        assert decompressed == test_data