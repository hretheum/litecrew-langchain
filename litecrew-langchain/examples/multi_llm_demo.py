"""
Demo of multi-LLM support in LiteCrew
"""

from litecrew import LiteAgent, LiteTask, LiteCrew
from litecrew.llm import LLMProvider

def demo_multi_llm():
    """Demonstrate multi-LLM support."""
    
    # Create agent with OpenAI (default)
    openai_agent = LiteAgent(
        role="OpenAI Assistant",
        goal="Help with general tasks using OpenAI",
        backstory="An AI assistant powered by OpenAI's GPT models"
    )
    
    # Create agent with Anthropic
    anthropic_agent = LiteAgent(
        role="Claude Assistant",
        goal="Help with analysis using Anthropic's Claude",
        backstory="An AI assistant powered by Anthropic's Claude models",
        llm_provider="anthropic",
        llm_config={
            "model": "claude-3-sonnet",
            "temperature": 0.5
        }
    )
    
    # Create agent with local Ollama
    local_agent = LiteAgent(
        role="Local Assistant",
        goal="Process data locally using Ollama",
        backstory="A privacy-focused assistant running locally",
        llm_provider=LLMProvider.OLLAMA,
        llm_config={
            "model": "llama2",
            "api_base": "http://localhost:11434"
        }
    )
    
    # Create agent with fallback chain
    resilient_agent = LiteAgent(
        role="Resilient Assistant",
        goal="Always provide responses using fallback providers",
        backstory="An assistant that switches providers if one fails",
        llm_provider="openai",
        fallback_providers=["anthropic", "groq", "ollama"],
        cache_responses=True  # Cache responses for efficiency
    )
    
    # Demonstrate provider switching
    print("Initial provider:", resilient_agent.llm.__class__.__name__)
    
    # Switch to a different provider
    resilient_agent.switch_llm_provider("groq", {"model": "mixtral-8x7b"})
    print("After switch:", resilient_agent.llm.__class__.__name__)
    
    # Create tasks
    analysis_task = LiteTask(
        description="Analyze the benefits of using multiple LLM providers",
        agent=anthropic_agent
    )
    
    local_task = LiteTask(
        description="List 3 advantages of running LLMs locally",
        agent=local_agent
    )
    
    # Create crew
    crew = LiteCrew(
        agents=[openai_agent, anthropic_agent, local_agent, resilient_agent],
        tasks=[analysis_task, local_task],
        verbose=True
    )
    
    # Execute crew
    print("\nExecuting crew with multiple LLM providers...")
    result = crew.kickoff()
    print("\nResults:")
    print(result)
    
    # Show metrics
    print("\nAgent Metrics:")
    for agent in crew.agents:
        metrics = agent.metrics
        print(f"\n{agent.role}:")
        print(f"  - LLM Provider: {metrics['llm_provider']}")
        print(f"  - Executions: {metrics['execution_count']}")
        print(f"  - Cache Enabled: {metrics['cache_enabled']}")
        if 'cache_stats' in metrics:
            stats = metrics['cache_stats']
            print(f"  - Cache Hit Rate: {stats['hit_rate']:.2%}")


if __name__ == "__main__":
    demo_multi_llm()