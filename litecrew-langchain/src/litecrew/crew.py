"""
LiteCrew - Orchestration engine for multi-agent systems
"""

import time
from enum import Enum
from typing import List, Optional, Dict, Any, Union, Callable
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from litecrew.agent import LiteAgent
from litecrew.task import LiteTask, TaskOutput
# Lazy imports for context management
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from litecrew.context import SharedContextStore, ContextConfig, ContextMerger, ContextMergeStrategy


class ProcessType(str, Enum):
    """Types of crew execution processes."""
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"


class CrewOutput(BaseModel):
    """Output from crew execution."""
    raw: str = Field(description="Raw output from the crew")
    tasks_output: List[TaskOutput] = Field(description="Individual task outputs")
    token_usage: Dict[str, Any] = Field(default_factory=dict, description="Token usage metrics")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        return self.raw


class LiteCrew(BaseModel):
    """
    Orchestration engine for managing multiple agents and tasks.
    
    Compatible with CrewAI API but optimized for performance.
    """
    agents: List[LiteAgent] = Field(description="List of agents in the crew")
    tasks: List[LiteTask] = Field(description="List of tasks to execute")
    process: ProcessType = Field(default=ProcessType.SEQUENTIAL, description="Execution process type")
    verbose: bool = Field(default=False, description="Enable verbose output")
    manager_llm: Optional[Any] = Field(default=None, description="LLM for manager agent (hierarchical only)")
    memory: bool = Field(default=False, description="Enable shared memory")
    cache: bool = Field(default=True, description="Enable result caching")
    max_rpm: Optional[int] = Field(default=None, description="Max requests per minute")
    share_crew: bool = Field(default=False, description="Share crew on CrewAI Hub")
    manager_agent: Optional[LiteAgent] = Field(default=None, description="Manager agent for hierarchical process")
    function_calling_llm: Optional[Any] = Field(default=None, description="LLM for function calling")
    step_callback: Optional[Any] = Field(default=None, description="Callback after each step")
    
    # Context management
    shared_context: bool = Field(default=False, description="Enable shared context between agents")
    context_config: Optional[Any] = Field(default=None, description="Context management configuration")
    
    # Runtime state (not in Pydantic schema)
    _start_time: Optional[float] = None
    _usage_metrics: Dict[str, Any] = {}
    _progress_callback: Optional[Callable] = None
    
    model_config = {"arbitrary_types_allowed": True}
    
    def __init__(self, **data):
        """Initialize crew with validation."""
        super().__init__(**data)
        self._usage_metrics = {}
        self._start_time = None
        self._progress_callback = None
        
        # Validate setup
        self._validate_setup()
        
        # Auto-assign tasks to agents if needed
        self._auto_assign_tasks()
        
        # Setup delegation if needed
        if len(self.agents) > 1:
            self._setup_delegation()
        
        # Setup shared context if enabled
        self._setup_shared_context()
    
    @field_validator("process", mode="before")
    def validate_process(cls, v):
        """Validate and convert process type."""
        if isinstance(v, str):
            if v.lower() == "sequential":
                return ProcessType.SEQUENTIAL
            elif v.lower() == "hierarchical":
                return ProcessType.HIERARCHICAL
            else:
                raise ValueError(f"Invalid process type: {v}. Must be 'sequential' or 'hierarchical'")
        return v
    
    def _validate_setup(self):
        """Validate crew configuration."""
        if not self.agents:
            raise ValueError("Crew must have at least one agent")
            
        if not self.tasks:
            raise ValueError("Crew must have at least one task")
            
        # Ensure all tasks have agents
        for task in self.tasks:
            if task.agent is None and self.agents:
                task.agent = self.agents[0]
                
        if self.process == ProcessType.HIERARCHICAL and not self.manager_agent:
            # First agent becomes manager in hierarchical mode
            if self.agents:
                self.manager_agent = self.agents[0]
    
    def _auto_assign_tasks(self):
        """Auto-assign tasks to agents if not assigned."""
        unassigned_tasks = [task for task in self.tasks if not task.agent]
        
        if unassigned_tasks and self.agents:
            # Simple round-robin assignment
            for i, task in enumerate(unassigned_tasks):
                task.agent = self.agents[i % len(self.agents)]
                
    def _setup_delegation(self):
        """Setup delegation tools for agents with enhanced delegation system."""
        if len(self.agents) <= 1:
            return  # No delegation needed for single agent
        
        from .tools import DelegationTool
        from .delegation import DelegationManager, DelegationValidator
        
        # Create delegation validator with crew-level constraints
        validator = DelegationValidator(
            max_depth=3,  # Allow 3 levels of delegation
            allowed_agents=[agent.role for agent in self.agents],
            prevent_cycles=True
        )
        
        # Create shared delegation manager for the crew
        delegation_manager = DelegationManager(
            available_agents={agent.role: agent for agent in self.agents},
            validator=validator
        )
        
        # Add delegation tool to each agent that allows delegation
        for agent in self.agents:
            if agent.allow_delegation:
                # Create delegation tool for this agent
                delegation_tool = DelegationTool(
                    agents=self.agents,
                    delegation_manager=delegation_manager
                )
                
                # Set current agent context
                delegation_tool.set_current_agent(agent)
                
                # Add tool to agent's tools list
                if hasattr(agent, 'tools') and agent.tools:
                    agent.tools.append(delegation_tool)
                else:
                    agent.tools = [delegation_tool]
        
        # Store delegation manager for crew-level access (private to avoid Pydantic issues)
        self._delegation_manager = delegation_manager
    
    def _setup_shared_context(self):
        """Setup shared context management for the crew."""
        if not self.shared_context:
            return
        
        # Lazy import context components
        from litecrew.context import SharedContextStore, ContextConfig, ContextMerger
        
        # Create context configuration
        if self.context_config is None:
            self.context_config = ContextConfig()
        
        # Initialize shared context store
        self._shared_context_store = SharedContextStore(config=self.context_config)
        
        # Initialize context merger
        self._context_merger = ContextMerger()
    
    def kickoff(self, inputs: Optional[Dict[str, Any]] = None) -> CrewOutput:
        """
        Execute the crew's tasks according to the process type.
        
        Args:
            inputs: Optional inputs to pass to tasks
            
        Returns:
            CrewOutput with results
        """
        self._start_time = time.perf_counter()
        self._usage_metrics = {
            "task_count": len(self.tasks),
            "agent_count": len(self.agents),
            "process": self.process.value
        }
        
        if self.verbose:
            print(f"\n[Crew] Starting {self.process.value} execution with {len(self.tasks)} tasks")
        
        try:
            if self.process == ProcessType.SEQUENTIAL:
                output = self._run_sequential(inputs)
            elif self.process == ProcessType.HIERARCHICAL:
                output = self._run_hierarchical(inputs)
            else:
                raise ValueError(f"Unknown process type: {self.process}")
                
            # Record metrics
            self._usage_metrics["total_time"] = time.perf_counter() - self._start_time
            self._usage_metrics["success"] = True
            
            return output
            
        except Exception as e:
            self._usage_metrics["total_time"] = time.perf_counter() - self._start_time
            self._usage_metrics["success"] = False
            self._usage_metrics["error"] = str(e)
            raise
    
    def _run_sequential(self, inputs: Optional[Dict[str, Any]] = None) -> CrewOutput:
        """Run tasks sequentially."""
        task_outputs = []
        crew_context = inputs or {}
        
        for i, task in enumerate(self.tasks):
            if self.verbose:
                print(f"\n[Task {i+1}/{len(self.tasks)}] {task.description}")
            
            # Update progress
            if self._progress_callback:
                self._progress_callback({
                    "current_task": i + 1,
                    "total_tasks": len(self.tasks),
                    "task_description": task.description,
                    "progress": (i + 1) / len(self.tasks)
                })
            
            # Execute task with shared context support
            if hasattr(self, '_shared_context_store'):
                output = task.execute(
                    crew_context=crew_context,
                    shared_context=self._shared_context_store
                )
            else:
                output = task.execute(crew_context=crew_context)
            
            task_outputs.append(output)
            
            # Add output to context for next tasks
            crew_context[f"task_{i}_output"] = output.raw
            
            # Store in shared context if enabled
            if hasattr(self, '_shared_context_store'):
                from litecrew.context import ContextMetadata
                metadata = ContextMetadata(
                    agent_role=output.agent_role,
                    task_description=task.description,
                    priority=2,  # Medium priority for task outputs
                    ttl_seconds=self.context_config.ttl_seconds if self.context_config else 3600
                )
                self._shared_context_store.store_context(
                    key=f"task_{i}_output",
                    value=output.raw,
                    metadata=metadata
                )
            
            # Callback if provided
            if self.step_callback:
                self.step_callback(task, output)
            
            if self.verbose:
                print(f"[Task {i+1}] Output: {output.raw[:100]}...")
        
        # Compile final output
        final_output = self._compile_output(task_outputs)
        
        return CrewOutput(
            raw=final_output,
            tasks_output=task_outputs,
            token_usage=self._calculate_token_usage()
        )
    
    def _run_hierarchical(self, inputs: Optional[Dict[str, Any]] = None) -> CrewOutput:
        """Run tasks in hierarchical mode with manager coordinating."""
        if not self.agents:
            raise ValueError("Hierarchical process requires at least one agent")
            
        # Use manager_agent if set, otherwise first agent is manager
        manager = self.manager_agent or self.agents[0]
        workers = [a for a in self.agents if a != manager]
        
        task_outputs = []
        crew_context = inputs or {}
        
        if self.verbose:
            print(f"\n[Hierarchical] Manager: {manager.role}")
            print(f"[Hierarchical] Workers: {[w.role for w in workers]}")
        
        # Manager creates execution plan
        plan_prompt = f"""You are managing a team to complete these tasks:
{chr(10).join(f"- {task.description}" for task in self.tasks)}

Available agents:
{chr(10).join(f"- {agent.role}: {agent.goal}" for agent in self.agents)}

Create an execution plan assigning each task to the most suitable agent.
Respond with task assignments in format: "Task N -> Agent Role"
"""
        
        plan = manager.execute(plan_prompt)
        
        if self.verbose:
            print(f"Manager's plan:\n{plan}")
        
        # Execute tasks based on plan
        for i, task in enumerate(self.tasks):
            if self.verbose:
                print(f"\n[Manager] Delegating task {i+1}: {task.description}")
            
            # Execute task (manager coordinates but agents do the work)
            output = task.execute(crew_context=crew_context)
            task_outputs.append(output)
            crew_context[f"task_{i}_output"] = output.raw
            
            # Update manager on progress
            if self.verbose:
                progress_update = f"Task completed by {task.agent.role}: {output.raw[:100]}..."
                manager.execute(f"Note this progress: {progress_update}")
        
        # Manager reviews all outputs
        final_output = self._manager_review(manager, task_outputs, crew_context)
        
        return CrewOutput(
            raw=final_output,
            tasks_output=task_outputs,
            token_usage=self._calculate_token_usage()
        )
    
    def _manager_review(self, manager: LiteAgent, outputs: List[TaskOutput], context: Dict) -> str:
        """Manager reviews and summarizes all task outputs."""
        review_context = "Task outputs to review:\n\n"
        for i, output in enumerate(outputs):
            review_context += f"Task {i+1}: {output.raw}\n\n"
            
        review_task = "Review all task outputs and provide a final summary"
        
        if self.verbose:
            print(f"\n[Manager] Reviewing {len(outputs)} task outputs")
            
        summary = manager.execute(review_task, review_context)
        return summary
    
    def _compile_output(self, task_outputs: List[TaskOutput]) -> str:
        """Compile task outputs into final crew output."""
        if not task_outputs:
            return "No tasks completed"
            
        # Use last task output as final output by default
        # Can be customized for more sophisticated compilation
        return task_outputs[-1].raw
    
    def _calculate_token_usage(self) -> Dict[str, Any]:
        """Calculate token usage across all agents."""
        # TODO: Implement actual token counting
        return {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "successful_requests": len(self.tasks)
        }
    
    def get_delegation_metrics(self) -> Dict[str, Any]:
        """Get delegation metrics from the crew's delegation manager."""
        if hasattr(self, '_delegation_manager'):
            return self._delegation_manager.get_delegation_metrics()
        return {
            "total_delegations": 0,
            "successful_delegations": 0,
            "failed_delegations": 0,
            "average_execution_time": 0.0,
            "success_rate": 0.0
        }
    
    def get_delegation_history(self, limit: Optional[int] = None):
        """Get delegation history from the crew's delegation manager."""
        if hasattr(self, '_delegation_manager'):
            return self._delegation_manager.get_delegation_history(limit)
        return []
    
    def get_shared_context_metrics(self) -> Dict[str, Any]:
        """Get shared context metrics from the crew's context store."""
        if hasattr(self, '_shared_context_store'):
            return self._shared_context_store.get_metrics()
        return {
            "total_items": 0,
            "total_size_bytes": 0,
            "access_count": 0,
            "current_size_mb": 0,
            "utilization_percent": 0
        }
    
    def get_shared_context_status(self) -> Dict[str, Any]:
        """Get detailed shared context status."""
        if hasattr(self, '_shared_context_store'):
            return self._shared_context_store.get_status()
        return {"shared_context": False}
    
    def get_agent_context(self, agent_role: str, max_items: int = 5) -> str:
        """Get formatted context for a specific agent."""
        if hasattr(self, '_shared_context_store'):
            return self._shared_context_store.get_agent_context(agent_role, max_items)
        return ""
    
    def clear_agent_context(self, agent_role: str):
        """Clear all context for a specific agent."""
        if hasattr(self, '_shared_context_store'):
            self._shared_context_store.clear_agent_context(agent_role)
    
    def clear_shared_context(self):
        """Clear all shared context data."""
        if hasattr(self, '_shared_context_store'):
            self._shared_context_store.clear_all()
    
    async def kickoff_async(self, inputs: Optional[Dict[str, Any]] = None) -> CrewOutput:
        """Execute crew asynchronously."""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.kickoff, inputs)
    
    @property
    def usage_metrics(self) -> Dict[str, Any]:
        """Get usage metrics from last execution."""
        return self._usage_metrics
    
    @property
    def on_progress(self) -> Optional[Callable]:
        """Get progress callback."""
        return self._progress_callback
    
    @on_progress.setter
    def on_progress(self, callback: Callable):
        """Set progress callback."""
        self._progress_callback = callback
    
    def memory_usage(self) -> int:
        """Estimate memory usage in bytes."""
        # Simple estimation based on agent and task count
        base_memory = 1024 * 1024  # 1MB base
        per_agent = 100 * 1024     # 100KB per agent
        per_task = 50 * 1024       # 50KB per task
        
        return base_memory + (len(self.agents) * per_agent) + (len(self.tasks) * per_task)
    
    def __str__(self) -> str:
        return f"Crew(agents={len(self.agents)}, tasks={len(self.tasks)}, process={self.process.value})"
    
    def __repr__(self) -> str:
        return f"LiteCrew(agents={[a.role for a in self.agents]}, task_count={len(self.tasks)})"


# Alias for CrewAI compatibility
Crew = LiteCrew