"""Tests for storage base to improve coverage."""

from unittest.mock import Mock
from litecrew.storage.base import StorageBackend, StorageError, StorageMetrics


class TestStorageBaseCoverage:
    """Tests for StorageBackend base class to improve coverage."""
    
    def test_storage_error(self):
        """Test StorageError exception."""
        error = StorageError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_storage_metrics_defaults(self):
        """Test StorageMetrics default values."""
        metrics = StorageMetrics()
        assert metrics.total_writes == 0
        assert metrics.total_reads == 0
        assert metrics.total_size_bytes == 0
        assert metrics.average_write_time_ms == 0.0
        assert metrics.average_read_time_ms == 0.0
        assert metrics.compression_ratio == 1.0
    
    def test_read_batch_implementation(self):
        """Test read_batch default implementation."""
        # Create a mock backend
        backend = Mock(spec=StorageBackend)
        
        # Set up the exists and read methods
        backend.exists.side_effect = lambda key: key in ['key1', 'key2']
        backend.read.side_effect = lambda key: {'data': f'value_{key}'} if key in ['key1', 'key2'] else None
        
        # Use the real read_batch method
        result = StorageBackend.read_batch(backend, ['key1', 'key2', 'key3'])
        
        # Verify calls
        backend.exists.assert_any_call('key1')
        backend.exists.assert_any_call('key2')
        backend.exists.assert_any_call('key3')
        backend.read.assert_any_call('key1')
        backend.read.assert_any_call('key2')
        
        # Check result
        assert result == {'key1': {'data': 'value_key1'}, 'key2': {'data': 'value_key2'}}
    
    def test_write_batch_implementation(self):
        """Test write_batch default implementation."""
        # Create a mock backend
        backend = Mock(spec=StorageBackend)
        
        # Use the real write_batch method
        items = {'key1': {'data': 'value1'}, 'key2': {'data': 'value2'}}
        StorageBackend.write_batch(backend, items)
        
        # Verify calls
        backend.write.assert_any_call('key1', {'data': 'value1'})
        backend.write.assert_any_call('key2', {'data': 'value2'})
    
    def test_search_implementation(self):
        """Test search default implementation."""
        # Create a mock backend
        backend = Mock(spec=StorageBackend)
        
        # Set up the list_keys and read methods
        backend.list_keys.return_value = ['key1', 'key2', 'key3']
        backend.read.side_effect = lambda key: {'data': f'value_{key}'} if key != 'key3' else None
        
        # Use the real search method
        result = StorageBackend.search(backend, 'pattern*')
        
        # Verify calls
        backend.list_keys.assert_called_once_with('pattern*')
        backend.read.assert_any_call('key1')
        backend.read.assert_any_call('key2')
        backend.read.assert_any_call('key3')
        
        # Check result (should filter out None values)
        assert result == [{'data': 'value_key1'}, {'data': 'value_key2'}]