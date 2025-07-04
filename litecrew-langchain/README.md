# LiteCrew-LangChain

A lightweight multi-agent orchestration framework built on LangChain, inspired by CrewAI but with 10x better performance.

## Why This Project?

Our benchmarks revealed:
- **CrewAI**: 3.268s import time, 208MB memory overhead
- **LangChain**: 0.008s import time, 17MB memory overhead
- **LiteCrew Fork**: Failed attempt, increased size instead of reducing it

This project provides CrewAI's multi-agent features on LangChain's efficient foundation.

## Project Status

**Current Phase**: 6/9 completed (67% complete)
**Production Ready**: Yes! Full Docker deployment with CI/CD

## Features

### ✅ Core Functionality (Phase 1-2)
- Role-based agents (role, goal, backstory)
- Multi-agent crew orchestration
- Task dependencies and context passing
- Sequential and hierarchical execution
- Agent delegation capabilities
- CrewAI-compatible API
- <30MB memory footprint (~17MB actual)
- <100ms startup time (9ms import)

### ✅ LLM Integration (Phase 3)
- **Multi-LLM Support** - 10+ providers with fallback chains
- **Async Operations** - Full async/await support
- **Conversation Memory** - Short-term memory with summarization

### ✅ Storage & Caching (Phase 4)
- **State Management** - Snapshots and restoration
- **Multi-level Caching** - Memory, Redis, and disk caching
- **Persistent Storage** - SQLite with versioning

### ✅ API & Monitoring (Phase 5)
- **REST API** - FastAPI endpoints for crew management
- **Web Dashboard** - Real-time monitoring
- **CLI Tools** - Command-line interface for all operations

### ✅ Production Ready (Phase 6)
- **Rate Limiting** - Token bucket algorithm with <1ms overhead
- **Token Management** - Accurate counting and budget control
- **Structured Outputs** - Dataclass models with validation
- **Event System** - Pub/sub with lifecycle callbacks
- **Docker Deployment** - Full containerization with CI/CD

### 🚧 Coming Soon (Phase 7-9)
- **Advanced Memory** - Long-term, RAG, entity tracking
- **Advanced Orchestration** - Planning, conditional flows, consensus
- **Production Features** - Testing framework, debugging, human-in-the-loop

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

### Advanced Usage Examples

#### Rate Limiting & Budget Management
```python
# Create agent with rate limiting
agent = LiteAgent(
    role="Analyst",
    goal="Analyze data efficiently",
    backstory="Data analysis expert",
    max_rpm=60,  # Max 60 requests per minute
    track_tokens=True,
    budget_limit=10.0  # $10 daily budget
)
```

#### Structured Outputs
```python
from dataclasses import dataclass
from typing import List

@dataclass
class AnalysisResult:
    summary: str
    key_findings: List[str]
    confidence: float

agent = LiteAgent(
    role="Analyst",
    goal="Provide structured analysis",
    backstory="Expert analyst",
    output_dataclass=AnalysisResult,
    auto_fix_outputs=True
)
```

#### Event System
```python
from litecrew.events import EventEmitter, EventType

# Create event emitter
emitter = EventEmitter()

# Subscribe to events
def on_task_complete(data):
    print(f"Task completed: {data['task']}")

emitter.on(EventType.TASK_COMPLETED, on_task_complete)

# Create crew with events
crew = LiteCrew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    event_emitter=emitter
)
```

## Performance

| Metric | CrewAI | LiteCrew | Improvement |
|--------|---------|----------|-------------|
| Import Time | 3.268s | 0.009s | 363x faster |
| Memory Usage | 208MB | ~17MB | 12x less |
| Agent Creation | >100ms | <5ms | 20x faster |
| Task Execution Overhead | ~15% | <3% | 5x less |
| Rate Limiting Overhead | N/A | <1ms | ✅ |
| Event Dispatch | N/A | 0.011ms | ✅ |

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

## Deployment

LiteCrew is fully containerized and production-ready:

```bash
# Local development with Docker
docker-compose up -d

# Access endpoints
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Dashboard: http://localhost:8000/
```

Production deployment uses GitLab CI/CD:
1. Push to `main` branch
2. CI/CD builds Docker image
3. Automatic deployment to server
4. Zero-downtime updates

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for details.

## License

MIT License - see LICENSE file

## Credits

Inspired by CrewAI's excellent API design, implemented with LangChain's efficient core.