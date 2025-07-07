# LiteCrewAI - Project Context

## 🎯 Quick Overview

**LiteCrewAI** is a lightweight fork of CrewAI focused on personal use with minimal resource consumption, privacy-first approach, and cost-effectiveness. The project aims to create an AI agent orchestration platform that runs efficiently on modest hardware while maintaining full functionality.

## 📏 Current Status

- **Phase**: Phase 7 - User-Friendly Execution 🚧
- **Current Work**: Block 7.1 - API Quick Start Features
- **Environment**: Production deployment on DigitalOcean
- **Deployment URL**: https://api.litecrew.app
- **Last Update**: 2025-07-07 (Starting Phase 7)
- **Current Issue**: Implementing quick start API endpoints
- **Current Branch**: feat/user-friendly-execution
- **CI/CD Status**: ✅ Fully operational pipeline with security scanning
- **Latest Deployment**: SHA `5d8c83d0` (2025-07-06 18:53)
- **Completed Major Features**:
  - ✅ Core LiteCrew engine (Agent, Task, Crew)
  - ✅ Multi-LLM support (OpenAI, Anthropic, Groq, Ollama)
  - ✅ FastAPI with security (auth, rate limiting, CORS)
  - ✅ Comprehensive testing suite (473 tests, 72.7% coverage)
  - ✅ Docker containerization + CI/CD deployment
  - ✅ Local development tooling + pipeline testing script
  - ✅ HTTPS with Cloudflare Origin Certificate + Nginx reverse proxy
  - ✅ Multi-Process Engine (Sequential, Conversational, Debate, Panel)
  - ✅ Agent Type System (Conversational, Thinking, Moderator, Critic)

## 🎯 CURRENT STATUS SUMMARY

### ✅ PRODUCTION DEPLOYMENT COMPLETE

**Live Application**: https://api.litecrew.app
- ✅ API Documentation: https://api.litecrew.app/docs
- ✅ OpenAPI Spec: https://api.litecrew.app/openapi.json
- ✅ Health Check: https://api.litecrew.app/api/v1/health
- ✅ Dashboard: https://api.litecrew.app/
- ✅ Container: `543728580c56` running successfully
- ✅ HTTPS: Cloudflare proxy with Origin Certificate
- ✅ Nginx: Reverse proxy on port 443

### 🔧 MAJOR FIXES COMPLETED (MR #24)

**Test Infrastructure**:
- ✅ Fixed all 39 failing tests (OAuth, CLI, LLM Manager)
- ✅ 445 tests now passing (was 406 failing)
- ✅ Test coverage: 72.7% (>70% requirement met)
- ✅ Local pipeline testing script: `./run_pipeline_locally.sh`

**Security Implementation**:
- ✅ API key authentication middleware
- ✅ Rate limiting (60/600 req/min unauth/auth)
- ✅ Security headers and CORS restrictions
- ✅ Google OAuth integration (optional)
- ✅ All Bandit security warnings resolved

**CI/CD Pipeline Enhancements**:
- ✅ Added lint stage (black, ruff, mypy)
- ✅ Enhanced security scanning (bandit, safety, pip-audit)
- ✅ Fixed flaky test timeouts for CI environment
- ✅ Proper coverage reporting and artifacts

## 🚀 Quick Start

### Access the System (after deployment)

```bash
# SSH to server
ssh -i ~/.ssh/id_rag litecrewai@152.42.139.18

# Access endpoints
Dashboard: https://api.litecrew.app/dashboard
Health: https://api.litecrew.app/api/v1/health
API Docs: https://api.litecrew.app/docs
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
- **Server**: DigitalOcean Droplet (2GB RAM, Ubuntu 24.04)
- **Domain**: litecrew.app (with api subdomain)
- **SSL/TLS**: Cloudflare proxy + Origin Certificate
- **Reverse Proxy**: Nginx (port 443 → localhost:8000)
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
- **Test coverage**: >70% (current: 72.7% ✅)

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

### Recently Completed ✅
- **Security & Testing**: Comprehensive implementation
  - ✅ API authentication and authorization
  - ✅ Rate limiting and security headers
  - ✅ 445 passing tests with 72.7% coverage
  - ✅ Local pipeline testing tooling
- **Multi-LLM Support**: Core implementation
  - ✅ Support for 10+ LLM providers (OpenAI, Anthropic, Groq, Ollama, etc.)
  - ✅ LLM fallback chains with error handling
  - ✅ Provider-specific configurations
  - ✅ Response caching and metrics tracking

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

### Next Priorities:
1. **Enhancement**: Streaming & Async capabilities
2. **Features**: Advanced conversation memory
3. **Performance**: Response caching optimizations
4. **Monitoring**: Production observability and metrics

### Critical Information:
- **Production URL**: https://api.litecrew.app
- **Direct Access**: http://152.42.139.18:8000 (bypasses Cloudflare)
- **SSH Access**: `ssh litecrewai@152.42.139.18` (port 22)
- **GitLab Repo**: https://gitlab.com/eof3/litecrewai
- **Docker Registry**: registry.gitlab.com/eof3/litecrewai
- **Current Branch**: master
- **Latest Deploy**: SHA `5d8c83d0` (2025-07-06)
- **Local Testing**: Use `./run_pipeline_locally.sh` before commits

---

**Remember**: 
- Always test locally before pushing
- Update this file when starting new work
- Check SECURITY.md for security guidelines
- Monitor pipeline after push