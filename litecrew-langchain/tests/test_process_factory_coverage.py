"""Tests for process factory to improve coverage."""

import pytest
from unittest.mock import Mock
from litecrew.processes.factory import ProcessFactory
from litecrew.processes.base import BaseProcess, ProcessConfig


class TestProcessFactoryCoverage:
    """Tests for ProcessFactory to improve coverage."""
    
    def setup_method(self):
        """Clear registry before each test."""
        ProcessFactory.clear_registry()
    
    def test_register_process_type(self):
        """Test registering a process type."""
        mock_process_class = Mock(spec=BaseProcess)
        
        ProcessFactory.register("test_process", mock_process_class)
        
        assert "test_process" in ProcessFactory._registry
        assert ProcessFactory._registry["test_process"] == mock_process_class
    
    def test_register_case_insensitive(self):
        """Test that registration is case insensitive."""
        mock_process_class = Mock(spec=BaseProcess)
        
        ProcessFactory.register("TEST_PROCESS", mock_process_class)
        
        assert "test_process" in ProcessFactory._registry
    
    def test_create_unknown_process_type(self):
        """Test creating unknown process type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown process type: unknown"):
            ProcessFactory.create("unknown")
    
    def test_create_process_without_config(self):
        """Test creating process without config."""
        mock_process_class = Mock(spec=BaseProcess)
        mock_instance = Mock()
        mock_process_class.return_value = mock_instance
        
        ProcessFactory.register("test", mock_process_class)
        
        result = ProcessFactory.create("test")
        
        mock_process_class.assert_called_once_with()
        assert result == mock_instance
    
    def test_create_process_with_config(self):
        """Test creating process with config."""
        mock_process_class = Mock(spec=BaseProcess)
        mock_instance = Mock()
        mock_process_class.return_value = mock_instance
        
        ProcessFactory.register("test", mock_process_class)
        
        config = {
            "verbose": True,
            "max_iterations": 10,
            "timeout": 30,
            "custom_field": "value"
        }
        
        result = ProcessFactory.create("test", config)
        
        # Should be called with ProcessConfig
        mock_process_class.assert_called_once()
        args = mock_process_class.call_args[0]
        assert isinstance(args[0], ProcessConfig)
        assert args[0].verbose is True
        assert args[0].max_iterations == 10
        assert args[0].timeout == 30
        assert result == mock_instance
    
    def test_create_process_with_from_config(self):
        """Test creating process with from_config method."""
        mock_process_class = Mock()
        mock_instance = Mock()
        mock_process_class.from_config.return_value = mock_instance
        
        ProcessFactory.register("test", mock_process_class)
        
        config = {
            "verbose": True,
            "custom_field": "value"
        }
        
        result = ProcessFactory.create("test", config)
        
        # Should call from_config method
        mock_process_class.from_config.assert_called_once()
        args = mock_process_class.from_config.call_args[0]
        assert isinstance(args[0], ProcessConfig)
        assert args[1] == {"custom_field": "value"}
        assert result == mock_instance
    
    def test_list_types(self):
        """Test listing available process types."""
        mock_process1 = Mock(spec=BaseProcess)
        mock_process2 = Mock(spec=BaseProcess)
        
        ProcessFactory.register("type1", mock_process1)
        ProcessFactory.register("type2", mock_process2)
        
        types = ProcessFactory.list_types()
        
        assert "type1" in types
        assert "type2" in types
        assert len(types) == 2
    
    def test_clear_registry(self):
        """Test clearing the registry."""
        mock_process_class = Mock(spec=BaseProcess)
        ProcessFactory.register("test", mock_process_class)
        
        assert len(ProcessFactory._registry) == 1
        
        ProcessFactory.clear_registry()
        
        assert len(ProcessFactory._registry) == 0
    
    def test_case_insensitive_creation(self):
        """Test that process creation is case insensitive."""
        mock_process_class = Mock(spec=BaseProcess)
        mock_instance = Mock()
        mock_process_class.return_value = mock_instance
        
        ProcessFactory.register("test", mock_process_class)
        
        result = ProcessFactory.create("TEST")
        
        mock_process_class.assert_called_once_with()
        assert result == mock_instance