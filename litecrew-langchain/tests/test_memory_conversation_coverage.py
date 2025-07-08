"""Tests for conversation memory to improve coverage."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from litecrew.memory.conversation import ConversationMemory


class TestConversationMemoryCoverage:
    """Tests for ConversationMemory to improve coverage."""
    
    def test_get_turns_with_last_n(self):
        """Test get_turns with last_n parameter."""
        memory = ConversationMemory()
        
        # Add some turns
        memory.add_turn("user", "First message")
        memory.add_turn("assistant", "First response")
        memory.add_turn("user", "Second message")
        memory.add_turn("assistant", "Second response")
        
        # Get last 2 turns
        turns = memory.get_turns(last_n=2)
        
        assert len(turns) == 2
        assert turns[0]["content"] == "Second message"
        assert turns[1]["content"] == "Second response"
    
    def test_build_context_with_summary(self):
        """Test build_context with summary."""
        memory = ConversationMemory()
        
        # Set summary
        memory.set_summary("Previous conversation about weather")
        
        # Add some turns
        memory.add_turn("user", "Hello")
        memory.add_turn("assistant", "Hi there!")
        
        context = memory.build_context()
        
        # Should include summary
        assert "Previous conversation summary: Previous conversation about weather" in context
        assert "user: Hello" in context
        assert "assistant: Hi there!" in context
    
    def test_build_context_with_max_tokens(self):
        """Test build_context with max_tokens truncation."""
        memory = ConversationMemory()
        
        # Add long content
        long_message = "A" * 1000
        memory.add_turn("user", long_message)
        memory.add_turn("assistant", "B" * 1000)
        
        # Build context with token limit
        context = memory.build_context(max_tokens=100)
        
        # Should be truncated (max_tokens * 4 = 400 chars)
        assert len(context) <= 400
    
    def test_build_context_truncation_with_newline_finding(self):
        """Test build_context truncation with newline finding."""
        memory = ConversationMemory()
        
        # Add content with newlines
        memory.add_turn("user", "Line 1\nLine 2\nLine 3")
        memory.add_turn("assistant", "Response 1\nResponse 2")
        
        # Build context with small token limit
        context = memory.build_context(max_tokens=10)  # 40 chars max
        
        # Should be truncated and find first complete turn
        assert len(context) <= 40
    
    def test_build_context_truncation_no_newline(self):
        """Test build_context truncation when no newline found."""
        memory = ConversationMemory()
        
        # Add content without newlines
        memory.add_turn("user", "A" * 200)
        memory.add_turn("assistant", "B" * 200)
        
        # Build context with token limit
        context = memory.build_context(max_tokens=50)  # 200 chars max
        
        # Should be truncated
        assert len(context) <= 200
    
    def test_build_context_truncation_with_newline_at_position_0(self):
        """Test build_context truncation when newline found at position 0."""
        memory = ConversationMemory()
        
        # Add content that will result in newline at position 0 after truncation
        memory.add_turn("user", "A" * 100)
        memory.add_turn("assistant", "\nB" * 100)  # Newline at beginning
        
        # Build context with token limit that will find newline at position 0
        context = memory.build_context(max_tokens=20)  # 80 chars max
        
        # Should be truncated but not further processed due to newline at position 0
        assert len(context) <= 80
    
    def test_search_with_matches(self):
        """Test search with matching content."""
        memory = ConversationMemory()
        
        # Add some turns
        memory.add_turn("user", "What is the weather like?")
        memory.add_turn("assistant", "The weather is sunny today")
        memory.add_turn("user", "Tell me about cats")
        memory.add_turn("assistant", "Cats are wonderful pets")
        
        # Search for weather
        results = memory.search("weather")
        
        assert len(results) == 2
        assert "weather" in results[0]["content"].lower()
        assert "weather" in results[1]["content"].lower()
    
    def test_search_with_no_matches(self):
        """Test search with no matching content."""
        memory = ConversationMemory()
        
        # Add some turns
        memory.add_turn("user", "Hello")
        memory.add_turn("assistant", "Hi there!")
        
        # Search for non-existent content
        results = memory.search("nonexistent")
        
        assert len(results) == 0
    
    def test_search_case_insensitive(self):
        """Test search is case insensitive."""
        memory = ConversationMemory()
        
        # Add turn with mixed case
        memory.add_turn("user", "Hello WORLD")
        
        # Search with different case
        results = memory.search("hello")
        
        assert len(results) == 1
        assert results[0]["content"] == "Hello WORLD"
        
        results = memory.search("HELLO")
        assert len(results) == 1
        
        results = memory.search("world")
        assert len(results) == 1
    
    def test_get_summary(self):
        """Test get_summary method."""
        memory = ConversationMemory()
        
        # Initially no summary
        assert memory.get_summary() is None
        
        # Set summary
        memory.set_summary("Test summary")
        
        # Should return summary
        assert memory.get_summary() == "Test summary"
    
    def test_set_summary(self):
        """Test set_summary method."""
        memory = ConversationMemory()
        
        # Set summary
        memory.set_summary("New summary")
        
        # Should be set
        assert memory._summary == "New summary"
        assert memory.get_summary() == "New summary"
    
    def test_get_memory_stats_with_turns(self):
        """Test get_memory_stats with turns."""
        memory = ConversationMemory(max_size=100)
        
        # Add some turns
        memory.add_turn("user", "First")
        memory.add_turn("assistant", "Second")
        memory.set_summary("Test summary")
        
        stats = memory.get_memory_stats()
        
        assert stats["turn_count"] == 2
        assert stats["max_size"] == 100
        assert stats["has_summary"] is True
        assert stats["oldest_turn"] is not None
        assert stats["newest_turn"] is not None
        assert "metadata" in stats
    
    def test_get_memory_stats_empty(self):
        """Test get_memory_stats with empty memory."""
        memory = ConversationMemory()
        
        stats = memory.get_memory_stats()
        
        assert stats["turn_count"] == 0
        assert stats["has_summary"] is False
        assert stats["oldest_turn"] is None
        assert stats["newest_turn"] is None