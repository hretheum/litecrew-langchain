"""Tests for processes to improve coverage."""

import pytest
from unittest.mock import Mock, patch
from litecrew.processes.debate import DebateProcess
from litecrew.processes.panel import PanelProcess
from litecrew.agent import LiteAgent
from litecrew.task import Task


class TestDebateProcessCoverage:
    """Tests for DebateProcess to improve coverage."""
    
    def test_debate_assign_positions_with_role_moderator(self):
        """Test _assign_positions with moderator role."""
        process = DebateProcess()
        process.moderator_role = "moderator"  # Set moderator role
        
        # Mock agents
        agent1 = Mock(spec=LiteAgent)
        agent1.role = "moderator"
        agent2 = Mock(spec=LiteAgent)
        agent2.role = "debater"
        agent3 = Mock(spec=LiteAgent)
        agent3.role = "debater"
        agents = [agent1, agent2, agent3]
        
        # Assign positions
        positions = process._assign_debate_positions(agents)
        
        # Should assign moderator correctly
        assert positions["moderator"] == agent1
        assert positions["debaters"] == [agent2, agent3]
    
    def test_debate_assign_positions_without_moderator(self):
        """Test _assign_positions without moderator role."""
        process = DebateProcess()
        
        # Mock agents
        agent1 = Mock(spec=LiteAgent)
        agent1.role = "debater"
        agent2 = Mock(spec=LiteAgent)
        agent2.role = "debater"
        agents = [agent1, agent2]
        
        # Assign positions
        positions = process._assign_debate_positions(agents)
        
        # Should assign all as debaters
        assert "moderator" not in positions
        assert positions["debaters"] == [agent1, agent2]
    
    def test_debate_assign_positions_with_moderator_role_but_no_match(self):
        """Test _assign_positions with moderator role but no matching agent."""
        process = DebateProcess()
        process.moderator_role = "moderator"  # Set moderator role
        
        # Mock agents without moderator role
        agent1 = Mock(spec=LiteAgent)
        agent1.role = "debater"
        agent2 = Mock(spec=LiteAgent)
        agent2.role = "debater"
        agents = [agent1, agent2]
        
        # Assign positions
        positions = process._assign_debate_positions(agents)
        
        # Should assign all as debaters when no moderator found
        assert "moderator" not in positions
        assert positions["debaters"] == [agent1, agent2]

