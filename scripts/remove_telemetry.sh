#!/bin/bash

# CrewAI Telemetry Removal Script
# This script removes all telemetry and analytics from CrewAI fork
# It creates backups before making changes

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR="/Users/hretheum/dev/bezrobocie/crewAI/crewai-fork"
BACKUP_DIR="${BASE_DIR}/../telemetry_backup_$(date +%Y%m%d_%H%M%S)"
REPORT_FILE="${BASE_DIR}/../telemetry_removal_report_$(date +%Y%m%d_%H%M%S).txt"

# Files and directories to track
REMOVED_FILES=()
MODIFIED_FILES=()
TELEMETRY_IMPORTS=()

echo -e "${BLUE}=== CrewAI Telemetry Removal Script ===${NC}"
echo -e "${YELLOW}Base directory: ${BASE_DIR}${NC}"
echo -e "${YELLOW}Backup directory: ${BACKUP_DIR}${NC}"
echo -e "${YELLOW}Report file: ${REPORT_FILE}${NC}"
echo ""

# Function to create backup
create_backup() {
    echo -e "${BLUE}Creating backup...${NC}"
    mkdir -p "${BACKUP_DIR}"
    cp -r "${BASE_DIR}" "${BACKUP_DIR}/crewai-fork-backup"
    echo -e "${GREEN}✓ Backup created at: ${BACKUP_DIR}${NC}"
}

# Function to remove telemetry directory
remove_telemetry_directory() {
    echo -e "\n${BLUE}1. Removing telemetry directory...${NC}"
    
    if [ -d "${BASE_DIR}/src/crewai/telemetry" ]; then
        REMOVED_FILES+=("src/crewai/telemetry/")
        rm -rf "${BASE_DIR}/src/crewai/telemetry"
        echo -e "${GREEN}✓ Removed src/crewai/telemetry/${NC}"
    fi
    
    if [ -d "${BASE_DIR}/tests/telemetry" ]; then
        REMOVED_FILES+=("tests/telemetry/")
        rm -rf "${BASE_DIR}/tests/telemetry"
        echo -e "${GREEN}✓ Removed tests/telemetry/${NC}"
    fi
}

# Function to remove fingerprint/security tracking
remove_fingerprint_tracking() {
    echo -e "\n${BLUE}2. Removing fingerprint/security tracking...${NC}"
    
    if [ -d "${BASE_DIR}/src/crewai/security" ]; then
        # Check if security dir only contains fingerprint
        if [ -f "${BASE_DIR}/src/crewai/security/fingerprint.py" ]; then
            # Create a stub file instead of removing completely
            cat > "${BASE_DIR}/src/crewai/security/fingerprint.py" << 'EOF'
"""Stub for removed fingerprint functionality"""

class Fingerprint:
    """Stub class for removed fingerprint functionality"""
    def __init__(self, **kwargs):
        pass
    
    def to_dict(self):
        return {}
    
    @classmethod
    def from_dict(cls, data):
        return cls()
    
    @classmethod
    def generate(cls, seed=None, metadata=None):
        return cls()

class SecurityConfig:
    """Stub class for removed security config functionality"""
    def __init__(self, **kwargs):
        self.fingerprint = None
EOF
            MODIFIED_FILES+=("src/crewai/security/fingerprint.py")
            echo -e "${GREEN}✓ Replaced src/crewai/security/fingerprint.py with stub${NC}"
        fi
    fi
}

# Function to find and list telemetry imports
find_telemetry_imports() {
    echo -e "\n${BLUE}3. Finding telemetry imports...${NC}"
    
    # Find all Python files with telemetry imports
    while IFS= read -r file; do
        if grep -l "from crewai\.telemetry\|from crewai import.*Telemetry\|import.*telemetry\|Telemetry()" "$file" > /dev/null 2>&1; then
            TELEMETRY_IMPORTS+=("$file")
        fi
    done < <(find "${BASE_DIR}" -name "*.py" -type f)
    
    echo -e "${YELLOW}Found ${#TELEMETRY_IMPORTS[@]} files with telemetry imports${NC}"
}

# Function to remove telemetry from a Python file
remove_telemetry_from_file() {
    local file=$1
    local temp_file="${file}.tmp"
    local modified=false
    
    # Create a Python script to process the file
    cat > /tmp/remove_telemetry.py << 'EOF'
import sys
import re

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Remove telemetry imports
    content = re.sub(r'from crewai\.telemetry(?:\.[a-zA-Z_]+)* import [^\n]+\n', '', content)
    content = re.sub(r'from crewai import.*?Telemetry.*?\n', '', content)
    content = re.sub(r'import.*telemetry.*\n', '', content)
    
    # Remove telemetry instance creation
    content = re.sub(r'.*_telemetry.*=.*Telemetry\(\).*\n', '', content)
    content = re.sub(r'.*telemetry.*=.*Telemetry\(\).*\n', '', content)
    
    # Remove telemetry method calls
    content = re.sub(r'self\._telemetry\.[a-zA-Z_]+\([^)]*\)(?:\n)?', '', content)
    content = re.sub(r'telemetry\.[a-zA-Z_]+\([^)]*\)(?:\n)?', '', content)
    
    # Remove telemetry spans
    content = re.sub(r'.*=.*_telemetry\.[a-zA-Z_]+_span\([^)]*\).*\n', '', content)
    
    # Remove telemetry-related if blocks
    content = re.sub(r'if.*_telemetry.*:.*\n(?:\s+.*\n)*', '', content, flags=re.MULTILINE)
    
    # Clean up empty lines
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

if __name__ == "__main__":
    modified = process_file(sys.argv[1])
    sys.exit(0 if modified else 1)
EOF
    
    if python3 /tmp/remove_telemetry.py "$file"; then
        modified=true
        MODIFIED_FILES+=("$file")
    fi
    
    rm -f /tmp/remove_telemetry.py
    
    if [ "$modified" = true ]; then
        echo -e "${GREEN}✓ Modified: ${file#${BASE_DIR}/}${NC}"
    fi
}

# Function to process event listener separately
process_event_listener() {
    echo -e "\n${BLUE}4. Processing event_listener.py...${NC}"
    
    local event_listener="${BASE_DIR}/src/crewai/utilities/events/event_listener.py"
    
    if [ -f "$event_listener" ]; then
        # Create a modified version without telemetry
        cat > "$event_listener" << 'EOF'
from io import StringIO
from typing import Any, Dict

from pydantic import Field, PrivateAttr
from crewai.llm import LLM
from crewai.task import Task
from crewai.utilities import Logger
from crewai.utilities.constants import EMITTER_COLOR
from crewai.utilities.events.base_event_listener import BaseEventListener
from crewai.utilities.events.knowledge_events import (
    KnowledgeQueryCompletedEvent,
    KnowledgeQueryFailedEvent,
    KnowledgeQueryStartedEvent,
    KnowledgeRetrievalCompletedEvent,
    KnowledgeRetrievalStartedEvent,
    KnowledgeSearchQueryFailedEvent,
)
from crewai.utilities.events.llm_events import (
    LLMCallCompletedEvent,
    LLMCallFailedEvent,
    LLMCallStartedEvent,
    LLMStreamChunkEvent,
)
from crewai.utilities.events.utils.console_formatter import ConsoleFormatter

from .agent_events import (
    AgentExecutionCompletedEvent,
    AgentExecutionStartedEvent,
    AgentLogsStartedEvent,
    AgentLogsExecutionEvent,
    LiteAgentExecutionCompletedEvent,
    LiteAgentExecutionErrorEvent,
    LiteAgentExecutionStartedEvent,
)
from .crew_events import (
    CrewKickoffCompletedEvent,
    CrewKickoffFailedEvent,
    CrewKickoffStartedEvent,
    CrewTestCompletedEvent,
    CrewTestFailedEvent,
    CrewTestResultEvent,
    CrewTestStartedEvent,
    CrewTrainCompletedEvent,
    CrewTrainFailedEvent,
    CrewTrainStartedEvent,
)
from .flow_events import (
    FlowCreatedEvent,
    FlowFinishedEvent,
    FlowStartedEvent,
    MethodExecutionFailedEvent,
    MethodExecutionFinishedEvent,
    MethodExecutionStartedEvent,
)
from .task_events import TaskCompletedEvent, TaskFailedEvent, TaskStartedEvent
from .tool_usage_events import (
    ToolUsageErrorEvent,
    ToolUsageFinishedEvent,
    ToolUsageStartedEvent,
)
from .reasoning_events import (
    AgentReasoningStartedEvent,
    AgentReasoningCompletedEvent,
    AgentReasoningFailedEvent,
)


class EventListener(BaseEventListener):
    _instance = None
    logger = Logger(verbose=True, default_color=EMITTER_COLOR)
    execution_spans: Dict[Task, Any] = Field(default_factory=dict)
    next_chunk = 0
    text_stream = StringIO()
    knowledge_retrieval_in_progress = False
    knowledge_query_in_progress = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized") or not self._initialized:
            super().__init__()
            self.execution_spans = {}
            self._initialized = True
            self.formatter = ConsoleFormatter(verbose=True)

    # ----------- CREW EVENTS -----------

    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on(CrewKickoffStartedEvent)
        def on_crew_started(source, event: CrewKickoffStartedEvent):
            self.formatter.create_crew_tree(event.crew_name or "Crew", source.id)

        @crewai_event_bus.on(CrewKickoffCompletedEvent)
        def on_crew_completed(source, event: CrewKickoffCompletedEvent):
            final_string_output = event.output.raw
            self.formatter.update_crew_tree(
                self.formatter.current_crew_tree,
                event.crew_name or "Crew",
                source.id,
                "completed",
                final_string_output,
            )

        @crewai_event_bus.on(CrewKickoffFailedEvent)
        def on_crew_failed(source, event: CrewKickoffFailedEvent):
            self.formatter.update_crew_tree(
                self.formatter.current_crew_tree,
                event.crew_name or "Crew",
                source.id,
                "failed",
            )

        @crewai_event_bus.on(CrewTrainStartedEvent)
        def on_crew_train_started(source, event: CrewTrainStartedEvent):
            self.formatter.handle_crew_train_started(
                event.crew_name or "Crew", str(event.timestamp)
            )

        @crewai_event_bus.on(CrewTrainCompletedEvent)
        def on_crew_train_completed(source, event: CrewTrainCompletedEvent):
            self.formatter.handle_crew_train_completed(
                event.crew_name or "Crew", str(event.timestamp)
            )

        @crewai_event_bus.on(CrewTrainFailedEvent)
        def on_crew_train_failed(source, event: CrewTrainFailedEvent):
            self.formatter.handle_crew_train_failed(event.crew_name or "Crew")

        @crewai_event_bus.on(CrewTestResultEvent)
        def on_crew_test_result(source, event: CrewTestResultEvent):
            # Telemetry removed - just pass
            pass

        # ----------- TASK EVENTS -----------

        @crewai_event_bus.on(TaskStartedEvent)
        def on_task_started(source, event: TaskStartedEvent):
            self.formatter.create_task_branch(
                self.formatter.current_crew_tree, source.id
            )

        @crewai_event_bus.on(TaskCompletedEvent)
        def on_task_completed(source, event: TaskCompletedEvent):
            self.formatter.update_task_status(
                self.formatter.current_crew_tree,
                source.id,
                source.agent.role,
                "completed",
            )

        @crewai_event_bus.on(TaskFailedEvent)
        def on_task_failed(source, event: TaskFailedEvent):
            self.formatter.update_task_status(
                self.formatter.current_crew_tree,
                source.id,
                source.agent.role,
                "failed",
            )

        # ----------- AGENT EVENTS -----------

        @crewai_event_bus.on(AgentExecutionStartedEvent)
        def on_agent_execution_started(source, event: AgentExecutionStartedEvent):
            self.formatter.create_agent_branch(
                self.formatter.current_task_branch,
                event.agent.role,
                self.formatter.current_crew_tree,
            )

        @crewai_event_bus.on(AgentExecutionCompletedEvent)
        def on_agent_execution_completed(source, event: AgentExecutionCompletedEvent):
            self.formatter.update_agent_status(
                self.formatter.current_agent_branch,
                event.agent.role,
                self.formatter.current_crew_tree,
            )

        # ----------- LITE AGENT EVENTS -----------

        @crewai_event_bus.on(LiteAgentExecutionStartedEvent)
        def on_lite_agent_execution_started(
            source, event: LiteAgentExecutionStartedEvent
        ):
            """Handle LiteAgent execution started event."""
            self.formatter.handle_lite_agent_execution(
                event.agent_info["role"], status="started", **event.agent_info
            )

        @crewai_event_bus.on(LiteAgentExecutionCompletedEvent)
        def on_lite_agent_execution_completed(
            source, event: LiteAgentExecutionCompletedEvent
        ):
            """Handle LiteAgent execution completed event."""
            self.formatter.handle_lite_agent_execution(
                event.agent_info["role"], status="completed", **event.agent_info
            )

        @crewai_event_bus.on(LiteAgentExecutionErrorEvent)
        def on_lite_agent_execution_error(source, event: LiteAgentExecutionErrorEvent):
            """Handle LiteAgent execution error event."""
            self.formatter.handle_lite_agent_execution(
                event.agent_info["role"],
                status="failed",
                error=event.error,
                **event.agent_info,
            )

        # ----------- FLOW EVENTS -----------

        @crewai_event_bus.on(FlowCreatedEvent)
        def on_flow_created(source, event: FlowCreatedEvent):
            self.formatter.create_flow_tree(event.flow_name, str(source.flow_id))

        @crewai_event_bus.on(FlowStartedEvent)
        def on_flow_started(source, event: FlowStartedEvent):
            self.formatter.start_flow(event.flow_name, str(source.flow_id))

        @crewai_event_bus.on(FlowFinishedEvent)
        def on_flow_finished(source, event: FlowFinishedEvent):
            self.formatter.update_flow_status(
                self.formatter.current_flow_tree, event.flow_name, source.flow_id
            )

        @crewai_event_bus.on(MethodExecutionStartedEvent)
        def on_method_execution_started(source, event: MethodExecutionStartedEvent):
            self.formatter.update_method_status(
                self.formatter.current_method_branch,
                self.formatter.current_flow_tree,
                event.method_name,
                "running",
            )

        @crewai_event_bus.on(MethodExecutionFinishedEvent)
        def on_method_execution_finished(source, event: MethodExecutionFinishedEvent):
            self.formatter.update_method_status(
                self.formatter.current_method_branch,
                self.formatter.current_flow_tree,
                event.method_name,
                "completed",
            )

        @crewai_event_bus.on(MethodExecutionFailedEvent)
        def on_method_execution_failed(source, event: MethodExecutionFailedEvent):
            self.formatter.update_method_status(
                self.formatter.current_method_branch,
                self.formatter.current_flow_tree,
                event.method_name,
                "failed",
            )

        # ----------- TOOL USAGE EVENTS -----------

        @crewai_event_bus.on(ToolUsageStartedEvent)
        def on_tool_usage_started(source, event: ToolUsageStartedEvent):
            if isinstance(source, LLM):
                self.formatter.handle_llm_tool_usage_started(
                    event.tool_name,
                    event.tool_args,
                )
            else:
                self.formatter.handle_tool_usage_started(
                    self.formatter.current_agent_branch,
                    event.tool_name,
                    self.formatter.current_crew_tree,
                )

        @crewai_event_bus.on(ToolUsageFinishedEvent)
        def on_tool_usage_finished(source, event: ToolUsageFinishedEvent):
            if isinstance(source, LLM):
                self.formatter.handle_llm_tool_usage_finished(
                    event.tool_name,
                )
            else:
                self.formatter.handle_tool_usage_finished(
                    self.formatter.current_tool_branch,
                    event.tool_name,
                    self.formatter.current_crew_tree,
                )

        @crewai_event_bus.on(ToolUsageErrorEvent)
        def on_tool_usage_error(source, event: ToolUsageErrorEvent):
            if isinstance(source, LLM):
                self.formatter.handle_llm_tool_usage_error(
                    event.tool_name,
                    event.error,
                )
            else:
                self.formatter.handle_tool_usage_error(
                    self.formatter.current_tool_branch,
                    event.tool_name,
                    event.error,
                    self.formatter.current_crew_tree,
                )

        # ----------- LLM EVENTS -----------

        @crewai_event_bus.on(LLMCallStartedEvent)
        def on_llm_call_started(source, event: LLMCallStartedEvent):
            thinking_branch = self.formatter.handle_llm_call_started(
                self.formatter.current_agent_branch,
                self.formatter.current_crew_tree,
            )
            if thinking_branch is not None:
                self.formatter.current_tool_branch = thinking_branch

        @crewai_event_bus.on(LLMCallCompletedEvent)
        def on_llm_call_completed(source, event: LLMCallCompletedEvent):
            self.formatter.handle_llm_call_completed(
                self.formatter.current_tool_branch,
                self.formatter.current_agent_branch,
                self.formatter.current_crew_tree,
            )

        @crewai_event_bus.on(LLMCallFailedEvent)
        def on_llm_call_failed(source, event: LLMCallFailedEvent):
            self.formatter.handle_llm_call_failed(
                self.formatter.current_tool_branch,
                event.error,
                self.formatter.current_crew_tree,
            )

        @crewai_event_bus.on(LLMStreamChunkEvent)
        def on_llm_stream_chunk(source, event: LLMStreamChunkEvent):
            self.text_stream.write(event.chunk)
            self.text_stream.seek(self.next_chunk)
            content = self.text_stream.read()
            print(content, end="", flush=True)
            self.next_chunk = self.text_stream.tell()

        @crewai_event_bus.on(CrewTestStartedEvent)
        def on_crew_test_started(source, event: CrewTestStartedEvent):
            self.formatter.handle_crew_test_started(
                event.crew_name or "Crew", source.id, event.n_iterations
            )

        @crewai_event_bus.on(CrewTestCompletedEvent)
        def on_crew_test_completed(source, event: CrewTestCompletedEvent):
            self.formatter.handle_crew_test_completed(
                self.formatter.current_flow_tree,
                event.crew_name or "Crew",
            )

        @crewai_event_bus.on(CrewTestFailedEvent)
        def on_crew_test_failed(source, event: CrewTestFailedEvent):
            self.formatter.handle_crew_test_failed(event.crew_name or "Crew")

        @crewai_event_bus.on(KnowledgeRetrievalStartedEvent)
        def on_knowledge_retrieval_started(
            source, event: KnowledgeRetrievalStartedEvent
        ):
            if self.knowledge_retrieval_in_progress:
                return

            self.knowledge_retrieval_in_progress = True

            self.formatter.handle_knowledge_retrieval_started(
                self.formatter.current_agent_branch,
                self.formatter.current_crew_tree,
            )

        @crewai_event_bus.on(KnowledgeRetrievalCompletedEvent)
        def on_knowledge_retrieval_completed(
            source, event: KnowledgeRetrievalCompletedEvent
        ):
            if not self.knowledge_retrieval_in_progress:
                return

            self.knowledge_retrieval_in_progress = False
            self.formatter.handle_knowledge_retrieval_completed(
                self.formatter.current_agent_branch,
                self.formatter.current_crew_tree,
                event.retrieved_knowledge,
            )

        @crewai_event_bus.on(KnowledgeQueryStartedEvent)
        def on_knowledge_query_started(source, event: KnowledgeQueryStartedEvent):
            pass

        @crewai_event_bus.on(KnowledgeQueryFailedEvent)
        def on_knowledge_query_failed(source, event: KnowledgeQueryFailedEvent):
            self.formatter.handle_knowledge_query_failed(
                self.formatter.current_agent_branch,
                event.error,
                self.formatter.current_crew_tree,
            )

        @crewai_event_bus.on(KnowledgeQueryCompletedEvent)
        def on_knowledge_query_completed(source, event: KnowledgeQueryCompletedEvent):
            pass

        @crewai_event_bus.on(KnowledgeSearchQueryFailedEvent)
        def on_knowledge_search_query_failed(
            source, event: KnowledgeSearchQueryFailedEvent
        ):
            self.formatter.handle_knowledge_search_query_failed(
                self.formatter.current_agent_branch,
                event.error,
                self.formatter.current_crew_tree,
            )

        # ----------- REASONING EVENTS -----------

        @crewai_event_bus.on(AgentReasoningStartedEvent)
        def on_agent_reasoning_started(source, event: AgentReasoningStartedEvent):
            self.formatter.handle_reasoning_started(
                self.formatter.current_agent_branch,
                event.attempt,
                self.formatter.current_crew_tree,
            )

        @crewai_event_bus.on(AgentReasoningCompletedEvent)
        def on_agent_reasoning_completed(source, event: AgentReasoningCompletedEvent):
            self.formatter.handle_reasoning_completed(
                event.plan,
                event.ready,
                self.formatter.current_crew_tree,
            )

        @crewai_event_bus.on(AgentReasoningFailedEvent)
        def on_agent_reasoning_failed(source, event: AgentReasoningFailedEvent):
            self.formatter.handle_reasoning_failed(
                event.error,
                self.formatter.current_crew_tree,
            )

        # ----------- AGENT LOGGING EVENTS -----------

        @crewai_event_bus.on(AgentLogsStartedEvent)
        def on_agent_logs_started(source, event: AgentLogsStartedEvent):
            self.formatter.handle_agent_logs_started(
                event.agent_role,
                event.task_description,
                event.verbose,
            )

        @crewai_event_bus.on(AgentLogsExecutionEvent)
        def on_agent_logs_execution(source, event: AgentLogsExecutionEvent):
            self.formatter.handle_agent_logs_execution(
                event.agent_role,
                event.formatted_answer,
                event.verbose,
            )


event_listener = EventListener()
EOF
        MODIFIED_FILES+=("src/crewai/utilities/events/event_listener.py")
        echo -e "${GREEN}✓ Modified event_listener.py to remove telemetry${NC}"
    fi
}

# Function to process tool_usage.py separately
process_tool_usage() {
    echo -e "\n${BLUE}5. Processing tool_usage.py...${NC}"
    
    local tool_usage="${BASE_DIR}/src/crewai/tools/tool_usage.py"
    
    if [ -f "$tool_usage" ]; then
        # Remove telemetry imports and usage
        sed -i '' '/from crewai.telemetry import Telemetry/d' "$tool_usage"
        sed -i '' 's/self\._telemetry: Telemetry = Telemetry()/# Telemetry removed/g' "$tool_usage"
        sed -i '' 's/self\._telemetry\.tool_repeated_usage(/# Telemetry removed: tool_repeated_usage(/g' "$tool_usage"
        sed -i '' 's/self\._telemetry\.tool_usage(/# Telemetry removed: tool_usage(/g' "$tool_usage"
        sed -i '' 's/self\._telemetry\.tool_usage_error(/# Telemetry removed: tool_usage_error(/g' "$tool_usage"
        
        MODIFIED_FILES+=("src/crewai/tools/tool_usage.py")
        echo -e "${GREEN}✓ Modified tool_usage.py to remove telemetry${NC}"
    fi
}

# Function to process command.py
process_command() {
    echo -e "\n${BLUE}6. Processing command.py...${NC}"
    
    local command="${BASE_DIR}/src/crewai/cli/command.py"
    
    if [ -f "$command" ]; then
        cat > "$command" << 'EOF'
import requests
from requests.exceptions import JSONDecodeError
from rich.console import Console

from crewai.cli.authentication.token import get_auth_token
from crewai.cli.plus_api import PlusAPI

console = Console()


class BaseCommand:
    def __init__(self):
        # Telemetry removed
        pass


class PlusAPIMixin:
    def __init__(self, telemetry=None):
        try:
            # Telemetry removed
            self.plus_api_client = PlusAPI(api_key=get_auth_token())
        except Exception:
            console.print(
                "Please sign up/login to CrewAI+ before using the CLI.",
                style="bold red",
            )
            console.print("Run 'crewai signup' to sign up/login.", style="bold green")
            raise SystemExit

    def _validate_response(self, response: requests.Response) -> None:
        """
        Handle and display error messages from API responses.

        Args:
            response (requests.Response): The response from the Plus API
        """
        try:
            json_response = response.json()
        except (JSONDecodeError, ValueError):
            console.print(
                "Failed to parse response from Enterprise API failed. Details:",
                style="bold red",
            )
            console.print(f"Status Code: {response.status_code}")
            console.print(f"Response:\n{response.content}")
            raise SystemExit

        if response.status_code == 422:
            error_detail = json_response.get("detail", [])
            for error in error_detail:
                field = error.get("loc", ["Unknown field"])[-1]
                message = error.get("msg", "Unknown error")
                console.print(f"Validation Error: {field} - {message}", style="bold red")
            raise SystemExit

        if response.status_code != 200:
            error_message = json_response.get("detail", {}).get(
                "message", "An unknown error occurred"
            )
            console.print(f"Enterprise API Error: {error_message}", style="bold red")
            raise SystemExit
EOF
        MODIFIED_FILES+=("src/crewai/cli/command.py")
        echo -e "${GREEN}✓ Modified command.py to remove telemetry${NC}"
    fi
}

# Function to remove telemetry from deploy/main.py
process_deploy_main() {
    echo -e "\n${BLUE}7. Processing deploy/main.py...${NC}"
    
    local deploy_main="${BASE_DIR}/src/crewai/cli/deploy/main.py"
    
    if [ -f "$deploy_main" ]; then
        # Remove telemetry calls but keep the structure
        sed -i '' 's/PlusAPIMixin.__init__(self, telemetry=self._telemetry)/PlusAPIMixin.__init__(self)/g' "$deploy_main"
        sed -i '' 's/self._start_deployment_span = self._telemetry.start_deployment_span(uuid)/# Telemetry removed/g' "$deploy_main"
        sed -i '' 's/self._create_crew_deployment_span = (/# Telemetry removed/g' "$deploy_main"
        sed -i '' 's/    self._telemetry.create_crew_deployment_span()/# Telemetry removed/g' "$deploy_main"
        sed -i '' 's/)$//g' "$deploy_main"
        
        MODIFIED_FILES+=("src/crewai/cli/deploy/main.py")
        echo -e "${GREEN}✓ Modified deploy/main.py to remove telemetry${NC}"
    fi
}

# Function to check for environment variables
check_env_vars() {
    echo -e "\n${BLUE}8. Checking for telemetry-related environment variables...${NC}"
    
    env_vars_found=0
    
    # Search for telemetry environment variables in code
    if grep -r "OTEL_SDK_DISABLED\|CREWAI_DISABLE_TELEMETRY\|CREWAI_TELEMETRY" "${BASE_DIR}" --include="*.py" > /dev/null 2>&1; then
        echo -e "${YELLOW}Found references to telemetry environment variables${NC}"
        env_vars_found=1
    fi
    
    if [ $env_vars_found -eq 0 ]; then
        echo -e "${GREEN}✓ No telemetry environment variables found${NC}"
    fi
}

# Function to generate report
generate_report() {
    echo -e "\n${BLUE}Generating report...${NC}"
    
    {
        echo "CrewAI Telemetry Removal Report"
        echo "==============================="
        echo "Date: $(date)"
        echo ""
        echo "Removed Files:"
        echo "--------------"
        for file in "${REMOVED_FILES[@]}"; do
            echo "- $file"
        done
        echo ""
        echo "Modified Files:"
        echo "---------------"
        for file in "${MODIFIED_FILES[@]}"; do
            echo "- ${file#${BASE_DIR}/}"
        done
        echo ""
        echo "Summary:"
        echo "--------"
        echo "- Removed ${#REMOVED_FILES[@]} files/directories"
        echo "- Modified ${#MODIFIED_FILES[@]} files"
        echo ""
        echo "Actions taken:"
        echo "1. Removed telemetry directory and test files"
        echo "2. Replaced fingerprint.py with stub implementation"
        echo "3. Removed telemetry imports and calls from all Python files"
        echo "4. Modified event_listener.py to remove telemetry functionality"
        echo "5. Modified tool_usage.py to remove telemetry tracking"
        echo "6. Modified CLI command files to remove telemetry initialization"
        echo ""
        echo "Backup location: ${BACKUP_DIR}"
    } > "$REPORT_FILE"
    
    echo -e "${GREEN}✓ Report saved to: ${REPORT_FILE}${NC}"
}

# Main execution
main() {
    # Ask for confirmation
    echo -e "${YELLOW}This script will remove all telemetry from CrewAI.${NC}"
    echo -e "${YELLOW}A backup will be created before any changes.${NC}"
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Operation cancelled.${NC}"
        exit 1
    fi
    
    # Create backup
    create_backup
    
    # Remove telemetry
    remove_telemetry_directory
    remove_fingerprint_tracking
    find_telemetry_imports
    
    # Process specific files first
    process_event_listener
    process_tool_usage
    process_command
    process_deploy_main
    
    # Process remaining files
    echo -e "\n${BLUE}9. Processing remaining files...${NC}"
    for file in "${TELEMETRY_IMPORTS[@]}"; do
        # Skip files we've already processed
        if [[ ! " ${MODIFIED_FILES[@]} " =~ " ${file} " ]]; then
            remove_telemetry_from_file "$file"
        fi
    done
    
    # Check environment variables
    check_env_vars
    
    # Generate report
    generate_report
    
    echo -e "\n${GREEN}✅ Telemetry removal completed!${NC}"
    echo -e "${YELLOW}Please review the changes and test the code.${NC}"
    echo -e "${YELLOW}Report saved to: ${REPORT_FILE}${NC}"
    echo -e "${YELLOW}Backup saved to: ${BACKUP_DIR}${NC}"
}

# Run main function
main