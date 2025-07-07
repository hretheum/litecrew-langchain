"""Debate Process Implementation"""

from typing import Any, Dict, List, Optional, Tuple
import random

from litecrew.agent import LiteAgent
from litecrew.task import LiteTask, TaskOutput

from .base import BaseProcess, ProcessResult
from .factory import ProcessFactory


class DebateProcess(BaseProcess):
    """Execute tasks through structured debate between agents"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.rounds = 3  # Number of debate rounds
        self.allow_rebuttals = True
        self.moderator_role = None  # Optional moderator
        self.debate_style = "oxford"  # oxford, parliamentary, socratic
        
    @classmethod
    def from_config(cls, base_config, specific_config):
        """Create instance with specific configuration"""
        instance = cls(base_config)
        instance.rounds = specific_config.get('rounds', 3)
        instance.allow_rebuttals = specific_config.get('allow_rebuttals', True)
        instance.moderator_role = specific_config.get('moderator_role')
        instance.debate_style = specific_config.get('debate_style', 'oxford')
        return instance
        
    async def execute(
        self, 
        agents: List[LiteAgent], 
        tasks: List[LiteTask],
        inputs: Optional[Dict[str, Any]] = None
    ) -> ProcessResult:
        """Execute tasks through structured debate"""
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
        
        turns = []
        tasks_output: List[TaskOutput] = []
        
        try:
            # Assign debate positions
            positions = self._assign_debate_positions(agents)
            moderator = positions.get('moderator')
            debaters = positions.get('debaters', agents)
            
            # Opening: Frame the debate
            if moderator:
                opening = await self._moderator_opening(moderator, tasks)
                turns.append(self._create_turn(
                    moderator,
                    opening,
                    phase="opening",
                    role="moderator"
                ))
            
            # Process each task through debate
            for task_idx, task in enumerate(tasks):
                if not self._should_continue(task_idx):
                    break
                
                self._emit_event('debate_start', {'task': task})
                
                # Opening statements
                for i, debater in enumerate(debaters):
                    position = "proposition" if i % 2 == 0 else "opposition"
                    statement = await self._generate_opening_statement(
                        debater, task, position
                    )
                    turns.append(self._create_turn(
                        debater,
                        statement,
                        phase="opening_statement",
                        position=position,
                        task_index=task_idx
                    ))
                
                # Debate rounds
                for round_num in range(self.rounds):
                    # Main arguments
                    for i, debater in enumerate(debaters):
                        position = "proposition" if i % 2 == 0 else "opposition"
                        argument = await self._generate_argument(
                            debater, task, position, turns, round_num
                        )
                        turns.append(self._create_turn(
                            debater,
                            argument,
                            phase="argument",
                            round=round_num + 1,
                            position=position,
                            task_index=task_idx
                        ))
                    
                    # Rebuttals (if enabled)
                    if self.allow_rebuttals and round_num < self.rounds - 1:
                        for i, debater in enumerate(debaters):
                            position = "proposition" if i % 2 == 0 else "opposition"
                            rebuttal = await self._generate_rebuttal(
                                debater, position, turns[-len(debaters):]
                            )
                            turns.append(self._create_turn(
                                debater,
                                rebuttal,
                                phase="rebuttal",
                                round=round_num + 1,
                                position=position,
                                task_index=task_idx
                            ))
                
                # Closing statements
                for i, debater in enumerate(debaters):
                    position = "proposition" if i % 2 == 0 else "opposition"
                    closing = await self._generate_closing_statement(
                        debater, task, position, turns
                    )
                    turns.append(self._create_turn(
                        debater,
                        closing,
                        phase="closing_statement",
                        position=position,
                        task_index=task_idx
                    ))
                
                # Resolution/Synthesis
                resolution = await self._synthesize_debate_outcome(
                    task, turns, moderator or debaters[0]
                )
                
                turns.append(self._create_turn(
                    moderator or debaters[0],
                    resolution,
                    phase="resolution",
                    task_index=task_idx
                ))
                
                # Create task output
                tasks_output.append(TaskOutput(
                    raw=resolution,
                    agent_role=(moderator or debaters[0]).role
                ))
                
                self._emit_event('debate_complete', {'task': task, 'resolution': resolution})
            
            # Final summary
            final_summary = self._create_debate_summary(turns, tasks_output)
            
            return ProcessResult(
                raw=final_summary,
                turns=turns,
                tasks_output=tasks_output,
                success=True,
                duration=self._get_duration(),
                metadata={
                    'process_type': 'debate',
                    'debate_style': self.debate_style,
                    'total_rounds': self.rounds,
                    'total_turns': len(turns),
                    'positions': {
                        'moderator': moderator.role if moderator else None,
                        'debaters': [d.role for d in debaters]
                    }
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
    
    def _assign_debate_positions(self, agents: List[LiteAgent]) -> Dict[str, Any]:
        """Assign debate positions to agents"""
        positions = {}
        
        # Check for moderator
        if self.moderator_role:
            moderator_agent = next(
                (a for a in agents if a.role == self.moderator_role), 
                None
            )
            if moderator_agent:
                positions['moderator'] = moderator_agent
                positions['debaters'] = [a for a in agents if a != moderator_agent]
            else:
                positions['debaters'] = agents
        else:
            positions['debaters'] = agents
        
        return positions
    
    async def _moderator_opening(self, moderator: LiteAgent, tasks: List[LiteTask]) -> str:
        """Generate moderator's opening statement"""
        task_list = "\n".join(f"- {task.description}" for task in tasks)
        return f"Welcome to this debate. As {moderator.role}, I will moderate our discussion on:\n{task_list}\n\nLet's hear opening statements from all parties."
    
    async def _generate_opening_statement(
        self, 
        agent: LiteAgent, 
        task: LiteTask,
        position: str
    ) -> str:
        """Generate opening statement for debate position"""
        stance = "support" if position == "proposition" else "challenge"
        return f"As {agent.role} representing the {position}, I {stance} the approach to '{task.description}'. My position is that we should focus on {task.expected_output} through careful analysis and evidence-based reasoning."
    
    async def _generate_argument(
        self,
        agent: LiteAgent,
        task: LiteTask,
        position: str,
        previous_turns: List,
        round_num: int
    ) -> str:
        """Generate debate argument"""
        stance = "advocate for" if position == "proposition" else "argue against"
        round_focus = ["initial", "substantive", "concluding"][min(round_num, 2)]
        
        return f"In this {round_focus} round, I {stance} the current approach. For '{task.description}', the evidence shows that {task.expected_output} is best achieved through methods aligned with the {position} position."
    
    async def _generate_rebuttal(
        self,
        agent: LiteAgent,
        position: str,
        recent_arguments: List
    ) -> str:
        """Generate rebuttal to opposing arguments"""
        opposing_position = "opposition" if position == "proposition" else "proposition"
        return f"While the {opposing_position} makes some points, as {agent.role}, I must highlight the flaws in their reasoning. The {position} position remains stronger because it addresses the core requirements more effectively."
    
    async def _generate_closing_statement(
        self,
        agent: LiteAgent,
        task: LiteTask,
        position: str,
        all_turns: List
    ) -> str:
        """Generate closing statement"""
        return f"In closing, the {position} has demonstrated through this debate that '{task.description}' is best addressed by our approach. We've shown clear reasoning and evidence supporting our position on achieving {task.expected_output}."
    
    async def _synthesize_debate_outcome(
        self,
        task: LiteTask,
        turns: List,
        synthesizer: LiteAgent
    ) -> str:
        """Synthesize debate into actionable outcome"""
        # Count arguments by position
        prop_args = len([t for t in turns if t.metadata.get('position') == 'proposition'])
        opp_args = len([t for t in turns if t.metadata.get('position') == 'opposition'])
        
        synthesis = f"After careful consideration of {prop_args + opp_args} arguments, "
        synthesis += f"the debate on '{task.description}' has revealed key insights. "
        synthesis += f"Both sides presented valid points, leading to a nuanced understanding. "
        synthesis += f"The recommended approach to achieve {task.expected_output} incorporates "
        synthesis += f"elements from both the proposition and opposition positions."
        
        return synthesis
    
    def _create_debate_summary(self, turns: List, outputs: List[TaskOutput]) -> str:
        """Create summary of entire debate"""
        total_arguments = len([t for t in turns if t.metadata.get('phase') == 'argument'])
        total_rebuttals = len([t for t in turns if t.metadata.get('phase') == 'rebuttal'])
        
        summary = f"Debate concluded after {self.rounds} rounds with {total_arguments} arguments and {total_rebuttals} rebuttals.\n\n"
        summary += "Resolutions reached:\n"
        
        for i, output in enumerate(outputs, 1):
            summary += f"{i}. {output.raw[:150]}...\n"
        
        return summary


# Register with factory
ProcessFactory.register('debate', DebateProcess)