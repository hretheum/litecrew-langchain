"""
Result versioning functionality.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ResultVersion:
    """Represents a version of a result."""

    version: int
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    parent_version: Optional[int] = None
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate checksum if not provided."""
        if self.checksum is None:
            self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate checksum of data."""
        data_str = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    @classmethod
    def create(
        cls, data: Dict[str, Any], parent: Optional["ResultVersion"] = None
    ) -> "ResultVersion":
        """Create a new version."""
        version = parent.version + 1 if parent else 1
        parent_version = parent.version if parent else None

        return cls(version=version, data=data, parent_version=parent_version)

    def get_diff(self, other: "ResultVersion") -> Dict[str, Any]:
        """Get differences between this version and another."""
        diff = {
            "version_from": other.version,
            "version_to": self.version,
            "changes": {},
        }

        # Simple diff - could be enhanced with deep diff
        all_keys = set(self.data.keys()) | set(other.data.keys())

        for key in all_keys:
            if key not in other.data:
                diff["changes"][key] = {"type": "added", "value": self.data[key]}
            elif key not in self.data:
                diff["changes"][key] = {"type": "removed", "old_value": other.data[key]}
            elif self.data[key] != other.data[key]:
                diff["changes"][key] = {
                    "type": "modified",
                    "old_value": other.data[key],
                    "new_value": self.data[key],
                }

        return diff

    def get_history(self, all_versions: List["ResultVersion"]) -> List["ResultVersion"]:
        """Get version history leading to this version."""
        history = []
        current = self

        # Build version map for efficient lookup
        version_map = {v.version: v for v in all_versions}

        while current:
            history.append(current)
            if current.parent_version and current.parent_version in version_map:
                current = version_map[current.parent_version]
            else:
                break

        return list(reversed(history))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "parent_version": self.parent_version,
            "checksum": self.checksum,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResultVersion":
        """Create from dictionary."""
        return cls(
            version=data["version"],
            data=data["data"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            parent_version=data.get("parent_version"),
            checksum=data.get("checksum"),
            metadata=data.get("metadata", {}),
        )
