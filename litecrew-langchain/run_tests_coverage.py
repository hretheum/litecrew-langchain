#!/usr/bin/env python3
"""Run tests with coverage check."""

import os
import sys
import subprocess

# Set environment variables
os.environ["LITECREW_API_KEYS"] = "test-key-123,test-key-456"
os.environ["ENVIRONMENT"] = "test"
os.environ["SESSION_SECRET"] = "test-secret"

# Run tests with coverage
result = subprocess.run([
    sys.executable, "-m", "pytest", 
    "tests/", 
    "-v", 
    "--cov=src/litecrew",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=70",
    "--tb=short"
], capture_output=False)

sys.exit(result.returncode)