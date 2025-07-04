"""Crew management API endpoints."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import asyncio
from datetime import datetime

from litecrew import LiteAgent, LiteTask, LiteCrew
from ..models import CrewCreate, CrewResponse, CrewUpdate, TaskSubmission
from ..storage import APIStorage

router = APIRouter()
storage = APIStorage()


@router.post("/crews", response_model=CrewResponse, status_code=status.HTTP_201_CREATED)
async def create_crew(crew_data: CrewCreate) -> CrewResponse:
    """Create a new crew."""
    crew_id = str(uuid.uuid4())
    
    # Create agents
    agents = []
    for agent_data in crew_data.agents:
        agent = LiteAgent(
            role=agent_data["role"],
            goal=agent_data["goal"],
            backstory=agent_data["backstory"]
        )
        agents.append(agent)
    
    # Create tasks
    tasks = []
    for task_data in crew_data.tasks:
        # Find agent by role
        agent = next((a for a in agents if a.role == task_data.get("agent_role")), agents[0])
        
        task = LiteTask(
            description=task_data["description"],
            agent=agent,
            expected_output=task_data.get("expected_output", "Task result")
        )
        tasks.append(task)
    
    # Create crew
    crew = LiteCrew(
        agents=agents,
        tasks=tasks,
        process=crew_data.process or "sequential"
    )
    
    # Store crew
    crew_info = {
        "crew_id": crew_id,
        "name": crew_data.name,
        "description": crew_data.description,
        "agents": crew_data.agents,
        "tasks": crew_data.tasks,
        "process": crew_data.process or "sequential",
        "created_at": datetime.utcnow().isoformat(),
        "crew_instance": crew
    }
    
    await storage.store_crew(crew_id, crew_info)
    
    return CrewResponse(
        crew_id=crew_id,
        name=crew_data.name,
        description=crew_data.description,
        agents=crew_data.agents,
        tasks=crew_data.tasks,
        process=crew_data.process or "sequential",
        created_at=crew_info["created_at"]
    )


@router.get("/crews/{crew_id}", response_model=CrewResponse)
async def get_crew(crew_id: str) -> CrewResponse:
    """Get crew information."""
    crew_info = await storage.get_crew(crew_id)
    if not crew_info:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    return CrewResponse(**crew_info)


@router.get("/crews")
async def list_crews() -> Dict[str, List[CrewResponse]]:
    """List all crews."""
    crews = await storage.list_crews()
    crew_responses = [CrewResponse(**crew) for crew in crews]
    return {"crews": crew_responses}


@router.patch("/crews/{crew_id}", response_model=CrewResponse)
async def update_crew(crew_id: str, update_data: CrewUpdate) -> CrewResponse:
    """Update crew configuration."""
    crew_info = await storage.get_crew(crew_id)
    if not crew_info:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    # Update fields
    if update_data.name is not None:
        crew_info["name"] = update_data.name
    if update_data.description is not None:
        crew_info["description"] = update_data.description
    
    crew_info["updated_at"] = datetime.utcnow().isoformat()
    
    await storage.store_crew(crew_id, crew_info)
    
    return CrewResponse(**crew_info)


@router.delete("/crews/{crew_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crew(crew_id: str):
    """Delete a crew."""
    crew_info = await storage.get_crew(crew_id)
    if not crew_info:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    await storage.delete_crew(crew_id)
    return None


@router.post("/crews/{crew_id}/tasks", status_code=status.HTTP_202_ACCEPTED)
async def submit_task(crew_id: str, task_data: TaskSubmission) -> Dict[str, Any]:
    """Submit a task for execution."""
    crew_info = await storage.get_crew(crew_id)
    if not crew_info:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    task_id = str(uuid.uuid4())
    
    # Store task
    task_info = {
        "task_id": task_id,
        "crew_id": crew_id,
        "description": task_data.description,
        "expected_output": task_data.expected_output,
        "priority": task_data.priority or "medium",
        "status": "accepted",
        "created_at": datetime.utcnow().isoformat()
    }
    
    await storage.store_task(task_id, task_info)
    
    return {
        "task_id": task_id,
        "status": "accepted",
        "message": "Task submitted for execution"
    }


@router.post("/crews/{crew_id}/execute")
async def execute_crew(crew_id: str, execution_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a crew."""
    crew_info = await storage.get_crew(crew_id)
    if not crew_info:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    execution_id = str(uuid.uuid4())
    
    # Get crew instance
    crew = crew_info["crew_instance"]
    
    # Execute crew
    try:
        if execution_data.get("async_execution", False):
            # Async execution - return immediately
            asyncio.create_task(storage.execute_crew_async(execution_id, crew, execution_data))
            result = {"status": "running", "message": "Execution started"}
        else:
            # Sync execution
            result = await crew.kickoff_async(execution_data.get("inputs", {}))
        
        # Store execution
        execution_info = {
            "execution_id": execution_id,
            "crew_id": crew_id,
            "status": "completed" if not execution_data.get("async_execution") else "running",
            "result": result,
            "created_at": datetime.utcnow().isoformat()
        }
        
        await storage.store_execution(execution_id, execution_info)
        
        return {
            "execution_id": execution_id,
            "status": execution_info["status"],
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.get("/crews/{crew_id}/executions")
async def get_crew_executions(crew_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """Get execution history for a crew."""
    executions = await storage.get_crew_executions(crew_id)
    return {"executions": executions}