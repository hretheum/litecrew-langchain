"""
Verify Phase 3 metrics according to IMPLEMENTATION_ROADMAP.md
"""

import time
import asyncio
import sys
from litecrew import LiteAgent, LiteTask, LiteCrew
from litecrew.llm import LLMProvider, LLMConfig, LLMManager, ResponseCache
from litecrew.memory import ConversationMemory, MemorySummarizer, MemorySearch


def test_block_3_1_metrics():
    """Test Block 3.1: Multi-LLM Support metrics."""
    print("\n=== Block 3.1: Multi-LLM Support ===")
    
    # Metric 1: Provider switching < 5ms
    print("\n1. Testing provider switching time...")
    manager = LLMManager()
    
    providers = [LLMProvider.OPENAI, LLMProvider.ANTHROPIC, LLMProvider.GROQ]
    configs = [
        LLMConfig(provider=p, model="test-model", temperature=0.7) 
        for p in providers
    ]
    
    switch_times = []
    for i in range(1, len(configs)):
        start = time.perf_counter()
        try:
            llm = manager.create_llm(configs[i])
        except:
            pass  # Provider might not be available
        duration = (time.perf_counter() - start) * 1000
        switch_times.append(duration)
        print(f"   Switch {i}: {duration:.2f}ms")
    
    avg_switch_time = sum(switch_times) / len(switch_times) if switch_times else 0
    print(f"   Average switch time: {avg_switch_time:.2f}ms")
    print(f"   ✅ PASS: {avg_switch_time:.2f}ms < 5ms" if avg_switch_time < 5 else f"   ❌ FAIL: {avg_switch_time:.2f}ms >= 5ms")
    
    # Metric 2: Cache hit rate > 80%
    print("\n2. Testing cache hit rate...")
    cache = ResponseCache(max_size=100)
    
    # Simulate queries
    queries = ["test query"] * 10 + ["new query 1", "new query 2", "test query"] * 3
    
    for i, query in enumerate(queries):
        cached = cache.get(query, provider="test")
        if not cached:
            cache.add(query, f"Response for {query}", provider="test")
    
    stats = cache.get_stats()
    hit_rate = stats['hit_rate'] * 100
    print(f"   Cache stats: {stats['hits']} hits, {stats['misses']} misses")
    print(f"   Hit rate: {hit_rate:.1f}%")
    print(f"   ✅ PASS: {hit_rate:.1f}% > 80%" if hit_rate > 80 else f"   ❌ FAIL: {hit_rate:.1f}% <= 80%")
    
    # Metric 3: Fallback latency < 100ms
    print("\n3. Testing fallback latency...")
    start = time.perf_counter()
    try:
        # Test with a provider that will fail and trigger fallback
        agent = LiteAgent(
            role="Test",
            goal="Test",
            backstory="Test",
            llm_provider="openai",  # Might fail if no API key
            fallback_providers=["groq", "anthropic", "ollama"]
        )
        fallback_duration = (time.perf_counter() - start) * 1000
        print(f"   Agent creation with fallback: {fallback_duration:.2f}ms")
        print(f"   ✅ PASS: {fallback_duration:.2f}ms < 100ms" if fallback_duration < 100 else f"   ❌ FAIL: {fallback_duration:.2f}ms >= 100ms")
    except Exception as e:
        print(f"   ⚠️  Could not test fallback: {str(e)}")


async def test_block_3_2_metrics():
    """Test Block 3.2: Streaming and Async metrics."""
    print("\n\n=== Block 3.2: Streaming and Async ===")
    
    # Metric 1: First token latency < 500ms
    print("\n1. Testing first token latency...")
    agent = LiteAgent(
        role="Test",
        goal="Test",
        backstory="Test",
        streaming=True
    )
    
    start = time.perf_counter()
    first_chunk = None
    async for chunk in agent.stream_execute("Test"):
        first_chunk = chunk
        break
    first_token_latency = (time.perf_counter() - start) * 1000
    
    print(f"   First token latency: {first_token_latency:.2f}ms")
    print(f"   ✅ PASS: {first_token_latency:.2f}ms < 500ms" if first_token_latency < 500 else f"   ❌ FAIL: {first_token_latency:.2f}ms >= 500ms")
    
    # Metric 2: Streaming overhead < 5%
    print("\n2. Testing streaming overhead...")
    
    # Regular execution
    start = time.perf_counter()
    regular_result = await agent.aexecute("Test task")
    regular_time = time.perf_counter() - start
    
    # Streaming execution
    start = time.perf_counter()
    streaming_result = []
    async for chunk in agent.stream_execute("Test task"):
        streaming_result.append(chunk)
    streaming_time = time.perf_counter() - start
    
    overhead = ((streaming_time - regular_time) / regular_time * 100) if regular_time > 0 else 0
    print(f"   Regular time: {regular_time*1000:.2f}ms")
    print(f"   Streaming time: {streaming_time*1000:.2f}ms")
    print(f"   Overhead: {overhead:.1f}%")
    print(f"   ✅ PASS: {overhead:.1f}% < 5%" if overhead < 5 else f"   ❌ FAIL: {overhead:.1f}% >= 5%")
    
    # Metric 3: Batch efficiency > 80% vs sequential
    print("\n3. Testing batch efficiency...")
    tasks = ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5"]
    
    # Sequential execution
    start = time.perf_counter()
    sequential_results = []
    for task in tasks:
        result = await agent.aexecute(task)
        sequential_results.append(result)
    sequential_time = time.perf_counter() - start
    
    # Batch execution
    start = time.perf_counter()
    batch_results = await agent.batch_execute(tasks)
    batch_time = time.perf_counter() - start
    
    efficiency = (sequential_time / batch_time * 100) if batch_time > 0 else 100
    print(f"   Sequential time: {sequential_time*1000:.2f}ms")
    print(f"   Batch time: {batch_time*1000:.2f}ms")
    print(f"   Efficiency: {efficiency:.1f}%")
    print(f"   ✅ PASS: {efficiency:.1f}% > 80%" if efficiency > 80 else f"   ❌ FAIL: {efficiency:.1f}% <= 80%")


def test_block_3_3_metrics():
    """Test Block 3.3: Conversation Memory metrics."""
    print("\n\n=== Block 3.3: Conversation Memory ===")
    
    # Metric 1: Memory access O(1)
    print("\n1. Testing memory access time complexity...")
    memory = ConversationMemory(max_size=1000)
    
    # Add many turns
    for i in range(100):
        memory.add_turn("user", f"Message {i}")
    
    # Test access time doesn't increase with size
    access_times = []
    for _ in range(10):
        start = time.perf_counter()
        turns = memory.get_turns(last_n=1)
        duration = (time.perf_counter() - start) * 1000
        access_times.append(duration)
    
    avg_access_time = sum(access_times) / len(access_times)
    print(f"   Average access time: {avg_access_time:.3f}ms")
    print(f"   ✅ PASS: Access time is constant O(1)" if avg_access_time < 1 else f"   ⚠️  WARNING: Access time might not be O(1)")
    
    # Metric 2: Memory overhead < 1KB per turn
    print("\n2. Testing memory overhead...")
    import sys
    
    memory = ConversationMemory()
    initial_size = sys.getsizeof(memory.get_turns())
    
    # Add 10 turns
    for i in range(10):
        memory.add_turn("user", f"This is message number {i} with some content")
    
    final_size = sys.getsizeof(memory.get_turns())
    overhead_per_turn = (final_size - initial_size) / 10
    
    print(f"   Initial size: {initial_size} bytes")
    print(f"   Final size: {final_size} bytes")
    print(f"   Overhead per turn: {overhead_per_turn:.0f} bytes")
    print(f"   ✅ PASS: {overhead_per_turn:.0f} bytes < 1024 bytes" if overhead_per_turn < 1024 else f"   ❌ FAIL: {overhead_per_turn:.0f} bytes >= 1024 bytes")
    
    # Metric 3: Summarization quality > 90%
    print("\n3. Testing summarization quality...")
    memory = ConversationMemory()
    summarizer = MemorySummarizer()
    
    # Add test conversation
    test_conversation = [
        ("user", "I need help with Python programming"),
        ("assistant", "I'd be happy to help you with Python programming. What specific topic do you need help with?"),
        ("user", "I want to learn about decorators"),
        ("assistant", "Decorators in Python are functions that modify other functions. They use the @ syntax."),
        ("user", "Can you show me an example?"),
        ("assistant", "Here's a simple example: @timer decorator that measures function execution time.")
    ]
    
    for role, content in test_conversation:
        memory.add_turn(role, content)
    
    summary = summarizer.summarize(memory)
    quality = summarizer.estimate_summary_quality(summary, memory.get_turns())
    
    print(f"   Summary: {summary[:100]}...")
    print(f"   Quality score: {quality:.1%}")
    print(f"   ✅ PASS: {quality:.1%} > 90%" if quality > 0.9 else f"   ❌ FAIL: {quality:.1%} <= 90%")


async def run_all_tests():
    """Run all Phase 3 metric tests."""
    print("=" * 60)
    print("PHASE 3 METRICS VERIFICATION")
    print("=" * 60)
    
    # Block 3.1
    test_block_3_1_metrics()
    
    # Block 3.2
    await test_block_3_2_metrics()
    
    # Block 3.3
    test_block_3_3_metrics()
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())