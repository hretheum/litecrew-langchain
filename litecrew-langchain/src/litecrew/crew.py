"""
LiteCrew - Multi-agent orchestration
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from litecrew.agent import LiteAgent
from litecrew.task import LiteTask, TaskOutput
from litecrew.memory import ConversationMemory
from litecrew.state import StateManager, CrewState
from litecrew.events import EventEmitter, EventType, LifecycleCallbacks


class CrewOutput(BaseModel):
    """Output from crew execution."""
    raw: str = Field(description="Final output from the crew")
    tasks_output: List[TaskOutput] = Field(description="All task outputs")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        return self.raw


class LiteCrew:
    """
    Lightweight crew orchestration for multi-agent systems.
    
    Compatible with CrewAI Crew API but built on LangChain.
    """
    
    def __init__(
        self,
        agents: List[LiteAgent],
        tasks: List[LiteTask],
        process: str = "sequential",
        manager_agent: Optional[LiteAgent] = None,
        verbose: bool = False,
        max_rpm: Optional[int] = None,
        memory: bool = False,
        cache: bool = True,
        function_calling_llm: Optional[Any] = None,
        step_callback: Optional[Any] = None,
        async_execution: bool = False,
        state_manager: Optional[StateManager] = None,
        event_emitter: Optional[EventEmitter] = None,
        lifecycle_callbacks: Optional[LifecycleCallbacks] = None,
    ):
        """
        Initialize a crew of agents.
        
        Args:
            agents: List of agents in the crew
            tasks: List of tasks to execute
            process: Execution process - "sequential" or "hierarchical"
            manager_agent: Manager agent for hierarchical process
            verbose: Enable verbose output
            max_rpm: Maximum requests per minute limit
            memory: Enable crew memory
            cache: Enable caching
            function_calling_llm: LLM for function calling
            step_callback: Callback after each step
            async_execution: Whether to execute tasks asynchronously
            state_manager: Optional state manager for snapshots
        """
        self.agents = agents
        self.tasks = tasks
        self.process = process
        self.manager_agent = manager_agent
        self.verbose = verbose
        self.max_rpm = max_rpm
        self.memory = memory
        self.cache = cache
        self.function_calling_llm = function_calling_llm
        self.step_callback = step_callback
        self.async_execution = async_execution
        
        # Generate unique crew ID
        self.id = f"crew_{uuid.uuid4().hex[:8]}"
        
        # Setup state management
        self._state_manager = state_manager
        self._state: Optional[CrewState] = None
        
        # Validate setup
        self._validate_setup()
        
        # Assign tasks to agents if not already assigned
        self._auto_assign_tasks()
        
        # Add delegation tools if multiple agents
        if len(self.agents) > 1:
            self._setup_delegation()
        
        # Setup shared memory if enabled
        if self.memory:
            self._setup_shared_memory()
        
        # Event system
        self.event_emitter = event_emitter
        self.lifecycle_callbacks = lifecycle_callbacks
        
        # Share event emitter with agents
        if self.event_emitter:
            for agent in self.agents:
                if not agent.event_emitter:
                    agent.event_emitter = self.event_emitter
            
    def _validate_setup(self):
        """Validate crew configuration."""
        if not self.agents:
            raise ValueError("Crew must have at least one agent")
            
        if not self.tasks:
            raise ValueError("Crew must have at least one task")
            
        if self.process == "hierarchical" and not self.manager_agent:
            # Create default manager
            self.manager_agent = LiteAgent(
                role="Crew Manager",
                goal="Coordinate agents to complete tasks efficiently",
                backstory="Experienced project manager skilled at delegation"
            )
            
    def _auto_assign_tasks(self):
        """Auto-assign tasks to agents if not assigned."""
        unassigned_tasks = [task for task in self.tasks if not task.agent]
        
        if unassigned_tasks and self.agents:
            # Simple round-robin assignment
            for i, task in enumerate(unassigned_tasks):
                task.agent = self.agents[i % len(self.agents)]
                
    def _setup_delegation(self):
        """Setup delegation tools for agents."""
        from litecrew.tools import DelegationTool
        
        delegation_tool = DelegationTool(self.agents)
        
        for agent in self.agents:
            if agent.allow_delegation:
                agent.tools.append(delegation_tool)
    
    def _setup_shared_memory(self):
        """Setup shared memory for crew."""
        self._shared_memory = ConversationMemory()
        
        # Configure agents to use shared memory
        for agent in self.agents:
            if hasattr(agent, '_use_crew_memory'):
                agent._use_crew_memory = True
            # Share the memory reference
            if hasattr(agent, '_conversation_memory'):
                agent._conversation_memory = self._shared_memory
        
        # Manager also uses shared memory
        if self.manager_agent and hasattr(self.manager_agent, '_conversation_memory'):
            self.manager_agent._conversation_memory = self._shared_memory
            self.manager_agent._use_crew_memory = True
    
    def get_memory_context(self) -> str:
        """Get shared memory context."""
        if hasattr(self, '_shared_memory'):
            return self._shared_memory.build_context()
        return ""
                
    def kickoff(self, inputs: Optional[Dict[str, Any]] = None) -> CrewOutput:
        """
        Execute the crew tasks.
        
        Args:
            inputs: Optional input variables for tasks
            
        Returns:
            CrewOutput with results
        """
        if self.verbose:
            print(f"Starting crew execution with {len(self.tasks)} tasks...")
        
        # Emit crew started event
        if self.event_emitter:
            self.event_emitter.emit(
                EventType.CREW_STARTED,
                {"crew_id": self.id, "tasks": len(self.tasks), "agents": len(self.agents)},
                source=self.id
            )
        
        # Trigger lifecycle callback
        if self.lifecycle_callbacks:
            self.lifecycle_callbacks.trigger('crew_start', self)
        
        # Initialize state if state manager is available
        if self._state_manager:
            self._state = CrewState.from_crew(
                crew_id=self.id,
                agents=self.agents,
                tasks=self.tasks,
                process=self.process
            )
            self._state.update_status("running")
            self._save_state()
            
        # Execute based on process type
        try:
            if self.process == "sequential":
                result = self._execute_sequential(inputs)
            elif self.process == "hierarchical":
                result = self._execute_hierarchical(inputs)
            else:
                raise ValueError(f"Unknown process type: {self.process}")
            
            # Update final state
            if self._state:
                self._state.update_status("completed")
                self._save_state()
                
            return result
            
        except Exception as e:
            # Update state on failure
            if self._state:
                self._state.update_status("failed")
                self._state.metadata["error"] = str(e)
                self._save_state()
            raise
            
    def _execute_sequential(self, inputs: Optional[Dict[str, Any]] = None) -> CrewOutput:
        """Execute tasks sequentially."""
        outputs = []
        
        for i, task in enumerate(self.tasks):
            if self.verbose:
                print(f"\nExecuting task {i+1}/{len(self.tasks)}: {task.description[:50]}...")
            
            # Update state
            if self._state:
                self._state.current_task_index = i
                self._state.update_task_status(i, "in_progress")
                self._save_state()
                
            # Execute task
            try:
                output = task.execute(crew_context=inputs)
                outputs.append(output)
                
                # Update state with output
                if self._state:
                    self._state.update_task_status(i, "completed")
                    self._state.update_task_output(i, output.raw)
                    self._save_state()
                
                # Emit task completed event
                if self.event_emitter:
                    self.event_emitter.emit(
                        EventType.TASK_COMPLETED,
                        {"task_index": i, "task": task.description, "output": str(output)},
                        source=self.id
                    )
                
                # Trigger lifecycle callback
                if self.lifecycle_callbacks:
                    self.lifecycle_callbacks.trigger('crew_task_complete', {"task": task, "output": output})
                
                # Callback if provided
                if self.step_callback:
                    self.step_callback(task, output)
                    
            except Exception as e:
                if self.verbose:
                    print(f"Task failed: {e}")
                
                # Update state with error
                if self._state:
                    self._state.update_task_error(i, str(e))
                    self._save_state()
                    
                raise
                
        # Return final output
        return CrewOutput(
            raw=outputs[-1].raw if outputs else "",
            tasks_output=outputs
        )
        
    def _execute_hierarchical(self, inputs: Optional[Dict[str, Any]] = None) -> CrewOutput:
        """Execute tasks using hierarchical process with manager."""
        if not self.manager_agent:
            raise ValueError("Manager agent required for hierarchical process")
            
        outputs = []
        
        # Manager creates execution plan
        plan_prompt = f"""You are managing a team to complete these tasks:
{chr(10).join(f"- {task.description}" for task in self.tasks)}

Available agents:
{chr(10).join(f"- {agent.role}: {agent.goal}" for agent in self.agents)}

Create an execution plan assigning each task to the most suitable agent.
Respond with task assignments in format: "Task N -> Agent Role"
"""
        
        plan = self.manager_agent.execute(plan_prompt)
        
        if self.verbose:
            print(f"Manager's plan:\n{plan}")
            
        # Execute tasks based on manager's coordination
        for task in self.tasks:
            # Manager delegates
            delegation_prompt = f"""Based on your plan, which agent should handle this task?
Task: {task.description}
Respond with just the agent's role."""
            
            assigned_role = self.manager_agent.execute(delegation_prompt).strip()
            
            # Find matching agent
            assigned_agent = next(
                (agent for agent in self.agents if agent.role.lower() in assigned_role.lower()),
                task.agent or self.agents[0]
            )
            
            # Update task assignment
            task.agent = assigned_agent
            
            if self.verbose:
                print(f"\nManager assigned task to {assigned_agent.role}")
                
            # Execute task
            output = task.execute(crew_context=inputs)
            outputs.append(output)
            
            # Update manager on progress
            progress_update = f"Task completed by {assigned_agent.role}: {output.raw[:100]}..."
            self.manager_agent.execute(f"Note this progress: {progress_update}")
            
        return CrewOutput(
            raw=outputs[-1].raw if outputs else "",
            tasks_output=outputs
        )
        
    async def akickoff(self, inputs: Optional[Dict[str, Any]] = None) -> CrewOutput:
        """Execute crew asynchronously."""
        if self.async_execution:
            # Execute tasks concurrently when possible
            if self.process == "sequential":
                return await self._aexecute_sequential(inputs)
            else:
                return await self._aexecute_hierarchical(inputs)
        else:
            # Fallback to sync execution in thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                return await loop.run_in_executor(executor, self.kickoff, inputs)
    
    async def _aexecute_sequential(self, inputs: Optional[Dict[str, Any]] = None) -> CrewOutput:
        """Execute tasks sequentially using async."""
        outputs = []
        
        for i, task in enumerate(self.tasks):
            if self.verbose:
                print(f"\n\n> Executing task {i+1}/{len(self.tasks)}: {task.description}")
            
            # Execute task asynchronously
            if hasattr(task.agent, 'aexecute'):
                output_text = await task.agent.aexecute(task.description, "\n".join([o.raw for o in outputs]))
            else:
                # Fallback to sync execution
                loop = asyncio.get_event_loop()
                output_text = await loop.run_in_executor(None, task.execute, inputs)
            
            output = TaskOutput(
                raw=output_text if isinstance(output_text, str) else output_text.raw,
                agent=task.agent.role,
                task=task.description
            )
            outputs.append(output)
            
            if self.step_callback:
                self.step_callback(task, output)
        
        return CrewOutput(
            raw=outputs[-1].raw if outputs else "",
            tasks_output=outputs
        )
    
    async def _aexecute_hierarchical(self, inputs: Optional[Dict[str, Any]] = None) -> CrewOutput:
        """Execute tasks hierarchically using async."""
        # For now, fall back to sync execution
        # TODO: Implement proper async hierarchical execution
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._execute_hierarchical, inputs)
    
    # Legacy alias for backward compatibility
    async def kickoff_async(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Legacy async method - use akickoff instead."""
        crew_output = await self.akickoff(inputs)
        return {
            "result": crew_output.raw,
            "tasks_output": [{"raw": output.raw, "agent": getattr(output, 'agent_role', 'unknown'), "task": getattr(output, 'task_id', 'unknown')} for output in crew_output.tasks_output],
            "timestamp": crew_output.timestamp.isoformat()
        }
            
    def _save_state(self) -> None:
        """Save current state if state manager is available."""
        if self._state_manager and self._state:
            # Check if auto-snapshot is needed
            if self._state_manager.should_auto_snapshot(self.id):
                self._state_manager.save_state(self._state)
            else:
                # Save incremental update
                self._state_manager.save_incremental_update(
                    self._state,
                    changed_fields=["task_states", "current_task_index", "status", "updated_at"]
                )
    
    def save_state_snapshot(self) -> Optional[str]:
        """Manually save a state snapshot."""
        if self._state_manager and self._state:
            return self._state_manager.save_state(self._state)
        return None
    
    def restore_state(self, version: Optional[int] = None) -> None:
        """Restore crew state from a snapshot."""
        if self._state_manager:
            restored_state = self._state_manager.load_state(self.id, version)
            if restored_state:
                self._state = restored_state
                # TODO: Restore task outputs and crew state
    
    def get_state_history(self) -> List[Dict[str, Any]]:
        """Get state history."""
        if self._state_manager:
            return self._state_manager.get_state_history(self.id)
        return []
    
    def __repr__(self) -> str:
        return f"LiteCrew(agents={len(self.agents)}, tasks={len(self.tasks)}, process={self.process})"


# Alias for CrewAI compatibility
Crew = LiteCrew