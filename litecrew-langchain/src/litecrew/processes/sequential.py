"""Sequential Process Implementation"""

from typing import Any, Dict, List, Optional

from litecrew.agent import LiteAgent
from litecrew.task import LiteTask, TaskOutput

from .base import BaseProcess, ProcessResult
from .factory import ProcessFactory


class SequentialProcess(BaseProcess):
    """Execute tasks sequentially in order"""
    
    async def execute(
        self, 
        agents: List[LiteAgent], 
        tasks: List[LiteTask],
        inputs: Optional[Dict[str, Any]] = None
    ) -> ProcessResult:
        """Execute tasks sequentially"""
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
        
        # Build agent lookup
        agent_lookup = {agent.role: agent for agent in agents}
        
        tasks_output: List[TaskOutput] = []
        turns = []
        
        try:
            # Execute tasks sequentially
            for i, task in enumerate(tasks):
                if not self._should_continue(i):
                    break
                    
                # Find agent for task
                agent = None
                if hasattr(task, 'agent') and task.agent:
                    agent = task.agent
                elif hasattr(task, 'agent_role') and task.agent_role:
                    agent = agent_lookup.get(task.agent_role)
                else:
                    # Use first agent as default
                    agent = agents[0] if agents else None
                    
                if not agent:
                    raise ValueError(f"No agent found for task: {task.description}")
                
                # Set context from previous tasks
                if hasattr(task, 'context') and task.context:
                    context_outputs = []
                    for ctx_idx in task.context:
                        if 0 <= ctx_idx < len(tasks_output):
                            context_outputs.append(tasks_output[ctx_idx])
                    # Pass context to task execution
                    if context_outputs:
                        task._context_outputs = context_outputs
                
                # Execute task
                self._emit_event('task_start', {'task': task, 'agent': agent})
                
                if self.config.verbose:
                    print(f"\nExecuting task {i+1}/{len(tasks)}: {task.description[:50]}...")
                
                # Execute the task
                output = await task.execute_async() if hasattr(task, 'execute_async') else task.execute()
                
                # Create turn
                turn = self._create_turn(
                    agent,
                    output.raw if hasattr(output, 'raw') else str(output),
                    task_index=i,
                    task_description=task.description
                )
                turns.append(turn)
                
                # Store output
                if isinstance(output, TaskOutput):
                    tasks_output.append(output)
                else:
                    # Wrap in TaskOutput if needed
                    tasks_output.append(TaskOutput(
                        raw=str(output),
                        task=task
                    ))
                
                self._emit_event('task_complete', {'task': task, 'output': output})
                
            # Aggregate results
            raw_output = self._aggregate_results(turns, tasks_output)
            
            return ProcessResult(
                raw=raw_output,
                turns=turns,
                tasks_output=tasks_output,
                success=True,
                duration=self._get_duration(),
                metadata={
                    'process_type': 'sequential',
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


# Register with factory
ProcessFactory.register('sequential', SequentialProcess)