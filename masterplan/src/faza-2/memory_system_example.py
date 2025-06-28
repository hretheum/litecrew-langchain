# Memory System Example

from litecrewai import Agent

agent = Agent(role="Assistant", memory_enabled=True)
agent.memory.store("user_name", "John", type="fact")
agent.memory.store("prefers_coffee", True, type="preference")

context = agent.memory.retrieve("user preferences")
# Returns: ["user prefers coffee", "user name is John"]