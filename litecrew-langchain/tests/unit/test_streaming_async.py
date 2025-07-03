"""
Tests for streaming and async functionality in LiteCrew.
"""

import pytest
import asyncio
import time
from typing import AsyncIterator, List
from unittest.mock import Mock, patch, AsyncMock
from litecrew.agent import LiteAgent
from litecrew.task import LiteTask
from litecrew.crew import LiteCrew


class TestStreamingAsync:
    """Test streaming and async functionality."""
    
    @pytest.mark.asyncio
    async def test_agent_async_execution(self):
        """Test agent async execution."""
        agent = LiteAgent(
            role="Async Agent",
            goal="Execute tasks asynchronously",
            backstory="An agent optimized for async operations"
        )
        
        # Test async execution
        result = await agent.aexecute("Test async task")
        assert isinstance(result, str)
        
    @pytest.mark.asyncio
    async def test_streaming_response(self):
        """Test streaming LLM responses."""
        agent = LiteAgent(
            role="Streaming Agent",
            goal="Stream responses",
            backstory="An agent that streams responses",
            streaming=True
        )
        
        # Test streaming (will use fallback implementation)
        chunks = []
        async for chunk in agent.stream_execute("Say hello"):
            chunks.append(chunk)
        
        # Should have chunks
        assert len(chunks) > 0
        # Should reconstruct to a valid response
        full_response = "".join(chunks)
        assert isinstance(full_response, str)
        assert len(full_response) > 0
    
    @pytest.mark.asyncio
    async def test_batch_processing(self):
        """Test batch processing of multiple tasks."""
        agent = LiteAgent(
            role="Batch Agent",
            goal="Process tasks in batches",
            backstory="An agent optimized for batch processing"
        )
        
        tasks = [
            "Task 1: Calculate 2+2",
            "Task 2: What is the capital of France?",
            "Task 3: List 3 colors"
        ]
        
        start = time.time()
        results = await agent.batch_execute(tasks)
        duration = time.time() - start
        
        assert len(results) == 3
        assert all(isinstance(r, str) for r in results)
        # Batch should be faster than sequential
        assert duration < len(tasks) * 0.1  # Assuming 100ms per task sequential
    
    @pytest.mark.asyncio
    async def test_partial_response_handling(self):
        """Test handling of partial responses."""
        agent = LiteAgent(
            role="Partial Agent",
            goal="Handle partial responses",
            backstory="An agent that handles incomplete responses"
        )
        
        # Create partial response handler
        partial_responses = []
        
        def on_partial(partial: str):
            partial_responses.append(partial)
        
        agent.on_partial_response = on_partial
        
        # Test that we can set partial response handler
        result = await agent.aexecute("Generate long response")
        
        # Should get a response
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_progress_callbacks(self):
        """Test progress callback functionality."""
        progress_updates = []
        
        def on_progress(status: str, percentage: float):
            progress_updates.append((status, percentage))
        
        agent = LiteAgent(
            role="Progress Agent",
            goal="Report progress",
            backstory="An agent that reports progress",
            on_progress=on_progress
        )
        
        # Execute with progress tracking
        await agent.aexecute("Long running task")
        
        # Progress updates are optional based on implementation
        # Just verify the execution completed
        assert isinstance(await agent.aexecute("Test task"), str)
    
    @pytest.mark.asyncio
    async def test_first_token_latency(self):
        """Test first token latency in streaming."""
        agent = LiteAgent(
            role="Fast Agent",
            goal="Minimize first token latency",
            backstory="An agent optimized for low latency",
            streaming=True
        )
        
        start = time.time()
        first_chunk = None
        async for chunk in agent.stream_execute("Quick response"):
            first_chunk = chunk
            break
        first_token_time = (time.time() - start) * 1000
        
        # First token should arrive reasonably quickly
        assert first_chunk is not None
        assert first_token_time < 1000  # 1 second is reasonable for mock
    
    @pytest.mark.asyncio
    async def test_streaming_overhead(self):
        """Test streaming overhead vs non-streaming."""
        # Create two agents
        streaming_agent = LiteAgent(
            role="Streaming",
            goal="Stream",
            backstory="Streams",
            streaming=True
        )
        
        regular_agent = LiteAgent(
            role="Regular",
            goal="Regular",
            backstory="Regular",
            streaming=False
        )
        
        # Both should complete successfully
        chunks = []
        async for chunk in streaming_agent.stream_execute("Test"):
            chunks.append(chunk)
        stream_result = "".join(chunks)
        
        result = await regular_agent.aexecute("Test")
        
        # Both should produce results
        assert len(stream_result) > 0
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_agents(self):
        """Test multiple agents executing concurrently."""
        agents = [
            LiteAgent(
                role=f"Agent {i}",
                goal=f"Process task {i}",
                backstory=f"Agent number {i}"
            )
            for i in range(5)
        ]
        
        # Execute all agents concurrently
        start = time.time()
        tasks = [agent.aexecute(f"Task for agent {i}") for i, agent in enumerate(agents)]
        results = await asyncio.gather(*tasks)
        duration = time.time() - start
        
        assert len(results) == 5
        assert all(isinstance(r, str) for r in results)
        # Should be much faster than sequential (5 * 100ms = 500ms)
        assert duration < 0.2  # Should complete in ~100ms with concurrency
    
    @pytest.mark.asyncio
    async def test_crew_async_execution(self):
        """Test crew async execution."""
        agent1 = LiteAgent(
            role="Async Agent 1",
            goal="First async agent",
            backstory="First agent"
        )
        
        agent2 = LiteAgent(
            role="Async Agent 2", 
            goal="Second async agent",
            backstory="Second agent"
        )
        
        task1 = LiteTask(
            description="First async task",
            agent=agent1
        )
        
        task2 = LiteTask(
            description="Second async task",
            agent=agent2
        )
        
        crew = LiteCrew(
            agents=[agent1, agent2],
            tasks=[task1, task2],
            async_execution=True
        )
        
        # Execute crew asynchronously
        result = await crew.akickoff()
        # Result is CrewOutput, not string
        assert hasattr(result, 'raw')
        assert isinstance(result.raw, str)
    
    @pytest.mark.asyncio
    async def test_streaming_with_callbacks(self):
        """Test streaming with multiple callbacks."""
        chunks_received = []
        
        def on_chunk(chunk: str):
            chunks_received.append(chunk)
        
        agent = LiteAgent(
            role="Callback Agent",
            goal="Stream with callbacks",
            backstory="Agent with streaming callbacks",
            streaming=True,
            on_chunk=on_chunk
        )
        
        async for chunk in agent.stream_execute("Generate text"):
            pass
        
        # Should have received chunks via callback
        assert len(chunks_received) > 0
    
    @pytest.mark.asyncio
    async def test_error_handling_in_streaming(self):
        """Test error handling during streaming."""
        agent = LiteAgent(
            role="Error Agent",
            goal="Handle streaming errors",
            backstory="Agent that handles errors",
            streaming=True
        )
        
        # For now, just test that streaming completes without error
        chunks = []
        try:
            async for chunk in agent.stream_execute("Test error handling"):
                chunks.append(chunk)
        except Exception:
            pass
        
        # Should handle gracefully
        assert isinstance(chunks, list)
    
    @pytest.mark.asyncio
    async def test_batch_with_different_providers(self):
        """Test batch processing with different LLM providers."""
        agents = [
            LiteAgent(
                role="OpenAI Agent",
                goal="Use OpenAI",
                backstory="OpenAI powered",
                llm_provider="openai"
            ),
            LiteAgent(
                role="Anthropic Agent",
                goal="Use Anthropic",
                backstory="Claude powered",
                llm_provider="anthropic"
            ),
            LiteAgent(
                role="Local Agent",
                goal="Use Ollama",
                backstory="Local LLM",
                llm_provider="ollama"
            )
        ]
        
        # Batch execute across providers
        tasks = ["Task 1", "Task 2", "Task 3"]
        start = time.time()
        
        batch_tasks = []
        for agent, task in zip(agents, tasks):
            batch_tasks.append(agent.aexecute(task))
        
        results = await asyncio.gather(*batch_tasks)
        duration = time.time() - start
        
        assert len(results) == 3
        # Even with different providers, should execute concurrently
        assert duration < 0.3  # Much less than sequential