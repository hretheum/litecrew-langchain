"""Process visualization helpers for dashboard display."""

from typing import Any, Dict, List, Optional
from datetime import datetime

from litecrew.processes import ProcessResult, ProcessTurn


class ProcessVisualizer:
    """Helper class for visualizing process execution."""
    
    @staticmethod
    def format_process_result(result: ProcessResult) -> Dict[str, Any]:
        """Format process result for visualization."""
        return {
            "success": result.success,
            "duration": result.duration,
            "error": result.error,
            "metadata": result.metadata,
            "turns": [
                ProcessVisualizer.format_turn(turn) 
                for turn in result.turns
            ],
            "tasks_completed": len(result.tasks_output),
            "summary": result.raw[:500] if result.raw else ""
        }
    
    @staticmethod
    def format_turn(turn: ProcessTurn) -> Dict[str, Any]:
        """Format a single turn for visualization."""
        return {
            "agent": turn.agent,
            "content": turn.content[:200] + "..." if len(turn.content) > 200 else turn.content,
            "timestamp": turn.timestamp.isoformat(),
            "phase": turn.metadata.get("phase", "unknown"),
            "metadata": turn.metadata
        }
    
    @staticmethod
    def create_timeline(turns: List[ProcessTurn]) -> List[Dict[str, Any]]:
        """Create timeline visualization data."""
        timeline = []
        
        for i, turn in enumerate(turns):
            timeline.append({
                "id": i,
                "agent": turn.agent,
                "phase": turn.metadata.get("phase", "conversation"),
                "timestamp": turn.timestamp.isoformat(),
                "duration_from_start": (
                    turn.timestamp - turns[0].timestamp
                ).total_seconds() if turns else 0
            })
        
        return timeline
    
    @staticmethod
    def create_agent_stats(turns: List[ProcessTurn]) -> Dict[str, Dict[str, Any]]:
        """Create agent participation statistics."""
        stats = {}
        
        for turn in turns:
            agent = turn.agent
            if agent not in stats:
                stats[agent] = {
                    "turn_count": 0,
                    "phases": set(),
                    "first_turn": turn.timestamp,
                    "last_turn": turn.timestamp
                }
            
            stats[agent]["turn_count"] += 1
            stats[agent]["phases"].add(turn.metadata.get("phase", "unknown"))
            stats[agent]["last_turn"] = turn.timestamp
        
        # Convert sets to lists for JSON serialization
        for agent in stats:
            stats[agent]["phases"] = list(stats[agent]["phases"])
            stats[agent]["first_turn"] = stats[agent]["first_turn"].isoformat()
            stats[agent]["last_turn"] = stats[agent]["last_turn"].isoformat()
        
        return stats
    
    @staticmethod
    def create_process_flow(
        process_type: str, 
        turns: List[ProcessTurn]
    ) -> Dict[str, Any]:
        """Create process flow visualization data."""
        flow = {
            "process_type": process_type,
            "nodes": [],
            "edges": []
        }
        
        # Create nodes for each unique agent
        agents = list(set(turn.agent for turn in turns))
        for i, agent in enumerate(agents):
            flow["nodes"].append({
                "id": f"agent_{i}",
                "label": agent,
                "type": "agent"
            })
        
        # Create edges based on turn sequence
        for i in range(len(turns) - 1):
            from_agent = turns[i].agent
            to_agent = turns[i + 1].agent
            
            if from_agent != to_agent:  # Only show transitions between different agents
                from_idx = agents.index(from_agent)
                to_idx = agents.index(to_agent)
                
                edge = {
                    "from": f"agent_{from_idx}",
                    "to": f"agent_{to_idx}",
                    "label": turns[i + 1].metadata.get("phase", ""),
                    "timestamp": turns[i + 1].timestamp.isoformat()
                }
                
                # Avoid duplicate edges
                if edge not in flow["edges"]:
                    flow["edges"].append(edge)
        
        return flow
    
    @staticmethod
    def create_debate_visualization(turns: List[ProcessTurn]) -> Dict[str, Any]:
        """Create specialized visualization for debate process."""
        debate_data = {
            "rounds": {},
            "positions": {},
            "arguments_count": {}
        }
        
        for turn in turns:
            # Extract round information
            round_num = turn.metadata.get("round", 0)
            if round_num not in debate_data["rounds"]:
                debate_data["rounds"][round_num] = []
            
            debate_data["rounds"][round_num].append({
                "agent": turn.agent,
                "position": turn.metadata.get("position", "unknown"),
                "phase": turn.metadata.get("phase", ""),
                "summary": turn.content[:100] + "..."
            })
            
            # Track positions
            position = turn.metadata.get("position")
            if position:
                if position not in debate_data["positions"]:
                    debate_data["positions"][position] = []
                debate_data["positions"][position].append(turn.agent)
            
            # Count arguments
            agent = turn.agent
            debate_data["arguments_count"][agent] = debate_data["arguments_count"].get(agent, 0) + 1
        
        return debate_data
    
    @staticmethod
    def create_panel_visualization(turns: List[ProcessTurn]) -> Dict[str, Any]:
        """Create specialized visualization for panel process."""
        panel_data = {
            "moderator": None,
            "panelists": [],
            "topics": [],
            "consensus_reached": False,
            "votes": {}
        }
        
        for turn in turns:
            # Identify moderator
            if turn.metadata.get("role") == "moderator" and not panel_data["moderator"]:
                panel_data["moderator"] = turn.agent
            
            # Track topics
            if turn.metadata.get("phase") == "topic_introduction":
                panel_data["topics"].append({
                    "index": turn.metadata.get("task_index", 0),
                    "introduced_by": turn.agent,
                    "summary": turn.content[:100]
                })
            
            # Track panelists
            if turn.metadata.get("phase") == "expert_opinion" and turn.agent not in panel_data["panelists"]:
                panel_data["panelists"].append(turn.agent)
            
            # Check for consensus
            if turn.metadata.get("phase") == "consensus":
                panel_data["consensus_reached"] = True
            
            # Track votes
            if turn.metadata.get("votes"):
                panel_data["votes"] = turn.metadata["votes"]
        
        return panel_data


def add_visualization_endpoints(router: APIRouter) -> None:
    """Add visualization endpoints to a router."""
    
    @router.get("/crews/{crew_id}/visualization")
    async def get_crew_visualization(crew_id: str) -> Dict[str, Any]:
        """Get visualization data for crew execution."""
        from ..storage import get_storage
        
        storage = get_storage()
        crew_info = await storage.get_crew(crew_id)
        
        if not crew_info:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Crew not found")
        
        # Get latest execution result
        executions = await storage.get_crew_executions(crew_id)
        if not executions:
            return {"message": "No executions yet"}
        
        latest_execution = executions[-1]
        result = latest_execution.get("result")
        
        if not result:
            return {"message": "No result available"}
        
        # Create visualization data
        viz_data = {
            "crew_id": crew_id,
            "process_type": crew_info.get("process", "sequential"),
            "execution_id": latest_execution.get("execution_id"),
            "result": ProcessVisualizer.format_process_result(result),
            "timeline": ProcessVisualizer.create_timeline(result.turns),
            "agent_stats": ProcessVisualizer.create_agent_stats(result.turns),
            "process_flow": ProcessVisualizer.create_process_flow(
                crew_info.get("process", "sequential"),
                result.turns
            )
        }
        
        # Add process-specific visualizations
        if crew_info.get("process") == "debate":
            viz_data["debate_data"] = ProcessVisualizer.create_debate_visualization(result.turns)
        elif crew_info.get("process") == "panel":
            viz_data["panel_data"] = ProcessVisualizer.create_panel_visualization(result.turns)
        
        return viz_data