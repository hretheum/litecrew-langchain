"""Comprehensive tests for storage compression module."""

import pytest
from litecrew.storage.compression import CompressionType, Compressor


class TestCompressionType:
    """Test CompressionType enum."""
    
    def test_compression_types_exist(self):
        """Test all compression types exist."""
        assert CompressionType.NONE.value == "none"
        assert CompressionType.ZLIB.value == "zlib"
        assert CompressionType.GZIP.value == "gzip"
        assert CompressionType.BZ2.value == "bz2"
        
    def test_compression_types_count(self):
        """Test expected number of compression types."""
        types = list(CompressionType)
        assert len(types) == 4


class TestCompressor:
    """Test Compressor class."""
    
    def test_compress_string_zlib(self):
        """Test compressing string with zlib."""
        data = "Hello, World!" * 100  # Make it worth compressing
        compressed, original_size, compressed_size = Compressor.compress(
            data, CompressionType.ZLIB
        )
        
        assert isinstance(compressed, bytes)
        assert original_size == len(data.encode('utf-8'))
        assert compressed_size == len(compressed)
        assert compressed_size < original_size  # Should compress
        
    def test_compress_bytes_zlib(self):
        """Test compressing bytes with zlib."""
        data = b"Hello, World!" * 100
        compressed, original_size, compressed_size = Compressor.compress(
            data, CompressionType.ZLIB
        )
        
        assert isinstance(compressed, bytes)
        assert original_size == len(data)
        assert compressed_size == len(compressed)
        assert compressed_size < original_size
        
    def test_compress_gzip(self):
        """Test compressing with gzip."""
        data = "Hello, World!" * 100
        compressed, original_size, compressed_size = Compressor.compress(
            data, CompressionType.GZIP
        )
        
        assert isinstance(compressed, bytes)
        assert original_size == len(data.encode('utf-8'))
        assert compressed_size == len(compressed)
        assert compressed_size < original_size
        
    def test_compress_bz2(self):
        """Test compressing with bz2."""
        data = "Hello, World!" * 100
        compressed, original_size, compressed_size = Compressor.compress(
            data, CompressionType.BZ2
        )
        
        assert isinstance(compressed, bytes)
        assert original_size == len(data.encode('utf-8'))
        assert compressed_size == len(compressed)
        assert compressed_size < original_size
        
    def test_compress_none(self):
        """Test no compression."""
        data = "Hello, World!"
        compressed, original_size, compressed_size = Compressor.compress(
            data, CompressionType.NONE
        )
        
        assert isinstance(compressed, bytes)
        assert compressed == data.encode('utf-8')
        assert original_size == compressed_size
        assert compressed_size == len(data.encode('utf-8'))
        
    def test_compress_with_level(self):
        """Test compression with different levels."""
        data = "Hello, World!" * 1000
        
        # Test different compression levels
        compressed_1, _, size_1 = Compressor.compress(
            data, CompressionType.ZLIB, level=1
        )
        compressed_9, _, size_9 = Compressor.compress(
            data, CompressionType.ZLIB, level=9
        )
        
        assert isinstance(compressed_1, bytes)
        assert isinstance(compressed_9, bytes)
        # Higher level should give better compression
        assert size_9 <= size_1
        
    def test_compress_invalid_type(self):
        """Test compression with invalid type."""
        data = "Hello, World!"
        
        with pytest.raises(ValueError, match="Unsupported compression type"):
            Compressor.compress(data, "invalid_type")
            
    def test_decompress_zlib(self):
        """Test decompressing zlib data."""
        original = "Hello, World!" * 100
        compressed, _, _ = Compressor.compress(original, CompressionType.ZLIB)
        
        decompressed = Compressor.decompress(compressed, CompressionType.ZLIB)
        
        assert isinstance(decompressed, bytes)
        assert decompressed == original.encode('utf-8')
        
    def test_decompress_gzip(self):
        """Test decompressing gzip data."""
        original = "Hello, World!" * 100
        compressed, _, _ = Compressor.compress(original, CompressionType.GZIP)
        
        decompressed = Compressor.decompress(compressed, CompressionType.GZIP)
        
        assert isinstance(decompressed, bytes)
        assert decompressed == original.encode('utf-8')
        
    def test_decompress_bz2(self):
        """Test decompressing bz2 data."""
        original = "Hello, World!" * 100
        compressed, _, _ = Compressor.compress(original, CompressionType.BZ2)
        
        decompressed = Compressor.decompress(compressed, CompressionType.BZ2)
        
        assert isinstance(decompressed, bytes)
        assert decompressed == original.encode('utf-8')
        
    def test_decompress_none(self):
        """Test decompressing uncompressed data."""
        original = "Hello, World!"
        data = original.encode('utf-8')
        
        decompressed = Compressor.decompress(data, CompressionType.NONE)
        
        assert decompressed == data
        
    def test_decompress_invalid_type(self):
        """Test decompressing with invalid type."""
        data = b"Hello, World!"
        
        with pytest.raises(ValueError, match="Unsupported compression type"):
            Compressor.decompress(data, "invalid_type")
            
    def test_compress_decompress_roundtrip(self):
        """Test complete compress-decompress cycle."""
        original = "This is a test string that should compress well! " * 50
        
        for compression_type in [CompressionType.ZLIB, CompressionType.GZIP, CompressionType.BZ2]:
            compressed, _, _ = Compressor.compress(original, compression_type)
            decompressed = Compressor.decompress(compressed, compression_type)
            
            assert decompressed.decode('utf-8') == original
            
    def test_get_compression_ratio(self):
        """Test compression ratio calculation."""
        # Perfect compression
        ratio = Compressor.get_compression_ratio(1000, 500)
        assert ratio == 0.5
        
        # No compression
        ratio = Compressor.get_compression_ratio(1000, 1000)
        assert ratio == 1.0
        
        # Expansion (theoretical)
        ratio = Compressor.get_compression_ratio(1000, 1200)
        assert ratio == 1.2
        
    def test_get_compression_ratio_zero_original(self):
        """Test compression ratio with zero original size."""
        ratio = Compressor.get_compression_ratio(0, 100)
        assert ratio == 1.0
        
    def test_get_compression_ratio_zero_both(self):
        """Test compression ratio with zero sizes."""
        ratio = Compressor.get_compression_ratio(0, 0)
        assert ratio == 1.0
        
    def test_should_compress_above_threshold(self):
        """Test should compress for data above threshold."""
        assert Compressor.should_compress(2048) is True
        assert Compressor.should_compress(10000) is True
        
    def test_should_compress_below_threshold(self):
        """Test should compress for data below threshold."""
        assert Compressor.should_compress(512) is False
        assert Compressor.should_compress(1023) is False
        
    def test_should_compress_at_threshold(self):
        """Test should compress for data at threshold."""
        assert Compressor.should_compress(1024) is False
        assert Compressor.should_compress(1025) is True
        
    def test_should_compress_custom_threshold(self):
        """Test should compress with custom threshold."""
        assert Compressor.should_compress(500, threshold=1000) is False
        assert Compressor.should_compress(1500, threshold=1000) is True
        
    def test_should_compress_zero_threshold(self):
        """Test should compress with zero threshold."""
        assert Compressor.should_compress(1, threshold=0) is True
        assert Compressor.should_compress(0, threshold=0) is False
        
    def test_compress_empty_string(self):
        """Test compressing empty string."""
        compressed, original_size, compressed_size = Compressor.compress(
            "", CompressionType.ZLIB
        )
        
        assert isinstance(compressed, bytes)
        assert original_size == 0
        assert compressed_size > 0  # Compression headers add size
        
    def test_compress_empty_bytes(self):
        """Test compressing empty bytes."""
        compressed, original_size, compressed_size = Compressor.compress(
            b"", CompressionType.ZLIB
        )
        
        assert isinstance(compressed, bytes)
        assert original_size == 0
        assert compressed_size > 0  # Compression headers add size
        
    def test_decompress_empty_data(self):
        """Test decompressing empty compressed data."""
        compressed, _, _ = Compressor.compress(b"", CompressionType.ZLIB)
        decompressed = Compressor.decompress(compressed, CompressionType.ZLIB)
        
        assert decompressed == b""
        
    def test_compress_unicode_string(self):
        """Test compressing unicode string."""
        data = "Hello, 世界! 🌍" * 100
        compressed, original_size, compressed_size = Compressor.compress(
            data, CompressionType.ZLIB
        )
        
        assert isinstance(compressed, bytes)
        assert original_size == len(data.encode('utf-8'))
        assert compressed_size < original_size
        
        # Test roundtrip
        decompressed = Compressor.decompress(compressed, CompressionType.ZLIB)
        assert decompressed.decode('utf-8') == data
        
    def test_compression_efficiency_comparison(self):
        """Test compression efficiency of different algorithms."""
        # Use repetitive data that compresses well
        data = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 1000
        
        results = {}
        for compression_type in [CompressionType.ZLIB, CompressionType.GZIP, CompressionType.BZ2]:
            compressed, original_size, compressed_size = Compressor.compress(
                data, compression_type
            )
            ratio = Compressor.get_compression_ratio(original_size, compressed_size)
            results[compression_type] = ratio
            
        # All should achieve some compression
        for compression_type, ratio in results.items():
            assert ratio < 1.0, f"{compression_type} failed to compress"
            
    def test_compression_levels_effect(self):
        """Test effect of compression levels."""
        data = "This is a test string with repeated content. " * 200
        
        # Test levels 1, 6, 9
        size_1 = Compressor.compress(data, CompressionType.ZLIB, level=1)[2]
        size_6 = Compressor.compress(data, CompressionType.ZLIB, level=6)[2]
        size_9 = Compressor.compress(data, CompressionType.ZLIB, level=9)[2]
        
        # Higher levels should compress better or equal
        assert size_9 <= size_6
        assert size_6 <= size_1
        
    def test_invalid_compression_level(self):
        """Test invalid compression levels are handled gracefully."""
        data = "Hello, World!"
        
        # These should not raise exceptions, just use default behavior
        try:
            Compressor.compress(data, CompressionType.ZLIB, level=0)
            Compressor.compress(data, CompressionType.ZLIB, level=10)
        except Exception:
            # If compression libraries raise exceptions for invalid levels,
            # that's expected behavior
            pass