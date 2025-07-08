"""Tests for tools to improve coverage."""

from unittest.mock import Mock
from litecrew.tools import DelegationTool


class TestDelegationToolCoverage:
    """Tests for DelegationTool to improve coverage."""
    
    def test_delegation_tool_init(self):
        """Test DelegationTool initialization."""
        # Create mock agents
        agent1 = Mock()
        agent1.role = "Researcher"
        agent2 = Mock()
        agent2.role = "Writer"
        
        tool = DelegationTool([agent1, agent2])
        
        assert tool.name == "delegate_task"
        assert "Researcher" in tool.description
        assert "Writer" in tool.description
    
    def test_delegation_successful(self):
        """Test successful delegation."""
        # Create mock agent
        agent = Mock()
        agent.role = "Researcher"
        agent.execute.return_value = "Research result"
        
        tool = DelegationTool([agent])
        
        result = tool.func("Ask the Researcher to find information about AI")
        
        assert "Delegation result from Researcher: Research result" in result
        agent.execute.assert_called_once_with("find information about ai")
    
    def test_delegation_agent_not_found(self):
        """Test delegation to non-existent agent."""
        agent = Mock()
        agent.role = "Researcher"
        
        tool = DelegationTool([agent])
        
        result = tool.func("Ask the Writer to write something")
        
        assert "Agent role 'Writer' not found" in result
        assert "Available agents: Researcher" in result
    
    def test_parse_delegation_ask_pattern(self):
        """Test parsing delegation with 'ask the' pattern."""
        agent = Mock()
        agent.role = "Researcher"
        
        tool = DelegationTool([agent])
        
        role, task = tool._parse_delegation("ask the researcher to find data")
        
        assert role == "Researcher"
        assert task == "find data"
    
    def test_parse_delegation_delegate_pattern(self):
        """Test parsing delegation with 'delegate to' pattern."""
        agent = Mock()
        agent.role = "Writer"
        
        tool = DelegationTool([agent])
        
        role, task = tool._parse_delegation("delegate to writer: write a report")
        
        assert role == "Writer"
        assert task == "write a report"
    
    def test_parse_delegation_have_pattern(self):
        """Test parsing delegation with 'have the' pattern."""
        agent = Mock()
        agent.role = "Analyst"
        
        tool = DelegationTool([agent])
        
        role, task = tool._parse_delegation("have the analyst analyze the data")
        
        assert role == "Analyst"
        assert task == "analyze the data"
    
    def test_parse_delegation_get_pattern(self):
        """Test parsing delegation with 'get the' pattern."""
        agent = Mock()
        agent.role = "Reviewer"
        
        tool = DelegationTool([agent])
        
        role, task = tool._parse_delegation("get the reviewer to review the document")
        
        assert role == "Reviewer"
        assert task == "review the document"
    
    def test_parse_delegation_fallback(self):
        """Test parsing delegation with fallback pattern."""
        agent = Mock()
        agent.role = "Helper"
        
        tool = DelegationTool([agent])
        
        role, task = tool._parse_delegation("helper do something")
        
        assert role == "Helper"
        assert task == "do something"
    
    def test_parse_delegation_single_word(self):
        """Test parsing delegation with single word."""
        agent = Mock()
        agent.role = "Agent"
        
        tool = DelegationTool([agent])
        
        role, task = tool._parse_delegation("help")
        
        assert role == "Unknown"
        assert task == "help"
    
    def test_agent_without_role(self):
        """Test agent without role attribute."""
        agent = Mock()
        # Don't set role attribute - Mock still has it, so remove it
        del agent.role
        
        tool = DelegationTool([agent])
        
        # Should use "Unknown" as role
        assert "Unknown" in tool.description