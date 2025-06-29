#!/usr/bin/env python3
"""
CrewAI Dependency Analysis Script
Analyzes dependencies from pyproject.toml and categorizes them for optimization.
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import re

class DependencyAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.pyproject_path = self.project_path / "pyproject.toml"
        self.dependencies = {}
        self.categorized_deps = {
            "CORE": {},
            "OPTIONAL": {},
            "REPLACEABLE": {},
            "REMOVABLE": {}
        }
        
    def load_dependencies(self) -> Dict:
        """Load dependencies from pyproject.toml"""
        with open(self.pyproject_path, "r") as f:
            content = f.read()
        
        # Parse main dependencies
        main_deps = self._extract_dependencies(content, r'\[project\].*?dependencies\s*=\s*\[(.*?)\]', True)
        self.dependencies["main"] = self._parse_deps(main_deps)
        
        # Parse optional dependencies
        optional_match = re.search(r'\[project\.optional-dependencies\](.*?)(?=\[|$)', content, re.DOTALL)
        if optional_match:
            optional_content = optional_match.group(1)
            # Find each optional dependency group
            for match in re.finditer(r'(\w+)\s*=\s*\[(.*?)\]', optional_content, re.DOTALL):
                group_name = match.group(1)
                deps = self._extract_dep_list(match.group(2))
                self.dependencies[f"optional-{group_name}"] = self._parse_deps(deps)
        
        # Parse dev dependencies
        dev_deps = self._extract_dependencies(content, r'\[tool\.uv\].*?dev-dependencies\s*=\s*\[(.*?)\]', True)
        self.dependencies["dev"] = self._parse_deps(dev_deps)
        
        return self.dependencies
    
    def _extract_dependencies(self, content: str, pattern: str, multiline: bool = False) -> List[str]:
        """Extract dependencies using regex pattern"""
        flags = re.DOTALL if multiline else 0
        match = re.search(pattern, content, flags)
        if match:
            dep_content = match.group(1)
            return self._extract_dep_list(dep_content)
        return []
    
    def _extract_dep_list(self, dep_content: str) -> List[str]:
        """Extract individual dependencies from content"""
        deps = []
        # Match quoted strings
        for match in re.finditer(r'"([^"]+)"', dep_content):
            deps.append(match.group(1))
        return deps
    
    def _parse_deps(self, deps: List[str]) -> Dict[str, str]:
        """Parse dependency strings into name and version spec"""
        parsed = {}
        for dep in deps:
            # Handle different dependency formats
            match = re.match(r'^([a-zA-Z0-9_-]+)(.*)$', dep)
            if match:
                name = match.group(1)
                version_spec = match.group(2).strip()
                parsed[name] = version_spec
        return parsed
    
    def get_package_size(self, package_name: str) -> Optional[int]:
        """Get the estimated size of a package in bytes"""
        # Package size estimates in MB
        size_estimates = {
            # Core Dependencies
            "pydantic": 2.5,
            "python-dotenv": 0.02,
            "click": 0.6,
            "jsonref": 0.02,
            "tomli-w": 0.01,
            "tomli": 0.02,
            "blinker": 0.02,
            
            # LLM/AI Dependencies
            "openai": 0.8,
            "litellm": 15.0,
            "instructor": 0.5,
            
            # Document Processing
            "pdfplumber": 5.0,
            "openpyxl": 2.5,
            
            # ML/Data Processing
            "chromadb": 45.0,
            "tokenizers": 15.0,
            "onnxruntime": 150.0,
            "regex": 0.4,
            
            # Visualization
            "pyvis": 0.5,
            
            # Utilities
            "appdirs": 0.02,
            "json-repair": 0.1,
            "json5": 0.03,
            "uv": 25.0,
        }
        
        # Get size in MB, default to 0.5 MB for unknown packages
        size_mb = size_estimates.get(package_name, 0.5)
        # Convert to bytes
        return int(size_mb * 1024 * 1024)
    
    
    def categorize_dependencies(self):
        """Categorize dependencies based on their purpose and necessity"""
        
        # Core dependencies - absolutely required
        core_deps = {
            "pydantic": "Data validation and settings management - CORE framework requirement",
            "click": "CLI framework - required for crewai command",
            "python-dotenv": "Environment variable management - security requirement",
            "jsonref": "JSON reference resolution - required for configuration",
            "tomli": "TOML parsing for Python < 3.11",
            "tomli-w": "TOML writing capability",
            "blinker": "Event dispatching system - core functionality"
        }
        
        # Optional features
        optional_deps = {
            "openai": "OpenAI API integration - can use other LLMs",
            "instructor": "Structured output from LLMs - optional feature",
            "tokenizers": "Text tokenization - optional for embeddings",
            "regex": "Advanced regex - could use standard re module"
        }
        
        # Replaceable with lighter alternatives
        replaceable_deps = {
            "chromadb": {
                "reason": "Heavy vector database",
                "alternatives": ["faiss-cpu", "annoy", "simple in-memory solution"],
                "size_reduction": "~90%"
            },
            "onnxruntime": {
                "reason": "Large ML runtime",
                "alternatives": ["onnxruntime-mobile", "custom implementation"],
                "size_reduction": "~70%"
            },
            "pdfplumber": {
                "reason": "Heavy PDF processing",
                "alternatives": ["pypdf", "pdftotext"],
                "size_reduction": "~50%"
            },
            "litellm": {
                "reason": "Large LLM abstraction",
                "alternatives": ["direct API calls", "minimal wrapper"],
                "size_reduction": "~80%"
            }
        }
        
        # Removable - not needed for core functionality
        removable_deps = {
            "pyvis": "Network visualization - rarely used feature",
            "openpyxl": "Excel processing - specific use case",
            "appdirs": "App directory paths - can be hardcoded",
            "json-repair": "JSON repair - edge case handling",
            "json5": "JSON5 format support - rarely needed",
            "uv": "Package installer - only needed for development"
        }
        
        # Categorize main dependencies
        for dep_name, version_spec in self.dependencies.get("main", {}).items():
            size = self.get_package_size(dep_name)
            
            if dep_name in core_deps:
                self.categorized_deps["CORE"][dep_name] = {
                    "version": version_spec,
                    "reason": core_deps[dep_name],
                    "size_bytes": size,
                    "size_mb": round(size / 1024 / 1024, 2) if size else "Unknown"
                }
            elif dep_name in optional_deps:
                self.categorized_deps["OPTIONAL"][dep_name] = {
                    "version": version_spec,
                    "reason": optional_deps[dep_name],
                    "size_bytes": size,
                    "size_mb": round(size / 1024 / 1024, 2) if size else "Unknown"
                }
            elif dep_name in replaceable_deps:
                self.categorized_deps["REPLACEABLE"][dep_name] = {
                    "version": version_spec,
                    "reason": replaceable_deps[dep_name]["reason"],
                    "alternatives": replaceable_deps[dep_name]["alternatives"],
                    "size_reduction": replaceable_deps[dep_name]["size_reduction"],
                    "size_bytes": size,
                    "size_mb": round(size / 1024 / 1024, 2) if size else "Unknown"
                }
            elif dep_name in removable_deps:
                self.categorized_deps["REMOVABLE"][dep_name] = {
                    "version": version_spec,
                    "reason": removable_deps[dep_name],
                    "size_bytes": size,
                    "size_mb": round(size / 1024 / 1024, 2) if size else "Unknown"
                }
            else:
                # Uncategorized - need manual review
                self.categorized_deps["OPTIONAL"][dep_name] = {
                    "version": version_spec,
                    "reason": "Uncategorized - needs manual review",
                    "size_bytes": size,
                    "size_mb": round(size / 1024 / 1024, 2) if size else "Unknown"
                }
    
    def generate_report(self) -> str:
        """Generate comprehensive dependency analysis report"""
        report = []
        report.append("# CrewAI Dependency Analysis Report")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("\n## Executive Summary")
        
        # Calculate totals
        total_deps = sum(len(deps) for deps in self.categorized_deps.values())
        total_size = 0
        for category, deps in self.categorized_deps.items():
            for dep_name, info in deps.items():
                size = info.get("size_bytes")
                if size and isinstance(size, (int, float)):
                    total_size += size
        
        report.append(f"- Total dependencies analyzed: {total_deps}")
        report.append(f"- Total estimated size: {round(total_size / 1024 / 1024, 2)} MB")
        report.append(f"- Core dependencies: {len(self.categorized_deps['CORE'])}")
        report.append(f"- Optional dependencies: {len(self.categorized_deps['OPTIONAL'])}")
        report.append(f"- Replaceable dependencies: {len(self.categorized_deps['REPLACEABLE'])}")
        report.append(f"- Removable dependencies: {len(self.categorized_deps['REMOVABLE'])}")
        
        # Detailed sections
        for category in ["CORE", "OPTIONAL", "REPLACEABLE", "REMOVABLE"]:
            report.append(f"\n## {category} Dependencies")
            
            if category == "CORE":
                report.append("These dependencies are absolutely required for basic CrewAI functionality.")
            elif category == "OPTIONAL":
                report.append("These dependencies enable specific features but aren't required for core functionality.")
            elif category == "REPLACEABLE":
                report.append("These dependencies can be replaced with lighter alternatives.")
            elif category == "REMOVABLE":
                report.append("These dependencies can be removed without affecting core functionality.")
            
            deps = self.categorized_deps[category]
            if not deps:
                report.append("*No dependencies in this category*")
                continue
                
            # Sort by size (largest first)
            sorted_deps = sorted(
                deps.items(), 
                key=lambda x: x[1].get("size_bytes", 0) or 0, 
                reverse=True
            )
            
            for dep_name, info in sorted_deps:
                report.append(f"\n### {dep_name} {info['version']}")
                report.append(f"- **Size**: {info['size_mb']} MB")
                report.append(f"- **Reason**: {info['reason']}")
                
                if category == "REPLACEABLE" and "alternatives" in info:
                    report.append(f"- **Alternatives**: {', '.join(info['alternatives'])}")
                    report.append(f"- **Potential size reduction**: {info['size_reduction']}")
        
        # Optimization recommendations
        report.append("\n## Optimization Recommendations")
        report.append("\n### Quick Wins (High Impact, Low Effort)")
        
        removable_size = sum(
            info.get("size_bytes") or 0
            for info in self.categorized_deps["REMOVABLE"].values()
        )
        report.append(f"1. **Remove unnecessary dependencies**: Save ~{round(removable_size / 1024 / 1024, 2)} MB")
        report.append("   - Remove: " + ", ".join(self.categorized_deps["REMOVABLE"].keys()))
        
        report.append("\n2. **Make heavy dependencies optional**:")
        heavy_optional = [
            (name, info) for name, info in self.categorized_deps["OPTIONAL"].items()
            if (info.get("size_bytes") or 0) > 10 * 1024 * 1024  # > 10MB
        ]
        for name, info in heavy_optional:
            report.append(f"   - Move {name} ({info['size_mb']} MB) to optional group")
        
        report.append("\n### Medium-term Optimizations")
        report.append("1. **Replace heavy dependencies with lighter alternatives**:")
        for name, info in self.categorized_deps["REPLACEABLE"].items():
            report.append(f"   - Replace {name} ({info['size_mb']} MB) → {info['size_reduction']} reduction")
        
        report.append("\n2. **Implement lazy loading for optional features**")
        report.append("3. **Create minimal installation profiles** (core, standard, full)")
        
        # Proposed dependency groups
        report.append("\n## Proposed Dependency Groups")
        report.append("\n### crewai-core (Minimal)")
        report.append("```toml")
        report.append("[project]")
        report.append("dependencies = [")
        for dep in self.categorized_deps["CORE"].keys():
            version = self.categorized_deps["CORE"][dep]["version"]
            report.append(f'    "{dep}{version}",')
        report.append("]")
        report.append("```")
        
        report.append("\n### Optional Feature Groups")
        report.append("```toml")
        report.append("[project.optional-dependencies]")
        report.append("llm = [")
        for dep in ["openai", "litellm", "instructor"]:
            if dep in self.categorized_deps["OPTIONAL"]:
                version = self.categorized_deps["OPTIONAL"][dep]["version"]
                report.append(f'    "{dep}{version}",')
        report.append("]")
        report.append("embeddings = [")
        for dep in ["tokenizers", "onnxruntime", "chromadb"]:
            if dep in self.categorized_deps["OPTIONAL"] or dep in self.categorized_deps["REPLACEABLE"]:
                info = self.categorized_deps.get("OPTIONAL", {}).get(dep) or self.categorized_deps.get("REPLACEABLE", {}).get(dep)
                if info:
                    report.append(f'    "{dep}{info["version"]}",')
        report.append("]")
        report.append("documents = [")
        for dep in ["pdfplumber", "openpyxl"]:
            if dep in self.categorized_deps["OPTIONAL"] or dep in self.categorized_deps["REPLACEABLE"]:
                info = self.categorized_deps.get("OPTIONAL", {}).get(dep) or self.categorized_deps.get("REPLACEABLE", {}).get(dep)
                if info:
                    report.append(f'    "{dep}{info["version"]}",')
        report.append("]")
        report.append("```")
        
        return "\n".join(report)
    
    def save_report(self, output_path: str):
        """Save the report to a file"""
        report = self.generate_report()
        with open(output_path, "w") as f:
            f.write(report)
        print(f"Report saved to: {output_path}")
    
    def save_json_data(self, output_path: str):
        """Save raw analysis data as JSON"""
        data = {
            "analysis_date": datetime.now().isoformat(),
            "dependencies": self.dependencies,
            "categorized": self.categorized_deps
        }
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"JSON data saved to: {output_path}")


def main():
    # Get project path
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "/Users/hretheum/dev/bezrobocie/crewAI/crewai-fork"
    
    print(f"Analyzing dependencies for: {project_path}")
    
    # Create analyzer
    analyzer = DependencyAnalyzer(project_path)
    
    # Load and analyze dependencies
    print("Loading dependencies from pyproject.toml...")
    analyzer.load_dependencies()
    
    print("Categorizing dependencies...")
    analyzer.categorize_dependencies()
    
    # Generate reports
    script_dir = Path(__file__).parent
    report_path = script_dir / "dependency_analysis_report.md"
    json_path = script_dir / "dependency_analysis_data.json"
    
    print("Generating report...")
    analyzer.save_report(report_path)
    analyzer.save_json_data(json_path)
    
    # Print summary
    print("\n=== Analysis Complete ===")
    print(f"Markdown report: {report_path}")
    print(f"JSON data: {json_path}")


if __name__ == "__main__":
    main()