"""
Performance benchmarks comparing LiteCrew to CrewAI
"""

import time
import psutil
import gc
from typing import Dict, Any


def measure_import_time(module_name: str) -> float:
    """Measure time to import a module."""
    start = time.perf_counter()
    
    if module_name == "litecrew":
        import litecrew
    elif module_name == "crewai":
        try:
            import crewai
        except ImportError:
            return -1
            
    duration = time.perf_counter() - start
    return duration


def measure_memory_usage() -> Dict[str, Any]:
    """Measure current memory usage."""
    process = psutil.Process()
    mem_info = process.memory_info()
    
    return {
        "rss_mb": mem_info.rss / 1024 / 1024,
        "vms_mb": mem_info.vms / 1024 / 1024,
    }


def benchmark_framework(framework: str) -> Dict[str, Any]:
    """Benchmark a framework."""
    results = {}
    
    # Measure import time
    import_time = measure_import_time(framework)
    results["import_time"] = import_time
    
    if import_time < 0:
        results["error"] = f"{framework} not installed"
        return results
    
    # Measure memory after import
    gc.collect()
    mem_after_import = measure_memory_usage()
    results["memory_after_import_mb"] = mem_after_import["rss_mb"]
    
    # Create basic setup
    if framework == "litecrew":
        from litecrew import LiteAgent, LiteCrew, LiteTask
        
        start = time.perf_counter()
        agent = LiteAgent(
            role="Researcher",
            goal="Research topics",
            backstory="Expert researcher"
        )
        task = LiteTask(
            description="Research AI frameworks",
            agent=agent
        )
        crew = LiteCrew(
            agents=[agent],
            tasks=[task]
        )
        setup_time = time.perf_counter() - start
        
    elif framework == "crewai":
        from crewai import Agent, Crew, Task
        
        start = time.perf_counter()
        agent = Agent(
            role="Researcher",
            goal="Research topics",
            backstory="Expert researcher"
        )
        task = Task(
            description="Research AI frameworks",
            expected_output="Research summary",
            agent=agent
        )
        crew = Crew(
            agents=[agent],
            tasks=[task]
        )
        setup_time = time.perf_counter() - start
        
    results["setup_time"] = setup_time
    
    # Measure memory after setup
    gc.collect()
    mem_after_setup = measure_memory_usage()
    results["memory_after_setup_mb"] = mem_after_setup["rss_mb"]
    results["memory_overhead_mb"] = mem_after_setup["rss_mb"] - mem_after_import["rss_mb"]
    
    return results


def main():
    """Run benchmarks."""
    print("🚀 LiteCrew Performance Benchmark\n")
    
    # Measure baseline
    gc.collect()
    baseline_memory = measure_memory_usage()
    print(f"Baseline memory: {baseline_memory['rss_mb']:.1f}MB\n")
    
    # Benchmark LiteCrew
    print("📊 Benchmarking LiteCrew...")
    litecrew_results = benchmark_framework("litecrew")
    
    # Benchmark CrewAI (if available)
    print("\n📊 Benchmarking CrewAI...")
    crewai_results = benchmark_framework("crewai")
    
    # Print results
    print("\n📈 Results:\n")
    print("| Metric | LiteCrew | CrewAI | Improvement |")
    print("|--------|----------|---------|-------------|")
    
    if "error" not in crewai_results:
        # Import time
        improvement = crewai_results["import_time"] / litecrew_results["import_time"]
        print(f"| Import Time | {litecrew_results['import_time']:.3f}s | {crewai_results['import_time']:.3f}s | {improvement:.1f}x faster |")
        
        # Setup time
        improvement = crewai_results["setup_time"] / litecrew_results["setup_time"]
        print(f"| Setup Time | {litecrew_results['setup_time']:.3f}s | {crewai_results['setup_time']:.3f}s | {improvement:.1f}x faster |")
        
        # Memory overhead
        litecrew_mem = litecrew_results["memory_overhead_mb"]
        crewai_mem = crewai_results["memory_overhead_mb"]
        improvement = crewai_mem / litecrew_mem if litecrew_mem > 0 else 0
        print(f"| Memory Overhead | {litecrew_mem:.1f}MB | {crewai_mem:.1f}MB | {improvement:.1f}x less |")
    else:
        print(f"| Import Time | {litecrew_results['import_time']:.3f}s | N/A | - |")
        print(f"| Setup Time | {litecrew_results['setup_time']:.3f}s | N/A | - |")
        print(f"| Memory Overhead | {litecrew_results['memory_overhead_mb']:.1f}MB | N/A | - |")
        print(f"\nNote: {crewai_results['error']}")
    
    # Success criteria
    print("\n✅ Success Criteria:")
    print(f"- Import time < 0.05s: {'✓' if litecrew_results['import_time'] < 0.05 else '✗'}")
    print(f"- Memory overhead < 30MB: {'✓' if litecrew_results['memory_overhead_mb'] < 30 else '✗'}")
    print(f"- Setup time < 0.1s: {'✓' if litecrew_results['setup_time'] < 0.1 else '✗'}")


if __name__ == "__main__":
    main()