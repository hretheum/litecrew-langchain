# Example Agent implementation

from litecrewai import Agent

agent = Agent(
    role="Researcher",
    goal="Find accurate information",
    tools=["web_search", "calculator"],
    llm="ollama/mistral"
)
result = agent.execute("What is quantum computing?")