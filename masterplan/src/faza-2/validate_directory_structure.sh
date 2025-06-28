#!/bin/bash
# validate_directory_structure.sh

echo "🔍 Validating directory structure..."

# Check directories exist
dirs=(
    "/opt/litecrewai/app"
    "/opt/litecrewai/config"
    "/opt/litecrewai/data"
    "/opt/litecrewai/logs"
    "/opt/litecrewai/backups"
    "/opt/litecrewai/scripts"
)

for dir in "${dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Missing directory: $dir"
        exit 1
    fi
    
    # Check ownership
    owner=$(stat -c '%U:%G' "$dir")
    if [ "$owner" != "litecrewai:litecrewai" ]; then
        echo "❌ Wrong ownership for $dir: $owner"
        exit 1
    fi
done

# Check git
if ! git -C /opt/litecrewai rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Git not initialized"
    exit 1
fi

# Check .env.example
env_vars=$(grep -c "=" /opt/litecrewai/.env.example)
if [ "$env_vars" -lt 10 ]; then
    echo "❌ .env.example has only $env_vars variables (need >= 10)"
    exit 1
fi

echo "✅ Directory structure validated!"