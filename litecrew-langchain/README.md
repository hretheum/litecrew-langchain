# LiteCrew-LangChain

A lightweight multi-agent orchestration framework built on LangChain, inspired by CrewAI but with 10x better performance.

## Why This Project?

Our benchmarks revealed:
- **CrewAI**: 3.268s import time, 208MB memory overhead
- **LangChain**: 0.008s import time, 17MB memory overhead
- **LiteCrew Fork**: Failed attempt, increased size instead of reducing it

This project provides CrewAI's multi-agent features on LangChain's efficient foundation.

## Features

- ✅ Role-based agents (role, goal, backstory)
- ✅ Multi-agent crew orchestration
- ✅ Task dependencies and context passing
- ✅ Sequential and hierarchical execution
- ✅ Agent delegation capabilities (5 strategies)
- ✅ Advanced context management with compression
- ✅ CrewAI-compatible API
- ✅ <30MB memory footprint
- ✅ 9ms import time

## Quick Start

```python
from litecrew import LiteAgent, LiteCrew, LiteTask

# Create agents
researcher = LiteAgent(
    role="Researcher",
    goal="Find accurate information",
    backstory="Expert at research and analysis"
)

writer = LiteAgent(
    role="Writer", 
    goal="Create engaging content",
    backstory="Professional content creator"
)

# Define tasks
research_task = LiteTask(
    description="Research AI frameworks performance",
    agent=researcher,
    expected_output="Summary of benchmark results"
)

write_task = LiteTask(
    description="Write blog post about findings",
    agent=writer,
    context=[research_task],  # Uses output from research
    expected_output="Blog post draft"
)

# Create and run crew
crew = LiteCrew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process="sequential"
)

result = crew.kickoff()
print(result.raw)
```

## Performance

| Metric | CrewAI | LiteCrew | Improvement |
|--------|---------|----------|-------------|
| Import Time | 3.268s | 9ms | 363x faster |
| Memory Usage | 208MB | <30MB | 7x less |
| Agent Creation | N/A | <5ms | ✅ |
| Task Overhead | N/A | <3% | ✅ |

**Note**: Import time of 9ms achieved after Phase 2 completion (migration from Pydantic to dataclasses)

## Installation

```bash
pip install litecrew-langchain
```

Or from source:
```bash
git clone https://gitlab.com/eof3/litecrewai.git
cd litecrewai/litecrew-langchain
pip install -e .
```

## Migration from CrewAI

The API is designed to be compatible with CrewAI:

```python
# Your existing CrewAI code works with minimal changes
from litecrew import Agent, Crew, Task  # Just change import!

# Rest of your code remains the same
agent = Agent(role="...", goal="...", backstory="...")
```

## Architecture

LiteCrew is built as a thin layer on top of LangChain:
- Uses LangChain's efficient agent system
- Adds CrewAI-style role-based configuration
- Implements multi-agent orchestration
- Maintains minimal dependencies

## Development

```bash
# Setup development environment
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# Run benchmarks
python benchmarks/performance_test.py
```

## License

MIT License - see LICENSE file

## Credits

Inspired by CrewAI's excellent API design, implemented with LangChain's efficient core.