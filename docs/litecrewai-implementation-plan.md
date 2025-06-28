# 🚀 LiteCrewAI Implementation Guide - Complete Personal Fork

## 📝 Continuation Prompt (if context window fills):
```
Kontynuuję implementację LiteCrewAI. Mam już:
- Plan implementacji w 7 fazach
- [COMPLETED]: Fazy 0-X, Starter Scripts Y/5, Moduły Z/8
- [CURRENT]: Pracuję nad [NAZWA_SEKCJI]
- [TODO]: Lista pozostałych elementów

Proszę kontynuować od miejsca gdzie skończyłem, dodając kolejne implementacje do artefaktu.
```

---

# 🚀 Plan implementacji LiteCrewAI - od zera do działającego systemu

## Faza 0: Setup infrastruktury (Dzień 1-2)

### Blok 0.1: Przygotowanie DigitalOcean
```yaml
Zadania atomowe:
  - 0.1.1: Utworzenie konta DO i dodanie metody płatności
  - 0.1.2: Wygenerowanie API token
  - 0.1.3: Instalacja doctl CLI lokalnie
  - 0.1.4: Utworzenie SSH key pair
  - 0.1.5: Utworzenie dropletu

Metryki sukcesu:
  - SSH do dropletu działa: ssh root@<IP> zwraca prompt
  - doctl compute droplet list pokazuje droplet
  - curl http://<IP> zwraca connection refused (jeszcze nic nie działa)

Walidacja:
  - Test: ssh_connection_test.sh
    #!/bin/bash
    ssh -o ConnectTimeout=5 root@$DROPLET_IP "echo 'SSH OK'" || exit 1
```

### Blok 0.2: Setup podstawowego środowiska
```yaml
Zadania atomowe:
  - 0.2.1: Utworzenie użytkownika non-root 'litecrewai'
  - 0.2.2: Setup firewall (ufw) - tylko 22,80,443
  - 0.2.3: Instalacja Python 3.11, git, redis, nginx
  - 0.2.4: Konfiguracja swap (2GB dla bezpieczeństwa)
  - 0.2.5: Setup systemd service files (szablony)

Metryki sukcesu:
  - python3.11 --version zwraca 3.11.x
  - redis-cli ping zwraca PONG
  - systemctl status nginx pokazuje active
  - free -h pokazuje 2G swap

Testy:
  - environment_check.py:
    def test_python_version():
        assert sys.version_info >= (3, 11)
    
    def test_redis_connection():
        r = redis.Redis()
        assert r.ping() == True
    
    def test_disk_space():
        usage = shutil.disk_usage('/')
        assert usage.free > 10 * 1024**3  # >10GB free
```

## Faza 1: Fork i minimalizacja CrewAI (Dzień 3-5)

### Blok 1.1: Fork i initial cleanup
```yaml
Zadania atomowe:
  - 1.1.1: Fork CrewAI na GitHub
  - 1.1.2: Clone na droplet i lokalnie
  - 1.1.3: Utworzenie brancha 'lite-personal'
  - 1.1.4: Usunięcie telemetrii (rm -rf telemetry/)
  - 1.1.5: Usunięcie enterprise features
  - 1.1.6: Update pyproject.toml - minimal deps

Metryki sukcesu:
  - grep -r "telemetry" src/ zwraca 0 wyników
  - Rozmiar repo < 50% oryginału
  - pip install -e . działa bez błędów

Code Review Checklist:
  □ Wszystkie importy telemetrii usunięte
  □ Brak wywołań do zewnętrznych analytics
  □ Configs nie zawierają enterprise flags
  □ Dependencies zredukowane do minimum

Testy:
  - test_no_telemetry.py:
    def test_no_telemetry_imports():
        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith('.py'):
                    content = open(os.path.join(root, file)).read()
                    assert 'telemetry' not in content
                    assert 'analytics' not in content
```

### Blok 1.2: Simplified Agent Engine
```yaml
Zadania atomowe:
  - 1.2.1: Przepisanie agent.py na sync-only
  - 1.2.2: Uproszczenie execution flow
  - 1.2.3: Dodanie simple retry logic
  - 1.2.4: Local LLM fallback mechanism
  - 1.2.5: Deploy i test na droplecie

Metryki sukcesu:
  - Agent wykonuje proste zadanie w <5s
  - Memory usage <100MB per agent
  - Fallback na Ollama działa

Testy jednostkowe:
  - test_lite_agent.py:
    def test_agent_creation():
        agent = LiteAgent(role="test", goal="test")
        assert agent.memory_usage() < 100 * 1024 * 1024
    
    def test_sync_execution():
        start = time.time()
        agent.execute("Say hello")
        assert time.time() - start < 5

Testy integracyjne (na droplecie):
  - integration_test_agent.sh:
    curl -X POST localhost:8000/api/agent/test \
      -d '{"task": "Hello world"}' \
      -H "Content-Type: application/json" | \
      grep -q "response"
```

## Faza 2: Storage i Cache Layer (Dzień 6-8)

### Blok 2.1: SQLite optimization
```yaml
Zadania atomowe:
  - 2.1.1: Setup SQLite z WAL mode
  - 2.1.2: Schema dla agents, tasks, memory
  - 2.1.3: Prepared statements dla performance
  - 2.1.4: Auto-vacuum i optimize pragmas
  - 2.1.5: Backup cron job

Metryki sukcesu:
  - 1000 zapisów/s do agents table
  - DB size pozostaje <1GB po 10k operations
  - Backup działa codziennie o 3AM

Testy:
  - test_sqlite_performance.py:
    def test_write_performance():
        start = time.time()
        for i in range(1000):
            db.insert_agent(f"agent_{i}")
        elapsed = time.time() - start
        assert elapsed < 1.0  # 1000 ops/sec
    
    def test_wal_mode():
        conn = sqlite3.connect('litecrewai.db')
        result = conn.execute("PRAGMA journal_mode").fetchone()
        assert result[0] == 'wal'
```

### Blok 2.2: Redis cache layer
```yaml
Zadania atomowe:
  - 2.2.1: Redis config z maxmemory 100MB
  - 2.2.2: Eviction policy: allkeys-lru
  - 2.2.3: Cache wrapper dla LLM calls
  - 2.2.4: Cache dla tool results
  - 2.2.5: Monitoring cache hit rate

Metryki sukcesu:
  - Cache hit rate >60% po 1 dniu
  - Redis memory <100MB zawsze
  - Response time <50ms dla cached

Testy:
  - test_cache_layer.py:
    def test_cache_size_limit():
        for i in range(10000):
            cache.set(f"key_{i}", "x" * 1000)
        info = redis_client.info()
        assert info['used_memory'] < 100 * 1024 * 1024
    
    def test_cache_performance():
        cache.set("test", "value")
        start = time.time()
        result = cache.get("test")
        assert time.time() - start < 0.05
```

## Faza 3: LLM Router i Cost Control (Dzień 9-11)

### Blok 3.1: Ollama integration
```yaml
Zadania atomowe:
  - 3.1.1: Install Ollama na droplecie
  - 3.1.2: Pull mistral i phi-2 models
  - 3.1.3: Ollama API wrapper
  - 3.1.4: Model warm-up on boot
  - 3.1.5: Graceful fallback logic

Metryki sukcesu:
  - Ollama odpowiada w <2s dla prostych promptów
  - Auto-start po reboot działa
  - CPU usage <80% podczas inference

Testy:
  - test_ollama_integration.py:
    def test_ollama_response_time():
        start = time.time()
        response = ollama.generate("Hi", model="mistral")
        assert time.time() - start < 2.0
    
    def test_ollama_availability():
        response = requests.get("http://localhost:11434/api/tags")
        models = response.json()['models']
        assert any('mistral' in m['name'] for m in models)
```

### Blok 3.2: Smart routing i budget control
```yaml
Zadania atomowe:
  - 3.2.1: Task complexity analyzer
  - 3.2.2: Cost tracking w SQLite
  - 3.2.3: Budget alerts via email/webhook
  - 3.2.4: Automatic quality downgrade
  - 3.2.5: Daily cost report generator

Metryki sukcesu:
  - 80% zadań idzie do local LLM
  - Miesięczny koszt <$30
  - Alert działa przy 80% budżetu

Testy:
  - test_budget_control.py:
    def test_complexity_routing():
        simple = analyze_complexity("What is 2+2?")
        assert simple == "local"
        
        complex = analyze_complexity("Write a 1000 word essay...")
        assert complex == "openai"
    
    def test_budget_enforcement():
        set_monthly_budget(30)
        set_current_spend(29)
        
        model = route_request("expensive task")
        assert model == "local"  # Forced local when near limit
```

## Faza 4: Core Features (Dzień 12-16)

### Blok 4.1: Task execution pipeline
```yaml
Zadania atomowe:
  - 4.1.1: Simple task queue w Redis
  - 4.1.2: Task status tracking
  - 4.1.3: Result storage w SQLite
  - 4.1.4: Error handling i retry
  - 4.1.5: Task dependencies resolver

Metryki sukcesu:
  - 100 tasks/min throughput
  - <1% task loss przy crash
  - Dependency resolution w <100ms

Testy integracyjne:
  - test_task_pipeline_integration.py:
    def test_end_to_end_task():
        # Create crew with 2 agents
        crew = create_test_crew()
        
        # Submit task
        task_id = crew.kickoff("Research and summarize Python")
        
        # Wait for completion
        result = wait_for_task(task_id, timeout=30)
        
        assert result.status == "completed"
        assert len(result.output) > 100
        assert result.cost < 0.10
```

### Blok 4.2: Memory system
```yaml
Zadania atomowe:
  - 4.2.1: Short-term memory w Redis
  - 4.2.2: Long-term memory w SQLite
  - 4.2.3: Context window management
  - 4.2.4: Memory search/retrieval
  - 4.2.5: Auto-summarization stale memory

Metryki sukcesu:
  - Memory search <200ms
  - Context fit w 4k tokens zawsze
  - Auto-cleanup działa co 24h

Testy:
  - test_memory_system.py:
    def test_memory_limits():
        agent = LiteAgent("test")
        for i in range(1000):
            agent.remember(f"fact_{i}")
        
        assert agent.memory_size() < 1024 * 1024  # <1MB
        assert agent.retrieve("fact_500") is not None
```

## Faza 5: Web UI i API (Dzień 17-19)

### Blok 5.1: FastAPI backend
```yaml
Zadania atomowe:
  - 5.1.1: FastAPI app structure
  - 5.1.2: REST endpoints dla CRUD
  - 5.1.3: WebSocket dla live updates
  - 5.1.4: Auth via simple API key
  - 5.1.5: Rate limiting

Metryki sukcesu:
  - API response <100ms dla GET
  - WebSocket stable przez 24h
  - 1000 req/s capacity

Testy API:
  - test_api_endpoints.py:
    def test_api_performance():
        async with httpx.AsyncClient() as client:
            start = time.time()
            tasks = []
            for i in range(100):
                task = client.get(f"{API_URL}/agents")
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            elapsed = time.time() - start
            
            assert elapsed < 1.0  # 100 req/s
            assert all(r.status_code == 200 for r in responses)
```

### Blok 5.2: Simple web UI
```yaml
Zadania atomowe:
  - 5.2.1: Static HTML/JS dashboard
  - 5.2.2: Agent creation form
  - 5.2.3: Task monitoring view
  - 5.2.4: Cost dashboard
  - 5.2.5: Nginx serving config

Metryki sukcesu:
  - Page load <1s
  - Works on mobile
  - No external CDN deps

Testy E2E (Playwright):
  - test_ui_e2e.py:
    def test_create_agent_flow():
        page = browser.new_page()
        page.goto(f"http://{DROPLET_IP}")
        
        # Create agent
        page.click("#new-agent")
        page.fill("#agent-name", "Test Agent")
        page.fill("#agent-goal", "Test tasks")
        page.click("#create-btn")
        
        # Verify created
        assert page.wait_for_selector(".agent-card:has-text('Test Agent')")
```

## Faza 6: Deployment automation (Dzień 20-21)

### Blok 6.1: CI/CD pipeline
```yaml
Zadania atomowe:
  - 6.1.1: GitHub Actions workflow
  - 6.1.2: Automated tests on PR
  - 6.1.3: Deploy script via SSH
  - 6.1.4: Zero-downtime deployment
  - 6.1.5: Rollback mechanism

Metryki sukcesu:
  - Deploy time <2 min
  - Zero downtime (test podczas deploy)
  - Rollback w <30s

GitHub Actions workflow:
  name: Deploy to DO
  on:
    push:
      branches: [main]
  
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - run: |
            python -m pytest tests/
            python -m pytest tests/integration/ --droplet-ip=${{ secrets.DROPLET_IP }}
    
    deploy:
      needs: test
      steps:
        - name: Deploy via SSH
          run: |
            ssh root@${{ secrets.DROPLET_IP }} "
              cd /opt/litecrewai
              git pull
              systemctl reload litecrewai
            "
```

## Faza 7: Monitoring i maintenance (Dzień 22-23)

### Blok 7.1: Monitoring stack
```yaml
Zadania atomowe:
  - 7.1.1: Prometheus node exporter
  - 7.1.2: Custom metrics (tasks, costs)
  - 7.1.3: Grafana dashboard
  - 7.1.4: Uptime monitoring
  - 7.1.5: Alert rules

Metryki sukcesu:
  - Dashboard load <2s
  - Metrics retention 30 dni
  - Alert latency <1 min

Smoke tests:
  - monitoring_smoke_test.sh:
    #!/bin/bash
    # Check Prometheus
    curl -s localhost:9090/-/healthy | grep -q "Prometheus is Healthy"
    
    # Check metrics
    curl -s localhost:9090/api/v1/query?query=up | grep -q '"status":"success"'
    
    # Check Grafana
    curl -s localhost:3000/api/health | grep -q "ok"
```

## 🎯 Continuous Validation Strategy

### Po każdym bloku:
1. **Unit tests** lokalnie (pytest)
2. **Deploy** na droplet (git push + auto-deploy)
3. **Integration tests** na żywym systemie
4. **Smoke tests** że poprzednie features działają
5. **Performance baseline** że nie ma regresji

### Daily validation:
```bash
#!/bin/bash
# daily_health_check.sh

echo "=== LiteCrewAI Daily Health Check ==="

# 1. System resources
echo "1. System Check:"
ssh $DROPLET_IP "free -h; df -h; uptime"

# 2. Services status
echo "2. Services Check:"
ssh $DROPLET_IP "systemctl status litecrewai redis nginx"

# 3. API health
echo "3. API Check:"
curl -s http://$DROPLET_IP/health | jq .

# 4. Run test crew
echo "4. Test Crew:"
curl -X POST http://$DROPLET_IP/api/crew/test \
  -d '{"task": "Say hello and compute 2+2"}' | jq .

# 5. Check costs
echo "5. Daily costs:"
curl -s http://$DROPLET_IP/api/costs/today | jq .
```

## 📊 Metryki sukcesu całego projektu:

1. **Funkcjonalność**: 80% features CrewAI działa
2. **Performance**: <2s response time dla 90% zadań  
3. **Koszt**: <$30/miesiąc łącznie
4. **Stabilność**: 99% uptime przez 30 dni
5. **Maintenance**: <2h/tydzień

## 🚀 Quick Start Commands

### Initial setup
```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/litecrewai.git
cd litecrewai
./scripts/setup_droplet.sh

# First deploy
./scripts/deploy.sh
```

### Development workflow
```bash
# Local testing
python -m pytest tests/

# Deploy changes
git push origin main  # Auto-deploy via GitHub Actions

# Check status
./scripts/health_check.sh
```

### Maintenance
```bash
# Daily backup
./scripts/backup.sh

# Check costs
curl http://your-droplet-ip/api/costs/month

# Update dependencies
./scripts/update_deps.sh
```

---

# 📁 STARTER SCRIPTS

## Script 1/5: setup_droplet.sh
```bash
#!/bin/bash
# setup_droplet.sh - Complete DigitalOcean droplet setup for LiteCrewAI
# Usage: ./setup_droplet.sh <DROPLET_IP>

set -euo pipefail

DROPLET_IP=${1:-}
if [ -z "$DROPLET_IP" ]; then
    echo "Usage: $0 <DROPLET_IP>"
    exit 1
fi

echo "🚀 Setting up LiteCrewAI on $DROPLET_IP"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Create setup script to run on droplet
cat > /tmp/remote_setup.sh << 'EOF'
#!/bin/bash
set -euo pipefail

echo "📦 Updating system packages..."
apt update && apt upgrade -y

echo "👤 Creating litecrewai user..."
useradd -m -s /bin/bash litecrewai || true
usermod -aG sudo litecrewai

echo "🔥 Setting up firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw reload

echo "🐍 Installing Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

echo "📚 Installing system dependencies..."
apt install -y \
    git curl wget htop tmux \
    redis-server nginx sqlite3 \
    build-essential libssl-dev libffi-dev \
    python3-dev cargo pkg-config \
    supervisor jq

echo "💾 Setting up swap (2GB)..."
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo "🦙 Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh
systemctl enable ollama
systemctl start ollama

# Pull lightweight models
ollama pull mistral
ollama pull phi

echo "📂 Creating directory structure..."
mkdir -p /opt/litecrewai/{app,data,logs,backups,scripts}
chown -R litecrewai:litecrewai /opt/litecrewai

echo "🔧 Configuring Redis..."
cat > /etc/redis/redis.conf << 'REDIS_EOF'
bind 127.0.0.1
port 6379
maxmemory 100mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
dir /opt/litecrewai/data
logfile /opt/litecrewai/logs/redis.log
REDIS_EOF

systemctl restart redis-server
systemctl enable redis-server

echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/litecrewai << 'NGINX_EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
NGINX_EOF

ln -sf /etc/nginx/sites-available/litecrewai /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

echo "🎭 Creating systemd service..."
cat > /etc/systemd/system/litecrewai.service << 'SERVICE_EOF'
[Unit]
Description=LiteCrewAI Service
After=network.target redis-server.service

[Service]
Type=exec
User=litecrewai
Group=litecrewai
WorkingDirectory=/opt/litecrewai/app
Environment="PATH=/opt/litecrewai/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONPATH=/opt/litecrewai/app"
ExecStart=/opt/litecrewai/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_EOF

systemctl daemon-reload
systemctl enable litecrewai

echo "📊 Installing monitoring tools..."
# Node exporter for Prometheus
wget -q https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz
tar xvfz node_exporter-*.tar.gz
cp node_exporter-*/node_exporter /usr/local/bin/
rm -rf node_exporter-*

cat > /etc/systemd/system/node_exporter.service << 'NODE_EOF'
[Unit]
Description=Node Exporter
After=network.target

[Service]
Type=simple
User=nobody
Group=nogroup
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
NODE_EOF

systemctl daemon-reload
systemctl enable node_exporter
systemctl start node_exporter

echo "✅ Base setup complete!"
EOF

# Copy and execute setup script
echo -e "${GREEN}📤 Copying setup script to droplet...${NC}"
scp /tmp/remote_setup.sh root@$DROPLET_IP:/tmp/
ssh root@$DROPLET_IP "chmod +x /tmp/remote_setup.sh && /tmp/remote_setup.sh"

# Create local management script
cat > manage_litecrewai.sh << EOF
#!/bin/bash
# Local management script for LiteCrewAI

DROPLET_IP=$DROPLET_IP

case "\$1" in
    ssh)
        ssh litecrewai@\$DROPLET_IP
        ;;
    logs)
        ssh litecrewai@\$DROPLET_IP "journalctl -u litecrewai -f"
        ;;
    restart)
        ssh root@\$DROPLET_IP "systemctl restart litecrewai"
        ;;
    status)
        ssh root@\$DROPLET_IP "systemctl status litecrewai redis-server nginx ollama"
        ;;
    backup)
        ssh litecrewai@\$DROPLET_IP "/opt/litecrewai/scripts/backup.sh"
        ;;
    *)
        echo "Usage: \$0 {ssh|logs|restart|status|backup}"
        exit 1
        ;;
esac
EOF

chmod +x manage_litecrewai.sh

echo -e "${GREEN}✅ Setup complete!${NC}"
echo -e "${GREEN}📋 Next steps:${NC}"
echo "1. Run: ./manage_litecrewai.sh ssh"
echo "2. Clone your LiteCrewAI fork in /opt/litecrewai/app"
echo "3. Set up Python environment and install dependencies"
echo "4. Start the service: sudo systemctl start litecrewai"
echo ""
echo "Management script created: ./manage_litecrewai.sh"
```

## Script 2/5: fork_and_clean.py
```python
#!/usr/bin/env python3
# fork_and_clean.py - Automatically clean CrewAI fork
# Usage: python fork_and_clean.py <github_token> <your_username>

import os
import sys
import shutil
import subprocess
import re
from pathlib import Path
import requests
import json

def run_command(cmd, cwd=None):
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error running: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def remove_telemetry(repo_path):
    """Remove all telemetry and analytics code"""
    print("🔍 Removing telemetry...")
    
    # Remove telemetry directory
    telemetry_path = Path(repo_path) / "src/crewai/telemetry"
    if telemetry_path.exists():
        shutil.rmtree(telemetry_path)
        print("  ✅ Removed telemetry directory")
    
    # Remove telemetry imports and calls
    for py_file in Path(repo_path).rglob("*.py"):
        try:
            content = py_file.read_text()
            original = content
            
            # Remove telemetry imports
            content = re.sub(r'from .*telemetry.* import .*\n', '', content)
            content = re.sub(r'import .*telemetry.*\n', '', content)
            
            # Remove telemetry function calls
            content = re.sub(r'.*telemetry\..*\(.*\).*\n', '', content)
            content = re.sub(r'.*Telemetry\(\).*\n', '', content)
            
            # Remove analytics
            content = re.sub(r'.*analytics.*\(.*\).*\n', '', content)
            content = re.sub(r'.*track.*event.*\(.*\).*\n', '', content)
            
            if content != original:
                py_file.write_text(content)
                print(f"  ✅ Cleaned {py_file.relative_to(repo_path)}")
                
        except Exception as e:
            print(f"  ⚠️  Error processing {py_file}: {e}")

def remove_enterprise_features(repo_path):
    """Remove enterprise and cloud features"""
    print("🔍 Removing enterprise features...")
    
    dirs_to_remove = ["enterprise", "cloud", "plus", "saas"]
    for dir_name in dirs_to_remove:
        for path in Path(repo_path).rglob(dir_name):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  ✅ Removed {path.relative_to(repo_path)}")

def simplify_dependencies(repo_path):
    """Reduce dependencies to minimum"""
    print("🔍 Simplifying dependencies...")
    
    pyproject_path = Path(repo_path) / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        
        # Create minimal dependencies
        new_deps = '''
[tool.poetry.dependencies]
python = "^3.11,<3.14"
pydantic = "^2.0"
python-dotenv = "^1.0"
click = "^8.1"
rich = "^13.0"
openai = "^1.0"
tiktoken = "^0.7"
chromadb = "^0.5"
embedchain = "^0.1"
pypdf = "^4.0"
docx2txt = "^0.8"
pandas = "^2.0"
'''
        
        # Replace dependencies section
        content = re.sub(
            r'\[tool\.poetry\.dependencies\].*?(?=\[|$)', 
            new_deps, 
            content, 
            flags=re.DOTALL
        )
        
        pyproject_path.write_text(content)
        print("  ✅ Updated pyproject.toml")

def create_lite_configs(repo_path):
    """Create optimized configs for personal use"""
    print("🔍 Creating lite configs...")
    
    config_dir = Path(repo_path) / "configs"
    config_dir.mkdir(exist_ok=True)
    
    # Create .env.example
    env_example = config_dir / ".env.example"
    env_example.write_text('''# LiteCrewAI Configuration

# LLM Settings
OPENAI_API_KEY=your-key-here
GROQ_API_KEY=your-key-here
DEFAULT_LLM=ollama/mistral

# Budget Control
MONTHLY_BUDGET_USD=30
ALERT_AT_PERCENT=80

# Storage
LITECREWAI_DB_PATH=/opt/litecrewai/data/litecrewai.db
REDIS_URL=redis://localhost:6379/0

# Feature Flags
ENABLE_TELEMETRY=false
ENABLE_COST_TRACKING=true
ENABLE_LOCAL_FALLBACK=true

# API Settings
API_KEY=generate-a-secure-key-here
RATE_LIMIT_PER_MINUTE=60
''')
    print("  ✅ Created .env.example")

def main():
    if len(sys.argv) != 3:
        print("Usage: python fork_and_clean.py <github_token> <your_username>")
        sys.exit(1)
    
    token = sys.argv[1]
    username = sys.argv[2]
    
    print("🚀 Starting CrewAI fork and cleanup process...")
    
    # Fork via GitHub API
    print("🍴 Forking CrewAI...")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.post(
        "https://api.github.com/repos/crewAIInc/crewAI/forks",
        headers=headers
    )
    
    if response.status_code == 202:
        print("  ✅ Fork created successfully")
    elif response.status_code == 200:
        print("  ℹ️  Fork already exists")
    else:
        print(f"  ❌ Error forking: {response.status_code} - {response.text}")
        sys.exit(1)
    
    # Clone the fork
    print("📥 Cloning fork...")
    repo_url = f"https://github.com/{username}/crewAI.git"
    run_command(f"git clone {repo_url} litecrewai")
    
    repo_path = "litecrewai"
    
    # Create new branch
    print("🌿 Creating lite-personal branch...")
    run_command("git checkout -b lite-personal", cwd=repo_path)
    
    # Clean the repo
    remove_telemetry(repo_path)
    remove_enterprise_features(repo_path)
    simplify_dependencies(repo_path)
    create_lite_configs(repo_path)
    
    # Create .gitignore for lite version
    gitignore_path = Path(repo_path) / ".gitignore"
    with open(gitignore_path, "a") as f:
        f.write("\n# LiteCrewAI\n")
        f.write(".env\n")
        f.write("*.db\n")
        f.write("*.db-journal\n")
        f.write("/data/\n")
        f.write("/backups/\n")
    
    # Commit changes
    print("💾 Committing changes...")
    run_command("git add -A", cwd=repo_path)
    run_command('git commit -m "feat: Transform to LiteCrewAI - remove telemetry, enterprise features"', cwd=repo_path)
    
    print("\n✅ Fork and cleanup complete!")
    print(f"📁 Your cleaned fork is in: {Path(repo_path).absolute()}")
    print("\n📋 Next steps:")
    print("1. cd litecrewai")
    print("2. Review changes with: git diff main HEAD")
    print("3. Push to GitHub: git push -u origin lite-personal")
    print("4. Deploy to your droplet!")

if __name__ == "__main__":
    main()
```

## Script 3/5: install_dependencies.sh
```bash
#!/bin/bash
# install_dependencies.sh - Install all Python dependencies for LiteCrewAI
# Run this after cloning your fork on the droplet

set -euo pipefail

echo "📦 Installing LiteCrewAI dependencies..."

# Ensure we're in the right directory
cd /opt/litecrewai/app

# Create virtual environment if it doesn't exist
if [ ! -d "/opt/litecrewai/venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3.11 -m venv /opt/litecrewai/venv
fi

# Activate virtual environment
source /opt/litecrewai/venv/bin/activate

# Upgrade pip and install build tools
echo "🔧 Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel

# Install core dependencies
echo "📚 Installing core dependencies..."
pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn[standard]==0.27.0 \
    pydantic==2.6.0 \
    pydantic-settings==2.2.0 \
    python-dotenv==1.0.1 \
    click==8.1.7 \
    rich==13.7.0 \
    httpx==0.26.0 \
    python-multipart==0.0.9

# Install LLM dependencies
echo "🤖 Installing LLM dependencies..."
pip install --no-cache-dir \
    openai==1.12.0 \
    tiktoken==0.6.0 \
    langchain-community==0.0.24 \
    chromadb==0.4.22 \
    sentence-transformers==2.5.0

# Install data processing
echo "📊 Installing data processing dependencies..."
pip install --no-cache-dir \
    pandas==2.2.0 \
    numpy==1.26.4 \
    pypdf==4.0.1 \
    python-docx==1.1.0 \
    beautifulsoup4==4.12.3 \
    markdownify==0.11.6

# Install storage and caching
echo "💾 Installing storage dependencies..."
pip install --no-cache-dir \
    redis==5.0.1 \
    aiosqlite==0.19.0 \
    sqlalchemy==2.0.27 \
    alembic==1.13.1

# Install monitoring and testing
echo "📊 Installing monitoring dependencies..."
pip install --no-cache-dir \
    prometheus-client==0.20.0 \
    pytest==8.0.0 \
    pytest-asyncio==0.23.4 \
    pytest-cov==4.1.0 \
    black==24.2.0 \
    ruff==0.2.1

# Install the LiteCrewAI package in development mode
echo "🚀 Installing LiteCrewAI..."
if [ -f "setup.py" ]; then
    pip install -e .
elif [ -f "pyproject.toml" ]; then
    pip install -e .
else
    echo "⚠️  No setup.py or pyproject.toml found, skipping package installation"
fi

# Create requirements.txt for reproducibility
echo "📝 Generating requirements.txt..."
pip freeze > requirements.txt

# Install pre-commit hooks if .pre-commit-config.yaml exists
if [ -f ".pre-commit-config.yaml" ]; then
    echo "🪝 Installing pre-commit hooks..."
    pip install pre-commit
    pre-commit install
fi

# Verify critical imports
echo "✅ Verifying installations..."
python -c "
import fastapi
import pydantic
import openai
import redis
import chromadb
print('✅ All critical imports successful!')
"

echo "🎉 Dependencies installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy your .env file to /opt/litecrewai/app/.env"
echo "2. Run migrations if needed: alembic upgrade head"
echo "3. Start the service: sudo systemctl start litecrewai"
```

## Script 4/5: create_systemd_services.sh
```bash
#!/bin/bash
# create_systemd_services.sh - Create all systemd service files
# This creates services for the main app, backup cron, and monitoring

set -euo pipefail

echo "🎭 Creating systemd services for LiteCrewAI..."

# Main LiteCrewAI service
cat > /etc/systemd/system/litecrewai.service << 'EOF'
[Unit]
Description=LiteCrewAI API Service
After=network.target redis-server.service
Requires=redis-server.service

[Service]
Type=exec
User=litecrewai
Group=litecrewai
WorkingDirectory=/opt/litecrewai/app
Environment="PATH=/opt/litecrewai/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONPATH=/opt/litecrewai/app"
Environment="PYTHONUNBUFFERED=1"

# Main process
ExecStart=/opt/litecrewai/venv/bin/python -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --loop uvloop \
    --access-log \
    --log-config /opt/litecrewai/app/logging.yaml

# Restart policy
Restart=always
RestartSec=10
StandardOutput=append:/opt/litecrewai/logs/litecrewai.log
StandardError=append:/opt/litecrewai/logs/litecrewai-error.log

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Background task processor
cat > /etc/systemd/system/litecrewai-worker.service << 'EOF'
[Unit]
Description=LiteCrewAI Background Worker
After=network.target redis-server.service litecrewai.service
Requires=redis-server.service

[Service]
Type=exec
User=litecrewai
Group=litecrewai
WorkingDirectory=/opt/litecrewai/app
Environment="PATH=/opt/litecrewai/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONPATH=/opt/litecrewai/app"

ExecStart=/opt/litecrewai/venv/bin/python -m workers.task_processor

Restart=always
RestartSec=30
StandardOutput=append:/opt/litecrewai/logs/worker.log
StandardError=append:/opt/litecrewai/logs/worker-error.log

[Install]
WantedBy=multi-user.target
EOF

# Daily backup service
cat > /etc/systemd/system/litecrewai-backup.service << 'EOF'
[Unit]
Description=LiteCrewAI Daily Backup
After=network.target

[Service]
Type=oneshot
User=litecrewai
Group=litecrewai
WorkingDirectory=/opt/litecrewai
ExecStart=/opt/litecrewai/scripts/backup.sh
StandardOutput=append:/opt/litecrewai/logs/backup.log
StandardError=append:/opt/litecrewai/logs/backup-error.log
EOF

# Daily backup timer
cat > /etc/systemd/system/litecrewai-backup.timer << 'EOF'
[Unit]
Description=Run LiteCrewAI backup daily at 3 AM
Requires=litecrewai-backup.service

[Timer]
OnCalendar=daily
Persistent=true
RandomizedDelaySec=1h

[Install]
WantedBy=timers.target
EOF

# Cost monitor service
cat > /etc/systemd/system/litecrewai-cost-monitor.service << 'EOF'
[Unit]
Description=LiteCrewAI Cost Monitor
After=network.target litecrewai.service

[Service]
Type=simple
User=litecrewai
Group=litecrewai
WorkingDirectory=/opt/litecrewai/app
Environment="PATH=/opt/litecrewai/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONPATH=/opt/litecrewai/app"

ExecStart=/opt/litecrewai/venv/bin/python -m monitors.cost_tracker

Restart=always
RestartSec=300

[Install]
WantedBy=multi-user.target
EOF

# Log rotation config
cat > /etc/logrotate.d/litecrewai << 'EOF'
/opt/litecrewai/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 litecrewai litecrewai
    sharedscripts
    postrotate
        systemctl reload litecrewai >/dev/null 2>&1 || true
    endscript
}
EOF

# Create startup check script
cat > /opt/litecrewai/scripts/health_check.sh << 'EOF'
#!/bin/bash
# Simple health check for monitoring

# Check if API is responding
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "✅ API is healthy"
    exit 0
else
    echo "❌ API is not responding"
    exit 1
fi
EOF

chmod +x /opt/litecrewai/scripts/health_check.sh

# Create service management helper
cat > /usr/local/bin/litecrewai-ctl << 'EOF'
#!/bin/bash
# LiteCrewAI service control helper

case "$1" in
    start)
        systemctl start litecrewai litecrewai-worker litecrewai-cost-monitor
        ;;
    stop)
        systemctl stop litecrewai litecrewai-worker litecrewai-cost-monitor
        ;;
    restart)
        systemctl restart litecrewai litecrewai-worker litecrewai-cost-monitor
        ;;
    status)
        systemctl status litecrewai litecrewai-worker litecrewai-cost-monitor
        ;;
    logs)
        journalctl -u litecrewai -u litecrewai-worker -f
        ;;
    backup)
        systemctl start litecrewai-backup
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|backup}"
        exit 1
        ;;
esac
EOF

chmod +x /usr/local/bin/litecrewai-ctl

# Reload systemd and enable services
systemctl daemon-reload
systemctl enable litecrewai.service
systemctl enable litecrewai-worker.service
systemctl enable litecrewai-cost-monitor.service
systemctl enable litecrewai-backup.timer

echo "✅ Systemd services created!"
echo ""
echo "📋 Available services:"
echo "  - litecrewai.service         (main API)"
echo "  - litecrewai-worker.service  (background tasks)"
echo "  - litecrewai-cost-monitor    (cost tracking)"
echo "  - litecrewai-backup.timer    (daily backups)"
echo ""
echo "🎮 Control all services with: litecrewai-ctl {start|stop|restart|status|logs}"
```

## Script 5/5: backup.sh
```bash
#!/bin/bash
# backup.sh - Backup script for LiteCrewAI data
# Backs up SQLite DB, Redis dump, and configuration

set -euo pipefail

# Configuration
BACKUP_DIR="/opt/litecrewai/backups"
DATA_DIR="/opt/litecrewai/data"
APP_DIR="/opt/litecrewai/app"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="litecrewai_backup_${TIMESTAMP}"

# Optional: DigitalOcean Spaces for offsite backup
DO_SPACES_BUCKET=${DO_SPACES_BUCKET:-""}
DO_SPACES_KEY=${DO_SPACES_KEY:-""}
DO_SPACES_SECRET=${DO_SPACES_SECRET:-""}

echo "🔄 Starting LiteCrewAI backup..."

# Create backup directory
CURRENT_BACKUP="${BACKUP_DIR}/${BACKUP_NAME}"
mkdir -p "${CURRENT_BACKUP}"

# Backup SQLite database
if [ -f "${DATA_DIR}/litecrewai.db" ]; then
    echo "📊 Backing up SQLite database..."
    sqlite3 "${DATA_DIR}/litecrewai.db" ".backup '${CURRENT_BACKUP}/litecrewai.db'"
    
    # Also create a SQL dump for safety
    sqlite3 "${DATA_DIR}/litecrewai.db" .dump > "${CURRENT_BACKUP}/litecrewai.sql"
fi

# Backup Redis
echo "💾 Backing up Redis..."
redis-cli BGSAVE
sleep 2  # Wait for background save to start

# Wait for Redis backup to complete
while [ $(redis-cli LASTSAVE) -eq $(redis-cli LASTSAVE) ]; do
    sleep 1
done

# Copy Redis dump
if [ -f "${DATA_DIR}/dump.rdb" ]; then
    cp "${DATA_DIR}/dump.rdb" "${CURRENT_BACKUP}/"
fi

# Backup configuration files
echo "⚙️ Backing up configuration..."
mkdir -p "${CURRENT_BACKUP}/config"

# Copy important config files
for file in .env logging.yaml config.yaml; do
    if [ -f "${APP_DIR}/${file}" ]; then
        cp "${APP_DIR}/${file}" "${CURRENT_BACKUP}/config/"
    fi
done

# Backup custom agents and crews definitions
if [ -d "${APP_DIR}/crews" ]; then
    cp -r "${APP_DIR}/crews" "${CURRENT_BACKUP}/"
fi

# Create backup manifest
cat > "${CURRENT_BACKUP}/manifest.json" << EOF
{
    "timestamp": "${TIMESTAMP}",
    "version": "$(cd ${APP_DIR} && git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "files": [
        "litecrewai.db",
        "litecrewai.sql",
        "dump.rdb",
        "config/",
        "crews/"
    ],
    "size": "$(du -sh ${CURRENT_BACKUP} | cut -f1)"
}
EOF

# Compress backup
echo "🗜️ Compressing backup..."
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
rm -rf "${BACKUP_NAME}"

# Upload to DigitalOcean Spaces if configured
if [ -n "${DO_SPACES_BUCKET}" ] && [ -n "${DO_SPACES_KEY}" ] && [ -n "${DO_SPACES_SECRET}" ]; then
    echo "☁️ Uploading to DigitalOcean Spaces..."
    
    # Install s3cmd if not present
    if ! command -v s3cmd &> /dev/null; then
        apt-get update && apt-get install -y s3cmd
    fi
    
    # Configure s3cmd
    cat > ~/.s3cfg << EOF
[default]
access_key = ${DO_SPACES_KEY}
secret_key = ${DO_SPACES_SECRET}
host_base = nyc3.digitaloceanspaces.com
host_bucket = %(bucket)s.nyc3.digitaloceanspaces.com
EOF
    
    # Upload backup
    s3cmd put "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" "s3://${DO_SPACES_BUCKET}/litecrewai-backups/"
    
    echo "✅ Backup uploaded to Spaces"
fi

# Clean up old backups
echo "🧹 Cleaning up old backups..."
find "${BACKUP_DIR}" -name "litecrewai_backup_*.tar.gz" -mtime +${RETENTION_DAYS} -delete

# Report backup status
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)
echo "✅ Backup complete!"
echo "📦 Backup saved: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "📏 Size: ${BACKUP_SIZE}"
echo "🗓️ Old backups cleaned (kept last ${RETENTION_DAYS} days)"

# Send notification (optional)
if [ -n "${WEBHOOK_URL:-}" ]; then
    curl -X POST "${WEBHOOK_URL}" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"LiteCrewAI backup completed: ${BACKUP_NAME}.tar.gz (${BACKUP_SIZE})\"}"
fi
```

---

# 🔧 IMPLEMENTACJA KLUCZOWYCH MODUŁÓW

## Module 1/8: lite_agent.py
```python
# lite_agent.py - Simplified synchronous agent for LiteCrewAI
# Optimized for single-user, low-resource usage

import time
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

import tiktoken
from pydantic import BaseModel, Field

from .llm_router import LLMRouter
from .memory_manager import MemoryManager
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Predefined agent roles with optimized prompts"""
    RESEARCHER = "researcher"
    WRITER = "writer"
    ANALYST = "analyst"
    CODER = "coder"
    ASSISTANT = "assistant"
    CUSTOM = "custom"


@dataclass
class AgentConfig:
    """Lightweight agent configuration"""
    role: AgentRole
    goal: str
    backstory: str = ""
    tools: List[str] = field(default_factory=list)
    max_iterations: int = 5
    temperature: float = 0.7
    allow_delegation: bool = False
    memory_enabled: bool = True
    cache_responses: bool = True
    
    @property
    def system_prompt(self) -> str:
        """Generate system prompt from config"""
        prompt = f"You are a {self.role.value}. Your goal is: {self.goal}"
        if self.backstory:
            prompt += f"\n\nBackground: {self.backstory}"
        if self.tools:
            prompt += f"\n\nAvailable tools: {', '.join(self.tools)}"
        return prompt


class LiteAgent:
    """Simplified agent optimized for personal use"""
    
    def __init__(
        self,
        name: str,
        config: AgentConfig,
        llm_router: Optional[LLMRouter] = None,
        memory_manager: Optional[MemoryManager] = None,
        cache_manager: Optional[CacheManager] = None
    ):
        self.name = name
        self.config = config
        self.llm_router = llm_router or LLMRouter()
        self.memory = memory_manager or MemoryManager(agent_name=name)
        self.cache = cache_manager or CacheManager()
        
        # Performance tracking
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.execution_count = 0
        
        # Token counting
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        logger.info(f"Initialized LiteAgent: {name} as {config.role.value}")
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a task synchronously"""
        start_time = time.time()
        self.execution_count += 1
        
        # Check cache first
        cache_key = self._generate_cache_key(task, context)
        if self.config.cache_responses:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for task: {task[:50]}...")
                return cached_result
        
        # Prepare conversation with memory context
        messages = self._prepare_messages(task, context)
        
        # Route to appropriate LLM based on complexity
        model = self.llm_router.select_model(task, messages)
        
        # Execute with retry logic
        result = None
        last_error = None
        
        for attempt in range(3):  # Simple retry logic
            try:
                response = self._call_llm(model, messages)
                result = self._process_response(response, task)
                break
            except Exception as e:
                last_error = e
                logger.warning(f"LLM call failed (attempt {attempt + 1}): {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        if result is None:
            # Fallback to local model
            logger.info("Falling back to local model due to errors")
            model = "ollama/mistral"
            try:
                response = self._call_llm(model, messages)
                result = self._process_response(response, task)
            except Exception as e:
                raise RuntimeError(f"All LLM calls failed: {last_error}") from e
        
        # Update memory if enabled
        if self.config.memory_enabled:
            self.memory.add_interaction(task, result['output'])
        
        # Cache result
        if self.config.cache_responses:
            self.cache.set(cache_key, result, ttl=3600)  # 1 hour cache
        
        # Track metrics
        execution_time = time.time() - start_time
        result['metrics'] = {
            'execution_time': execution_time,
            'model_used': model,
            'tokens_used': result.get('tokens', 0),
            'cost': result.get('cost', 0.0),
            'cache_hit': False
        }
        
        logger.info(
            f"Task completed in {execution_time:.2f}s using {model} "
            f"({result['metrics']['tokens_used']} tokens, ${result['metrics']['cost']:.4f})"
        )
        
        return result
    
    def _prepare_messages(self, task: str, context: Optional[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Prepare messages with system prompt and memory context"""
        messages = [
            {"role": "system", "content": self.config.system_prompt}
        ]
        
        # Add relevant memory context
        if self.config.memory_enabled:
            memory_context = self.memory.get_relevant_context(task, limit=3)
            if memory_context:
                context_str = "\n".join([f"- {m}" for m in memory_context])
                messages.append({
                    "role": "system",
                    "content": f"Relevant previous interactions:\n{context_str}"
                })
        
        # Add task context if provided
        if context:
            messages.append({
                "role": "system",
                "content": f"Task context: {json.dumps(context, indent=2)}"
            })
        
        # Add the actual task
        messages.append({"role": "user", "content": task})
        
        return messages
    
    def _call_llm(self, model: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Call LLM with token counting and cost tracking"""
        # Count input tokens
        input_text = " ".join([m["content"] for m in messages])
        input_tokens = len(self.tokenizer.encode(input_text))
        
        # Make the actual call (simplified for example)
        response = self.llm_router.call(model, messages, temperature=self.config.temperature)
        
        # Count output tokens
        output_tokens = len(self.tokenizer.encode(response['content']))
        total_tokens = input_tokens + output_tokens
        
        # Calculate cost
        cost = self.llm_router.calculate_cost(model, total_tokens)
        
        # Track usage
        self.total_tokens_used += total_tokens
        self.total_cost += cost
        
        return {
            'content': response['content'],
            'model': model,
            'tokens': total_tokens,
            'cost': cost
        }
    
    def _process_response(self, response: Dict[str, Any], task: str) -> Dict[str, Any]:
        """Process and structure the response"""
        return {
            'task': task,
            'output': response['content'],
            'model': response['model'],
            'tokens': response['tokens'],
            'cost': response['cost'],
            'timestamp': time.time()
        }
    
    def _generate_cache_key(self, task: str, context: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for task + context"""
        key_parts = [
            self.name,
            self.config.role.value,
            task[:100],  # Truncate long tasks
            json.dumps(context or {}, sort_keys=True)[:100]
        ]
        return ":".join(key_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics"""
        return {
            'name': self.name,
            'role': self.config.role.value,
            'executions': self.execution_count,
            'total_tokens': self.total_tokens_used,
            'total_cost': self.total_cost,
            'avg_tokens_per_execution': self.total_tokens_used / max(1, self.execution_count),
            'avg_cost_per_execution': self.total_cost / max(1, self.execution_count),
            'memory_size': self.memory.size() if self.config.memory_enabled else 0,
            'cache_stats': self.cache.get_stats() if self.config.cache_responses else {}
        }
    
    def reset_stats(self):
        """Reset performance statistics"""
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.execution_count = 0
        logger.info(f"Reset statistics for agent: {self.name}")
    
    def clear_memory(self):
        """Clear agent memory"""
        if self.config.memory_enabled:
            self.memory.clear()
            logger.info(f"Cleared memory for agent: {self.name}")
    
    def __repr__(self) -> str:
        return f"LiteAgent(name='{self.name}', role={self.config.role.value}, executions={self.execution_count})"


# Factory function for common agent types
def create_agent(name: str, role: AgentRole, goal: str, **kwargs) -> LiteAgent:
    """Factory function to create preconfigured agents"""
    
    # Role-specific defaults
    role_defaults = {
        AgentRole.RESEARCHER: {
            "tools": ["web_search", "arxiv_search", "wikipedia"],
            "temperature": 0.3,
            "backstory": "You are an expert researcher skilled at finding and synthesizing information."
        },
        AgentRole.WRITER: {
            "tools": ["text_editor", "grammar_check"],
            "temperature": 0.8,
            "backstory": "You are a creative writer who crafts engaging and clear content."
        },
        AgentRole.ANALYST: {
            "tools": ["calculator", "data_analyzer", "chart_creator"],
            "temperature": 0.2,
            "backstory": "You are a data analyst who excels at finding insights in numbers."
        },
        AgentRole.CODER: {
            "tools": ["code_executor", "debugger", "docs_search"],
            "temperature": 0.1,
            "backstory": "You are an experienced programmer who writes clean, efficient code."
        },
        AgentRole.ASSISTANT: {
            "tools": ["calendar", "reminder", "email"],
            "temperature": 0.5,
            "backstory": "You are a helpful assistant focused on productivity and organization."
        }
    }
    
    # Merge role defaults with provided kwargs
    defaults = role_defaults.get(role, {})
    config_params = {**defaults, **kwargs, "role": role, "goal": goal}
    
    config = AgentConfig(**config_params)
    return LiteAgent(name, config)


# Example usage
if __name__ == "__main__":
    # Create a simple research agent
    researcher = create_agent(
        name="researcher_1",
        role=AgentRole.RESEARCHER,
        goal="Find accurate information and provide comprehensive summaries"
    )
    
    # Execute a task
    result = researcher.execute("What are the latest developments in quantum computing?")
    print(f"Result: {result['output'][:200]}...")
    print(f"Cost: ${result['cost']:.4f}")
    print(f"Stats: {researcher.get_stats()}")
```

## Module 2/8: llm_router.py
```python
# llm_router.py - Intelligent LLM routing with cost optimization
# Routes requests to appropriate models based on complexity and budget

import os
import time
import re
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import logging

import openai
import httpx
from dotenv import load_dotenv

from .cost_tracker import CostTracker

load_dotenv()
logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Task complexity levels for routing"""
    SIMPLE = "simple"      # Basic Q&A, short responses
    MEDIUM = "medium"      # Moderate analysis, summaries
    COMPLEX = "complex"    # Deep analysis, creative work
    LOCAL_ONLY = "local"   # Force local model


@dataclass
class ModelConfig:
    """Configuration for each available model"""
    name: str
    provider: str
    cost_per_1k_tokens: float
    max_tokens: int
    latency_ms: int  # Average latency
    quality_score: float  # 0-1 quality rating
    is_local: bool
    
    @property
    def cost_per_token(self) -> float:
        return self.cost_per_1k_tokens / 1000


# Model configurations
MODELS = {
    # Local models (Ollama)
    "ollama/mistral": ModelConfig(
        name="mistral",
        provider="ollama",
        cost_per_1k_tokens=0.0,
        max_tokens=8192,
        latency_ms=500,
        quality_score=0.7,
        is_local=True
    ),
    "ollama/phi": ModelConfig(
        name="phi",
        provider="ollama",
        cost_per_1k_tokens=0.0,
        max_tokens=4096,
        latency_ms=300,
        quality_score=0.6,
        is_local=True
    ),
    
    # Groq (fast and cheap)
    "groq/mixtral-8x7b": ModelConfig(
        name="mixtral-8x7b-32768",
        provider="groq",
        cost_per_1k_tokens=0.27,
        max_tokens=32768,
        latency_ms=200,
        quality_score=0.85,
        is_local=False
    ),
    
    # OpenAI
    "openai/gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        provider="openai",
        cost_per_1k_tokens=0.15,
        max_tokens=16384,
        latency_ms=800,
        quality_score=0.9,
        is_local=False
    ),
    "openai/gpt-4o": ModelConfig(
        name="gpt-4o",
        provider="openai",
        cost_per_1k_tokens=5.0,
        max_tokens=128000,
        latency_ms=1200,
        quality_score=0.98,
        is_local=False
    ),
}


class LLMRouter:
    """Routes LLM requests to optimal model based on task and budget"""
    
    def __init__(self, cost_tracker: Optional[CostTracker] = None):
        self.cost_tracker = cost_tracker or CostTracker()
        self.monthly_budget = float(os.getenv("MONTHLY_BUDGET_USD", "30"))
        self.force_local_threshold = float(os.getenv("FORCE_LOCAL_THRESHOLD", "0.8"))
        
        # Initialize API clients
        self._init_clients()
        
        # Complexity analysis patterns
        self.complexity_patterns = {
            TaskComplexity.SIMPLE: [
                r"^(what|when|where|who|how much|how many)",
                r"^(define|explain briefly|what is)",
                r"(yes or no|true or false)",
                r"(calculate|compute|math)",
                r"^(translate|convert)",
            ],
            TaskComplexity.COMPLEX: [
                r"(analyze|analysis|evaluate)",
                r"(write|create|generate).*(essay|article|story|report)",
                r"(comprehensive|detailed|in-depth)",
                r"(compare and contrast)",
                r"(step.?by.?step|detailed plan)",
                r"(code|program|implement|debug)",
            ]
        }
        
        logger.info(f"LLM Router initialized with ${self.monthly_budget} monthly budget")
    
    def _init_clients(self):
        """Initialize API clients"""
        # OpenAI
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Groq
        self.groq_client = openai.OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Ollama (local)
        self.ollama_base = "http://localhost:11434"
    
    def analyze_complexity(self, task: str, messages: List[Dict[str, str]]) -> TaskComplexity:
        """Analyze task complexity based on content"""
        # Combine all message content
        full_text = " ".join([m["content"] for m in messages]).lower()
        
        # Check for simple patterns
        for pattern in self.complexity_patterns[TaskComplexity.SIMPLE]:
            if re.search(pattern, full_text):
                return TaskComplexity.SIMPLE
        
        # Check for complex patterns
        complex_matches = 0
        for pattern in self.complexity_patterns[TaskComplexity.COMPLEX]:
            if re.search(pattern, full_text):
                complex_matches += 1
        
        if complex_matches >= 2:
            return TaskComplexity.COMPLEX
        
        # Check length as a factor
        word_count = len(full_text.split())
        if word_count < 20:
            return TaskComplexity.SIMPLE
        elif word_count > 200:
            return TaskComplexity.COMPLEX
        
        return TaskComplexity.MEDIUM
    
    def select_model(self, task: str, messages: List[Dict[str, str]]) -> str:
        """Select optimal model based on task, budget, and complexity"""
        # Check if we're near budget limit
        budget_usage = self.cost_tracker.get_monthly_usage_percentage()
        if budget_usage >= self.force_local_threshold:
            logger.warning(f"Budget usage at {budget_usage:.1%}, forcing local model")
            return "ollama/mistral"
        
        # Analyze task complexity
        complexity = self.analyze_complexity(task, messages)
        logger.info(f"Task complexity: {complexity.value}")
        
        # Model selection logic
        if complexity == TaskComplexity.SIMPLE:
            # Prefer local for simple tasks
            return "ollama/mistral"
        
        elif complexity == TaskComplexity.MEDIUM:
            # Use Groq for good balance of cost/quality
            if budget_usage < 0.5:
                return "groq/mixtral-8x7b"
            else:
                return "ollama/mistral"
        
        elif complexity == TaskComplexity.COMPLEX:
            # Use best model if budget allows
            if budget_usage < 0.3:
                return "openai/gpt-4o-mini"
            elif budget_usage < 0.6:
                return "groq/mixtral-8x7b"
            else:
                return "ollama/mistral"
        
        return "ollama/mistral"  # Default fallback
    
    def call(
        self,
        model_key: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute LLM call with the specified model"""
        model_config = MODELS.get(model_key)
        if not model_config:
            raise ValueError(f"Unknown model: {model_key}")
        
        start_time = time.time()
        
        try:
            if model_config.provider == "ollama":
                response = self._call_ollama(model_config, messages, temperature)
            elif model_config.provider == "openai":
                response = self._call_openai(model_config, messages, temperature, max_tokens)
            elif model_config.provider == "groq":
                response = self._call_groq(model_config, messages, temperature, max_tokens)
            else:
                raise ValueError(f"Unknown provider: {model_config.provider}")
            
            # Track latency
            latency = (time.time() - start_time) * 1000
            logger.info(f"LLM call to {model_key} completed in {latency:.0f}ms")
            
            return response
            
        except Exception as e:
            logger.error(f"Error calling {model_key}: {e}")
            raise
    
    def _call_ollama(
        self,
        model: ModelConfig,
        messages: List[Dict[str, str]],
        temperature: float
    ) -> Dict[str, Any]:
        """Call Ollama local model"""
        # Convert messages to Ollama format
        prompt = "\n".join([
            f"{m['role']}: {m['content']}" for m in messages
        ])
        
        response = httpx.post(
            f"{self.ollama_base}/api/generate",
            json={
                "model": model.name,
                "prompt": prompt,
                "temperature": temperature,
                "stream": False
            },
            timeout=30.0
        )
        response.raise_for_status()
        
        result = response.json()
        return {
            "content": result["response"],
            "total_tokens": len(prompt.split()) + len(result["response"].split())  # Approximate
        }
    
    def _call_openai(
        self,
        model: ModelConfig,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """Call OpenAI API"""
        response = self.openai_client.chat.completions.create(
            model=model.name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens or 2000
        )
        
        return {
            "content": response.choices[0].message.content,
            "total_tokens": response.usage.total_tokens
        }
    
    def _call_groq(
        self,
        model: ModelConfig,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """Call Groq API"""
        response = self.groq_client.chat.completions.create(
            model=model.name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens or 2000
        )
        
        return {
            "content": response.choices[0].message.content,
            "total_tokens": response.usage.total_tokens
        }
    
    def calculate_cost(self, model_key: str, tokens: int) -> float:
        """Calculate cost for tokens used"""
        model = MODELS.get(model_key)
        if not model:
            return 0.0
        
        cost = tokens * model.cost_per_token
        
        # Track the cost
        self.cost_tracker.track_usage(model_key, tokens, cost)
        
        return cost
    
    def get_model_recommendations(self, budget_remaining: float) -> List[Tuple[str, str]]:
        """Get model recommendations based on remaining budget"""
        recommendations = []
        
        for model_key, config in MODELS.items():
            if config.is_local:
                recommendations.append((model_key, "Free - Local model"))
            else:
                # Calculate how many tokens we can afford
                affordable_tokens = int(budget_remaining / config.cost_per_token)
                if affordable_tokens > 1000:
                    recommendations.append(
                        (model_key, f"~{affordable_tokens:,} tokens (${budget_remaining:.2f})")
                    )
        
        return sorted(recommendations, key=lambda x: MODELS[x[0]].quality_score, reverse=True)
    
    def get_router_stats(self) -> Dict[str, Any]:
        """Get router statistics"""
        return {
            "monthly_budget": self.monthly_budget,
            "budget_used": self.cost_tracker.get_monthly_cost(),
            "budget_remaining": self.monthly_budget - self.cost_tracker.get_monthly_cost(),
            "usage_percentage": self.cost_tracker.get_monthly_usage_percentage(),
            "model_usage": self.cost_tracker.get_model_usage_stats(),
            "recommendations": self.get_model_recommendations(
                self.monthly_budget - self.cost_tracker.get_monthly_cost()
            )
        }


# Example usage
if __name__ == "__main__":
    router = LLMRouter()
    
    # Test complexity analysis
    simple_task = "What is 2+2?"
    complex_task = "Write a comprehensive analysis of quantum computing developments in 2024"
    
    simple_messages = [{"role": "user", "content": simple_task}]
    complex_messages = [{"role": "user", "content": complex_task}]
    
    print(f"Simple task model: {router.select_model(simple_task, simple_messages)}")
    print(f"Complex task model: {router.select_model(complex_task, complex_messages)}")
    
    print(f"\nRouter stats: {router.get_router_stats()}")
```

## Module 3/8: cache_manager.py
```python
# cache_manager.py - Aggressive caching system for LLM responses and tool results
# Saves money by caching everything possible

import json
import time
import hashlib
import logging
from typing import Any, Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import pickle

import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Structure for cache entries with metadata"""
    key: str
    value: Any
    created_at: float
    expires_at: float
    hit_count: int = 0
    size_bytes: int = 0
    tags: List[str] = None
    
    def is_expired(self) -> bool:
        return time.time() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CacheManager:
    """Aggressive caching with Redis backend and smart eviction"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        max_memory_mb: int = 100,
        default_ttl: int = 3600
    ):
        self.redis_url = redis_url
        self.max_memory_mb = max_memory_mb
        self.default_ttl = default_ttl
        
        # Cache key prefixes
        self.PREFIX_LLM = "llm:"
        self.PREFIX_TOOL = "tool:"
        self.PREFIX_SEARCH = "search:"
        self.PREFIX_STATS = "stats:"
        
        # Initialize Redis connection
        self._init_redis()
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "errors": 0
        }
        
        logger.info(f"Cache manager initialized with {max_memory_mb}MB limit")
    
    def _init_redis(self):
        """Initialize Redis connection with optimal settings"""
        try:
            self.redis = redis.from_url(
                self.redis_url,
                decode_responses=False,  # We'll handle encoding
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Configure Redis for LRU eviction
            self.redis.config_set("maxmemory", f"{self.max_memory_mb}mb")
            self.redis.config_set("maxmemory-policy", "allkeys-lru")
            
            # Test connection
            self.redis.ping()
            logger.info("Redis connection established")
            
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def _generate_key(self, prefix: str, *args) -> str:
        """Generate a unique cache key from arguments"""
        # Create a string representation of all arguments
        key_data = json.dumps(args, sort_keys=True, default=str)
        
        # Hash it for consistent length
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        
        return f"{prefix}{key_hash}"
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage"""
        try:
            # Try JSON first (more portable)
            return json.dumps(value).encode('utf-8')
        except (TypeError, ValueError):
            # Fall back to pickle for complex objects
            return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(data)
    
    def get(
        self,
        key: str,
        prefix: str = "",
        update_stats: bool = True
    ) -> Optional[Any]:
        """Get value from cache with automatic deserialization"""
        full_key = prefix + key if prefix else key
        
        try:
            # Get from Redis
            data = self.redis.get(full_key)
            
            if data is None:
                if update_stats:
                    self.stats["misses"] += 1
                return None
            
            # Deserialize
            value = self._deserialize(data)
            
            # Update hit count
            self.redis.hincrby(f"{self.PREFIX_STATS}{full_key}", "hits", 1)
            
            if update_stats:
                self.stats["hits"] += 1
            
            logger.debug(f"Cache hit: {full_key}")
            return value
            
        except Exception as e:
            logger.error(f"Cache get error for {full_key}: {e}")
            self.stats["errors"] += 1
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        prefix: str = "",
        tags: Optional[List[str]] = None
    ) -> bool:
        """Set value in cache with automatic serialization"""
        full_key = prefix + key if prefix else key
        ttl = ttl or self.default_ttl
        
        try:
            # Serialize value
            data = self._serialize(value)
            size_bytes = len(data)
            
            # Store in Redis with expiration
            self.redis.setex(full_key, ttl, data)
            
            # Store metadata
            metadata = {
                "created_at": time.time(),
                "expires_at": time.time() + ttl,
                "size_bytes": size_bytes,
                "hits": 0
            }
            
            if tags:
                metadata["tags"] = json.dumps(tags)
                # Add to tag indices
                for tag in tags:
                    self.redis.sadd(f"tag:{tag}", full_key)
            
            self.redis.hset(f"{self.PREFIX_STATS}{full_key}", mapping={
                k: str(v) for k, v in metadata.items()
            })
            
            logger.debug(f"Cache set: {full_key} ({size_bytes} bytes, TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for {full_key}: {e}")
            self.stats["errors"] += 1
            return False
    
    def cache_llm_response(
        self,
        prompt: str,
        response: str,
        model: str,
        temperature: float,
        ttl: Optional[int] = None
    ) -> bool:
        """Cache LLM response with smart key generation"""
        # Longer TTL for expensive models
        if "gpt-4" in model:
            ttl = ttl or 86400  # 24 hours
        else:
            ttl = ttl or 3600   # 1 hour
        
        key = self._generate_key(
            self.PREFIX_LLM,
            prompt[:1000],  # Truncate very long prompts
            model,
            f"temp_{temperature}"
        )
        
        return self.set(
            key,
            {
                "response": response,
                "model": model,
                "cached_at": datetime.now().isoformat()
            },
            ttl=ttl,
            tags=["llm", model]
        )
    
    def get_llm_response(
        self,
        prompt: str,
        model: str,
        temperature: float
    ) -> Optional[Dict[str, Any]]:
        """Get cached LLM response"""
        key = self._generate_key(
            self.PREFIX_LLM,
            prompt[:1000],
            model,
            f"temp_{temperature}"
        )
        
        return self.get(key)
    
    def cache_tool_result(
        self,
        tool_name: str,
        params: Dict[str, Any],
        result: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Cache tool execution result"""
        # Tool-specific TTLs
        tool_ttls = {
            "web_search": 86400 * 7,    # 7 days
            "wikipedia": 86400 * 30,     # 30 days
            "calculator": 86400 * 365,   # 1 year (math doesn't change!)
            "weather": 3600,             # 1 hour
        }
        
        ttl = ttl or tool_ttls.get(tool_name, 86400)  # Default 24 hours
        
        key = self._generate_key(self.PREFIX_TOOL, tool_name, params)
        
        return self.set(
            key,
            {
                "result": result,
                "tool": tool_name,
                "params": params,
                "cached_at": datetime.now().isoformat()
            },
            ttl=ttl,
            tags=["tool", tool_name]
        )
    
    def get_tool_result(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get cached tool result"""
        key = self._generate_key(self.PREFIX_TOOL, tool_name, params)
        return self.get(key)
    
    def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate all cache entries with given tags"""
        invalidated = 0
        
        for tag in tags:
            # Get all keys with this tag
            keys = self.redis.smembers(f"tag:{tag}")
            
            if keys:
                # Delete the keys
                invalidated += self.redis.delete(*keys)
                
                # Clean up tag index
                self.redis.delete(f"tag:{tag}")
        
        logger.info(f"Invalidated {invalidated} cache entries with tags: {tags}")
        return invalidated
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        # Get Redis info
        info = self.redis.info()
        memory_info = self.redis.info("memory")
        
        # Calculate hit rate
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "hit_rate": f"{hit_rate:.2%}",
            "total_hits": self.stats["hits"],
            "total_misses": self.stats["misses"],
            "total_errors": self.stats["errors"],
            "memory_used_mb": round(memory_info["used_memory"] / 1024 / 1024, 2),
            "memory_limit_mb": self.max_memory_mb,
            "memory_usage_percent": round(
                (memory_info["used_memory"] / 1024 / 1024) / self.max_memory_mb * 100, 1
            ),
            "total_keys": info["db0"]["keys"] if "db0" in info else 0,
            "evicted_keys": info.get("evicted_keys", 0),
            "expired_keys": info.get("expired_keys", 0)
        }
    
    def optimize_cache(self) -> Dict[str, int]:
        """Optimize cache by removing old entries and analyzing patterns"""
        results = {
            "expired_removed": 0,
            "low_hit_removed": 0,
            "total_freed_bytes": 0
        }
        
        # Scan all keys
        cursor = 0
        while True:
            cursor, keys = self.redis.scan(cursor, count=100)
            
            for key in keys:
                # Skip system keys
                if key.startswith(b"tag:") or key.startswith(self.PREFIX_STATS.encode()):
                    continue
                
                # Get metadata
                stats_key = f"{self.PREFIX_STATS}{key.decode()}"
                metadata = self.redis.hgetall(stats_key)
                
                if metadata:
                    hits = int(metadata.get(b"hits", 0))
                    created_at = float(metadata.get(b"created_at", 0))
                    size_bytes = int(metadata.get(b"size_bytes", 0))
                    
                    # Remove entries with low hit rate after 24 hours
                    age_hours = (time.time() - created_at) / 3600
                    if age_hours > 24 and hits < 2:
                        self.redis.delete(key, stats_key)
                        results["low_hit_removed"] += 1
                        results["total_freed_bytes"] += size_bytes
            
            if cursor == 0:
                break
        
        logger.info(f"Cache optimization complete: {results}")
        return results
    
    def clear(self, prefix: Optional[str] = None) -> int:
        """Clear cache, optionally by prefix"""
        if prefix:
            # Clear specific prefix
            pattern = f"{prefix}*"
            keys = []
            cursor = 0
            
            while True:
                cursor, batch = self.redis.scan(cursor, match=pattern, count=100)
                keys.extend(batch)
                if cursor == 0:
                    break
            
            if keys:
                return self.redis.delete(*keys)
            return 0
        else:
            # Clear everything
            return self.redis.flushdb()
    
    def warmup(self, common_prompts: List[str], model: str = "ollama/mistral"):
        """Warmup cache with common prompts"""
        logger.info(f"Warming up cache with {len(common_prompts)} common prompts")
        
        for prompt in common_prompts:
            # Check if already cached
            if not self.get_llm_response(prompt, model, 0.7):
                # In real implementation, this would call the LLM
                # For now, we'll just log it
                logger.debug(f"Would fetch and cache: {prompt[:50]}...")


# Example usage
if __name__ == "__main__":
    cache = CacheManager()
    
    # Test LLM caching
    cache.cache_llm_response(
        "What is Python?",
        "Python is a high-level programming language...",
        "ollama/mistral",
        0.7
    )
    
    # Test retrieval
    result = cache.get_llm_response("What is Python?", "ollama/mistral", 0.7)
    print(f"Cached result: {result}")
    
    # Test tool caching
    cache.cache_tool_result(
        "calculator",
        {"expression": "2+2"},
        {"result": 4}
    )
    
    # Get stats
    print(f"Cache stats: {cache.get_stats()}")
```

## Module 4/8: memory_manager.py
```python
# memory_manager.py - Multi-layer memory system for agents
# Manages short-term, long-term, and contextual memory

import json
import time
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Single memory entry with metadata"""
    id: Optional[int]
    agent_name: str
    content: str
    embedding: Optional[List[float]]
    memory_type: str  # short_term, long_term, entity
    importance: float  # 0-1 score
    created_at: float
    accessed_at: float
    access_count: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        # Convert embedding to JSON-serializable format
        if data['embedding']:
            data['embedding'] = json.dumps(data['embedding'])
        data['metadata'] = json.dumps(data['metadata'])
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        # Parse JSON fields
        if isinstance(data['embedding'], str):
            data['embedding'] = json.loads(data['embedding']) if data['embedding'] else None
        if isinstance(data['metadata'], str):
            data['metadata'] = json.loads(data['metadata']) if data['metadata'] else {}
        return cls(**data)


class MemoryManager:
    """Manages agent memory with SQLite backend and semantic search"""
    
    def __init__(
        self,
        agent_name: str,
        db_path: str = "/opt/litecrewai/data/memories.db",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.agent_name = agent_name
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
        
        # Initialize embedding model (lightweight)
        try:
            self.embedder = SentenceTransformer(embedding_model)
            self.embedding_dim = self.embedder.get_sentence_embedding_dimension()
            logger.info(f"Loaded embedding model: {embedding_model}")
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}. Semantic search disabled.")
            self.embedder = None
            self.embedding_dim = 0
        
        # Memory limits
        self.short_term_limit = 50
        self.long_term_limit = 1000
        self.importance_threshold = 0.7  # For promotion to long-term
        
        logger.info(f"Memory manager initialized for agent: {agent_name}")
    
    def _init_db(self):
        """Initialize SQLite database with optimized schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding TEXT,
                    memory_type TEXT NOT NULL,
                    importance REAL NOT NULL DEFAULT 0.5,
                    created_at REAL NOT NULL,
                    accessed_at REAL NOT NULL,
                    access_count INTEGER NOT NULL DEFAULT 0,
                    metadata TEXT,
                    
                    -- Indexes for performance
                    UNIQUE(agent_name, content, memory_type)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_type ON memories(agent_name, memory_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_accessed ON memories(accessed_at DESC)")
            
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            
            conn.commit()
    
    def add_interaction(
        self,
        user_input: str,
        agent_response: str,
        importance: Optional[float] = None
    ) -> int:
        """Add a user-agent interaction to memory"""
        # Combine interaction for context
        content = f"User: {user_input}\nAssistant: {agent_response}"
        
        # Calculate importance if not provided
        if importance is None:
            importance = self._calculate_importance(content)
        
        # Determine memory type based on importance
        memory_type = "long_term" if importance >= self.importance_threshold else "short_term"
        
        # Create embedding if available
        embedding = None
        if self.embedder:
            embedding = self.embedder.encode(content).tolist()
        
        # Create memory entry
        entry = MemoryEntry(
            id=None,
            agent_name=self.agent_name,
            content=content,
            embedding=embedding,
            memory_type=memory_type,
            importance=importance,
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=1,
            metadata={
                "user_input_length": len(user_input),
                "response_length": len(agent_response)
            }
        )
        
        return self._store_memory(entry)
    
    def remember(
        self,
        content: str,
        memory_type: str = "short_term",
        importance: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Store a general memory"""
        if importance is None:
            importance = self._calculate_importance(content)
        
        embedding = None
        if self.embedder:
            embedding = self.embedder.encode(content).tolist()
        
        entry = MemoryEntry(
            id=None,
            agent_name=self.agent_name,
            content=content,
            embedding=embedding,
            memory_type=memory_type,
            importance=importance,
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=1,
            metadata=metadata or {}
        )
        
        return self._store_memory(entry)
    
    def _store_memory(self, entry: MemoryEntry) -> int:
        """Store memory entry in database"""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            del data['id']  # Let SQLite auto-increment
            
            cursor = conn.execute("""
                INSERT OR REPLACE INTO memories 
                (agent_name, content, embedding, memory_type, importance, 
                 created_at, accessed_at, access_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['agent_name'], data['content'], data['embedding'],
                data['memory_type'], data['importance'], data['created_at'],
                data['accessed_at'], data['access_count'], data['metadata']
            ))
            
            memory_id = cursor.lastrowid
            
            # Enforce memory limits
            self._enforce_limits(conn)
            
            conn.commit()
            
        logger.debug(f"Stored memory {memory_id}: {entry.content[:50]}...")
        return memory_id
    
    def get_relevant_context(
        self,
        query: str,
        limit: int = 5,
        memory_types: Optional[List[str]] = None
    ) -> List[str]:
        """Get relevant memories for a query using semantic search"""
        if not memory_types:
            memory_types = ["short_term", "long_term"]
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if self.embedder:
                # Semantic search
                query_embedding = self.embedder.encode(query)
                memories = self._semantic_search(conn, query_embedding, limit, memory_types)
            else:
                # Fallback to recency-based retrieval
                memories = self._recent_search(conn, limit, memory_types)
            
            # Update access stats
            for memory in memories:
                conn.execute("""
                    UPDATE memories 
                    SET accessed_at = ?, access_count = access_count + 1
                    WHERE id = ?
                """, (time.time(), memory['id']))
            
            conn.commit()
            
        return [m['content'] for m in memories]
    
    def _semantic_search(
        self,
        conn: sqlite3.Connection,
        query_embedding: np.ndarray,
        limit: int,
        memory_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Perform semantic similarity search"""
        # Get all memories with embeddings
        placeholders = ','.join('?' * len(memory_types))
        cursor = conn.execute(f"""
            SELECT id, content, embedding, importance, access_count
            FROM memories
            WHERE agent_name = ? 
            AND memory_type IN ({placeholders})
            AND embedding IS NOT NULL
            ORDER BY importance DESC, accessed_at DESC
            LIMIT 100
        """, [self.agent_name] + memory_types)
        
        # Calculate similarities
        candidates = []
        for row in cursor:
            memory_embedding = np.array(json.loads(row['embedding']))
            
            # Cosine similarity
            similarity = np.dot(query_embedding, memory_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(memory_embedding)
            )
            
            # Boost by importance and access count
            score = similarity * (0.7 + 0.2 * row['importance'] + 0.1 * min(row['access_count'] / 10, 1))
            
            candidates.append({
                'id': row['id'],
                'content': row['content'],
                'score': score
            })
        
        # Sort by score and return top matches
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[:limit]
    
    def _recent_search(
        self,
        conn: sqlite3.Connection,
        limit: int,
        memory_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Fallback to recency-based search"""
        placeholders = ','.join('?' * len(memory_types))
        cursor = conn.execute(f"""
            SELECT id, content
            FROM memories
            WHERE agent_name = ?
            AND memory_type IN ({placeholders})
            ORDER BY accessed_at DESC
            LIMIT ?
        """, [self.agent_name] + memory_types + [limit])
        
        return [dict(row) for row in cursor]
    
    def retrieve(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memories matching a query"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Simple keyword search
            cursor = conn.execute("""
                SELECT * FROM memories
                WHERE agent_name = ?
                AND content LIKE ?
                ORDER BY importance DESC, accessed_at DESC
                LIMIT ?
            """, (self.agent_name, f"%{query}%", limit))
            
            memories = []
            for row in cursor:
                memories.append(MemoryEntry.from_dict(dict(row)))
            
            return memories
    
    def _calculate_importance(self, content: str) -> float:
        """Calculate importance score for content"""
        # Simple heuristics for importance
        score = 0.5  # Base score
        
        # Length factor (longer = more important, up to a point)
        word_count = len(content.split())
        if word_count > 50:
            score += 0.1
        if word_count > 100:
            score += 0.1
        
        # Keywords that indicate importance
        important_keywords = [
            "important", "remember", "critical", "key", "main",
            "summary", "conclusion", "decision", "action"
        ]
        
        content_lower = content.lower()
        for keyword in important_keywords:
            if keyword in content_lower:
                score += 0.05
        
        # Questions are often important
        if "?" in content:
            score += 0.1
        
        return min(score, 1.0)
    
    def _enforce_limits(self, conn: sqlite3.Connection):
        """Enforce memory limits by removing old entries"""
        # Check short-term memory limit
        cursor = conn.execute("""
            SELECT COUNT(*) as count FROM memories
            WHERE agent_name = ? AND memory_type = 'short_term'
        """, (self.agent_name,))
        
        short_term_count = cursor.fetchone()[0]
        
        if short_term_count > self.short_term_limit:
            # Remove oldest, least important short-term memories
            conn.execute("""
                DELETE FROM memories
                WHERE id IN (
                    SELECT id FROM memories
                    WHERE agent_name = ? AND memory_type = 'short_term'
                    ORDER BY importance ASC, accessed_at ASC
                    LIMIT ?
                )
            """, (self.agent_name, short_term_count - self.short_term_limit))
        
        # Promote important short-term memories to long-term
        conn.execute("""
            UPDATE memories
            SET memory_type = 'long_term'
            WHERE agent_name = ?
            AND memory_type = 'short_term'
            AND importance >= ?
            AND created_at < ?
        """, (
            self.agent_name,
            self.importance_threshold,
            time.time() - 3600  # Older than 1 hour
        ))
    
    def consolidate(self):
        """Consolidate and summarize old memories"""
        # This would use an LLM to summarize old memories
        # For now, just log the intent
        logger.info(f"Would consolidate memories for {self.agent_name}")
    
    def clear(self, memory_type: Optional[str] = None):
        """Clear memories, optionally by type"""
        with sqlite3.connect(self.db_path) as conn:
            if memory_type:
                conn.execute("""
                    DELETE FROM memories
                    WHERE agent_name = ? AND memory_type = ?
                """, (self.agent_name, memory_type))
            else:
                conn.execute("""
                    DELETE FROM memories
                    WHERE agent_name = ?
                """, (self.agent_name,))
            
            conn.commit()
        
        logger.info(f"Cleared memories for {self.agent_name} (type: {memory_type or 'all'})")
    
    def size(self) -> int:
        """Get total memory size in bytes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT SUM(LENGTH(content) + COALESCE(LENGTH(embedding), 0))
                FROM memories
                WHERE agent_name = ?
            """, (self.agent_name,))
            
            size = cursor.fetchone()[0] or 0
            
        return size
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Count by type
            cursor = conn.execute("""
                SELECT memory_type, COUNT(*) as count
                FROM memories
                WHERE agent_name = ?
                GROUP BY memory_type
            """, (self.agent_name,))
            
            type_counts = dict(cursor.fetchall())
            
            # Average importance
            cursor = conn.execute("""
                SELECT AVG(importance) as avg_importance
                FROM memories
                WHERE agent_name = ?
            """, (self.agent_name,))
            
            avg_importance = cursor.fetchone()[0] or 0
            
            # Memory age
            cursor = conn.execute("""
                SELECT 
                    MIN(created_at) as oldest,
                    MAX(created_at) as newest
                FROM memories
                WHERE agent_name = ?
            """, (self.agent_name,))
            
            row = cursor.fetchone()
            oldest = row[0] if row else None
            newest = row[1] if row else None
            
        return {
            "agent_name": self.agent_name,
            "total_memories": sum(type_counts.values()),
            "by_type": type_counts,
            "average_importance": round(avg_importance, 2),
            "size_bytes": self.size(),
            "oldest_memory": datetime.fromtimestamp(oldest).isoformat() if oldest else None,
            "newest_memory": datetime.fromtimestamp(newest).isoformat() if newest else None,
            "embedding_enabled": self.embedder is not None
        }


# Example usage
if __name__ == "__main__":
    memory = MemoryManager("test_agent")
    
    # Add some interactions
    memory.add_interaction(
        "What is the capital of France?",
        "The capital of France is Paris.",
        importance=0.6
    )
    
    memory.add_interaction(
        "Remember that my favorite color is blue",
        "I'll remember that your favorite color is blue.",
        importance=0.8
    )
    
    # Get relevant context
    context = memory.get_relevant_context("What's my favorite color?")
    print(f"Relevant memories: {context}")
    
    # Get stats
    print(f"Memory stats: {memory.get_stats()}")
```

## Module 5/8: cost_tracker.py
```python
# cost_tracker.py - Track and control LLM API costs
# Prevents budget overruns with alerts and automatic fallbacks

import json
import sqlite3
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import os
import smtplib
from email.mime.text import MIMEText
import httpx

logger = logging.getLogger(__name__)


@dataclass
class CostEntry:
    """Single cost entry for tracking"""
    id: Optional[int]
    timestamp: float
    model: str
    provider: str
    tokens_used: int
    cost_usd: float
    task_type: str
    agent_name: Optional[str]
    success: bool
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['metadata'] = json.dumps(data['metadata'])
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CostEntry':
        if isinstance(data['metadata'], str):
            data['metadata'] = json.loads(data['metadata'])
        return cls(**data)


class CostTracker:
    """Track LLM costs with budget enforcement and alerts"""
    
    def __init__(
        self,
        db_path: str = "/opt/litecrewai/data/costs.db",
        monthly_budget: float = 30.0,
        alert_threshold: float = 0.8
    ):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.monthly_budget = monthly_budget
        self.alert_threshold = alert_threshold
        self.alerts_sent = set()  # Track which alerts have been sent
        
        # Initialize database
        self._init_db()
        
        # Alert configuration
        self.webhook_url = os.getenv("BUDGET_WEBHOOK_URL")
        self.email_to = os.getenv("BUDGET_ALERT_EMAIL")
        
        logger.info(f"Cost tracker initialized with ${monthly_budget} monthly budget")
    
    def _init_db(self):
        """Initialize cost tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cost_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    model TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    tokens_used INTEGER NOT NULL,
                    cost_usd REAL NOT NULL,
                    task_type TEXT,
                    agent_name TEXT,
                    success INTEGER NOT NULL DEFAULT 1,
                    metadata TEXT
                )
            """)
            
            # Indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON cost_entries(timestamp DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_model ON cost_entries(model)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_month ON cost_entries(date(timestamp, 'unixepoch', 'start of month'))")
            
            # Daily aggregates table for faster reporting
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_costs (
                    date TEXT PRIMARY KEY,
                    total_cost REAL NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    request_count INTEGER NOT NULL,
                    by_model TEXT,
                    updated_at REAL NOT NULL
                )
            """)
            
            conn.commit()
    
    def track_usage(
        self,
        model: str,
        tokens_used: int,
        cost_usd: float,
        task_type: str = "general",
        agent_name: Optional[str] = None,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Track a single LLM usage"""
        # Determine provider from model name
        provider = "unknown"
        if model.startswith("ollama/"):
            provider = "ollama"
        elif model.startswith("openai/"):
            provider = "openai"
        elif model.startswith("groq/"):
            provider = "groq"
        
        entry = CostEntry(
            id=None,
            timestamp=time.time(),
            model=model,
            provider=provider,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            task_type=task_type,
            agent_name=agent_name,
            success=success,
            metadata=metadata or {}
        )
        
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            del data['id']
            
            cursor = conn.execute("""
                INSERT INTO cost_entries 
                (timestamp, model, provider, tokens_used, cost_usd, 
                 task_type, agent_name, success, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['timestamp'], data['model'], data['provider'],
                data['tokens_used'], data['cost_usd'], data['task_type'],
                data['agent_name'], data['success'], data['metadata']
            ))
            
            entry_id = cursor.lastrowid
            
            # Update daily aggregate
            self._update_daily_aggregate(conn, datetime.now().date())
            
            conn.commit()
        
        # Check budget and send alerts if needed
        self._check_budget_alerts()
        
        logger.debug(f"Tracked cost: {model} - {tokens_used} tokens - ${cost_usd:.4f}")
        return entry_id
    
    def _update_daily_aggregate(self, conn: sqlite3.Connection, date: datetime.date):
        """Update daily cost aggregate for faster queries"""
        date_str = date.isoformat()
        
        # Calculate daily totals
        cursor = conn.execute("""
            SELECT 
                SUM(cost_usd) as total_cost,
                SUM(tokens_used) as total_tokens,
                COUNT(*) as request_count,
                json_group_object(model, SUM(cost_usd)) as by_model
            FROM cost_entries
            WHERE date(timestamp, 'unixepoch') = ?
        """, (date_str,))
        
        row = cursor.fetchone()
        if row and row[0] is not None:
            conn.execute("""
                INSERT OR REPLACE INTO daily_costs 
                (date, total_cost, total_tokens, request_count, by_model, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                date_str,
                row[0] or 0,
                row[1] or 0,
                row[2] or 0,
                row[3] or '{}',
                time.time()
            ))
    
    def get_current_day_cost(self) -> float:
        """Get total cost for current day"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT total_cost FROM daily_costs
                WHERE date = date('now')
            """)
            
            row = cursor.fetchone()
            if row:
                return row[0]
            
            # Fallback to direct calculation
            cursor = conn.execute("""
                SELECT SUM(cost_usd) FROM cost_entries
                WHERE date(timestamp, 'unixepoch') = date('now')
            """)
            
            return cursor.fetchone()[0] or 0.0
    
    def get_monthly_cost(self, month: Optional[datetime] = None) -> float:
        """Get total cost for a month"""
        if month is None:
            month = datetime.now()
        
        start_of_month = month.replace(day=1, hour=0, minute=0, second=0)
        
        with sqlite3.connect(self.db_path) as conn:
            # Try daily aggregates first
            cursor = conn.execute("""
                SELECT SUM(total_cost) FROM daily_costs
                WHERE date >= ? AND date < date(?, '+1 month')
            """, (start_of_month.date().isoformat(), start_of_month.date().isoformat()))
            
            total = cursor.fetchone()[0]
            if total is not None:
                return total
            
            # Fallback to direct calculation
            cursor = conn.execute("""
                SELECT SUM(cost_usd) FROM cost_entries
                WHERE timestamp >= ? AND timestamp < ?
            """, (
                start_of_month.timestamp(),
                (start_of_month + timedelta(days=32)).replace(day=1).timestamp()
            ))
            
            return cursor.fetchone()[0] or 0.0
    
    def get_monthly_usage_percentage(self) -> float:
        """Get percentage of monthly budget used"""
        monthly_cost = self.get_monthly_cost()
        return (monthly_cost / self.monthly_budget) * 100 if self.monthly_budget > 0 else 0
    
    def get_remaining_budget(self) -> float:
        """Get remaining budget for current month"""
        return max(0, self.monthly_budget - self.get_monthly_cost())
    
    def get_model_usage_stats(self, days: int = 30) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics by model"""
        since = time.time() - (days * 86400)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    model,
                    COUNT(*) as request_count,
                    SUM(tokens_used) as total_tokens,
                    SUM(cost_usd) as total_cost,
                    AVG(tokens_used) as avg_tokens,
                    AVG(cost_usd) as avg_cost,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
                FROM cost_entries
                WHERE timestamp > ?
                GROUP BY model
                ORDER BY total_cost DESC
            """, (since,))
            
            stats = {}
            for row in cursor:
                stats[row[0]] = {
                    'request_count': row[1],
                    'total_tokens': row[2],
                    'total_cost': round(row[3], 4),
                    'avg_tokens_per_request': round(row[4], 0),
                    'avg_cost_per_request': round(row[5], 4),
                    'success_rate': round(row[6], 1)
                }
            
            return stats
    
    def get_cost_by_agent(self, days: int = 30) -> Dict[str, float]:
        """Get costs broken down by agent"""
        since = time.time() - (days * 86400)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COALESCE(agent_name, 'unknown') as agent,
                    SUM(cost_usd) as total_cost
                FROM cost_entries
                WHERE timestamp > ?
                GROUP BY agent_name
                ORDER BY total_cost DESC
            """, (since,))
            
            return dict(cursor.fetchall())
    
    def get_daily_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily cost trend"""
        since = (datetime.now() - timedelta(days=days)).date()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    date,
                    total_cost,
                    total_tokens,
                    request_count
                FROM daily_costs
                WHERE date >= ?
                ORDER BY date
            """, (since.isoformat(),))
            
            trend = []
            for row in cursor:
                trend.append({
                    'date': row[0],
                    'cost': round(row[1], 2),
                    'tokens': row[2],
                    'requests': row[3]
                })
            
            return trend
    
    def _check_budget_alerts(self):
        """Check if budget alerts need to be sent"""
        usage_pct = self.get_monthly_usage_percentage() / 100
        monthly_cost = self.get_monthly_cost()
        
        # Define alert levels
        alert_levels = [
            (0.5, "50%", "halfway through"),
            (0.8, "80%", "approaching limit"),
            (0.9, "90%", "critical - near limit"),
            (1.0, "100%", "EXCEEDED")
        ]
        
        for threshold, pct_str, description in alert_levels:
            if usage_pct >= threshold:
                alert_key = f"{datetime.now().strftime('%Y-%m')}-{pct_str}"
                
                if alert_key not in self.alerts_sent:
                    self._send_alert(
                        f"Budget Alert: {pct_str} used ({description})",
                        f"Monthly cost: ${monthly_cost:.2f} / ${self.monthly_budget:.2f}"
                    )
                    self.alerts_sent.add(alert_key)
    
    def _send_alert(self, subject: str, message: str):
        """Send budget alert via webhook and/or email"""
        full_message = f"{subject}\n\n{message}\n\nTime: {datetime.now().isoformat()}"
        
        # Send webhook
        if self.webhook_url:
            try:
                httpx.post(
                    self.webhook_url,
                    json={"text": full_message},
                    timeout=5.0
                )
                logger.info(f"Sent webhook alert: {subject}")
            except Exception as e:
                logger.error(f"Failed to send webhook alert: {e}")
        
        # Send email
        if self.email_to and os.getenv("SMTP_SERVER"):
            try:
                msg = MIMEText(full_message)
                msg['Subject'] = f"LiteCrewAI: {subject}"
                msg['From'] = os.getenv("SMTP_FROM", "litecrewai@localhost")
                msg['To'] = self.email_to
                
                with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT", "587"))) as server:
                    if os.getenv("SMTP_USER"):
                        server.starttls()
                        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
                    server.send_message(msg)
                
                logger.info(f"Sent email alert to {self.email_to}")
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
        
        # Log alert
        logger.warning(full_message)
    
    def generate_report(self, format: str = "text") -> str:
        """Generate cost report in specified format"""
        monthly_cost = self.get_monthly_cost()
        daily_cost = self.get_current_day_cost()
        usage_pct = self.get_monthly_usage_percentage()
        model_stats = self.get_model_usage_stats(30)
        agent_costs = self.get_cost_by_agent(30)
        
        if format == "text":
            report = f"""
=== LiteCrewAI Cost Report ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

BUDGET STATUS:
- Monthly Budget: ${self.monthly_budget:.2f}
- Used: ${monthly_cost:.2f} ({usage_pct:.1f}%)
- Remaining: ${self.get_remaining_budget():.2f}
- Today's Cost: ${daily_cost:.2f}

MODEL USAGE (Last 30 days):
"""
            for model, stats in model_stats.items():
                report += f"\n{model}:"
                report += f"\n  - Requests: {stats['request_count']:,}"
                report += f"\n  - Total Cost: ${stats['total_cost']:.2f}"
                report += f"\n  - Avg Cost/Request: ${stats['avg_cost_per_request']:.4f}"
                report += f"\n  - Success Rate: {stats['success_rate']}%"
            
            report += "\n\nCOST BY AGENT:"
            for agent, cost in agent_costs.items():
                report += f"\n  - {agent}: ${cost:.2f}"
            
            return report
        
        elif format == "json":
            return json.dumps({
                "generated_at": datetime.now().isoformat(),
                "budget": {
                    "monthly_limit": self.monthly_budget,
                    "used": round(monthly_cost, 2),
                    "remaining": round(self.get_remaining_budget(), 2),
                    "usage_percentage": round(usage_pct, 1),
                    "today": round(daily_cost, 2)
                },
                "model_usage": model_stats,
                "agent_costs": agent_costs
            }, indent=2)
        
        else:
            raise ValueError(f"Unknown report format: {format}")
    
    def optimize_costs(self) -> Dict[str, Any]:
        """Analyze usage and provide cost optimization recommendations"""
        model_stats = self.get_model_usage_stats(30)
        recommendations = []
        potential_savings = 0.0
        
        # Analyze expensive model usage
        for model, stats in model_stats.items():
            if "gpt-4" in model and stats['request_count'] > 10:
                # Check if simpler tasks are using expensive models
                avg_tokens = stats['avg_tokens_per_request']
                if avg_tokens < 500:  # Short responses
                    potential_savings += stats['total_cost'] * 0.7
                    recommendations.append({
                        'model': model,
                        'issue': 'Using expensive model for short responses',
                        'recommendation': 'Switch to gpt-4o-mini or Groq for simple tasks',
                        'potential_savings': round(stats['total_cost'] * 0.7, 2)
                    })
        
        # Check for high-frequency patterns that could be cached
        with sqlite3.connect(self.db_path) as conn:
            # Find repeated similar requests (simplified - in practice would use embeddings)
            cursor = conn.execute("""
                SELECT 
                    task_type,
                    COUNT(*) as count,
                    SUM(cost_usd) as total_cost
                FROM cost_entries
                WHERE timestamp > ?
                GROUP BY task_type
                HAVING count > 10
                ORDER BY total_cost DESC
            """, (time.time() - 30 * 86400,))
            
            for row in cursor:
                if row[2] > 1.0:  # More than $1 spent on similar tasks
                    potential_savings += row[2] * 0.5
                    recommendations.append({
                        'task_type': row[0],
                        'issue': f'Repeated similar tasks ({row[1]} times)',
                        'recommendation': 'Implement aggressive caching for this task type',
                        'potential_savings': round(row[2] * 0.5, 2)
                    })
        
        return {
            'total_potential_savings': round(potential_savings, 2),
            'recommendations': recommendations,
            'estimated_new_monthly_cost': round(self.get_monthly_cost() - potential_savings, 2)
        }
    
    def export_data(self, start_date: datetime, end_date: datetime, format: str = "csv") -> str:
        """Export cost data for external analysis"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM cost_entries
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp
            """, (start_date.timestamp(), end_date.timestamp()))
            
            if format == "csv":
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Header
                writer.writerow([
                    'timestamp', 'model', 'provider', 'tokens_used',
                    'cost_usd', 'task_type', 'agent_name', 'success'
                ])
                
                # Data
                for row in cursor:
                    writer.writerow(row[1:9])  # Skip ID, metadata
                
                return output.getvalue()
            
            else:
                raise ValueError(f"Unknown export format: {format}")


# Example usage
if __name__ == "__main__":
    tracker = CostTracker(monthly_budget=30.0)
    
    # Track some usage
    tracker.track_usage(
        model="openai/gpt-4o-mini",
        tokens_used=500,
        cost_usd=0.075,
        task_type="research",
        agent_name="researcher_1"
    )
    
    # Get current status
    print(f"Daily cost: ${tracker.get_current_day_cost():.2f}")
    print(f"Monthly cost: ${tracker.get_monthly_cost():.2f}")
    print(f"Budget used: {tracker.get_monthly_usage_percentage():.1f}%")
    
    # Generate report
    print(tracker.generate_report())
    
    # Get optimization recommendations
    print("\nOptimization recommendations:")
    print(json.dumps(tracker.optimize_costs(), indent=2))
```

## Module 6/8: task_processor.py
```python
# task_processor.py - Simple task queue and execution system
# Handles task dependencies and parallel execution where possible

import json
import time
import uuid
import logging
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import sqlite3
from pathlib import Path

import redis
from pydantic import BaseModel, Field

from .lite_agent import LiteAgent
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING = "waiting"  # Waiting for dependencies


class TaskPriority(int, Enum):
    """Task priority levels"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class Task:
    """Task definition with dependencies"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    agent_name: Optional[str] = None
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        data['status'] = TaskStatus(data['status'])
        data['priority'] = TaskPriority(data['priority'])
        return cls(**data)
    
    @property
    def is_ready(self) -> bool:
        """Check if task is ready to run (no pending dependencies)"""
        return self.status == TaskStatus.PENDING and not self.dependencies
    
    @property
    def execution_time(self) -> Optional[float]:
        """Get task execution time in seconds"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None


class TaskProcessor:
    """Process tasks with dependency resolution and simple queuing"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/1",
        db_path: str = "/opt/litecrewai/data/tasks.db",
        max_workers: int = 2
    ):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        
        # Task queues by priority
        self.queue_keys = {
            TaskPriority.URGENT: "tasks:urgent",
            TaskPriority.HIGH: "tasks:high",
            TaskPriority.NORMAL: "tasks:normal",
            TaskPriority.LOW: "tasks:low"
        }
        
        # Active tasks tracking
        self.active_tasks: Dict[str, Task] = {}
        self.task_results: Dict[str, Any] = {}
        
        # Agents registry
        self.agents: Dict[str, LiteAgent] = {}
        
        # Thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Initialize database
        self._init_db()
        
        logger.info(f"Task processor initialized with {max_workers} workers")
    
    def _init_db(self):
        """Initialize task history database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    agent_name TEXT,
                    status TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    dependencies TEXT,
                    context TEXT,
                    result TEXT,
                    error TEXT,
                    created_at REAL NOT NULL,
                    started_at REAL,
                    completed_at REAL,
                    execution_time REAL,
                    retry_count INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON task_history(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON task_history(created_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent ON task_history(agent_name)")
            
            conn.commit()
    
    def register_agent(self, agent: LiteAgent):
        """Register an agent for task execution"""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def submit_task(self, task: Task) -> str:
        """Submit a task for execution"""
        # Store task
        self.active_tasks[task.id] = task
        self._save_task_to_db(task)
        
        # Check dependencies
        if task.dependencies:
            task.status = TaskStatus.WAITING
            logger.info(f"Task {task.id} waiting for dependencies: {task.dependencies}")
        else:
            # Add to appropriate queue
            queue_key = self.queue_keys[task.priority]
            self.redis.lpush(queue_key, task.id)
            logger.info(f"Task {task.id} queued with priority {task.priority.name}")
        
        return task.id
    
    def submit_crew(self, tasks: List[Task]) -> List[str]:
        """Submit multiple tasks with dependency management"""
        task_ids = []
        
        # Validate dependencies exist
        task_id_set = {t.id for t in tasks}
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_id_set:
                    raise ValueError(f"Task {task.id} has unknown dependency: {dep_id}")
        
        # Submit all tasks
        for task in tasks:
            task_id = self.submit_task(task)
            task_ids.append(task_id)
        
        logger.info(f"Submitted crew of {len(tasks)} tasks")
        return task_ids
    
    def get_next_task(self) -> Optional[Task]:
        """Get next task from queues by priority"""
        for priority in [TaskPriority.URGENT, TaskPriority.HIGH, 
                        TaskPriority.NORMAL, TaskPriority.LOW]:
            queue_key = self.queue_keys[priority]
            
            # Try to pop from queue
            task_id = self.redis.rpop(queue_key)
            if task_id:
                task = self.active_tasks.get(task_id)
                if task and task.is_ready:
                    return task
        
        return None
    
    def execute_task(self, task: Task) -> Any:
        """Execute a single task"""
        logger.info(f"Executing task {task.id}: {task.name}")
        
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        self._save_task_to_db(task)
        
        try:
            # Get agent
            if task.agent_name and task.agent_name in self.agents:
                agent = self.agents[task.agent_name]
            else:
                # Use default agent
                agent = self._get_default_agent()
            
            # Prepare context with dependency results
            full_context = task.context.copy()
            for dep_id in task.dependencies:
                if dep_id in self.task_results:
                    full_context[f"dep_{dep_id}"] = self.task_results[dep_id]
            
            # Execute
            result = agent.execute(task.description, full_context)
            
            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = time.time()
            
            # Store result for dependent tasks
            self.task_results[task.id] = result
            
            logger.info(f"Task {task.id} completed in {task.execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = time.time()
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                logger.info(f"Retrying task {task.id} (attempt {task.retry_count})")
                
                # Re-queue with slight delay
                time.sleep(2 ** task.retry_count)
                queue_key = self.queue_keys[task.priority]
                self.redis.lpush(queue_key, task.id)
        
        finally:
            self._save_task_to_db(task)
            self._check_dependent_tasks(task.id)
        
        return task.result
    
    def _check_dependent_tasks(self, completed_task_id: str):
        """Check and queue tasks that were waiting for this dependency"""
        for task in self.active_tasks.values():
            if task.status == TaskStatus.WAITING and completed_task_id in task.dependencies:
                # Remove completed dependency
                task.dependencies.remove(completed_task_id)
                
                # Check if ready to run
                if not task.dependencies:
                    task.status = TaskStatus.PENDING
                    queue_key = self.queue_keys[task.priority]
                    self.redis.lpush(queue_key, task.id)
                    logger.info(f"Task {task.id} ready after dependency completion")
    
    def process_tasks(self, timeout: Optional[float] = None):
        """Main processing loop"""
        start_time = time.time()
        processed = 0
        
        while True:
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                break
            
            # Get next task
            task = self.get_next_task()
            if not task:
                # No tasks available, wait a bit
                time.sleep(0.1)
                continue
            
            # Execute task
            self.execute_task(task)
            processed += 1
            
            # Clean up completed tasks from memory after a while
            if processed % 10 == 0:
                self._cleanup_completed_tasks()
        
        logger.info(f"Processed {processed} tasks")
        return processed
    
    def process_async(self):
        """Async processing with multiple workers"""
        async def worker(worker_id: int):
            logger.info(f"Worker {worker_id} started")
            
            while True:
                task = self.get_next_task()
                if task:
                    # Run in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(self.executor, self.execute_task, task)
                else:
                    await asyncio.sleep(0.1)
        
        # Create workers
        async def main():
            workers = [worker(i) for i in range(self.max_workers)]
            await asyncio.gather(*workers)
        
        asyncio.run(main())
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current task status"""
        task = self.active_tasks.get(task_id)
        if task:
            return task.to_dict()
        
        # Check database for historical task
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM task_history WHERE id = ?
            """, (task_id,))
            
            row = cursor.fetchone()
            if row:
                return self._row_to_task_dict(row)
        
        return None
    
    def wait_for_task(self, task_id: str, timeout: float = 300) -> Optional[Any]:
        """Wait for a task to complete"""
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            task = self.active_tasks.get(task_id)
            
            if task and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return task.result if task.status == TaskStatus.COMPLETED else None
            
            time.sleep(0.5)
        
        raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task"""
        task = self.active_tasks.get(task_id)
        
        if task and task.status in [TaskStatus.PENDING, TaskStatus.WAITING]:
            task.status = TaskStatus.CANCELLED
            task.completed_at = time.time()
            self._save_task_to_db(task)
            
            # Remove from queue if present
            for queue_key in self.queue_keys.values():
                self.redis.lrem(queue_key, 0, task_id)
            
            logger.info(f"Cancelled task {task_id}")
            return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Task counts by status
            cursor = conn.execute("""
                SELECT status, COUNT(*) FROM task_history
                GROUP BY status
            """)
            status_counts = dict(cursor.fetchall())
            
            # Average execution time
            cursor = conn.execute("""
                SELECT AVG(execution_time) FROM task_history
                WHERE status = 'completed' AND execution_time IS NOT NULL
            """)
            avg_execution_time = cursor.fetchone()[0] or 0
            
            # Queue lengths
            queue_lengths = {}
            for priority, queue_key in self.queue_keys.items():
                queue_lengths[priority.name] = self.redis.llen(queue_key)
        
        return {
            "tasks_by_status": status_counts,
            "average_execution_time": round(avg_execution_time, 2),
            "queue_lengths": queue_lengths,
            "active_tasks": len(self.active_tasks),
            "registered_agents": list(self.agents.keys())
        }
    
    def _save_task_to_db(self, task: Task):
        """Save task to database"""
        with sqlite3.connect(self.db_path) as conn:
            data = task.to_dict()
            
            # Convert complex fields to JSON
            data['dependencies'] = json.dumps(data['dependencies'])
            data['context'] = json.dumps(data['context'])
            data['result'] = json.dumps(data['result']) if data['result'] else None
            data['execution_time'] = task.execution_time
            
            conn.execute("""
                INSERT OR REPLACE INTO task_history
                (id, name, description, agent_name, status, priority,
                 dependencies, context, result, error, created_at,
                 started_at, completed_at, execution_time, retry_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['id'], data['name'], data['description'],
                data['agent_name'], data['status'], data['priority'],
                data['dependencies'], data['context'], data['result'],
                data['error'], data['created_at'], data['started_at'],
                data['completed_at'], data['execution_time'], data['retry_count']
            ))
            
            conn.commit()
    
    def _cleanup_completed_tasks(self):
        """Remove old completed tasks from memory"""
        cutoff_time = time.time() - 3600  # 1 hour
        
        to_remove = []
        for task_id, task in self.active_tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
                and task.completed_at and task.completed_at < cutoff_time):
                to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.active_tasks[task_id]
            if task_id in self.task_results:
                del self.task_results[task_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} completed tasks")
    
    def _get_default_agent(self) -> LiteAgent:
        """Get or create default agent"""
        if "default" not in self.agents:
            from .lite_agent import create_agent, AgentRole
            self.agents["default"] = create_agent(
                "default",
                AgentRole.ASSISTANT,
                "Complete tasks efficiently"
            )
        return self.agents["default"]
    
    def _row_to_task_dict(self, row: tuple) -> Dict[str, Any]:
        """Convert database row to task dictionary"""
        columns = [
            'id', 'name', 'description', 'agent_name', 'status', 'priority',
            'dependencies', 'context', 'result', 'error', 'created_at',
            'started_at', 'completed_at', 'execution_time', 'retry_count'
        ]
        
        data = dict(zip(columns, row))
        
        # Parse JSON fields
        data['dependencies'] = json.loads(data['dependencies']) if data['dependencies'] else []
        data['context'] = json.loads(data['context']) if data['context'] else {}
        data['result'] = json.loads(data['result']) if data['result'] else None
        
        return data


# Example usage
if __name__ == "__main__":
    processor = TaskProcessor()
    
    # Create some tasks with dependencies
    task1 = Task(
        name="Research Python",
        description="Research the latest Python features",
        priority=TaskPriority.HIGH
    )
    
    task2 = Task(
        name="Write Summary",
        description="Write a summary of the research findings",
        dependencies=[task1.id],
        priority=TaskPriority.NORMAL
    )
    
    task3 = Task(
        name="Create Presentation",
        description="Create a presentation based on the summary",
        dependencies=[task2.id],
        priority=TaskPriority.LOW
    )
    
    # Submit tasks
    processor.submit_crew([task1, task2, task3])
    
    # Process tasks
    processor.process_tasks(timeout=60)
    
    # Get results
    print(f"Task 1 result: {processor.get_task_status(task1.id)}")
    print(f"Task 2 result: {processor.get_task_status(task2.id)}")
    print(f"Task 3 result: {processor.get_task_status(task3.id)}")
    
    print(f"\nProcessor stats: {processor.get_stats()}")
```