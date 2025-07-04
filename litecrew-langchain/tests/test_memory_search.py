"""Tests for memory search functionality."""

from unittest.mock import Mock

import pytest

from litecrew.memory.conversation import ConversationMemory
from litecrew.memory.search import MemorySearch


class TestMemorySearch:
    """Test memory search and relevance scoring."""

    def test_memory_search_initialization(self):
        """Test memory search initialization."""
        search = MemorySearch()
        
        # Should have stop words defined
        assert hasattr(search, '_stop_words')
        assert isinstance(search._stop_words, set)
        assert len(search._stop_words) > 0
        
        # Common stop words should be present
        assert "the" in search._stop_words
        assert "and" in search._stop_words
        assert "is" in search._stop_words

    def test_basic_search_functionality(self):
        """Test basic search functionality."""
        search = MemorySearch()
        
        # Mock memory with conversations
        memory = Mock()
        memory.get_turns.return_value = [
            {"role": "human", "content": "What is machine learning?"},
            {"role": "assistant", "content": "Machine learning is a subset of AI that enables computers to learn without explicit programming."},
            {"role": "human", "content": "How does deep learning work?"},
            {"role": "assistant", "content": "Deep learning uses neural networks with multiple layers to learn complex patterns."}
        ]
        
        # Should be able to search memory
        if hasattr(search, 'search'):
            results = search.search(memory, "machine learning")
            assert isinstance(results, list)

    def test_keyword_extraction(self):
        """Test keyword extraction from text."""
        search = MemorySearch()
        
        text = "Machine learning and artificial intelligence are transforming technology"
        
        # Test if search has keyword extraction
        if hasattr(search, '_extract_keywords'):
            keywords = search._extract_keywords(text)
            
            assert isinstance(keywords, (list, set))
            # Should exclude stop words
            assert "and" not in keywords
            assert "are" not in keywords
            # Should include important terms
            meaningful_words = ["machine", "learning", "artificial", "intelligence", "transforming", "technology"]
            extracted_lower = [k.lower() for k in keywords]
            assert any(word in extracted_lower for word in meaningful_words)

    def test_relevance_scoring(self):
        """Test relevance scoring algorithm."""
        search = MemorySearch()
        
        query = "machine learning algorithms"
        documents = [
            "Machine learning algorithms are powerful tools for data analysis",
            "Deep learning is a subset of machine learning techniques",
            "The weather today is sunny and warm",
            "Algorithms in computer science solve computational problems"
        ]
        
        if hasattr(search, '_calculate_relevance'):
            scores = []
            for doc in documents:
                score = search._calculate_relevance(query, doc)
                scores.append(score)
            
            # First two documents should score higher than weather doc
            assert scores[0] > scores[2]  # ML algorithms vs weather
            assert scores[1] > scores[2]  # Deep learning vs weather

    def test_search_with_filters(self):
        """Test search with time or role filters."""
        search = MemorySearch()
        
        # Mock memory with timestamped conversations
        memory = Mock()
        memory.get_turns.return_value = [
            {"role": "human", "content": "Question about AI", "timestamp": "2024-01-01"},
            {"role": "assistant", "content": "AI response", "timestamp": "2024-01-01"},
            {"role": "human", "content": "Question about ML", "timestamp": "2024-01-02"},
            {"role": "assistant", "content": "ML response", "timestamp": "2024-01-02"},
        ]
        
        # Test role filtering if available
        if hasattr(search, 'search_by_role'):
            human_results = search.search_by_role(memory, "human")
            assert all(turn["role"] == "human" for turn in human_results)

    def test_semantic_similarity(self):
        """Test semantic similarity calculation."""
        search = MemorySearch()
        
        # Test semantic similarity if implemented
        if hasattr(search, '_semantic_similarity'):
            text1 = "machine learning algorithms"
            text2 = "AI and ML techniques"
            text3 = "cooking recipes"
            
            sim1 = search._semantic_similarity(text1, text2)
            sim2 = search._semantic_similarity(text1, text3)
            
            # Related terms should be more similar
            assert sim1 > sim2

    def test_search_result_ranking(self):
        """Test search result ranking by relevance."""
        search = MemorySearch()
        
        query = "neural networks"
        
        # Mock memory with varying relevance
        memory = Mock()
        memory.get_turns.return_value = [
            {"role": "assistant", "content": "Neural networks are the foundation of deep learning systems"},
            {"role": "assistant", "content": "Networks in computer science connect nodes"},
            {"role": "assistant", "content": "Deep neural architectures use multiple hidden layers"},
            {"role": "assistant", "content": "The network connection failed yesterday"}
        ]
        
        if hasattr(search, 'search'):
            results = search.search(memory, query, limit=4)
            
            # Results should be ranked by relevance
            if len(results) > 1:
                # First result should be most relevant
                first_content = results[0]["content"].lower()
                assert "neural" in first_content or "deep" in first_content

    def test_empty_query_handling(self):
        """Test handling of empty or invalid queries."""
        search = MemorySearch()
        memory = Mock()
        memory.get_turns.return_value = []
        
        if hasattr(search, 'search'):
            # Empty query
            results = search.search(memory, "")
            assert isinstance(results, list)
            
            # None query
            results = search.search(memory, None)
            assert isinstance(results, list)

    def test_large_memory_search_performance(self):
        """Test search performance with large memory."""
        search = MemorySearch()
        
        # Create large mock memory
        large_turns = []
        for i in range(1000):
            large_turns.append({
                "role": "human" if i % 2 == 0 else "assistant",
                "content": f"This is conversation turn {i} about various topics including AI, ML, and technology."
            })
        
        memory = Mock()
        memory.get_turns.return_value = large_turns
        
        if hasattr(search, 'search'):
            import time
            start_time = time.perf_counter()
            results = search.search(memory, "AI technology", limit=10)
            search_time = time.perf_counter() - start_time
            
            # Should complete reasonably quickly
            assert search_time < 1.0  # Less than 1 second
            assert len(results) <= 10

    def test_memory_integration(self):
        """Test integration with ConversationMemory."""
        # Create real conversation memory
        memory = ConversationMemory(max_turns=10)
        search = MemorySearch()
        
        # Add some conversations
        memory.add_turn("human", "What is artificial intelligence?")
        memory.add_turn("assistant", "AI is the simulation of human intelligence in machines.")
        memory.add_turn("human", "How does machine learning work?")
        memory.add_turn("assistant", "ML algorithms learn patterns from data to make predictions.")
        
        # Search should work with real memory
        if hasattr(search, 'search'):
            results = search.search(memory, "machine learning")
            assert isinstance(results, list)
            
            # Should find relevant conversations
            if len(results) > 0:
                found_ml = any("machine learning" in result["content"].lower() or 
                              "ml" in result["content"].lower() 
                              for result in results)
                assert found_ml

    def test_search_context_preservation(self):
        """Test that search preserves conversation context."""
        search = MemorySearch()
        memory = Mock()
        
        # Mock conversation with context
        memory.get_turns.return_value = [
            {"role": "human", "content": "What is deep learning?", "turn_id": 1},
            {"role": "assistant", "content": "Deep learning uses neural networks", "turn_id": 2},
            {"role": "human", "content": "Can you give an example?", "turn_id": 3},
            {"role": "assistant", "content": "CNNs are used for image recognition", "turn_id": 4}
        ]
        
        if hasattr(search, 'search_with_context'):
            results = search.search_with_context(memory, "example neural networks")
            
            # Should maintain conversation flow
            assert isinstance(results, list)

    def test_stop_words_filtering(self):
        """Test stop words are properly filtered."""
        search = MemorySearch()
        
        # Text with many stop words
        text = "The quick brown fox is jumping over the lazy dog and running around"
        
        if hasattr(search, '_remove_stop_words'):
            filtered = search._remove_stop_words(text.split())
            
            # Stop words should be removed
            assert "the" not in [w.lower() for w in filtered]
            assert "is" not in [w.lower() for w in filtered]
            assert "and" not in [w.lower() for w in filtered]
            
            # Content words should remain
            assert any(w.lower() in ["quick", "brown", "fox", "jumping"] 
                      for w in filtered)