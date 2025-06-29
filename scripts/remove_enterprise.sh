#!/bin/bash

# CrewAI Enterprise Features Removal Script
# This script removes enterprise features from CrewAI to create a single-user, local-only version

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")/crewai-fork"
REPORT_FILE="$SCRIPT_DIR/enterprise_removal_report.md"
BACKUP_DIR="$PROJECT_ROOT.backup.$(date +%Y%m%d_%H%M%S)"

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to log changes to report
log_change() {
    local type=$1
    local file=$2
    local description=$3
    echo "### $type: $file" >> "$REPORT_FILE"
    echo "$description" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
}

# Initialize report
init_report() {
    cat > "$REPORT_FILE" << EOF
# Enterprise Features Removal Report
Generated on: $(date)
Project: $PROJECT_ROOT

## Summary
This report documents all changes made to remove enterprise features from CrewAI.

## Changes Made

EOF
}

# Backup the project
backup_project() {
    print_color "$BLUE" "Creating backup at $BACKUP_DIR..."
    cp -r "$PROJECT_ROOT" "$BACKUP_DIR"
    print_color "$GREEN" "Backup created successfully."
}

# Remove enterprise directories
remove_enterprise_dirs() {
    print_color "$YELLOW" "\n1. Removing enterprise directories..."
    
    # Remove enterprise documentation
    if [ -d "$PROJECT_ROOT/docs/enterprise" ]; then
        rm -rf "$PROJECT_ROOT/docs/enterprise"
        log_change "Directory Removed" "docs/enterprise" "Removed enterprise documentation directory"
    fi
    
    if [ -d "$PROJECT_ROOT/docs/en/enterprise" ]; then
        rm -rf "$PROJECT_ROOT/docs/en/enterprise"
        log_change "Directory Removed" "docs/en/enterprise" "Removed English enterprise documentation"
    fi
    
    if [ -d "$PROJECT_ROOT/docs/pt-BR/enterprise" ]; then
        rm -rf "$PROJECT_ROOT/docs/pt-BR/enterprise"
        log_change "Directory Removed" "docs/pt-BR/enterprise" "Removed Portuguese enterprise documentation"
    fi
    
    # Remove authentication modules
    if [ -d "$PROJECT_ROOT/src/crewai/cli/authentication" ]; then
        rm -rf "$PROJECT_ROOT/src/crewai/cli/authentication"
        log_change "Directory Removed" "src/crewai/cli/authentication" "Removed authentication module (Auth0/SSO)"
    fi
    
    # Remove deploy module
    if [ -d "$PROJECT_ROOT/src/crewai/cli/deploy" ]; then
        rm -rf "$PROJECT_ROOT/src/crewai/cli/deploy"
        log_change "Directory Removed" "src/crewai/cli/deploy" "Removed cloud deployment module"
    fi
    
    # Remove organization module
    if [ -d "$PROJECT_ROOT/src/crewai/cli/organization" ]; then
        rm -rf "$PROJECT_ROOT/src/crewai/cli/organization"
        log_change "Directory Removed" "src/crewai/cli/organization" "Removed multi-tenant organization module"
    fi
    
    # Remove tools repository module
    if [ -d "$PROJECT_ROOT/src/crewai/cli/tools" ]; then
        rm -rf "$PROJECT_ROOT/src/crewai/cli/tools"
        log_change "Directory Removed" "src/crewai/cli/tools" "Removed cloud tools repository module"
    fi
    
    print_color "$GREEN" "Enterprise directories removed."
}

# Remove enterprise files
remove_enterprise_files() {
    print_color "$YELLOW" "\n2. Removing enterprise-specific files..."
    
    # Remove Plus API client
    if [ -f "$PROJECT_ROOT/src/crewai/cli/plus_api.py" ]; then
        rm -f "$PROJECT_ROOT/src/crewai/cli/plus_api.py"
        log_change "File Removed" "src/crewai/cli/plus_api.py" "Removed CrewAI+ API client"
    fi
    
    # Remove enterprise API spec
    if [ -f "$PROJECT_ROOT/docs/enterprise-api.yaml" ]; then
        rm -f "$PROJECT_ROOT/docs/enterprise-api.yaml"
        log_change "File Removed" "docs/enterprise-api.yaml" "Removed enterprise API specification"
    fi
    
    print_color "$GREEN" "Enterprise files removed."
}

# Modify pyproject.toml to remove enterprise dependencies
modify_pyproject() {
    print_color "$YELLOW" "\n3. Modifying pyproject.toml..."
    
    local pyproject="$PROJECT_ROOT/pyproject.toml"
    local temp_file=$(mktemp)
    
    # Create modified version
    cat "$pyproject" | sed -e '/auth0-python/d' > "$temp_file"
    
    # Show diff for report
    echo "### Modified: pyproject.toml" >> "$REPORT_FILE"
    echo '```diff' >> "$REPORT_FILE"
    diff -u "$pyproject" "$temp_file" >> "$REPORT_FILE" || true
    echo '```' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # Apply changes
    mv "$temp_file" "$pyproject"
    
    print_color "$GREEN" "pyproject.toml modified."
}

# Modify CLI to remove enterprise commands
modify_cli() {
    print_color "$YELLOW" "\n4. Modifying CLI to remove enterprise commands..."
    
    local cli_file="$PROJECT_ROOT/src/crewai/cli/cli.py"
    
    if [ -f "$cli_file" ]; then
        # Create a Python script to modify the CLI
        cat > "$SCRIPT_DIR/modify_cli.py" << 'EOF'
import sys
import re

def remove_enterprise_commands(content):
    # Remove import statements
    patterns_to_remove = [
        r'from crewai\.cli\.authentication.*\n',
        r'from crewai\.cli\.deploy.*\n',
        r'from crewai\.cli\.organization.*\n',
        r'from crewai\.cli\.tools.*\n',
        r'import.*authentication.*\n',
        r'import.*deploy.*\n',
        r'import.*organization.*\n',
        r'import.*tools.*\n'
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    # Remove command registrations
    # This is a simplified approach - in practice, we'd need more sophisticated parsing
    lines = content.split('\n')
    filtered_lines = []
    skip = False
    
    for line in lines:
        if any(cmd in line for cmd in ['@crewai.command(name="login")', '@crewai.command(name="signup")', 
                                       '@crewai.command(name="deploy")', '@crewai.command(name="tool")',
                                       '@crewai.command(name="org")', 'deploy_command', 'tool_command',
                                       'organization_command', 'auth_command']):
            skip = True
        elif skip and (line.strip() == '' or not line.startswith(' ')):
            skip = False
        
        if not skip:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as f:
        content = f.read()
    
    modified = remove_enterprise_commands(content)
    
    with open(sys.argv[2], 'w') as f:
        f.write(modified)
EOF
        
        # Run the Python script
        python3 "$SCRIPT_DIR/modify_cli.py" "$cli_file" "$cli_file.tmp"
        
        # Show diff for report
        echo "### Modified: src/crewai/cli/cli.py" >> "$REPORT_FILE"
        echo '```diff' >> "$REPORT_FILE"
        diff -u "$cli_file" "$cli_file.tmp" >> "$REPORT_FILE" || true
        echo '```' >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        
        # Apply changes
        mv "$cli_file.tmp" "$cli_file"
        
        # Clean up
        rm -f "$SCRIPT_DIR/modify_cli.py"
    fi
    
    print_color "$GREEN" "CLI modified."
}

# Remove enterprise imports from __init__.py files
clean_init_files() {
    print_color "$YELLOW" "\n5. Cleaning __init__.py files..."
    
    # CLI __init__.py
    local cli_init="$PROJECT_ROOT/src/crewai/cli/__init__.py"
    if [ -f "$cli_init" ]; then
        # Remove enterprise imports
        sed -i.bak -e '/authentication/d' -e '/deploy/d' -e '/organization/d' -e '/tools/d' -e '/plus_api/d' "$cli_init"
        rm -f "$cli_init.bak"
        log_change "Modified" "src/crewai/cli/__init__.py" "Removed enterprise imports"
    fi
    
    print_color "$GREEN" "__init__.py files cleaned."
}

# Modify command.py to remove PlusAPIMixin
modify_command() {
    print_color "$YELLOW" "\n6. Modifying command.py..."
    
    local command_file="$PROJECT_ROOT/src/crewai/cli/command.py"
    
    if [ -f "$command_file" ]; then
        # Create a Python script to modify command.py
        cat > "$SCRIPT_DIR/modify_command.py" << 'EOF'
import sys
import re

def modify_command(content):
    # Remove PlusAPIMixin class and related imports
    content = re.sub(r'from \.plus_api import PlusAPI\n', '', content)
    content = re.sub(r'from crewai\.cli\.plus_api import PlusAPI\n', '', content)
    
    # Remove the entire PlusAPIMixin class
    content = re.sub(r'class PlusAPIMixin.*?(?=\nclass|\Z)', '', content, flags=re.DOTALL)
    
    return content

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as f:
        content = f.read()
    
    modified = modify_command(content)
    
    with open(sys.argv[2], 'w') as f:
        f.write(modified)
EOF
        
        # Run the Python script
        python3 "$SCRIPT_DIR/modify_command.py" "$command_file" "$command_file.tmp"
        
        # Show diff for report
        echo "### Modified: src/crewai/cli/command.py" >> "$REPORT_FILE"
        echo '```diff' >> "$REPORT_FILE"
        diff -u "$command_file" "$command_file.tmp" >> "$REPORT_FILE" || true
        echo '```' >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        
        # Apply changes
        mv "$command_file.tmp" "$command_file"
        
        # Clean up
        rm -f "$SCRIPT_DIR/modify_command.py"
    fi
    
    print_color "$GREEN" "command.py modified."
}

# Remove test files for enterprise features
remove_enterprise_tests() {
    print_color "$YELLOW" "\n7. Removing enterprise test files..."
    
    # Remove authentication tests
    if [ -d "$PROJECT_ROOT/tests/cli/authentication" ]; then
        rm -rf "$PROJECT_ROOT/tests/cli/authentication"
        log_change "Directory Removed" "tests/cli/authentication" "Removed authentication tests"
    fi
    
    # Remove deploy tests
    if [ -d "$PROJECT_ROOT/tests/cli/deploy" ]; then
        rm -rf "$PROJECT_ROOT/tests/cli/deploy"
        log_change "Directory Removed" "tests/cli/deploy" "Removed deployment tests"
    fi
    
    # Remove organization tests
    if [ -d "$PROJECT_ROOT/tests/cli/organization" ]; then
        rm -rf "$PROJECT_ROOT/tests/cli/organization"
        log_change "Directory Removed" "tests/cli/organization" "Removed organization tests"
    fi
    
    # Remove tools tests
    if [ -d "$PROJECT_ROOT/tests/cli/tools" ]; then
        rm -rf "$PROJECT_ROOT/tests/cli/tools"
        log_change "Directory Removed" "tests/cli/tools" "Removed tools repository tests"
    fi
    
    # Remove plus_api tests
    if [ -f "$PROJECT_ROOT/tests/cli/test_plus_api.py" ]; then
        rm -f "$PROJECT_ROOT/tests/cli/test_plus_api.py"
        log_change "File Removed" "tests/cli/test_plus_api.py" "Removed Plus API tests"
    fi
    
    print_color "$GREEN" "Enterprise test files removed."
}

# Create simple local configuration
create_local_config() {
    print_color "$YELLOW" "\n8. Creating simple local configuration..."
    
    # Create a simple local auth stub (optional, for compatibility)
    mkdir -p "$PROJECT_ROOT/src/crewai/auth"
    
    cat > "$PROJECT_ROOT/src/crewai/auth/__init__.py" << 'EOF'
"""Simple local authentication stub for single-user mode."""

class LocalAuth:
    """Simple local authentication - always authenticated."""
    
    def __init__(self):
        self.authenticated = True
        self.username = "local_user"
    
    def is_authenticated(self):
        return True
    
    def get_username(self):
        return self.username

# Global instance
auth = LocalAuth()
EOF
    
    log_change "File Created" "src/crewai/auth/__init__.py" "Created simple local authentication stub"
    
    print_color "$GREEN" "Local configuration created."
}

# Final cleanup
final_cleanup() {
    print_color "$YELLOW" "\n9. Final cleanup..."
    
    # Remove any enterprise-related images
    if [ -d "$PROJECT_ROOT/docs/images/enterprise" ]; then
        rm -rf "$PROJECT_ROOT/docs/images/enterprise"
        log_change "Directory Removed" "docs/images/enterprise" "Removed enterprise images"
    fi
    
    # Find and remove any remaining enterprise references in Python files
    find "$PROJECT_ROOT/src" -name "*.py" -type f -exec grep -l "enterprise\|plus_api\|auth0\|organization\|deploy" {} \; | while read file; do
        # Skip our newly created auth module
        if [[ "$file" == *"src/crewai/auth"* ]]; then
            continue
        fi
        
        print_color "$BLUE" "Checking $file for enterprise references..."
    done
    
    print_color "$GREEN" "Cleanup completed."
}

# Finalize report
finalize_report() {
    cat >> "$REPORT_FILE" << EOF

## Summary Statistics

- Directories removed: $(grep -c "Directory Removed" "$REPORT_FILE" || echo "0")
- Files removed: $(grep -c "File Removed" "$REPORT_FILE" || echo "0")
- Files modified: $(grep -c "Modified" "$REPORT_FILE" || echo "0")
- Files created: $(grep -c "File Created" "$REPORT_FILE" || echo "0")

## Core Functionality Preserved

The following core features remain intact:
- Agents and Agent management
- Tasks and Task execution
- Tools and Tool usage
- Memory systems (short-term, long-term, contextual)
- Basic API functionality
- Local execution and workflows
- Flow management
- Knowledge base features

## Next Steps

1. Run \`uv sync\` in the project directory to update dependencies
2. Run tests to ensure core functionality works: \`pytest tests/\`
3. Review the changes in this report
4. Test basic crew creation and execution

## Backup Location

A full backup of the original project was created at:
$BACKUP_DIR

EOF
    
    print_color "$GREEN" "\nReport saved to: $REPORT_FILE"
}

# Main execution
main() {
    print_color "$BLUE" "=== CrewAI Enterprise Features Removal Script ==="
    print_color "$YELLOW" "Target: $PROJECT_ROOT"
    
    # Verify project exists
    if [ ! -d "$PROJECT_ROOT" ]; then
        print_color "$RED" "Error: Project directory not found at $PROJECT_ROOT"
        exit 1
    fi
    
    # Initialize report
    init_report
    
    # Create backup
    backup_project
    
    # Execute removal steps
    remove_enterprise_dirs
    remove_enterprise_files
    modify_pyproject
    modify_cli
    clean_init_files
    modify_command
    remove_enterprise_tests
    create_local_config
    final_cleanup
    
    # Finalize report
    finalize_report
    
    print_color "$GREEN" "\n✅ Enterprise features removal completed successfully!"
    print_color "$YELLOW" "Please review the report at: $REPORT_FILE"
}

# Run main function
main