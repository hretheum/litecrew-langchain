#!/usr/bin/env python3
"""
LiteCrewAI Dependency Cache Management Script

This script manages the local dependency cache for LiteCrewAI, including:
- Creating and updating wheel files
- Managing the pip cache
- Generating requirements lock files
- Cleaning up old cache entries
- Offline installation support
- GitLab CI cache integration
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Configuration
CACHE_ROOT = Path.home() / ".litecrewai" / "cache"
PROJECT_ROOT = Path(__file__).parent.parent / "crewai-fork"
WHEELHOUSE_DIR = PROJECT_ROOT / ".pip" / "wheelhouse"
CACHE_DIR = PROJECT_ROOT / ".pip" / "cache"
DOWNLOAD_DIR = PROJECT_ROOT / ".pip" / "downloads"
REQUIREMENTS_DIR = PROJECT_ROOT / "requirements"
CACHE_METADATA_FILE = CACHE_ROOT / "cache_metadata.json"


class DependencyCacheManager:
    """Manages dependency caching for LiteCrewAI"""
    
    def __init__(self):
        self.ensure_directories()
        self.metadata = self.load_metadata()
    
    def ensure_directories(self):
        """Create necessary cache directories"""
        for directory in [CACHE_ROOT, WHEELHOUSE_DIR, CACHE_DIR, DOWNLOAD_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def load_metadata(self) -> Dict:
        """Load cache metadata"""
        if CACHE_METADATA_FILE.exists():
            with open(CACHE_METADATA_FILE, 'r') as f:
                return json.load(f)
        return {
            "created": datetime.now().isoformat(),
            "wheels": {},
            "downloads": {},
            "last_cleanup": None
        }
    
    def save_metadata(self):
        """Save cache metadata"""
        with open(CACHE_METADATA_FILE, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def get_requirements_hash(self) -> str:
        """Calculate hash of all requirements files"""
        hasher = hashlib.sha256()
        
        # Hash all requirements files
        for req_file in sorted(PROJECT_ROOT.glob("requirements*.txt")):
            if req_file.exists():
                hasher.update(req_file.read_bytes())
        
        # Hash requirements directory
        if REQUIREMENTS_DIR.exists():
            for req_file in sorted(REQUIREMENTS_DIR.glob("*.txt")):
                hasher.update(req_file.read_bytes())
        
        # Hash constraints file
        constraints_file = PROJECT_ROOT / "constraints.txt"
        if constraints_file.exists():
            hasher.update(constraints_file.read_bytes())
        
        return hasher.hexdigest()
    
    def build_wheels(self, force: bool = False) -> List[Path]:
        """Build wheel files for all dependencies"""
        print("🔨 Building wheel files for dependencies...")
        
        current_hash = self.get_requirements_hash()
        
        # Check if we need to rebuild
        if not force and self.metadata.get("requirements_hash") == current_hash:
            print("✅ Wheels are up to date")
            return list(WHEELHOUSE_DIR.glob("*.whl"))
        
        # Clear old wheels if forcing rebuild
        if force:
            print("🧹 Clearing old wheels...")
            shutil.rmtree(WHEELHOUSE_DIR, ignore_errors=True)
            WHEELHOUSE_DIR.mkdir(parents=True, exist_ok=True)
        
        wheels_built = []
        
        # Build wheels for each requirements file
        for req_type in ["base", "dev", "optional"]:
            req_file = REQUIREMENTS_DIR / f"{req_type}.txt"
            if req_file.exists():
                print(f"📦 Building wheels for {req_type} requirements...")
                try:
                    subprocess.run([
                        sys.executable, "-m", "pip", "wheel",
                        "-w", str(WHEELHOUSE_DIR),
                        "-r", str(req_file),
                        "-c", str(PROJECT_ROOT / "constraints.txt"),
                        "--no-deps"
                    ], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"⚠️  Warning: Failed to build some {req_type} wheels: {e}")
        
        # Update metadata
        self.metadata["requirements_hash"] = current_hash
        self.metadata["wheels_built"] = datetime.now().isoformat()
        
        # Record wheel information
        wheels = list(WHEELHOUSE_DIR.glob("*.whl"))
        self.metadata["wheels"] = {
            wheel.name: {
                "size": wheel.stat().st_size,
                "mtime": datetime.fromtimestamp(wheel.stat().st_mtime).isoformat()
            }
            for wheel in wheels
        }
        
        self.save_metadata()
        
        print(f"✅ Built {len(wheels)} wheel files")
        return wheels
    
    def download_sources(self) -> List[Path]:
        """Download source distributions for offline installation"""
        print("📥 Downloading source distributions...")
        
        downloads = []
        
        for req_type in ["base", "dev", "optional"]:
            req_file = REQUIREMENTS_DIR / f"{req_type}.txt"
            if req_file.exists():
                print(f"📦 Downloading {req_type} sources...")
                try:
                    subprocess.run([
                        sys.executable, "-m", "pip", "download",
                        "-d", str(DOWNLOAD_DIR),
                        "-r", str(req_file),
                        "-c", str(PROJECT_ROOT / "constraints.txt")
                    ], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"⚠️  Warning: Failed to download some {req_type} sources: {e}")
        
        # Update metadata
        downloads = list(DOWNLOAD_DIR.glob("*"))
        self.metadata["downloads"] = {
            dl.name: {
                "size": dl.stat().st_size,
                "mtime": datetime.fromtimestamp(dl.stat().st_mtime).isoformat()
            }
            for dl in downloads
        }
        self.metadata["downloads_updated"] = datetime.now().isoformat()
        self.save_metadata()
        
        print(f"✅ Downloaded {len(downloads)} packages")
        return downloads
    
    def create_requirements_lock(self):
        """Create locked requirements files with exact versions"""
        print("🔒 Creating requirements lock files...")
        
        # Create a temporary virtual environment
        venv_dir = PROJECT_ROOT / ".tmp_venv"
        if venv_dir.exists():
            shutil.rmtree(venv_dir)
        
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        
        # Install dependencies in the venv
        pip_exe = venv_dir / "bin" / "pip" if sys.platform != "win32" else venv_dir / "Scripts" / "pip.exe"
        
        subprocess.run([str(pip_exe), "install", "--upgrade", "pip", "wheel"], check=True)
        subprocess.run([
            str(pip_exe), "install",
            "-r", str(PROJECT_ROOT / "requirements.txt"),
            "-c", str(PROJECT_ROOT / "constraints.txt")
        ], check=True)
        
        # Generate lock file
        result = subprocess.run([str(pip_exe), "freeze"], capture_output=True, text=True)
        
        lock_file = PROJECT_ROOT / "requirements.lock"
        with open(lock_file, 'w') as f:
            f.write("# Locked requirements for LiteCrewAI\n")
            f.write(f"# Generated on {datetime.now().isoformat()}\n")
            f.write(f"# Requirements hash: {self.get_requirements_hash()}\n\n")
            f.write(result.stdout)
        
        # Clean up
        shutil.rmtree(venv_dir)
        
        print(f"✅ Created requirements.lock with {len(result.stdout.splitlines())} packages")
    
    def clean_cache(self, max_age_days: int = 30):
        """Clean up old cache entries"""
        print(f"🧹 Cleaning cache entries older than {max_age_days} days...")
        
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        removed_count = 0
        
        # Clean wheelhouse
        for wheel in WHEELHOUSE_DIR.glob("*.whl"):
            if datetime.fromtimestamp(wheel.stat().st_mtime) < cutoff_date:
                wheel.unlink()
                removed_count += 1
        
        # Clean downloads
        for download in DOWNLOAD_DIR.glob("*"):
            if datetime.fromtimestamp(download.stat().st_mtime) < cutoff_date:
                download.unlink()
                removed_count += 1
        
        # Update metadata
        self.metadata["last_cleanup"] = datetime.now().isoformat()
        self.save_metadata()
        
        print(f"✅ Removed {removed_count} old cache entries")
    
    def verify_cache(self) -> Tuple[bool, List[str]]:
        """Verify cache integrity"""
        print("🔍 Verifying cache integrity...")
        
        issues = []
        
        # Check if directories exist
        for directory in [WHEELHOUSE_DIR, CACHE_DIR, DOWNLOAD_DIR]:
            if not directory.exists():
                issues.append(f"Missing directory: {directory}")
        
        # Check wheel files
        wheel_count = len(list(WHEELHOUSE_DIR.glob("*.whl")))
        if wheel_count == 0:
            issues.append("No wheel files found in wheelhouse")
        
        # Check metadata
        if not self.metadata.get("requirements_hash"):
            issues.append("No requirements hash in metadata")
        
        # Verify hash matches current requirements
        if self.metadata.get("requirements_hash") != self.get_requirements_hash():
            issues.append("Requirements have changed since last cache build")
        
        is_valid = len(issues) == 0
        
        if is_valid:
            print("✅ Cache is valid")
        else:
            print("❌ Cache validation failed:")
            for issue in issues:
                print(f"  - {issue}")
        
        return is_valid, issues
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        stats = {
            "wheelhouse_size": sum(f.stat().st_size for f in WHEELHOUSE_DIR.glob("*.whl")),
            "wheelhouse_count": len(list(WHEELHOUSE_DIR.glob("*.whl"))),
            "download_size": sum(f.stat().st_size for f in DOWNLOAD_DIR.glob("*")),
            "download_count": len(list(DOWNLOAD_DIR.glob("*"))),
            "cache_size": sum(f.stat().st_size for f in CACHE_DIR.rglob("*") if f.is_file()),
            "last_build": self.metadata.get("wheels_built"),
            "last_cleanup": self.metadata.get("last_cleanup"),
            "requirements_hash": self.metadata.get("requirements_hash", "")[:8] + "..."
        }
        
        return stats
    
    def export_cache(self, output_dir: Path):
        """Export cache to a directory for offline use"""
        print(f"📤 Exporting cache to {output_dir}...")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy wheelhouse
        wheelhouse_export = output_dir / "wheelhouse"
        if WHEELHOUSE_DIR.exists():
            shutil.copytree(WHEELHOUSE_DIR, wheelhouse_export, dirs_exist_ok=True)
        
        # Copy downloads
        downloads_export = output_dir / "downloads"
        if DOWNLOAD_DIR.exists():
            shutil.copytree(DOWNLOAD_DIR, downloads_export, dirs_exist_ok=True)
        
        # Copy requirements
        for req_file in PROJECT_ROOT.glob("requirements*.txt"):
            shutil.copy2(req_file, output_dir)
        
        if REQUIREMENTS_DIR.exists():
            shutil.copytree(REQUIREMENTS_DIR, output_dir / "requirements", dirs_exist_ok=True)
        
        # Copy constraints
        constraints_file = PROJECT_ROOT / "constraints.txt"
        if constraints_file.exists():
            shutil.copy2(constraints_file, output_dir)
        
        # Copy lock file if it exists
        lock_file = PROJECT_ROOT / "requirements.lock"
        if lock_file.exists():
            shutil.copy2(lock_file, output_dir)
        
        # Copy pip configuration
        pip_conf = PROJECT_ROOT / ".pip" / "pip.conf"
        if pip_conf.exists():
            shutil.copy2(pip_conf, output_dir)
        
        # Create offline installation script with enhanced options
        install_script = output_dir / "install_offline.sh"
        install_script.write_text("""#!/bin/bash
# Offline installation script for LiteCrewAI

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

# Colors for output
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
NC='\\033[0m' # No Color

echo -e "${GREEN}🚀 Installing LiteCrewAI from offline cache...${NC}"

# Parse command line arguments
INSTALL_TYPE="basic"
while [[ $# -gt 0 ]]; do
  case $1 in
    --dev)
      INSTALL_TYPE="dev"
      shift
      ;;
    --all)
      INSTALL_TYPE="all"
      shift
      ;;
    --venv)
      VENV_DIR="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [--dev|--all] [--venv VENV_DIR]"
      echo "  --dev: Install with development dependencies"
      echo "  --all: Install with all optional dependencies"
      echo "  --venv: Specify virtual environment directory (default: venv)"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${YELLOW}Python version: $PYTHON_VERSION${NC}"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo -e "${RED}❌ Python 3.10 or higher is required${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment: $VENV_DIR${NC}"
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Verify activation
if [[ "$VIRTUAL_ENV" != *"$VENV_DIR"* ]]; then
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
fi

# Set pip configuration
if [ -f "pip.conf" ]; then
    mkdir -p "$VIRTUAL_ENV/pip"
    cp pip.conf "$VIRTUAL_ENV/pip/"
fi

# Upgrade pip and build tools
echo -e "${YELLOW}📦 Upgrading pip and build tools...${NC}"
pip install --upgrade --no-index --find-links wheelhouse pip setuptools wheel

# Install based on type
case "$INSTALL_TYPE" in
  "basic")
    echo -e "${YELLOW}📦 Installing basic dependencies...${NC}"
    pip install --no-index --find-links wheelhouse -r requirements.txt
    ;;
  "dev")
    echo -e "${YELLOW}📦 Installing with development dependencies...${NC}"
    pip install --no-index --find-links wheelhouse -r requirements.txt
    if [ -f "requirements/dev.txt" ]; then
      pip install --no-index --find-links wheelhouse -r requirements/dev.txt || true
    fi
    ;;
  "all")
    echo -e "${YELLOW}📦 Installing with all dependencies...${NC}"
    pip install --no-index --find-links wheelhouse -r requirements.txt
    if [ -f "requirements/dev.txt" ]; then
      pip install --no-index --find-links wheelhouse -r requirements/dev.txt || true
    fi
    if [ -f "requirements/optional.txt" ]; then
      pip install --no-index --find-links wheelhouse -r requirements/optional.txt || true
    fi
    ;;
esac

# Verify installation
echo -e "${YELLOW}🔍 Verifying installation...${NC}"
if python -c "import sys; print(f'Python: {sys.version}'); import pip; print(f'Pip: {pip.__version__}')"; then
    echo -e "${GREEN}✅ LiteCrewAI installed successfully!${NC}"
    echo -e "${GREEN}Virtual environment: $VENV_DIR${NC}"
    echo -e "${GREEN}Activate with: source $VENV_DIR/bin/activate${NC}"
    
    # Show installed packages
    echo -e "${YELLOW}📦 Installed packages:${NC}"
    pip list | head -20
    echo "..."
else
    echo -e "${RED}❌ Installation verification failed${NC}"
    exit 1
fi
""")
        install_script.chmod(0o755)
        
        # Create verification script
        verify_script = output_dir / "verify_installation.py"
        verify_script.write_text("""#!/usr/bin/env python3
\"\"\"Comprehensive LiteCrewAI installation verification\"\"\"

import sys
import importlib
from pathlib import Path

def check_python_version():
    \"\"\"Check Python version compatibility\"\"\"
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 10):
        print("❌ Python 3.10 or higher is required")
        return False
    elif version >= (3, 14):
        print("⚠️  Python 3.14+ may have compatibility issues")
    
    print("✅ Python version is compatible")
    return True

def verify_import(module_name, optional=False):
    \"\"\"Verify module import\"\"\"
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {module_name} ({version})")
        return True
    except ImportError as e:
        status = "⚠️ " if optional else "❌"
        print(f"{status} {module_name}: {e}")
        return optional

def main():
    print("🔍 Verifying LiteCrewAI installation...\\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print("\\n📦 Checking core dependencies:")
    
    # Core dependencies
    core_modules = [
        "pydantic",
        "click", 
        "python_dotenv",
        "jsonref",
        "blinker",
    ]
    
    # Python version specific
    if sys.version_info < (3, 11):
        core_modules.append("tomli")
    
    core_modules.append("tomli_w")
    
    core_success = all(verify_import(module) for module in core_modules)
    
    print("\\n📦 Checking optional dependencies:")
    
    # Optional dependencies
    optional_modules = [
        "openai",
        "litellm", 
        "instructor",
        "pdfplumber",
        "chromadb",
        "tokenizers",
        "openpyxl",
        "pandas",
    ]
    
    for module in optional_modules:
        verify_import(module, optional=True)
    
    print("\\n🏥 System health check:")
    
    # Virtual environment check
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not running in virtual environment")
    
    # Installation path
    print(f"📍 Python executable: {sys.executable}")
    print(f"📍 Python path: {sys.path[0]}")
    
    # Package locations
    try:
        import crewai
        crewai_path = Path(crewai.__file__).parent
        print(f"📍 CrewAI location: {crewai_path}")
    except ImportError:
        print("⚠️  CrewAI not found in path")
    
    if core_success:
        print("\\n✅ Installation verification completed successfully!")
        sys.exit(0)
    else:
        print("\\n❌ Installation verification failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
""")
        verify_script.chmod(0o755)
        
        # Create export metadata
        metadata = {
            "export_date": datetime.now().isoformat(),
            "requirements_hash": self.get_requirements_hash(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "wheel_count": len(list(wheelhouse_export.glob("*.whl"))) if wheelhouse_export.exists() else 0,
            "download_count": len(list(downloads_export.glob("*"))) if downloads_export.exists() else 0,
        }
        
        metadata_file = output_dir / "export_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Cache exported to {output_dir}")
        print(f"   Total size: {sum(f.stat().st_size for f in output_dir.rglob('*') if f.is_file()) / 1024 / 1024:.1f} MB")
        print(f"   Wheels: {metadata['wheel_count']}")
        print(f"   Downloads: {metadata['download_count']}")
        
    def gitlab_ci_setup(self):
        """Setup cache for GitLab CI environment"""
        print("🔧 Setting up cache for GitLab CI...")
        
        # Check if we're in GitLab CI
        if not os.environ.get('GITLAB_CI'):
            print("⚠️  Not running in GitLab CI environment")
            return
        
        # Create CI-specific directories
        ci_cache_dirs = [
            Path(os.environ.get('CI_PROJECT_DIR', '.')) / '.pip' / 'cache',
            Path(os.environ.get('CI_PROJECT_DIR', '.')) / '.pip' / 'wheelhouse',
            Path(os.environ.get('CI_PROJECT_DIR', '.')) / '.uv' / 'cache',
        ]
        
        for cache_dir in ci_cache_dirs:
            cache_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created cache directory: {cache_dir}")
        
        # Set environment variables for CI
        ci_env_vars = {
            'PIP_CACHE_DIR': str(ci_cache_dirs[0]),
            'PIP_WHEEL_DIR': str(ci_cache_dirs[1]),
            'UV_CACHE_DIR': str(ci_cache_dirs[2]),
        }
        
        for var, value in ci_env_vars.items():
            os.environ[var] = value
            print(f"🔧 Set {var}={value}")
        
        print("✅ GitLab CI cache setup completed")
        
    def restore_from_backup(self, backup_path: Path):
        """Restore cache from backup"""
        print(f"🔄 Restoring cache from backup: {backup_path}")
        
        if not backup_path.exists():
            print(f"❌ Backup path does not exist: {backup_path}")
            return False
        
        # Extract if it's an archive
        if backup_path.suffix in ['.tar', '.gz', '.tgz']:
            import tarfile
            with tarfile.open(backup_path, 'r:*') as tar:
                tar.extractall(path=PROJECT_ROOT)
        elif backup_path.suffix == '.zip':
            import zipfile
            with zipfile.ZipFile(backup_path, 'r') as zip_file:
                zip_file.extractall(PROJECT_ROOT)
        else:
            # Assume it's a directory
            shutil.copytree(backup_path, PROJECT_ROOT, dirs_exist_ok=True)
        
        print("✅ Cache restored from backup")
        return True


def main():
    parser = argparse.ArgumentParser(description="LiteCrewAI Dependency Cache Manager")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build wheel cache")
    build_parser.add_argument("--force", action="store_true", help="Force rebuild even if up to date")
    
    # Download command
    subparsers.add_parser("download", help="Download source distributions")
    
    # Lock command
    subparsers.add_parser("lock", help="Create requirements lock file")
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean old cache entries")
    clean_parser.add_argument("--max-age", type=int, default=30, help="Maximum age in days (default: 30)")
    
    # Verify command
    subparsers.add_parser("verify", help="Verify cache integrity")
    
    # Stats command
    subparsers.add_parser("stats", help="Show cache statistics")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export cache for offline use")
    export_parser.add_argument("output", type=Path, help="Output directory")
    
    # GitLab CI setup command
    subparsers.add_parser("gitlab-ci-setup", help="Setup cache for GitLab CI environment")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore cache from backup")
    restore_parser.add_argument("backup", type=Path, help="Backup file or directory path")
    
    # All command
    all_parser = subparsers.add_parser("all", help="Run all cache operations")
    all_parser.add_argument("--force", action="store_true", help="Force rebuild")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = DependencyCacheManager()
    
    if args.command == "build":
        manager.build_wheels(force=args.force)
    
    elif args.command == "download":
        manager.download_sources()
    
    elif args.command == "lock":
        manager.create_requirements_lock()
    
    elif args.command == "clean":
        manager.clean_cache(max_age_days=args.max_age)
    
    elif args.command == "verify":
        is_valid, issues = manager.verify_cache()
        sys.exit(0 if is_valid else 1)
    
    elif args.command == "stats":
        stats = manager.get_cache_stats()
        print("\n📊 Cache Statistics:")
        print(f"  Wheelhouse: {stats['wheelhouse_count']} files, {stats['wheelhouse_size'] / 1024 / 1024:.1f} MB")
        print(f"  Downloads: {stats['download_count']} files, {stats['download_size'] / 1024 / 1024:.1f} MB")
        print(f"  Total cache: {stats['cache_size'] / 1024 / 1024:.1f} MB")
        print(f"  Last build: {stats['last_build'] or 'Never'}")
        print(f"  Last cleanup: {stats['last_cleanup'] or 'Never'}")
        print(f"  Requirements hash: {stats['requirements_hash']}")
    
    elif args.command == "export":
        manager.export_cache(args.output)
    
    elif args.command == "gitlab-ci-setup":
        manager.gitlab_ci_setup()
    
    elif args.command == "restore":
        success = manager.restore_from_backup(args.backup)
        sys.exit(0 if success else 1)
    
    elif args.command == "all":
        # Run all operations
        manager.build_wheels(force=args.force)
        manager.download_sources()
        manager.create_requirements_lock()
        manager.clean_cache()
        is_valid, _ = manager.verify_cache()
        
        if is_valid:
            print("\n✅ All cache operations completed successfully!")
        else:
            print("\n⚠️  Cache operations completed with warnings")


if __name__ == "__main__":
    main()