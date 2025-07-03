#!/usr/bin/env python3
# benchmark/scripts/export_results.py
from benchmark_schema import BenchmarkReport

def generate_summary(report: BenchmarkReport) -> str:
    """Generate executive summary"""
    results = []
    for fw in report.frameworks:
        avg_memory = sum(t.memory_mb for t in fw.tests) / len(fw.tests) if fw.tests else 0
        results.append(f"- {fw.framework_name}: {avg_memory:.1f}MB avg, {fw.package_size_mb:.1f}MB package")
    return "\n".join(results)

def format_detailed_results(report: BenchmarkReport) -> str:
    """Format detailed test results"""
    output = []
    for fw in report.frameworks:
        output.append(f"\n{fw.framework_name} v{fw.version}:")
        for test in fw.tests:
            status = "✅" if test.success else "❌"
            output.append(f"  {status} {test.test_name}: {test.memory_mb:.1f}MB, {test.duration_seconds:.2f}s")
    return "\n".join(output)

def analyze_optimization_potential(report: BenchmarkReport) -> str:
    """Analyze optimization opportunities"""
    analysis = []
    for fw in report.frameworks:
        if fw.package_size_mb > 100:
            analysis.append(f"- {fw.framework_name}: High optimization potential (current: {fw.package_size_mb}MB)")
    return "\n".join(analysis) or "No significant optimization opportunities identified"

def export_for_llm(report: BenchmarkReport) -> str:
    """Format optimized for LLM analysis"""
    return f"""
BENCHMARK REPORT - {report.timestamp}

EXECUTIVE SUMMARY:
{generate_summary(report)}

DETAILED RESULTS:
{format_detailed_results(report)}

OPTIMIZATION OPPORTUNITIES:
{analyze_optimization_potential(report)}

RECOMMENDATION:
Based on the data, recommend which framework to use and why.
Consider: performance, size, features, optimization potential.
"""

def export_raw_json(report: BenchmarkReport) -> str:
    """Raw JSON for data analysis"""
    return report.model_dump_json(indent=2)

def export_markdown_table(report: BenchmarkReport) -> str:
    """Markdown table for reports"""
    lines = ["| Framework | Version | Package Size | Avg Memory | Avg Time |"]
    lines.append("|-----------|---------|--------------|------------|----------|")
    
    for fw in report.frameworks:
        avg_memory = sum(t.memory_mb for t in fw.tests) / len(fw.tests) if fw.tests else 0
        avg_time = sum(t.duration_seconds for t in fw.tests) / len(fw.tests) if fw.tests else 0
        lines.append(f"| {fw.framework_name} | {fw.version} | {fw.package_size_mb:.1f}MB | {avg_memory:.1f}MB | {avg_time:.2f}s |")
    
    return "\n".join(lines)