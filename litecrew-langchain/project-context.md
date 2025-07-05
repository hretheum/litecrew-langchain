# LiteCrewAI - Project Context

## 🎯 Quick Overview

**LiteCrewAI** is a lightweight fork of CrewAI focused on personal use with minimal resource consumption, privacy-first approach, and cost-effectiveness. The project aims to create an AI agent orchestration platform that runs efficiently on modest hardware while maintaining full functionality.

## 📏 Current Status

- **Phase**: Ready for Phase 3 Block 3.1 (Multi-LLM Support)
- **Current Work**: CI/CD pipeline fixed, ready for deployment
- **Environment**: Local development (Docker ready)
- **Current Branch**: feature/phase-3-block-1 (ready to merge)
- **Last Update**: 2025-07-05 14:10
- **CI/CD Status**: ✅ All checks passing
- **Completed Phases**:
  - Phase 0: Infrastructure (97%) ✅
  - Phase 1: Cleanup & Optimization (100%) ✅
  - Phase 2: Core Engine (100%) ✅

## 🚨 IMMEDIATE NEXT STEPS

### 1. Deploy to DigitalOcean Droplet (152.42.139.18)

**Prerequisites**:
- SSH access: `ssh -p 2222 litecrewai@152.42.139.18` (key: ~/.ssh/id_rag)
- GitLab CI/CD variables need to be set:
  ```
  SSH_PRIVATE_KEY     = [content of ~/.ssh/id_rag]
  DROPLET_IP          = 152.42.139.18
  CI_REGISTRY_USER    = [GitLab username]
  CI_REGISTRY_PASSWORD = [GitLab Personal Access Token]
  OPENAI_API_KEY      = [your OpenAI key]
  SECRET_KEY          = [generate secure random string]
  JWT_SECRET          = [generate another secure random string]
  DB_PASSWORD         = [generate secure password]
  ```

**Deployment Steps**:
1. Merge feature/phase-3-block-1 to master (auto-merge set up)
2. Wait for pipeline to complete (tests, build)
3. Manually trigger deploy:production job in GitLab
4. Verify deployment at http://152.42.139.18:8000

### 2. CI/CD Pipeline Issues Fixed

**What was fixed**:
- ✅ Black formatting issues
- ✅ mypy type checking errors
- ✅ ruff linting problems
- ✅ Bandit security issues (13 total)
- ✅ GitLeaks secrets detection
- ✅ Docker build path issues
- ✅ Test timeouts for CI environment
- ✅ Coverage artifact path

**GitLeaks false positives added to .gitleaksignore**:
- Example API keys in SECURITY.md
- Auth0 public client ID (not a secret)
- Test JWT tokens in fixtures
- False positives in minified JS

## 🚀 Quick Start

### Access the System (after deployment)

```bash
# SSH to server (port 2222!)
ssh -p 2222 -i ~/.ssh/id_rag litecrewai@152.42.139.18

# Access endpoints
Dashboard: http://152.42.139.18:8000/dashboard
Health: http://152.42.139.18:8000/health
API Docs: http://152.42.139.18:8000/docs
```

### Local Development

```bash
# Clone repository
git clone https://gitlab.com/eof3/litecrewai.git
cd litecrewai/litecrew-langchain

# Option 1: Docker (recommended)
docker-compose up -d
# Access at http://localhost:8000

# Option 2: Virtual environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
python -m litecrew.api
```

### Docker Configuration
- **Ports**: API:8000, Redis:6379 (disabled), PostgreSQL:5432 (disabled)
- **Images**: Python 3.12-slim base
- **Build**: Multi-stage for optimization
- **Health checks**: Configured for API service

## 🏗️ Architecture

### Infrastructure
- **Server**: DigitalOcean Droplet (2GB RAM, Ubuntu)
- **Deployment**: Docker-based via GitLab CI/CD
- **Storage**: SQLite for data (future: Redis for cache)
- **LLM**: Multiple providers (OpenAI, Anthropic, Groq, Ollama)

### Tech Stack
- **Core**: Python 3.12, LangChain 0.3.26
- **API**: FastAPI 0.115.14
- **Testing**: pytest with 70%+ coverage
- **CI/CD**: GitLab with security scanning
- **Security**: Bandit, GitLeaks, Trivy

## 📁 Project Structure

```
litecrew-langchain/
├── src/litecrew/     # Main package
│   ├── agent.py      # LiteAgent implementation
│   ├── crew.py       # LiteCrew orchestration
│   ├── task.py       # LiteTask definition
│   ├── config.py     # Configuration management
│   ├── api/          # FastAPI application
│   ├── cli/          # CLI commands
│   ├── llm/          # Multi-LLM support
│   ├── memory/       # Memory systems
│   ├── storage/      # Persistence layer
│   └── cache/        # Caching strategies
├── tests/            # Comprehensive test suite
├── benchmarks/       # Performance benchmarks
├── docs/             # Documentation
├── Dockerfile        # Container definition
├── docker-compose.yml # Local development
└── .gitlab-ci.yml    # CI/CD pipeline
```

## 📊 Key Metrics & Goals

### Performance Targets
- **Import time**: <0.05s (current: ~0.009s ✅)
- **Memory**: <30MB (current: ~17MB ✅)
- **Agent creation**: <10ms (current: <5ms ✅)
- **Task execution overhead**: <5% (current: <3% ✅)
- **Test coverage**: >90% (current: 70% ⚠️)

### Current Performance
- **Import**: 9ms (363x faster than CrewAI)
- **Memory**: ~17MB (12x less than CrewAI)
- **API Compatibility**: 100% with CrewAI

## 🗺️ Roadmap

### Completed ✅
- **Phase 0**: Infrastructure and environment setup (97%)
- **Phase 1**: Cleanup & Optimization (100%)
  - Removed telemetry, enterprise features
  - Migrated to lightweight dependencies
  - Achieved sub-10ms import time
- **Phase 2**: Core Engine Implementation (100%)
  - Implemented LiteAgent, LiteTask, LiteCrew
  - Added context management and delegation
  - Full CrewAI API compatibility

### In Progress 🚧
- **Phase 3**: LLM Integration Layer
  - Block 3.1: Multi-LLM Support (Next)
    - [ ] Support for 10+ LLM providers
    - [ ] LLM fallback chains
    - [ ] Response caching with LRU
    - [ ] Provider-specific optimizations
  - Block 3.2: Streaming & Async
  - Block 3.3: Conversation Memory

### Upcoming
- **Phase 4**: Storage & Persistence Layer
- **Phase 5**: API & Dashboard
- **Phase 6**: Production Readiness
- **Phase 7**: Advanced Memory & Knowledge
- **Phase 8**: Advanced Orchestration
- **Phase 9**: Production Features

## 🔐 Security & Configuration

### Environment Variables
```bash
# Required for production
OPENAI_API_KEY=your-key
SECRET_KEY=generate-long-random-string
JWT_SECRET=another-random-string
DB_PASSWORD=secure-password

# Optional providers
ANTHROPIC_API_KEY=your-key
GROQ_API_KEY=your-key
OLLAMA_BASE_URL=http://localhost:11434

# Development
ENVIRONMENT=development  # or production
DEBUG=false
```

### Security Features
- No hardcoded credentials
- Environment-based configuration
- Security scanning in CI/CD
- Rate limiting on all endpoints
- Input validation everywhere

## 🛠️ Development Workflow

### Code Quality
```bash
# Format code
black src/ tests/

# Lint
ruff check src/

# Type check
mypy src/ --ignore-missing-imports

# Security scan
bandit -r src/

# Run tests
pytest tests/ -v --cov=src/litecrew --cov-fail-under=70

# Check everything (like CI/CD)
black src/ tests/ && ruff check src/ && mypy src/ --ignore-missing-imports && bandit -r src/ && pytest
```

### GitLab CI/CD Pipeline
```
stages:
  - test (unit tests, linting, coverage)
  - security (Bandit, GitLeaks, Trivy)
  - build (Docker image)
  - deploy (manual trigger to production)
```

### Deployment Process
1. Push to feature branch
2. Create MR, wait for pipeline
3. Merge to master (auto-merge configured)
4. Pipeline runs again on master
5. Manually trigger deploy:production
6. Automatic health checks and rollback if needed

## ⚠️ Known Issues & Solutions

### GitLeaks False Positives
- All handled in .gitleaksignore
- Includes test fixtures and example keys
- Both root and litecrew-langchain directories

### Test Timeouts in CI
- Increased timeouts for slower CI runners
- API tests: 2s timeout
- Execution tests: 30s timeout
- Async tests: adjusted for CI environment

### Coverage Artifacts
- Fixed path issue by copying to root
- Coverage report properly uploaded

## 🆘 Troubleshooting

### Pipeline Failures
```bash
# Check locally before push
black src/ tests/
ruff check src/
mypy src/ --ignore-missing-imports
bandit -r src/
gitleaks detect --source . --verbose
pytest tests/ -v
```

### Docker Issues
```bash
# Build locally
docker build -t litecrew-langchain:test .

# Test with Trivy
trivy image litecrew-langchain:test

# Run locally
docker run -p 8000:8000 litecrew-langchain:test
```

## 📈 Project Status Summary

### What's Done:
- ✅ Core engine with full CrewAI compatibility
- ✅ Clean, optimized codebase
- ✅ Docker containerization
- ✅ CI/CD pipeline with security scanning
- ✅ 70% test coverage
- ✅ Ready for deployment

### What's Next:
1. **Immediate**: Deploy to Droplet
2. **Phase 3.1**: Multi-LLM Support
3. **Phase 3.2**: Streaming & Async
4. **Phase 3.3**: Conversation Memory

### Critical Information:
- **Droplet IP**: 152.42.139.18
- **SSH Port**: 2222 (not 22!)
- **GitLab Repo**: https://gitlab.com/eof3/litecrewai
- **Docker Registry**: registry.gitlab.com/eof3/litecrewai
- **Current Branch**: feature/phase-3-block-1

---

**Remember**: 
- Always test locally before pushing
- Update this file when starting new work
- Check SECURITY.md for security guidelines
- Monitor pipeline after push