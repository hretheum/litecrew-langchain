"""
Advanced Memory Demo - Phase 7 Features

This example demonstrates the new advanced memory capabilities:
- Long-term memory with persistence
- Knowledge base with RAG
- Entity extraction and tracking
"""

from litecrew import LiteAgent, LiteCrew, LiteTask


def main():
    """Demonstrate advanced memory features."""
    
    # Create agent with all advanced memory features enabled
    researcher = LiteAgent(
        role="Research Analyst",
        goal="Analyze information and extract insights",
        backstory="Expert researcher with deep knowledge of technology and business",
        enable_long_term_memory=True,
        enable_knowledge_base=True,
        enable_entity_memory=True,
        memory_config={
            "long_term": {
                "max_items": 1000,
                "importance_threshold": 0.3,
                "decay_rate": 0.95
            },
            "knowledge_base": {
                "chunk_size": 300,
                "chunk_overlap": 50
            },
            "entity": {
                "enable_privacy": True,
                "cross_session": True
            }
        },
        verbose=True
    )
    
    writer = LiteAgent(
        role="Content Writer",
        goal="Create engaging content based on research",
        backstory="Professional writer specializing in technology topics",
        enable_knowledge_base=True,  # Share knowledge base
        verbose=True
    )
    
    # Add some knowledge to the knowledge base
    print("📚 Adding knowledge to the knowledge base...")
    
    knowledge_docs = [
        {
            "content": """
            LiteCrew is a lightweight multi-agent orchestration framework built on LangChain.
            It provides 363x faster import times compared to CrewAI while maintaining full API compatibility.
            The framework was developed to address performance issues in CrewAI, which has a 3.3s import time
            and 208MB memory overhead. LiteCrew achieves <0.009s import time and ~17MB memory usage.
            """,
            "source": "litecrew_overview.md",
            "metadata": {"category": "documentation", "version": "1.0"}
        },
        {
            "content": """
            Performance benchmarks show:
            - Import time: LiteCrew 0.009s vs CrewAI 3.268s (363x faster)
            - Memory usage: LiteCrew ~17MB vs CrewAI 208MB (12x less)
            - Agent creation: LiteCrew <5ms vs CrewAI >100ms (20x faster)
            - Task execution overhead: LiteCrew <3% vs CrewAI ~15% (5x less)
            """,
            "source": "benchmark_results.md",
            "metadata": {"category": "performance", "date": "2024-01-01"}
        },
        {
            "content": """
            Key features include:
            - Multi-LLM support with fallback chains
            - Advanced memory systems (short-term, long-term, RAG)
            - Rate limiting and token management
            - Structured outputs with validation
            - Event system for monitoring
            - Production-ready with Docker deployment
            """,
            "source": "features.md",
            "metadata": {"category": "features"}
        }
    ]
    
    for doc in knowledge_docs:
        doc_ids = researcher.add_knowledge(
            content=doc["content"],
            source=doc["source"],
            metadata=doc["metadata"]
        )
        print(f"  ✅ Added {len(doc_ids)} chunks from {doc['source']}")
    
    # Create tasks that will use the advanced memory
    research_task = LiteTask(
        description="""
        Research and analyze the performance improvements of LiteCrew compared to CrewAI.
        Focus on specific metrics and their implications for production use.
        Identify the key entities (frameworks, metrics, features) mentioned.
        """,
        agent=researcher,
        expected_output="Detailed analysis with metrics and entity relationships"
    )
    
    summary_task = LiteTask(
        description="""
        Based on the research, write a compelling summary about LiteCrew's advantages.
        Use the knowledge base to ensure accuracy of technical details.
        Highlight the most important performance improvements.
        """,
        agent=writer,
        context=[research_task],
        expected_output="Engaging summary suitable for technical audience"
    )
    
    # Create crew
    crew = LiteCrew(
        agents=[researcher, writer],
        tasks=[research_task, summary_task],
        verbose=True
    )
    
    # Execute crew
    print("\n🚀 Starting crew execution with advanced memory...\n")
    result = crew.kickoff()
    
    print("\n📊 Results:")
    print(result.raw)
    
    # Show memory statistics
    print("\n📈 Memory Statistics:")
    
    # Researcher memory stats
    researcher_stats = researcher.get_memory_stats()
    print("\nResearcher Memory:")
    for memory_type, stats in researcher_stats.items():
        print(f"  {memory_type}: {stats}")
    
    # Show extracted entities
    entities = researcher.get_entities()
    if entities:
        print("\n🏷️ Extracted Entities:")
        for name, entity_info in list(entities.items())[:5]:  # Show first 5
            print(f"  - {name} ({entity_info['type']})")
            if entity_info.get('relationships'):
                print(f"    Relationships: {entity_info['relationships']}")
    
    # Show knowledge base search example
    print("\n🔍 Knowledge Base Search Example:")
    search_results = researcher.search_knowledge("performance import time", k=3)
    for i, result in enumerate(search_results):
        print(f"  {i+1}. {result.snippet} (score: {result.score:.2f})")
    
    # Show long-term memories
    print("\n🧠 Long-term Memories:")
    memories = researcher.get_long_term_memories(limit=3)
    for i, memory in enumerate(memories):
        print(f"  {i+1}. {memory.content[:100]}... (importance: {memory.importance:.2f})")
    
    # Demonstrate memory compression
    print("\n🗜️ Memory Compression:")
    compression_stats = researcher.compress_memory()
    print(f"  Compression results: {compression_stats}")


if __name__ == "__main__":
    main()