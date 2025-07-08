"""Tests for agent behaviors to improve coverage."""

import pytest
from litecrew.agent_types.behaviors import ModerationBehavior, ConversationalBehavior


class TestModerationBehaviorCoverage:
    """Tests for ModerationBehavior to improve coverage."""
    
    def test_modify_response_strict_style_without_next(self):
        """Test modify_response with strict style and no 'next' in response."""
        behavior = ModerationBehavior()
        behavior.style = "strict"
        
        response = "This is a response without the word."
        context = {}
        
        result = behavior.modify_response(response, context)
        
        assert "Now, let's move to the next point in our agenda." in result
    
    def test_modify_response_balanced_style_with_redirection(self):
        """Test modify_response with balanced style and needs_redirection."""
        behavior = ModerationBehavior()
        behavior.style = "balanced"
        
        response = "This is a response."
        context = {"needs_redirection": True}
        
        result = behavior.modify_response(response, context)
        
        assert "Perhaps we could refocus on the main topic at hand." in result


class TestConversationalBehaviorCoverage:
    """Tests for ConversationalBehavior to improve coverage."""
    
    def test_modify_response_friendly_style_without_great(self):
        """Test modify_response with friendly style and no 'great' in response."""
        behavior = ConversationalBehavior()
        behavior.style = "friendly"
        
        response = "This is a response."
        context = {}
        
        result = behavior.modify_response(response, context)
        
        assert "That's an interesting point!" in result
    
    def test_modify_response_casual_style_without_i_think(self):
        """Test modify_response with casual style and no 'I think' in response."""
        behavior = ConversationalBehavior()
        behavior.style = "casual"
        
        response = "It is a good idea."
        context = {}
        
        result = behavior.modify_response(response, context)
        
        assert "I think it's" in result
        assert "It is" not in result