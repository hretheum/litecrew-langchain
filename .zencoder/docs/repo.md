# LiteCrew Project Information

## Summary
LiteCrew is a lightweight multi-agent orchestration framework built on LangChain, designed as a high-performance alternative to CrewAI. The project focuses on providing CrewAI's multi-agent features with significantly better performance metrics, including 363x faster import time and 12x less memory usage.

## Structure
- **litecrew-langchain/**: Main implementation with source code, tests, benchmarks, and documentation
- **benchmark-archive/**: Historical benchmark data and performance testing tools
- **masterplan/**: Original planning documents and implementation phases
- **scripts/**: Utility scripts for deployment, dependency management, and monitoring

## Language & Runtime
**Language**: Python
**Version**: Python 3.10+ (supports 3.10, 3.11, 3.12)
**Build System**: setuptools
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- langchain (>=0.2.1): Core framework for AI agent functionality
- langchain-openai (>=0.1.8): OpenAI integration
- pydantic (>=2.0): Data validation and settings management
- fastapi (>=0.104.0): API framework
- uvicorn (>=0.24.0): ASGI server
- sqlalchemy (>=2.0.0): Database ORM
- redis (>=5.0.1): Caching and message broker

**Development Dependencies**:
- pytest (>=7.4.0): Testing framework
- black (>=23.0.0): Code formatter
- ruff (>=0.1.0): Linter
- mypy (>=1.5.0): Type checking

## Build & Installation
```bash
# Install from PyPI
pip install litecrew-langchain

# Install from source
git clone https://gitlab.com/eof3/litecrewai.git
cd litecrewai/litecrew-langchain
pip install -e .

# Run tests
pytest tests/ -v --cov=src/litecrew --cov-fail-under=70
```

## Docker
**Dockerfile**: litecrew-langchain/Dockerfile
**Image**: Python 3.11-slim multi-stage build
**Configuration**: Docker Compose with Redis and PostgreSQL services
**Run Command**:
```bash
docker-compose up -d
# API available at http://localhost:8000
```

## Main Components
**Core Framework**:
- **Agent System**: Role-based agents with goals and backstories
- **Task Management**: Task dependencies and context passing
- **Process Types**: Sequential, hierarchical, conversational, and panel execution
- **LLM Integration**: Support for multiple LLM providers with fallback chains

**API & Services**:
- **REST API**: FastAPI endpoints for crew management
- **WebSocket**: Real-time updates during execution
- **Dashboard**: Monitoring interface for crew execution
- **CLI Tools**: Command-line interface for operations

**Storage & Caching**:
- **State Management**: Snapshots and restoration
- **Multi-level Caching**: Memory, Redis, and disk caching
- **Persistent Storage**: SQLite with versioning

## Testing
**Framework**: pytest with pytest-asyncio and pytest-cov
**Test Location**: litecrew-langchain/tests/
**Naming Convention**: test_*.py
**Test Types**: Unit, integration, and end-to-end tests
**Run Command**:
```bash
pytest tests/ -v --cov=src/litecrew
```

## Project Status
- Current Phase: Production Deployed
- Test Coverage: 72.7% (445 tests passing)
- Performance: All targets exceeded
- API: Live at https://api.litecrew.app