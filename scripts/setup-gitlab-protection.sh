#!/bin/bash
# setup-gitlab-protection.sh - Configure protected branches via GitLab API

# Configuration
GITLAB_URL="https://gitlab.com/api/v4"
PROJECT_PATH="eof3/litecrewai"

# Check if GITLAB_TOKEN is set
if [ -z "$GITLAB_TOKEN" ]; then
    echo "❌ Error: GITLAB_TOKEN environment variable not set"
    echo "Please run: export GITLAB_TOKEN='your-personal-access-token'"
    exit 1
fi

# Get project ID
echo "🔍 Getting project ID for $PROJECT_PATH..."
PROJECT_ID=$(curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    "$GITLAB_URL/projects/$(echo $PROJECT_PATH | sed 's/\//%2F/g')" | \
    grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Could not find project ID"
    exit 1
fi

echo "✅ Found project ID: $PROJECT_ID"

# Configure protected branch for master/main
echo ""
echo "🔒 Configuring protected branch: master..."

# First, unprotect if already protected (to update settings)
curl -s --request DELETE \
    --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    "$GITLAB_URL/projects/$PROJECT_ID/protected_branches/master" > /dev/null 2>&1

# Create protected branch with proper settings
RESPONSE=$(curl -s --request POST \
    --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    --header "Content-Type: application/json" \
    --data '{
        "name": "master",
        "push_access_level": 0,
        "merge_access_level": 40,
        "unprotect_access_level": 40,
        "allow_force_push": false
    }' \
    "$GITLAB_URL/projects/$PROJECT_ID/protected_branches")

if echo "$RESPONSE" | grep -q '"name":"master"'; then
    echo "  ✅ Protected branch 'master' configured:"
    echo "     - Push access: No one"
    echo "     - Merge access: Maintainers"
    echo "     - Force push: Disabled"
else
    echo "  ⚠️  Failed to protect branch 'master'"
    echo "  Response: $RESPONSE"
fi

# Check Container Registry status
echo ""
echo "📦 Checking Container Registry..."

PROJECT_INFO=$(curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    "$GITLAB_URL/projects/$PROJECT_ID")

if echo "$PROJECT_INFO" | grep -q '"container_registry_enabled":true'; then
    echo "  ✅ Container Registry is enabled"
    echo "  📍 Registry URL: registry.gitlab.com/$PROJECT_PATH"
else
    echo "  ❌ Container Registry is disabled"
    echo "  ℹ️  Please enable it manually in GitLab UI"
fi

# Create CI/CD variables
echo ""
echo "🔧 Setting up CI/CD variables..."

# Function to create or update variable
create_or_update_variable() {
    local key=$1
    local value=$2
    local protected=$3
    
    # Try to create
    RESPONSE=$(curl -s --request POST \
        --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
        --header "Content-Type: application/json" \
        --data "{
            \"key\": \"$key\",
            \"value\": \"$value\",
            \"protected\": $protected,
            \"masked\": false
        }" \
        "$GITLAB_URL/projects/$PROJECT_ID/variables")
    
    if echo "$RESPONSE" | grep -q "has already been taken"; then
        # Update if exists
        curl -s --request PUT \
            --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
            --header "Content-Type: application/json" \
            --data "{
                \"value\": \"$value\",
                \"protected\": $protected,
                \"masked\": false
            }" \
            "$GITLAB_URL/projects/$PROJECT_ID/variables/$key" > /dev/null
        echo "  ✅ Updated: $key"
    else
        echo "  ✅ Created: $key"
    fi
}

# Set basic CI/CD variables
create_or_update_variable "CI_REGISTRY_USER" "gitlab-ci-token" false
create_or_update_variable "CI_REGISTRY_PASSWORD" "\$CI_JOB_TOKEN" false

echo ""
echo "✅ GitLab protection setup complete!"
echo ""
echo "📋 Summary:"
echo "- Protected branch 'master' configured"
echo "- Container Registry status checked"
echo "- Basic CI/CD variables set"
echo ""
echo "ℹ️  Note: Some settings like enabling Container Registry may still require GitLab UI access"