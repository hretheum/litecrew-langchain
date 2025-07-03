#!/usr/bin/env python3
"""Test direct import time of our models without LangChain."""

import time
import sys
import subprocess

def measure_import_time(module_path, num_runs=10):
    """Measure import time for a module."""
    times = []
    
    for _ in range(num_runs):
        # Use subprocess to ensure clean imports
        result = subprocess.run(
            [sys.executable, "-c", f"import time; start = time.perf_counter(); from {module_path} import *; print(time.perf_counter() - start)"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            import_time = float(result.stdout.strip())
            times.append(import_time)
    
    if times:
        mean_time = sum(times) / len(times)
        return mean_time * 1000  # Convert to ms
    return None

print("Direct Import Time Test")
print("=" * 50)
print()

# Test our modules directly
modules = [
    ("litecrew.base", "PydanticCompatible mixin"),
    ("litecrew.task", "Task models"),
    ("litecrew.crew", "Crew models"),
    ("litecrew.types", "Type definitions"),
    ("litecrew.agent", "Agent (uses LangChain)"),
    ("litecrew", "Full package"),
]

for module, description in modules:
    print(f"{description} ({module}):")
    time_ms = measure_import_time(module, num_runs=5)
    if time_ms:
        status = "✅" if time_ms < 10 else "❌"
        print(f"  Import time: {time_ms:.2f}ms {status}")
    else:
        print(f"  Failed to measure")
    print()

# Test dataclasses vs old Pydantic approach
print("=" * 50)
print("Comparison:")
print()

# Pure dataclasses
dataclass_time = subprocess.run(
    [sys.executable, "-c", "import time; start = time.perf_counter(); from dataclasses import dataclass, field; print(time.perf_counter() - start)"],
    capture_output=True,
    text=True
)
if dataclass_time.returncode == 0:
    print(f"dataclasses import: {float(dataclass_time.stdout.strip()) * 1000:.2f}ms")

# Pydantic
pydantic_time = subprocess.run(
    [sys.executable, "-c", "import time; start = time.perf_counter(); from pydantic import BaseModel, Field; print(time.perf_counter() - start)"],
    capture_output=True,
    text=True
)
if pydantic_time.returncode == 0:
    print(f"Pydantic import: {float(pydantic_time.stdout.strip()) * 1000:.2f}ms")