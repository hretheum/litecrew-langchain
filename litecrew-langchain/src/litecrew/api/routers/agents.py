"""Agent management API endpoints."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status

from litecrew.agent import Agent
from litecrew.agent_types import AgentTypeFactory

from ..models import AgentCreate, AgentResponse, AgentTypeInfo
from ..storage import get_storage

router = APIRouter()


@router.get("/agents/types", response_model=List[str])
async def list_agent_types() -> List[str]:
    """List all available agent types."""
    return AgentTypeFactory.list_types()


@router.get("/agents/types/{type_name}", response_model=AgentTypeInfo)
async def get_agent_type_info(type_name: str) -> AgentTypeInfo:
    """Get detailed information about a specific agent type."""
    try:
        info = AgentTypeFactory.get_type_info(type_name)
        return AgentTypeInfo(**info)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(agent_data: AgentCreate) -> AgentResponse:
    """Create a new agent with optional type."""
    agent_id = str(uuid.uuid4())
    
    try:
        # Create agent with type if specified
        agent_kwargs = {
            "role": agent_data.role,
            "goal": agent_data.goal,
            "backstory": agent_data.backstory,
            "memory": agent_data.memory,
            "verbose": agent_data.verbose,
            "max_iter": agent_data.max_iter,
        }
        
        # Add type fields if specified
        if agent_data.type:
            agent_kwargs["type"] = agent_data.type
            agent_kwargs["type_config"] = agent_data.type_config
        
        # Add LLM configuration if specified
        if agent_data.llm_provider:
            agent_kwargs["llm_provider"] = agent_data.llm_provider
            agent_kwargs["llm_config"] = agent_data.llm_config
        
        # Add rate limiting if specified
        if agent_data.max_rpm:
            agent_kwargs["max_rpm"] = agent_data.max_rpm
        
        # Add streaming if specified
        agent_kwargs["streaming"] = agent_data.streaming
        
        # Create the agent
        agent = Agent(**agent_kwargs)
        
        # Get type info if agent has a type
        type_info = None
        if agent.type:
            type_info_dict = agent.get_type_info()
            type_info = AgentTypeInfo(
                name=type_info_dict["name"],
                description=type_info_dict["description"],
                configurable_options=type_info_dict.get("configurable_options", []),
                default_config=type_info_dict.get("default_config", {}),
                personality=type_info_dict.get("personality")
            )
        
        # Store agent data
        storage = get_storage()
        agent_doc = {
            "agent_id": agent_id,
            "role": agent.role,
            "goal": agent.goal,
            "backstory": agent.backstory,
            "tools": [tool.name if hasattr(tool, 'name') else str(tool) for tool in agent.tools],
            "memory": agent._memory_enabled,
            "verbose": agent.verbose,
            "max_iter": agent.max_iter,
            "type": agent.type,
            "type_config": agent.type_config,
            "created_at": datetime.utcnow().isoformat(),
            "metrics": agent.get_metrics()
        }
        storage.store_agent_sync(agent_id, agent_doc)
        
        return AgentResponse(
            agent_id=agent_id,
            role=agent.role,
            goal=agent.goal,
            backstory=agent.backstory,
            tools=agent_doc["tools"],
            memory=agent._memory_enabled,
            verbose=agent.verbose,
            max_iter=agent.max_iter,
            type=agent.type,
            type_config=agent.type_config,
            type_info=type_info,
            created_at=agent_doc["created_at"],
            metrics=agent_doc["metrics"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str) -> AgentResponse:
    """Get agent by ID."""
    storage = get_storage()
    agent_doc = storage.get_agent_sync(agent_id)
    
    if not agent_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    # Get type info if agent has a type
    type_info = None
    if agent_doc.get("type"):
        try:
            info = AgentTypeFactory.get_type_info(agent_doc["type"])
            type_info = AgentTypeInfo(
                name=info["name"],
                description=info["description"],
                configurable_options=info.get("configurable_options", []),
                default_config=info.get("default_config", {}),
                personality=info.get("personality")
            )
        except:
            pass  # Type might no longer exist
    
    return AgentResponse(
        agent_id=agent_doc["agent_id"],
        role=agent_doc["role"],
        goal=agent_doc["goal"],
        backstory=agent_doc["backstory"],
        tools=agent_doc.get("tools", []),
        memory=agent_doc.get("memory", True),
        verbose=agent_doc.get("verbose", False),
        max_iter=agent_doc.get("max_iter", 5),
        type=agent_doc.get("type"),
        type_config=agent_doc.get("type_config"),
        type_info=type_info,
        created_at=agent_doc["created_at"],
        metrics=agent_doc.get("metrics")
    )


@router.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[AgentResponse]:
    """List all agents with optional filtering by type."""
    storage = get_storage()
    agents = storage.list_agents_sync(limit=limit, offset=offset)
    
    # Filter by type if specified
    if type:
        agents = [a for a in agents if a.get("type") == type]
    
    responses = []
    for agent_doc in agents:
        # Get type info if agent has a type
        type_info = None
        if agent_doc.get("type"):
            try:
                info = AgentTypeFactory.get_type_info(agent_doc["type"])
                type_info = AgentTypeInfo(
                    name=info["name"],
                    description=info["description"],
                    configurable_options=info.get("configurable_options", []),
                    default_config=info.get("default_config", {}),
                    personality=info.get("personality")
                )
            except:
                pass  # Type might no longer exist
        
        responses.append(AgentResponse(
            agent_id=agent_doc["agent_id"],
            role=agent_doc["role"],
            goal=agent_doc["goal"],
            backstory=agent_doc["backstory"],
            tools=agent_doc.get("tools", []),
            memory=agent_doc.get("memory", True),
            verbose=agent_doc.get("verbose", False),
            max_iter=agent_doc.get("max_iter", 5),
            type=agent_doc.get("type"),
            type_config=agent_doc.get("type_config"),
            type_info=type_info,
            created_at=agent_doc["created_at"],
            metrics=agent_doc.get("metrics")
        ))
    
    return responses


@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str) -> None:
    """Delete an agent."""
    storage = get_storage()
    
    if not storage.get_agent_sync(agent_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    storage.delete_agent_sync(agent_id)


@router.post("/agents/{agent_id}/validate-type")
async def validate_agent_type(agent_id: str) -> Dict[str, Any]:
    """Validate an agent's type configuration."""
    storage = get_storage()
    agent_doc = storage.get_agent_sync(agent_id)
    
    if not agent_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    if not agent_doc.get("type"):
        return {"valid": True, "message": "Agent has no type configured"}
    
    try:
        # Recreate agent to validate
        agent = Agent(
            role=agent_doc["role"],
            goal=agent_doc["goal"],
            backstory=agent_doc["backstory"],
            type=agent_doc["type"],
            type_config=agent_doc.get("type_config")
        )
        
        is_valid = agent.validate_type_config()
        
        return {
            "valid": is_valid,
            "type": agent_doc["type"],
            "type_config": agent_doc.get("type_config"),
            "message": "Type configuration is valid" if is_valid else "Type configuration is invalid"
        }
        
    except Exception as e:
        return {
            "valid": False,
            "type": agent_doc["type"],
            "type_config": agent_doc.get("type_config"),
            "message": f"Validation error: {str(e)}"
        }