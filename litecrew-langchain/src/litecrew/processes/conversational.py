"""Conversational Process Implementation"""

from typing import Any, Dict, List, Optional
import random

from litecrew.agent import LiteAgent
from litecrew.task import LiteTask, TaskOutput

from .base import BaseProcess, ProcessResult
from .factory import ProcessFactory


class ConversationalProcess(BaseProcess):
    """Execute tasks through natural conversation between agents"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.min_turns = 3  # Minimum turns per agent
        self.max_turns = 10  # Maximum total turns
        self.turn_style = "round_robin"  # or "dynamic"
        
    @classmethod
    def from_config(cls, base_config, specific_config):
        """Create instance with specific configuration"""
        instance = cls(base_config)
        instance.min_turns = specific_config.get('min_turns', 3)
        instance.max_turns = specific_config.get('max_turns', 10)
        instance.turn_style = specific_config.get('turn_style', 'round_robin')
        return instance
        
    async def execute(
        self, 
        agents: List[LiteAgent], 
        tasks: List[LiteTask],
        inputs: Optional[Dict[str, Any]] = None
    ) -> ProcessResult:
        """Execute tasks through conversational exchanges"""
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
        
        # Initialize conversation
        turns = []
        tasks_output: List[TaskOutput] = []
        context = inputs or {}
        
        try:
            # Start conversation with first agent introducing the tasks
            intro = await self._generate_introduction(agents[0], tasks)
            turns.append(self._create_turn(
                agents[0],
                intro,
                phase="introduction"
            ))
            
            # Conversational turns
            turn_count = 0
            agent_turn_counts = {agent.role: 0 for agent in agents}
            
            while turn_count < self.max_turns:
                if not self._should_continue(turn_count):
                    break
                
                # Select next speaker
                next_agent = await self._select_next_speaker(
                    agents, 
                    agent_turn_counts, 
                    turns
                )
                
                # Generate response using agent's execute method
                try:
                    # Build conversation context
                    conversation_context = self._build_conversation_context(turns, tasks)
                    
                    # Execute through agent
                    response = next_agent.execute(
                        f"Continue the conversation about: {tasks[0].description}",
                        conversation_context
                    )
                except Exception as e:
                    # Let error propagate to outer try/except
                    raise e
                
                # Create turn
                turns.append(self._create_turn(
                    next_agent,
                    response,
                    phase="conversation",
                    turn_number=turn_count
                ))
                
                # Update counters
                agent_turn_counts[next_agent.role] += 1
                turn_count += 1
                
                # Extract any task completions from response
                task_output = self._extract_task_output(response, next_agent, tasks)
                if task_output:
                    tasks_output.append(task_output)
                    self._emit_event('task_progress', {'agent': next_agent, 'output': task_output})
                
                # Check if minimum turns reached for all agents
                min_reached = all(count >= self.min_turns for count in agent_turn_counts.values())
                if min_reached and turn_count >= len(agents) * self.min_turns:
                    if self._conversation_complete(turns, tasks) or self._all_tasks_discussed(tasks, turns):
                        break
            
            # Final summary
            summary_agent = self._select_summary_agent(agents, agent_turn_counts)
            summary = await self._generate_conversation_summary(
                summary_agent,
                turns,
                tasks_output
            )
            
            turns.append(self._create_turn(
                summary_agent,
                summary,
                phase="summary"
            ))
            
            # Ensure all tasks have outputs
            for task in tasks:
                if not any(out.raw for out in tasks_output if hasattr(out, 'task') and out.task == task):
                    # Create output from conversation
                    task_result = self._synthesize_task_result(task, turns)
                    tasks_output.append(TaskOutput(
                        raw=task_result,
                        task=task
                    ))
            
            return ProcessResult(
                raw=summary,
                turns=turns,
                tasks_output=tasks_output,
                success=True,
                duration=self._get_duration(),
                metadata={
                    'process_type': 'conversational',
                    'total_turns': len(turns),
                    'agent_turns': agent_turn_counts,
                    'min_turns_reached': all(count >= self.min_turns for count in agent_turn_counts.values())
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
    
    async def _generate_introduction(self, agent: LiteAgent, tasks: List[LiteTask]) -> str:
        """Generate introduction to start conversation"""
        task_list = "\n".join(f"- {task.description}" for task in tasks)
        prompt = f"As {agent.role}, introduce these topics for discussion:\n{task_list}"
        
        # For now, return a template response
        return f"Hello team, I'm {agent.role}. We need to discuss the following tasks:\n{task_list}\nLet's collaborate to find the best solutions."
    
    async def _select_next_speaker(
        self, 
        agents: List[LiteAgent],
        turn_counts: Dict[str, int],
        turns: List
    ) -> LiteAgent:
        """Select next agent to speak"""
        if self.turn_style == "round_robin":
            # Find agent with least turns
            min_turns = min(turn_counts.values())
            candidates = [a for a in agents if turn_counts[a.role] == min_turns]
            return random.choice(candidates)
        else:
            # Dynamic selection based on conversation flow
            # For now, random selection with slight bias to those who spoke less
            weights = [max(1, max(turn_counts.values()) - turn_counts[a.role] + 1) for a in agents]
            return random.choices(agents, weights=weights)[0]
    
    async def _generate_conversational_response(
        self,
        agent: LiteAgent,
        turns: List,
        tasks: List[LiteTask],
        context: Dict
    ) -> str:
        """Generate agent's conversational response"""
        # Build conversation history
        recent_turns = turns[-5:] if len(turns) > 5 else turns
        history = "\n".join(f"{turn.agent}: {turn.content[:200]}..." for turn in recent_turns)
        
        # For now, return a template response
        task_focus = random.choice(tasks)
        return f"Building on the previous points, I believe {task_focus.description} requires careful consideration. From my perspective as {agent.role}, we should focus on achieving {task_focus.expected_output}."
    
    def _extract_task_output(self, response: str, agent: LiteAgent, tasks: List[LiteTask]) -> Optional[TaskOutput]:
        """Extract task completion from conversational response"""
        # Simple heuristic: if response mentions completing or solving a task
        keywords = ["completed", "solved", "finished", "achieved", "implemented"]
        if any(keyword in response.lower() for keyword in keywords):
            # Find which task might be completed
            for task in tasks:
                if task.description.lower() in response.lower():
                    return TaskOutput(
                        raw=response,
                        agent_role=agent.role
                    )
        return None
    
    def _all_tasks_discussed(self, tasks: List[LiteTask], turns: List) -> bool:
        """Check if all tasks have been discussed"""
        discussed_tasks = set()
        for turn in turns:
            for task in tasks:
                if task.description.lower() in turn.content.lower():
                    discussed_tasks.add(task.description)
        return len(discussed_tasks) == len(tasks)
    
    def _conversation_complete(self, turns: List, tasks: List[LiteTask]) -> bool:
        """Check if conversation has reached natural completion"""
        # Check if all tasks discussed and some consensus reached
        if not self._all_tasks_discussed(tasks, turns):
            return False
        
        # Check for conclusion indicators in recent turns
        recent = [turn.content.lower() for turn in turns[-3:]]
        conclusion_words = ["agree", "consensus", "decided", "conclusion", "summary"]
        return any(word in content for content in recent for word in conclusion_words)
    
    def _select_summary_agent(self, agents: List[LiteAgent], turn_counts: Dict[str, int]) -> LiteAgent:
        """Select agent to provide summary"""
        # Select agent who participated most (likely has best overview)
        max_turns = max(turn_counts.values())
        candidates = [a for a in agents if turn_counts[a.role] == max_turns]
        return candidates[0] if candidates else agents[0]
    
    async def _generate_conversation_summary(
        self,
        agent: LiteAgent,
        turns: List,
        outputs: List[TaskOutput]
    ) -> str:
        """Generate summary of conversation"""
        total_turns = len(turns)
        participants = list(set(turn.agent for turn in turns))
        
        summary = f"After {total_turns} exchanges between {', '.join(participants)}, "
        summary += f"we reached the following conclusions:\n\n"
        
        if outputs:
            summary += "Key outcomes:\n"
            for i, output in enumerate(outputs, 1):
                summary += f"{i}. {output.raw[:100]}...\n"
        else:
            summary += "The team engaged in productive discussion and explored various perspectives."
        
        return summary
    
    def _synthesize_task_result(self, task: LiteTask, turns: List) -> str:
        """Synthesize task result from conversation turns"""
        relevant_content = []
        for turn in turns:
            if task.description.lower() in turn.content.lower():
                relevant_content.append(f"{turn.agent}: {turn.content}")
        
        if relevant_content:
            return f"Based on team discussion:\n" + "\n".join(relevant_content[-3:])
        else:
            return f"Task '{task.description}' was addressed through collaborative discussion."
    
    def _build_conversation_context(self, turns: List, tasks: List[LiteTask]) -> str:
        """Build context from conversation history"""
        if not turns:
            return f"Starting discussion about: {', '.join(t.description for t in tasks)}"
        
        # Get recent conversation
        recent_turns = turns[-5:] if len(turns) > 5 else turns
        context = "Previous conversation:\n"
        for turn in recent_turns:
            context += f"{turn.agent}: {turn.content[:150]}...\n"
        
        context += f"\nTasks to discuss: {', '.join(t.description for t in tasks)}"
        return context


# Register with factory
ProcessFactory.register('conversational', ConversationalProcess)