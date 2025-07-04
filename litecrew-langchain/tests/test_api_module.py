"""Tests for the api.py file - direct import to ensure coverage."""

import sys
import os
import importlib.util


def test_api_file_direct_import():
    """Test api.py file by directly importing it."""
    # Get the path to the api.py file
    api_file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'litecrew', 'api.py')
    
    # Load the module directly from the file
    spec = importlib.util.spec_from_file_location("api_module", api_file_path)
    api_module = importlib.util.module_from_spec(spec)
    
    # Execute the module to trigger coverage
    spec.loader.exec_module(api_module)
    
    # Test that create_app function exists and is callable
    assert hasattr(api_module, 'create_app')
    assert callable(api_module.create_app)
    
    # Test __all__ attribute
    assert hasattr(api_module, '__all__')
    assert 'create_app' in api_module.__all__

def test_api_file_function_execution():
    """Test executing the create_app function from api.py."""
    # Import the module and execute the function
    api_file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'litecrew', 'api.py')
    spec = importlib.util.spec_from_file_location("api_module", api_file_path)
    api_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api_module)
    
    # Execute the function to ensure all lines are covered
    app = api_module.create_app()
    assert app is not None
    
    # Verify it's a FastAPI instance
    from fastapi import FastAPI
    assert isinstance(app, FastAPI)