#!/bin/bash
# setup-gitlab-milestones.sh - Create all project milestones via API

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

# Function to create milestone
create_milestone() {
    local title=$1
    local description=$2
    local due_date=$3
    
    echo "Creating milestone: $title"
    curl -s --request POST \
        --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
        --header "Content-Type: application/json" \
        --data "{\"title\": \"$title\", \"description\": \"$description\", \"due_date\": \"$due_date\"}" \
        "$GITLAB_URL/projects/$PROJECT_ID/milestones" > /dev/null
    
    if [ $? -eq 0 ]; then
        echo "  ✅ Created: $title (Due: $due_date)"
    else
        echo "  ⚠️  Failed or already exists: $title"
    fi
}

# Calculate dates (starting from today)
START_DATE=$(date +%Y-%m-%d)

# Helper function to add days to date
add_days() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        date -j -v +${1}d -f "%Y-%m-%d" "$2" "+%Y-%m-%d"
    else
        # Linux
        date -d "$2 + $1 days" "+%Y-%m-%d"
    fi
}

echo ""
echo "📅 Creating Project Milestones..."
echo "Start date: $START_DATE"
echo ""

# Phase 0: Project Setup (3 days)
create_milestone "Phase 0 - Project Setup" \
    "GitLab infrastructure, development environment, CI/CD pipeline setup. Deliverables: Complete development environment ready for Phase 1." \
    "$(add_days 3 $START_DATE)"

# Phase 1: Core Foundation (5 days)
create_milestone "Phase 1 - Core Foundation" \
    "LiteAgent + LiteTask implementation. Deliverables: Working agents with <10ms creation time, <5MB memory per agent." \
    "$(add_days 8 $START_DATE)"

# Phase 2: Core Engine (5 days)
create_milestone "Phase 2 - Core Engine" \
    "LiteCrew orchestration engine. Deliverables: Full orchestration with <50MB memory for 10 agents, <50ms startup." \
    "$(add_days 13 $START_DATE)"

# Phase 3: LLM Integration (5 days)
create_milestone "Phase 3 - LLM Integration Layer" \
    "Multi-LLM support with streaming. Deliverables: Provider abstraction, async support, streaming responses." \
    "$(add_days 18 $START_DATE)"

# Phase 4: Storage Layer (5 days)
create_milestone "Phase 4 - Storage Layer" \
    "SQLite + Redis storage implementation. Deliverables: Persistent state management, <10ms write/read latency." \
    "$(add_days 23 $START_DATE)"

# Phase 5: API & Dashboard (5 days)
create_milestone "Phase 5 - API & Dashboard" \
    "REST API + monitoring dashboard. Deliverables: FastAPI endpoints, WebSocket support, simple dashboard." \
    "$(add_days 28 $START_DATE)"

# Phase 6: Production Readiness (5 days)
create_milestone "Phase 6 - Production Readiness" \
    "Rate limiting, structured outputs, event system. Deliverables: Production-grade features, <1ms overhead." \
    "$(add_days 33 $START_DATE)"

# Phase 7: Advanced Memory (5 days)
create_milestone "Phase 7 - Advanced Memory & Knowledge" \
    "Long-term memory, RAG, entity tracking. Deliverables: Knowledge management system, <50ms search." \
    "$(add_days 38 $START_DATE)"

# Phase 8: Advanced Orchestration (5 days)
create_milestone "Phase 8 - Advanced Orchestration" \
    "Planning, conditional flows, consensus. Deliverables: Complex orchestration patterns, dynamic planning." \
    "$(add_days 43 $START_DATE)"

# Phase 9: Production Features (5 days)
create_milestone "Phase 9 - Production Features" \
    "Testing framework, debugging, HITL. Deliverables: Complete production suite, v1.0.0 release ready." \
    "$(add_days 48 $START_DATE)"

echo ""
echo "✅ Milestone creation complete!"
echo ""
echo "📊 Summary:"
echo "- Total phases: 10 (including Phase 0)"
echo "- Total duration: 48 days"
echo "- End date: $(add_days 48 $START_DATE)"