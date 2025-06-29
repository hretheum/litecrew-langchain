#!/usr/bin/env python3
"""
Visual wrapper for existing benchmark infrastructure
Uses the virtualenvs and scripts already created
"""
import subprocess
import json
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich import box

# Import existing schemas
import sys
sys.path.append('scripts')
from benchmark_schema import BenchmarkResult, FrameworkResult, BenchmarkReport
from run_framework import run_in_env

console = Console()

def run_benchmark_in_venv(framework: str, test_script: str):
    """Run benchmark using existing virtualenv"""
    env_name = {
        "crewai": "crewai_official",
        "langchain": "langchain", 
        "pyautogen": "autogpt",
        "litecrew": "litecrew_fork"
    }.get(framework, framework)
    
    # Use existing run_framework.py
    result = run_in_env(env_name, test_script)
    return result

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Visual benchmark for agent frameworks')
    parser.add_argument('frameworks', nargs='*', 
                       choices=['crewai', 'langchain', 'pyautogen', 'litecrew'],
                       help='Frameworks to test (default: all)')
    args = parser.parse_args()
    
    console.print("[bold cyan]🚀 VISUAL BENCHMARK USING EXISTING INFRASTRUCTURE[/bold cyan]\n")
    
    # Check if envs exist
    envs_path = Path("envs")
    if not envs_path.exists():
        console.print("[red]Error: envs/ directory not found![/red]")
        console.print("Run this from the benchmark directory!")
        return
    
    # List available environments
    console.print("[yellow]Found virtual environments:[/yellow]")
    for env in envs_path.iterdir():
        if env.is_dir():
            console.print(f"  ✓ {env.name}")
    
    # Create test script that will run in each env
    test_script_content = '''
import time
import psutil
import sys
import json

# Test framework import
start_time = time.time()
process = psutil.Process()
mem_before = process.memory_info().rss / 1024 / 1024

try:
    if "crewai" in sys.prefix:
        import crewai
        framework = "crewai"
    elif "langchain" in sys.prefix:
        import langchain
        framework = "langchain"
    elif "autogpt" in sys.prefix:
        import autogen
        framework = "pyautogen"
    elif "litecrew" in sys.prefix:
        # This would be the fork
        framework = "litecrew"
    else:
        framework = "unknown"
        
    import_time = time.time() - start_time
    mem_after = process.memory_info().rss / 1024 / 1024
    
    result = {
        "framework": framework,
        "import_time": import_time,
        "import_memory": mem_after - mem_before,
        "success": True
    }
except Exception as e:
    result = {
        "framework": framework if 'framework' in locals() else "unknown",
        "import_time": 0,
        "import_memory": 0,
        "success": False,
        "error": str(e)
    }

print(json.dumps(result))
'''
    
    # Write test script
    test_file = Path("test_import.py")
    test_file.write_text(test_script_content)
    
    # Run tests with visual progress
    results = []
    
    # Map framework names to env names
    framework_map = {
        'crewai': 'crewai_official',
        'langchain': 'langchain',
        'pyautogen': 'autogpt',
        'litecrew': 'litecrew_fork'
    }
    
    # Determine which frameworks to test
    if args.frameworks:
        frameworks = [framework_map[f] for f in args.frameworks]
        console.print(f"[yellow]Testing selected frameworks: {', '.join(args.frameworks)}[/yellow]\n")
    else:
        frameworks = ["crewai_official", "langchain", "autogpt", "litecrew_fork"]
        console.print("[yellow]Testing all frameworks[/yellow]\n")
    
    for env in track(frameworks, description="Testing frameworks..."):
        console.print(f"\n[cyan]Testing {env}...[/cyan]")
        
        try:
            # Run test in virtualenv
            result = subprocess.run(
                f"source envs/{env}/bin/activate && python test_import.py",
                shell=True,
                capture_output=True,
                text=True,
                executable="/bin/bash"
            )
            
            if result.stdout:
                data = json.loads(result.stdout)
                results.append(data)
                
                if data["success"]:
                    console.print(f"  ✅ Import time: {data['import_time']:.3f}s")
                    console.print(f"  ✅ Memory used: {data['import_memory']:.1f}MB")
                else:
                    console.print(f"  ❌ Failed: {data.get('error', 'Unknown error')}")
            else:
                console.print(f"  ❌ No output from test")
                if result.stderr:
                    console.print(f"  Error: {result.stderr}")
                    
        except Exception as e:
            console.print(f"  ❌ Error running test: {e}")
    
    # Display results
    console.print("\n[bold]📊 RESULTS[/bold]\n")
    
    table = Table(title="Framework Comparison", box=box.ROUNDED)
    table.add_column("Framework", style="cyan")
    table.add_column("Import Time", style="green")
    table.add_column("Memory Usage", style="yellow")
    table.add_column("Status", style="white")
    
    for r in results:
        if r["success"]:
            table.add_row(
                r["framework"],
                f"{r['import_time']:.3f}s",
                f"{r['import_memory']:.1f}MB",
                "✅ Success"
            )
        else:
            table.add_row(
                r["framework"],
                "-",
                "-",
                "❌ Failed"
            )
    
    console.print(table)
    
    # Cleanup
    test_file.unlink()

if __name__ == "__main__":
    main()