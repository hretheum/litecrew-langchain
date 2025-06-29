#!/usr/bin/env python3
"""
Real Visual Benchmark with actual measurements
Beautiful output for screen recording + real data
"""
import os
import sys
import time
import gc
import psutil
import random
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

# Import the real benchmark
from real_benchmark import RealBenchmark, MemoryTracker

# Visual enhancements
COLORS = {
    "crewai": "bright_yellow",
    "litecrew": "bright_green", 
    "langchain": "bright_blue",
    "pyautogen": "bright_magenta"
}

EMOJIS = {
    "crewai": "🚢",
    "litecrew": "🚀",
    "langchain": "🔗", 
    "pyautogen": "🤖"
}

def print_banner():
    """Print beautiful ASCII banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     🔥 REAL AGENT FRAMEWORK BENCHMARK 2025 🔥                ║
    ║                                                              ║
    ║  Measuring ACTUAL memory usage and performance               ║
    ║  CrewAI vs LangChain vs PyAutoGen vs LiteCrew              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bright_cyan bold")
    time.sleep(2)

def animate_startup():
    """Startup animation with system info"""
    with console.status("[bold green]Initializing benchmark environment...") as status:
        
        # System info
        cpu_count = psutil.cpu_count()
        memory_total = psutil.virtual_memory().total / (1024**3)  # GB
        
        tasks = [
            f"System: {cpu_count} CPU cores, {memory_total:.1f}GB RAM",
            "Loading measurement tools...",
            "Preparing isolated test environments...",
            "Initializing memory trackers...",
            "Setting up performance monitors...",
            "Ready for real measurements!"
        ]
        
        for task in tasks:
            console.log(f"✓ {task}", style="green")
            time.sleep(0.7)
    
    console.print("\n[bold bright_green]✨ All systems ready! Starting REAL benchmark! ✨[/bold bright_green]\n")
    time.sleep(1)

class VisualRealBenchmark(RealBenchmark):
    """Enhanced real benchmark with beautiful visuals"""
    
    def run_all_tests(self):
        """Run all tests with enhanced visuals"""
        print_banner()
        animate_startup()
        
        console.print("[bold]📊 Starting Real Framework Benchmarks[/bold]")
        console.print("[dim]Measuring actual memory usage and performance...[/dim]\n")
        
        test_scenarios = [
            ("import_framework", "Framework Import Test", "Measuring import time and memory overhead"),
            ("create_simple_agent", "Agent Creation Test", "Creating a simple agent instance"),
            ("execute_simple_task", "Task Execution Test", "Running a basic task"),
            ("multi_agent_setup", "Multi-Agent Test", "Setting up multiple agents"),
            ("memory_stress_test", "Memory Stress Test", "Testing memory under load")
        ]
        
        # Create layout for live display
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="progress", size=10),
            Layout(name="results", size=20)
        )
        
        results_by_framework = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(style="cyan"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            for framework_name in self.frameworks:
                emoji = EMOJIS.get(framework_name, "📦")
                color = COLORS.get(framework_name, "white")
                
                console.print(f"\n[bold {color}]{emoji} Testing {framework_name.upper()} {emoji}[/bold {color}]")
                console.print(f"[{color}]{'─' * 50}[/{color}]")
                
                results_by_framework[framework_name] = []
                
                for test_id, test_title, test_desc in test_scenarios:
                    # Create task for this test
                    task = progress.add_task(
                        f"{emoji} [{color}]{framework_name}[/{color}] - {test_title}",
                        total=100
                    )
                    
                    console.print(f"\n[dim]🧪 {test_title}[/dim]")
                    console.print(f"[dim]   {test_desc}[/dim]")
                    
                    # Show live memory before test
                    process = psutil.Process()
                    mem_before = process.memory_info().rss / 1024 / 1024
                    console.print(f"[dim]   Memory before: {mem_before:.1f}MB[/dim]")
                    
                    # Animate progress while running test
                    for i in range(0, 90, 10):
                        progress.update(task, advance=10)
                        time.sleep(0.1)
                    
                    # Run actual test
                    result = self._run_isolated_test(framework_name, test_id)
                    results_by_framework[framework_name].append(result)
                    self.results.append(result)
                    
                    # Complete progress
                    progress.update(task, advance=10)
                    
                    # Show result with color coding
                    if result.success:
                        mem_used = result.total_memory
                        time_used = result.total_time
                        
                        # Color based on performance
                        mem_color = "green" if mem_used < 50 else "yellow" if mem_used < 200 else "red"
                        time_color = "green" if time_used < 0.5 else "yellow" if time_used < 1.0 else "red"
                        
                        console.print(
                            f"   ✅ Result: [{mem_color}]{mem_used:.1f}MB[/{mem_color}] "
                            f"in [{time_color}]{time_used:.3f}s[/{time_color}]"
                        )
                        
                        # Show memory after
                        mem_after = process.memory_info().rss / 1024 / 1024
                        console.print(f"[dim]   Memory after: {mem_after:.1f}MB (Δ {mem_after-mem_before:.1f}MB)[/dim]")
                    else:
                        console.print(f"   ❌ Failed: {result.error}", style="red")
                    
                    # Clean up
                    gc.collect()
                    time.sleep(0.3)
                
                # Framework summary
                self._show_framework_summary(framework_name, results_by_framework[framework_name])
        
        # Show final results with fanfare
        self._display_final_results()
    
    def _show_framework_summary(self, framework: str, results: list):
        """Show summary for a framework"""
        emoji = EMOJIS.get(framework, "📦")
        color = COLORS.get(framework, "white")
        
        total_memory = sum(r.total_memory for r in results if r.success)
        total_time = sum(r.total_time for r in results if r.success)
        passed = sum(1 for r in results if r.success)
        
        console.print(f"\n[{color}]╔══ {framework.upper()} SUMMARY ══╗[/{color}]")
        console.print(f"[{color}]  Tests passed: {passed}/{len(results)}[/{color}]")
        console.print(f"[{color}]  Total memory: {total_memory:.1f}MB[/{color}]")
        console.print(f"[{color}]  Total time: {total_time:.3f}s[/{color}]")
        console.print(f"[{color}]╚{'═' * 25}╝[/{color}]")
    
    def _display_final_results(self):
        """Display final results with visual flair"""
        console.print("\n" + "="*60)
        console.print("[bold bright_yellow]🏆 FINAL BENCHMARK RESULTS 🏆[/bold bright_yellow]".center(60))
        console.print("="*60 + "\n")
        
        # Calculate framework totals
        framework_totals = {}
        for result in self.results:
            if result.success:
                if result.framework not in framework_totals:
                    framework_totals[result.framework] = {
                        'memory': 0, 'time': 0, 'count': 0, 'peak': 0
                    }
                framework_totals[result.framework]['memory'] += result.total_memory
                framework_totals[result.framework]['time'] += result.total_time
                framework_totals[result.framework]['count'] += 1
                framework_totals[result.framework]['peak'] = max(
                    framework_totals[result.framework]['peak'], 
                    result.peak_memory
                )
        
        # Create beautiful results table
        table = Table(title="Performance Comparison", box=box.DOUBLE_EDGE, show_lines=True)
        table.add_column("Rank", style="bold white", justify="center")
        table.add_column("Framework", style="cyan", no_wrap=True)
        table.add_column("Avg Memory", style="yellow", justify="right")
        table.add_column("Peak Memory", style="red", justify="right")
        table.add_column("Avg Time", style="green", justify="right")
        table.add_column("Score", style="bright_white", justify="center")
        
        # Calculate scores and sort
        scores = []
        for fw, totals in framework_totals.items():
            if totals['count'] > 0:
                avg_mem = totals['memory'] / totals['count']
                avg_time = totals['time'] / totals['count']
                # Score: lower is better (memory has more weight)
                score = avg_mem + (avg_time * 50)
                scores.append((fw, avg_mem, totals['peak'], avg_time, score))
        
        scores.sort(key=lambda x: x[4])  # Sort by score (lower is better)
        
        # Add to table with medals
        for i, (fw, avg_mem, peak_mem, avg_time, score) in enumerate(scores):
            rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}"
            emoji = EMOJIS.get(fw, "📦")
            color = COLORS.get(fw, "white")
            
            # Invert score for display (higher is better)
            display_score = 1000 / score if score > 0 else 0
            
            table.add_row(
                rank,
                f"{emoji} [{color}]{fw.upper()}[/{color}]",
                f"{avg_mem:.1f} MB",
                f"{peak_mem:.1f} MB",
                f"{avg_time:.3f} s",
                f"{display_score:.1f}"
            )
        
        console.print(table)
        
        # Winner announcement with animation
        if scores:
            winner = scores[0][0]
            winner_emoji = EMOJIS.get(winner, "📦")
            winner_color = COLORS.get(winner, "white")
            
            # Drumroll effect
            console.print("\n[bold]And the winner is...[/bold]")
            for _ in range(3):
                console.print("🥁", end=" ", style="yellow")
                time.sleep(0.5)
            
            console.print(f"\n\n[bold {winner_color} blink]")
            console.print(f"  {winner_emoji} {winner.upper()} {winner_emoji}  ", style=f"bold {winner_color} on black")
            console.print(f"[/bold {winner_color} blink]")
            
            # Show performance comparison
            if len(scores) > 1:
                improvement = (scores[1][4] / scores[0][4] - 1) * 100
                console.print(f"\n[bright_green]✨ {winner.upper()} is {improvement:.1f}% more efficient! ✨[/bright_green]")
        
        # Memory usage bar chart
        console.print("\n[bold]Memory Usage Comparison:[/bold]")
        max_memory = max(s[1] for s in scores) if scores else 100
        
        for fw, avg_mem, _, _, _ in scores:
            bar_length = int((avg_mem / max_memory) * 40)
            bar = "█" * bar_length
            emoji = EMOJIS.get(fw, "📦")
            color = COLORS.get(fw, "white")
            
            console.print(
                f"{emoji} {fw:10} [{color}]{bar}[/{color}] {avg_mem:.1f}MB"
            )
        
        # Save results
        self._save_results()
        
        # Call to action
        console.print("\n[dim]Share your results: #AgentFrameworkBenchmark[/dim]")
        console.print("[dim]Built with ❤️ using Claude AI[/dim]\n")

def main():
    """Run the visual real benchmark"""
    # Clear screen for recording
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # Run benchmark
    benchmark = VisualRealBenchmark()
    
    try:
        benchmark.run_all_tests()
    except KeyboardInterrupt:
        console.print("\n[red]Benchmark interrupted by user[/red]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()