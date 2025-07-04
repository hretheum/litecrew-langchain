"""
Compression utilities for storage layer.
"""

import bz2
import gzip
import zlib
from enum import Enum
from typing import Tuple, Union


class CompressionType(Enum):
    """Supported compression types."""

    NONE = "none"
    ZLIB = "zlib"
    GZIP = "gzip"
    BZ2 = "bz2"


class Compressor:
    """Handle data compression and decompression."""

    @staticmethod
    def compress(
        data: Union[str, bytes],
        compression_type: CompressionType = CompressionType.ZLIB,
        level: int = 6,
    ) -> Tuple[bytes, int, int]:
        """
        Compress data.

        Args:
            data: Data to compress
            compression_type: Type of compression
            level: Compression level (1-9)

        Returns:
            Tuple of (compressed_data, original_size, compressed_size)
        """
        # Convert to bytes if needed
        if isinstance(data, str):
            data_bytes = data.encode("utf-8")
        else:
            data_bytes = data

        original_size = len(data_bytes)

        if compression_type == CompressionType.NONE:
            return data_bytes, original_size, original_size

        elif compression_type == CompressionType.ZLIB:
            compressed = zlib.compress(data_bytes, level=level)

        elif compression_type == CompressionType.GZIP:
            compressed = gzip.compress(data_bytes, compresslevel=level)

        elif compression_type == CompressionType.BZ2:
            compressed = bz2.compress(data_bytes, compresslevel=level)

        else:
            raise ValueError(f"Unsupported compression type: {compression_type}")

        compressed_size = len(compressed)
        return compressed, original_size, compressed_size

    @staticmethod
    def decompress(
        data: bytes, compression_type: CompressionType = CompressionType.ZLIB
    ) -> bytes:
        """
        Decompress data.

        Args:
            data: Compressed data
            compression_type: Type of compression used

        Returns:
            Decompressed data as bytes
        """
        if compression_type == CompressionType.NONE:
            return data

        elif compression_type == CompressionType.ZLIB:
            return zlib.decompress(data)

        elif compression_type == CompressionType.GZIP:
            return gzip.decompress(data)

        elif compression_type == CompressionType.BZ2:
            return bz2.decompress(data)

        else:
            raise ValueError(f"Unsupported compression type: {compression_type}")

    @staticmethod
    def get_compression_ratio(original_size: int, compressed_size: int) -> float:
        """Calculate compression ratio."""
        if original_size == 0:
            return 1.0
        return compressed_size / original_size

    @staticmethod
    def should_compress(data_size: int, threshold: int = 1024) -> bool:
        """Determine if data should be compressed based on size."""
        return data_size > threshold
