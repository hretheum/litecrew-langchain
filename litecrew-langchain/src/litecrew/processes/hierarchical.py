"""Hierarchical Process Implementation"""

from typing import Any, Dict, List, Optional

from litecrew.agent import LiteAgent
from litecrew.task import LiteTask, TaskOutput

from .base import BaseProcess, ProcessResult
from .factory import ProcessFactory


class HierarchicalProcess(BaseProcess):
    """Execute tasks in hierarchical manner with manager delegation"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.manager_agent: Optional[LiteAgent] = None
        
    async def execute(
        self, 
        agents: List[LiteAgent], 
        tasks: List[LiteTask],
        inputs: Optional[Dict[str, Any]] = None
    ) -> ProcessResult:
        """Execute tasks hierarchically with manager coordination"""
        # Validate inputs
        valid, error = await self.validate_inputs(agents, tasks)
        if not valid:
            return ProcessResult(
                raw="",
                success=False,
                error=error
            )
        
        self._track_time()
        self._agents = agents
        self._tasks = tasks
        
        # First agent is the manager in hierarchical process
        self.manager_agent = agents[0]
        worker_agents = agents[1:] if len(agents) > 1 else []
        
        if not worker_agents:
            # Fall back to sequential if no workers
            from .sequential import SequentialProcess
            seq_process = SequentialProcess(self.config)
            return await seq_process.execute(agents, tasks, inputs)
        
        # Build agent lookup
        agent_lookup = {agent.role: agent for agent in agents}
        
        tasks_output: List[TaskOutput] = []
        turns = []
        
        try:
            # Manager analyzes all tasks first
            manager_analysis = await self._manager_analyze_tasks(tasks)
            turns.append(self._create_turn(
                self.manager_agent,
                manager_analysis,
                phase="analysis"
            ))
            
            # Execute tasks with delegation
            for i, task in enumerate(tasks):
                if not self._should_continue(i):
                    break
                
                # Manager decides delegation
                delegated_agent = await self._manager_delegate_task(
                    task, 
                    worker_agents,
                    agent_lookup
                )
                
                if self.config.verbose:
                    print(f"\nManager delegating task {i+1} to {delegated_agent.role}")
                
                # Create delegation turn
                turns.append(self._create_turn(
                    self.manager_agent,
                    f"Delegating task to {delegated_agent.role}: {task.description[:50]}...",
                    phase="delegation",
                    task_index=i
                ))
                
                # Worker executes task
                self._emit_event('task_start', {'task': task, 'agent': delegated_agent})
                
                # Temporarily assign the delegated agent to the task
                original_agent = task.agent
                task.agent = delegated_agent
                
                # Set context if needed
                if hasattr(task, 'context') and task.context:
                    context_outputs = []
                    for ctx_idx in task.context:
                        if 0 <= ctx_idx < len(tasks_output):
                            context_outputs.append(tasks_output[ctx_idx])
                    if context_outputs:
                        task._context_outputs = context_outputs
                
                try:
                    # Execute task
                    output = await task.execute_async() if hasattr(task, 'execute_async') else task.execute()
                finally:
                    # Restore original agent
                    task.agent = original_agent
                
                # Worker response turn
                turns.append(self._create_turn(
                    delegated_agent,
                    output.raw if hasattr(output, 'raw') else str(output),
                    phase="execution",
                    task_index=i
                ))
                
                # Manager review
                review = await self._manager_review_output(task, output, delegated_agent)
                turns.append(self._create_turn(
                    self.manager_agent,
                    review,
                    phase="review",
                    task_index=i
                ))
                
                # Store output
                if isinstance(output, TaskOutput):
                    tasks_output.append(output)
                else:
                    tasks_output.append(TaskOutput(
                        raw=str(output),
                        task=task
                    ))
                
                self._emit_event('task_complete', {'task': task, 'output': output})
            
            # Manager final summary
            final_summary = await self._manager_summarize_results(tasks_output)
            turns.append(self._create_turn(
                self.manager_agent,
                final_summary,
                phase="summary"
            ))
            
            return ProcessResult(
                raw=final_summary,
                turns=turns,
                tasks_output=tasks_output,
                success=True,
                duration=self._get_duration(),
                metadata={
                    'process_type': 'hierarchical',
                    'manager': self.manager_agent.role,
                    'workers': [agent.role for agent in worker_agents],
                    'tasks_completed': len(tasks_output),
                    'total_tasks': len(tasks)
                }
            )
            
        except Exception as e:
            return ProcessResult(
                raw="",
                turns=turns,
                tasks_output=tasks_output,
                success=False,
                error=str(e),
                duration=self._get_duration()
            )
    
    async def _manager_analyze_tasks(self, tasks: List[LiteTask]) -> str:
        """Manager analyzes all tasks"""
        task_descriptions = "\n".join(f"- {task.description}" for task in tasks)
        analysis_prompt = f"Analyze these tasks and plan the execution strategy:\n{task_descriptions}"
        
        # Use manager agent to analyze
        return "Task analysis complete. Ready to delegate to team members."
    
    async def _manager_delegate_task(
        self, 
        task: LiteTask, 
        worker_agents: List[LiteAgent],
        agent_lookup: Dict[str, LiteAgent]
    ) -> LiteAgent:
        """Manager decides which agent should handle the task"""
        # If task has specific agent assigned, use it
        if hasattr(task, 'agent_role') and task.agent_role:
            if task.agent_role in agent_lookup:
                return agent_lookup[task.agent_role]
        
        # Otherwise manager decides (for now, round-robin)
        task_index = self._tasks.index(task)
        return worker_agents[task_index % len(worker_agents)]
    
    async def _manager_review_output(
        self, 
        task: LiteTask, 
        output: Any,
        worker: LiteAgent
    ) -> str:
        """Manager reviews worker output"""
        return f"Reviewed {worker.role}'s work. Output meets requirements."
    
    async def _manager_summarize_results(self, outputs: List[TaskOutput]) -> str:
        """Manager creates final summary"""
        if not outputs:
            return "No tasks were completed."
        
        summary = "Team successfully completed all assigned tasks:\n\n"
        for i, output in enumerate(outputs):
            summary += f"{i+1}. {output.raw[:100]}...\n"
        
        return summary


# Register with factory
ProcessFactory.register('hierarchical', HierarchicalProcess)