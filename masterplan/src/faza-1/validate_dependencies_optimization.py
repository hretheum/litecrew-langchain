#!/usr/bin/env python3
"""
Validate Dependencies Optimization
Checks if dependency optimization was successful
"""

import os
import subprocess
import sys
import json
from pathlib import Path


def check_analysis_reports_exist(repo_path):
    """Check if dependency analysis reports were generated"""
    reports = [
        "../scripts/dependency_analysis_report.md",
        "../scripts/dependency_analysis_data.json"
    ]
    
    missing = []
    for report in reports:
        full_path = os.path.join(repo_path, report)
        if not os.path.exists(full_path):
            missing.append(report)
    
    if missing:
        return False, f"Missing analysis reports: {', '.join(missing)}"
    
    return True, "Analysis reports generated"


def check_dependency_count_reduced(repo_path):
    """Check if dependencies were significantly reduced"""
    json_path = os.path.join(repo_path, "../scripts/dependency_analysis_data.json")
    
    if not os.path.exists(json_path):
        return False, "Analysis data not found"
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        total_deps = len(data.get('dependencies', {}).get('main', {}))
        categorization = data.get('categorized', {})
        core_deps = len(categorization.get('CORE', {}))
        
        if core_deps > 10:
            return False, f"Too many core dependencies: {core_deps} (should be ≤10)"
        
        if total_deps > 25:
            return False, f"Too many total dependencies: {total_deps}"
        
        return True, f"Dependencies optimized: {core_deps} core, {total_deps} total"
        
    except Exception as e:
        return False, f"Error reading analysis data: {str(e)}"


def check_size_reduction_potential(repo_path):
    """Check if significant size reduction was identified"""
    json_path = os.path.join(repo_path, "../scripts/dependency_analysis_data.json")
    
    if not os.path.exists(json_path):
        return False, "Analysis data not found"
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        categorization = data.get('categorized', {})
        
        # Calculate total size and potential savings
        total_size = 0
        potential_savings = 0
        
        removable_deps = categorization.get('REMOVABLE', {})
        replaceable_deps = categorization.get('REPLACEABLE', {})
        
        # Calculate total size from all categories
        for category_deps in categorization.values():
            for dep, info in category_deps.items():
                total_size += info.get('size_mb', 0)
        
        # Calculate potential savings from removable deps
        for dep, info in removable_deps.items():
            potential_savings += info.get('size_mb', 0)
        
        # Add estimated savings from replaceable (assume 70% reduction)
        for dep, info in replaceable_deps.items():
            potential_savings += info.get('size_mb', 0) * 0.7
        
        if potential_savings < 100:  # Should save at least 100MB
            return False, f"Insufficient savings identified: {potential_savings}MB"
        
        savings_percent = (potential_savings / total_size) * 100 if total_size > 0 else 0
        
        if savings_percent < 50:  # Should save at least 50%
            return False, f"Savings percentage too low: {savings_percent:.1f}%"
        
        return True, f"Excellent savings potential: {potential_savings}MB ({savings_percent:.1f}%)"
        
    except Exception as e:
        return False, f"Error calculating savings: {str(e)}"


def check_categorization_complete(repo_path):
    """Check if all dependencies were properly categorized"""
    json_path = os.path.join(repo_path, "../scripts/dependency_analysis_data.json")
    
    if not os.path.exists(json_path):
        return False, "Analysis data not found"
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        categorization = data.get('categorized', {})
        categories = ['CORE', 'OPTIONAL', 'REPLACEABLE', 'REMOVABLE']
        
        categorized_count = {}
        for category in categories:
            categorized_count[category] = len(categorization.get(category, {}))
        
        total_categorized = sum(categorized_count.values())
        total_deps = len(data.get('dependencies', {}).get('main', {}))
        
        if total_categorized != total_deps:
            return False, f"Not all deps categorized: {total_categorized}/{total_deps}"
        
        # Check if we have some of each category
        if categorized_count['REMOVABLE'] == 0:
            return False, "No removable dependencies identified"
        
        return True, f"All {total_deps} dependencies categorized: {categorized_count}"
        
    except Exception as e:
        return False, f"Error checking categorization: {str(e)}"


def check_visualization_generated(repo_path):
    """Check if dependency visualization was generated"""
    viz_script = os.path.join(repo_path, "../scripts/visualize_dependencies.py")
    
    if not os.path.exists(viz_script):
        return False, "Visualization script not found"
    
    # Test if script runs without error
    try:
        result = subprocess.run(
            [sys.executable, viz_script],
            cwd=os.path.dirname(viz_script),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return False, f"Visualization script failed: {result.stderr}"
        
        # Check if output contains expected sections
        required_sections = [
            "DEPENDENCY SIZE CHART",
            "SUMMARY BY CATEGORY", 
            "OPTIMIZATION IMPACT",
            "MINIMAL INSTALLATION"
        ]
        
        missing_sections = [s for s in required_sections if s not in result.stdout]
        
        if missing_sections:
            return False, f"Missing visualization sections: {', '.join(missing_sections)}"
        
        return True, "Visualization generated successfully"
        
    except Exception as e:
        return False, f"Error running visualization: {str(e)}"


def main():
    """Run all validation checks"""
    repo_path = "/Users/hretheum/dev/bezrobocie/crewAI/crewai-fork"
    
    print("🔍 Validating Dependencies Optimization...")
    print("=" * 50)
    
    checks = [
        ("Analysis reports exist", lambda: check_analysis_reports_exist(repo_path)),
        ("Dependency count reduced", lambda: check_dependency_count_reduced(repo_path)),
        ("Size reduction potential", lambda: check_size_reduction_potential(repo_path)),
        ("Categorization complete", lambda: check_categorization_complete(repo_path)),
        ("Visualization generated", lambda: check_visualization_generated(repo_path))
    ]
    
    all_passed = True
    optimization_score = 0
    
    for check_name, check_func in checks:
        passed, message = check_func()
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {message}")
        if not passed:
            all_passed = False
        else:
            optimization_score += 1
    
    print("=" * 50)
    print(f"📊 Optimization Score: {optimization_score}/5")
    
    if optimization_score >= 4:
        print("✅ Excellent dependency optimization!")
    elif optimization_score >= 3:
        print("🟡 Good optimization with minor issues")
    else:
        print("❌ Dependency optimization needs improvement")
    
    if all_passed:
        print("✅ All dependency optimization checks passed!")
        return 0
    else:
        print("❌ Some dependency optimization checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())