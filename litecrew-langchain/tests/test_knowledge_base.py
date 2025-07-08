"""
Tests for Knowledge Base with RAG implementation.
"""

import time
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from litecrew.memory.knowledge_base import KnowledgeBase, Document, SearchResult


class TestKnowledgeBase:
    """Test knowledge base functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test storage."""
        with TemporaryDirectory() as td:
            yield Path(td)
    
    @pytest.fixture
    def kb(self, temp_dir):
        """Create KnowledgeBase instance."""
        return KnowledgeBase(
            storage_path=temp_dir / "test_kb",
            model_name="all-MiniLM-L6-v2",  # Small, fast model
            chunk_size=200,
            chunk_overlap=20
        )
    
    def test_document_ingestion(self, kb):
        """Test document ingestion and chunking."""
        content = """
        LiteCrew is a lightweight multi-agent orchestration framework built on LangChain.
        It provides 363x faster import times compared to CrewAI while maintaining API compatibility.
        
        The framework supports multiple LLM providers including OpenAI, Anthropic, and local models.
        It features advanced memory management, rate limiting, and structured outputs.
        """
        
        doc_ids = kb.ingest_document(
            content=content,
            source="test_doc.md",
            metadata={"type": "documentation", "version": "1.0"}
        )
        
        assert len(doc_ids) >= 2  # Should be chunked
        assert len(kb.documents) == len(doc_ids)
        
        # Check chunks
        for doc_id in doc_ids:
            doc = kb.documents[doc_id]
            assert doc.source == "test_doc.md"
            assert doc.metadata["type"] == "documentation"
            assert doc.embedding is not None
    
    def test_embedding_performance(self, kb):
        """Test embedding time meets <100ms per doc requirement."""
        content = "This is a test document for measuring embedding performance." * 10
        
        start_time = time.perf_counter()
        doc_ids = kb.ingest_document(content, "perf_test.txt")
        embedding_time = (time.perf_counter() - start_time) * 1000
        
        # Should be <100ms per document
        time_per_doc = embedding_time / len(doc_ids)
        assert time_per_doc < 100
        
        print(f"Embedding time per doc: {time_per_doc:.2f}ms")
    
    def test_search_performance(self, kb):
        """Test search latency meets <200ms requirement."""
        # Add test documents
        documents = [
            "LangChain is a framework for developing applications powered by language models.",
            "CrewAI provides multi-agent orchestration but has performance issues.",
            "LiteCrew combines the best of both worlds with excellent performance.",
            "The benchmark results show 363x faster import times.",
            "Memory management is crucial for production applications."
        ]
        
        for i, content in enumerate(documents):
            kb.ingest_document(content, f"doc_{i}.txt")
        
        # Test search performance
        queries = ["performance", "LangChain", "memory", "benchmark"]
        total_time = 0
        
        for query in queries:
            start_time = time.perf_counter()
            results = kb.search(query, k=3)
            search_time = (time.perf_counter() - start_time) * 1000
            total_time += search_time
            
            assert search_time < 200  # <200ms requirement
            assert len(results) <= 3
        
        avg_time = total_time / len(queries)
        print(f"Average search time: {avg_time:.2f}ms")
    
    def test_retrieval_accuracy(self, kb):
        """Test retrieval accuracy meets >90% requirement."""
        # Add documents with specific topics
        test_data = [
            ("Python is a high-level programming language.", "programming"),
            ("Machine learning enables computers to learn from data.", "ml"),
            ("Docker containers provide application isolation.", "devops"),
            ("React is a JavaScript library for building UIs.", "frontend"),
            ("PostgreSQL is a powerful relational database.", "database"),
        ]
        
        for content, topic in test_data:
            kb.ingest_document(
                content=content,
                source=f"{topic}.txt",
                metadata={"topic": topic}
            )
        
        # Test retrieval accuracy
        correct_retrievals = 0
        total_queries = 0
        
        test_queries = [
            ("Python programming", "programming"),
            ("machine learning AI", "ml"),
            ("container Docker", "devops"),
            ("React frontend", "frontend"),
            ("database PostgreSQL", "database")
        ]
        
        for query, expected_topic in test_queries:
            results = kb.search(query, k=1)
            total_queries += 1
            
            if results and results[0].document.metadata.get("topic") == expected_topic:
                correct_retrievals += 1
        
        accuracy = correct_retrievals / total_queries
        assert accuracy > 0.9  # >90% accuracy requirement
        
        print(f"Retrieval accuracy: {accuracy * 100:.1f}%")
    
    def test_document_update(self, kb):
        """Test document update functionality."""
        # Add initial document
        doc_ids = kb.ingest_document("Initial content", "update_test.txt")
        doc_id = doc_ids[0]
        
        # Update document
        success = kb.update_document(
            doc_id,
            content="Updated content with new information",
            metadata={"updated": True}
        )
        
        assert success
        
        # Verify update
        doc = kb.documents[doc_id]
        assert "Updated content" in doc.content
        assert doc.metadata["updated"] is True
        
        # Search should find updated content
        results = kb.search("new information", k=1)
        assert len(results) == 1
        assert results[0].document.id == doc_id
    
    def test_source_tracking(self, kb):
        """Test source tracking functionality."""
        # Add documents from different sources
        kb.ingest_document("Content from file 1", "file1.txt")
        kb.ingest_document("More content from file 1", "file1.txt")
        kb.ingest_document("Content from file 2", "file2.txt")
        
        # Get source statistics
        stats = kb.get_source_tracking()
        
        assert "file1.txt" in stats
        assert "file2.txt" in stats
        assert stats["file1.txt"]["count"] >= 2
        assert stats["file2.txt"]["count"] >= 1
    
    def test_persistence(self, temp_dir):
        """Test knowledge base persistence."""
        kb_path = temp_dir / "persist_kb"
        
        # First session - add documents
        kb1 = KnowledgeBase(storage_path=kb_path)
        kb1.ingest_document("Persistent document 1", "doc1.txt")
        kb1.ingest_document("Persistent document 2", "doc2.txt")
        kb1._save_documents()
        doc_count = len(kb1.documents)
        
        # Second session - load documents
        kb2 = KnowledgeBase(storage_path=kb_path)
        
        assert len(kb2.documents) == doc_count
        
        # Search should work
        results = kb2.search("Persistent", k=2)
        assert len(results) == 2
    
    def test_chunking_with_overlap(self, kb):
        """Test text chunking with overlap."""
        # Create text that will be chunked
        sentences = [f"Sentence {i}. " for i in range(20)]
        content = "".join(sentences)
        
        chunks = kb._chunk_text(content)
        
        assert len(chunks) > 1
        
        # Check overlap exists
        for i in range(len(chunks) - 1):
            # Some content from chunk i should appear in chunk i+1
            overlap_exists = any(
                part in chunks[i+1] 
                for part in chunks[i].split()[-5:]  # Last few words
            )
            assert overlap_exists or i == len(chunks) - 2
    
    def test_semantic_search(self, kb):
        """Test semantic search capabilities."""
        # Add documents with semantic variations
        kb.ingest_document("The quick brown fox jumps over the lazy dog", "doc1.txt")
        kb.ingest_document("A fast auburn canine leaps above a sleepy hound", "doc2.txt")
        kb.ingest_document("Python is a programming language", "doc3.txt")
        
        # Search semantically similar content
        results = kb.search("speedy red animal jumping", k=2)
        
        # Should find the semantically similar documents
        assert len(results) >= 2
        sources = [r.document.source for r in results[:2]]
        assert "doc1.txt" in sources or "doc2.txt" in sources
    
    def test_filter_by_source(self, kb):
        """Test filtering search results by source."""
        # Add documents from different sources
        kb.ingest_document("Python content", "python.txt")
        kb.ingest_document("Python tutorial", "python.txt")
        kb.ingest_document("Java content", "java.txt")
        
        # Search with source filter
        results = kb.search("content", k=5, filter_source="python.txt")
        
        # All results should be from python.txt
        assert all(r.document.source == "python.txt" for r in results)
        assert len(results) <= 2
    
    def test_storage_cleanup(self, kb):
        """Test automatic cleanup of old documents."""
        kb.max_documents = 5
        
        # Add more documents than limit
        for i in range(10):
            time.sleep(0.01)  # Ensure different timestamps
            kb.ingest_document(f"Document {i}", f"doc_{i}.txt")
        
        # Should have cleaned up old documents
        assert len(kb.documents) <= kb.max_documents
        
        # Newest documents should be kept
        sources = [doc.source for doc in kb.documents.values()]
        assert "doc_9.txt" in sources
        assert "doc_0.txt" not in sources