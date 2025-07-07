"""Tests for PanelProcess"""

import asyncio
import pytest
from unittest.mock import Mock, patch

from litecrew.agent import Agent as LiteAgent
from litecrew.task import LiteTask, TaskOutput
from litecrew.processes import (
    PanelProcess,
    ProcessConfig,
    ProcessFactory,
    ProcessPrompts
)


class TestPanelProcess:
    """Test PanelProcess functionality"""
    
    @pytest.mark.asyncio
    async def test_basic_panel(self):
        """Test basic panel discussion"""
        # Setup panel
        moderator = LiteAgent(role="Host", goal="Moderate", backstory="TV host")
        expert1 = LiteAgent(role="Scientist", goal="Explain", backstory="Researcher")
        expert2 = LiteAgent(role="Engineer", goal="Apply", backstory="Builder")
        
        task = LiteTask(
            description="Discuss renewable energy",
            expected_output="Expert insights and recommendations"
        )
        
        # Mock responses
        moderator.execute = Mock(return_value="Welcome to our panel.")
        expert1.execute = Mock(return_value="From a scientific perspective...")
        expert2.execute = Mock(return_value="In practical terms...")
        
        # Execute panel
        process = PanelProcess()
        result = await process.execute([moderator, expert1, expert2], [task])
        
        # Verify results
        assert result.success is True
        assert len(result.turns) > 0
        assert len(result.tasks_output) == 1
        assert "panel" in result.metadata['process_type']
        
        # Check structure
        phases = {turn.metadata.get('phase') for turn in result.turns}
        assert "introduction" in phases
        assert "expert_opinion" in phases
        assert "synthesis" in phases or "consensus" in phases
        assert "closing" in phases
    
    @pytest.mark.asyncio
    async def test_panel_styles(self):
        """Test different panel styles"""
        agents = [
            LiteAgent(role="Moderator", goal="Guide", backstory="Host"),
            LiteAgent(role="Expert1", goal="Inform", backstory="Specialist"),
            LiteAgent(role="Expert2", goal="Advise", backstory="Consultant")
        ]
        task = LiteTask(description="Topic", expected_output="Insights")
        
        for agent in agents:
            agent.execute = Mock(return_value=f"{agent.role} contribution")
        
        # Test different styles
        for style in ["expert", "roundtable", "symposium"]:
            process = ProcessFactory.create("panel", {"panel_style": style})
            result = await process.execute(agents, [task])
            
            assert result.success is True
            assert result.metadata['panel_style'] == style
    
    @pytest.mark.asyncio
    async def test_panel_with_voting(self):
        """Test panel with voting enabled"""
        agents = [
            LiteAgent(role="Chair", goal="Lead", backstory="Leader"),
            LiteAgent(role="Member1", goal="Contribute", backstory="Expert"),
            LiteAgent(role="Member2", goal="Contribute", backstory="Expert"),
            LiteAgent(role="Member3", goal="Contribute", backstory="Expert")
        ]
        task = LiteTask(description="Choose best approach", expected_output="Voted decision")
        
        for agent in agents:
            agent.execute = Mock(return_value="Opinion")
        
        # Enable voting
        process = ProcessFactory.create(
            "panel",
            {"voting_enabled": True, "consensus_required": False}
        )
        
        result = await process.execute(agents, [task])
        
        # Check voting occurred
        assert result.success is True
        voting_turns = [t for t in result.turns if t.metadata.get('phase') == 'voting']
        assert len(voting_turns) == 1
        
        # Check vote results in turn
        vote_turn = voting_turns[0]
        assert 'votes' in vote_turn.metadata
        assert "vote results" in vote_turn.content.lower()
    
    @pytest.mark.asyncio
    async def test_panel_consensus(self):
        """Test panel consensus building"""
        agents = [
            LiteAgent(role="Facilitator", goal="Unite", backstory="Mediator"),
            LiteAgent(role="Voice1", goal="Express", backstory="Advocate"),
            LiteAgent(role="Voice2", goal="Express", backstory="Representative")
        ]
        task = LiteTask(description="Find common ground", expected_output="Consensus")
        
        for agent in agents:
            agent.execute = Mock(return_value="Perspective")
        
        # Require consensus
        process = ProcessFactory.create(
            "panel",
            {"consensus_required": True, "voting_enabled": False}
        )
        
        result = await process.execute(agents, [task])
        
        # Check consensus reached
        assert result.success is True
        consensus_turns = [t for t in result.turns if t.metadata.get('phase') == 'consensus']
        assert len(consensus_turns) == 1
        assert "consensus" in consensus_turns[0].content.lower()
    
    @pytest.mark.asyncio
    async def test_panel_follow_ups(self):
        """Test panel follow-up discussions"""
        agents = [
            LiteAgent(role="Mod", goal="Guide", backstory="Guide"),
            LiteAgent(role="A", goal="Share", backstory="Expert"),
            LiteAgent(role="B", goal="Share", backstory="Expert")
        ]
        task = LiteTask(description="Complex topic", expected_output="Deep insights")
        
        # Track call order
        call_counts = {"Mod": 0, "A": 0, "B": 0}
        
        def mock_execute(agent_role):
            call_counts[agent_role] += 1
            return f"Call {call_counts[agent_role]} from {agent_role}"
        
        for agent in agents:
            agent.execute = Mock(side_effect=lambda r=agent.role: mock_execute(r))
        
        process = PanelProcess()
        result = await process.execute(agents, [task])
        
        # Check multiple rounds occurred
        follow_up_turns = [t for t in result.turns if t.metadata.get('phase') == 'follow_up']
        assert len(follow_up_turns) >= 4  # At least 2 rounds * 2 panelists
        
        # Check round numbers
        rounds = {t.metadata.get('round') for t in follow_up_turns if 'round' in t.metadata}
        assert len(rounds) >= 2
    
    @pytest.mark.asyncio
    async def test_moderator_questions(self):
        """Test moderator question functionality"""
        agents = [
            LiteAgent(role="Moderator", goal="Question", backstory="Journalist"),
            LiteAgent(role="Guest", goal="Answer", backstory="Expert")
        ]
        task = LiteTask(description="Interview topic", expected_output="Insights")
        
        for agent in agents:
            agent.execute = Mock(return_value="Response")
        
        # Test with questions enabled
        process = PanelProcess()
        process.moderator_questions = True
        
        result = await process.execute(agents, [task])
        
        # Check for topic introductions
        topic_intros = [t for t in result.turns if t.metadata.get('phase') == 'topic_introduction']
        assert len(topic_intros) >= 1
        
        # Test without questions
        process.moderator_questions = False
        result2 = await process.execute(agents, [task])
        
        topic_intros2 = [t for t in result2.turns if t.metadata.get('phase') == 'topic_introduction']
        assert len(topic_intros2) == 0
    
    def test_panel_prompts(self):
        """Test panel-specific prompts"""
        # Panel introduction
        intro = ProcessPrompts.get_prompt(
            "panel",
            "introduction",
            moderator_role="Host",
            panel_style="expert",
            panelist_list="Dr. A, Prof. B, Mr. C",
            task_list="- Topic 1\n- Topic 2"
        )
        
        assert "Host" in intro
        assert "expert" in intro
        assert "Dr. A, Prof. B, Mr. C" in intro
        
        # Expert opinion prompt
        opinion = ProcessPrompts.get_prompt(
            "panel",
            "expert_opinion",
            agent_role="Scientist",
            task_description="Climate change",
            expected_output="Solutions",
            context=""
        )
        
        assert "Scientist" in opinion
        assert "Climate change" in opinion
        assert "expert perspective" in opinion
        
        # Vote summary prompt
        vote_summary = ProcessPrompts.get_prompt(
            "panel",
            "vote_summary",
            moderator_role="Chair",
            task_description="Policy decision",
            vote_results="Option A: 3 votes\nOption B: 2 votes"
        )
        
        assert "Chair" in vote_summary
        assert "Option A: 3 votes" in vote_summary
    
    @pytest.mark.asyncio
    async def test_panel_metadata(self):
        """Test panel metadata tracking"""
        agents = [
            LiteAgent(role="Lead", goal="Guide", backstory="Leader"),
            LiteAgent(role="Expert1", goal="Advise", backstory="Advisor"),
            LiteAgent(role="Expert2", goal="Analyze", backstory="Analyst")
        ]
        task = LiteTask(description="Review proposal", expected_output="Recommendation")
        
        for agent in agents:
            agent.execute = Mock(return_value="Input")
        
        process = ProcessFactory.create(
            "panel",
            {
                "panel_style": "symposium",
                "consensus_required": True,
                "voting_enabled": False
            }
        )
        
        result = await process.execute(agents, [task])
        
        # Check metadata
        assert result.metadata['process_type'] == 'panel'
        assert result.metadata['panel_style'] == 'symposium'
        assert result.metadata['moderator'] == 'Lead'
        assert set(result.metadata['panelists']) == {'Expert1', 'Expert2'}
        assert result.metadata['consensus_required'] is True
        assert result.metadata['voting_enabled'] is False
    
    @pytest.mark.asyncio
    async def test_single_panelist(self):
        """Test panel with only moderator (edge case)"""
        moderator = LiteAgent(role="SoloHost", goal="Discuss", backstory="Expert host")
        task = LiteTask(description="Monologue topic", expected_output="Analysis")
        
        moderator.execute = Mock(return_value="Solo analysis")
        
        process = PanelProcess()
        result = await process.execute([moderator], [task])
        
        # Should still work
        assert result.success is True
        assert len(result.tasks_output) == 1
        assert result.metadata['moderator'] == 'SoloHost'
        assert len(result.metadata['panelists']) == 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in panel"""
        process = PanelProcess()
        
        # No agents
        result = await process.execute([], [LiteTask(description="Test", expected_output="Test")])
        assert result.success is False
        assert "No agents" in result.error
        
        # No tasks
        result = await process.execute([LiteAgent(role="Test", goal="Test", backstory="Test")], [])
        assert result.success is False
        assert "No tasks" in result.error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])