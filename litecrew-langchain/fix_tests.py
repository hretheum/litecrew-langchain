#!/usr/bin/env python3
"""Script to run tests with proper authentication setup."""

import os
import sys
import subprocess

# Set environment variables
os.environ["LITECREW_API_KEYS"] = "test-key-123,test-key-456"
os.environ["ENVIRONMENT"] = "test"
os.environ["SESSION_SECRET"] = "test-secret"

# Run tests
result = subprocess.run([
    sys.executable, "-m", "pytest", 
    "tests/", 
    "-v", 
    "--tb=short",
    "--ignore=tests/test_crewai_compatibility.py"  # Ignore compatibility tests for now
], capture_output=False)

sys.exit(result.returncode)