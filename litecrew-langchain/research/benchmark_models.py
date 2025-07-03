#!/usr/bin/env python3
"""
Benchmark different model libraries for LiteCrew.
Tests import time, creation time, validation, and serialization.
"""

import time
import json
import sys
from typing import Optional, List, Any
import tracemalloc

def measure_import(module_name: str, import_stmt: str) -> tuple[float, float]:
    """Measure import time and memory for a module."""
    # Measure import time
    start_time = time.perf_counter()
    tracemalloc.start()
    exec(import_stmt)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    import_time = (time.perf_counter() - start_time) * 1000
    
    return import_time, peak / 1024 / 1024  # Convert to MB


def benchmark_pydantic():
    """Benchmark Pydantic BaseModel."""
    print("\n=== PYDANTIC ===")
    
    # Import time
    import_time, import_memory = measure_import(
        "pydantic", 
        "from pydantic import BaseModel, Field"
    )
    print(f"Import time: {import_time:.2f}ms")
    print(f"Import memory: {import_memory:.2f}MB")
    
    from pydantic import BaseModel, Field
    
    # Define model
    class Agent(BaseModel):
        role: str
        goal: str
        backstory: str = ""
        max_iter: int = Field(default=25, ge=1)
        tools: List[str] = Field(default_factory=list)
        
    # Creation benchmark
    start = time.perf_counter()
    agents = []
    for i in range(1000):
        agent = Agent(
            role=f"Agent {i}",
            goal=f"Goal {i}",
            max_iter=10
        )
        agents.append(agent)
    creation_time = (time.perf_counter() - start) * 1000
    print(f"Create 1000 agents: {creation_time:.2f}ms ({creation_time/1000:.3f}ms each)")
    
    # Validation test
    try:
        Agent(role="Test", goal="Test", max_iter=-1)
    except Exception:
        print("Validation: ✓ Works (caught invalid max_iter)")
    
    # Serialization
    start = time.perf_counter()
    for agent in agents[:100]:
        json.dumps(agent.model_dump())
    serialize_time = (time.perf_counter() - start) * 1000
    print(f"Serialize 100 agents: {serialize_time:.2f}ms")


def benchmark_dataclasses():
    """Benchmark standard dataclasses."""
    print("\n=== DATACLASSES ===")
    
    # Import time
    import_time, import_memory = measure_import(
        "dataclasses",
        "from dataclasses import dataclass, field"
    )
    print(f"Import time: {import_time:.2f}ms")
    print(f"Import memory: {import_memory:.2f}MB")
    
    from dataclasses import dataclass, field, asdict
    
    # Define model
    @dataclass
    class Agent:
        role: str
        goal: str
        backstory: str = ""
        max_iter: int = 25
        tools: List[str] = field(default_factory=list)
        
        def __post_init__(self):
            # Manual validation
            if self.max_iter < 1:
                raise ValueError("max_iter must be >= 1")
    
    # Creation benchmark
    start = time.perf_counter()
    agents = []
    for i in range(1000):
        agent = Agent(
            role=f"Agent {i}",
            goal=f"Goal {i}",
            max_iter=10
        )
        agents.append(agent)
    creation_time = (time.perf_counter() - start) * 1000
    print(f"Create 1000 agents: {creation_time:.2f}ms ({creation_time/1000:.3f}ms each)")
    
    # Validation test
    try:
        Agent(role="Test", goal="Test", max_iter=-1)
    except ValueError:
        print("Validation: ✓ Works (caught invalid max_iter)")
    
    # Serialization
    start = time.perf_counter()
    for agent in agents[:100]:
        json.dumps(asdict(agent))
    serialize_time = (time.perf_counter() - start) * 1000
    print(f"Serialize 100 agents: {serialize_time:.2f}ms")


def benchmark_attrs():
    """Benchmark attrs library."""
    print("\n=== ATTRS ===")
    
    # Import time
    import_time, import_memory = measure_import(
        "attrs",
        "import attrs"
    )
    print(f"Import time: {import_time:.2f}ms")
    print(f"Import memory: {import_memory:.2f}MB")
    
    import attrs
    from typing import List
    
    # Define model
    @attrs.define
    class Agent:
        role: str
        goal: str
        backstory: str = ""
        max_iter: int = attrs.field(default=25, validator=attrs.validators.ge(1))
        tools: List[str] = attrs.field(factory=list)
    
    # Creation benchmark
    start = time.perf_counter()
    agents = []
    for i in range(1000):
        agent = Agent(
            role=f"Agent {i}",
            goal=f"Goal {i}",
            max_iter=10
        )
        agents.append(agent)
    creation_time = (time.perf_counter() - start) * 1000
    print(f"Create 1000 agents: {creation_time:.2f}ms ({creation_time/1000:.3f}ms each)")
    
    # Validation test
    try:
        Agent(role="Test", goal="Test", max_iter=-1)
    except ValueError:
        print("Validation: ✓ Works (caught invalid max_iter)")
    
    # Serialization
    start = time.perf_counter()
    for agent in agents[:100]:
        json.dumps(attrs.asdict(agent))
    serialize_time = (time.perf_counter() - start) * 1000
    print(f"Serialize 100 agents: {serialize_time:.2f}ms")


def benchmark_msgspec():
    """Benchmark msgspec library."""
    print("\n=== MSGSPEC ===")
    
    # Import time
    import_time, import_memory = measure_import(
        "msgspec",
        "import msgspec"
    )
    print(f"Import time: {import_time:.2f}ms")
    print(f"Import memory: {import_memory:.2f}MB")
    
    import msgspec
    from typing import List
    
    # Define model
    class Agent(msgspec.Struct):
        role: str
        goal: str
        backstory: str = ""
        max_iter: int = 25
        tools: List[str] = msgspec.field(default_factory=list)
        
        def __post_init__(self):
            if self.max_iter < 1:
                raise ValueError("max_iter must be >= 1")
    
    # Creation benchmark
    start = time.perf_counter()
    agents = []
    for i in range(1000):
        agent = Agent(
            role=f"Agent {i}",
            goal=f"Goal {i}",
            max_iter=10
        )
        agents.append(agent)
    creation_time = (time.perf_counter() - start) * 1000
    print(f"Create 1000 agents: {creation_time:.2f}ms ({creation_time/1000:.3f}ms each)")
    
    # Validation test
    try:
        Agent(role="Test", goal="Test", max_iter=-1)
    except ValueError:
        print("Validation: ✓ Works (caught invalid max_iter)")
    
    # Serialization
    encoder = msgspec.json.Encoder()
    start = time.perf_counter()
    for agent in agents[:100]:
        encoder.encode(agent)
    serialize_time = (time.perf_counter() - start) * 1000
    print(f"Serialize 100 agents: {serialize_time:.2f}ms")


def benchmark_plain_python():
    """Benchmark plain Python classes."""
    print("\n=== PLAIN PYTHON ===")
    
    # No import needed
    print(f"Import time: 0.00ms")
    print(f"Import memory: 0.00MB")
    
    # Define model
    class Agent:
        def __init__(self, role: str, goal: str, backstory: str = "", 
                     max_iter: int = 25, tools: Optional[List[str]] = None):
            self.role = role
            self.goal = goal
            self.backstory = backstory
            if max_iter < 1:
                raise ValueError("max_iter must be >= 1")
            self.max_iter = max_iter
            self.tools = tools or []
        
        def to_dict(self):
            return {
                'role': self.role,
                'goal': self.goal,
                'backstory': self.backstory,
                'max_iter': self.max_iter,
                'tools': self.tools
            }
    
    # Creation benchmark
    start = time.perf_counter()
    agents = []
    for i in range(1000):
        agent = Agent(
            role=f"Agent {i}",
            goal=f"Goal {i}",
            max_iter=10
        )
        agents.append(agent)
    creation_time = (time.perf_counter() - start) * 1000
    print(f"Create 1000 agents: {creation_time:.2f}ms ({creation_time/1000:.3f}ms each)")
    
    # Validation test
    try:
        Agent(role="Test", goal="Test", max_iter=-1)
    except ValueError:
        print("Validation: ✓ Works (caught invalid max_iter)")
    
    # Serialization
    start = time.perf_counter()
    for agent in agents[:100]:
        json.dumps(agent.to_dict())
    serialize_time = (time.perf_counter() - start) * 1000
    print(f"Serialize 100 agents: {serialize_time:.2f}ms")


def main():
    """Run all benchmarks."""
    print("LiteCrew Model Library Benchmarks")
    print("=" * 50)
    
    # Check available libraries
    libraries = {
        'pydantic': benchmark_pydantic,
        'dataclasses': benchmark_dataclasses,
        'attrs': benchmark_attrs,
        'msgspec': benchmark_msgspec,
        'plain': benchmark_plain_python
    }
    
    # Run benchmarks
    for name, benchmark_func in libraries.items():
        try:
            if name == 'attrs':
                try:
                    import attrs
                except ImportError:
                    print(f"\n=== ATTRS === (not installed)")
                    continue
            elif name == 'msgspec':
                try:
                    import msgspec
                except ImportError:
                    print(f"\n=== MSGSPEC === (not installed)")
                    continue
                    
            benchmark_func()
        except Exception as e:
            print(f"\nError in {name}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()