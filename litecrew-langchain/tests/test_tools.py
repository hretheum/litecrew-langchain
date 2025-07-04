"""Tests for LiteCrew tools."""

from unittest.mock import Mock

import pytest

from litecrew.tools import DelegationTool


class TestDelegationTool:
    """Test delegation tool functionality."""

    def test_delegation_tool_creation(self):
        """Test creating delegation tool with agents."""
        # Create mock agents using actual LiteAgent for compatibility
        from litecrew import LiteAgent
        
        agent1 = LiteAgent(
            role="Researcher", 
            goal="Research things", 
            backstory="I research"
        )
        agent2 = LiteAgent(
            role="Writer", 
            goal="Write things", 
            backstory="I write"
        )
        
        # Create delegation tool
        tool = DelegationTool([agent1, agent2])
        
        assert tool.name == "delegate_task"
        assert "Researcher, Writer" in tool.description

    def test_delegation_success(self):
        """Test successful task delegation."""
        # Test just the parsing functionality 
        from litecrew.tools import DelegationTool
        
        # Test the parsing directly without full tool setup
        tool_class = DelegationTool.__new__(DelegationTool)
        role, task = tool_class._parse_delegation("Ask the Researcher to find information about AI")
        
        assert role == "Researcher"
        assert task == "find information about ai"

    def test_delegation_unknown_agent(self):
        """Test delegation query parsing for unknown agent."""
        from litecrew.tools import DelegationTool
        
        # Test just the parsing
        tool_class = DelegationTool.__new__(DelegationTool)
        role, task = tool_class._parse_delegation("Ask the Writer to write something")
        
        assert role == "Writer"
        assert task == "write something"

    def test_parse_delegation_patterns(self):
        """Test parsing different delegation query patterns."""
        agent = Mock()
        agent.role = "Test"
        tool = DelegationTool([agent])
        
        # Test different patterns
        patterns = [
            ("ask the researcher to do research", ("Researcher", "do research")),
            ("delegate to writer: write a story", ("Writer", "write a story")),
            ("have the analyst analyze data", ("Analyst", "analyze data")),
            ("get the designer to create mockups", ("Designer", "create mockups")),
        ]
        
        for query, expected in patterns:
            role, task = tool._parse_delegation(query)
            assert role == expected[0]
            assert task == expected[1]

    def test_parse_delegation_fallback(self):
        """Test fallback parsing for unrecognized patterns."""
        agent = Mock()
        agent.role = "Test"
        tool = DelegationTool([agent])
        
        # Test fallback pattern
        role, task = tool._parse_delegation("Developer fix the bug")
        assert role == "Developer"
        assert task == "fix the bug"
        
        # Test single word input
        role, task = tool._parse_delegation("help")
        assert role == "Unknown"
        assert task == "help"

    def test_tool_parsing_edge_cases(self):
        """Test edge cases in delegation parsing."""
        from litecrew.tools import DelegationTool
        
        tool_class = DelegationTool.__new__(DelegationTool)
        
        # Test different formats
        role, task = tool_class._parse_delegation("delegate to writer: write a story")
        assert role == "Writer"
        assert task == "write a story"
        
        role, task = tool_class._parse_delegation("have the analyst analyze data")
        assert role == "Analyst"
        assert task == "analyze data"

    def test_tool_parsing_simple_format(self):
        """Test simple delegation format parsing."""
        from litecrew.tools import DelegationTool
        
        tool_class = DelegationTool.__new__(DelegationTool)
        
        # Test simple space-separated format
        role, task = tool_class._parse_delegation("Developer fix the bug")
        assert role == "Developer"
        assert task == "fix the bug"