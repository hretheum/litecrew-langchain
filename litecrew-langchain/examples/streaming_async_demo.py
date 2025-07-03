"""
Demo of streaming and async functionality in LiteCrew
"""

import asyncio
import time
from litecrew import LiteAgent, LiteTask, LiteCrew


async def demo_streaming():
    """Demonstrate streaming responses."""
    print("=== Streaming Demo ===\n")
    
    # Create streaming agent
    agent = LiteAgent(
        role="Streaming Assistant",
        goal="Provide responses in a streaming fashion",
        backstory="An AI that streams responses for better UX",
        streaming=True,
        verbose=True
    )
    
    print("Streaming response:")
    async for chunk in agent.stream_execute("Write a haiku about programming"):
        print(chunk, end="", flush=True)
    print("\n")


async def demo_async_execution():
    """Demonstrate async execution."""
    print("\n=== Async Execution Demo ===\n")
    
    # Create agent with progress tracking
    def on_progress(status: str, percentage: float):
        print(f"Progress: {status} - {percentage:.0f}%")
    
    agent = LiteAgent(
        role="Async Worker",
        goal="Process tasks asynchronously",
        backstory="Efficient async task processor",
        on_progress=on_progress
    )
    
    # Execute async
    result = await agent.aexecute("Calculate the meaning of life")
    print(f"\nResult: {result}")


async def demo_batch_processing():
    """Demonstrate batch processing."""
    print("\n=== Batch Processing Demo ===\n")
    
    agent = LiteAgent(
        role="Batch Processor",
        goal="Process multiple tasks efficiently",
        backstory="Optimized for batch operations"
    )
    
    tasks = [
        "Task 1: What is 2+2?",
        "Task 2: Name the capital of France",
        "Task 3: List 3 primary colors",
        "Task 4: What year is it?",
        "Task 5: Name a programming language"
    ]
    
    print(f"Processing {len(tasks)} tasks in batch...")
    start = time.time()
    
    # Batch execution
    results = await agent.batch_execute(tasks)
    
    duration = time.time() - start
    print(f"\nCompleted in {duration:.2f}s")
    
    for i, (task, result) in enumerate(zip(tasks, results)):
        print(f"\n{task}")
        print(f"→ {result}")


async def demo_concurrent_agents():
    """Demonstrate multiple agents working concurrently."""
    print("\n\n=== Concurrent Agents Demo ===\n")
    
    # Create multiple specialized agents
    researcher = LiteAgent(
        role="Researcher",
        goal="Find information",
        backstory="Expert at research"
    )
    
    analyst = LiteAgent(
        role="Analyst",
        goal="Analyze data",
        backstory="Data analysis expert"
    )
    
    writer = LiteAgent(
        role="Writer",
        goal="Create content",
        backstory="Creative writer"
    )
    
    # Define tasks
    research_task = researcher.aexecute("Research benefits of async programming")
    analysis_task = analyst.aexecute("Analyze performance gains from async")
    writing_task = writer.aexecute("Write summary of async benefits")
    
    print("Running 3 agents concurrently...")
    start = time.time()
    
    # Execute all concurrently
    results = await asyncio.gather(research_task, analysis_task, writing_task)
    
    duration = time.time() - start
    print(f"\nAll agents completed in {duration:.2f}s")
    
    for agent, result in zip([researcher, analyst, writer], results):
        print(f"\n{agent.role}: {result[:100]}...")


async def demo_streaming_with_callbacks():
    """Demonstrate streaming with callbacks."""
    print("\n\n=== Streaming with Callbacks Demo ===\n")
    
    chunks_received = []
    
    def on_chunk(chunk: str):
        chunks_received.append(chunk)
        print(f"[Callback] Received chunk: '{chunk}'")
    
    agent = LiteAgent(
        role="Callback Agent",
        goal="Stream with callbacks",
        backstory="Demonstrates callback functionality",
        streaming=True,
        on_chunk=on_chunk
    )
    
    print("Streaming with callbacks:")
    async for _ in agent.stream_execute("Count from 1 to 5"):
        # Chunks are also sent to callback
        pass
    
    print(f"\nTotal chunks received: {len(chunks_received)}")


async def demo_async_crew():
    """Demonstrate async crew execution."""
    print("\n\n=== Async Crew Demo ===\n")
    
    # Create agents
    planner = LiteAgent(
        role="Project Planner",
        goal="Plan project tasks",
        backstory="Expert project planner"
    )
    
    developer = LiteAgent(
        role="Developer",
        goal="Implement features",
        backstory="Skilled developer"
    )
    
    tester = LiteAgent(
        role="Tester",
        goal="Test implementations",
        backstory="Quality assurance expert"
    )
    
    # Create tasks
    planning_task = LiteTask(
        description="Plan a simple web app project",
        agent=planner
    )
    
    dev_task = LiteTask(
        description="List key features to implement",
        agent=developer
    )
    
    test_task = LiteTask(
        description="Create test strategy",
        agent=tester
    )
    
    # Create async crew
    crew = LiteCrew(
        agents=[planner, developer, tester],
        tasks=[planning_task, dev_task, test_task],
        async_execution=True,
        verbose=True
    )
    
    print("Executing crew asynchronously...")
    start = time.time()
    
    result = await crew.akickoff()
    
    duration = time.time() - start
    print(f"\n\nCrew completed in {duration:.2f}s")
    print(f"Final output: {result.raw[:200]}...")


async def main():
    """Run all demos."""
    print("LiteCrew Streaming & Async Demos")
    print("=" * 50)
    
    # Run demos
    await demo_streaming()
    await demo_async_execution()
    await demo_batch_processing()
    await demo_concurrent_agents()
    await demo_streaming_with_callbacks()
    await demo_async_crew()
    
    print("\n\nAll demos completed!")


if __name__ == "__main__":
    asyncio.run(main())