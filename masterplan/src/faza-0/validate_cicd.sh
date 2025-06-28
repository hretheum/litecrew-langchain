#!/bin/bash
# validate_cicd.sh

echo "🔍 Validating CI/CD setup..."

# Check git remote
cd /opt/litecrewai
git remote -v | grep -q "github.com" || { echo "❌ No GitHub remote"; exit 1; }

# Check workflows exist
workflows=(".github/workflows/test.yml" ".github/workflows/deploy.yml" ".github/workflows/scheduled-backup.yml")
for workflow in "${workflows[@]}"; do
    [ -f "$workflow" ] || { echo "❌ Missing workflow: $workflow"; exit 1; }
done

# Test deployment script
if [ -f "scripts/deploy.sh" ]; then
    bash scripts/deploy.sh --dry-run || { echo "❌ Deploy script failed"; exit 1; }
fi

# Check for required files
files=(".gitignore" "README.md" "LICENSE" "CONTRIBUTING.md")
for file in "${files[@]}"; do
    [ -f "$file" ] || { echo "❌ Missing file: $file"; exit 1; }
done

echo "✅ CI/CD setup validated!"