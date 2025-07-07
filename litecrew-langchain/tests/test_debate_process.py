"""Tests for DebateProcess"""

from unittest.mock import Mock

import pytest

from litecrew.agent import Agent as LiteAgent
from litecrew.processes import (
    DebateProcess,
    ProcessFactory,
    ProcessPrompts,
)
from litecrew.task import LiteTask

# Ensure process is registered
from litecrew.processes.debate import DebateProcess as _DebateProcess


class TestDebateProcess:
    """Test DebateProcess functionality"""

    @pytest.mark.asyncio
    async def test_basic_debate(self):
        """Test basic debate process execution"""
        # Setup agents
        proponent = LiteAgent(
            role="Advocate", goal="Support", backstory="Policy expert"
        )
        opponent = LiteAgent(
            role="Critic", goal="Challenge", backstory="Devil's advocate"
        )

        # Setup task
        task = LiteTask(
            description="Should we implement feature X?",
            expected_output="Decision with rationale",
        )

        # Mock responses
        proponent.execute = Mock(return_value="Feature X will improve efficiency.")
        opponent.execute = Mock(return_value="Feature X has significant risks.")

        # Execute debate
        process = DebateProcess()
        result = await process.execute([proponent, opponent], [task])

        # Verify results
        assert result.success is True
        assert len(result.turns) > 0
        assert len(result.tasks_output) == 1
        assert "debate" in result.metadata["process_type"]

        # Check debate structure
        phases = {turn.metadata.get("phase") for turn in result.turns}
        assert "opening_statement" in phases
        assert "argument" in phases
        assert "closing_statement" in phases
        assert "resolution" in phases

    @pytest.mark.asyncio
    async def test_debate_with_moderator(self):
        """Test debate with moderator"""
        # Setup agents
        moderator = LiteAgent(
            role="Moderator", goal="Facilitate", backstory="Neutral party"
        )
        debater1 = LiteAgent(role="For", goal="Support", backstory="Supporter")
        debater2 = LiteAgent(role="Against", goal="Oppose", backstory="Opposer")

        task = LiteTask(description="Debate topic", expected_output="Consensus")

        # Mock responses
        for agent in [moderator, debater1, debater2]:
            agent.execute = Mock(return_value=f"{agent.role} statement")

        # Configure with moderator
        process = ProcessFactory.create(
            "debate",
            {"moderator_role": "Moderator", "rounds": 2, "allow_rebuttals": True},
        )

        result = await process.execute([moderator, debater1, debater2], [task])

        # Verify moderator participation
        assert result.success is True
        moderator_turns = [t for t in result.turns if t.agent == "Moderator"]
        assert len(moderator_turns) >= 2  # Opening and resolution

        # Check metadata
        assert result.metadata["positions"]["moderator"] == "Moderator"
        assert set(result.metadata["positions"]["debaters"]) == {"For", "Against"}

    @pytest.mark.asyncio
    async def test_debate_rounds(self):
        """Test multiple debate rounds"""
        agents = [
            LiteAgent(role="Pro", goal="Argue for", backstory="Expert"),
            LiteAgent(role="Con", goal="Argue against", backstory="Expert"),
        ]
        task = LiteTask(description="Topic", expected_output="Resolution")

        for agent in agents:
            agent.execute = Mock(return_value=f"{agent.role} argument")

        # Test with 3 rounds
        process = DebateProcess()
        process.rounds = 3

        result = await process.execute(agents, [task])

        # Count argument turns
        argument_turns = [
            t for t in result.turns if t.metadata.get("phase") == "argument"
        ]
        assert len(argument_turns) == 6  # 3 rounds * 2 debaters

        # Check round numbers
        rounds = {t.metadata.get("round") for t in argument_turns}
        assert rounds == {1, 2, 3}

    @pytest.mark.asyncio
    async def test_debate_positions(self):
        """Test debate position assignment"""
        agents = [
            LiteAgent(role=f"Debater{i}", goal="Debate", backstory="Expert")
            for i in range(4)
        ]
        task = LiteTask(description="Complex topic", expected_output="Analysis")

        for agent in agents:
            agent.execute = Mock(return_value="Statement")

        process = DebateProcess()
        result = await process.execute(agents, [task])

        # Check position distribution
        positions = {}
        for turn in result.turns:
            if "position" in turn.metadata:
                agent = turn.agent
                position = turn.metadata["position"]
                if agent not in positions:
                    positions[agent] = set()
                positions[agent].add(position)

        # Each debater should maintain consistent position
        for agent, pos_set in positions.items():
            assert len(pos_set) == 1  # One position per agent

        # Should have both positions represented
        all_positions = set()
        for pos_set in positions.values():
            all_positions.update(pos_set)
        assert "proposition" in all_positions
        assert "opposition" in all_positions

    @pytest.mark.asyncio
    async def test_rebuttals(self):
        """Test rebuttal functionality"""
        agents = [
            LiteAgent(role="A", goal="Win", backstory="Debater"),
            LiteAgent(role="B", goal="Win", backstory="Debater"),
        ]
        task = LiteTask(description="Topic", expected_output="Winner")

        for agent in agents:
            agent.execute = Mock(return_value="Response")

        # Test with rebuttals enabled
        process = DebateProcess()
        process.allow_rebuttals = True
        process.rounds = 2

        result = await process.execute(agents, [task])

        # Check for rebuttals
        rebuttal_turns = [
            t for t in result.turns if t.metadata.get("phase") == "rebuttal"
        ]
        assert len(rebuttal_turns) > 0  # Should have rebuttals

        # Test without rebuttals
        process.allow_rebuttals = False
        result2 = await process.execute(agents, [task])

        rebuttal_turns2 = [
            t for t in result2.turns if t.metadata.get("phase") == "rebuttal"
        ]
        assert len(rebuttal_turns2) == 0  # No rebuttals

    @pytest.mark.asyncio
    async def test_debate_styles(self):
        """Test different debate styles"""
        agents = [
            LiteAgent(role="Philosopher", goal="Explore", backstory="Thinker"),
            LiteAgent(role="Pragmatist", goal="Apply", backstory="Doer"),
        ]
        task = LiteTask(description="Abstract concept", expected_output="Understanding")

        for agent in agents:
            agent.execute = Mock(return_value="Perspective")

        # Test different styles
        for style in ["oxford", "parliamentary", "socratic"]:
            process = ProcessFactory.create("debate", {"debate_style": style})
            result = await process.execute(agents, [task])

            assert result.success is True
            assert result.metadata["debate_style"] == style

    def test_debate_prompts(self):
        """Test debate-specific prompts"""
        # Opening statement prompt
        opening = ProcessPrompts.get_prompt(
            "debate",
            "opening_statement",
            agent_role="Advocate",
            position="proposition",
            stance="support",
            task_description="Policy change",
            expected_output="Clear decision",
        )

        assert "Advocate" in opening
        assert "proposition" in opening
        assert "support" in opening

        # Synthesis prompt
        synthesis = ProcessPrompts.get_prompt(
            "debate",
            "synthesis",
            synthesizer_role="Judge",
            task_description="Complex issue",
            total_arguments=12,
            expected_output="Balanced view",
        )

        assert "Judge" in synthesis
        assert "12" in synthesis
        assert "balanced" in synthesis.lower()

    @pytest.mark.asyncio
    async def test_debate_resolution(self):
        """Test debate resolution synthesis"""
        agents = [
            LiteAgent(role="Yes", goal="Affirm", backstory="Supporter"),
            LiteAgent(role="No", goal="Negate", backstory="Opposer"),
        ]
        task = LiteTask(
            description="Should we proceed?",
            expected_output="Clear yes/no with reasoning",
        )

        # Mock detailed responses
        agents[0].execute = Mock(
            return_value="Strong arguments for proceeding due to benefits."
        )
        agents[1].execute = Mock(
            return_value="Significant risks that outweigh benefits."
        )

        process = DebateProcess()
        result = await process.execute(agents, [task])

        # Check resolution
        assert result.success is True
        resolution = result.tasks_output[0].raw
        assert "both" in resolution.lower() or "sides" in resolution.lower()
        assert "insight" in resolution.lower() or "understand" in resolution.lower()

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in debate"""
        # Test with invalid inputs instead
        process = DebateProcess()

        # No agents
        result = await process.execute(
            [], [LiteTask(description="Test", expected_output="Test")]
        )
        assert result.success is False
        assert "No agents" in result.error

        # No tasks
        result = await process.execute(
            [LiteAgent(role="Test", goal="Test", backstory="Test")], []
        )
        assert result.success is False
        assert "No tasks" in result.error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
