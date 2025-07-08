"""Tests for state base to improve coverage."""

from litecrew.state.base import StateError


class TestStateBaseCoverage:
    """Tests for state base classes to improve coverage."""
    
    def test_state_error_creation(self):
        """Test StateError exception creation."""
        error = StateError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    def test_state_error_inheritance(self):
        """Test StateError inheritance."""
        error = StateError("Test error")
        assert issubclass(StateError, Exception)
        assert isinstance(error, Exception)
        
    def test_state_error_empty_message(self):
        """Test StateError with empty message."""
        error = StateError("")
        assert str(error) == ""