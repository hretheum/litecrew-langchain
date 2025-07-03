"""
Demo of conversation memory functionality in LiteCrew
"""

from litecrew import LiteAgent, LiteTask, LiteCrew
from litecrew.memory import ConversationMemory, MemorySummarizer, MemorySearch


def demo_agent_memory():
    """Demonstrate agent with conversation memory."""
    print("=== Agent Memory Demo ===\n")
    
    # Create agent with memory
    agent = LiteAgent(
        role="Personal Assistant",
        goal="Help users while remembering context",
        backstory="An AI assistant with perfect memory of conversations",
        memory=True,
        verbose=True
    )
    
    # Simulate conversation
    print("User: My name is Alice and I work at OpenAI")
    response1 = agent.execute("My name is Alice and I work at OpenAI")
    print(f"Assistant: {response1}\n")
    
    print("User: I'm working on a project about LLMs")
    response2 = agent.execute("I'm working on a project about LLMs")
    print(f"Assistant: {response2}\n")
    
    print("User: What's my name and where do I work?")
    response3 = agent.execute("What's my name and where do I work?")
    print(f"Assistant: {response3}\n")
    
    # Search memory
    print("\n--- Memory Search ---")
    results = agent.search_memory("OpenAI")
    print(f"Found {len(results)} results for 'OpenAI'")
    for result in results:
        print(f"  {result['role']}: {result['content'][:50]}...")


def demo_memory_summarization():
    """Demonstrate memory summarization."""
    print("\n\n=== Memory Summarization Demo ===\n")
    
    # Create memory and add conversation
    memory = ConversationMemory()
    summarizer = MemorySummarizer()
    
    # Add a longer conversation
    conversation = [
        ("user", "Tell me about Python programming"),
        ("assistant", "Python is a high-level, interpreted programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991."),
        ("user", "What are its main features?"),
        ("assistant", "Python's main features include: dynamic typing, automatic memory management, extensive standard library, support for multiple programming paradigms, and cross-platform compatibility."),
        ("user", "How does it compare to JavaScript?"),
        ("assistant", "Python and JavaScript are both high-level languages but differ in their primary use cases. Python excels in data science, AI, and backend development, while JavaScript dominates web frontend development. Python uses indentation for blocks while JavaScript uses braces."),
        ("user", "Which one should I learn first?"),
        ("assistant", "For beginners, Python is often recommended first due to its cleaner syntax and gentler learning curve. However, if your goal is web development, starting with JavaScript might be more practical.")
    ]
    
    for role, content in conversation:
        memory.add_turn(role, content)
    
    # Summarize
    summary = summarizer.summarize(memory)
    print(f"Original conversation length: {sum(len(c[1]) for c in conversation)} chars")
    print(f"Summary length: {len(summary)} chars")
    print(f"\nSummary: {summary}")
    
    # Test summarization quality
    quality = summarizer.estimate_summary_quality(summary, memory.get_turns())
    print(f"\nEstimated quality score: {quality:.2%}")


def demo_memory_persistence():
    """Demonstrate memory persistence."""
    print("\n\n=== Memory Persistence Demo ===\n")
    
    # Create memory with persistence
    memory1 = ConversationMemory()
    
    # Storage for persistence
    storage = {}
    
    # Set up persistence hooks
    memory1.set_save_hook(lambda data: storage.update({"memory": data}))
    memory1.set_load_hook(lambda: storage.get("memory"))
    
    # Add conversation
    memory1.add_turn("user", "Remember this: The secret code is 42")
    memory1.add_turn("assistant", "I'll remember that the secret code is 42")
    
    # Save memory
    memory1.save()
    print("Memory saved!")
    
    # Create new memory instance and load
    memory2 = ConversationMemory()
    memory2.set_load_hook(lambda: storage.get("memory"))
    memory2.load()
    
    print("\nLoaded memory:")
    for turn in memory2.get_turns():
        print(f"  {turn['role']}: {turn['content']}")


def demo_memory_search_advanced():
    """Demonstrate advanced memory search."""
    print("\n\n=== Advanced Memory Search Demo ===\n")
    
    memory = ConversationMemory()
    search = MemorySearch()
    
    # Add diverse conversation
    conversations = [
        ("user", "I love programming in Python"),
        ("assistant", "Python is great for many applications"),
        ("user", "Tell me about machine learning libraries"),
        ("assistant", "Popular ML libraries include TensorFlow, PyTorch, and scikit-learn"),
        ("user", "Which one is best for beginners?"),
        ("assistant", "Scikit-learn is often recommended for beginners due to its simplicity"),
        ("user", "Can Python be used for web development?"),
        ("assistant", "Yes, Python has excellent web frameworks like Django and Flask")
    ]
    
    for role, content in conversations:
        memory.add_turn(role, content)
    
    # Search with relevance
    print("Searching for 'Python':")
    results = search.search(memory, "Python", top_k=3)
    for result in results:
        print(f"  Score: {result['relevance_score']:.2f} - {result['role']}: {result['content'][:60]}...")
    
    # Semantic search with context
    print("\n\nSemantic search for 'beginner' with context:")
    context_results = search.semantic_search(memory, "beginner", context_window=1)
    for group in context_results[:1]:
        print(f"  Matched: {group['matched_turn']['content']}")
        print("  Context:")
        for ctx in group['context_turns']:
            print(f"    {ctx['role']}: {ctx['content'][:60]}...")


def demo_crew_shared_memory():
    """Demonstrate crew with shared memory."""
    print("\n\n=== Crew Shared Memory Demo ===\n")
    
    # Create agents
    researcher = LiteAgent(
        role="Researcher",
        goal="Find information and remember findings",
        backstory="Expert at research with excellent memory",
        memory=True
    )
    
    analyst = LiteAgent(
        role="Analyst",
        goal="Analyze data using shared knowledge",
        backstory="Data analyst who builds on research findings",
        memory=True
    )
    
    writer = LiteAgent(
        role="Writer",
        goal="Create content based on shared insights",
        backstory="Content creator who synthesizes team knowledge",
        memory=True
    )
    
    # Create tasks
    research_task = LiteTask(
        description="Research the benefits of using AI in education",
        agent=researcher
    )
    
    analysis_task = LiteTask(
        description="Analyze the research findings and identify key trends",
        agent=analyst
    )
    
    writing_task = LiteTask(
        description="Write a summary of the benefits and trends identified",
        agent=writer
    )
    
    # Create crew with shared memory
    crew = LiteCrew(
        agents=[researcher, analyst, writer],
        tasks=[research_task, analysis_task, writing_task],
        memory=True,  # Enable shared memory
        verbose=True
    )
    
    print("Executing crew with shared memory...")
    result = crew.kickoff()
    
    print(f"\n\nFinal result: {result.raw[:200]}...")
    
    # Show shared memory context
    print("\n\nShared memory context:")
    print(crew.get_memory_context()[:500] + "...")


def main():
    """Run all memory demos."""
    print("LiteCrew Memory System Demos")
    print("=" * 50)
    
    demo_agent_memory()
    demo_memory_summarization()
    demo_memory_persistence()
    demo_memory_search_advanced()
    demo_crew_shared_memory()
    
    print("\n\nAll memory demos completed!")


if __name__ == "__main__":
    main()