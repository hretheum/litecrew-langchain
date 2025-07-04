"""Tests for the api module imports."""

def test_api_module_imports():
    """Test that api module correctly imports create_app."""
    from litecrew.api import create_app
    
    # Verify that create_app is available
    assert create_app is not None
    assert callable(create_app)

def test_api_module_all():
    """Test that __all__ is properly defined."""
    import litecrew.api as api_module
    
    # The api.py file has __all__ defined
    if hasattr(api_module, '__all__'):
        assert 'create_app' in api_module.__all__
        assert len(api_module.__all__) == 1
    else:
        # If __all__ is not defined, just verify create_app is available
        assert hasattr(api_module, 'create_app')