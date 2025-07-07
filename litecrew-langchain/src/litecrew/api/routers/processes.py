"""Process types API endpoints."""

from typing import List

from fastapi import APIRouter, HTTPException, status

from litecrew.processes import ProcessFactory
from litecrew.crew import LiteCrew

from ..models import ProcessType, ProcessSwitch, CrewResponse
from ..storage import get_storage
from ..process_callbacks import create_process_config_with_websocket
from ..visualization import add_visualization_endpoints

router = APIRouter()


# Process type information
PROCESS_TYPES = {
    "sequential": {
        "description": "Execute tasks one after another in order",
        "supports_moderator": False,
        "configurable_options": ["verbose", "max_iterations", "timeout"],
        "example_config": {"verbose": True, "max_iterations": 10}
    },
    "hierarchical": {
        "description": "Manager delegates tasks to workers",
        "supports_moderator": True,
        "configurable_options": ["verbose", "manager_rounds"],
        "example_config": {"manager_rounds": 2}
    },
    "conversational": {
        "description": "Natural conversation between agents",
        "supports_moderator": False,
        "configurable_options": ["min_turns", "max_turns", "turn_style"],
        "example_config": {"min_turns": 3, "max_turns": 10, "turn_style": "round_robin"}
    },
    "debate": {
        "description": "Structured debate with positions",
        "supports_moderator": True,
        "configurable_options": ["rounds", "allow_rebuttals", "debate_style", "moderator_role"],
        "example_config": {"rounds": 3, "allow_rebuttals": True, "debate_style": "oxford"}
    },
    "panel": {
        "description": "Panel discussion with expert perspectives",
        "supports_moderator": True,
        "configurable_options": ["panel_style", "consensus_required", "voting_enabled", "moderator_questions"],
        "example_config": {"panel_style": "expert", "consensus_required": False, "voting_enabled": True}
    }
}


@router.get("/process-types", response_model=List[ProcessType])
async def list_process_types() -> List[ProcessType]:
    """List available process types."""
    process_types = []
    
    for name in ProcessFactory.list_types():
        info = PROCESS_TYPES.get(name, {})
        process_types.append(ProcessType(
            name=name,
            description=info.get("description", f"{name.title()} process"),
            supports_moderator=info.get("supports_moderator", False),
            configurable_options=info.get("configurable_options", []),
            example_config=info.get("example_config", {})
        ))
    
    return process_types


@router.get("/process-types/{process_name}", response_model=ProcessType)
async def get_process_type(process_name: str) -> ProcessType:
    """Get details about a specific process type."""
    if process_name not in ProcessFactory.list_types():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process type '{process_name}' not found"
        )
    
    info = PROCESS_TYPES.get(process_name, {})
    return ProcessType(
        name=process_name,
        description=info.get("description", f"{process_name.title()} process"),
        supports_moderator=info.get("supports_moderator", False),
        configurable_options=info.get("configurable_options", []),
        example_config=info.get("example_config", {})
    )


@router.put("/crews/{crew_id}/process", response_model=CrewResponse)
async def switch_crew_process(crew_id: str, process_switch: ProcessSwitch) -> CrewResponse:
    """Switch crew's process type."""
    storage = get_storage()
    crew_info = await storage.get_crew(crew_id)
    
    if not crew_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crew {crew_id} not found"
        )
    
    # Validate process type
    if process_switch.process_type not in ProcessFactory.list_types():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid process type: {process_switch.process_type}"
        )
    
    # Get crew instance
    crew_instance = crew_info.get("crew_instance")
    if not crew_instance:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Crew instance not found in storage"
        )
    
    # Switch process with WebSocket callbacks
    try:
        process_config = create_process_config_with_websocket(
            crew_id,
            process_switch.process_config
        )
        
        crew_instance.switch_process(
            process_switch.process_type,
            process_config
        )
        
        # Update storage
        crew_info["process"] = process_switch.process_type
        crew_info["process_config"] = process_switch.process_config
        await storage.store_crew(crew_id, crew_info)
        
        return CrewResponse(
            crew_id=crew_id,
            name=crew_info["name"],
            description=crew_info.get("description"),
            agents=crew_info["agents"],
            tasks=crew_info["tasks"],
            process=process_switch.process_type,
            process_config=process_switch.process_config,
            created_at=crew_info["created_at"],
            updated_at=crew_info.get("updated_at")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to switch process: {str(e)}"
        )


# Add visualization endpoints
add_visualization_endpoints(router)