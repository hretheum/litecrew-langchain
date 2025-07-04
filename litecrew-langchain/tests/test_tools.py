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

    def test_delegation_parsing_comprehensive(self):
        """Test comprehensive delegation parsing patterns."""
        from litecrew.tools import DelegationTool
        
        # Test parsing without initialization issues
        tool_class = DelegationTool.__new__(DelegationTool)
        
        test_cases = [
            ("ask the researcher to find data", ("Researcher", "find data")),
            ("delegate to writer: create content", ("Writer", "create content")),
            ("have the analyst analyze trends", ("Analyst", "analyze trends")),
            ("get the designer to create mockups", ("Designer", "create mockups")),
            ("ASK THE researcher TO find INFO", ("Researcher", "find info")),
            ("Developer fix the bug", ("Developer", "fix the bug")),
            ("help", ("Unknown", "help"))
        ]
        
        for query, expected in test_cases:
            role, task = tool_class._parse_delegation(query)
            assert role == expected[0], f"Failed for query: {query}"
            assert task == expected[1], f"Failed for query: {query}"

    def test_tool_creation_basic(self):
        """Test basic tool creation without complex mock setup."""
        # Just test that we can create a tool with simple mock agents
        from litecrew.tools import DelegationTool
        from unittest.mock import Mock
        
        # Simple mock that just has a role attribute
        mock_agent = Mock()
        mock_agent.role = "TestAgent"
        
        # This should work without issues
        tool = DelegationTool([mock_agent])
        
        # Verify basic properties
        assert tool.name == "delegate_task"
        assert "TestAgent" in tool.description
        assert "Delegate a task to another agent" in tool.description

    def test_regex_patterns_comprehensive(self):
        """Test all regex patterns in isolation."""
        from litecrew.tools import DelegationTool
        import re
        
        patterns = [
            r"ask the (\w+) to (.+)",
            r"delegate to (\w+): (.+)",
            r"have the (\w+) (.+)",
            r"get the (\w+) to (.+)",
        ]
        
        test_queries = [
            ("ask the researcher to find data", "researcher", "find data"),
            ("delegate to writer: create story", "writer", "create story"),
            ("have the analyst review data", "analyst", "review data"),
            ("get the designer to create ui", "designer", "create ui"),
        ]
        
        for query, expected_role, expected_task in test_queries:
            matched = False
            for pattern in patterns:
                match = re.match(pattern, query.lower())
                if match:
                    role = match.group(1).title()
                    task = match.group(2)
                    assert role == expected_role.title()
                    assert task == expected_task
                    matched = True
                    break
            assert matched, f"No pattern matched query: {query}"

    def test_delegate_method_success(self):
        """Test successful delegation execution."""
        from litecrew.tools import DelegationTool
        from unittest.mock import Mock
        
        # Create mock agents
        agent1 = Mock()
        agent1.role = "Researcher"
        agent1.execute = Mock(return_value="Research results about AI")
        
        agent2 = Mock()
        agent2.role = "Writer"
        agent2.execute = Mock(return_value="Written article about AI")
        
        # Create tool
        tool = DelegationTool([agent1, agent2])
        
        # Test delegation to researcher
        result = tool._delegate("Ask the Researcher to find information about AI")
        assert result == "Delegation result from Researcher: Research results about AI"
        agent1.execute.assert_called_once_with("find information about ai")
        
        # Test delegation to writer
        result = tool._delegate("Ask the Writer to write about AI")
        assert result == "Delegation result from Writer: Written article about AI"
        agent2.execute.assert_called_once_with("write about ai")

    def test_delegate_method_unknown_agent(self):
        """Test delegation to unknown agent."""
        from litecrew.tools import DelegationTool
        from unittest.mock import Mock
        
        # Create mock agent
        agent = Mock()
        agent.role = "Researcher"
        
        # Create tool
        tool = DelegationTool([agent])
        
        # Test delegation to unknown agent
        result = tool._delegate("Ask the Writer to write something")
        assert "Agent role 'Writer' not found" in result
        assert "Available agents: Researcher" in result

    def test_delegate_method_various_patterns(self):
        """Test delegation with various query patterns."""
        from litecrew.tools import DelegationTool
        from unittest.mock import Mock
        
        # Create mock agent
        agent = Mock()
        agent.role = "Analyst"
        agent.execute = Mock(return_value="Analysis complete")
        
        # Create tool
        tool = DelegationTool([agent])
        
        # Test different patterns
        test_patterns = [
            "delegate to analyst: analyze the data",
            "have the analyst review metrics",
            "get the analyst to check performance"
        ]
        
        for pattern in test_patterns:
            result = tool._delegate(pattern)
            assert result == "Delegation result from Analyst: Analysis complete"
            assert agent.execute.called

    def test_delegate_method_fallback_parsing(self):
        """Test delegation with fallback parsing."""
        from litecrew.tools import DelegationTool
        from unittest.mock import Mock
        
        # Create mock agent
        agent = Mock()
        agent.role = "Developer"
        agent.execute = Mock(return_value="Bug fixed")
        
        # Create tool
        tool = DelegationTool([agent])
        
        # Test fallback pattern (simple space-separated)
        result = tool._delegate("Developer fix the critical bug")
        assert result == "Delegation result from Developer: Bug fixed"
        agent.execute.assert_called_with("fix the critical bug")

    def test_tool_as_langchain_tool(self):
        """Test DelegationTool works as a langchain Tool."""
        from litecrew.tools import DelegationTool
        from unittest.mock import Mock
        
        # Create mock agent
        agent = Mock()
        agent.role = "Tester"
        agent.execute = Mock(return_value="Tests passed")
        
        # Create tool
        tool = DelegationTool([agent])
        
        # Test using the tool's func method (like langchain would)
        result = tool.func("Ask the Tester to run the test suite")
        assert result == "Delegation result from Tester: Tests passed"
        
        # Verify tool metadata
        assert tool.name == "delegate_task"
        assert callable(tool.func)