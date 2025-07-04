"""
State snapshot functionality.
"""

import json
import hashlib
import zlib
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

from litecrew.state.crew_state import CrewState
from litecrew.storage.compression import Compressor, CompressionType


@dataclass
class StateSnapshot:
    """Represents a snapshot of crew state at a point in time."""

    crew_id: str
    version: int
    timestamp: datetime = field(default_factory=datetime.now)
    data: Union[Dict[str, Any], bytes] = field(default_factory=dict)
    checksum: Optional[str] = None
    compressed: bool = False
    compression_type: CompressionType = CompressionType.ZLIB
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate checksum if not provided."""
        if self.checksum is None:
            self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate checksum of data."""
        if isinstance(self.data, bytes):
            data_bytes = self.data
        else:
            data_str = json.dumps(self.data, sort_keys=True)
            data_bytes = data_str.encode("utf-8")

        return hashlib.sha256(data_bytes).hexdigest()[:16]

    @classmethod
    def create(
        cls,
        state: CrewState,
        version: int = 1,
        compress: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "StateSnapshot":
        """Create snapshot from crew state."""
        data = state.to_dict()

        if compress:
            # Compress data
            data_str = json.dumps(data)
            compressed_data, _, _ = Compressor.compress(data_str, CompressionType.ZLIB)

            return cls(
                crew_id=state.crew_id,
                version=version,
                data=compressed_data,
                compressed=True,
                compression_type=CompressionType.ZLIB,
                metadata=metadata or {},
            )
        else:
            return cls(
                crew_id=state.crew_id,
                version=version,
                data=data,
                compressed=False,
                metadata=metadata or {},
            )

    def restore(self) -> CrewState:
        """Restore crew state from snapshot."""
        if self.compressed:
            # Decompress data
            decompressed = Compressor.decompress(self.data, self.compression_type)
            data = json.loads(decompressed.decode("utf-8"))
        else:
            data = self.data

        return CrewState.from_dict(data)

    def verify_integrity(self) -> bool:
        """Verify snapshot integrity using checksum."""
        calculated = self._calculate_checksum()
        return calculated == self.checksum

    def get_size(self) -> int:
        """Get snapshot size in bytes."""
        if isinstance(self.data, bytes):
            return len(self.data)
        else:
            return len(json.dumps(self.data).encode("utf-8"))

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""
        # Handle binary data for JSON serialization
        if isinstance(self.data, bytes):
            data_repr = self.data.hex()
        else:
            data_repr = self.data

        return {
            "crew_id": self.crew_id,
            "version": self.version,
            "timestamp": self.timestamp.isoformat(),
            "data": data_repr,
            "checksum": self.checksum,
            "compressed": self.compressed,
            "compression_type": self.compression_type.value,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateSnapshot":
        """Create snapshot from dictionary."""
        # Handle binary data deserialization
        snapshot_data = data["data"]
        if data["compressed"] and isinstance(snapshot_data, str):
            snapshot_data = bytes.fromhex(snapshot_data)

        return cls(
            crew_id=data["crew_id"],
            version=data["version"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            data=snapshot_data,
            checksum=data["checksum"],
            compressed=data["compressed"],
            compression_type=CompressionType(data["compression_type"]),
            metadata=data.get("metadata", {}),
        )
