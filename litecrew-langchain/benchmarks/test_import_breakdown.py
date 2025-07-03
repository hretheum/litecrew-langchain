#!/usr/bin/env python3
"""Breakdown of import times to find bottlenecks."""

import time
import sys
import subprocess

def test_import(imports):
    """Test import time for given imports."""
    code = f"""
import time
start = time.perf_counter()
{imports}
print(time.perf_counter() - start)
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        return float(result.stdout.strip()) * 1000
    return None

print("Import Time Breakdown")
print("=" * 50)
print()

tests = [
    ("Empty import", ""),
    ("dataclasses only", "from dataclasses import dataclass, field"),
    ("typing only", "from typing import List, Dict, Optional, Any"),
    ("datetime only", "from datetime import datetime"),
    ("All base imports", """from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime"""),
    ("base.py imports", """from dataclasses import asdict, fields, replace
from typing import Dict, Any, Optional, Type, TypeVar, get_type_hints
import json
from datetime import datetime
from enum import Enum"""),
    ("Just litecrew.base", "from litecrew.base import PydanticCompatible"),
    ("task.py without base", """from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict
from datetime import datetime"""),
    ("Full task.py", "from litecrew.task import LiteTask, TaskOutput"),
]

for name, imports in tests:
    time_ms = test_import(imports)
    if time_ms is not None:
        status = "✅" if time_ms < 10 else "⚠️" if time_ms < 20 else "❌"
        print(f"{name:30} {time_ms:6.2f}ms {status}")
        if time_ms > 20:
            print(f"{'':30} ^-- This is slow!")
    else:
        print(f"{name:30} Failed")
    print()

# Check if we're importing something heavy indirectly
print("=" * 50)
print("Checking for hidden imports...")
print()

# Use python -X importtime to trace imports
result = subprocess.run(
    [sys.executable, "-X", "importtime", "-c", "from litecrew.base import PydanticCompatible"],
    capture_output=True,
    text=True
)

if result.stderr:
    lines = result.stderr.split('\n')
    # Find the slowest imports
    slow_imports = []
    for line in lines:
        if 'import' in line and '|' in line:
            parts = line.split('|')
            if len(parts) >= 2:
                try:
                    time_us = int(parts[1].strip())
                    if time_us > 1000:  # More than 1ms
                        module = parts[-1].strip().split()[-1] if parts[-1].strip() else "unknown"
                        slow_imports.append((time_us / 1000, module))
                except:
                    pass
    
    if slow_imports:
        slow_imports.sort(reverse=True)
        print("Slowest imports (>1ms):")
        for time_ms, module in slow_imports[:10]:
            print(f"  {module:40} {time_ms:6.2f}ms")