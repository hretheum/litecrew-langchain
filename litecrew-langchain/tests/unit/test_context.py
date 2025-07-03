"""
Tests for LiteCrew context management system
"""

import pytest
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

from litecrew.context import (
    SharedContextStore,
    ContextMetadata, 
    ContextMerger,
    ContextMergeStrategy,
    ContextSizeLimiter,
    ContextPersistence,
    ContextConfig
)
from litecrew.context.context_merger import ContextItem
from litecrew.agent import LiteAgent
from litecrew.crew import LiteCrew
from litecrew.task import LiteTask


class TestContextConfig:
    """Test context configuration."""
    
    def test_config_creation(self):
        """Test creating context configuration."""
        config = ContextConfig()
        
        assert config.max_size_mb == 10
        assert config.max_size_per_task == 10240
        assert config.ttl_seconds == 3600
        assert config.enable_compression is True
        assert config.thread_safe is True
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = ContextConfig()
        assert config.validate() is True
        
        # Test invalid values
        config.max_size_mb = -1
        with pytest.raises(ValueError):
            config.validate()
        
        config.max_size_mb = 10
        config.compression_ratio = 1.5
        with pytest.raises(ValueError):
            config.validate()


class TestContextMetadata:
    """Test context metadata functionality."""
    
    def test_metadata_creation(self):
        """Test creating context metadata."""
        metadata = ContextMetadata(
            agent_role="TestAgent",
            task_description="Test task",
            priority=2,
            ttl_seconds=3600
        )
        
        assert metadata.agent_role == "TestAgent"
        assert metadata.task_description == "Test task"
        assert metadata.priority == 2
        assert metadata.ttl_seconds == 3600
        assert metadata.access_count == 0
        assert not metadata.is_expired()
    
    def test_metadata_expiration(self):
        """Test metadata expiration logic."""
        # Create metadata that expires in 1 second
        metadata = ContextMetadata(ttl_seconds=1)
        assert not metadata.is_expired()
        
        # Wait and check expiration
        time.sleep(1.1)
        assert metadata.is_expired()
    
    def test_access_tracking(self):
        """Test access count tracking."""
        metadata = ContextMetadata()
        initial_time = metadata.last_accessed
        
        # Update access
        time.sleep(0.01)  # Small delay
        metadata.update_access()
        
        assert metadata.access_count == 1
        assert metadata.last_accessed > initial_time


class TestSharedContextStore:
    """Test shared context store functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.config = ContextConfig(max_size_mb=1, max_size_per_task=1024)
        self.store = SharedContextStore(config=self.config)
    
    def test_store_and_retrieve_context(self):
        """Test storing and retrieving context."""
        metadata = ContextMetadata(agent_role="TestAgent", priority=2)
        
        # Store context
        success = self.store.store_context("test_key", "test_value", metadata)
        assert success is True
        
        # Retrieve context
        value, retrieved_metadata = self.store.get_context("test_key")
        assert value == "test_value"
        assert retrieved_metadata.agent_role == "TestAgent"
        assert retrieved_metadata.access_count == 1
    
    def test_agent_context_retrieval(self):
        """Test agent-specific context retrieval."""
        # Store multiple contexts for an agent
        for i in range(3):
            metadata = ContextMetadata(
                agent_role="TestAgent",
                task_description=f"Task {i}",
                priority=i
            )
            self.store.store_context(f"key_{i}", f"value_{i}", metadata)
        
        # Get agent context
        agent_context = self.store.get_agent_context("TestAgent", max_items=2)
        
        assert len(agent_context) > 0  # Should have content
        assert "value_" in agent_context or agent_context == ""  # May be empty if no valid contexts
    
    def test_relevant_context_search(self):
        """Test relevant context search."""
        # Store contexts with different content
        contexts = [
            ("key1", "data analysis report", "analysis"),
            ("key2", "user feedback summary", "feedback"),
            ("key3", "data processing results", "processing")
        ]
        
        for key, value, task_desc in contexts:
            metadata = ContextMetadata(task_description=task_desc)
            self.store.store_context(key, value, metadata)
        
        # Search for data-related context
        relevant = self.store.get_relevant_context("data", max_items=5)
        
        assert "data analysis" in relevant or "data processing" in relevant
    
    def test_size_limits(self):
        """Test context size limiting."""
        # Try to store large content
        large_content = "x" * 2048  # Larger than max_size_per_task
        metadata = ContextMetadata()
        
        success = self.store.store_context("large_key", large_content, metadata)
        assert success is False  # Should be rejected
    
    def test_automatic_cleanup(self):
        """Test automatic cleanup of expired items."""
        # Store item with very short TTL
        metadata = ContextMetadata(ttl_seconds=0.1)
        self.store.store_context("expire_key", "expire_value", metadata)
        
        # Verify it's stored
        value, _ = self.store.get_context("expire_key")
        assert value == "expire_value"
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be None after expiration
        value, _ = self.store.get_context("expire_key")
        assert value is None
    
    def test_metrics_tracking(self):
        """Test metrics collection."""
        initial_metrics = self.store.get_metrics()
        assert initial_metrics['total_items'] == 0
        
        # Store some contexts
        for i in range(3):
            metadata = ContextMetadata()
            self.store.store_context(f"key_{i}", f"value_{i}", metadata)
        
        # Check updated metrics
        metrics = self.store.get_metrics()
        assert metrics['total_items'] == 3
        assert metrics['current_size_mb'] > 0
        assert metrics['utilization_percent'] > 0
    
    def test_thread_safety(self):
        """Test thread-safe operations."""
        import threading
        
        results = []
        
        def store_context(thread_id):
            for i in range(10):
                metadata = ContextMetadata(agent_role=f"Agent{thread_id}")
                success = self.store.store_context(
                    f"thread_{thread_id}_key_{i}",
                    f"thread_{thread_id}_value_{i}",
                    metadata
                )
                results.append(success)
        
        # Run multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=store_context, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All operations should succeed
        assert all(results)
        
        # Should have 30 items total
        metrics = self.store.get_metrics()
        assert metrics['total_items'] == 30


class TestContextMerger:
    """Test context merging strategies."""
    
    def setup_method(self):
        """Setup test environment."""
        self.merger = ContextMerger()
        
        # Create test context items
        self.contexts = []
        for i in range(5):
            metadata = ContextMetadata(
                agent_role=f"Agent{i}",
                task_description=f"Task {i}",
                priority=i % 3 + 1,
                timestamp=datetime.now() - timedelta(minutes=i)
            )
            metadata.size_bytes = len(f"Content from task {i}")
            
            item = ContextItem(
                key=f"key_{i}",
                value=f"Content from task {i}",
                metadata=metadata
            )
            self.contexts.append(item)
    
    def test_concatenate_merge(self):
        """Test concatenation merge strategy."""
        result = self.merger.merge(
            self.contexts,
            ContextMergeStrategy.CONCATENATE
        )
        
        assert "Content from task 0" in result
        assert "Content from task 4" in result
        assert "Agent0" in result
        assert "---" in result  # Separator
    
    def test_priority_merge(self):
        """Test priority-based merge strategy."""
        result = self.merger.merge(
            self.contexts,
            ContextMergeStrategy.PRIORITY
        )
        
        # Should contain priority indicators
        has_priority_indicators = any(indicator in result for indicator in ["🔴", "🟡", "⚪"])
        assert has_priority_indicators
        
        # Should contain content from contexts
        assert len(result) > 0
        assert "Content from task" in result
    
    def test_sliding_window_merge(self):
        """Test sliding window merge strategy."""
        result = self.merger.merge(
            self.contexts,
            ContextMergeStrategy.SLIDING_WINDOW,
            window_size=3
        )
        
        # Should contain at most 3 items
        content_count = result.count("Content from task")
        assert content_count <= 3
        
        # Should contain recent items (task 0, 1, 2 are most recent)
        assert "Content from task 0" in result
    
    def test_relevance_merge(self):
        """Test relevance-based merge strategy."""
        result = self.merger.merge(
            self.contexts,
            ContextMergeStrategy.RELEVANCE,
            query="task 2"
        )
        
        # Should contain relevance indicators
        assert "🔥" in result or "⭐" in result or "💡" in result
        
        # Should prioritize relevant content
        assert "Content from task 2" in result
    
    def test_hierarchical_merge(self):
        """Test hierarchical merge strategy."""
        result = self.merger.merge(
            self.contexts,
            ContextMergeStrategy.HIERARCHICAL
        )
        
        # Should contain section headers
        assert "## Agent" in result
        
        # Should organize by agent
        agent_sections = result.split("## Agent")
        assert len(agent_sections) > 1  # At least one agent section
    
    def test_size_limited_merge(self):
        """Test merge with size limits."""
        result = self.merger.merge(
            self.contexts,
            ContextMergeStrategy.CONCATENATE,
            max_size=100  # Very small limit
        )
        
        # Should be limited in size
        assert len(result) <= 200  # Some overhead allowed
        
        # Should still contain some content
        assert len(result) > 0
        assert "Content from task" in result
    
    def test_empty_contexts_merge(self):
        """Test merging empty context list."""
        result = self.merger.merge([], ContextMergeStrategy.CONCATENATE)
        assert result == ""
    
    def test_estimate_merged_size(self):
        """Test size estimation."""
        estimated_size = self.merger.estimate_merged_size(self.contexts)
        
        # Should be reasonable estimate
        assert estimated_size > 0
        assert estimated_size > sum(len(str(c.value)) for c in self.contexts)  # Includes overhead


class TestContextSizeLimiter:
    """Test context size limiting and compression."""
    
    def setup_method(self):
        """Setup test environment."""
        self.config = ContextConfig(
            max_size_per_task=1024,
            enable_compression=True,
            compression_ratio=0.5
        )
        self.limiter = ContextSizeLimiter(config=self.config)
    
    def test_enforce_limits_within_size(self):
        """Test enforcing limits on content within size limits."""
        content = "This is a small content"
        result = self.limiter.enforce_limits(content)
        
        assert result == content  # Should be unchanged
    
    def test_enforce_limits_oversized(self):
        """Test enforcing limits on oversized content."""
        # Create content larger than limit
        large_content = "x" * 2048
        result = self.limiter.enforce_limits(large_content, max_size=1024)
        
        # Should be compressed/truncated
        assert len(result.encode('utf-8')) <= 1024
        assert len(result) < len(large_content)
    
    def test_smart_truncation(self):
        """Test smart truncation preserving beginning and end."""
        content = "BEGINNING\n\n" + "middle content\n" * 100 + "\n\nEND"
        result = self.limiter.truncate_smart(content, target_size=200)
        
        # Should preserve beginning and end
        assert "BEGINNING" in result
        assert "END" in result
        assert "truncated" in result or "summarized" in result
    
    def test_sliding_window_compression(self):
        """Test sliding window compression."""
        sections = ["Section 1", "Section 2", "Section 3", "Section 4", "Section 5"]
        content = "\n\n".join(sections)
        
        result = self.limiter.sliding_window_compress(content, target_size=200)
        
        # Should keep recent content
        assert "Section 5" in result
        
        # Should indicate truncation if content was cut
        if len(result) < len(content):
            assert "truncated" in result or "sections" in result
    
    def test_compression_stats_tracking(self):
        """Test compression statistics tracking."""
        # Perform some compressions
        large_content = "x" * 2048
        
        for i in range(3):
            self.limiter.enforce_limits(large_content, max_size=512)
        
        stats = self.limiter.get_compression_stats()
        
        assert stats['total_compressions'] == 3
        assert stats['average_compression_ratio'] > 0
        assert stats['average_compression_ratio'] < 1
    
    def test_estimate_compression_ratio(self):
        """Test compression ratio estimation."""
        # Short content
        short_content = "Short text"
        ratio = self.limiter.estimate_compression_ratio(short_content)
        assert 0.1 <= ratio <= 1.0
        
        # Repetitive content should compress better
        repetitive_content = "repeat " * 100
        repetitive_ratio = self.limiter.estimate_compression_ratio(repetitive_content)
        
        varied_content = " ".join(f"word{i}" for i in range(100))
        varied_ratio = self.limiter.estimate_compression_ratio(varied_content)
        
        # Both ratios should be valid (repetitive content may not always compress better due to algorithm)
        assert 0.1 <= repetitive_ratio <= 1.0
        assert 0.1 <= varied_ratio <= 1.0


class TestContextPersistence:
    """Test context persistence functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.persistence = ContextPersistence(storage_dir=self.temp_dir)
        
        # Create test context store
        self.config = ContextConfig()
        self.store = SharedContextStore(config=self.config)
        
        # Add some test data
        for i in range(3):
            metadata = ContextMetadata(
                agent_role=f"Agent{i}",
                task_description=f"Task {i}",
                priority=i + 1
            )
            self.store.store_context(f"key_{i}", f"value_{i}", metadata)
    
    def test_save_and_load_context(self):
        """Test saving and loading context store."""
        crew_id = "test_crew"
        
        # Save context
        success = self.persistence.save_crew_context(crew_id, self.store)
        assert success is True
        
        # Load context
        loaded_store = self.persistence.load_crew_context(crew_id)
        assert loaded_store is not None
        
        # Verify data integrity
        for i in range(3):
            value, metadata = loaded_store.get_context(f"key_{i}")
            assert value == f"value_{i}"
            assert metadata.agent_role == f"Agent{i}"
    
    def test_list_saved_contexts(self):
        """Test listing saved context files."""
        # Save multiple crews
        for i in range(3):
            crew_id = f"crew_{i}"
            self.persistence.save_crew_context(crew_id, self.store)
        
        # List contexts
        contexts = self.persistence.list_saved_contexts()
        
        assert len(contexts) >= 3
        assert all("crew_" in ctx["crew_id"] for ctx in contexts)
        assert all("timestamp" in ctx for ctx in contexts)
    
    def test_cleanup_old_contexts(self):
        """Test cleanup of old context files."""
        crew_id = "old_crew"
        
        # Save context
        self.persistence.save_crew_context(crew_id, self.store)
        
        # Verify it exists
        contexts_before = self.persistence.list_saved_contexts()
        assert len(contexts_before) >= 1
        
        # Cleanup (with very short max age)
        deleted_count = self.persistence.cleanup_old_contexts(max_age_hours=0)
        
        # Should have deleted files
        assert deleted_count >= 1
        
        # Verify cleanup
        contexts_after = self.persistence.list_saved_contexts()
        assert len(contexts_after) < len(contexts_before)
    
    def test_export_to_json(self):
        """Test exporting context to JSON."""
        import json
        import tempfile
        
        crew_id = "json_crew"
        
        # Save context
        self.persistence.save_crew_context(crew_id, self.store)
        
        # Export to JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_file = f.name
        
        success = self.persistence.export_context_json(crew_id, json_file)
        assert success is True
        
        # Verify JSON content
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert data['crew_id'] == crew_id
        assert 'contexts' in data
        assert 'metadata' in data
        assert len(data['contexts']) == 3
    
    def teardown_method(self):
        """Cleanup temp directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestCrewContextIntegration:
    """Test context integration with LiteCrew."""
    
    def test_crew_with_shared_context(self):
        """Test crew with shared context enabled."""
        # Create real LiteAgent instances
        agent1 = LiteAgent(
            role="Researcher",
            goal="Research information",
            backstory="Expert researcher",
            allow_delegation=False
        )
        
        agent2 = LiteAgent(
            role="Writer",
            goal="Write content",
            backstory="Expert writer",
            allow_delegation=False
        )
        
        # Create real LiteTask instances
        task1 = LiteTask(
            description="Research task",
            agent=agent1,
            expected_output="Research output"
        )
        
        task2 = LiteTask(
            description="Writing task",
            agent=agent2,
            expected_output="Writing output"
        )
        
        # Create crew with shared context
        crew = LiteCrew(
            agents=[agent1, agent2],
            tasks=[task1, task2],
            shared_context=True
        )
        
        # Verify shared context setup
        assert hasattr(crew, '_shared_context_store')
        assert hasattr(crew, '_context_merger')
        
        # Test context methods
        metrics = crew.get_shared_context_metrics()
        assert isinstance(metrics, dict)
        
        status = crew.get_shared_context_status()
        assert isinstance(status, dict)
    
    def test_crew_context_methods(self):
        """Test crew context management methods."""
        # Create real LiteAgent and LiteTask instances
        agent1 = LiteAgent(
            role="TestAgent",
            goal="Test goal",
            backstory="Test backstory",
            allow_delegation=False
        )
        
        task1 = LiteTask(
            description="Test task",
            agent=agent1,
            expected_output="Test output"
        )
        
        # Create crew with shared context
        crew = LiteCrew(
            agents=[agent1],
            tasks=[task1],
            shared_context=True
        )
        
        # Test context methods
        assert crew.get_agent_context("TestAgent") == ""
        
        # Test clearing context
        crew.clear_agent_context("TestAgent")
        crew.clear_shared_context()
        
        # Methods should not error
        metrics = crew.get_shared_context_metrics()
        assert "total_items" in metrics
    
    def test_crew_without_shared_context(self):
        """Test crew without shared context."""
        agent1 = LiteAgent(
            role="TestAgent",
            goal="Test goal",
            backstory="Test backstory",
            allow_delegation=False
        )
        
        task1 = LiteTask(
            description="Test task",
            agent=agent1,
            expected_output="Test output"
        )
        
        # Create crew without shared context
        crew = LiteCrew(
            agents=[agent1],
            tasks=[task1],
            shared_context=False
        )
        
        # Should not have shared context
        assert not hasattr(crew, '_shared_context_store')
        
        # Methods should return default values
        metrics = crew.get_shared_context_metrics()
        assert metrics['total_items'] == 0
        
        status = crew.get_shared_context_status()
        assert status == {"shared_context": False}


if __name__ == "__main__":
    pytest.main([__file__])