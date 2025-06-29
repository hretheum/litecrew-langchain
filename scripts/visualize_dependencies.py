#!/usr/bin/env python3
"""
Visualize dependency analysis results
Creates ASCII charts for better understanding of dependency sizes and categories
"""

import json
from pathlib import Path

def load_analysis_data(json_path: str) -> dict:
    """Load the analysis data from JSON file"""
    with open(json_path, 'r') as f:
        return json.load(f)

def create_ascii_bar(value: float, max_value: float, width: int = 40) -> str:
    """Create an ASCII bar chart"""
    filled = int((value / max_value) * width)
    return '█' * filled + '░' * (width - filled)

def format_size(size_mb: float) -> str:
    """Format size for display"""
    if size_mb < 1:
        return f"{int(size_mb * 1024)} KB"
    else:
        return f"{size_mb:.1f} MB"

def print_size_chart(data: dict):
    """Print a size chart of all dependencies"""
    print("\n" + "=" * 80)
    print("DEPENDENCY SIZE CHART")
    print("=" * 80 + "\n")
    
    # Collect all dependencies with sizes
    all_deps = []
    for category, deps in data['categorized'].items():
        for name, info in deps.items():
            all_deps.append({
                'name': name,
                'category': category,
                'size_mb': info.get('size_mb', 0)
            })
    
    # Sort by size (largest first)
    all_deps.sort(key=lambda x: x['size_mb'], reverse=True)
    
    # Find max size for scaling
    max_size = max(dep['size_mb'] for dep in all_deps) if all_deps else 1
    
    # Print chart
    for dep in all_deps[:20]:  # Top 20 largest
        name = dep['name']
        category = dep['category']
        size_mb = dep['size_mb']
        
        bar = create_ascii_bar(size_mb, max_size)
        print(f"{name:20} [{category:12}] {bar} {format_size(size_mb):>8}")
    
    if len(all_deps) > 20:
        print(f"\n... and {len(all_deps) - 20} more dependencies")

def print_category_summary(data: dict):
    """Print summary by category"""
    print("\n" + "=" * 80)
    print("SUMMARY BY CATEGORY")
    print("=" * 80 + "\n")
    
    categories = data['categorized']
    
    # Calculate totals per category
    category_stats = {}
    for category, deps in categories.items():
        total_size = sum(info.get('size_mb', 0) for info in deps.values())
        category_stats[category] = {
            'count': len(deps),
            'size_mb': total_size,
            'deps': deps
        }
    
    # Print summary table
    print(f"{'Category':15} {'Count':>8} {'Total Size':>12} {'Avg Size':>10}")
    print("-" * 50)
    
    total_count = 0
    total_size = 0
    
    for category in ['CORE', 'OPTIONAL', 'REPLACEABLE', 'REMOVABLE']:
        stats = category_stats.get(category, {'count': 0, 'size_mb': 0})
        count = stats['count']
        size_mb = stats['size_mb']
        avg_size = size_mb / count if count > 0 else 0
        
        print(f"{category:15} {count:>8} {format_size(size_mb):>12} {format_size(avg_size):>10}")
        
        total_count += count
        total_size += size_mb
    
    print("-" * 50)
    print(f"{'TOTAL':15} {total_count:>8} {format_size(total_size):>12}")

def print_optimization_impact(data: dict):
    """Print potential optimization impact"""
    print("\n" + "=" * 80)
    print("OPTIMIZATION IMPACT ANALYSIS")
    print("=" * 80 + "\n")
    
    categories = data['categorized']
    
    # Calculate removable size
    removable_size = sum(
        info.get('size_mb', 0) 
        for info in categories.get('REMOVABLE', {}).values()
    )
    
    # Calculate replaceable savings
    replaceable_savings = 0
    for name, info in categories.get('REPLACEABLE', {}).items():
        size_mb = info.get('size_mb', 0)
        reduction = info.get('size_reduction', '0%')
        # Parse reduction percentage
        reduction_pct = float(reduction.strip('~%')) / 100
        replaceable_savings += size_mb * reduction_pct
    
    # Current total size
    total_size = sum(
        sum(info.get('size_mb', 0) for info in deps.values())
        for deps in categories.values()
    )
    
    # Print impact analysis
    print(f"Current total size: {format_size(total_size)}")
    print(f"\nPotential savings:")
    print(f"  - Remove unnecessary deps: -{format_size(removable_size)} ({removable_size/total_size*100:.1f}%)")
    print(f"  - Replace heavy deps:     -{format_size(replaceable_savings)} ({replaceable_savings/total_size*100:.1f}%)")
    print(f"  - Total potential savings: -{format_size(removable_size + replaceable_savings)} ({(removable_size + replaceable_savings)/total_size*100:.1f}%)")
    print(f"\nOptimized size: {format_size(total_size - removable_size - replaceable_savings)}")
    
    # Show specific replaceable dependencies
    print("\n### Replaceable Dependencies Impact:")
    for name, info in categories.get('REPLACEABLE', {}).items():
        size_mb = info.get('size_mb', 0)
        reduction = info.get('size_reduction', '0%')
        reduction_pct = float(reduction.strip('~%')) / 100
        savings = size_mb * reduction_pct
        
        print(f"  - {name}: {format_size(size_mb)} → {format_size(size_mb - savings)} (save {format_size(savings)})")

def print_minimal_install(data: dict):
    """Print minimal installation size"""
    print("\n" + "=" * 80)
    print("MINIMAL INSTALLATION")
    print("=" * 80 + "\n")
    
    core_deps = data['categorized'].get('CORE', {})
    core_size = sum(info.get('size_mb', 0) for info in core_deps.values())
    
    print(f"Core dependencies only: {format_size(core_size)}")
    print("\nIncludes:")
    for name, info in sorted(core_deps.items(), key=lambda x: x[1].get('size_mb', 0), reverse=True):
        print(f"  - {name}: {format_size(info.get('size_mb', 0))}")

def main():
    # Load analysis data
    script_dir = Path(__file__).parent
    json_path = script_dir / "dependency_analysis_data.json"
    
    if not json_path.exists():
        print("Error: dependency_analysis_data.json not found. Run analyze_dependencies.py first.")
        return
    
    data = load_analysis_data(json_path)
    
    # Print various visualizations
    print_size_chart(data)
    print_category_summary(data)
    print_optimization_impact(data)
    print_minimal_install(data)

if __name__ == "__main__":
    main()