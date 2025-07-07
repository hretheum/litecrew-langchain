"""API routes for process templates."""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from ..models import CrewCreate, CrewResponse, QuickStartRequest, TemplateInfo
from ..storage import get_storage
from ..templates import get_template, list_templates

router = APIRouter()


@router.get("/process-templates", response_model=List[TemplateInfo])
async def get_process_templates() -> List[TemplateInfo]:
    """Get all available process templates."""
    templates = list_templates()
    return [TemplateInfo(**t) for t in templates]


@router.get("/process-templates/{template_name}", response_model=TemplateInfo)
async def get_process_template(template_name: str) -> TemplateInfo:
    """Get details of a specific process template."""
    try:
        template = get_template(template_name)
        return TemplateInfo(
            name=template.name,
            description=template.description,
            process_type=template.process_type,
            estimated_time=template.estimated_time(),
            default_inputs=template.get_default_inputs(),
            configurable_options={
                "topic": "string",
                "decision": "string",
                "options": "list[string]",
                "rounds": "integer",
                "require_consensus": "boolean",
                "min_turns": "integer",
                "max_turns": "integer",
                "language": "string",
                "code": "string",
                "aspects": "list[string]",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/crews/quick-start", response_model=Dict[str, Any])
async def quick_start_crew(request: QuickStartRequest) -> Dict[str, Any]:
    """Create and start a crew from a template."""
    try:
        # Get the template
        process_template = get_template(request.template)
        
        # Build kwargs from request
        kwargs = request.dict(exclude={"template", "auto_execute"}, exclude_none=True)
        
        # Generate configuration from template
        agents = process_template.generate_agents(**kwargs)
        tasks = process_template.generate_tasks(**kwargs)
        process_config = process_template.get_process_config(**kwargs)
        
        # Create crew data
        crew_data = CrewCreate(
            name=f"{process_template.name} - {kwargs.get('topic', kwargs.get('decision', 'Session'))}",
            description=process_template.description,
            agents=agents,
            tasks=tasks,
            process=process_template.process_type,
            process_config=process_config,
        )
        
        # Create the crew using the same logic as crews router
        from .crews import create_crew as create_crew_endpoint
        
        crew_response = await create_crew_endpoint(crew_data)
        
        # Auto-execute if requested
        execution_info = {}
        if request.auto_execute:
            from .crews import execute_crew
            
            execution_data = {"inputs": {}, "async_execution": True}
            execution = await execute_crew(crew_response.crew_id, execution_data)
            execution_info = {
                "execution_id": execution["execution_id"],
                "execution_status": execution["status"],
            }
        
        # Return response with additional info
        return {
            "crew_id": crew_response.crew_id,
            "name": crew_response.name,
            "template": request.template,
            "estimated_time": process_template.estimated_time(),
            "status": "executing" if request.auto_execute else "created",
            "message": f"Crew created from '{request.template}' template. {'Execution started.' if request.auto_execute else f'Use /api/v1/crews/{crew_response.crew_id}/execute to start.'}",
            "execute_url": f"/api/v1/crews/{crew_response.crew_id}/execute",
            **execution_info,
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create crew: {str(e)}")


@router.post("/crews/quick-start/{template_name}", response_model=Dict[str, Any])
async def quick_start_specific_template(
    template_name: str, inputs: Dict[str, Any]
) -> Dict[str, Any]:
    """Create and start a crew from a specific template with inputs."""
    request = QuickStartRequest(template=template_name, **inputs)
    return await quick_start_crew(request)