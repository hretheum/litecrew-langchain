"""Process-specific prompts for multi-agent processes"""

from typing import Any, Dict, Optional


class ProcessPrompts:
    """Centralized prompt templates for different process types"""

    # Conversational Process Prompts
    CONVERSATIONAL = {
        "introduction": """As {agent_role}, introduce the following topics for collaborative discussion:
{task_list}

Start with a warm greeting and set a collaborative tone.""",
        "response": """You are {agent_role} in a collaborative discussion.

Previous conversation:
{history}

Your task: Contribute meaningfully to the discussion about '{task_description}'.
Expected outcome: {expected_output}

Provide your perspective, build on others' ideas, and work towards the goal.""",
        "summary": """As {agent_role}, summarize our conversation.

Total exchanges: {turn_count}
Participants: {participants}
Topics discussed: {topics}

Provide a concise summary highlighting key decisions and next steps.""",
    }

    # Debate Process Prompts
    DEBATE = {
        "moderator_opening": """As {moderator_role}, formally open this debate.

Topics for debate:
{task_list}

Welcome all participants and establish debate rules and structure.""",
        "opening_statement": """You are {agent_role} representing the {position} in this debate.

Topic: {task_description}
Your stance: You {stance} this approach
Goal: {expected_output}

Present your opening statement with clear position and initial arguments.""",
        "argument": """You are {agent_role} representing the {position}.

Round {round_num} of the debate on: {task_description}
Previous arguments have been made.

Present your {round_focus} arguments with evidence and reasoning.""",
        "rebuttal": """You are {agent_role} representing the {position}.

Respond to the {opposing_position}'s recent arguments.
Highlight flaws in their reasoning while strengthening your position.""",
        "closing_statement": """You are {agent_role} representing the {position}.

This is your closing statement for: {task_description}
Goal: {expected_output}

Summarize your strongest arguments and why your position should prevail.""",
        "synthesis": """As {synthesizer_role}, synthesize this debate into actionable outcomes.

Topic debated: {task_description}
Total arguments: {total_arguments}
Goal: {expected_output}

Create a balanced resolution incorporating insights from all positions.""",
    }

    # Panel Process Prompts
    PANEL = {
        "introduction": """As {moderator_role}, welcome everyone to our {panel_style} panel.

Panelists: {panelist_list}
Topics for discussion:
{task_list}

Set the stage for expert discussion and introduce the format.""",
        "topic_intro": """As {moderator_role}, introduce the next topic:

Topic: {task_description}
Goal: {expected_output}

Frame the question for our expert panelists.""",
        "expert_opinion": """You are {agent_role}, an expert panelist.

Topic: {task_description}
Goal: {expected_output}
{context}

Share your expert perspective, drawing from your domain expertise.""",
        "follow_up": """You are {agent_role} in round {round_num} of panel discussion.

Topic: {task_description}
Previous perspectives shared.

Add nuance, address gaps, or build on other panelists' contributions.""",
        "consensus": """As {moderator_role}, help the panel reach consensus.

Topic: {task_description}
Goal: {expected_output}
Expert views have been shared.

Identify common ground and synthesize a consensus position.""",
        "vote_summary": """As {moderator_role}, announce the panel vote results.

Topic: {task_description}
Voting results:
{vote_results}

Declare the panel's recommendation based on the vote.""",
        "synthesis": """As {moderator_role}, synthesize the panel discussion.

Topic: {task_description}
Goal: {expected_output}
Number of expert perspectives: {expert_count}

Create a comprehensive synthesis incorporating all viewpoints.""",
    }

    # Brainstorm Process Prompts (for future implementation)
    BRAINSTORM = {
        "kickoff": """Let's brainstorm solutions for: {task_description}

Goal: {expected_output}
Rules: No idea is too wild, build on others' ideas, quantity over quality initially.

Start sharing creative ideas!""",
        "ideation": """You are {agent_role} in a brainstorming session.

Topic: {task_description}
Ideas so far: {idea_count}

Contribute {ideas_per_turn} new ideas. Be creative and think outside the box!""",
        "refinement": """Now let's refine our best ideas.

Top ideas identified: {top_ideas}

As {agent_role}, help develop these ideas into actionable solutions.""",
    }

    @classmethod
    def get_prompt(cls, process_type: str, prompt_name: str, **kwargs: Any) -> str:
        """Get a specific prompt template and format it with provided kwargs"""
        process_prompts = getattr(cls, process_type.upper(), {})

        if prompt_name not in process_prompts:
            raise ValueError(
                f"Unknown prompt '{prompt_name}' for process '{process_type}'"
            )

        template = process_prompts[prompt_name]

        try:
            return str(template.format(**kwargs))
        except KeyError as e:
            raise ValueError(f"Missing required parameter for prompt: {e}")

    @classmethod
    def get_process_instructions(cls, process_type: str) -> Dict[str, Any]:
        """Get general instructions for how agents should behave in each process type"""
        instructions = {
            "conversational": {
                "tone": "collaborative and friendly",
                "goals": [
                    "build on others' ideas",
                    "seek understanding",
                    "find common ground",
                ],
                "avoid": [
                    "dominating conversation",
                    "dismissing others",
                    "going off-topic",
                ],
                "techniques": [
                    "active listening",
                    "yes-and thinking",
                    "clarifying questions",
                ],
            },
            "debate": {
                "tone": "formal and respectful",
                "goals": [
                    "present strong arguments",
                    "address counterpoints",
                    "persuade audience",
                ],
                "avoid": [
                    "personal attacks",
                    "logical fallacies",
                    "emotional manipulation",
                ],
                "techniques": [
                    "evidence-based reasoning",
                    "structured arguments",
                    "effective rebuttals",
                ],
            },
            "panel": {
                "tone": "professional and expert",
                "goals": [
                    "share domain expertise",
                    "provide unique insights",
                    "educate audience",
                ],
                "avoid": [
                    "oversimplification",
                    "jargon overuse",
                    "contradicting unnecessarily",
                ],
                "techniques": [
                    "drawing from experience",
                    "citing examples",
                    "clear explanations",
                ],
            },
            "brainstorm": {
                "tone": "creative and energetic",
                "goals": [
                    "generate many ideas",
                    "think unconventionally",
                    "inspire others",
                ],
                "avoid": [
                    "criticism during ideation",
                    "self-censoring",
                    "premature evaluation",
                ],
                "techniques": [
                    "lateral thinking",
                    "building on ideas",
                    "wild associations",
                ],
            },
        }

        return instructions.get(process_type, {})


def enhance_agent_for_process(
    agent: Any, process_type: str, role_in_process: Optional[str] = None
) -> None:
    """Enhance an agent with process-specific instructions"""
    instructions = ProcessPrompts.get_process_instructions(process_type)

    if not instructions:
        return

    # Add process-specific context to agent's backstory or instructions
    process_context = (
        f"\n\nIn this {process_type} process, maintain a {instructions['tone']} tone. "
    )
    process_context += f"Focus on: {', '.join(instructions['goals'])}. "
    process_context += f"Avoid: {', '.join(instructions['avoid'])}."

    # This would be integrated with the agent's system prompt
    # The actual implementation depends on how agents store their configuration
    if hasattr(agent, "process_instructions"):
        agent.process_instructions = process_context

    if role_in_process:
        if hasattr(agent, "process_role"):
            agent.process_role = role_in_process
