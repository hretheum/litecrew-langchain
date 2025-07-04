"""Comprehensive tests for memory search functionality."""

import pytest
from litecrew.memory.conversation import ConversationMemory
from litecrew.memory.search import MemorySearch


class TestMemorySearchComprehensive:
    """Comprehensive tests for MemorySearch class."""

    @pytest.fixture
    def search(self):
        """Create MemorySearch instance."""
        return MemorySearch()

    @pytest.fixture
    def populated_memory(self):
        """Create memory with sample conversations."""
        memory = ConversationMemory(max_size=20)
        
        # Add sample conversations
        memory.add_turn("user", "What is machine learning?")
        memory.add_turn("assistant", "Machine learning is a subset of AI that enables computers to learn from data.")
        memory.add_turn("user", "How does deep learning differ from traditional ML?")
        memory.add_turn("assistant", "Deep learning uses neural networks with multiple layers to automatically learn hierarchical representations.")
        memory.add_turn("user", "Can you explain neural networks?")
        memory.add_turn("assistant", "Neural networks are computing systems inspired by biological neural networks in animal brains.")
        memory.add_turn("user", "What about reinforcement learning?")
        memory.add_turn("assistant", "Reinforcement learning is where agents learn to make decisions by receiving rewards or penalties.")
        memory.add_turn("user", "Tell me about natural language processing")
        memory.add_turn("assistant", "NLP is a field focused on enabling computers to understand and process human language.")
        
        return memory

    def test_search_basic(self, search, populated_memory):
        """Test basic search functionality."""
        # Search for machine learning
        results = search.search(populated_memory, "machine learning")
        assert len(results) > 0
        assert results[0]["relevance_score"] > 0
        assert "machine learning" in results[0]["content"].lower()
        
        # Search with empty query
        results = search.search(populated_memory, "")
        assert len(results) == 0
        
        # Search with stop words only
        results = search.search(populated_memory, "the and is")
        assert len(results) == 0

    def test_search_with_top_k(self, search, populated_memory):
        """Test search with top_k limit."""
        # Search with top_k
        results = search.search(populated_memory, "learning", top_k=3)
        assert len(results) <= 3
        
        # Verify results are sorted by relevance
        for i in range(len(results) - 1):
            assert results[i]["relevance_score"] >= results[i + 1]["relevance_score"]

    def test_search_with_min_score(self, search, populated_memory):
        """Test search with minimum score threshold."""
        # Search with high min_score
        results = search.search(populated_memory, "learning", min_score=0.8)
        
        # All results should meet threshold
        for result in results:
            assert result["relevance_score"] >= 0.8

    def test_semantic_search(self, search, populated_memory):
        """Test semantic search with context."""
        results = search.semantic_search(populated_memory, "neural networks", context_window=1)
        
        assert len(results) > 0
        
        # Check structure
        first_result = results[0]
        assert "matched_turn" in first_result
        assert "context_turns" in first_result
        assert "relevance_score" in first_result
        
        # Context turns should be marked
        for context_turn in first_result["context_turns"]:
            assert context_turn["is_context"] is True
            assert "distance_from_match" in context_turn

    def test_semantic_search_empty_results(self, search, populated_memory):
        """Test semantic search with no matches."""
        results = search.semantic_search(populated_memory, "quantum physics xyz123")
        assert len(results) == 0

    def test_find_related_turns(self, search, populated_memory):
        """Test finding related turns."""
        # Find turns related to the first machine learning turn
        related = search.find_related_turns(populated_memory, 0, max_related=3)
        
        assert len(related) <= 3
        
        # Each related turn should have required fields
        for turn in related:
            assert "relevance_score" in turn
            assert "turn_index" in turn
            assert "relation_type" in turn
            assert turn["turn_index"] != 0  # Should not include the target turn

    def test_find_related_turns_invalid_index(self, search, populated_memory):
        """Test find_related_turns with invalid index."""
        # Index beyond memory size
        related = search.find_related_turns(populated_memory, 999)
        assert len(related) == 0

    def test_find_related_turns_empty_content(self, search):
        """Test find_related_turns when target has no meaningful content."""
        memory = ConversationMemory(max_size=5)
        memory.add_turn("user", "the and is")  # Only stop words
        memory.add_turn("assistant", "Machine learning is powerful")
        
        related = search.find_related_turns(memory, 0)
        assert len(related) == 0

    def test_tokenize(self, search):
        """Test tokenization method."""
        # Test basic tokenization
        tokens = search._tokenize("Hello, world! This is a test-case.")
        assert "Hello" in tokens
        assert "world" in tokens
        assert "This" in tokens
        assert "is" in tokens
        assert "test" in tokens
        assert "case" in tokens
        
        # Test single character removal
        tokens = search._tokenize("a b c testing")
        assert "a" not in tokens
        assert "b" not in tokens
        assert "c" not in tokens
        assert "testing" in tokens

    def test_score_turn(self, search):
        """Test turn scoring method."""
        turn = {"role": "user", "content": "Machine learning and deep learning are AI techniques"}
        
        # Test exact match scoring
        score1 = search._score_turn(turn, ["machine", "learning"])
        assert score1 > 0
        
        # Test partial match
        score2 = search._score_turn(turn, ["mach", "learn"])
        assert score2 > 0
        
        # Test no match
        score3 = search._score_turn(turn, ["quantum", "physics"])
        assert score3 < score1
        
        # Test empty content
        empty_turn = {"role": "user", "content": ""}
        score4 = search._score_turn(empty_turn, ["test"])
        assert score4 == 0.0

    def test_score_turn_role_weighting(self, search):
        """Test role weighting in scoring."""
        user_turn = {"role": "user", "content": "machine learning"}
        assistant_turn = {"role": "assistant", "content": "machine learning"}
        
        user_score = search._score_turn(user_turn, ["machine", "learning"])
        assistant_score = search._score_turn(assistant_turn, ["machine", "learning"])
        
        # User turns should score higher
        assert user_score > assistant_score

    def test_determine_relation_type(self, search):
        """Test relation type determination."""
        # Question-answer pair
        question = {"role": "user", "content": "What is AI?"}
        answer = {"role": "assistant", "content": "AI is artificial intelligence"}
        
        relation = search._determine_relation_type(question, answer)
        assert relation == "answer"
        
        # Follow-up question
        statement = {"role": "assistant", "content": "AI is powerful"}
        followup = {"role": "user", "content": "How does it work?"}
        
        relation = search._determine_relation_type(statement, followup)
        assert relation == "follow_up_question"
        
        # Topic continuation
        turn1 = {"role": "user", "content": "Machine learning uses algorithms to learn patterns"}
        turn2 = {"role": "assistant", "content": "These patterns help in making predictions"}
        
        relation = search._determine_relation_type(turn1, turn2)
        assert relation == "topic_continuation"
        
        # Default related
        turn3 = {"role": "user", "content": "Hello"}
        turn4 = {"role": "assistant", "content": "Goodbye"}
        
        relation = search._determine_relation_type(turn3, turn4)
        assert relation == "related"

    def test_get_search_stats(self, search):
        """Test search statistics method."""
        stats = search.get_search_stats()
        
        assert "stop_words_count" in stats
        assert stats["stop_words_count"] == len(search._stop_words)
        assert "search_algorithm" in stats
        assert "features" in stats
        assert isinstance(stats["features"], list)
        assert len(stats["features"]) > 0

    def test_complex_search_scenario(self, search):
        """Test complex search scenario with mixed content."""
        memory = ConversationMemory(max_size=50)
        
        # Add varied conversations
        memory.add_turn("user", "Tell me about Python programming")
        memory.add_turn("assistant", "Python is a high-level programming language")
        memory.add_turn("user", "What frameworks are popular?")
        memory.add_turn("assistant", "Django and Flask for web, TensorFlow for ML")
        memory.add_turn("user", "Speaking of ML, how does TensorFlow compare to PyTorch?")
        memory.add_turn("assistant", "Both are deep learning frameworks with different design philosophies")
        
        # Search for frameworks
        results = search.search(memory, "frameworks", top_k=5)
        assert len(results) > 0
        
        # Should find both mentions
        contents = [r["content"] for r in results]
        framework_mentions = sum(1 for c in contents if "framework" in c.lower())
        assert framework_mentions >= 2

    def test_search_with_special_characters(self, search):
        """Test search handles special characters properly."""
        memory = ConversationMemory(max_size=10)
        memory.add_turn("user", "What about C++ and C#?")
        memory.add_turn("assistant", "C++ is lower-level, C# is managed")
        memory.add_turn("user", "And F#?")
        memory.add_turn("assistant", "F# is a functional language on .NET")
        
        # Search should handle special chars
        results = search.search(memory, "C++")
        assert len(results) > 0
        
        results = search.search(memory, "F#")
        assert len(results) > 0

    def test_semantic_search_edge_cases(self, search):
        """Test semantic search edge cases."""
        memory = ConversationMemory(max_size=5)
        memory.add_turn("user", "Test")
        
        # Search with large context window
        results = search.semantic_search(memory, "test", context_window=10)
        assert len(results) <= 1
        
        # Verify no duplicate indices
        if results:
            all_indices = set()
            for result in results:
                all_indices.add(result["matched_turn"]["turn_index"])
                for ctx in result["context_turns"]:
                    all_indices.add(ctx["turn_index"])
            
            # Each index should appear only once
            assert len(all_indices) == len(memory.get_turns())