#!/usr/bin/env python3
"""
Dependency management script for LiteCrewAI.
Helps manage different dependency configurations and analyze package sizes.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import pkg_resources
import importlib.metadata


class DependencyManager:
    """Manages LiteCrewAI dependencies."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.requirements_dir = base_path / "requirements"
        self.constraints_file = base_path / "constraints.txt"
        
    def install_base(self, use_constraints: bool = True) -> None:
        """Install only core dependencies."""
        print("Installing base dependencies...")
        cmd = ["pip", "install", "-r", str(self.requirements_dir / "base.txt")]
        if use_constraints:
            cmd.extend(["-c", str(self.constraints_file)])
        subprocess.run(cmd, check=True)
        
    def install_dev(self, use_constraints: bool = True) -> None:
        """Install development dependencies."""
        print("Installing development dependencies...")
        cmd = ["pip", "install", "-r", str(self.requirements_dir / "dev.txt")]
        if use_constraints:
            cmd.extend(["-c", str(self.constraints_file)])
        subprocess.run(cmd, check=True)
        
    def install_optional(self, packages: Optional[List[str]] = None, use_constraints: bool = True) -> None:
        """Install optional dependencies."""
        optional_file = self.requirements_dir / "optional.txt"
        
        if packages:
            # Install specific packages
            for package in packages:
                print(f"Installing optional package: {package}")
                cmd = ["pip", "install", package]
                if use_constraints:
                    cmd.extend(["-c", str(self.constraints_file)])
                subprocess.run(cmd, check=True)
        else:
            # Install all optional dependencies
            print("Installing all optional dependencies...")
            cmd = ["pip", "install", "-r", str(optional_file)]
            if use_constraints:
                cmd.extend(["-c", str(self.constraints_file)])
            subprocess.run(cmd, check=True)
    
    def list_installed(self) -> Dict[str, str]:
        """List all installed packages with versions."""
        installed = {}
        for dist in pkg_resources.working_set:
            installed[dist.key] = dist.version
        return installed
    
    def check_size(self) -> Dict[str, float]:
        """Check the size of installed packages."""
        sizes = {}
        
        for dist in pkg_resources.working_set:
            try:
                # Get the distribution's location
                location = dist.location
                if location:
                    size_bytes = 0
                    dist_path = Path(location) / f"{dist.key}-{dist.version}.dist-info"
                    
                    if dist_path.exists():
                        # Calculate size
                        for file in dist_path.rglob("*"):
                            if file.is_file():
                                size_bytes += file.stat().st_size
                    
                    # Also check the actual package directory
                    package_name = dist.key.replace("-", "_")
                    package_path = Path(location) / package_name
                    if package_path.exists():
                        for file in package_path.rglob("*"):
                            if file.is_file():
                                size_bytes += file.stat().st_size
                    
                    sizes[dist.key] = size_bytes / (1024 * 1024)  # Convert to MB
            except Exception:
                pass
                
        return sizes
    
    def analyze_dependencies(self) -> None:
        """Analyze current dependency status."""
        print("\n=== Dependency Analysis ===\n")
        
        # Load requirements files
        base_deps = self._parse_requirements_file(self.requirements_dir / "base.txt")
        optional_deps = self._parse_requirements_file(self.requirements_dir / "optional.txt")
        
        # Get installed packages
        installed = self.list_installed()
        
        # Check base dependencies
        print("Core Dependencies:")
        for dep in base_deps:
            status = "✓" if dep in installed else "✗"
            version = installed.get(dep, "Not installed")
            print(f"  {status} {dep}: {version}")
        
        print("\nOptional Dependencies:")
        for dep in optional_deps:
            status = "✓" if dep in installed else "✗"
            version = installed.get(dep, "Not installed")
            print(f"  {status} {dep}: {version}")
        
        # Show size information
        print("\n=== Package Sizes ===\n")
        sizes = self.check_size()
        total_size = 0
        
        for package, size in sorted(sizes.items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"  {package}: {size:.1f} MB")
            total_size += size
            
        print(f"\nTotal size of top 20 packages: {total_size:.1f} MB")
    
    def _parse_requirements_file(self, file_path: Path) -> Set[str]:
        """Parse a requirements file to extract package names."""
        packages = set()
        
        if not file_path.exists():
            return packages
            
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-r"):
                    # Extract package name (before any version specifier)
                    for sep in [">=", "==", "<=", ">", "<", "~=", "!="]:
                        if sep in line:
                            package_name = line.split(sep)[0].strip()
                            break
                    else:
                        package_name = line.split("[")[0].strip()
                    
                    packages.add(package_name.lower())
                    
        return packages
    
    def create_minimal_env(self) -> None:
        """Create a minimal environment with only core dependencies."""
        print("Creating minimal environment...")
        
        # Create a new virtual environment
        venv_path = self.base_path / ".venv-minimal"
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        
        # Install base dependencies in the new environment
        pip_path = venv_path / "bin" / "pip" if sys.platform != "win32" else venv_path / "Scripts" / "pip.exe"
        subprocess.run([str(pip_path), "install", "-r", str(self.requirements_dir / "base.txt")], check=True)
        
        print(f"Minimal environment created at: {venv_path}")
        print(f"Activate with: source {venv_path}/bin/activate")


def main():
    parser = argparse.ArgumentParser(description="Manage LiteCrewAI dependencies")
    parser.add_argument("--base-path", type=Path, 
                       default=Path("/Users/hretheum/dev/bezrobocie/crewAI/crewai-fork"),
                       help="Base path of the LiteCrewAI project")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Install commands
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.add_argument("profile", choices=["base", "dev", "optional", "all"],
                               help="Which dependency profile to install")
    install_parser.add_argument("--packages", nargs="+", 
                               help="Specific optional packages to install")
    install_parser.add_argument("--no-constraints", action="store_true",
                               help="Don't use constraints file")
    
    # Analysis commands
    subparsers.add_parser("analyze", help="Analyze installed dependencies")
    subparsers.add_parser("size", help="Check package sizes")
    subparsers.add_parser("minimal", help="Create minimal environment")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = DependencyManager(args.base_path)
    
    if args.command == "install":
        use_constraints = not args.no_constraints
        
        if args.profile == "base":
            manager.install_base(use_constraints)
        elif args.profile == "dev":
            manager.install_dev(use_constraints)
        elif args.profile == "optional":
            manager.install_optional(args.packages, use_constraints)
        elif args.profile == "all":
            manager.install_dev(use_constraints)
            manager.install_optional(use_constraints=use_constraints)
            
    elif args.command == "analyze":
        manager.analyze_dependencies()
        
    elif args.command == "size":
        sizes = manager.check_size()
        for package, size in sorted(sizes.items(), key=lambda x: x[1], reverse=True):
            print(f"{package}: {size:.1f} MB")
            
    elif args.command == "minimal":
        manager.create_minimal_env()


if __name__ == "__main__":
    main()