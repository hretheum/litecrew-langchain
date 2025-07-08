"""Comprehensive tests for ProcessPrompts module."""

import pytest
from litecrew.processes.prompts import ProcessPrompts, enhance_agent_for_process


class TestProcessPrompts:
    """Test ProcessPrompts class functionality."""
    
    def test_get_conversational_prompt(self):
        """Test getting conversational process prompts."""
        prompt = ProcessPrompts.get_prompt(
            "conversational",
            "introduction",
            agent_role="Test Agent",
            task_list="Task 1\nTask 2"
        )
        assert "Test Agent" in prompt
        assert "Task 1" in prompt
        assert "collaborative discussion" in prompt
        
    def test_get_debate_prompt(self):
        """Test getting debate process prompts."""
        prompt = ProcessPrompts.get_prompt(
            "debate",
            "opening_statement",
            agent_role="Debater",
            position="Pro",
            task_description="Test topic",
            stance="support",
            expected_output="Decision"
        )
        assert "Debater" in prompt
        assert "Pro" in prompt
        assert "Test topic" in prompt
        assert "support" in prompt
        
    def test_get_panel_prompt(self):
        """Test getting panel process prompts."""
        prompt = ProcessPrompts.get_prompt(
            "panel",
            "expert_opinion",
            agent_role="Expert",
            task_description="Test topic",
            expected_output="Recommendation",
            context="Additional context"
        )
        assert "Expert" in prompt
        assert "Test topic" in prompt
        assert "Additional context" in prompt
        
    def test_get_brainstorm_prompt(self):
        """Test getting brainstorm process prompts."""
        prompt = ProcessPrompts.get_prompt(
            "brainstorm",
            "ideation",
            agent_role="Creative",
            task_description="Innovation challenge",
            idea_count=5,
            ideas_per_turn=3
        )
        assert "Creative" in prompt
        assert "Innovation challenge" in prompt
        assert "5" in prompt
        assert "3" in prompt
        
    def test_get_prompt_invalid_process(self):
        """Test getting prompt for invalid process type."""
        with pytest.raises(ValueError, match="Unknown prompt"):
            ProcessPrompts.get_prompt("invalid_process", "test_prompt")
            
    def test_get_prompt_invalid_prompt_name(self):
        """Test getting invalid prompt name."""
        with pytest.raises(ValueError, match="Unknown prompt"):
            ProcessPrompts.get_prompt("conversational", "invalid_prompt")
            
    def test_get_prompt_missing_parameter(self):
        """Test getting prompt with missing parameters."""
        with pytest.raises(ValueError, match="Missing required parameter"):
            ProcessPrompts.get_prompt("conversational", "introduction")
            
    def test_get_process_instructions_conversational(self):
        """Test getting conversational process instructions."""
        instructions = ProcessPrompts.get_process_instructions("conversational")
        assert instructions["tone"] == "collaborative and friendly"
        assert "build on others' ideas" in instructions["goals"]
        assert "dominating conversation" in instructions["avoid"]
        assert "active listening" in instructions["techniques"]
        
    def test_get_process_instructions_debate(self):
        """Test getting debate process instructions."""
        instructions = ProcessPrompts.get_process_instructions("debate")
        assert instructions["tone"] == "formal and respectful"
        assert "present strong arguments" in instructions["goals"]
        assert "personal attacks" in instructions["avoid"]
        assert "evidence-based reasoning" in instructions["techniques"]
        
    def test_get_process_instructions_panel(self):
        """Test getting panel process instructions."""
        instructions = ProcessPrompts.get_process_instructions("panel")
        assert instructions["tone"] == "professional and expert"
        assert "share domain expertise" in instructions["goals"]
        assert "oversimplification" in instructions["avoid"]
        assert "drawing from experience" in instructions["techniques"]
        
    def test_get_process_instructions_brainstorm(self):
        """Test getting brainstorm process instructions."""
        instructions = ProcessPrompts.get_process_instructions("brainstorm")
        assert instructions["tone"] == "creative and energetic"
        assert "generate many ideas" in instructions["goals"]
        assert "criticism during ideation" in instructions["avoid"]
        assert "lateral thinking" in instructions["techniques"]
        
    def test_get_process_instructions_invalid(self):
        """Test getting instructions for invalid process type."""
        instructions = ProcessPrompts.get_process_instructions("invalid")
        assert instructions == {}
        
    def test_all_prompt_types_exist(self):
        """Test that all expected prompt types exist."""
        assert hasattr(ProcessPrompts, "CONVERSATIONAL")
        assert hasattr(ProcessPrompts, "DEBATE")
        assert hasattr(ProcessPrompts, "PANEL")
        assert hasattr(ProcessPrompts, "BRAINSTORM")
        
    def test_conversational_prompts_complete(self):
        """Test conversational prompts have all expected keys."""
        prompts = ProcessPrompts.CONVERSATIONAL
        expected_keys = ["introduction", "response", "summary"]
        for key in expected_keys:
            assert key in prompts
            
    def test_debate_prompts_complete(self):
        """Test debate prompts have all expected keys."""
        prompts = ProcessPrompts.DEBATE
        expected_keys = [
            "moderator_opening", "opening_statement", "argument", 
            "rebuttal", "closing_statement", "synthesis"
        ]
        for key in expected_keys:
            assert key in prompts
            
    def test_panel_prompts_complete(self):
        """Test panel prompts have all expected keys."""
        prompts = ProcessPrompts.PANEL
        expected_keys = [
            "introduction", "topic_intro", "expert_opinion", 
            "follow_up", "consensus", "vote_summary", "synthesis"
        ]
        for key in expected_keys:
            assert key in prompts
            
    def test_brainstorm_prompts_complete(self):
        """Test brainstorm prompts have all expected keys."""
        prompts = ProcessPrompts.BRAINSTORM
        expected_keys = ["kickoff", "ideation", "refinement"]
        for key in expected_keys:
            assert key in prompts


class TestEnhanceAgentForProcess:
    """Test enhance_agent_for_process function."""
    
    def test_enhance_agent_conversational(self):
        """Test enhancing agent for conversational process."""
        class MockAgent:
            def __init__(self):
                self.process_instructions = None
                self.process_role = None
                
        agent = MockAgent()
        enhance_agent_for_process(agent, "conversational", "facilitator")
        
        assert agent.process_instructions is not None
        assert "collaborative and friendly" in agent.process_instructions
        assert "build on others' ideas" in agent.process_instructions
        assert agent.process_role == "facilitator"
        
    def test_enhance_agent_debate(self):
        """Test enhancing agent for debate process."""
        class MockAgent:
            def __init__(self):
                self.process_instructions = None
                self.process_role = None
                
        agent = MockAgent()
        enhance_agent_for_process(agent, "debate", "moderator")
        
        assert agent.process_instructions is not None
        assert "formal and respectful" in agent.process_instructions
        assert "present strong arguments" in agent.process_instructions
        assert agent.process_role == "moderator"
        
    def test_enhance_agent_panel(self):
        """Test enhancing agent for panel process."""
        class MockAgent:
            def __init__(self):
                self.process_instructions = None
                self.process_role = None
                
        agent = MockAgent()
        enhance_agent_for_process(agent, "panel", "expert")
        
        assert agent.process_instructions is not None
        assert "professional and expert" in agent.process_instructions
        assert "share domain expertise" in agent.process_instructions
        assert agent.process_role == "expert"
        
    def test_enhance_agent_brainstorm(self):
        """Test enhancing agent for brainstorm process."""
        class MockAgent:
            def __init__(self):
                self.process_instructions = None
                self.process_role = None
                
        agent = MockAgent()
        enhance_agent_for_process(agent, "brainstorm", "ideator")
        
        assert agent.process_instructions is not None
        assert "creative and energetic" in agent.process_instructions
        assert "generate many ideas" in agent.process_instructions
        assert agent.process_role == "ideator"
        
    def test_enhance_agent_invalid_process(self):
        """Test enhancing agent for invalid process type."""
        class MockAgent:
            def __init__(self):
                self.process_instructions = None
                
        agent = MockAgent()
        enhance_agent_for_process(agent, "invalid_process")
        
        assert agent.process_instructions is None
        
    def test_enhance_agent_no_role(self):
        """Test enhancing agent without specific role."""
        class MockAgent:
            def __init__(self):
                self.process_instructions = None
                self.process_role = None
                
        agent = MockAgent()
        enhance_agent_for_process(agent, "conversational")
        
        assert agent.process_instructions is not None
        assert agent.process_role is None
        
    def test_enhance_agent_without_attributes(self):
        """Test enhancing agent that doesn't have process attributes."""
        class MockAgent:
            pass
            
        agent = MockAgent()
        # Should not raise error
        enhance_agent_for_process(agent, "conversational", "facilitator")
        
        # Should not have added attributes
        assert not hasattr(agent, "process_instructions")
        assert not hasattr(agent, "process_role")
        
    def test_enhance_agent_with_existing_instructions(self):
        """Test enhancing agent that already has process instructions."""
        class MockAgent:
            def __init__(self):
                self.process_instructions = "existing instructions"
                self.process_role = "existing role"
                
        agent = MockAgent()
        enhance_agent_for_process(agent, "debate", "new_role")
        
        # Should overwrite existing instructions
        assert "formal and respectful" in agent.process_instructions
        assert agent.process_role == "new_role"