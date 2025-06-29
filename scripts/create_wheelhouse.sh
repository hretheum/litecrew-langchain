#!/bin/bash
# Create offline wheelhouse for LiteCrewAI
# Enhanced version with GitLab CI support and better error handling

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CREWAI_FORK="$PROJECT_ROOT/crewai-fork"
WHEELHOUSE_DIR="$CREWAI_FORK/.pip/wheelhouse"
OFFLINE_BUNDLE_DIR="$PROJECT_ROOT/offline_bundle"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# GitLab CI compatibility
if [ -n "$CI_PROJECT_DIR" ]; then
    PROJECT_ROOT="$CI_PROJECT_DIR"
    CREWAI_FORK="$CI_PROJECT_DIR"
    WHEELHOUSE_DIR="$CI_PROJECT_DIR/.pip/wheelhouse"
    OFFLINE_BUNDLE_DIR="$CI_PROJECT_DIR/offline_bundle"
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Error handling
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_error "Script failed with exit code $exit_code"
        if [ -n "$TEMP_VENV" ] && [ -d "$TEMP_VENV" ]; then
            log_info "Cleaning up temporary virtual environment..."
            rm -rf "$TEMP_VENV"
        fi
    fi
}

trap cleanup EXIT

SCRIPT_START_TIME=$(date +%s)

log_success "🚀 Creating offline wheelhouse for LiteCrewAI"
log_info "Project root: $PROJECT_ROOT"
log_info "Timestamp: $TIMESTAMP"
log_info "Python version: $(python3 --version 2>/dev/null || echo 'Not found')"

# Validate environment
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is required but not found"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"; then
    log_error "Python 3.10 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

log_info "Using Python $PYTHON_VERSION"

# Change to project directory
cd "$CREWAI_FORK"

# Verify we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    log_error "Not in LiteCrewAI project directory (pyproject.toml not found)"
    exit 1
fi

# Use existing cache if available (GitLab CI optimization)
if [ -n "$CI" ] && [ -d ".pip/cache" ]; then
    log_info "Using existing pip cache from CI"
    export PIP_CACHE_DIR=".pip/cache"
fi

# Ensure pip is up to date
log_info "📦 Upgrading pip, wheel, and setuptools..."
python3 -m pip install --upgrade pip wheel setuptools

# Create wheelhouse directory
mkdir -p "$WHEELHOUSE_DIR"
mkdir -p "$WHEELHOUSE_DIR/sources"

# Function to build wheels for a requirements file
build_wheels() {
    local req_file=$1
    local req_name=$2
    
    if [ -f "$req_file" ]; then
        log_info "🔨 Building wheels for $req_name requirements..."
        
        # Use different cache strategies for CI vs local
        if [ -n "$CI" ]; then
            python3 -m pip wheel \
                -w "$WHEELHOUSE_DIR" \
                -r "$req_file" \
                -c constraints.txt \
                --cache-dir ".pip/cache" \
                --progress-bar off
        else
            python3 -m pip wheel \
                -w "$WHEELHOUSE_DIR" \
                -r "$req_file" \
                -c constraints.txt \
                --progress-bar on
        fi
        
        local exit_code=$?
        if [ $exit_code -eq 0 ]; then
            log_success "Built wheels for $req_name requirements"
        else
            log_warning "Some wheels for $req_name requirements failed to build (exit code: $exit_code)"
        fi
    else
        log_warning "Requirements file not found: $req_file"
    fi
}

# Build wheels in order of stability (most stable first for better caching)
build_wheels "requirements/base.txt" "core"
build_wheels "requirements.txt" "base"
build_wheels "requirements/optional.txt" "optional"
build_wheels "requirements/dev.txt" "development"

# Download source distributions as backup
log_info "📥 Downloading source distributions..."

download_sources() {
    local req_file=$1
    local req_name=$2
    
    if [ -f "$req_file" ]; then
        log_info "📦 Downloading $req_name sources..."
        
        if [ -n "$CI" ]; then
            # In CI, be more tolerant of failures and quieter
            python3 -m pip download \
                -d "$WHEELHOUSE_DIR/sources" \
                -r "$req_file" \
                -c constraints.txt \
                --no-binary :all: \
                --cache-dir ".pip/cache" \
                --quiet || log_warning "Some $req_name sources failed to download"
        else
            python3 -m pip download \
                -d "$WHEELHOUSE_DIR/sources" \
                -r "$req_file" \
                -c constraints.txt \
                --no-binary :all: || log_warning "Some $req_name sources failed to download"
        fi
    fi
}

# Download sources in the same order
download_sources "requirements/base.txt" "core"
download_sources "requirements.txt" "base"
download_sources "requirements/optional.txt" "optional"
download_sources "requirements/dev.txt" "development"

# Create requirements lock file
log_info "🔒 Creating requirements.lock file..."

# Skip lock file generation in CI if it already exists and is recent
if [ -n "$CI" ] && [ -f "requirements.lock" ]; then
    # Check if lock file is newer than 1 day
    if [ $(find requirements.lock -mtime -1 2>/dev/null | wc -l) -gt 0 ]; then
        log_info "Using existing recent requirements.lock file"
    else
        CREATE_LOCK=true
    fi
else
    CREATE_LOCK=true
fi

if [ "$CREATE_LOCK" = true ]; then
    # Create temporary virtual environment
    TEMP_VENV="$PROJECT_ROOT/.tmp_venv_$TIMESTAMP"
    log_info "Creating temporary virtual environment: $TEMP_VENV"
    
    python3 -m venv "$TEMP_VENV"
    source "$TEMP_VENV/bin/activate"
    
    # Install all requirements with error handling
    pip install --upgrade pip wheel setuptools
    
    # Install base requirements
    if pip install -r requirements.txt -c constraints.txt; then
        log_success "Installed base requirements"
    else
        log_error "Failed to install base requirements"
        deactivate
        rm -rf "$TEMP_VENV"
        exit 1
    fi
    
    # Install optional requirements (non-fatal)
    if [ -f "requirements/dev.txt" ]; then
        if pip install -r requirements/dev.txt -c constraints.txt; then
            log_success "Installed development requirements"
        else
            log_warning "Failed to install some development requirements"
        fi
    fi
    
    if [ -f "requirements/optional.txt" ]; then
        if pip install -r requirements/optional.txt -c constraints.txt; then
            log_success "Installed optional requirements"
        else
            log_warning "Failed to install some optional requirements"
        fi
    fi
    
    # Generate lock file with metadata
    {
        echo "# LiteCrewAI Requirements Lock File"
        echo "# Generated on: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
        echo "# Python version: $PYTHON_VERSION"
        echo "# Platform: $(uname -s) $(uname -m)"
        echo ""
        pip freeze
    } > requirements.lock
    
    log_success "Generated requirements.lock with $(pip list | wc -l) packages"
    
    # Deactivate and remove temp venv
    deactivate
    rm -rf "$TEMP_VENV"
fi

# Create offline bundle
log_info "📦 Creating offline bundle..."
rm -rf "$OFFLINE_BUNDLE_DIR"
mkdir -p "$OFFLINE_BUNDLE_DIR"

# Copy wheelhouse
if [ -d "$WHEELHOUSE_DIR" ]; then
    cp -r "$WHEELHOUSE_DIR" "$OFFLINE_BUNDLE_DIR/"
    log_success "Copied wheelhouse directory"
else
    log_warning "Wheelhouse directory not found: $WHEELHOUSE_DIR"
fi

# Copy requirements files
log_info "📄 Copying requirements files..."
cp requirements*.txt "$OFFLINE_BUNDLE_DIR/" 2>/dev/null || log_warning "No requirements*.txt files found"
if [ -d "requirements/" ]; then
    cp -r requirements/ "$OFFLINE_BUNDLE_DIR/" 
    log_success "Copied requirements directory"
fi
[ -f "constraints.txt" ] && cp constraints.txt "$OFFLINE_BUNDLE_DIR/" && log_success "Copied constraints.txt"
[ -f "requirements.lock" ] && cp requirements.lock "$OFFLINE_BUNDLE_DIR/" && log_success "Copied requirements.lock"

# Copy project configuration files
log_info "⚙️  Copying configuration files..."
[ -f "pyproject.toml" ] && cp pyproject.toml "$OFFLINE_BUNDLE_DIR/" && log_success "Copied pyproject.toml"
[ -f "setup.py" ] && cp setup.py "$OFFLINE_BUNDLE_DIR/" && log_info "Copied setup.py"
[ -f "setup.cfg" ] && cp setup.cfg "$OFFLINE_BUNDLE_DIR/" && log_info "Copied setup.cfg"
[ -f ".pip/pip.conf" ] && cp .pip/pip.conf "$OFFLINE_BUNDLE_DIR/" && log_success "Copied pip configuration"

# Create installation script
cat > "$OFFLINE_BUNDLE_DIR/install_offline.sh" << 'EOF'
#!/bin/bash
# Offline installation script for LiteCrewAI

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Installing LiteCrewAI from offline bundle${NC}"

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.12"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}❌ Python $required_version or higher is required (found $python_version)${NC}"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}📦 Upgrading pip...${NC}"
pip install --upgrade --no-index --find-links wheelhouse pip setuptools wheel

# Install from wheelhouse
echo -e "${YELLOW}📦 Installing dependencies from wheelhouse...${NC}"
pip install --no-index --find-links wheelhouse -r requirements.txt

# Install development dependencies if requested
if [ "$1" == "--dev" ]; then
    echo -e "${YELLOW}📦 Installing development dependencies...${NC}"
    pip install --no-index --find-links wheelhouse -r requirements/dev.txt || true
fi

# Install optional dependencies if requested
if [ "$1" == "--all" ]; then
    echo -e "${YELLOW}📦 Installing all dependencies...${NC}"
    pip install --no-index --find-links wheelhouse -r requirements/dev.txt || true
    pip install --no-index --find-links wheelhouse -r requirements/optional.txt || true
fi

echo -e "${GREEN}✅ LiteCrewAI installed successfully!${NC}"
echo -e "${GREEN}Activate the virtual environment with: source venv/bin/activate${NC}"
EOF

chmod +x "$OFFLINE_BUNDLE_DIR/install_offline.sh"

# Create verification script
cat > "$OFFLINE_BUNDLE_DIR/verify_installation.py" << 'EOF'
#!/usr/bin/env python3
"""Verify LiteCrewAI installation"""

import sys

def verify_import(module_name):
    try:
        __import__(module_name)
        print(f"✅ {module_name} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False

def main():
    print("🔍 Verifying LiteCrewAI installation...\n")
    
    modules = [
        "pydantic",
        "click",
        "dotenv",
        "jsonref",
        "blinker",
    ]
    
    if sys.version_info < (3, 11):
        modules.append("tomli")
    
    modules.append("tomli_w")
    
    success = all(verify_import(module) for module in modules)
    
    if success:
        print("\n✅ All core dependencies verified successfully!")
    else:
        print("\n❌ Some dependencies failed to import")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x "$OFFLINE_BUNDLE_DIR/verify_installation.py"

# Create README
cat > "$OFFLINE_BUNDLE_DIR/README.md" << EOF
# LiteCrewAI Offline Bundle

This bundle contains all dependencies needed to install LiteCrewAI offline.

## Contents

- \`wheelhouse/\` - Pre-built wheel files for all dependencies
- \`wheelhouse/sources/\` - Source distributions as backup
- \`requirements*.txt\` - Requirements files
- \`requirements/\` - Categorized requirements
- \`constraints.txt\` - Version constraints
- \`requirements.lock\` - Locked versions from build time

## Installation

1. Extract this bundle to your desired location
2. Run the installation script:

\`\`\`bash
# Basic installation
./install_offline.sh

# With development dependencies
./install_offline.sh --dev

# With all optional dependencies
./install_offline.sh --all
\`\`\`

3. Activate the virtual environment:

\`\`\`bash
source venv/bin/activate
\`\`\`

4. Verify the installation:

\`\`\`bash
python verify_installation.py
\`\`\`

## Manual Installation

If the script doesn't work, you can install manually:

\`\`\`bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade --no-index --find-links wheelhouse pip setuptools wheel

# Install dependencies
pip install --no-index --find-links wheelhouse -r requirements.txt
\`\`\`

## Bundle Information

- Created: $(date)
- Python version: $(python3 --version)
- Platform: $(uname -s) $(uname -m)

EOF

# Create archive
log_info "📦 Creating archive..."
ARCHIVE_NAME="litecrewai_offline_bundle_${TIMESTAMP}.tar.gz"
cd "$PROJECT_ROOT"

if tar -czf "$ARCHIVE_NAME" -C . offline_bundle/; then
    log_success "Created archive: $ARCHIVE_NAME"
else
    log_error "Failed to create archive"
    exit 1
fi

# Calculate sizes and statistics
log_info "📊 Calculating statistics..."
WHEELHOUSE_SIZE=$(du -sh "$WHEELHOUSE_DIR" 2>/dev/null | cut -f1 || echo "Unknown")
BUNDLE_SIZE=$(du -sh "$OFFLINE_BUNDLE_DIR" 2>/dev/null | cut -f1 || echo "Unknown")
ARCHIVE_SIZE=$(du -sh "$ARCHIVE_NAME" 2>/dev/null | cut -f1 || echo "Unknown")
WHEEL_COUNT=$(find "$WHEELHOUSE_DIR" -name "*.whl" 2>/dev/null | wc -l || echo "0")
SOURCE_COUNT=$(find "$WHEELHOUSE_DIR/sources" -type f 2>/dev/null | wc -l || echo "0")

# Create build info file for CI artifacts
if [ -n "$CI" ]; then
    BUILD_INFO_FILE="$OFFLINE_BUNDLE_DIR/build_info.json"
    cat > "$BUILD_INFO_FILE" << EOF
{
  "build_timestamp": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "python_version": "$PYTHON_VERSION",
  "platform": "$(uname -s) $(uname -m)",
  "ci_commit_sha": "${CI_COMMIT_SHA:-unknown}",
  "ci_commit_ref": "${CI_COMMIT_REF_NAME:-unknown}",
  "bundle_size": "$BUNDLE_SIZE",
  "archive_size": "$ARCHIVE_SIZE",
  "wheel_count": $WHEEL_COUNT,
  "source_count": $SOURCE_COUNT
}
EOF
    log_success "Created build info for CI"
fi

# Summary
log_success "✅ Offline bundle created successfully!"
echo ""
echo "📊 Build Statistics:"
echo "  🏗️  Platform: $(uname -s) $(uname -m)"
echo "  🐍 Python: $PYTHON_VERSION"
echo "  📦 Wheels: $WHEEL_COUNT packages"
echo "  📄 Sources: $SOURCE_COUNT packages"
echo "  💾 Wheelhouse size: $WHEELHOUSE_SIZE"
echo "  📦 Bundle size: $BUNDLE_SIZE"
echo "  🗜️  Archive size: $ARCHIVE_SIZE"
echo ""
echo "📍 Locations:"
echo "  📦 Bundle: $OFFLINE_BUNDLE_DIR"
echo "  🗜️  Archive: $PROJECT_ROOT/$ARCHIVE_NAME"

# GitLab CI artifact info
if [ -n "$CI" ]; then
    echo ""
    echo "🔧 GitLab CI Information:"
    echo "  📋 Job: ${CI_JOB_NAME:-unknown}"
    echo "  🌿 Branch: ${CI_COMMIT_REF_NAME:-unknown}"
    echo "  📝 Commit: ${CI_COMMIT_SHA:-unknown}"
    echo "  🏷️  Pipeline: ${CI_PIPELINE_ID:-unknown}"
fi

echo ""
log_info "🧪 To test the offline installation:"
echo "  1. Copy $ARCHIVE_NAME to an offline machine"
echo "  2. Extract: tar -xzf $ARCHIVE_NAME"
echo "  3. Run: cd offline_bundle && ./install_offline.sh"
echo "  4. Verify: python verify_installation.py"

# Performance metrics for CI
if [ -n "$CI" ]; then
    SCRIPT_END_TIME=$(date +%s)
    SCRIPT_DURATION=$((SCRIPT_END_TIME - ${SCRIPT_START_TIME:-$SCRIPT_END_TIME}))
    echo ""
    log_info "⏱️  Total build time: ${SCRIPT_DURATION}s"
fi

log_success "🎉 Wheelhouse creation completed successfully!"