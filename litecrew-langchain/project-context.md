# LiteCrewAI - Project Context

## 🎯 Quick Overview

**LiteCrewAI** is a lightweight fork of CrewAI focused on personal use with minimal resource consumption, privacy-first approach, and cost-effectiveness. The project aims to create an AI agent orchestration platform that runs efficiently on modest hardware while maintaining full functionality.

## 📏 Current Status

- **Phase**: 6/9 completed ✅ (Phase 1-6 completed ✅)
- **Current Work**: Containerization completed! Ready for deployment to Droplet
- **Environment**: Local development (Docker ready)
- **Current Branch**: feature/phase-2-block-1
- **Last Update**: 2025-01-04 16:30
- **Docker Status**: ✅ Build successful, API running in containers
- **Completed Phases**:
  - Phase 0: Infrastructure (97%) ✅
  - Phase 1: Cleanup & Optimization (100%) ✅
  - Phase 2: Core Engine (100%) ✅
  - Phase 3: LLM Integration Layer (100%) ✅
  - Phase 4: Storage Layer (100%) ✅
  - Phase 5: API & Dashboard (100%) ✅
  - Phase 6: Production Readiness (100%) ✅

## 🚀 Quick Start

### Access the System

```bash
# SSH to server (port 2222!)
ssh -p 2222 -i ~/.ssh/id_rag litecrewai@46.101.181.183

# Access endpoints
Dashboard: http://46.101.181.183:8000/dashboard
Health: http://46.101.181.183:8000/health
API Docs: http://46.101.181.183:8000/docs
```

### Local Development

```bash
# Clone repository
git clone https://gitlab.com/eof3/litecrewai.git
cd litecrewai

# Option 1: Docker (recommended)
docker-compose up -d
# Access at http://localhost:8000

# Option 2: Virtual environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"
python -m uvicorn app.main:app --reload
```

### Docker Configuration
- **Ports**: API:8000, Redis:6380, PostgreSQL:5433
- **Images**: Python 3.11-slim, Redis 7-alpine, PostgreSQL 15-alpine
- **Build**: Multi-stage for optimization (~200MB final image)
- **Health checks**: Configured for all services

## 🏗️ Architecture

### Infrastructure
- **Server**: DigitalOcean Droplet (2GB RAM, Ubuntu 24.10)
- **Deployment**: Hybrid (App in Docker, services native)
- **Storage**: SQLite for data, Redis for cache
- **LLM**: Local Ollama with mistral:7b, phi3:mini, nomic-embed-text

### Tech Stack
- **Backend**: Python 3.12, FastAPI
- **Monitoring**: Custom SQLite-based metrics, Prometheus endpoint
- **Logging**: JSON structured logs with rotation
- **CI/CD**: GitLab with automatic rollback
- **Security**: Fail2ban, UFW, automatic updates

## 📁 Project Structure

```
/opt/litecrewai/
├── app/              # Application code
│   ├── core/         # Core modules (logging, metrics, alerts)
│   ├── api/          # API endpoints and dashboard
│   └── main.py       # FastAPI application
├── scripts/          # Maintenance and deployment scripts
├── masterplan/       # Technical documentation (8 phases)
├── docs/            # User documentation
├── data/            # SQLite databases
├── logs/            # Application logs (rotated daily)
├── config/          # Configuration files
├── backups/         # Automated backups
└── venv/            # Python virtual environment
```

## 🔐 Security & Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
# Critical - must be set!
OPENAI_API_KEY=your-key
SECRET_KEY=generate-long-random-string
METRICS_USERNAME=choose-username
METRICS_PASSWORD=strong-password

# Telegram alerts (optional)
ALERT_WEBHOOK_URL=telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

### Security Features
- No hardcoded credentials
- Fail2ban with IP whitelist
- Automatic security updates
- Environment-based configuration
- Rate limiting on all endpoints

## 🛠️ Development Workflow

### Code Quality
```bash
# Format code
black app/

# Lint
ruff check app/

# Type check
mypy app/

# Run tests
pytest

# Pre-commit hooks (automatic)
pre-commit run --all-files
```

### Deployment
```bash
# Manual deployment
git push origin main
# Then in GitLab: manually trigger deploy job

# Rollback if needed
# In GitLab: trigger rollback job
```

### Monitoring
```bash
# View logs
ssh -p 2222 -i ~/.ssh/id_rag litecrewai@46.101.181.183 'tail -f /opt/litecrewai/logs/app.log'

# Check metrics
curl http://46.101.181.183:8000/metrics

# Run validation
ssh -p 2222 -i ~/.ssh/id_rag litecrewai@46.101.181.183 '/opt/litecrewai/masterplan/src/faza-0/validate_monitoring.py'
```

## 📊 Key Metrics & Goals

### Performance Targets
- **Memory**: <10MB per agent
- **Startup**: <100ms
- **Cost**: <$30/month infrastructure
- **Response**: <2s for typical operations

### Current Performance
- **Memory**: ~200MB total (app + services)
- **Uptime**: 99.9%
- **Cost**: ~$24/month (DigitalOcean droplet)
- **LLM**: Ollama generation ~5s (hardware limited)

## 🗺️ Roadmap

### Completed ✅
- **Phase 0**: Infrastructure and environment setup (97%)
- **Phase 1**: Cleanup & Optimization (100%)
  - Removed telemetry, enterprise features, cloud dependencies
  - Migrated from Pydantic to dataclasses
  - Achieved 9ms import time (363x faster than CrewAI)
- **Phase 2**: Core Engine Implementation (100%)
  - Implemented LiteAgent, LiteTask, LiteCrew
  - Added context management and delegation
  - Full CrewAI API compatibility
- **Phase 3 Block 3.1**: Multi-LLM Support ✅
  - Added support for 10+ LLM providers
  - Implemented LLM fallback chains
  - Added response caching with LRU
  - Provider-specific optimizations
- **Phase 3 Block 3.2**: Streaming & Async ✅
  - Implemented async/await for all LLM calls
  - Added streaming response support
  - Created batch processing for efficiency
  - Added progress callbacks
  - Full async crew execution
- **Phase 3 Block 3.3**: Conversation Memory ✅
  - Implemented short-term memory per session
  - Added memory summarization with compression
  - Created memory search with relevance scoring
  - Implemented memory limits and LRU eviction
  - Added persistence hooks for save/load
  - Crew shared memory support
- **Phase 4 Block 4.1**: Result Storage ✅
  - SQLite storage backend with versioning
  - Redis cache layer with fallback
  - Storage abstraction with compression
  - Automatic result versioning
  - Comprehensive persistence tests
- **Phase 4 Block 4.2**: State Management ✅
  - Crew state snapshots with compression
  - State restoration with integrity checks
  - Incremental state updates
  - State migration system
  - State validation and recovery tests
- **Phase 4 Block 4.3**: Caching Strategy ✅
  - Multi-level cache (L1: memory, L2: Redis, L3: disk)
  - Cache invalidation with patterns
  - Cache warming and preloading
  - Detailed cache metrics
  - Cache policies and configuration

- **Phase 5**: API & Dashboard (100%) ✅
  - Block 5.1: REST API ✅
  - Block 5.2: Monitoring Dashboard ✅
  - Block 5.3: CLI Tools ✅
- **Phase 6**: Production Readiness (100%) ✅
  - Block 6.1: Rate Limiting & Token Management ✅
  - Block 6.2: Structured Outputs ✅
  - Block 6.3: Event System & Callbacks ✅

### Next Steps
1. **Immediate**: Deploy to DigitalOcean Droplet
   - Configure GitLab CI/CD variables
   - Merge to main branch
   - Trigger deployment pipeline
   - No source code on production - only Docker images!

2. **Phase 7**: Advanced Memory & Knowledge (5 dni)
   - **Block 7.1**: Long-term Memory
     - Persistent memory store with indexing
     - Memory importance scoring and decay
     - Memory compression for efficiency
   - **Block 7.2**: Knowledge Base & RAG
     - Vector database integration (ChromaDB/FAISS)
     - Document ingestion and semantic search
     - Source tracking and knowledge updates
   - **Block 7.3**: Entity & Contextual Memory
     - Entity extraction and relationship tracking
     - Cross-session memory with privacy controls
     - Contextual memory layers

3. **Phase 8**: Advanced Orchestration (5 dni)
   - **Block 8.1**: Planning & Reasoning
     - Dynamic task planning with goal decomposition
     - Reasoning chains and plan validation
     - Automatic plan optimization
   - **Block 8.2**: Conditional Flows
     - If/else branching in task flows
     - Loop constructs and flow validation
     - Visual flow debugging
   - **Block 8.3**: Consensus & Voting
     - Multi-agent consensus mechanisms
     - Weighted voting and conflict resolution
     - Quality scoring with minority reports

4. **Phase 9**: Production Features (5 dni)
   - **Block 9.1**: Testing & Evaluation
     - Comprehensive crew testing framework
     - Performance benchmarks and quality metrics
     - A/B testing and regression tests
   - **Block 9.2**: Debugging & Observability
     - Execution tracing with <5% overhead
     - Debug mode and conversation replay
     - Metrics export and alerting
   - **Block 9.3**: Human-in-the-loop
     - Human approval flows and feedback collection
     - Override mechanisms and training mode
     - Complete audit trails

## 🆘 Troubleshooting

### Common Issues

**SSH Connection Refused**
- Check port 2222 (not 22!)
- Verify IP whitelist in fail2ban
- Try from web console if blocked

**Application Not Responding**
```bash
# Restart application
ssh -p 2222 -i ~/.ssh/id_rag litecrewai@46.101.181.183
cd /opt/litecrewai
pkill -f uvicorn
nohup venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/app.stdout.log 2>&1 &
```

**Metrics Not Collecting**
```bash
# Check aggregation timer
sudo systemctl status litecrewai-metrics-aggregation.timer
# Manual aggregation
/opt/litecrewai/venv/bin/python /opt/litecrewai/scripts/aggregate_metrics.py
```

## 🔗 Important Links

- **GitLab Repository**: https://gitlab.com/eof3/litecrewai
- **Production App**: http://46.101.181.183:8000
- **Documentation**: See `/masterplan/` directory
- **Monitoring Guide**: `/docs/monitoring-guide.md`

## 👥 Contact & Support

- **Issues**: Create in GitLab repository
- **Alerts**: Configure Telegram bot (see .env.example)
- **Logs**: Available in `/opt/litecrewai/logs/`

## 📈 Project Completion Summary

### What We've Achieved (Phases 1-6):
- **Performance**: 363x faster import than CrewAI (9ms vs 3.3s)
- **Memory**: 12x less RAM usage (17MB vs 208MB)
- **Features**: 100% CrewAI API compatibility
- **Production Ready**: Full containerization with CI/CD
- **Advanced Features**: Multi-LLM, async, caching, API, dashboard

### What's Coming (Phases 7-9):
- **Phase 7** (5 days): Enterprise-grade memory systems
  - Long-term persistent memory with decay
  - RAG integration for knowledge management
  - Entity tracking and contextual awareness
- **Phase 8** (5 days): Advanced AI orchestration
  - Intelligent planning and reasoning
  - Complex conditional workflows
  - Multi-agent consensus mechanisms
- **Phase 9** (5 days): Production excellence
  - Comprehensive testing framework
  - Full observability and debugging
  - Human oversight and control

### Final Deliverable:
A complete, production-ready alternative to CrewAI that is:
- 10x more efficient in resources
- 100% compatible with existing code
- Enterprise-ready with advanced features
- Fully observable and debuggable
- Human-controllable with audit trails

## 🎯 Key Decisions Made

1. **Full Containerization**: Everything runs in Docker
2. **GitLab CI/CD**: Automated deployment pipeline
3. **No Source on Production**: Only Docker images deployed
4. **Dataclasses over Pydantic**: Lightweight approach
5. **Multi-LLM Support**: Flexibility for different providers
6. **Event-Driven Architecture**: For extensibility

## ⚠️ Known Limitations

1. **Ollama Speed**: >3s generation due to 2GB RAM limit
2. **Single Server**: No HA/clustering yet
3. **Manual Deployment**: GitLab CI requires manual trigger
4. **Limited Models**: Only 3 Ollama models due to space

---

**Remember**: 
- Always check SECURITY.md before implementing features
- Use environment variables for ALL secrets
- Test locally before deploying
- Monitor logs and metrics regularly