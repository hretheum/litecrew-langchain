#!/bin/bash
# setup-gitlab-labels.sh - Create all required GitLab labels via API

# Configuration
GITLAB_URL="https://gitlab.com/api/v4"
PROJECT_PATH="eof3/litecrewai"  # Update with your project path

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

# Function to create label
create_label() {
    local name=$1
    local color=$2
    local description=$3
    
    echo "Creating label: $name"
    curl -s --request POST \
        --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
        --header "Content-Type: application/json" \
        --data "{\"name\": \"$name\", \"color\": \"$color\", \"description\": \"$description\"}" \
        "$GITLAB_URL/projects/$PROJECT_ID/labels" > /dev/null
    
    if [ $? -eq 0 ]; then
        echo "  ✅ Created: $name"
    else
        echo "  ⚠️  Failed or already exists: $name"
    fi
}

echo ""
echo "🏷️  Creating Priority Labels..."
create_label "P0-Critical" "#FF0000" "Blocker issues that stop all work"
create_label "P1-High" "#FF6600" "Must complete this sprint"
create_label "P2-Medium" "#FFCC00" "Should complete next sprint"
create_label "P3-Low" "#99CC00" "Nice to have, backlog"

echo ""
echo "🏷️  Creating Type Labels..."
create_label "type::feature" "#7057FF" "New feature implementation"
create_label "type::bug" "#D73A4A" "Bug fix needed"
create_label "type::test" "#0E8A16" "Test related work"
create_label "type::docs" "#0075CA" "Documentation updates"
create_label "type::performance" "#FBCA04" "Performance improvements"

echo ""
echo "🏷️  Creating Component Labels..."
create_label "component::agent" "#1F78B4" "Agent component"
create_label "component::task" "#33A02C" "Task component"
create_label "component::crew" "#E31A1C" "Crew orchestration"
create_label "component::api" "#FF7F00" "API endpoints"
create_label "component::memory" "#6A3D9A" "Memory systems"
create_label "component::storage" "#A6CEE3" "Storage layer"
create_label "component::llm" "#B2DF8A" "LLM integrations"
create_label "component::monitoring" "#FB9A99" "Monitoring & metrics"

echo ""
echo "🏷️  Creating Status Labels..."
create_label "status::ready" "#0E8A16" "Ready to work on"
create_label "status::in-progress" "#FBCA04" "Currently being worked on"
create_label "status::review" "#0075CA" "In code review"
create_label "status::blocked" "#D73A4A" "Blocked by dependencies"

echo ""
echo "✅ Label creation complete!"
echo ""
echo "📊 Summary:"
echo "- Priority labels: 4"
echo "- Type labels: 5"
echo "- Component labels: 8"
echo "- Status labels: 4"
echo "- Total: 21 labels"