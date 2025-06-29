#!/bin/bash

# CrewAI Fork Script with Full Cleanup and Analysis
# This script clones CrewAI, cleans it up, and generates a detailed report

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEST_DIR="/Users/hretheum/dev/bezrobocie/crewAI/app"
REPO_URL="https://github.com/crewAIInc/crewAI.git"
REPORT_FILE="/Users/hretheum/dev/bezrobocie/crewAI/crewai_analysis_report.md"
BRANCH_NAME="lite-personal"

echo -e "${BLUE}=== CrewAI Fork Script ===${NC}"
echo -e "${YELLOW}This script will clone CrewAI and perform a full cleanup analysis${NC}\n"

# Function to print status
print_status() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to calculate directory size
get_dir_size() {
    du -sh "$1" 2>/dev/null | cut -f1
}

# Function to count files by extension
count_files_by_ext() {
    local dir=$1
    local ext=$2
    find "$dir" -name "*.$ext" -type f 2>/dev/null | wc -l | tr -d ' '
}

# Create destination directory
print_status "Creating destination directory..."
mkdir -p "$DEST_DIR"

# Check if directory already exists and has content
if [ -d "$DEST_DIR/.git" ]; then
    echo -e "${YELLOW}Directory already contains a git repository.${NC}"
    read -p "Do you want to remove it and start fresh? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing existing repository..."
        rm -rf "$DEST_DIR"
        mkdir -p "$DEST_DIR"
    else
        print_error "Exiting without changes."
        exit 1
    fi
fi

# Clone the repository
print_status "Cloning CrewAI repository..."
git clone "$REPO_URL" "$DEST_DIR"

cd "$DEST_DIR"

# Get initial statistics
INITIAL_SIZE=$(get_dir_size .)
INITIAL_COMMIT_COUNT=$(git rev-list --all --count)

print_status "Removing remote tracking branches..."
# Remove all remote tracking branches except origin/main
git branch -r | grep -v 'origin/main' | sed 's/origin\///' | xargs -I {} git push origin --delete {} 2>/dev/null || true

# Remove remote
print_status "Removing original remote..."
git remote remove origin

# Create new branch
print_status "Creating branch '$BRANCH_NAME' from main..."
git checkout -b "$BRANCH_NAME"

# Start generating report
print_status "Analyzing project structure..."

cat > "$REPORT_FILE" << EOF
# CrewAI Fork Analysis Report

**Generated on:** $(date '+%Y-%m-%d %H:%M:%S')  
**Repository Location:** $DEST_DIR  
**Original Repository:** $REPO_URL  

## Repository Statistics

### General Information
- **Initial Repository Size:** $INITIAL_SIZE
- **Total Commits:** $INITIAL_COMMIT_COUNT
- **Current Branch:** $BRANCH_NAME

### File Statistics
EOF

# Count files by type
print_status "Counting files by type..."

TOTAL_FILES=$(find . -type f -not -path "./.git/*" | wc -l | tr -d ' ')
PY_FILES=$(count_files_by_ext . "py")
MD_FILES=$(count_files_by_ext . "md")
YML_FILES=$(count_files_by_ext . "yml")
YAML_FILES=$(count_files_by_ext . "yaml")
JSON_FILES=$(count_files_by_ext . "json")
TXT_FILES=$(count_files_by_ext . "txt")
JS_FILES=$(count_files_by_ext . "js")
TS_FILES=$(count_files_by_ext . "ts")

cat >> "$REPORT_FILE" << EOF

| File Type | Count |
|-----------|-------|
| Total Files | $TOTAL_FILES |
| Python (.py) | $PY_FILES |
| Markdown (.md) | $MD_FILES |
| YAML (.yml/.yaml) | $((YML_FILES + YAML_FILES)) |
| JSON (.json) | $JSON_FILES |
| Text (.txt) | $TXT_FILES |
| JavaScript (.js) | $JS_FILES |
| TypeScript (.ts) | $TS_FILES |

### Directory Structure
\`\`\`
$(tree -d -L 3 2>/dev/null || find . -type d -not -path "./.git/*" | head -50)
\`\`\`

## Dependencies Analysis

EOF

# Analyze Python dependencies
print_status "Analyzing Python dependencies..."

if [ -f "requirements.txt" ]; then
    echo "### requirements.txt" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    cat requirements.txt >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

if [ -f "setup.py" ]; then
    echo "### setup.py dependencies" >> "$REPORT_FILE"
    echo "Found setup.py - extracting dependencies..." >> "$REPORT_FILE"
    echo '```python' >> "$REPORT_FILE"
    grep -A 20 "install_requires" setup.py 2>/dev/null | head -30 >> "$REPORT_FILE" || echo "Could not extract dependencies from setup.py" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

if [ -f "pyproject.toml" ]; then
    echo "### pyproject.toml dependencies" >> "$REPORT_FILE"
    echo '```toml' >> "$REPORT_FILE"
    grep -A 30 "\[tool.poetry.dependencies\]" pyproject.toml 2>/dev/null >> "$REPORT_FILE" || echo "Could not extract dependencies from pyproject.toml" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

# Analyze package.json if exists
if [ -f "package.json" ]; then
    echo "### package.json dependencies" >> "$REPORT_FILE"
    echo '```json' >> "$REPORT_FILE"
    jq '.dependencies' package.json 2>/dev/null >> "$REPORT_FILE" || echo "Could not parse package.json" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

# Potential cleanup areas
print_status "Identifying potential cleanup areas..."

cat >> "$REPORT_FILE" << EOF

## Potential Cleanup Areas

### Large Directories
EOF

# Find large directories
echo '```' >> "$REPORT_FILE"
du -sh */ 2>/dev/null | sort -rh | head -20 >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"

cat >> "$REPORT_FILE" << EOF

### Documentation and Examples
EOF

# Find documentation and example directories
DOC_DIRS=$(find . -type d -name "*doc*" -o -name "*example*" -o -name "*demo*" -o -name "*test*" | grep -v ".git" | head -20)
if [ -n "$DOC_DIRS" ]; then
    echo "Found the following documentation/example directories:" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "$DOC_DIRS" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
else
    echo "No obvious documentation or example directories found." >> "$REPORT_FILE"
fi

# Check for common cleanup candidates
cat >> "$REPORT_FILE" << EOF

### Common Cleanup Candidates

Checking for typical files/directories that can be removed:

EOF

# List of common cleanup candidates
CLEANUP_CANDIDATES=(
    ".github"
    ".circleci"
    ".travis.yml"
    "docs"
    "examples"
    "tests"
    "benchmarks"
    "scripts"
    ".readthedocs.yml"
    "CONTRIBUTING.md"
    "CODE_OF_CONDUCT.md"
    ".dockerignore"
    "Dockerfile"
    "docker-compose.yml"
    "Makefile"
    ".pre-commit-config.yaml"
)

echo "| Path | Size | Recommendation |" >> "$REPORT_FILE"
echo "|------|------|----------------|" >> "$REPORT_FILE"

for item in "${CLEANUP_CANDIDATES[@]}"; do
    if [ -e "$item" ]; then
        SIZE=$(get_dir_size "$item")
        echo "| $item | $SIZE | Consider removing if not needed |" >> "$REPORT_FILE"
    fi
done

# Large files analysis
cat >> "$REPORT_FILE" << EOF

### Large Files (>1MB)
\`\`\`
$(find . -type f -size +1M -not -path "./.git/*" -exec ls -lh {} \; 2>/dev/null | awk '{print $5 " " $9}' | sort -rh | head -20)
\`\`\`

## Code Analysis

### Python Module Structure
EOF

# Analyze Python package structure
if [ -d "src" ] || [ -d "crewai" ]; then
    echo "Found Python package structure:" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    find . -name "__init__.py" -not -path "./.git/*" | head -30 >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
fi

# Check for entry points
cat >> "$REPORT_FILE" << EOF

### Entry Points and Main Files
EOF

MAIN_FILES=$(find . -name "main.py" -o -name "__main__.py" -o -name "cli.py" -o -name "app.py" -not -path "./.git/*")
if [ -n "$MAIN_FILES" ]; then
    echo "Found the following entry point files:" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "$MAIN_FILES" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
else
    echo "No obvious entry point files found." >> "$REPORT_FILE"
fi

# Summary and recommendations
cat >> "$REPORT_FILE" << EOF

## Summary and Recommendations

### Key Findings
1. **Total repository size:** $INITIAL_SIZE
2. **Total number of files:** $TOTAL_FILES
3. **Primary language:** Python ($PY_FILES files)

### Recommended Cleanup Actions

1. **Remove CI/CD configurations** if not needed (.github, .circleci, etc.)
2. **Remove documentation** that won't be maintained (docs/, examples/)
3. **Clean up test files** if creating a minimal version
4. **Remove large binary files** or move them to Git LFS
5. **Simplify dependency management** - review and remove unnecessary dependencies
6. **Remove example and demo code** if creating a production-focused fork

### Next Steps

1. Review the identified cleanup candidates
2. Decide which components are essential for your use case
3. Create a cleanup script based on your decisions
4. Consider setting up a new remote repository for your fork
5. Push your cleaned version to the new remote

## Git Commands for Setting New Remote

\`\`\`bash
# Add your new remote (replace with your repository URL)
git remote add origin YOUR_NEW_REPO_URL

# Push the lite-personal branch
git push -u origin lite-personal

# If you want to make lite-personal the default branch
git branch -M lite-personal main
git push -u origin main
\`\`\`

---
*Report generated by CrewAI Fork Script*
EOF

print_status "Report generated at: $REPORT_FILE"

# Make the report more accessible
cp "$REPORT_FILE" "$DEST_DIR/FORK_ANALYSIS.md"

echo -e "\n${GREEN}✓ Fork process completed successfully!${NC}"
echo -e "${BLUE}Repository location:${NC} $DEST_DIR"
echo -e "${BLUE}Current branch:${NC} $BRANCH_NAME"
echo -e "${BLUE}Analysis report:${NC} $REPORT_FILE"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Review the analysis report"
echo "2. Decide what to keep/remove"
echo "3. Set up your new remote repository"
echo "4. Push your changes"