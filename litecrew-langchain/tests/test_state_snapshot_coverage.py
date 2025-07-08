"""Tests for state snapshot to improve coverage."""

import pytest
import json
from datetime import datetime
from litecrew.state.snapshot import StateSnapshot


class TestStateSnapshotCoverage:
    """Tests for StateSnapshot to improve coverage."""
    
    def test_verify_integrity_valid(self):
        """Test verify_integrity returns True for valid checksum."""
        snapshot = StateSnapshot(
            crew_id="test_crew",
            version=1,
            data={"test": "data"},
            timestamp=datetime.now()
        )
        
        # Should return True for valid checksum
        assert snapshot.verify_integrity() is True
    
    def test_verify_integrity_invalid(self):
        """Test verify_integrity returns False for invalid checksum."""
        snapshot = StateSnapshot(
            crew_id="test_crew",
            version=1,
            data={"test": "data"},
            timestamp=datetime.now()
        )
        
        # Modify checksum to make it invalid
        snapshot.checksum = "invalid_checksum"
        
        # Should return False for invalid checksum
        assert snapshot.verify_integrity() is False
    
    def test_get_size_with_bytes_data(self):
        """Test get_size with bytes data."""
        test_data = b"test bytes data"
        snapshot = StateSnapshot(
            crew_id="test_crew",
            version=1,
            data=test_data,
            timestamp=datetime.now()
        )
        
        # Should return length of bytes data
        assert snapshot.get_size() == len(test_data)
    
    def test_get_size_with_dict_data(self):
        """Test get_size with dict data."""
        test_data = {"test": "data", "number": 42}
        snapshot = StateSnapshot(
            crew_id="test_crew",
            version=1,
            data=test_data,
            timestamp=datetime.now()
        )
        
        # Should return length of JSON encoded data
        expected_size = len(json.dumps(test_data).encode("utf-8"))
        assert snapshot.get_size() == expected_size
    
    def test_to_dict(self):
        """Test to_dict method."""
        snapshot = StateSnapshot(
            crew_id="test_crew",
            version=1,
            data={"test": "data"},
            timestamp=datetime.now()
        )
        
        result = snapshot.to_dict()
        
        # Should contain all snapshot fields
        assert "crew_id" in result
        assert "data" in result
        assert "timestamp" in result
        assert "version" in result
        assert "checksum" in result
        assert result["crew_id"] == "test_crew"
        assert result["data"] == {"test": "data"}
        assert result["version"] == 1