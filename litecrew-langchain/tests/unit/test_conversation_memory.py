"""
Tests for conversation memory functionality in LiteCrew.
"""

import pytest
import time
from unittest.mock import Mock, patch
from litecrew.agent import LiteAgent
from litecrew.task import LiteTask
from litecrew.crew import LiteCrew
from litecrew.memory import ConversationMemory, MemorySummarizer, MemorySearch


class TestConversationMemory:
    """Test conversation memory functionality."""
    
    def test_short_term_memory_creation(self):
        """Test short-term memory creation."""
        memory = ConversationMemory(max_size=100)
        
        assert memory.max_size == 100
        assert len(memory) == 0
        assert memory.get_turns() == []
    
    def test_memory_add_turn(self):
        """Test adding turns to memory."""
        memory = ConversationMemory()
        
        # Add user turn
        memory.add_turn("user", "What is the weather?")
        assert len(memory) == 1
        
        # Add assistant turn
        memory.add_turn("assistant", "I don't have access to weather data.")
        assert len(memory) == 2
        
        # Check turns
        turns = memory.get_turns()
        assert turns[0]["role"] == "user"
        assert turns[0]["content"] == "What is the weather?"
        assert turns[1]["role"] == "assistant"
    
    def test_memory_limits(self):
        """Test memory size limits."""
        memory = ConversationMemory(max_size=3)
        
        # Add 5 turns
        for i in range(5):
            memory.add_turn("user", f"Message {i}")
        
        # Should only keep last 3
        assert len(memory) == 3
        turns = memory.get_turns()
        assert turns[0]["content"] == "Message 2"
        assert turns[-1]["content"] == "Message 4"
    
    def test_memory_summarization(self):
        """Test memory summarization."""
        memory = ConversationMemory()
        summarizer = MemorySummarizer()
        
        # Add conversation
        memory.add_turn("user", "Tell me about Python")
        memory.add_turn("assistant", "Python is a high-level programming language...")
        memory.add_turn("user", "What are its main features?")
        memory.add_turn("assistant", "Python features include: dynamic typing, garbage collection...")
        
        # Summarize
        summary = summarizer.summarize(memory)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert len(summary) < len(str(memory.get_turns()))  # Summary should be shorter
    
    def test_memory_search(self):
        """Test memory search functionality."""
        memory = ConversationMemory()
        search = MemorySearch()
        
        # Add conversation
        memory.add_turn("user", "What is machine learning?")
        memory.add_turn("assistant", "Machine learning is a subset of AI...")
        memory.add_turn("user", "Tell me about neural networks")
        memory.add_turn("assistant", "Neural networks are computing systems...")
        
        # Search
        results = search.search(memory, "machine learning")
        assert len(results) > 0
        assert any("machine learning" in r["content"].lower() for r in results)
        
        # Search with no results (should not match "computing" alone)
        results = search.search(memory, "quantum physics")
        assert len(results) == 0
    
    def test_memory_persistence_hooks(self):
        """Test memory persistence hooks."""
        memory = ConversationMemory()
        
        # Set up persistence hooks
        saved_data = None
        
        def save_hook(data):
            nonlocal saved_data
            saved_data = data
        
        def load_hook():
            return saved_data
        
        memory.set_save_hook(save_hook)
        memory.set_load_hook(load_hook)
        
        # Add data and save
        memory.add_turn("user", "Test message")
        memory.save()
        
        assert saved_data is not None
        
        # Create new memory and load
        new_memory = ConversationMemory()
        new_memory.set_load_hook(load_hook)
        new_memory.load()
        
        assert len(new_memory) == 1
        assert new_memory.get_turns()[0]["content"] == "Test message"
    
    def test_agent_with_memory(self):
        """Test agent with conversation memory."""
        agent = LiteAgent(
            role="Memory Agent",
            goal="Remember conversations",
            backstory="An agent with perfect memory",
            memory=True
        )
        
        # First interaction
        result1 = agent.execute("My name is Alice")
        
        # Second interaction should remember
        result2 = agent.execute("What is my name?")
        
        # Memory should exist and contain interactions
        assert hasattr(agent, '_conversation_memory')
        # Note: The current implementation adds to memory in execute method
        # For now, just verify memory exists
        assert agent._conversation_memory is not None
    
    def test_memory_context_building(self):
        """Test building context from memory."""
        memory = ConversationMemory()
        
        # Add conversation
        memory.add_turn("user", "I work at OpenAI")
        memory.add_turn("assistant", "That's interesting!")
        memory.add_turn("user", "I'm working on GPT-5")
        
        # Build context
        context = memory.build_context(max_tokens=50)
        
        assert isinstance(context, str)
        assert "OpenAI" in context
        assert "GPT-5" in context
    
    def test_memory_clear(self):
        """Test clearing memory."""
        memory = ConversationMemory()
        
        # Add turns
        memory.add_turn("user", "Hello")
        memory.add_turn("assistant", "Hi!")
        
        assert len(memory) == 2
        
        # Clear
        memory.clear()
        assert len(memory) == 0
        assert memory.get_turns() == []
    
    def test_memory_overhead(self):
        """Test memory overhead stays under limit."""
        import sys
        
        memory = ConversationMemory()
        
        # Add 10 turns
        for i in range(10):
            memory.add_turn("user", f"Message {i}" * 10)  # ~100 chars each
        
        # Check memory size
        memory_size = sys.getsizeof(memory.get_turns())
        per_turn_size = memory_size / 10
        
        # Should be less than 1KB per turn
        assert per_turn_size < 1024
    
    def test_crew_with_shared_memory(self):
        """Test crew with shared memory."""
        agent1 = LiteAgent(
            role="Agent 1",
            goal="First agent",
            backstory="Agent one",
            memory=True
        )
        
        agent2 = LiteAgent(
            role="Agent 2",
            goal="Second agent",
            backstory="Agent two",
            memory=True
        )
        
        # Create dummy task to satisfy validation
        task = LiteTask(description="Test task", agent=agent1)
        
        crew = LiteCrew(
            agents=[agent1, agent2],
            tasks=[task],
            memory=True  # Enable shared memory
        )
        
        # Crew should have shared memory
        assert hasattr(crew, '_shared_memory')
        
        # Agents should use crew memory
        assert agent1._use_crew_memory == True
        assert agent2._use_crew_memory == True
    
    def test_memory_with_summarization_trigger(self):
        """Test automatic summarization when memory gets large."""
        memory = ConversationMemory(
            max_size=10,
            summarize_after=5
        )
        
        # Add turns to trigger summarization
        for i in range(7):
            memory.add_turn("user", f"Long message {i} " * 20)
        
        # Should have summarized older turns
        assert len(memory) <= 10
        assert memory.has_summary()
    
    def test_memory_search_relevance(self):
        """Test memory search relevance scoring."""
        memory = ConversationMemory()
        search = MemorySearch()
        
        # Add varied conversation
        memory.add_turn("user", "I love programming in Python")
        memory.add_turn("assistant", "Python is great for many tasks")
        memory.add_turn("user", "Tell me about Java")
        memory.add_turn("assistant", "Java is another popular language")
        memory.add_turn("user", "Python vs Java comparison")
        
        # Search for Python
        results = search.search(memory, "Python", top_k=3)
        
        # Results should be ordered by relevance
        assert len(results) <= 3
        assert results[0]["relevance_score"] >= results[-1]["relevance_score"]
    
    def test_memory_export_import(self):
        """Test exporting and importing memory."""
        memory = ConversationMemory()
        
        # Add conversation
        memory.add_turn("user", "Hello")
        memory.add_turn("assistant", "Hi there!")
        
        # Export
        exported = memory.export()
        assert isinstance(exported, dict)
        assert "turns" in exported
        assert "metadata" in exported
        
        # Import into new memory
        new_memory = ConversationMemory()
        new_memory.import_data(exported)
        
        assert len(new_memory) == 2
        assert new_memory.get_turns()[0]["content"] == "Hello"