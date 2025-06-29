#!/bin/bash

# CrewAI Cleanup Script
# This script performs the actual cleanup based on the analysis report

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
REPO_DIR="/opt/litecrewai/app"
BACKUP_DIR="/opt/litecrewai/backup_$(date +%Y%m%d_%H%M%S)"

echo -e "${BLUE}=== CrewAI Cleanup Script ===${NC}"
echo -e "${YELLOW}This script will clean up the forked CrewAI repository${NC}\n"

# Check if repository exists
if [ ! -d "$REPO_DIR/.git" ]; then
    echo -e "${RED}Error: Repository not found at $REPO_DIR${NC}"
    echo "Please run fork_crewai.sh first."
    exit 1
fi

cd "$REPO_DIR"

# Create backup
echo -e "${GREEN}Creating backup at $BACKUP_DIR...${NC}"
cp -r "$REPO_DIR" "$BACKUP_DIR"

# Function to safely remove items
safe_remove() {
    local item=$1
    if [ -e "$item" ]; then
        echo -e "${YELLOW}Removing: $item${NC}"
        rm -rf "$item"
        git add -A
        git commit -m "Remove $item" || true
    fi
}

# Start cleanup
echo -e "\n${BLUE}Starting cleanup process...${NC}"

# Remove CI/CD configurations
echo -e "\n${GREEN}Removing CI/CD configurations...${NC}"
safe_remove ".github"
safe_remove ".circleci"
safe_remove ".travis.yml"
safe_remove ".gitlab-ci.yml"
safe_remove "azure-pipelines.yml"
safe_remove ".readthedocs.yml"

# Remove documentation (optional - uncomment if needed)
# echo -e "\n${GREEN}Removing documentation...${NC}"
# safe_remove "docs"
# safe_remove "documentation"

# Remove examples and demos (optional - uncomment if needed)
# echo -e "\n${GREEN}Removing examples...${NC}"
# safe_remove "examples"
# safe_remove "demo"
# safe_remove "demos"

# Remove development files
echo -e "\n${GREEN}Removing development files...${NC}"
safe_remove "CONTRIBUTING.md"
safe_remove "CODE_OF_CONDUCT.md"
safe_remove ".pre-commit-config.yaml"
safe_remove ".flake8"
safe_remove ".isort.cfg"
safe_remove "tox.ini"
safe_remove ".coveragerc"
safe_remove "pytest.ini"
safe_remove ".editorconfig"

# Remove Docker files (optional - uncomment if needed)
# echo -e "\n${GREEN}Removing Docker files...${NC}"
# safe_remove "Dockerfile"
# safe_remove "docker-compose.yml"
# safe_remove ".dockerignore"

# Clean up Python cache and build artifacts
echo -e "\n${GREEN}Cleaning Python artifacts...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name ".DS_Store" -delete 2>/dev/null || true

# Create minimal .gitignore
echo -e "\n${GREEN}Creating minimal .gitignore...${NC}"
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
.env
.env.local
*.sqlite
*.db
EOF

git add .gitignore
git commit -m "Add minimal .gitignore" || true

# Generate cleanup summary
FINAL_SIZE=$(du -sh . | cut -f1)
FINAL_FILES=$(find . -type f -not -path "./.git/*" | wc -l | tr -d ' ')

echo -e "\n${GREEN}=== Cleanup Summary ===${NC}"
echo -e "Repository size: $FINAL_SIZE"
echo -e "Total files: $FINAL_FILES"
echo -e "Backup location: $BACKUP_DIR"

# Create cleanup report
CLEANUP_REPORT="$REPO_DIR/CLEANUP_REPORT.md"
cat > "$CLEANUP_REPORT" << EOF
# CrewAI Cleanup Report

**Cleanup Date:** $(date '+%Y-%m-%d %H:%M:%S')
**Backup Location:** $BACKUP_DIR

## Cleanup Summary

- **Final Repository Size:** $FINAL_SIZE
- **Final File Count:** $FINAL_FILES

## Removed Items

### CI/CD Configurations
- .github
- .circleci
- .travis.yml
- .readthedocs.yml

### Development Files
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- .pre-commit-config.yaml
- Various linting configurations

### Build Artifacts
- Python cache directories
- Build and dist directories
- Compiled Python files

## Next Steps

1. Review the changes with \`git log\`
2. Test that the core functionality still works
3. Consider additional cleanup based on your needs
4. Push to your remote repository

## Restore from Backup

If needed, you can restore from backup:
\`\`\`bash
rm -rf $REPO_DIR
cp -r $BACKUP_DIR $REPO_DIR
\`\`\`
EOF

git add "$CLEANUP_REPORT"
git commit -m "Add cleanup report" || true

echo -e "\n${GREEN}✓ Cleanup completed successfully!${NC}"
echo -e "${BLUE}Cleanup report:${NC} $CLEANUP_REPORT"
echo -e "${YELLOW}Backup saved at:${NC} $BACKUP_DIR"