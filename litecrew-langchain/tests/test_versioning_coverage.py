"""Tests for versioning to improve coverage."""

import json
import hashlib
from datetime import datetime
from litecrew.storage.versioning import ResultVersion


class TestResultVersionCoverage:
    """Tests for ResultVersion to improve coverage."""
    
    def test_post_init_checksum_calculation(self):
        """Test that checksum is calculated in __post_init__ if not provided."""
        data = {"key": "value", "number": 42}
        version = ResultVersion(version=1, data=data)
        
        # Should have calculated checksum
        assert version.checksum is not None
        
        # Should match manual calculation
        data_str = json.dumps(data, sort_keys=True)
        expected_checksum = hashlib.sha256(data_str.encode()).hexdigest()[:16]
        assert version.checksum == expected_checksum
    
    def test_post_init_with_provided_checksum(self):
        """Test that provided checksum is not overridden."""
        data = {"key": "value"}
        custom_checksum = "custom_checksum"
        version = ResultVersion(version=1, data=data, checksum=custom_checksum)
        
        # Should keep the provided checksum
        assert version.checksum == custom_checksum
    
    def test_create_first_version(self):
        """Test creating first version without parent."""
        data = {"key": "value"}
        version = ResultVersion.create(data)
        
        # Should be version 1 with no parent
        assert version.version == 1
        assert version.parent_version is None
        assert version.data == data
        assert version.checksum is not None
    
    def test_create_with_parent(self):
        """Test creating version with parent."""
        parent_data = {"key": "parent_value"}
        parent = ResultVersion(version=1, data=parent_data)
        
        child_data = {"key": "child_value"}
        child = ResultVersion.create(child_data, parent=parent)
        
        # Should be version 2 with parent reference
        assert child.version == 2
        assert child.parent_version == 1
        assert child.data == child_data
        assert child.checksum is not None
    
    def test_get_diff_basic(self):
        """Test basic diff functionality."""
        data1 = {"key": "value1"}
        data2 = {"key": "value2"}
        
        version1 = ResultVersion(version=1, data=data1)
        version2 = ResultVersion(version=2, data=data2)
        
        diff = version2.get_diff(version1)
        
        # Should have correct version info
        assert diff["version_from"] == 1
        assert diff["version_to"] == 2
        assert "changes" in diff
        assert isinstance(diff["changes"], dict)
    
    def test_calculate_checksum_consistency(self):
        """Test that checksum calculation is consistent."""
        data = {"key": "value", "number": 42}
        
        version1 = ResultVersion(version=1, data=data)
        version2 = ResultVersion(version=2, data=data)
        
        # Same data should produce same checksum
        assert version1.checksum == version2.checksum
    
    def test_default_values(self):
        """Test default values for optional fields."""
        data = {"key": "value"}
        version = ResultVersion(version=1, data=data)
        
        # Should have default values
        assert isinstance(version.timestamp, datetime)
        assert version.parent_version is None
        assert version.metadata == {}
        assert version.checksum is not None