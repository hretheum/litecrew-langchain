# docs/getting-started.md

# Getting Started with LiteCrewAI

## Prerequisites

- Python 3.11+
- 2GB RAM minimum
- Optional: Docker for containerized deployment

## 5-Minute Quickstart

### 1. Install LiteCrewAI

```bash
pip install litecrewai
```

### 2. Create Your First Agent

```python
from litecrewai import Agent, Task

# Create an agent
agent = Agent(
    name="Assistant",
    role="Personal AI Assistant",
    goal="Help with daily tasks",
    model="gpt-4"
)

# Create a task
task = Task(
    description="Summarize today's tech news",
    agent=agent
)

# Execute
result = await task.execute()
print(result)
```

### 3. Add Tools

```python
from litecrewai.tools import WebSearch, Calculator

agent = Agent(
    name="Researcher",
    tools=[WebSearch(), Calculator()]
)

task = Task(
    description="Find the market cap of top 5 tech companies and calculate total",
    agent=agent
)
```

### 4. Multi-Agent System

```python
from litecrewai import Crew

researcher = Agent(name="Researcher", tools=[WebSearch()])
analyst = Agent(name="Analyst", tools=[Calculator()])
writer = Agent(name="Writer")

crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[
        Task("Research topic", researcher),
        Task("Analyze data", analyst),
        Task("Write report", writer)
    ]
)

result = await crew.kickoff()
```

## Next Steps

- [Complete Installation Guide](./installation.md)
- [Understanding Agents](./concepts.md#agents)
- [Building Custom Tools](./tutorials/custom-tools.md)