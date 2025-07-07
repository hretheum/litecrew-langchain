"""Panel Process Implementation"""

from typing import Any, Dict, List, Optional
import random

from litecrew.agent import LiteAgent
from litecrew.task import LiteTask, TaskOutput

from .base import BaseProcess, ProcessResult
from .factory import ProcessFactory


class PanelProcess(BaseProcess):
    """Execute tasks through panel discussion with expert perspectives"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.panel_style = "expert"  # expert, roundtable, symposium
        self.consensus_required = False
        self.voting_enabled = False
        self.moderator_questions = True
        
    @classmethod
    def from_config(cls, base_config, specific_config):
        """Create instance with specific configuration"""
        instance = cls(base_config)
        instance.panel_style = specific_config.get('panel_style', 'expert')
        instance.consensus_required = specific_config.get('consensus_required', False)
        instance.voting_enabled = specific_config.get('voting_enabled', False)
        instance.moderator_questions = specific_config.get('moderator_questions', True)
        return instance
        
    async def execute(
        self, 
        agents: List[LiteAgent], 
        tasks: List[LiteTask],
        inputs: Optional[Dict[str, Any]] = None
    ) -> ProcessResult:
        """Execute tasks through panel discussion"""
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
            # Panel introduction
            moderator = agents[0]  # First agent acts as moderator
            panelists = agents[1:] if len(agents) > 1 else []
            
            # Opening
            opening = await self._generate_panel_introduction(moderator, panelists, tasks)
            turns.append(self._create_turn(
                moderator,
                opening,
                phase="introduction",
                role="moderator"
            ))
            
            # Process each task through panel discussion
            for task_idx, task in enumerate(tasks):
                if not self._should_continue(task_idx):
                    break
                
                self._emit_event('panel_topic_start', {'task': task})
                
                # Moderator introduces topic
                if self.moderator_questions:
                    question = await self._moderator_introduce_topic(moderator, task)
                    turns.append(self._create_turn(
                        moderator,
                        question,
                        phase="topic_introduction",
                        task_index=task_idx
                    ))
                
                # Collect expert opinions
                expert_views = []
                for panelist in panelists:
                    opinion = await self._generate_expert_opinion(
                        panelist, task, previous_opinions=expert_views
                    )
                    turns.append(self._create_turn(
                        panelist,
                        opinion,
                        phase="expert_opinion",
                        task_index=task_idx
                    ))
                    expert_views.append((panelist, opinion))
                
                # Follow-up discussion
                if len(panelists) > 1:
                    for round_num in range(2):  # 2 rounds of follow-up
                        for panelist in panelists:
                            follow_up = await self._generate_follow_up(
                                panelist, task, expert_views, round_num
                            )
                            turns.append(self._create_turn(
                                panelist,
                                follow_up,
                                phase="follow_up",
                                round=round_num + 1,
                                task_index=task_idx
                            ))
                
                # Synthesis or voting
                if self.voting_enabled:
                    votes, vote_summary = await self._conduct_panel_vote(
                        panelists, task, expert_views
                    )
                    turns.append(self._create_turn(
                        moderator,
                        vote_summary,
                        phase="voting",
                        task_index=task_idx,
                        votes=votes
                    ))
                    task_result = vote_summary
                elif self.consensus_required:
                    consensus = await self._build_consensus(
                        moderator, panelists, task, expert_views
                    )
                    turns.append(self._create_turn(
                        moderator,
                        consensus,
                        phase="consensus",
                        task_index=task_idx
                    ))
                    task_result = consensus
                else:
                    # Moderator synthesizes
                    synthesis = await self._moderator_synthesize(
                        moderator, task, expert_views
                    )
                    turns.append(self._create_turn(
                        moderator,
                        synthesis,
                        phase="synthesis",
                        task_index=task_idx
                    ))
                    task_result = synthesis
                
                # Create task output
                tasks_output.append(TaskOutput(
                    raw=task_result,
                    agent_role=moderator.role
                ))
                
                self._emit_event('panel_topic_complete', {'task': task})
            
            # Panel closing
            closing = await self._generate_panel_closing(moderator, tasks_output)
            turns.append(self._create_turn(
                moderator,
                closing,
                phase="closing"
            ))
            
            return ProcessResult(
                raw=closing,
                turns=turns,
                tasks_output=tasks_output,
                success=True,
                duration=self._get_duration(),
                metadata={
                    'process_type': 'panel',
                    'panel_style': self.panel_style,
                    'total_turns': len(turns),
                    'moderator': moderator.role,
                    'panelists': [p.role for p in panelists],
                    'consensus_required': self.consensus_required,
                    'voting_enabled': self.voting_enabled
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
    
    async def _generate_panel_introduction(
        self,
        moderator: LiteAgent,
        panelists: List[LiteAgent],
        tasks: List[LiteTask]
    ) -> str:
        """Generate panel introduction"""
        panelist_intros = ", ".join(p.role for p in panelists)
        task_topics = "\n".join(f"- {task.description}" for task in tasks)
        
        intro = f"Welcome to our {self.panel_style} panel. I'm {moderator.role}, your moderator. "
        intro += f"Today's distinguished panelists include: {panelist_intros}.\n\n"
        intro += f"We'll be discussing:\n{task_topics}\n\n"
        intro += "Let's begin with expert perspectives on each topic."
        
        return intro
    
    async def _moderator_introduce_topic(self, moderator: LiteAgent, task: LiteTask) -> str:
        """Moderator introduces a topic for discussion"""
        return f"Our next topic is '{task.description}'. The goal is to {task.expected_output}. Let's hear from our panel of experts."
    
    async def _generate_expert_opinion(
        self,
        panelist: LiteAgent,
        task: LiteTask,
        previous_opinions: List[tuple]
    ) -> str:
        """Generate expert opinion from panelist"""
        # Build on previous opinions if any
        context = ""
        if previous_opinions:
            context = f"Building on previous perspectives, "
        
        opinion = f"{context}As {panelist.role}, my expert view on '{task.description}' is that "
        opinion += f"achieving {task.expected_output} requires a specialized approach. "
        opinion += f"From my domain expertise, I recommend focusing on key factors that align with best practices in the field."
        
        return opinion
    
    async def _generate_follow_up(
        self,
        panelist: LiteAgent,
        task: LiteTask,
        expert_views: List[tuple],
        round_num: int
    ) -> str:
        """Generate follow-up comment from panelist"""
        if round_num == 0:
            return f"I'd like to add to my earlier point: the complexity of '{task.description}' also requires considering implementation challenges and practical constraints."
        else:
            return f"After hearing all perspectives, I believe the panel is converging on a comprehensive approach to {task.expected_output}."
    
    async def _conduct_panel_vote(
        self,
        panelists: List[LiteAgent],
        task: LiteTask,
        expert_views: List[tuple]
    ) -> tuple[Dict[str, str], str]:
        """Conduct panel voting on best approach"""
        votes = {}
        options = ["Option A: Rapid implementation", "Option B: Phased approach", "Option C: Hybrid strategy"]
        
        for panelist in panelists:
            votes[panelist.role] = random.choice(options)
        
        # Count votes
        vote_counts = {}
        for option in votes.values():
            vote_counts[option] = vote_counts.get(option, 0) + 1
        
        winner = max(vote_counts, key=vote_counts.get)
        summary = f"Panel vote results for '{task.description}':\n"
        for option, count in vote_counts.items():
            summary += f"- {option}: {count} votes\n"
        summary += f"\nThe panel recommends: {winner}"
        
        return votes, summary
    
    async def _build_consensus(
        self,
        moderator: LiteAgent,
        panelists: List[LiteAgent],
        task: LiteTask,
        expert_views: List[tuple]
    ) -> str:
        """Build consensus among panelists"""
        consensus = f"After extensive discussion, the panel has reached consensus on '{task.description}'. "
        consensus += f"All panelists agree that {task.expected_output} can be best achieved through "
        consensus += f"a collaborative approach that incorporates each expert's key insights."
        
        return consensus
    
    async def _moderator_synthesize(
        self,
        moderator: LiteAgent,
        task: LiteTask,
        expert_views: List[tuple]
    ) -> str:
        """Moderator synthesizes panel discussion"""
        synthesis = f"Based on our panel discussion of '{task.description}', several key themes emerged:\n"
        synthesis += f"1. Multiple valid approaches exist to achieve {task.expected_output}\n"
        synthesis += f"2. Each expert brought unique insights from their domain\n"
        synthesis += f"3. The recommended approach combines elements from all perspectives\n"
        synthesis += f"The panel's collective wisdom points to a balanced, multi-faceted solution."
        
        return synthesis
    
    async def _generate_panel_closing(
        self,
        moderator: LiteAgent,
        outputs: List[TaskOutput]
    ) -> str:
        """Generate panel closing statement"""
        closing = f"This concludes our {self.panel_style} panel discussion. "
        closing += f"We've addressed {len(outputs)} topics with insights from our expert panelists.\n\n"
        closing += "Key takeaways:\n"
        
        for i, output in enumerate(outputs, 1):
            closing += f"{i}. {output.raw[:100]}...\n"
        
        closing += f"\nThank you to all our panelists for their valuable contributions."
        
        return closing


# Register with factory
ProcessFactory.register('panel', PanelProcess)