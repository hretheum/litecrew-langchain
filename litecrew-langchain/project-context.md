# LiteCrewAI - Project Context

## 🎯 Quick Overview

**LiteCrewAI** is a lightweight fork of CrewAI focused on personal use with minimal resource consumption, privacy-first approach, and cost-effectiveness. The project aims to create an AI agent orchestration platform that runs efficiently on modest hardware while maintaining full functionality.

## 📍 Current Status

- **Phase**: 2/9 in progress (Phase 1 completed ✅, Block 2.1 completed ✅, Block 2.2 completed ✅, Block 2.3 completed ✅, Block 2.4 completed ✅)
- **Current Work**: Phase 2 - Core Engine (Post-work tasks)
- **Environment**: Local development
- **Next Block**: Phase 3 - LLM Integration (Dzień 13-16)
- **Last Update**: 2025-07-03

### 🔥 Critical Issue RESOLVED ✅
- Import time: Reduced from 82ms to 9ms (89% reduction!)
- Migration: Pydantic → dataclasses with PydanticCompatible mixin
- Results: Import <10ms ✅, memory -7MB ✅, 100% API compatibility ✅

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

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Run locally
python -m uvicorn app.main:app --reload
```

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
- **Phase 1 Block 1.1**: Fork and Initial Cleanup
  - Forked CrewAI repository
  - Removed all telemetry and analytics
  - Removed enterprise features
  - Simplified to single-user mode

### Next Steps
1. **Phase 1 Block 1.2**: Dependency Optimization
2. **Phase 2**: Implement lightweight agent engine
3. **Phase 3**: LLM provider integrations
4. **Phase 4**: Storage layer (SQLite + Redis)
5. **Phase 5**: REST API and web dashboard
6. **Phase 6**: Monitoring and observability
7. **Phase 7**: Production deployment
8. **Phase 8**: Documentation and examples

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

## 🎯 Key Decisions Made

1. **Hybrid Deployment**: App in Docker, services native (for flexibility)
2. **Python 3.12**: Instead of 3.11 (better performance)
3. **SQLite Storage**: For simplicity and portability
4. **Local LLM**: Ollama for privacy and cost control
5. **No JavaScript**: Dashboard uses htmx for simplicity
6. **SSH Port 2222**: For additional security

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