# 🚀 LinkedIn Lunatics - Szczegółowy Plan Projektu

## 📊 Struktura Planu
```
Projekt (3 miesiące)
└── Fazy (2-3 tygodnie)
    └── Milestones (3-5 dni)
        └── Bloki Zadań (1-2 dni)
            └── Zadania Atomowe (2-8h)
                └── Metryki + Walidacja
```

---

# POZIOM 1: Przegląd Wysokopoziomowy (3 miesiące)

## 🎯 Cel Projektu
Zbudować w pełni zautomatyzowany system generujący ultra-cringe LinkedIn posty, dystrybuujący je na wielu platformach i budujący engaged community.

## 📅 Timeline
- **Faza 1**: Infrastruktura & Core Engine (Tydzień 1-3)
- **Faza 2**: Content Generation & Quality (Tydzień 4-6)
- **Faza 3**: Distribution & Automation (Tydzień 7-8)
- **Faza 4**: Community & Monetization (Tydzień 9-12)

---

# POZIOM 2: Breakdown Faz

## Faza 1: Infrastruktura & Core Engine (21 dni)

### Milestone 1.1: Environment Setup (5 dni)
- Konfiguracja DigitalOcean droplet
- Instalacja LiteCrewAI core
- Setup bazy danych i cache

### Milestone 1.2: Agent Architecture (7 dni)
- Implementacja LinkedIn personality agents
- System promptów i templates
- Testing pipeline

### Milestone 1.3: Basic Generation (5 dni)
- Pierwszy working prototype
- 10 example posts
- Feedback loop

### Milestone 1.4: Storage & API (4 dni)
- SQLite schema
- REST API endpoints
- Basic web interface

---

# POZIOM 3: Szczegółowe Bloki Zadań

## 📦 Blok 1.1.1: Droplet Setup & Configuration

### Zadania Atomowe:

#### Task 1.1.1.1: Create DigitalOcean Droplet (2h)
**Działania:**
- Utworzenie droplet Ubuntu 22.04, 2GB RAM
- Konfiguracja SSH keys
- Setup firewall (ufw)
- Utworzenie użytkownika non-root

**Metryki Sukcesu:**
- ✅ SSH dostęp działa: `ssh user@ip` zwraca prompt
- ✅ Firewall aktywny: `sudo ufw status` pokazuje active
- ✅ Porty 22, 80, 443 otwarte
- ✅ Non-root user ma sudo privileges

**Walidacja:**
```bash
# validation_script_1.sh
#!/bin/bash
ssh -o ConnectTimeout=5 lunatics@$DROPLET_IP "whoami" | grep -q "lunatics" || exit 1
ssh lunatics@$DROPLET_IP "sudo ufw status" | grep -q "Status: active" || exit 1
echo "✅ Droplet setup validated"
```

#### Task 1.1.1.2: Install Base Dependencies (3h)
**Działania:**
- Install Python 3.11, pip, venv
- Install Redis, SQLite3, Nginx
- Install git, htop, tmux, curl
- Configure swap (2GB)

**Metryki Sukcesu:**
- ✅ Python 3.11 zainstalowany: `python3.11 --version`
- ✅ Redis running: `redis-cli ping` returns PONG
- ✅ Nginx active: `systemctl status nginx`
- ✅ 2GB swap configured: `free -h` shows swap

**Walidacja:**
```python
# validate_deps.py
import subprocess
import sys

checks = {
    "Python 3.11": "python3.11 --version",
    "Redis": "redis-cli ping",
    "Nginx": "systemctl is-active nginx",
    "Swap": "swapon --show"
}

for name, cmd in checks.items():
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        assert result.returncode == 0, f"{name} check failed"
        print(f"✅ {name} OK")
    except Exception as e:
        print(f"❌ {name} FAILED: {e}")
        sys.exit(1)
```

#### Task 1.1.1.3: Setup Project Structure (1h)
**Działania:**
- Create /opt/linkedin-lunatics/
- Setup directory structure
- Init git repository
- Create .env template

**Metryki Sukcesu:**
- ✅ Directories exist with correct permissions
- ✅ Git initialized with .gitignore
- ✅ .env.example contains all needed vars

**Walidacja:**
```bash
# Check directory structure
test -d /opt/linkedin-lunatics/app || exit 1
test -d /opt/linkedin-lunatics/data || exit 1
test -d /opt/linkedin-lunatics/logs || exit 1
test -f /opt/linkedin-lunatics/.env.example || exit 1
```

---

## 📦 Blok 1.1.2: LiteCrewAI Installation

### Zadania Atomowe:

#### Task 1.1.2.1: Clone and Setup LiteCrewAI (2h)
**Działania:**
- Clone LiteCrewAI repository
- Remove telemetry code
- Setup Python virtual environment
- Install core dependencies

**Metryki Sukcesu:**
- ✅ No telemetry imports: `grep -r "telemetry" src/` returns 0
- ✅ Venv activated: `which python` shows venv path
- ✅ Core imports work: `python -c "import crewai"`

**Walidacja:**
```python
# test_litecrewai_setup.py
import importlib
import os

# Check no telemetry
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            with open(os.path.join(root, file)) as f:
                assert 'telemetry' not in f.read().lower()

# Check core imports
required_modules = ['crewai', 'pydantic', 'sqlite3', 'redis']
for module in required_modules:
    importlib.import_module(module)
    print(f"✅ {module} imported successfully")
```

#### Task 1.1.2.2: Install and Configure Ollama (3h)
**Działania:**
- Install Ollama
- Pull mistral and phi models
- Configure systemd service
- Test local generation

**Metryki Sukcesu:**
- ✅ Ollama service active
- ✅ Models downloaded: `ollama list` shows both
- ✅ Generation works: <2s response time
- ✅ Auto-start enabled

**Walidacja:**
```python
# test_ollama.py
import requests
import time

# Check service
resp = requests.get("http://localhost:11434/api/tags")
assert resp.status_code == 200
models = resp.json()['models']
assert any('mistral' in m['name'] for m in models)

# Test generation speed
start = time.time()
resp = requests.post("http://localhost:11434/api/generate", 
    json={"model": "mistral", "prompt": "Hi"})
assert time.time() - start < 2.0
print("✅ Ollama ready")
```

---

## 📦 Blok 1.2.1: LinkedIn Personality Agents

### Zadania Atomowe:

#### Task 1.2.1.1: Create Base Agent Class (4h)
**Działania:**
- Design LinkedInPersonality base class
- Implement personality traits system
- Add cringe score calculator
- Create agent factory

**Metryki Sukcesu:**
- ✅ Base class with required methods
- ✅ 5+ personality traits defined
- ✅ Cringe score 0-100 range
- ✅ Factory creates agents dynamically

**Walidacja:**
```python
# test_agent_base.py
from agents import LinkedInPersonality, AgentFactory

# Test base class
agent = LinkedInPersonality(name="Test", traits={"humble_brag": 0.9})
assert hasattr(agent, 'generate_post')
assert hasattr(agent, 'calculate_cringe_score')

# Test factory
factory = AgentFactory()
agent_types = ['CryingCEO', 'StartupBro', 'MotivationalCoach']
for agent_type in agent_types:
    agent = factory.create(agent_type)
    assert agent is not None
    post = agent.generate_post()
    assert len(post) > 50
    assert 0 <= agent.calculate_cringe_score(post) <= 100
```

[... kontynuacja wszystkich pozostałych bloków zadań ...]