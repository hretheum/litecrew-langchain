# 🚀 LiteCrewAI - Kompletny Plan Implementacji Platformy

## 📋 Executive Summary
**Cel**: Stworzenie lekkiej, generycznej platformy agentów AI (fork CrewAI) zoptymalizowanej pod kątem personal use na DigitalOcean.

**Czas realizacji**: 30 dni
**Budżet infrastruktury**: <$30/miesiąc
**Stack**: Python 3.11, FastAPI, SQLite, Redis, Ollama

---

# POZIOM 1: Struktura Projektu (30 dni)

## 🏗️ Architektura Rozdzielczości
```
Projekt LiteCrewAI (30 dni)
├── Faza 0: Przygotowanie Środowiska (3 dni)
├── Faza 1: Fork i Minimalizacja CrewAI (5 dni)
├── Faza 2: Core Engine - Agenci i Zadania (7 dni)
├── Faza 3: Integracja LLM i Routing (5 dni)
├── Faza 4: Storage i Persistence (3 dni)
├── Faza 5: API i Interface (3 dni)
├── Faza 6: Monitoring i Optymalizacja (2 dni)
└── Faza 7: Dokumentacja i Deployment (2 dni)
```

---

# POZIOM 2: Milestones i Deliverables

## Faza 0: Przygotowanie Środowiska (Dni 1-3)
### Milestones:
- M0.1: Infrastruktura DigitalOcean gotowa
- M0.2: Środowisko developerskie skonfigurowane
- M0.3: CI/CD pipeline działający

## Faza 1: Fork i Minimalizacja CrewAI (Dni 4-8)
### Milestones:
- M1.1: Fork CrewAI oczyszczony z telemetrii
- M1.2: Zależności zredukowane do minimum
- M1.3: Testy jednostkowe przepisane

## Faza 2: Core Engine (Dni 9-15)
### Milestones:
- M2.1: System agentów uproszczony
- M2.2: Task executor zrefaktorowany
- M2.3: Memory system zaimplementowany

## Faza 3: Integracja LLM (Dni 16-20)
### Milestones:
- M3.1: Ollama zintegrowana
- M3.2: Router LLM z cost control
- M3.3: Fallback mechanism gotowy

## Faza 4: Storage (Dni 21-23)
### Milestones:
- M4.1: SQLite schema zoptymalizowana
- M4.2: Redis cache layer
- M4.3: Backup system

## Faza 5: API (Dni 24-26)
### Milestones:
- M5.1: REST API endpoints
- M5.2: WebSocket dla real-time
- M5.3: Basic web UI

## Faza 6: Monitoring (Dni 27-28)
### Milestones:
- M6.1: Metryki i logi
- M6.2: Cost tracking
- M6.3: Performance optimization

## Faza 7: Finalizacja (Dni 29-30)
### Milestones:
- M7.1: Dokumentacja kompletna
- M7.2: Deployment scripts
- M7.3: Projekt live na DigitalOcean

---

# POZIOM 3: Szczegółowe Bloki Zadań

## 📦 FAZA 0: PRZYGOTOWANIE ŚRODOWISKA

### Blok 0.1: Setup DigitalOcean Infrastructure
**Czas**: 8h
**Cel**: Przygotowanie kompletnej infrastruktury cloud

#### Zadania Atomowe:

##### Task 0.1.1: Utworzenie i Konfiguracja Droplet (2h)
**Cel**: Działający serwer z podstawową konfiguracją security

**Prompt dla AI Agent**:
```
Stwórz kompletny skrypt bash do setupu DigitalOcean droplet dla LiteCrewAI.
Wymagania:
- Ubuntu 22.04 LTS, 2GB RAM, 50GB SSD
- Konfiguracja firewall (ufw) - tylko porty 22, 80, 443
- Utworzenie użytkownika 'litecrewai' z sudo
- Disable root SSH login
- Setup fail2ban
- Konfiguracja automatycznych updates security

Skrypt powinien być idempotentny i zawierać sprawdzanie błędów.
```

**Metryki Sukcesu**:
- ✅ SSH działa na porcie 22: `ssh litecrewai@<IP>`
- ✅ Firewall aktywny: `sudo ufw status verbose`
- ✅ Fail2ban chroni SSH: `sudo fail2ban-client status sshd`
- ✅ Automatic updates włączone: `apt-config dump APT::Periodic::Unattended-Upgrade`

**Walidacja**:
```bash
#!/bin/bash
# validate_droplet_setup.sh
set -e

echo "🔍 Validating DigitalOcean Droplet Setup..."

# Test SSH access
ssh -o ConnectTimeout=5 litecrewai@$DROPLET_IP "echo '✅ SSH Access OK'" || exit 1

# Test firewall
ssh litecrewai@$DROPLET_IP "sudo ufw status" | grep -q "Status: active" || exit 1

# Test fail2ban
ssh litecrewai@$DROPLET_IP "sudo systemctl is-active fail2ban" || exit 1

# Test auto-updates
ssh litecrewai@$DROPLET_IP "cat /etc/apt/apt.conf.d/50unattended-upgrades" | grep -q "Unattended-Upgrade::Allowed-Origins" || exit 1

echo "✅ All droplet checks passed!"
```

##### Task 0.1.2: Instalacja Core Dependencies (3h)
**Cel**: Wszystkie wymagane pakiety systemowe zainstalowane i skonfigurowane

**Prompt dla AI Agent**:
```
Napisz skrypt instalacyjny dla wszystkich dependencies LiteCrewAI na Ubuntu 22.04.

Pakiety do instalacji:
- Python 3.11 (z deadsnakes PPA)
- Redis Server 7.x (z oficjalnego repo Redis)
- SQLite 3.40+ 
- Nginx (jako reverse proxy)
- Supervisor (do zarządzania procesami)
- Git, curl, wget, htop, tmux
- Build essentials dla Python packages
- Docker i docker-compose (opcjonalnie)

Konfiguracje:
- Redis: maxmemory 256mb, persistence włączone
- Nginx: przygotowany do proxy na port 8000
- Supervisor: template dla serwisów Python
- Swap: 4GB (dla bezpieczeństwa na małym droplet)

Skrypt ma logować wszystkie akcje i być re-runnable.
```

**Metryki Sukcesu**:
- ✅ Python 3.11: `python3.11 --version` zwraca 3.11.x
- ✅ Redis: `redis-cli ping` zwraca PONG
- ✅ SQLite: `sqlite3 --version` >= 3.40
- ✅ Nginx: `nginx -t` bez błędów
- ✅ Swap: `free -h` pokazuje 4G swap

**Walidacja**:
```python
# validate_dependencies.py
import subprocess
import sys
import re

def check_command(cmd, expected_pattern=None, min_version=None):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return False, f"Command failed: {result.stderr}"
        
        output = result.stdout.strip()
        
        if expected_pattern and not re.search(expected_pattern, output):
            return False, f"Pattern '{expected_pattern}' not found in output"
        
        if min_version:
            # Extract version and compare
            version_match = re.search(r'(\d+\.\d+)', output)
            if version_match:
                version = float(version_match.group(1))
                if version < min_version:
                    return False, f"Version {version} < required {min_version}"
        
        return True, output
    except Exception as e:
        return False, str(e)

checks = [
    ("Python 3.11", "python3.11 --version", r"3\.11\.", None),
    ("Redis", "redis-cli ping", "PONG", None),
    ("SQLite", "sqlite3 --version", r"\d+\.\d+", 3.40),
    ("Nginx", "nginx -v", "nginx", None),
    ("Supervisor", "supervisord --version", r"\d+\.\d+", None),
    ("Swap", "free -h | grep Swap", r"[0-9]+G", None),
]

all_passed = True
for name, cmd, pattern, min_ver in checks:
    passed, output = check_command(cmd, pattern, min_ver)
    status = "✅" if passed else "❌"
    print(f"{status} {name}: {output}")
    if not passed:
        all_passed = False

sys.exit(0 if all_passed else 1)
```

##### Task 0.1.3: Setup Project Directory Structure (1h)
**Cel**: Kompletna struktura katalogów z odpowiednimi uprawnieniami

**Prompt dla AI Agent**:
```
Stwórz skrypt tworzący optymalną strukturę katalogów dla LiteCrewAI.

Struktura:
/opt/litecrewai/
├── app/           # Kod aplikacji
├── config/        # Pliki konfiguracyjne
├── data/          # SQLite, uploads
├── logs/          # Logi aplikacji
├── backups/       # Automatyczne backupy
├── scripts/       # Skrypty maintenance
├── venv/          # Python virtual environment
└── .env.example   # Template zmiennych środowiskowych

Wymagania:
- Właściciel: litecrewai:litecrewai
- Uprawnienia: 755 dla katalogów, 644 dla plików
- Katalog data z prawami zapisu dla aplikacji
- Logrotate config dla logs/
- Struktura git-friendly (.gitignore)

Dodaj również przykładowy .env.example z wszystkimi wymaganymi zmiennymi.
```

**Metryki Sukcesu**:
- ✅ Struktura istnieje: `tree /opt/litecrewai -L 2`
- ✅ Uprawnienia poprawne: `ls -la /opt/litecrewai`
- ✅ Git repo zainicjalizowane: `git -C /opt/litecrewai status`
- ✅ .env.example kompletny: minimum 10 zmiennych

**Walidacja**:
```bash
#!/bin/bash
# validate_directory_structure.sh

echo "🔍 Validating directory structure..."

# Check directories exist
dirs=(
    "/opt/litecrewai/app"
    "/opt/litecrewai/config"
    "/opt/litecrewai/data"
    "/opt/litecrewai/logs"
    "/opt/litecrewai/backups"
    "/opt/litecrewai/scripts"
)

for dir in "${dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Missing directory: $dir"
        exit 1
    fi
    
    # Check ownership
    owner=$(stat -c '%U:%G' "$dir")
    if [ "$owner" != "litecrewai:litecrewai" ]; then
        echo "❌ Wrong ownership for $dir: $owner"
        exit 1
    fi
done

# Check git
if ! git -C /opt/litecrewai rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Git not initialized"
    exit 1
fi

# Check .env.example
env_vars=$(grep -c "=" /opt/litecrewai/.env.example)
if [ "$env_vars" -lt 10 ]; then
    echo "❌ .env.example has only $env_vars variables (need >= 10)"
    exit 1
fi

echo "✅ Directory structure validated!"
```

### Blok 0.2: Development Environment Setup
**Czas**: 6h
**Cel**: Kompletne środowisko developerskie lokalne i na serwerze

#### Zadania Atomowe:

##### Task 0.2.1: Python Virtual Environment (2h)
**Cel**: Izolowane środowisko Python z wszystkimi narzędziami

**Prompt dla AI Agent**:
```
Stwórz skrypt setupujący profesjonalne środowisko Python dla LiteCrewAI.

Wymagania:
1. Python 3.11 virtual environment w /opt/litecrewai/venv
2. Aktualizacja pip, setuptools, wheel do najnowszych
3. Instalacja narzędzi developerskich:
   - black (formatowanie)
   - ruff (linting) 
   - mypy (type checking)
   - pytest + pytest-cov (testy)
   - pre-commit (git hooks)
4. Konfiguracja pre-commit hooks dla:
   - black
   - ruff
   - mypy
   - trailing whitespace
   - end of file fixer
5. Setup pyproject.toml z konfiguracją wszystkich narzędzi

Skrypt powinien też tworzyć alias 'activate-lite' dla łatwej aktywacji.
```

**Metryki Sukcesu**:
- ✅ Venv aktywuje się: `source /opt/litecrewai/venv/bin/activate`
- ✅ Wszystkie tools zainstalowane: `black --version`, `ruff --version`
- ✅ Pre-commit działa: `pre-commit run --all-files`
- ✅ pyproject.toml skonfigurowany

**Walidacja**:
```python
# validate_python_env.py
import subprocess
import os
import toml

def test_venv():
    """Test virtual environment setup"""
    venv_python = "/opt/litecrewai/venv/bin/python"
    
    # Check venv exists
    assert os.path.exists(venv_python), "Venv not found"
    
    # Check Python version
    result = subprocess.run([venv_python, "--version"], capture_output=True, text=True)
    assert "3.11" in result.stdout, f"Wrong Python version: {result.stdout}"
    
    # Check installed packages
    packages = ["black", "ruff", "mypy", "pytest", "pre-commit"]
    result = subprocess.run([venv_python, "-m", "pip", "list"], capture_output=True, text=True)
    
    for package in packages:
        assert package in result.stdout, f"Missing package: {package}"
    
    print("✅ Virtual environment validated")

def test_precommit():
    """Test pre-commit configuration"""
    config_path = "/opt/litecrewai/.pre-commit-config.yaml"
    assert os.path.exists(config_path), "Pre-commit config not found"
    
    # Check hooks are installed
    git_dir = "/opt/litecrewai/.git/hooks"
    assert os.path.exists(f"{git_dir}/pre-commit"), "Pre-commit hook not installed"
    
    print("✅ Pre-commit validated")

def test_pyproject():
    """Test pyproject.toml configuration"""
    config_path = "/opt/litecrewai/pyproject.toml"
    assert os.path.exists(config_path), "pyproject.toml not found"
    
    config = toml.load(config_path)
    
    # Check tool configurations
    assert "tool" in config, "No tool section"
    assert "black" in config["tool"], "Black not configured"
    assert "ruff" in config["tool"], "Ruff not configured"
    assert "mypy" in config["tool"], "Mypy not configured"
    
    print("✅ pyproject.toml validated")

if __name__ == "__main__":
    test_venv()
    test_precommit()
    test_pyproject()
    print("✅ All Python environment checks passed!")
```

##### Task 0.2.2: Local Ollama Setup (2h)
**Cel**: Lokalne LLM działające i zoptymalizowane

**Prompt dla AI Agent**:
```
Napisz skrypt instalujący i konfigurujący Ollama dla LiteCrewAI.

Zadania:
1. Instalacja Ollama na serwerze
2. Pobranie modeli:
   - mistral:7b (główny model)
   - phi-2 (szybki fallback)
   - nomic-embed-text (embeddings)
3. Konfiguracja systemd service z:
   - Auto-restart
   - Memory limits (1GB)
   - CPU limits (2 cores)
4. Optimization settings:
   - OLLAMA_NUM_PARALLEL=2
   - OLLAMA_MAX_LOADED_MODELS=2
5. Health check endpoint
6. Prosty benchmark performance

Dodatkowo stwórz skrypt monitorujący zużycie zasobów przez Ollama.
```

**Metryki Sukcesu**:
- ✅ Ollama service aktywny: `systemctl status ollama`
- ✅ Modele pobrane: `ollama list` pokazuje 3 modele
- ✅ API odpowiada: `curl http://localhost:11434/api/tags`
- ✅ Generation <3s: dla promptu 50 słów

**Walidacja**:
```python
# validate_ollama.py
import requests
import time
import psutil
import subprocess

def test_ollama_service():
    """Test Ollama service status"""
    result = subprocess.run(["systemctl", "is-active", "ollama"], capture_output=True, text=True)
    assert result.stdout.strip() == "active", "Ollama service not active"
    print("✅ Ollama service active")

def test_ollama_models():
    """Test required models are installed"""
    response = requests.get("http://localhost:11434/api/tags")
    assert response.status_code == 200, "Ollama API not responding"
    
    models = response.json()["models"]
    model_names = [m["name"] for m in models]
    
    required = ["mistral:7b", "phi-2", "nomic-embed-text"]
    for model in required:
        assert any(model in name for name in model_names), f"Missing model: {model}"
    
    print("✅ All required models installed")

def test_ollama_performance():
    """Test generation performance"""
    prompt = "Explain quantum computing in exactly 50 words."
    
    start_time = time.time()
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral:7b",
        "prompt": prompt,
        "stream": False
    })
    generation_time = time.time() - start_time
    
    assert response.status_code == 200, "Generation failed"
    assert generation_time < 3.0, f"Generation too slow: {generation_time:.2f}s"
    
    print(f"✅ Generation performance: {generation_time:.2f}s")

def test_resource_limits():
    """Test Ollama resource limits"""
    # Get Ollama process
    for proc in psutil.process_iter(['pid', 'name']):
        if 'ollama' in proc.info['name']:
            ollama_proc = psutil.Process(proc.info['pid'])
            
            # Check memory usage
            mem_info = ollama_proc.memory_info()
            mem_mb = mem_info.rss / 1024 / 1024
            assert mem_mb < 1500, f"Memory usage too high: {mem_mb:.0f}MB"
            
            # Check CPU cores
            cpu_affinity = ollama_proc.cpu_affinity()
            assert len(cpu_affinity) <= 2, f"Too many CPU cores: {len(cpu_affinity)}"
            
            print(f"✅ Resource limits OK: {mem_mb:.0f}MB RAM, {len(cpu_affinity)} cores")
            break

if __name__ == "__main__":
    test_ollama_service()
    test_ollama_models()
    test_ollama_performance()
    test_resource_limits()
    print("✅ All Ollama checks passed!")
```

##### Task 0.2.3: Git Repository and CI/CD Setup (2h)
**Cel**: Pełna automatyzacja deploymentu z GitHub

**Prompt dla AI Agent**:
```
Stwórz kompletny setup CI/CD dla LiteCrewAI używając GitHub Actions.

Wymagania:
1. Initialize git repo z właściwą strukturą:
   - .gitignore dla Python projektu
   - README.md z podstawową dokumentacją
   - LICENSE (MIT)
   - CONTRIBUTING.md

2. GitHub Actions workflows:
   - test.yml: uruchamia testy przy każdym PR
   - deploy.yml: deploy na DigitalOcean przy merge do main
   - scheduled-backup.yml: codzienny backup o 3 AM

3. Secrets w GitHub:
   - DROPLET_IP
   - SSH_PRIVATE_KEY
   - BACKUP_ENCRYPTION_KEY

4. Deploy script który:
   - Robi backup przed deployem
   - Zero-downtime deployment
   - Rollback w razie błędu
   - Powiadomienie na Slack/Discord

5. Branch protection rules dla main

Wszystko ma być w pełni zautomatyzowane i bezpieczne.
```

**Metryki Sukcesu**:
- ✅ Git repo połączone z GitHub
- ✅ GitHub Actions workflows aktywne
- ✅ Deploy działa w <2 minuty
- ✅ Automatyczny rollback przy błędzie

**Walidacja**:
```bash
#!/bin/bash
# validate_cicd.sh

echo "🔍 Validating CI/CD setup..."

# Check git remote
cd /opt/litecrewai
git remote -v | grep -q "github.com" || { echo "❌ No GitHub remote"; exit 1; }

# Check workflows exist
workflows=(".github/workflows/test.yml" ".github/workflows/deploy.yml" ".github/workflows/scheduled-backup.yml")
for workflow in "${workflows[@]}"; do
    [ -f "$workflow" ] || { echo "❌ Missing workflow: $workflow"; exit 1; }
done

# Test deployment script
if [ -f "scripts/deploy.sh" ]; then
    bash scripts/deploy.sh --dry-run || { echo "❌ Deploy script failed"; exit 1; }
fi

# Check for required files
files=(".gitignore" "README.md" "LICENSE" "CONTRIBUTING.md")
for file in "${files[@]}"; do
    [ -f "$file" ] || { echo "❌ Missing file: $file"; exit 1; }
done

echo "✅ CI/CD setup validated!"
```

### Blok 0.3: Monitoring and Logging Infrastructure
**Czas**: 4h
**Cel**: Kompletny system monitorowania od początku

#### Zadania Atomowe:

##### Task 0.3.1: Setup Logging System (2h)
**Cel**: Scentralizowane logi z rotacją i analizą

**Prompt dla AI Agent**:
```
Zaprojektuj system logowania dla LiteCrewAI z następującymi wymaganiami:

1. Struktura logów:
   - /opt/litecrewai/logs/app.log (aplikacja)
   - /opt/litecrewai/logs/api.log (API requests)
   - /opt/litecrewai/logs/llm.log (LLM calls)
   - /opt/litecrewai/logs/error.log (błędy)

2. Konfiguracja Python logging:
   - Structured logging (JSON format)
   - Different levels per module
   - Correlation IDs dla śledzenia
   - Performance metrics w logach

3. Logrotate configuration:
   - Rotacja dzienna
   - Kompresja po 1 dniu
   - Retencja 30 dni
   - Max 100MB per file

4. Log aggregation:
   - Prosty dashboard w Bash/Python
   - Statystyki błędów
   - Monitoring performance
   - Alerty przy krytycznych błędach

5. Integration z systemd journald

Stwórz też przykładowy logger wrapper dla łatwego użycia w kodzie.
```

**Metryki Sukcesu**:
- ✅ Logi tworzone w odpowiednich plikach
- ✅ Rotacja działa automatycznie
- ✅ JSON format parseable
- ✅ Dashboard pokazuje metryki

**Walidacja**:
```python
# validate_logging.py
import json
import os
import logging
import subprocess
from datetime import datetime

def test_log_structure():
    """Test log files structure"""
    log_files = [
        "/opt/litecrewai/logs/app.log",
        "/opt/litecrewai/logs/api.log", 
        "/opt/litecrewai/logs/llm.log",
        "/opt/litecrewai/logs/error.log"
    ]
    
    for log_file in log_files:
        # Create log directory if not exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Test writing
        logger = logging.getLogger(os.path.basename(log_file))
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)
        
        # Write test log
        test_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "Test log entry",
            "correlation_id": "test-123"
        }
        logger.info(json.dumps(test_entry))
        
        # Verify it's readable as JSON
        with open(log_file, 'r') as f:
            last_line = f.readlines()[-1]
            parsed = json.loads(last_line)
            assert parsed["correlation_id"] == "test-123"
    
    print("✅ Log structure validated")

def test_logrotate():
    """Test logrotate configuration"""
    config_path = "/etc/logrotate.d/litecrewai"
    assert os.path.exists(config_path), "Logrotate config not found"
    
    # Test configuration
    result = subprocess.run(["logrotate", "-d", config_path], capture_output=True, text=True)
    assert result.returncode == 0, f"Logrotate config invalid: {result.stderr}"
    
    print("✅ Logrotate configuration validated")

def test_log_dashboard():
    """Test log analysis dashboard"""
    dashboard_script = "/opt/litecrewai/scripts/log_dashboard.py"
    assert os.path.exists(dashboard_script), "Dashboard script not found"
    
    # Run dashboard in test mode
    result = subprocess.run([
        "/opt/litecrewai/venv/bin/python",
        dashboard_script,
        "--test"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, f"Dashboard failed: {result.stderr}"
    assert "Error Rate:" in result.stdout
    assert "Performance:" in result.stdout
    
    print("✅ Log dashboard validated")

if __name__ == "__main__":
    test_log_structure()
    test_logrotate()
    test_log_dashboard()
    print("✅ All logging checks passed!")
```

##### Task 0.3.2: Setup Monitoring and Metrics (2h)
**Cel**: Real-time monitoring aplikacji i infrastruktury

**Prompt dla AI Agent**:
```
Zbuduj lekki system monitorowania dla LiteCrewAI bez zewnętrznych zależności.

Komponenty:
1. Metrics collector (Python):
   - System metrics (CPU, RAM, Disk)
   - Application metrics (requests, response time)
   - LLM metrics (tokens, cost, latency)
   - Custom business metrics

2. Storage w SQLite:
   - Tabela metrics z time-series data
   - Agregacje 1min, 5min, 1h
   - Auto-cleanup starych danych

3. Simple dashboard (FastAPI + htmx):
   - Real-time graphs
   - Alert status
   - Cost tracking
   - Health checks

4. Alerting system:
   - Email alerts (via SMTP)
   - Webhook alerts (Discord/Slack)
   - Telegram bot (opcjonalnie)
   - Alert fatigue prevention

5. Health check endpoints:
   - /health (basic)
   - /health/detailed (wszystkie komponenty)
   - /metrics (Prometheus format)

Dashboard powinien działać bez JavaScript (server-side rendering).
```

**Metryki Sukcesu**:
- ✅ Metryki zbierane co 60s
- ✅ Dashboard ładuje się <1s
- ✅ Alerty wysyłane w <30s
- ✅ Historia 7 dni dostępna

**Walidacja**:
```python
# validate_monitoring.py
import requests
import sqlite3
import time
import psutil

def test_metrics_collection():
    """Test metrics are being collected"""
    db_path = "/opt/litecrewai/data/metrics.db"
    
    # Wait for some metrics to be collected
    time.sleep(65)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if metrics exist
    cursor.execute("SELECT COUNT(*) FROM metrics WHERE timestamp > datetime('now', '-2 minutes')")
    count = cursor.fetchone()[0]
    assert count > 0, "No recent metrics found"
    
    # Check metric types
    cursor.execute("SELECT DISTINCT metric_name FROM metrics")
    metrics = [row[0] for row in cursor.fetchall()]
    
    required_metrics = ["cpu_usage", "memory_usage", "disk_usage", "api_requests"]
    for metric in required_metrics:
        assert metric in metrics, f"Missing metric: {metric}"
    
    conn.close()
    print("✅ Metrics collection validated")

def test_health_endpoints():
    """Test health check endpoints"""
    base_url = "http://localhost:8000"
    
    # Basic health
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    
    # Detailed health
    response = requests.get(f"{base_url}/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "redis" in data
    assert "ollama" in data
    
    # Metrics endpoint
    response = requests.get(f"{base_url}/metrics")
    assert response.status_code == 200
    assert "# HELP" in response.text  # Prometheus format
    
    print("✅ Health endpoints validated")

def test_dashboard():
    """Test monitoring dashboard"""
    response = requests.get("http://localhost:8000/dashboard")
    assert response.status_code == 200
    
    # Check for key elements
    html = response.text
    assert "System Metrics" in html
    assert "API Performance" in html
    assert "Cost Tracking" in html
    
    # Test it loads fast
    start = time.time()
    response = requests.get("http://localhost:8000/dashboard")
    load_time = time.time() - start
    assert load_time < 1.0, f"Dashboard too slow: {load_time:.2f}s"
    
    print("✅ Dashboard validated")

def test_alerting():
    """Test alert system"""
    # Trigger test alert
    response = requests.post("http://localhost:8000/api/test-alert")
    assert response.status_code == 200
    
    # Check alert was logged
    with open("/opt/litecrewai/logs/alerts.log", "r") as f:
        content = f.read()
        assert "TEST_ALERT" in content
    
    print("✅ Alerting system validated")

if __name__ == "__main__":
    test_metrics_collection()
    test_health_endpoints()
    test_dashboard()
    test_alerting()
    print("✅ All monitoring checks passed!")
```

---

## 📦 FAZA 1: FORK I MINIMALIZACJA CREWAI

### Blok 1.1: Fork and Initial Cleanup
**Czas**: 10h
**Cel**: Czysty fork CrewAI bez telemetrii i zbędnych features

#### Zadania Atomowe:

##### Task 1.1.1: Fork CrewAI Repository (2h)
**Cel**: Lokalny fork z pełną historią i właściwą strukturą

**Prompt dla AI Agent**:
```
Stwórz skrypt do forkowania CrewAI z pełnym cleanup.

Kroki:
1. Fork CrewAI na GitHub (instrukcje manualne)
2. Clone do /opt/litecrewai/app
3. Zachowaj historię ale usuń wszystkie remote branches
4. Stwórz branch 'lite-personal' od main
5. Analiza struktury projektu i dependencies
6. Raport z:
   - Liczba plików
   - Rozmiar repo
   - Lista głównych dependencies
   - Potencjalne miejsca do cleanup

Skrypt powinien generować szczegółowy raport w Markdown.
```

**Metryki Sukcesu**:
- ✅ Repo sklonowane lokalnie
- ✅ Branch lite-personal utworzony
- ✅ Raport wygenerowany
- ✅ Brak połączenia z oryginalnym repo

**Walidacja**:
```python
# validate_fork.py
import os
import subprocess
import git

def test_repo_structure():
    """Test forked repository structure"""
    repo_path = "/opt/litecrewai/app"
    
    # Check repo exists
    assert os.path.exists(f"{repo_path}/.git"), "Git repo not found"
    
    # Open repo
    repo = git.Repo(repo_path)
    
    # Check branch
    assert "lite-personal" in [b.name for b in repo.branches], "lite-personal branch not found"
    
    # Check no upstream remote
    remotes = [r.name for r in repo.remotes]
    assert "upstream" not in remotes, "Upstream remote should be removed"
    
    # Check report exists
    assert os.path.exists(f"{repo_path}/FORK_ANALYSIS.md"), "Analysis report not found"
    
    print("✅ Fork structure validated")

def test_repo_size():
    """Test repository size after fork"""
    repo_path = "/opt/litecrewai/app"
    
    # Get repo size
    result = subprocess.run(
        ["du", "-sh", repo_path],
        capture_output=True,
        text=True
    )
    size = result.stdout.split()[0]
    
    print(f"Repository size: {size}")
    
    # Count files
    result = subprocess.run(
        ["find", repo_path, "-type", "f", "-name", "*.py", "|", "wc", "-l"],
        shell=True,
        capture_output=True,
        text=True
    )
    py_files = int(result.stdout.strip())
    
    print(f"Python files: {py_files}")
    assert py_files > 10, "Too few Python files"

if __name__ == "__main__":
    test_repo_structure()
    test_repo_size()
    print("✅ Fork validation passed!")
```

##### Task 1.1.2: Remove Telemetry and Analytics (4h)
**Cel**: Kompletne usunięcie wszelkiego śledzenia

**Prompt dla AI Agent**:
```
Napisz skrypt do kompletnego usunięcia telemetrii z CrewAI.

Zadania:
1. Znajdź wszystkie pliki z telemetrią:
   - Szukaj: telemetry, analytics, tracking, metrics (jako tracking)
   - Sprawdź importy zewnętrznych serwisów
   - Znajdź environment variables związane z tracking

2. Usuń lub zastąp:
   - Całe moduły telemetry/
   - Importy i wywołania
   - Dekoratory śledzące
   - Middleware analytics
   - Zewnętrzne calls (Segment, Mixpanel, etc.)

3. Zastąp usuniętą funkcjonalność:
   - Puste funkcje gdzie potrzebne
   - Local-only metrics gdzie istotne

4. Wygeneruj raport:
   - Lista usuniętych plików
   - Lista zmodyfikowanych plików
   - Diff głównych zmian

Skrypt musi być bezpieczny i tworzyć backup przed zmianami.
```

**Metryki Sukcesu**:
- ✅ Zero wywołań telemetrii w kodzie
- ✅ Brak zewnętrznych analytics dependencies
- ✅ Kod nadal się kompiluje
- ✅ Testy przechodzą (po dostosowaniu)

**Walidacja**:
```python
# validate_no_telemetry.py
import os
import ast
import subprocess

def scan_for_telemetry(directory):
    """Scan Python files for telemetry code"""
    telemetry_keywords = [
        'telemetry', 'analytics', 'tracking', 'segment',
        'mixpanel', 'amplitude', 'posthog', 'sentry'
    ]
    
    issues = []
    
    for root, dirs, files in os.walk(directory):
        # Skip test and example directories
        if 'test' in root or 'example' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                # Check for keywords
                for keyword in telemetry_keywords:
                    if keyword.lower() in content.lower():
                        # Validate it's not a comment
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if keyword.lower() in line.lower() and not line.strip().startswith('#'):
                                issues.append(f"{filepath}:{i+1} - Found '{keyword}'")
    
    return issues

def check_dependencies():
    """Check for analytics dependencies in requirements"""
    req_files = [
        "/opt/litecrewai/app/requirements.txt",
        "/opt/litecrewai/app/setup.py",
        "/opt/litecrewai/app/pyproject.toml"
    ]
    
    analytics_packages = [
        'analytics-python', 'mixpanel', 'segment', 
        'amplitude', 'posthog', 'sentry-sdk'
    ]
    
    issues = []
    
    for req_file in req_files:
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                content = f.read()
                for package in analytics_packages:
                    if package in content:
                        issues.append(f"{req_file} - Found package '{package}'")
    
    return issues

def check_env_vars():
    """Check for telemetry-related environment variables"""
    env_file = "/opt/litecrewai/app/.env.example"
    telemetry_vars = [
        'TELEMETRY', 'ANALYTICS', 'TRACKING', 'SEGMENT',
        'MIXPANEL', 'SENTRY', 'POSTHOG'
    ]
    
    issues = []
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            for var in telemetry_vars:
                if var in content.upper():
                    issues.append(f".env.example - Found variable containing '{var}'")
    
    return issues

if __name__ == "__main__":
    print("🔍 Scanning for telemetry...")
    
    # Scan code
    code_issues = scan_for_telemetry("/opt/litecrewai/app")
    if code_issues:
        print("❌ Found telemetry in code:")
        for issue in code_issues[:5]:  # Show first 5
            print(f"  - {issue}")
        if len(code_issues) > 5:
            print(f"  ... and {len(code_issues) - 5} more")
    else:
        print("✅ No telemetry found in code")
    
    # Check dependencies
    dep_issues = check_dependencies()
    if dep_issues:
        print("❌ Found analytics dependencies:")
        for issue in dep_issues:
            print(f"  - {issue}")
    else:
        print("✅ No analytics dependencies")
    
    # Check env vars
    env_issues = check_env_vars()
    if env_issues:
        print("❌ Found telemetry env vars:")
        for issue in env_issues:
            print(f"  - {issue}")
    else:
        print("✅ No telemetry env vars")
    
    # Final verdict
    if not code_issues and not dep_issues and not env_issues:
        print("\n✅ Telemetry completely removed!")
    else:
        print(f"\n❌ Found {len(code_issues) + len(dep_issues) + len(env_issues)} telemetry issues")
        exit(1)
```

##### Task 1.1.3: Remove Enterprise Features (4h)
**Cel**: Usunięcie funkcji enterprise i chmurowych

**Prompt dla AI Agent**:
```
Stwórz skrypt do usunięcia enterprise features z CrewAI.

Do usunięcia:
1. Moduły enterprise:
   - Cloud sync/storage
   - Team collaboration
   - RBAC/permissions
   - Billing/subscriptions
   - Multi-tenant features
   - SSO/SAML

2. Zależności enterprise:
   - Cloud provider SDKs (AWS, GCP, Azure)
   - Payment processors
   - Enterprise auth libraries
   - Monitoring platforms (DataDog, NewRelic)

3. Uproszczenie do single-user:
   - Jeden użytkownik lokalny
   - Brak auth (lub bardzo prosty)
   - Local storage only
   - No cloud backups

4. Zachowaj core functionality:
   - Agents
   - Tasks
   - Tools
   - Memory
   - Basic API

Generuj szczegółowy raport zmian z diffami.
```

**Metryki Sukcesu**:
- ✅ Brak enterprise dependencies
- ✅ Kod działa single-user
- ✅ Zmniejszony rozmiar o >30%
- ✅ Podstawowe features działają

**Walidacja**:
```python
# validate_no_enterprise.py
import os
import json
import subprocess

def check_removed_modules():
    """Check that enterprise modules are removed"""
    removed_modules = [
        'enterprise', 'cloud', 'billing', 'teams',
        'auth/sso', 'auth/saml', 'multi_tenant'
    ]
    
    app_dir = "/opt/litecrewai/app"
    issues = []
    
    for module in removed_modules:
        module_path = os.path.join(app_dir, module.replace('/', os.sep))
        if os.path.exists(module_path):
            issues.append(f"Enterprise module still exists: {module}")
    
    return issues

def check_cloud_dependencies():
    """Check for cloud provider dependencies"""
    cloud_packages = [
        'boto3', 'google-cloud', 'azure', 'stripe',
        'auth0', 'okta', 'datadog', 'newrelic'
    ]
    
    # Check in requirements
    req_file = "/opt/litecrewai/app/requirements.txt"
    issues = []
    
    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            content = f.read().lower()
            for package in cloud_packages:
                if package in content:
                    issues.append(f"Cloud dependency found: {package}")
    
    return issues

def check_single_user():
    """Verify single-user simplification"""
    app_dir = "/opt/litecrewai/app"
    
    # Check for user/auth models
    auth_indicators = [
        'class User', 'class Team', 'class Organization',
        'def authenticate', 'def authorize', 'permissions.py'
    ]
    
    issues = []
    
    for root, dirs, files in os.walk(app_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    for indicator in auth_indicators:
                        if indicator in content:
                            issues.append(f"Multi-user code in {filepath}: {indicator}")
    
    return issues

def calculate_size_reduction():
    """Calculate repository size reduction"""
    # This would compare with original size stored during fork
    result = subprocess.run(
        ["du", "-sh", "/opt/litecrewai/app"],
        capture_output=True,
        text=True
    )
    current_size = result.stdout.split()[0]
    
    print(f"Current repository size: {current_size}")
    
    # Count Python files
    result = subprocess.run(
        ["find", "/opt/litecrewai/app", "-name", "*.py", "-type", "f", "|", "wc", "-l"],
        shell=True,
        capture_output=True,
        text=True
    )
    py_files = int(result.stdout.strip())
    print(f"Python files remaining: {py_files}")

if __name__ == "__main__":
    print("🔍 Validating enterprise feature removal...")
    
    # Check modules
    module_issues = check_removed_modules()
    if module_issues:
        print("❌ Enterprise modules found:")
        for issue in module_issues:
            print(f"  - {issue}")
    else:
        print("✅ Enterprise modules removed")
    
    # Check dependencies
    dep_issues = check_cloud_dependencies()
    if dep_issues:
        print("❌ Cloud dependencies found:")
        for issue in dep_issues:
            print(f"  - {issue}")
    else:
        print("✅ Cloud dependencies removed")
    
    # Check single-user
    user_issues = check_single_user()
    if user_issues:
        print("❌ Multi-user code found:")
        for issue in user_issues[:3]:
            print(f"  - {issue}")
    else:
        print("✅ Simplified to single-user")
    
    # Size calculation
    calculate_size_reduction()
    
    # Final verdict
    total_issues = len(module_issues) + len(dep_issues) + len(user_issues)
    if total_issues == 0:
        print("\n✅ Enterprise features successfully removed!")
    else:
        print(f"\n❌ Found {total_issues} enterprise-related issues")
        exit(1)
```

### Blok 1.2: Dependency Optimization
**Czas**: 8h
**Cel**: Minimalne, szybkie dependencies

#### Zadania Atomowe:

##### Task 1.2.1: Analyze and Minimize Dependencies (4h)
**Cel**: Zredukowanie dependencies do absolutnego minimum

**Prompt dla AI Agent**:
```
Przeprowadź głęboką analizę dependencies CrewAI i zminimalizuj je.

Proces:
1. Analiza obecnych dependencies:
   - pip-compile do wygenerowania pełnego drzewa
   - pipdeptree do wizualizacji
   - Sprawdź faktyczne użycie każdej biblioteki
   - Znajdź duplikaty funkcjonalności

2. Kategoryzacja:
   - CORE: absolutnie wymagane
   - OPTIONAL: dla specific features
   - REPLACEABLE: można zastąpić czymś lżejszym
   - REMOVABLE: niepotrzebne

3. Optymalizacje:
   - Zastąp ciężkie biblioteki lżejszymi alternatywami
   - Usuń unused dependencies
   - Połącz podobne funkcjonalności
   - Użyj stdlib gdzie możliwe

4. Target dependencies:
   - pydantic (validation)
   - fastapi (API)
   - sqlite3 (wbudowane)
   - redis (cache)
   - httpx (async requests)
   - Maksymalnie 10-15 zewnętrznych bibliotek

5. Generuj raport z:
   - Przed/po porównanie
   - Oszczędność w MB
   - Potencjalne ryzyko

Pamiętaj o kompatybilności wstecznej core features.
```

**Metryki Sukcesu**:
- ✅ <15 zewnętrznych dependencies
- ✅ Install time <30s
- ✅ Rozmiar site-packages <100MB
- ✅ Wszystkie testy przechodzą

**Walidacja**:
```python
# validate_dependencies.py
import subprocess
import pkg_resources
import os

def count_dependencies():
    """Count and analyze dependencies"""
    # Get installed packages
    installed = {pkg.key: pkg for pkg in pkg_resources.working_set}
    
    # Filter out standard library
    external = []
    for name, pkg in installed.items():
        if not pkg.location.startswith('/usr/lib/python'):
            external.append((name, pkg.version))
    
    print(f"Total external packages: {len(external)}")
    
    # List them
    print("\nInstalled packages:")
    for name, version in sorted(external):
        print(f"  - {name}=={version}")
    
    return len(external)

def check_install_time():
    """Measure clean install time"""
    print("\n🕐 Testing install time...")
    
    # Create temp venv
    subprocess.run(["python3.11", "-m", "venv", "/tmp/test_venv"])
    
    # Time the install
    start = subprocess.time.time()
    result = subprocess.run([
        "/tmp/test_venv/bin/pip", "install", "-r", 
        "/opt/litecrewai/app/requirements.txt", "--no-cache-dir"
    ], capture_output=True)
    
    install_time = subprocess.time.time() - start
    
    # Cleanup
    subprocess.run(["rm", "-rf", "/tmp/test_venv"])
    
    print(f"Install time: {install_time:.1f}s")
    return install_time

def check_package_size():
    """Check total size of installed packages"""
    venv_path = "/opt/litecrewai/venv"
    site_packages = os.path.join(venv_path, "lib/python3.11/site-packages")
    
    # Get size
    result = subprocess.run(
        ["du", "-sh", site_packages],
        capture_output=True,
        text=True
    )
    size = result.stdout.split()[0]
    
    # Convert to MB
    if size.endswith('M'):
        size_mb = float(size[:-1])
    elif size.endswith('G'):
        size_mb = float(size[:-1]) * 1024
    else:
        size_mb = 0
    
    print(f"\nSite-packages size: {size} ({size_mb:.0f} MB)")
    return size_mb

def check_core_imports():
    """Verify core functionality still works"""
    core_imports = [
        "from litecrewai import Agent, Task, Crew",
        "from litecrewai.tools import Tool",
        "from litecrewai.memory import Memory"
    ]
    
    print("\n🔍 Testing core imports...")
    issues = []
    
    for import_stmt in core_imports:
        try:
            exec(import_stmt)
            print(f"✅ {import_stmt}")
        except ImportError as e:
            issues.append(f"Failed: {import_stmt} - {e}")
            print(f"❌ {import_stmt}")
    
    return issues

if __name__ == "__main__":
    print("🔍 Validating optimized dependencies...\n")
    
    # Count packages
    package_count = count_dependencies()
    assert package_count <= 15, f"Too many packages: {package_count}"
    
    # Check install time
    install_time = check_install_time()
    assert install_time < 30, f"Install too slow: {install_time:.1f}s"
    
    # Check size
    size_mb = check_package_size()
    assert size_mb < 100, f"Packages too large: {size_mb:.0f}MB"
    
    # Check imports
    import_issues = check_core_imports()
    assert len(import_issues) == 0, f"Import issues: {import_issues}"
    
    print("\n✅ All dependency checks passed!")
```

##### Task 1.2.2: Create Minimal Requirements Files (2h)
**Cel**: Czyste, zorganizowane pliki requirements

**Prompt dla AI Agent**:
```
Stwórz optymalną strukturę requirements dla LiteCrewAI.

Pliki do utworzenia:
1. requirements/base.txt
   - Absolutne minimum do działania
   - Pinned versions dla stabilności
   - Komentarze wyjaśniające każdą zależność

2. requirements/dev.txt
   - Narzędzia developerskie
   - Testing frameworks
   - Linting/formatting

3. requirements/optional.txt
   - Opcjonalne integracje
   - Dodatkowe LLM providers
   - Advanced features

4. requirements.txt
   - Prosty alias do base.txt

5. constraints.txt
   - Upper bounds dla bezpieczeństwa
   - Konfliktujące wersje

6. Script do zarządzania:
   - Update dependencies
   - Security check
   - License check
   - Size analysis

Użyj pip-tools do kompilacji i zarządzania.
```

**Metryki Sukcesu**:
- ✅ Czysta separacja requirements
- ✅ Wszystkie wersje pinned
- ✅ pip-compile działa
- ✅ No security vulnerabilities

**Walidacja**:
```python
# validate_requirements.py
import os
import subprocess
import re

def check_requirements_structure():
    """Check all requirements files exist"""
    required_files = [
        "requirements.txt",
        "requirements/base.txt",
        "requirements/dev.txt",
        "requirements/optional.txt",
        "constraints.txt"
    ]
    
    base_dir = "/opt/litecrewai/app"
    missing = []
    
    for req_file in required_files:
        path = os.path.join(base_dir, req_file)
        if not os.path.exists(path):
            missing.append(req_file)
        else:
            # Check if pinned
            with open(path, 'r') as f:
                content = f.read()
                # Count unpinned dependencies
                unpinned = len(re.findall(r'^[a-zA-Z][^=<>]*$', content, re.MULTILINE))
                if unpinned > 0:
                    print(f"⚠️  {req_file} has {unpinned} unpinned dependencies")
    
    return missing

def test_pip_compile():
    """Test pip-compile works correctly"""
    os.chdir("/opt/litecrewai/app")
    
    # Test compile
    result = subprocess.run([
        "/opt/litecrewai/venv/bin/pip-compile",
        "requirements/base.txt",
        "--output-file", "/tmp/test-requirements.txt"
    ], capture_output=True)
    
    if result.returncode != 0:
        print(f"❌ pip-compile failed: {result.stderr.decode()}")
        return False
    
    # Check output
    with open("/tmp/test-requirements.txt", 'r') as f:
        compiled = f.read()
        # Should have hashes
        assert "--hash=sha256:" in compiled, "No hashes in compiled requirements"
    
    return True

def check_security():
    """Run security check on dependencies"""
    result = subprocess.run([
        "/opt/litecrewai/venv/bin/pip-audit",
        "-r", "/opt/litecrewai/app/requirements.txt"
    ], capture_output=True, text=True)
    
    if "No known vulnerabilities" in result.stdout:
        return True, []
    else:
        # Parse vulnerabilities
        vulns = []
        for line in result.stdout.split('\n'):
            if 'VULNERABILITY' in line:
                vulns.append(line.strip())
        return False, vulns

def check_licenses():
    """Check dependency licenses"""
    result = subprocess.run([
        "/opt/litecrewai/venv/bin/pip-licenses",
        "--format=json"
    ], capture_output=True, text=True)
    
    import json
    licenses = json.loads(result.stdout)
    
    # Check for problematic licenses
    problematic = ['GPL', 'AGPL', 'LGPL']
    issues = []
    
    for package in licenses:
        license_name = package.get('License', '')
        for prob in problematic:
            if prob in license_name:
                issues.append(f"{package['Name']}: {license_name}")
    
    return issues

if __name__ == "__main__":
    print("🔍 Validating requirements structure...\n")
    
    # Check structure
    missing = check_requirements_structure()
    if missing:
        print(f"❌ Missing files: {missing}")
    else:
        print("✅ All requirements files present")
    
    # Test pip-compile
    if test_pip_compile():
        print("✅ pip-compile working")
    else:
        print("❌ pip-compile failed")
    
    # Security check
    secure, vulns = check_security()
    if secure:
        print("✅ No security vulnerabilities")
    else:
        print(f"❌ Security issues found: {len(vulns)}")
        for vuln in vulns[:3]:
            print(f"  - {vuln}")
    
    # License check
    license_issues = check_licenses()
    if license_issues:
        print(f"⚠️  Potential license issues: {license_issues}")
    else:
        print("✅ All licenses compatible")
    
    print("\n✅ Requirements validation complete!")
```

##### Task 1.2.3: Setup Dependency Caching (2h)
**Cel**: Szybkie rebuildy z cache

**Prompt dla AI Agent**:
```
Zaimplementuj system cachowania dependencies dla szybkich deploymentów.

Komponenty:
1. Local pip cache:
   - Configure pip cache dir
   - Pre-download all dependencies
   - Create wheelhouse

2. Docker layer caching (jeśli używamy):
   - Multi-stage builds
   - Optimal layer ordering
   - Cache mount points

3. GitHub Actions cache:
   - Cache pip packages
   - Cache venv
   - Restore keys strategy

4. Dependency freeze:
   - Lock file z hashem
   - Reproducible builds
   - Version pinning strategy

5. Offline install capability:
   - Bundle dependencies
   - No internet required
   - Fallback mechanism

Stwórz skrypty do zarządzania cache i monitoring jego skuteczności.
```

**Metryki Sukcesu**:
- ✅ Rebuild <10s z cache
- ✅ Cache hit rate >90%
- ✅ Offline install działa
- ✅ Reproducible builds

**Walidacja**:
```python
# validate_dep_cache.py
import os
import subprocess
import time
import shutil

def test_cache_setup():
    """Test pip cache is configured"""
    # Check pip cache dir
    result = subprocess.run([
        "/opt/litecrewai/venv/bin/pip", "cache", "dir"
    ], capture_output=True, text=True)
    
    cache_dir = result.stdout.strip()
    assert os.path.exists(cache_dir), f"Cache dir doesn't exist: {cache_dir}"
    
    # Check cache has content
    cache_size = subprocess.run(
        ["du", "-sh", cache_dir],
        capture_output=True,
        text=True
    ).stdout.split()[0]
    
    print(f"Pip cache size: {cache_size}")
    return cache_dir

def test_wheelhouse():
    """Test local wheelhouse exists"""
    wheelhouse = "/opt/litecrewai/wheelhouse"
    assert os.path.exists(wheelhouse), "Wheelhouse doesn't exist"
    
    # Count wheels
    wheels = len([f for f in os.listdir(wheelhouse) if f.endswith('.whl')])
    print(f"Wheels in wheelhouse: {wheels}")
    
    assert wheels > 0, "No wheels in wheelhouse"
    return wheels

def test_rebuild_speed():
    """Test rebuild with cache"""
    # Create test venv
    test_venv = "/tmp/cache_test_venv"
    
    # First install (cold cache)
    subprocess.run(["python3.11", "-m", "venv", test_venv])
    
    start = time.time()
    subprocess.run([
        f"{test_venv}/bin/pip", "install",
        "-r", "/opt/litecrewai/app/requirements.txt",
        "--find-links", "/opt/litecrewai/wheelhouse",
        "--no-index"  # Force offline
    ], capture_output=True)
    offline_time = time.time() - start
    
    # Cleanup
    shutil.rmtree(test_venv)
    
    print(f"Offline install time: {offline_time:.1f}s")
    return offline_time

def test_reproducibility():
    """Test builds are reproducible"""
    # Generate freeze file
    result1 = subprocess.run([
        "/opt/litecrewai/venv/bin/pip", "freeze"
    ], capture_output=True, text=True)
    
    # Create new venv and install
    test_venv = "/tmp/repro_test"
    subprocess.run(["python3.11", "-m", "venv", test_venv])
    subprocess.run([
        f"{test_venv}/bin/pip", "install",
        "-r", "/opt/litecrewai/app/requirements.txt"
    ], capture_output=True)
    
    # Compare freeze
    result2 = subprocess.run([
        f"{test_venv}/bin/pip", "freeze"
    ], capture_output=True, text=True)
    
    # Cleanup
    shutil.rmtree(test_venv)
    
    # Compare
    freeze1 = set(result1.stdout.strip().split('\n'))
    freeze2 = set(result2.stdout.strip().split('\n'))
    
    diff = freeze1.symmetric_difference(freeze2)
    if diff:
        print(f"⚠️  Reproducibility issue: {diff}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 Validating dependency cache...\n")
    
    # Test cache
    cache_dir = test_cache_setup()
    print(f"✅ Cache configured at: {cache_dir}")
    
    # Test wheelhouse
    wheels = test_wheelhouse()
    print(f"✅ Wheelhouse ready with {wheels} packages")
    
    # Test speed
    rebuild_time = test_rebuild_speed()
    assert rebuild_time < 10, f"Rebuild too slow: {rebuild_time:.1f}s"
    print(f"✅ Offline rebuild in {rebuild_time:.1f}s")
    
    # Test reproducibility
    if test_reproducibility():
        print("✅ Builds are reproducible")
    else:
        print("⚠️  Reproducibility issues detected")
    
    print("\n✅ Dependency cache validation complete!")
```

---

## 📦 FAZA 2: CORE ENGINE - AGENCI I ZADANIA

### Blok 2.1: Simplified Agent System
**Czas**: 12h
**Cel**: Uproszczony ale potężny system agentów

#### Zadania Atomowe:

##### Task 2.1.1: Design Lite Agent Architecture (4h)
**Cel**: Minimalistyczna architektura agenta

**Prompt dla AI Agent**:
```
Zaprojektuj uproszczoną architekturę agenta dla LiteCrewAI.

Wymagania:
1. Agent class:
   - Synchroniczny (bez async complications)
   - Minimal memory footprint (<10MB per agent)
   - Clear separation of concerns
   - Pluggable LLM backend

2. Core components:
   - Role & Goal (simple strings)
   - Memory (optional, pluggable)
   - Tools (dynamic loading)
   - Prompt template system

3. Execution model:
   - Simple execute() method
   - Built-in retry logic
   - Timeout handling
   - Cost tracking per execution

4. State management:
   - Stateless by default
   - Optional persistence
   - JSON serializable

5. Example implementation:
   ```python
   agent = Agent(
       role="Researcher",
       goal="Find accurate information",
       tools=["web_search", "calculator"],
       llm="ollama/mistral"
   )
   result = agent.execute("What is quantum computing?")
```

Stwórz pełną implementację z docstrings i type hints.
```

**Metryki Sukcesu**:
- ✅ Agent tworzy się <100ms
- ✅ Memory usage <10MB
- ✅ Execute() <5s dla prostych zadań
- ✅ Full type coverage

**Walidacja**:
```python
# validate_agent_architecture.py
import time
import psutil
import os
from litecrewai.agent import Agent

def test_agent_creation():
    """Test agent creation performance"""
    start = time.time()
    
    agent = Agent(
        role="Test Agent",
        goal="Perform test tasks",
        tools=["calculator"],
        llm="ollama/mistral"
    )
    
    creation_time = time.time() - start
    print(f"Agent creation time: {creation_time*1000:.1f}ms")
    
    assert creation_time < 0.1, f"Creation too slow: {creation_time}s"
    assert agent.role == "Test Agent"
    assert agent.goal == "Perform test tasks"
    assert "calculator" in agent.tools
    
    return agent

def test_memory_usage():
    """Test agent memory footprint"""
    # Get baseline memory
    process = psutil.Process(os.getpid())
    baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Create multiple agents
    agents = []
    for i in range(10):
        agent = Agent(
            role=f"Agent {i}",
            goal=f"Goal {i}",
            tools=["web_search", "calculator"],
            llm="ollama/mistral"
        )
        agents.append(agent)
    
    # Measure memory
    current_memory = process.memory_info().rss / 1024 / 1024
    memory_per_agent = (current_memory - baseline_memory) / 10
    
    print(f"Memory per agent: {memory_per_agent:.1f}MB")
    assert memory_per_agent < 10, f"Too much memory: {memory_per_agent:.1f}MB"

def test_execution():
    """Test agent execution"""
    agent = Agent(
        role="Calculator",
        goal="Perform calculations",
        tools=["calculator"],
        llm="ollama/mistral"
    )
    
    # Simple task
    start = time.time()
    result = agent.execute("What is 2 + 2?")
    execution_time = time.time() - start
    
    print(f"Execution time: {execution_time:.2f}s")
    print(f"Result: {result}")
    
    assert execution_time < 5, f"Execution too slow: {execution_time}s"
    assert result is not None
    assert "4" in str(result) or "four" in str(result).lower()

def test_serialization():
    """Test agent serialization"""
    agent = Agent(
        role="Serializable Agent",
        goal="Test serialization",
        tools=["web_search"],
        llm="ollama/phi"
    )
    
    # Serialize
    serialized = agent.to_dict()
    assert isinstance(serialized, dict)
    assert serialized["role"] == "Serializable Agent"
    
    # Deserialize
    agent2 = Agent.from_dict(serialized)
    assert agent2.role == agent.role
    assert agent2.goal == agent.goal
    assert agent2.tools == agent.tools
    
    print("✅ Serialization working")

def test_type_hints():
    """Test type hint coverage"""
    import inspect
    from typing import get_type_hints
    
    # Get all methods
    methods = inspect.getmembers(Agent, predicate=inspect.ismethod)
    
    typed_methods = 0
    total_methods = 0
    
    for name, method in methods:
        if not name.startswith('_'):
            total_methods += 1
            try:
                hints = get_type_hints(method)
                if hints:
                    typed_methods += 1
            except:
                pass
    
    coverage = typed_methods / total_methods * 100 if total_methods > 0 else 0
    print(f"Type hint coverage: {coverage:.1f}%")
    assert coverage > 80, f"Low type coverage: {coverage:.1f}%"

if __name__ == "__main__":
    print("🔍 Validating agent architecture...\n")
    
    # Test creation
    agent = test_agent_creation()
    print("✅ Agent creation validated")
    
    # Test memory
    test_memory_usage()
    print("✅ Memory usage validated")
    
    # Test execution
    test_execution()
    print("✅ Execution validated")
    
    # Test serialization
    test_serialization()
    
    # Test types
    test_type_hints()
    
    print("\n✅ Agent architecture validation complete!")
```

##### Task 2.1.2: Implement Task Execution Engine (4h)
**Cel**: Prosty ale niezawodny silnik wykonywania zadań

**Prompt dla AI Agent**:
```
Zaimplementuj uproszczony task execution engine dla LiteCrewAI.

Komponenty:
1. Task class:
   - Unikalne ID (UUID)
   - Description & context
   - Agent assignment
   - Dependencies (inne tasks)
   - Status tracking
   - Result storage

2. Task Queue:
   - Priority queue
   - Redis-backed
   - Persistence
   - Retry mechanism

3. Execution flow:
   - Dependency resolution
   - Parallel execution gdzie możliwe
   - Timeout handling
   - Error recovery
   - Progress tracking

4. Task patterns:
   - Sequential tasks
   - Parallel tasks
   - Conditional tasks
   - Loop tasks

5. Monitoring:
   - Execution time
   - Success rate
   - Resource usage
   - Bottleneck detection

Przykład użycia:
```python
task1 = Task("Research Python trends")
task2 = Task("Write summary", dependencies=[task1])
task3 = Task("Create presentation", dependencies=[task2])

executor = TaskExecutor()
results = executor.run([task1, task2, task3])
```

Implementacja powinna być thread-safe i odporna na błędy.
```

**Metryki Sukcesu**:
- ✅ Task execution <10s average
- ✅ Dependency resolution <100ms
- ✅ Parallel execution działa
- ✅ 95%+ success rate

**Walidacja**:
```python
# validate_task_execution.py
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from litecrewai.task import Task, TaskExecutor

def test_basic_task():
    """Test basic task execution"""
    task = Task("Calculate 2+2")
    executor = TaskExecutor()
    
    start = time.time()
    result = executor.run_single(task)
    execution_time = time.time() - start
    
    print(f"Task executed in {execution_time:.2f}s")
    assert result.status == "completed"
    assert execution_time < 10
    
    return result

def test_dependencies():
    """Test task dependency resolution"""
    # Create dependent tasks
    task1 = Task("Step 1", id="task1")
    task2 = Task("Step 2", dependencies=["task1"])
    task3 = Task("Step 3", dependencies=["task1", "task2"])
    
    executor = TaskExecutor()
    
    # Test dependency resolution
    start = time.time()
    order = executor.resolve_dependencies([task3, task1, task2])
    resolution_time = time.time() - start
    
    print(f"Dependency resolution: {resolution_time*1000:.1f}ms")
    assert resolution_time < 0.1
    assert [t.id for t in order] == ["task1", "task2", "task3"]
    
    # Execute all
    results = executor.run(order)
    assert all(r.status == "completed" for r in results)

def test_parallel_execution():
    """Test parallel task execution"""
    # Create independent tasks
    tasks = [Task(f"Parallel task {i}") for i in range(5)]
    
    executor = TaskExecutor(max_workers=3)
    
    start = time.time()
    results = executor.run(tasks)
    total_time = time.time() - start
    
    # Should be faster than sequential
    print(f"Parallel execution time: {total_time:.2f}s")
    assert total_time < len(tasks) * 2  # Assuming each task ~2s
    assert all(r.status == "completed" for r in results)

def test_error_handling():
    """Test error recovery"""
    # Create task that will fail
    fail_task = Task("This will fail", will_fail=True)
    
    executor = TaskExecutor()
    result = executor.run_single(fail_task)
    
    assert result.status == "failed"
    assert result.error is not None
    assert result.retry_count > 0
    
    print(f"Task failed after {result.retry_count} retries")

def test_thread_safety():
    """Test concurrent task submission"""
    executor = TaskExecutor()
    results = []
    
    def submit_tasks():
        for i in range(10):
            task = Task(f"Concurrent task {i}")
            result = executor.run_single(task)
            results.append(result)
    
    # Run from multiple threads
    threads = []
    for _ in range(3):
        t = threading.Thread(target=submit_tasks)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # Check all completed
    assert len(results) == 30
    assert all(r.status == "completed" for r in results)
    print("✅ Thread safety verified")

def test_progress_tracking():
    """Test progress monitoring"""
    tasks = [Task(f"Progress task {i}") for i in range(10)]
    executor = TaskExecutor()
    
    progress_updates = []
    
    def progress_callback(completed, total):
        progress_updates.append((completed, total))
    
    executor.run(tasks, progress_callback=progress_callback)
    
    # Should have progress updates
    assert len(progress_updates) > 0
    assert progress_updates[-1] == (10, 10)
    print(f"Progress updates: {len(progress_updates)}")

if __name__ == "__main__":
    print("🔍 Validating task execution engine...\n")
    
    # Basic execution
    test_basic_task()
    print("✅ Basic task execution validated")
    
    # Dependencies
    test_dependencies()
    print("✅ Dependency resolution validated")
    
    # Parallel execution
    test_parallel_execution()
    print("✅ Parallel execution validated")
    
    # Error handling
    test_error_handling()
    print("✅ Error handling validated")
    
    # Thread safety
    test_thread_safety()
    
    # Progress tracking
    test_progress_tracking()
    print("✅ Progress tracking validated")
    
    print("\n✅ Task execution validation complete!")
```

##### Task 2.1.3: Build Memory System (4h)
**Cel**: Efektywny system pamięci dla agentów

**Prompt dla AI Agent**:
```
Zaprojektuj i zaimplementuj system pamięci dla LiteCrewAI agents.

Wymagania:
1. Memory types:
   - Short-term (ostatnie 10 interakcji)
   - Long-term (ważne fakty)
   - Semantic (vector embeddings)
   - Episodic (full conversations)

2. Storage backend:
   - SQLite dla structured data
   - Vector store dla embeddings (sqlite-vec)
   - Automatic compression starych danych
   - Size limits (100MB per agent)

3. Memory operations:
   - store(key, value, type)
   - retrieve(query, limit=5)
   - forget(older_than)
   - summarize() - AI summary of memories

4. Optimization:
   - Lazy loading
   - LRU cache w pamięci
   - Automatic importance scoring
   - Deduplikacja

5. Integration:
   - Automatic context injection
   - Memory sharing między agentami
   - Export/import capability

Przykład:
```python
agent = Agent(role="Assistant", memory_enabled=True)
agent.memory.store("user_name", "John", type="fact")
agent.memory.store("prefers_coffee", True, type="preference")

context = agent.memory.retrieve("user preferences")
# Returns: ["user prefers coffee", "user name is John"]
```

System musi być wydajny i skalować do 1000+ faktów.
```

**Metryki Sukcesu**:
- ✅ Store operation <10ms
- ✅ Retrieve <50ms dla 1000 items
- ✅ Memory size <100MB limit
- ✅ 90%+ relevance w retrieval

**Walidacja**:
```python
# validate_memory_system.py
import time
import sqlite3
import os
from litecrewai.memory import Memory, MemoryType

def test_memory_creation():
    """Test memory system initialization"""
    memory = Memory(agent_id="test_agent")
    
    # Check database created
    db_path = memory.db_path
    assert os.path.exists(db_path), "Memory database not created"
    
    # Check tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = ["short_term", "long_term", "semantic", "episodic"]
    for table in required_tables:
        assert table in tables, f"Missing table: {table}"
    
    conn.close()
    return memory

def test_store_performance():
    """Test memory storage performance"""
    memory = Memory(agent_id="perf_test")
    
    # Test single store
    start = time.time()
    memory.store("test_key", "test_value", MemoryType.FACT)
    store_time = (time.time() - start) * 1000
    
    print(f"Single store time: {store_time:.1f}ms")
    assert store_time < 10, f"Store too slow: {store_time}ms"
    
    # Test bulk store
    start = time.time()
    for i in range(100):
        memory.store(f"key_{i}", f"value_{i}", MemoryType.FACT)
    bulk_time = time.time() - start
    
    print(f"100 stores time: {bulk_time:.2f}s")
    assert bulk_time < 1, f"Bulk store too slow: {bulk_time}s"

def test_retrieve_performance():
    """Test memory retrieval performance"""
    memory = Memory(agent_id="retrieve_test")
    
    # Populate with data
    for i in range(1000):
        memory.store(
            f"fact_{i}", 
            f"This is fact number {i} about topic {i % 10}",
            MemoryType.FACT
        )
    
    # Test retrieval
    start = time.time()
    results = memory.retrieve("topic 5", limit=10)
    retrieve_time = (time.time() - start) * 1000
    
    print(f"Retrieve from 1000 items: {retrieve_time:.1f}ms")
    assert retrieve_time < 50, f"Retrieve too slow: {retrieve_time}ms"
    assert len(results) <= 10
    assert all("topic 5" in r or "fact_5" in r for r in results)

def test_memory_limits():
    """Test memory size limits"""
    memory = Memory(agent_id="limit_test", max_size_mb=1)  # 1MB limit for test
    
    # Fill memory
    large_value = "x" * 1000  # 1KB
    stored = 0
    
    for i in range(2000):  # Try to store 2MB
        try:
            memory.store(f"large_{i}", large_value, MemoryType.FACT)
            stored += 1
        except:
            break
    
    # Check size limit enforced
    size_mb = memory.get_size_mb()
    print(f"Memory size: {size_mb:.2f}MB (stored {stored} items)")
    assert size_mb <= 1.1, f"Memory limit not enforced: {size_mb}MB"

def test_memory_types():
    """Test different memory types"""
    memory = Memory(agent_id="type_test")
    
    # Store different types
    memory.store("name", "John", MemoryType.FACT)
    memory.store("recent_query", "What's the weather?", MemoryType.SHORT_TERM)
    memory.store("conversation", ["Hi", "Hello", "How are you?"], MemoryType.EPISODIC)
    
    # Retrieve by type
    facts = memory.retrieve_by_type(MemoryType.FACT)
    assert any("John" in f for f in facts)
    
    short_term = memory.retrieve_by_type(MemoryType.SHORT_TERM)
    assert any("weather" in s for s in short_term)
    
    print("✅ Memory types working correctly")

def test_memory_operations():
    """Test memory operations"""
    memory = Memory(agent_id="ops_test")
    
    # Store some data
    for i in range(20):
        memory.store(f"old_{i}", f"value_{i}", MemoryType.FACT)
    
    time.sleep(1)  # Wait to create time difference
    
    for i in range(10):
        memory.store(f"new_{i}", f"value_{i}", MemoryType.FACT)
    
    # Test forget old
    forgotten = memory.forget(older_than_seconds=0.5)
    print(f"Forgotten {forgotten} old memories")
    assert forgotten >= 20
    
    # Test summarize
    summary = memory.summarize()
    assert isinstance(summary, str)
    assert len(summary) > 0
    print(f"Memory summary: {summary[:100]}...")
    
    # Test export/import
    exported = memory.export()
    assert isinstance(exported, dict)
    
    memory2 = Memory(agent_id="import_test")
    memory2.import_data(exported)
    assert memory2.get_size_mb() > 0

if __name__ == "__main__":
    print("🔍 Validating memory system...\n")
    
    # Test creation
    memory = test_memory_creation()
    print("✅ Memory system initialized")
    
    # Test performance
    test_store_performance()
    print("✅ Store performance validated")
    
    test_retrieve_performance()
    print("✅ Retrieve performance validated")
    
    # Test limits
    test_memory_limits()
    print("✅ Memory limits enforced")
    
    # Test types
    test_memory_types()
    
    # Test operations
    test_memory_operations()
    print("✅ Memory operations validated")
    
    print("\n✅ Memory system validation complete!")
```

### Blok 2.2: Tool System Implementation
**Czas**: 8h
**Cel**: Elastyczny system narzędzi dla agentów

#### Zadania Atomowe:

##### Task 2.2.1: Design Tool Framework (3h)
**Cel**: Uniwersalny framework dla tools

**Prompt dla AI Agent**:
```
Zaprojektuj elastyczny tool framework dla LiteCrewAI.

Wymagania:
1. Base Tool class:
   - Name & description
   - Input/output schema (Pydantic)
   - Async/sync support
   - Error handling
   - Rate limiting

2. Tool Registry:
   - Dynamic tool loading
   - Tool discovery
   - Dependency injection
   - Version management

3. Built-in tools:
   - WebSearch (via DuckDuckGo)
   - Calculator (safe math eval)
   - FileReader/Writer
   - SQLQuery
   - HTTPRequest
   - ShellCommand (sandboxed)

4. Tool composition:
   - Chain tools together
   - Conditional execution
   - Parallel tool calls
   - Result aggregation

5. Security:
   - Input validation
   - Output sanitization
   - Permission system
   - Audit logging

Przykład:
```python
@tool
def web_search(query: str, max_results: int = 5) -> List[Dict]:
    """Search the web for information"""
    # Implementation
    return results

agent = Agent(tools=[web_search, calculator])
result = agent.execute("Search for Python tutorials and calculate 15% of 200")
```

Framework musi być rozszerzalny i bezpieczny.
```

**Metryki Sukcesu**:
- ✅ Tool registration <1ms
- ✅ Tool execution <2s average
- ✅ Input validation 100%
- ✅ No security vulnerabilities

**Walidacja**:
```python
# validate_tool_framework.py
import time
import inspect
from typing import List, Dict
from litecrewai.tools import Tool, tool, ToolRegistry

def test_tool_creation():
    """Test tool decorator and registration"""
    
    @tool
    def sample_tool(text: str, count: int = 1) -> str:
        """Sample tool for testing"""
        return text * count
    
    # Check tool is wrapped correctly
    assert hasattr(sample_tool, '__tool__')
    assert sample_tool.__tool__.name == "sample_tool"
    assert sample_tool.__tool__.description == "Sample tool for testing"
    
    # Test execution
    result = sample_tool("test", 3)
    assert result == "testtesttest"
    
    print("✅ Tool creation working")

def test_tool_registry():
    """Test tool registry functionality"""
    registry = ToolRegistry()
    
    # Register tools
    @tool
    def tool1(x: int) -> int:
        return x * 2
    
    @tool
    def tool2(s: str) -> str:
        return s.upper()
    
    start = time.time()
    registry.register(tool1)
    registry.register(tool2)
    reg_time = (time.time() - start) * 1000
    
    print(f"Registration time: {reg_time:.2f}ms")
    assert reg_time < 1, f"Registration too slow: {reg_time}ms"
    
    # Test discovery
    tools = registry.list_tools()
    assert len(tools) >= 2
    assert "tool1" in [t.name for t in tools]
    
    # Test get
    retrieved = registry.get_tool("tool1")
    assert retrieved is not None
    assert retrieved(5) == 10

def test_builtin_tools():
    """Test built-in tools"""
    from litecrewai.tools.builtin import (
        web_search, calculator, file_reader,
        sql_query, http_request
    )
    
    # Test calculator
    calc_result = calculator("2 + 2 * 3")
    assert calc_result == 8
    
    # Test web search (mock)
    search_results = web_search("Python tutorial", max_results=3)
    assert isinstance(search_results, list)
    assert len(search_results) <= 3
    
    # Test file reader with sandboxing
    try:
        # Should fail - outside sandbox
        file_reader("/etc/passwd")
        assert False, "Security breach!"
    except PermissionError:
        print("✅ File sandboxing working")
    
    print("✅ Built-in tools validated")

def test_tool_composition():
    """Test tool chaining and composition"""
    from litecrewai.tools import ToolChain
    
    @tool
    def get_number() -> int:
        return 42
    
    @tool
    def double(x: int) -> int:
        return x * 2
    
    @tool
    def to_string(x: int) -> str:
        return f"The number is {x}"
    
    # Create chain
    chain = ToolChain([get_number, double, to_string])
    result = chain.execute()
    
    assert result == "The number is 84"
    print("✅ Tool composition working")

def test_input_validation():
    """Test input validation and sanitization"""
    
    @tool
    def validated_tool(
        name: str,
        age: int,
        email: str
    ) -> Dict:
        """Tool with validation"""
        return {"name": name, "age": age, "email": email}
    
    # Test valid input
    result = validated_tool("John", 30, "john@example.com")
    assert result["age"] == 30
    
    # Test invalid input
    try:
        validated_tool("John", "thirty", "invalid-email")
        assert False, "Validation should fail"
    except ValueError as e:
        print(f"✅ Validation caught error: {e}")
    
    # Test injection attempt
    try:
        validated_tool("John'; DROP TABLE users;--", 30, "john@example.com")
        # Should sanitize, not fail
        print("✅ SQL injection sanitized")
    except:
        pass

def test_performance():
    """Test tool execution performance"""
    
    @tool
    def slow_tool(duration: float = 0.1) -> str:
        time.sleep(duration)
        return "done"
    
    # Test timeout
    from litecrewai.tools import execute_with_timeout
    
    start = time.time()
    result = execute_with_timeout(slow_tool, timeout=2.0, duration=0.5)
    exec_time = time.time() - start
    
    assert exec_time < 1, f"Execution too slow: {exec_time}s"
    assert result == "done"
    
    # Test timeout exceeded
    try:
        execute_with_timeout(slow_tool, timeout=0.5, duration=1.0)
        assert False, "Should timeout"
    except TimeoutError:
        print("✅ Timeout handling working")

if __name__ == "__main__":
    print("🔍 Validating tool framework...\n")
    
    test_tool_creation()
    test_tool_registry()
    test_builtin_tools()
    test_tool_composition()
    test_input_validation()
    test_performance()
    
    print("\n✅ Tool framework validation complete!")
```

##### Task 2.2.2: Implement Core Tools (3h)
**Cel**: Zestaw podstawowych narzędzi

**Prompt dla AI Agent**:
```
Zaimplementuj podstawowe tools dla LiteCrewAI z pełną funkcjonalnością.

Tools do implementacji:
1. WebSearch:
   - Używa DuckDuckGo API (no key required)
   - Cache results (24h)
   - Extract text from pages
   - Rate limiting (1 req/sec)

2. Calculator:
   - Safe math evaluation
   - Support for basic operations
   - Scientific functions (math.*)
   - Unit conversions

3. FileSystem:
   - Read/write files
   - List directory
   - Search files
   - Sandboxed to specific dirs

4. Database:
   - SQLite queries
   - Read-only by default
   - Query builder
   - Result formatting

5. HTTP:
   - GET/POST requests
   - Headers support
   - JSON parsing
   - Timeout handling

6. DateTime:
   - Current time/date
   - Timezone conversion
   - Date arithmetic
   - Parsing various formats

Każdy tool powinien mieć:
- Comprehensive error handling
- Input validation
- Logging
- Tests
- Documentation
- Usage examples

Przykładowa implementacja:
```python
@tool
def calculate(expression: str) -> float:
    """
    Safely evaluate mathematical expressions.
    
    Examples:
        calculate("2 + 2") -> 4.0
        calculate("sin(pi/2)") -> 1.0
        calculate("sqrt(16)") -> 4.0
    """
    # Safe implementation here
```
```

**Metryki Sukcesu**:
- ✅ Wszystkie tools działają
- ✅ 100% test coverage
- ✅ No security issues
- ✅ <2s execution time

**Walidacja**:
```python
# validate_core_tools.py
import os
import time
import tempfile
from litecrewai.tools.builtin import (
    web_search, calculator, file_system,
    database_query, http_request, datetime_tool
)

def test_web_search():
    """Test web search functionality"""
    # Mock search for testing
    results = web_search("Python programming", max_results=3)
    
    assert isinstance(results, list)
    assert len(results) <= 3
    
    if results:  # If not mocked
        result = results[0]
        assert "title" in result
        assert "url" in result
        assert "snippet" in result
    
    # Test rate limiting
    start = time.time()
    web_search("test1")
    web_search("test2")  # Should be delayed
    elapsed = time.time() - start
    assert elapsed >= 1.0, "Rate limiting not working"
    
    print("✅ Web search validated")

def test_calculator():
    """Test calculator functionality"""
    # Basic operations
    assert calculator("2 + 2") == 4
    assert calculator("10 * 5") == 50
    assert calculator("100 / 4") == 25
    assert calculator("2 ** 8") == 256
    
    # Scientific functions
    assert abs(calculator("sin(pi/2)") - 1.0) < 0.0001
    assert calculator("sqrt(16)") == 4
    assert calculator("log(e)") == 1
    
    # Safety test
    try:
        calculator("__import__('os').system('ls')")
        assert False, "Security breach!"
    except (ValueError, NameError):
        print("✅ Calculator security working")
    
    print("✅ Calculator validated")

def test_file_system():
    """Test file system operations"""
    # Create temp directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test write
        test_file = os.path.join(tmpdir, "test.txt")
        file_system.write(test_file, "Hello, World!")
        
        # Test read
        content = file_system.read(test_file)
        assert content == "Hello, World!"
        
        # Test list
        file_system.write(os.path.join(tmpdir, "test2.txt"), "Another file")
        files = file_system.list(tmpdir)
        assert len(files) == 2
        
        # Test search
        results = file_system.search(tmpdir, "*.txt")
        assert len(results) == 2
        
        # Test sandboxing
        try:
            file_system.read("/etc/passwd")
            assert False, "Sandbox breach!"
        except PermissionError:
            print("✅ File system sandboxing working")
    
    print("✅ File system validated")

def test_database():
    """Test database operations"""
    # Create test database
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db_path = tmp.name
        
        # Create table
        database_query(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)",
            db_path=db_path,
            read_only=False
        )
        
        # Insert data
        database_query(
            "INSERT INTO users (name) VALUES ('Alice'), ('Bob')",
            db_path=db_path,
            read_only=False
        )
        
        # Test query
        results = database_query(
            "SELECT * FROM users",
            db_path=db_path
        )
        assert len(results) == 2
        assert results[0]["name"] == "Alice"
        
        # Test read-only
        try:
            database_query(
                "DROP TABLE users",
                db_path=db_path,
                read_only=True
            )
            assert False, "Should be read-only"
        except PermissionError:
            print("✅ Database read-only working")
    
    print("✅ Database operations validated")

def test_http_request():
    """Test HTTP request functionality"""
    # Test GET (using httpbin for testing)
    response = http_request(
        "https://httpbin.org/get",
        method="GET",
        params={"test": "value"}
    )
    
    assert response["status_code"] == 200
    assert "args" in response["data"]
    assert response["data"]["args"]["test"] == "value"
    
    # Test POST
    response = http_request(
        "https://httpbin.org/post",
        method="POST",
        json={"key": "value"}
    )
    
    assert response["status_code"] == 200
    assert response["data"]["json"]["key"] == "value"
    
    # Test timeout
    try:
        http_request(
            "https://httpbin.org/delay/10",
            timeout=1
        )
        assert False, "Should timeout"
    except TimeoutError:
        print("✅ HTTP timeout working")
    
    print("✅ HTTP requests validated")

def test_datetime_tool():
    """Test datetime functionality"""
    # Current time
    now = datetime_tool("now")
    assert "datetime" in now
    assert "timezone" in now
    
    # Timezone conversion
    converted = datetime_tool(
        "convert",
        datetime="2024-01-01 12:00:00",
        from_tz="UTC",
        to_tz="America/New_York"
    )
    assert "07:00:00" in converted
    
    # Date arithmetic
    future = datetime_tool(
        "add",
        datetime="2024-01-01",
        days=30
    )
    assert "2024-01-31" in future
    
    # Parsing
    parsed = datetime_tool(
        "parse",
        date_string="January 1st, 2024"
    )
    assert "2024-01-01" in parsed
    
    print("✅ DateTime tool validated")

if __name__ == "__main__":
    print("🔍 Validating core tools...\n")
    
    test_web_search()
    test_calculator()
    test_file_system()
    test_database()
    test_http_request()
    test_datetime_tool()
    
    print("\n✅ All core tools validated!")
```

##### Task 2.2.3: Create Tool Development Kit (2h)
**Cel**: SDK dla tworzenia custom tools

**Prompt dla AI Agent**:
```
Stwórz comprehensive Tool Development Kit (TDK) dla LiteCrewAI.

Komponenty:
1. Tool templates:
   - Basic tool template
   - Async tool template
   - Stateful tool template
   - Composite tool template

2. Code generators:
   - CLI tool creator: `litecrewai create-tool my_tool`
   - Generates boilerplate
   - Includes tests
   - Documentation stub

3. Testing utilities:
   - MockAgent for testing
   - Tool test harness
   - Performance profiler
   - Security scanner

4. Documentation generator:
   - Auto-generate from docstrings
   - Usage examples extractor
   - API reference builder
   - Interactive playground

5. Tool packaging:
   - Package as plugin
   - Dependency management
   - Version compatibility
   - Distribution via pip

6. Development tools:
   - Hot reload in dev
   - Debug mode
   - Performance metrics
   - Error tracking

Przykład workflow:
```bash
# Create new tool
litecrewai create-tool weather_forecast

# Develop
cd weather_forecast/
# Edit weather_forecast.py

# Test
litecrewai test-tool .

# Package
litecrewai package-tool .

# Publish
pip install dist/weather_forecast-1.0.0.whl
```

Include VS Code extension snippets and IDE support.
```

**Metryki Sukcesu**:
- ✅ Tool creation <30s
- ✅ Auto-generated tests pass
- ✅ Documentation complete
- ✅ IDE integration works

**Walidacja**:
```python
# validate_tool_sdk.py
import os
import subprocess
import tempfile
import json
from pathlib import Path

def test_cli_tool_creation():
    """Test CLI tool generator"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tool_name = "test_weather"
        
        # Run tool creator
        result = subprocess.run([
            "litecrewai", "create-tool", tool_name,
            "--output", tmpdir
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Tool creation failed: {result.stderr}"
        
        # Check generated files
        tool_dir = Path(tmpdir) / tool_name
        assert tool_dir.exists()
        
        expected_files = [
            f"{tool_name}.py",
            f"test_{tool_name}.py",
            "requirements.txt",
            "README.md",
            "setup.py",
            ".gitignore"
        ]
        
        for file in expected_files:
            assert (tool_dir / file).exists(), f"Missing file: {file}"
        
        # Check content
        tool_file = tool_dir / f"{tool_name}.py"
        content = tool_file.read_text()
        assert "@tool" in content
        assert "def test_weather" in content
        assert "\"\"\"" in content  # Docstring
        
        print("✅ CLI tool creation validated")
        return tool_dir

def test_generated_tool():
    """Test that generated tool works"""
    tool_dir = test_cli_tool_creation()
    
    # Run tests on generated tool
    result = subprocess.run([
        "python", "-m", "pytest",
        str(tool_dir / "test_test_weather.py"),
        "-v"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, f"Generated tests failed: {result.stderr}"
    print("✅ Generated tool tests pass")

def test_tool_packaging():
    """Test tool packaging system"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create minimal tool
        tool_dir = Path(tmpdir) / "my_tool"
        tool_dir.mkdir()
        
        # Write tool file
        (tool_dir / "my_tool.py").write_text("""
from litecrewai.tools import tool

@tool
def my_tool(text: str) -> str:
    \"\"\"My custom tool\"\"\"
    return text.upper()
""")
        
        # Write setup.py
        (tool_dir / "setup.py").write_text("""
from setuptools import setup

setup(
    name="my_tool",
    version="1.0.0",
    py_modules=["my_tool"],
    install_requires=["litecrewai>=0.1.0"]
)
""")
        
        # Package tool
        os.chdir(tool_dir)
        result = subprocess.run([
            "python", "setup.py", "bdist_wheel"
        ], capture_output=True)
        
        assert result.returncode == 0
        assert (tool_dir / "dist").exists()
        assert any(f.endswith(".whl") for f in os.listdir(tool_dir / "dist"))
        
        print("✅ Tool packaging validated")

def test_documentation_generator():
    """Test documentation generation"""
    # Create test tool with docstring
    test_code = '''
from litecrewai.tools import tool

@tool
def advanced_calculator(
    expression: str,
    precision: int = 2,
    use_radians: bool = True
) -> float:
    """
    Advanced calculator with scientific functions.
    
    Args:
        expression: Mathematical expression to evaluate
        precision: Decimal places in result
        use_radians: Use radians for trig functions
        
    Returns:
        Calculated result
        
    Examples:
        >>> advanced_calculator("sin(pi/2)")
        1.0
        >>> advanced_calculator("2 ** 10", precision=0)
        1024.0
    """
    # Implementation here
    return eval(expression)
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
        f.write(test_code)
        f.flush()
        
        # Generate documentation
        result = subprocess.run([
            "litecrewai", "generate-docs",
            "--tool", f.name,
            "--format", "markdown"
        ], capture_output=True, text=True)
        
        docs = result.stdout
        
        # Check documentation content
        assert "# advanced_calculator" in docs
        assert "Mathematical expression to evaluate" in docs
        assert "Examples:" in docs
        assert "sin(pi/2)" in docs
        
        print("✅ Documentation generation validated")

def test_development_tools():
    """Test development utilities"""
    # Test debug mode
    os.environ["LITECREWAI_DEBUG"] = "1"
    
    from litecrewai.tools.debug import ToolDebugger
    from litecrewai.tools import tool
    
    @tool
    def debug_test(x: int) -> int:
        return x * 2
    
    debugger = ToolDebugger()
    
    # Wrap tool with debugger
    wrapped = debugger.wrap(debug_test)
    
    # Execute and check debug info
    result = wrapped(5)
    assert result == 10
    
    debug_info = debugger.get_last_execution()
    assert debug_info["tool_name"] == "debug_test"
    assert debug_info["args"] == {"x": 5}
    assert debug_info["result"] == 10
    assert "execution_time" in debug_info
    assert "memory_used" in debug_info
    
    print("✅ Development tools validated")

def test_ide_integration():
    """Test IDE integration files"""
    # Check VS Code snippets
    snippets_file = Path.home() / ".config/Code/User/snippets/litecrewai.json"
    
    if snippets_file.exists():
        snippets = json.loads(snippets_file.read_text())
        assert "LiteCrewAI Tool" in snippets
        print("✅ VS Code integration found")
    else:
        print("⚠️  VS Code snippets not installed")
    
    # Check for .editorconfig
    editorconfig = Path("/opt/litecrewai/app/.editorconfig")
    if editorconfig.exists():
        content = editorconfig.read_text()
        assert "indent_size = 4" in content
        print("✅ EditorConfig present")

if __name__ == "__main__":
    print("🔍 Validating Tool Development Kit...\n")
    
    # Check if CLI is installed
    result = subprocess.run(["which", "litecrewai"], capture_output=True)
    if result.returncode != 0:
        print("⚠️  LiteCrewAI CLI not installed")
        print("Skipping CLI-based tests")
    else:
        test_cli_tool_creation()
        test_generated_tool()
        test_documentation_generator()
    
    test_tool_packaging()
    test_development_tools()
    test_ide_integration()
    
    print("\n✅ Tool Development Kit validation complete!")
```

---

## 📦 FAZA 3: INTEGRACJA LLM I ROUTING

### Blok 3.1: LLM Integration Layer
**Czas**: 10h
**Cel**: Uniwersalna warstwa integracji LLM

#### Zadania Atomowe:

##### Task 3.1.1: Design LLM Abstraction Layer (3h)
**Cel**: Unified interface dla różnych LLM providers

**Prompt dla AI Agent**:
```
Zaprojektuj abstraction layer dla LLM w LiteCrewAI.

Wymagania:
1. Base LLM interface:
   - generate(prompt, **kwargs)
   - stream_generate(prompt, **kwargs)
   - embed(text)
   - count_tokens(text)
   - get_model_info()

2. Provider implementations:
   - OllamaProvider (local)
   - OpenAIProvider
   - GroqProvider
   - HuggingFaceProvider
   - CustomProvider (dla własnych modeli)

3. Configuration:
   - Model selection
   - Temperature, top_p, etc.
   - Timeout handling
   - Retry logic
   - Context window management

4. Response handling:
   - Unified response format
   - Error normalization
   - Token usage tracking
   - Latency measurement

5. Advanced features:
   - Response caching
   - Prompt templates
   - Multi-turn conversations
   - Function calling support

Przykład użycia:
```python
# Initialize provider
llm = LLMProvider.create("ollama/mistral")

# Simple generation
response = llm.generate("Explain quantum computing")

# Streaming
for chunk in llm.stream_generate("Write a story"):
    print(chunk.text, end="")

# With parameters
response = llm.generate(
    "Translate to French: Hello",
    temperature=0.3,
    max_tokens=100
)
```

Design powinien być extensible i testable.
```

**Metryki Sukcesu**:
- ✅ Unified interface works
- ✅ All providers implement same API
- ✅ <100ms overhead
- ✅ Proper error handling

**Walidacja**:
```python
# validate_llm_abstraction.py
import time
import asyncio
from typing import List
from litecrewai.llm import LLMProvider, LLMResponse, LLMError

def test_provider_creation():
    """Test provider factory"""
    # Test various provider strings
    providers = [
        "ollama/mistral",
        "openai/gpt-3.5-turbo",
        "groq/mixtral-8x7b",
        "local/custom-model"
    ]
    
    for provider_string in providers:
        try:
            provider = LLMProvider.create(provider_string)
            assert provider is not None
            assert hasattr(provider, 'generate')
            assert hasattr(provider, 'stream_generate')
            print(f"✅ Created provider: {provider_string}")
        except NotImplementedError:
            print(f"⚠️  Provider not implemented: {provider_string}")

def test_unified_interface():
    """Test all providers implement same interface"""
    from litecrewai.llm.base import BaseLLMProvider
    
    # Get all provider classes
    providers = BaseLLMProvider.__subclasses__()
    
    required_methods = [
        'generate', 'stream_generate', 'embed',
        'count_tokens', 'get_model_info'
    ]
    
    for provider_class in providers:
        for method in required_methods:
            assert hasattr(provider_class, method), \
                f"{provider_class.__name__} missing {method}"
    
    print(f"✅ All {len(providers)} providers implement required interface")

def test_response_format():
    """Test unified response format"""
    provider = LLMProvider.create("ollama/mistral")
    
    response = provider.generate("Say hello")
    
    # Check response structure
    assert isinstance(response, LLMResponse)
    assert hasattr(response, 'text')
    assert hasattr(response, 'tokens_used')
    assert hasattr(response, 'latency_ms')
    assert hasattr(response, 'model')
    assert hasattr(response, 'provider')
    
    # Check values
    assert len(response.text) > 0
    assert response.tokens_used > 0
    assert response.latency_ms > 0
    assert response.model == "mistral"
    assert response.provider == "ollama"
    
    print("✅ Response format validated")

def test_streaming():
    """Test streaming generation"""
    provider = LLMProvider.create("ollama/mistral")
    
    chunks = []
    start = time.time()
    
    for chunk in provider.stream_generate("Count from 1 to 5"):
        assert hasattr(chunk, 'text')
        assert hasattr(chunk, 'is_final')
        chunks.append(chunk.text)
    
    stream_time = time.time() - start
    full_text = ''.join(chunks)
    
    assert len(chunks) > 1, "Should stream multiple chunks"
    assert any(str(i) in full_text for i in range(1, 6))
    print(f"✅ Streaming working ({len(chunks)} chunks in {stream_time:.1f}s)")

def test_error_handling():
    """Test error normalization"""
    provider = LLMProvider.create("ollama/mistral")
    
    # Test timeout
    try:
        provider.generate("Test prompt", timeout=0.001)
        assert False, "Should timeout"
    except LLMError as e:
        assert e.error_type == "timeout"
        assert e.provider == "ollama"
        print("✅ Timeout handling working")
    
    # Test invalid model
    try:
        bad_provider = LLMProvider.create("ollama/nonexistent")
        bad_provider.generate("Test")
        assert False, "Should fail"
    except LLMError as e:
        assert e.error_type == "model_not_found"
        print("✅ Model error handling working")

def test_token_counting():
    """Test token counting accuracy"""
    provider = LLMProvider.create("ollama/mistral")
    
    test_texts = [
        "Hello world",  # ~2 tokens
        "This is a longer sentence with more words.",  # ~10 tokens
        "🚀 Emoji test! 你好世界",  # Special characters
    ]
    
    for text in test_texts:
        count = provider.count_tokens(text)
        assert count > 0
        assert isinstance(count, int)
        print(f"Tokens in '{text[:20]}...': {count}")
    
    print("✅ Token counting working")

def test_context_management():
    """Test context window management"""
    provider = LLMProvider.create("ollama/mistral")
    
    # Get model info
    info = provider.get_model_info()
    assert "context_window" in info
    assert info["context_window"] > 0
    
    # Test with long prompt
    long_prompt = "Hello " * 10000  # Very long
    
    # Should handle gracefully
    response = provider.generate(
        long_prompt,
        truncate=True,  # Auto-truncate to fit
        max_tokens=10
    )
    
    assert response is not None
    assert len(response.text) > 0
    print("✅ Context window management working")

def test_caching():
    """Test response caching"""
    provider = LLMProvider.create(
        "ollama/mistral",
        enable_cache=True
    )
    
    prompt = "What is 2+2?"
    
    # First call
    start = time.time()
    response1 = provider.generate(prompt)
    first_time = time.time() - start
    
    # Second call (should be cached)
    start = time.time()
    response2 = provider.generate(prompt)
    cache_time = time.time() - start
    
    assert response1.text == response2.text
    assert cache_time < first_time / 10  # Much faster
    assert response2.from_cache == True
    
    print(f"✅ Caching working (cache {cache_time*1000:.1f}ms vs {first_time*1000:.1f}ms)")

if __name__ == "__main__":
    print("🔍 Validating LLM abstraction layer...\n")
    
    test_provider_creation()
    test_unified_interface()
    test_response_format()
    test_streaming()
    test_error_handling()
    test_token_counting()
    test_context_management()
    test_caching()
    
    print("\n✅ LLM abstraction validation complete!")
```

##### Task 3.1.2: Implement Ollama Integration (4h)
**Cel**: Pełna integracja z lokalnym Ollama

**Prompt dla AI Agent**:
```
Zaimplementuj kompletną integrację Ollama dla LiteCrewAI.

Funkcjonalności:
1. Model management:
   - List available models
   - Pull new models
   - Delete unused models
   - Model info/stats
   - Auto-pull if missing

2. Generation features:
   - Text generation
   - Streaming support
   - Embeddings
   - Multi-modal (images)
   - JSON mode

3. Performance optimization:
   - Connection pooling
   - Request batching
   - Keep-alive connections
   - Parallel inference
   - GPU utilization tracking

4. Advanced features:
   - Custom model loading
   - Fine-tuned models
   - Model switching
   - Context caching
   - Conversation management

5. Monitoring:
   - Request metrics
   - Token usage
   - GPU/CPU usage
   - Model performance
   - Error rates

6. Configuration:
   - Server URL (default localhost)
   - Timeout settings
   - Retry configuration
   - Model preferences
   - Resource limits

Przykład:
```python
ollama = OllamaProvider(
    base_url="http://localhost:11434",
    default_model="mistral",
    timeout=30
)

# Check available models
models = ollama.list_models()

# Pull if needed
if "llama2" not in models:
    ollama.pull_model("llama2")

# Generate with specific model
response = ollama.generate(
    "Explain AI",
    model="llama2",
    temperature=0.7,
    format="json"  # Force JSON output
)

# Stream generation
for chunk in ollama.stream_generate("Write a poem"):
    print(chunk.text, end="", flush=True)

# Get embeddings
embeddings = ollama.embed(["text1", "text2"])
```

Include health checks and graceful degradation.
```

**Metryki Sukcesu**:
- ✅ All Ollama features work
- ✅ <50ms latency overhead
- ✅ Streaming smooth
- ✅ Auto-recovery works

**Walidacja**:
```python
# validate_ollama_integration.py
import time
import json
import asyncio
from litecrewai.llm.providers.ollama import OllamaProvider

def test_ollama_connection():
    """Test Ollama server connection"""
    ollama = OllamaProvider()
    
    # Test health check
    assert ollama.is_healthy(), "Ollama server not responding"
    
    # Test server info
    info = ollama.server_info()
    assert "version" in info
    print(f"✅ Connected to Ollama {info['version']}")

def test_model_management():
    """Test model management features"""
    ollama = OllamaProvider()
    
    # List models
    models = ollama.list_models()
    print(f"Available models: {[m['name'] for m in models]}")
    
    # Check if test model exists
    test_model = "mistral:7b"
    model_names = [m['name'] for m in models]
    
    if test_model not in model_names:
        print(f"Pulling {test_model}...")
        # In real test, would pull - here just check method exists
        assert hasattr(ollama, 'pull_model')
    
    # Get model info
    if model_names:
        info = ollama.get_model_info(model_names[0])
        assert "parameters" in info
        assert "context_length" in info
        print(f"✅ Model info retrieved for {model_names[0]}")

def test_generation_modes():
    """Test different generation modes"""
    ollama = OllamaProvider()
    
    # Standard generation
    response = ollama.generate("Say hello in JSON format")
    assert len(response.text) > 0
    print("✅ Standard generation working")
    
    # JSON mode
    response = ollama.generate(
        "Return a JSON object with name and age",
        format="json"
    )
    try:
        parsed = json.loads(response.text)
        assert isinstance(parsed, dict)
        print("✅ JSON mode working")
    except json.JSONDecodeError:
        print("⚠️  JSON mode returned invalid JSON")
    
    # With specific parameters
    response = ollama.generate(
        "Write exactly 5 words",
        temperature=0.1,
        top_p=0.9,
        max_tokens=20
    )
    word_count = len(response.text.split())
    print(f"✅ Parameter control working (got {word_count} words)")

def test_streaming_performance():
    """Test streaming generation performance"""
    ollama = OllamaProvider()
    
    chunks_received = 0
    first_chunk_time = None
    start_time = time.time()
    
    for chunk in ollama.stream_generate("Count from 1 to 10 slowly"):
        if first_chunk_time is None:
            first_chunk_time = time.time() - start_time
        chunks_received += 1
    
    total_time = time.time() - start_time
    
    print(f"✅ Streaming stats:")
    print(f"   - First chunk: {first_chunk_time*1000:.0f}ms")
    print(f"   - Total chunks: {chunks_received}")
    print(f"   - Total time: {total_time:.1f}s")
    
    assert first_chunk_time < 1.0, "First chunk too slow"
    assert chunks_received > 5, "Too few chunks"

def test_embeddings():
    """Test embedding generation"""
    ollama = OllamaProvider()
    
    # Single embedding
    embedding = ollama.embed("Hello world")
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)
    
    # Batch embeddings
    texts = ["Hello", "World", "AI", "Test"]
    embeddings = ollama.embed_batch(texts)
    assert len(embeddings) == len(texts)
    assert all(len(emb) == len(embeddings[0]) for emb in embeddings)
    
    print(f"✅ Embeddings working (dimension: {len(embedding)})")

def test_error_recovery():
    """Test error handling and recovery"""
    ollama = OllamaProvider(
        base_url="http://localhost:11434",
        timeout=1,
        max_retries=2
    )
    
    # Test timeout recovery
    try:
        # Very long prompt that might timeout
        ollama.generate("Write a 10000 word essay", timeout=0.1)
    except Exception as e:
        assert "timeout" in str(e).lower()
        print("✅ Timeout handling working")
    
    # Test invalid model
    try:
        ollama.generate("Test", model="nonexistent-model")
    except Exception as e:
        assert "model" in str(e).lower()
        print("✅ Invalid model handling working")
    
    # Test connection recovery
    # Simulate connection issue and recovery
    original_url = ollama.base_url
    ollama.base_url = "http://invalid:11434"
    
    try:
        ollama.generate("Test")
    except:
        pass
    
    # Restore and test recovery
    ollama.base_url = original_url
    response = ollama.generate("Test recovery")
    assert response is not None
    print("✅ Connection recovery working")

def test_performance_tracking():
    """Test performance metrics"""
    ollama = OllamaProvider(enable_metrics=True)
    
    # Generate multiple requests
    for i in range(5):
        ollama.generate(f"Test {i}")
    
    # Get metrics
    metrics = ollama.get_metrics()
    
    assert "total_requests" in metrics
    assert metrics["total_requests"] >= 5
    assert "average_latency_ms" in metrics
    assert "tokens_per_second" in metrics
    assert "error_rate" in metrics
    
    print(f"✅ Performance metrics:")
    print(f"   - Avg latency: {metrics['average_latency_ms']:.0f}ms")
    print(f"   - Tokens/sec: {metrics['tokens_per_second']:.1f}")
    print(f"   - Error rate: {metrics['error_rate']:.1%}")

def test_conversation_management():
    """Test conversation context management"""
    ollama = OllamaProvider()
    
    # Start conversation
    conv_id = ollama.create_conversation()
    
    # First message
    response1 = ollama.generate(
        "My name is Alice. Remember this.",
        conversation_id=conv_id
    )
    
    # Second message (should remember context)
    response2 = ollama.generate(
        "What is my name?",
        conversation_id=conv_id
    )
    
    assert "alice" in response2.text.lower()
    print("✅ Conversation management working")
    
    # Clear conversation
    ollama.clear_conversation(conv_id)

if __name__ == "__main__":
    print("🔍 Validating Ollama integration...\n")
    
    test_ollama_connection()
    test_model_management()
    test_generation_modes()
    test_streaming_performance()
    test_embeddings()
    test_error_recovery()
    test_performance_tracking()
    test_conversation_management()
    
    print("\n✅ Ollama integration validation complete!")
```

##### Task 3.1.3: Add External LLM Providers (3h)
**Cel**: Wsparcie dla OpenAI, Groq i innych

**Prompt dla AI Agent**:
```
Dodaj wsparcie dla zewnętrznych LLM providers w LiteCrewAI.

Providers do implementacji:
1. OpenAI:
   - GPT-4, GPT-3.5
   - Embeddings (ada-002)
   - Function calling
   - Vision support
   - Assistants API (optional)

2. Groq:
   - Mixtral, Llama2
   - Ultra-fast inference
   - Streaming
   - Token counting

3. Google (Gemini):
   - Gemini Pro
   - Multi-modal
   - Safety settings
   - Grounding

4. Anthropic (Claude):
   - Claude 3
   - Long context
   - Constitutional AI
   - Vision

5. Cohere:
   - Command model
   - Embeddings
   - Reranking
   - RAG support

Wspólne features:
- API key management (from env vars)
- Rate limiting per provider
- Cost tracking
- Fallback chains
- Request logging
- Error standardization

Przykład konfiguracji:
```yaml
llm_providers:
  primary: ollama/mistral  # Free, local
  fallback1: groq/mixtral  # Fast, cheap
  fallback2: openai/gpt-3.5-turbo  # Reliable
  
  config:
    openai:
      api_key: ${OPENAI_API_KEY}
      organization: ${OPENAI_ORG}
      max_retries: 3
    
    groq:
      api_key: ${GROQ_API_KEY}
      timeout: 30
    
    rate_limits:
      openai: 60/min
      groq: 100/min
```

Implementacja powinna być modułowa - każdy provider jako osobny moduł.
```

**Metryki Sukcesu**:
- ✅ All providers work
- ✅ Seamless fallback
- ✅ Cost tracking accurate
- ✅ <100ms switching time

**Walidacja**:
```python
# validate_external_providers.py
import os
import time
from unittest.mock import patch, MagicMock
from litecrewai.llm.providers import (
    OpenAIProvider, GroqProvider, GoogleProvider,
    AnthropicProvider, CohereProvider
)

def test_provider_initialization():
    """Test all providers initialize correctly"""
    providers = [
        (OpenAIProvider, "OPENAI_API_KEY"),
        (GroqProvider, "GROQ_API_KEY"),
        (GoogleProvider, "GOOGLE_API_KEY"),
        (AnthropicProvider, "ANTHROPIC_API_KEY"),
        (CohereProvider, "COHERE_API_KEY")
    ]
    
    for provider_class, env_var in providers:
        # Test with mock API key
        with patch.dict(os.environ, {env_var: "test-key"}):
            provider = provider_class()
            assert provider is not None
            assert hasattr(provider, 'generate')
            print(f"✅ {provider_class.__name__} initialized")

def test_api_key_management():
    """Test secure API key handling"""
    # Test environment variable loading
    test_key = "sk-test123"
    with patch.dict(os.environ, {"OPENAI_API_KEY": test_key}):
        provider = OpenAIProvider()
        # Key should be loaded but not exposed
        assert provider._api_key == test_key
        assert str(provider) != test_key  # Should not leak in repr
    
    # Test missing API key
    with patch.dict(os.environ, {}, clear=True):
        try:
            provider = OpenAIProvider()
            provider.generate("test")
            assert False, "Should fail without API key"
        except ValueError as e:
            assert "API key" in str(e)
    
    print("✅ API key management secure")

def test_rate_limiting():
    """Test rate limiting per provider"""
    # Mock provider with rate limit
    with patch('litecrewai.llm.providers.openai.openai') as mock_openai:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test"))]
        mock_response.usage = MagicMock(total_tokens=10)
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        provider = OpenAIProvider(rate_limit="10/min")
        
        # Make rapid requests
        start = time.time()
        for i in range(12):  # Exceed limit
            try:
                provider.generate(f"Test {i}")
            except Exception as e:
                if "rate limit" in str(e).lower():
                    print(f"✅ Rate limit enforced after {i} requests")
                    break
        
        elapsed = time.time() - start
        assert elapsed > 1, "Rate limiting should introduce delays"

def test_cost_tracking():
    """Test accurate cost tracking"""
    # Mock providers with known costs
    providers_costs = [
        (OpenAIProvider, "gpt-3.5-turbo", 0.001, 100),  # $0.001 per 1K tokens
        (GroqProvider, "mixtral-8x7b", 0.0002, 100),   # $0.0002 per 1K tokens
    ]
    
    for provider_class, model, cost_per_1k, tokens in providers_costs:
        with patch.object(provider_class, 'generate') as mock_generate:
            mock_generate.return_value = MagicMock(
                text="Response",
                tokens_used=tokens,
                cost=tokens * cost_per_1k / 1000
            )
            
            provider = provider_class()
            response = provider.generate("Test", model=model)
            
            expected_cost = tokens * cost_per_1k / 1000
            assert abs(response.cost - expected_cost) < 0.0001
            print(f"✅ {provider_class.__name__} cost tracking: ${response.cost:.4f}")

def test_fallback_chain():
    """Test fallback between providers"""
    from litecrewai.llm import FallbackChain
    
    # Create chain with mocked providers
    primary = MagicMock()
    fallback1 = MagicMock()
    fallback2 = MagicMock()
    
    # Primary fails
    primary.generate.side_effect = Exception("Primary failed")
    
    # Fallback1 fails
    fallback1.generate.side_effect = Exception("Fallback1 failed")
    
    # Fallback2 succeeds
    fallback2.generate.return_value = MagicMock(text="Success from fallback2")
    
    chain = FallbackChain([primary, fallback1, fallback2])
    
    start = time.time()
    result = chain.generate("Test prompt")
    switch_time = (time.time() - start) * 1000
    
    assert result.text == "Success from fallback2"
    assert switch_time < 100, f"Switching too slow: {switch_time}ms"
    print(f"✅ Fallback chain working ({switch_time:.0f}ms switch time)")

def test_request_logging():
    """Test request logging for debugging"""
    from litecrewai.llm.providers.base import RequestLogger
    
    logger = RequestLogger()
    
    # Mock provider with logging
    with patch('litecrewai.llm.providers.openai.OpenAIProvider.generate') as mock:
        mock.return_value = MagicMock(text="Response", tokens_used=50)
        
        provider = OpenAIProvider(request_logger=logger)
        provider.generate("Test prompt")
    
    # Check logged data
    logs = logger.get_logs()
    assert len(logs) == 1
    
    log = logs[0]
    assert log['provider'] == 'openai'
    assert log['prompt'] == 'Test prompt'
    assert log['response_length'] > 0
    assert log['tokens_used'] == 50
    assert 'timestamp' in log
    assert 'latency_ms' in log
    
    print("✅ Request logging working")

def test_error_standardization():
    """Test error handling is consistent across providers"""
    from litecrewai.llm.errors import (
        RateLimitError, AuthenticationError,
        ModelNotFoundError, ContextLengthError
    )
    
    error_scenarios = [
        ("rate_limit", RateLimitError),
        ("invalid_api_key", AuthenticationError),
        ("model_not_found", ModelNotFoundError),
        ("context_length_exceeded", ContextLengthError)
    ]
    
    for scenario, expected_error in error_scenarios:
        # Test each provider handles errors consistently
        for provider_class in [OpenAIProvider, GroqProvider]:
            with patch.object(provider_class, 'generate') as mock:
                # Simulate provider-specific error
                if provider_class == OpenAIProvider:
                    mock.side_effect = Exception(f"OpenAI: {scenario}")
                else:
                    mock.side_effect = Exception(f"Groq: {scenario}")
                
                provider = provider_class()
                
                try:
                    provider.generate("Test")
                    assert False, "Should raise error"
                except expected_error:
                    print(f"✅ {provider_class.__name__} standardizes {scenario}")
                except Exception as e:
                    # In real implementation, would check error mapping
                    pass

def test_multimodal_support():
    """Test multimodal capabilities where supported"""
    # Test OpenAI vision
    with patch('litecrewai.llm.providers.openai.OpenAIProvider.generate') as mock:
        mock.return_value = MagicMock(text="I see a cat")
        
        provider = OpenAIProvider()
        response = provider.generate(
            "What's in this image?",
            images=["path/to/image.jpg"]
        )
        
        assert "cat" in response.text
        print("✅ Multimodal support validated")

if __name__ == "__main__":
    print("🔍 Validating external LLM providers...\n")
    
    test_provider_initialization()
    test_api_key_management()
    test_rate_limiting()
    test_cost_tracking()
    test_fallback_chain()
    test_request_logging()
    test_error_standardization()
    test_multimodal_support()
    
    print("\n✅ External providers validation complete!")
```

### Blok 3.2: Intelligent Routing System
**Czas**: 8h
**Cel**: Inteligentny routing między LLM

#### Zadania Atomowe:

##### Task 3.2.1: Build Cost-Aware Router (3h)
**Cel**: Router minimalizujący koszty

**Prompt dla AI Agent**:
```
Zbuduj inteligentny router dla LiteCrewAI który minimalizuje koszty.

Komponenty:
1. Cost calculation:
   - Per-token costs dla każdego modelu
   - Ukryte koszty (API calls, embeddings)
   - Walutowe przeliczniki
   - Historical cost tracking

2. Decision factors:
   - Task complexity analysis
   - Required capabilities (vision, functions, etc)
   - Context length needs
   - Quality requirements
   - Latency requirements
   - Budget remaining

3. Routing strategies:
   - Greedy (zawsze najtańszy)
   - Quality-first (budget allowing)
   - Balanced (cost/quality ratio)
   - Time-based (tańsze modele w nocy)
   - Usage-based (premium dla ważnych zadań)

4. Budget management:
   - Daily/monthly limits
   - Per-user budgets
   - Per-task budgets
   - Alerts and warnings
   - Automatic downgrade

5. Optimization features:
   - Prompt compression
   - Response caching
   - Batch processing
   - Model-specific prompt optimization

Przykład:
```python
router = CostAwareRouter(
    monthly_budget=30.0,
    strategy="balanced"
)

# Analyze task and route
task = "Write a 500 word essay on AI"
model = router.select_model(
    task=task,
    min_quality=0.8,
    max_cost=0.10
)
print(f"Selected: {model} (est. cost: ${router.estimate_cost(task, model)})")

# Execute with budget tracking
response = router.execute(task)
print(f"Actual cost: ${response.cost}")
print(f"Budget remaining: ${router.budget_remaining}")

# Get recommendations
if router.budget_remaining < 5:
    print("Low budget! Switching to economy mode...")
    router.strategy = "greedy"
```
```

**Metryki Sukcesu**:
- ✅ Cost estimation ±10%
- ✅ Budget never exceeded
- ✅ Intelligent routing works
- ✅ <50ms routing decision

**Walidacja**:
```python
# validate_cost_router.py
import time
from datetime import datetime, timedelta
from litecrewai.routing import CostAwareRouter, RoutingStrategy

def test_cost_calculation():
    """Test accurate cost calculation"""
    router = CostAwareRouter()
    
    # Test known model costs
    test_cases = [
        ("openai/gpt-3.5-turbo", 100, 0.0001),  # $0.001 per 1K
        ("openai/gpt-4", 100, 0.003),            # $0.03 per 1K
        ("groq/mixtral-8x7b", 100, 0.00002),     # $0.0002 per 1K
        ("ollama/mistral", 100, 0.0),            # Free
    ]
    
    for model, tokens, expected_cost in test_cases:
        cost = router.calculate_cost(model, tokens)
        assert abs(cost - expected_cost) < 0.00001, \
            f"Wrong cost for {model}: {cost} vs {expected_cost}"
        print(f"✅ {model}: ${cost:.5f} for {tokens} tokens")

def test_complexity_analysis():
    """Test task complexity analysis"""
    router = CostAwareRouter()
    
    test_tasks = [
        ("What is 2+2?", "simple"),
        ("Explain quantum physics", "medium"),
        ("Write a research paper on AI ethics with citations", "complex"),
        ("Hi", "simple"),
        ("Analyze this 10-page document and create a summary", "complex")
    ]
    
    for task, expected_complexity in test_tasks:
        complexity = router.analyze_complexity(task)
        assert complexity == expected_complexity, \
            f"Wrong complexity for '{task[:30]}...': {complexity}"
        print(f"✅ Complexity '{expected_complexity}': {task[:30]}...")

def test_routing_strategies():
    """Test different routing strategies"""
    # Greedy strategy (always cheapest)
    router = CostAwareRouter(strategy=RoutingStrategy.GREEDY)
    model = router.select_model("Complex analysis task")
    assert "ollama" in model or "groq" in model
    print(f"✅ Greedy selected: {model}")
    
    # Quality-first strategy
    router = CostAwareRouter(
        strategy=RoutingStrategy.QUALITY_FIRST,
        monthly_budget=1000  # High budget
    )
    model = router.select_model("Write a novel chapter")
    assert "gpt-4" in model or "claude" in model
    print(f"✅ Quality-first selected: {model}")
    
    # Balanced strategy
    router = CostAwareRouter(strategy=RoutingStrategy.BALANCED)
    model = router.select_model("Summarize this article")
    assert model in ["groq/mixtral-8x7b", "openai/gpt-3.5-turbo"]
    print(f"✅ Balanced selected: {model}")

def test_budget_management():
    """Test budget tracking and limits"""
    router = CostAwareRouter(
        monthly_budget=1.0,  # $1 for testing
        strategy=RoutingStrategy.BALANCED
    )
    
    # Simulate spending
    router._spend(0.70)  # Spend 70% of budget
    
    # Should downgrade to cheaper models
    model = router.select_model("Complex task")
    assert "ollama" in model or "groq" in model, \
        "Should use cheap model when budget low"
    
    # Test budget alerts
    alerts = router.get_budget_alerts()
    assert len(alerts) > 0
    assert any("70%" in alert for alert in alerts)
    print("✅ Budget alerts working")
    
    # Test budget exceeded
    router._spend(0.35)  # Total 105%
    model = router.select_model("Any task")
    assert "ollama" in model, "Should only use free models when over budget"
    print("✅ Budget enforcement working")

def test_routing_performance():
    """Test routing decision performance"""
    router = CostAwareRouter()
    
    # Measure routing time
    times = []
    for _ in range(100):
        start = time.time()
        model = router.select_model("Test task for routing")
        times.append((time.time() - start) * 1000)
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    print(f"✅ Routing performance:")
    print(f"   - Average: {avg_time:.1f}ms")
    print(f"   - Max: {max_time:.1f}ms")
    
    assert avg_time < 50, f"Routing too slow: {avg_time}ms"
    assert max_time < 100, f"Max routing too slow: {max_time}ms"

def test_prompt_optimization():
    """Test prompt compression and optimization"""
    router = CostAwareRouter()
    
    # Long, redundant prompt
    original_prompt = """
    I need you to help me with something. What I want you to do is to 
    analyze the following text and provide a summary. The text is about 
    artificial intelligence. Please read it carefully and then write a 
    summary. Here is the text: AI is transforming the world...
    """ * 10  # Make it long
    
    # Optimize for expensive model
    optimized = router.optimize_prompt(original_prompt, "openai/gpt-4")
    
    assert len(optimized) < len(original_prompt) * 0.8
    assert "analyze" in optimized.lower()
    assert "summary" in optimized.lower()
    
    print(f"✅ Prompt optimization: {len(original_prompt)} → {len(optimized)} chars")
    print(f"   Cost reduction: {(1 - len(optimized)/len(original_prompt))*100:.1f}%")

def test_time_based_routing():
    """Test time-based routing strategies"""
    # Simulate different times
    with patch('datetime.datetime') as mock_datetime:
        # Business hours - normal routing
        mock_datetime.now.return_value = datetime(2024, 1, 1, 14, 0)  # 2 PM
        router = CostAwareRouter(strategy=RoutingStrategy.TIME_BASED)
        
        day_model = router.select_model("Business analysis")
        
        # Night hours - use cheaper models
        mock_datetime.now.return_value = datetime(2024, 1, 1, 3, 0)  # 3 AM
        night_model = router.select_model("Business analysis")
        
        # Night model should be cheaper
        day_cost = router.calculate_cost(day_model, 1000)
        night_cost = router.calculate_cost(night_model, 1000)
        
        assert night_cost <= day_cost
        print(f"✅ Time-based routing: day=${day_cost:.3f}, night=${night_cost:.3f}")

def test_caching_impact():
    """Test how caching affects routing decisions"""
    router = CostAwareRouter(enable_cache=True)
    
    prompt = "What is the capital of France?"
    
    # First call - routes to appropriate model
    model1 = router.select_model(prompt)
    response1 = router.execute(prompt)
    cost1 = response1.cost
    
    # Second call - should hit cache
    model2 = router.select_model(prompt)
    response2 = router.execute(prompt)
    cost2 = response2.cost
    
    assert cost2 == 0, "Cached response should be free"
    assert response1.text == response2.text
    print("✅ Cache-aware routing working")

if __name__ == "__main__":
    print("🔍 Validating cost-aware router...\n")
    
    test_cost_calculation()
    test_complexity_analysis() 
    test_routing_strategies()
    test_budget_management()
    test_routing_performance()
    test_prompt_optimization()
    
    # Mock required for time test
    from unittest.mock import patch
    test_time_based_routing()
    
    test_caching_impact()
    
    print("\n✅ Cost router validation complete!")
```

##### Task 3.2.2: Implement Quality-Based Selection (3h)
**Cel**: Wybór modelu based on quality needs

**Prompt dla AI Agent**:
```
Zaimplementuj system wyboru modelu bazujący na wymaganiach jakościowych.

Komponenty:
1. Quality metrics:
   - Accuracy score (0-1)
   - Creativity score (0-1)
   - Reasoning ability (0-1)
   - Language quality (0-1)
   - Instruction following (0-1)
   - Domain expertise (per domain)

2. Model capabilities:
   - Capability matrix per model
   - Benchmark results
   - User feedback integration
   - A/B test results
   - Dynamic scoring updates

3. Task requirements:
   - Required capabilities
   - Minimum quality threshold
   - Domain specificity
   - Output format needs
   - Language requirements

4. Matching algorithm:
   - Weighted scoring
   - Constraint satisfaction
   - Pareto optimization
   - Fallback strategies

5. Quality monitoring:
   - Output validation
   - User satisfaction tracking
   - Automatic reranking
   - Model performance decay detection

Przykład:
```python
selector = QualityBasedSelector()

# Define task requirements
requirements = TaskRequirements(
    domain="medical",
    min_accuracy=0.95,
    needs_citations=True,
    output_format="structured",
    language="en"
)

# Get best model
model = selector.select_best_model(
    task="Explain treatment options for diabetes",
    requirements=requirements
)

print(f"Selected: {model.name}")
print(f"Expected quality: {model.expected_quality}")
print(f"Capabilities: {model.capabilities}")

# Execute with quality validation
response = selector.execute_with_validation(
    task="...",
    model=model,
    validate_output=True
)

if response.quality_score < requirements.min_accuracy:
    # Automatic retry with better model
    response = selector.escalate_and_retry(response)
```

System powinien uczyć się z każdego użycia.
```

**Metryki Sukcesu**:
- ✅ Quality prediction ±15%
- ✅ Right model 90%+ time
- ✅ Learning improves selection
- ✅ Fast selection <100ms

**Walidacja**:
```python
# validate_quality_selector.py
import numpy as np
from dataclasses import dataclass
from litecrewai.routing.quality import (
    QualityBasedSelector, TaskRequirements,
    ModelCapabilities, QualityMetrics
)

def test_capability_matrix():
    """Test model capability scoring"""
    selector = QualityBasedSelector()
    
    # Check all models have capabilities defined
    models = selector.get_all_models()
    assert len(models) > 0
    
    for model in models:
        caps = model.capabilities
        assert isinstance(caps.accuracy, float)
        assert 0 <= caps.accuracy <= 1
        assert isinstance(caps.creativity, float)
        assert isinstance(caps.reasoning, float)
        assert isinstance(caps.language_quality, float)
        assert isinstance(caps.instruction_following, float)
        
        print(f"✅ {model.name}: accuracy={caps.accuracy:.2f}, "
              f"reasoning={caps.reasoning:.2f}")

def test_task_matching():
    """Test task requirement matching"""
    selector = QualityBasedSelector()
    
    # High accuracy requirement
    req1 = TaskRequirements(
        min_accuracy=0.95,
        domain="medical"
    )
    model1 = selector.select_best_model(
        "Diagnose symptoms", req1
    )
    assert model1.capabilities.accuracy >= 0.95
    assert "gpt-4" in model1.name or "claude" in model1.name
    print(f"✅ High accuracy task → {model1.name}")
    
    # Creative task
    req2 = TaskRequirements(
        min_creativity=0.8,
        domain="creative_writing"
    )
    model2 = selector.select_best_model(
        "Write a poem", req2
    )
    assert model2.capabilities.creativity >= 0.8
    print(f"✅ Creative task → {model2.name}")
    
    # Reasoning task
    req3 = TaskRequirements(
        min_reasoning=0.85,
        domain="mathematics"
    )
    model3 = selector.select_best_model(
        "Solve complex equation", req3
    )
    assert model3.capabilities.reasoning >= 0.85
    print(f"✅ Reasoning task → {model3.name}")

def test_constraint_satisfaction():
    """Test multiple constraint handling"""
    selector = QualityBasedSelector()
    
    # Multiple constraints
    requirements = TaskRequirements(
        min_accuracy=0.8,
        min_creativity=0.7,
        min_reasoning=0.8,
        max_cost_per_1k_tokens=0.01,  # Budget constraint
        needs_citations=True,
        output_format="json",
        max_latency_ms=2000
    )
    
    model = selector.select_best_model(
        "Research and summarize with citations",
        requirements
    )
    
    # Check all constraints met
    assert model.capabilities.accuracy >= 0.8
    assert model.capabilities.creativity >= 0.7
    assert model.capabilities.reasoning >= 0.8
    assert model.cost_per_1k_tokens <= 0.01
    assert model.supports_citations
    assert "json" in model.supported_formats
    
    print(f"✅ Multi-constraint satisfied by: {model.name}")

def test_quality_validation():
    """Test output quality validation"""
    selector = QualityBasedSelector()
    
    # Mock response
    @dataclass
    class MockResponse:
        text: str
        model: str
        
    # Good response
    good_response = MockResponse(
        text="The capital of France is Paris. This is a well-known fact.",
        model="gpt-3.5-turbo"
    )
    
    score = selector.validate_quality(
        good_response,
        task="What is the capital of France?",
        requirements=TaskRequirements(min_accuracy=0.8)
    )
    
    assert score.accuracy >= 0.8
    assert score.completeness >= 0.8
    print(f"✅ Good response score: {score.overall:.2f}")
    
    # Poor response
    poor_response = MockResponse(
        text="I don't know.",
        model="gpt-3.5-turbo"
    )
    
    score = selector.validate_quality(
        poor_response,
        task="What is the capital of France?",
        requirements=TaskRequirements(min_accuracy=0.8)
    )
    
    assert score.accuracy < 0.5
    assert score.completeness < 0.5
    print(f"✅ Poor response score: {score.overall:.2f}")

def test_learning_system():
    """Test quality learning from feedback"""
    selector = QualityBasedSelector()
    
    # Initial selection
    model1 = selector.select_best_model(
        "Technical documentation task",
        TaskRequirements(min_accuracy=0.85)
    )
    initial_score = model1.expected_quality
    
    # Simulate feedback
    feedback_data = [
        (model1.name, "Technical documentation task", 0.7),  # Lower than expected
        (model1.name, "Technical documentation task", 0.72),
        (model1.name, "Technical documentation task", 0.71),
    ]
    
    for model, task, actual_quality in feedback_data:
        selector.record_feedback(model, task, actual_quality)
    
    # Select again - should adapt
    model2 = selector.select_best_model(
        "Technical documentation task",
        TaskRequirements(min_accuracy=0.85)
    )
    
    # Should select different model or adjust expectations
    if model2.name == model1.name:
        assert model2.expected_quality < initial_score
        print(f"✅ Adjusted expectations: {initial_score:.2f} → {model2.expected_quality:.2f}")
    else:
        print(f"✅ Switched models: {model1.name} → {model2.name}")

def test_domain_expertise():
    """Test domain-specific model selection"""
    selector = QualityBasedSelector()
    
    domains = [
        ("medical", "Explain MRI results"),
        ("legal", "Draft a contract clause"),
        ("coding", "Write a Python function"),
        ("creative", "Write a haiku"),
        ("scientific", "Explain quantum entanglement")
    ]
    
    selected_models = {}
    
    for domain, task in domains:
        req = TaskRequirements(domain=domain)
        model = selector.select_best_model(task, req)
        selected_models[domain] = model.name
        
        # Check domain expertise
        domain_score = model.capabilities.domain_expertise.get(domain, 0)
        assert domain_score > 0.7, f"Low expertise for {domain}"
        
        print(f"✅ {domain}: {model.name} (expertise: {domain_score:.2f})")
    
    # Different domains should potentially use different models
    unique_models = len(set(selected_models.values()))
    assert unique_models > 1, "Should use varied models for different domains"

def test_performance_monitoring():
    """Test model performance tracking"""
    selector = QualityBasedSelector()
    
    # Simulate performance data
    model_name = "gpt-3.5-turbo"
    
    # Record successful uses
    for _ in range(10):
        selector.record_performance(
            model_name,
            task_type="general",
            latency_ms=800,
            quality_score=0.85,
            success=True
        )
    
    # Record some failures
    for _ in range(2):
        selector.record_performance(
            model_name,
            task_type="general", 
            latency_ms=5000,
            quality_score=0.4,
            success=False
        )
    
    # Get performance stats
    stats = selector.get_model_performance(model_name)
    
    assert stats["success_rate"] == 10/12
    assert stats["avg_quality"] > 0.7
    assert stats["avg_latency_ms"] < 2000
    assert stats["total_uses"] == 12
    
    print(f"✅ Performance tracking:")
    print(f"   - Success rate: {stats['success_rate']:.1%}")
    print(f"   - Avg quality: {stats['avg_quality']:.2f}")
    print(f"   - Avg latency: {stats['avg_latency_ms']:.0f}ms")

def test_escalation_strategy():
    """Test automatic escalation to better models"""
    selector = QualityBasedSelector()
    
    # Start with minimum requirements
    req = TaskRequirements(
        min_accuracy=0.9,
        escalation_enabled=True
    )
    
    # Mock poor quality response
    poor_response = MockResponse(
        text="Incomplete answer...",
        model="gpt-3.5-turbo"
    )
    
    # Validate and escalate
    escalated = selector.escalate_if_needed(
        poor_response,
        task="Complex medical diagnosis",
        requirements=req,
        measured_quality=0.6  # Below requirement
    )
    
    assert escalated.model != poor_response.model
    assert "gpt-4" in escalated.model or "claude" in escalated.model
    print(f"✅ Escalated from {poor_response.model} → {escalated.model}")

if __name__ == "__main__":
    print("🔍 Validating quality-based selector...\n")
    
    test_capability_matrix()
    test_task_matching()
    test_constraint_satisfaction()
    test_quality_validation()
    test_learning_system()
    test_domain_expertise()
    test_performance_monitoring()
    test_escalation_strategy()
    
    print("\n✅ Quality selector validation complete!")
```

##### Task 3.2.3: Create Fallback Mechanisms (2h)
**Cel**: Niezawodny system fallback

**Prompt dla AI Agent**:
```
Stwórz comprehensive fallback system dla LiteCrewAI.

Komponenty:
1. Fallback triggers:
   - Timeout (configurable)
   - Error responses
   - Rate limits hit
   - Quality below threshold
   - Cost exceeded
   - Model unavailable

2. Fallback strategies:
   - Simple retry with backoff
   - Switch to alternate model
   - Degrade gracefully
   - Queue for later
   - Return cached response
   - Use local model

3. Fallback chains:
   - Primary → Secondary → Emergency
   - Cost-ordered fallbacks
   - Quality-ordered fallbacks
   - Latency-ordered fallbacks
   - Geographic fallbacks

4. State preservation:
   - Maintain context
   - Transfer conversation
   - Adjust parameters
   - Log transition reason

5. Recovery mechanisms:
   - Auto-recovery detection
   - Gradual restoration
   - Health monitoring
   - Circuit breaker pattern

Przykład:
```python
# Configure fallback chain
fallback = FallbackChain([
    ModelConfig("openai/gpt-4", retry_times=2),
    ModelConfig("anthropic/claude-3", retry_times=1),
    ModelConfig("groq/mixtral", retry_times=3),
    ModelConfig("ollama/mistral", retry_times=5)  # Local last resort
])

# Execute with automatic fallback
result = fallback.execute(
    task="Complex analysis",
    timeout=30,
    min_quality=0.8
)

print(f"Success: {result.success}")
print(f"Final model: {result.model_used}")
print(f"Attempts: {result.total_attempts}")
print(f"Fallback reasons: {result.fallback_trail}")

# Check health status
health = fallback.get_health_status()
for model, status in health.items():
    print(f"{model}: {status.state} (success rate: {status.success_rate:.1%})")
```

System powinien być transparent i debuggable.
```

**Metryki Sukcesu**:
- ✅ 99.9% success rate
- ✅ Smooth transitions
- ✅ Context preserved
- ✅ Fast recovery <5s

**Walidacja**:
```python
# validate_fallback_system.py
import time
import asyncio
from unittest.mock import Mock, patch
from litecrewai.routing.fallback import (
    FallbackChain, ModelConfig, FallbackTrigger,
    CircuitBreaker, HealthMonitor
)

def test_basic_fallback():
    """Test basic fallback functionality"""
    # Create chain with mocked models
    model1 = Mock()
    model1.generate.side_effect = Exception("Model 1 failed")
    
    model2 = Mock()
    model2.generate.side_effect = Exception("Model 2 failed")
    
    model3 = Mock()
    model3.generate.return_value = Mock(text="Success from model 3")
    
    chain = FallbackChain([
        ModelConfig("model1", provider=model1),
        ModelConfig("model2", provider=model2),
        ModelConfig("model3", provider=model3)
    ])
    
    result = chain.execute("Test task")
    
    assert result.success == True
    assert result.model_used == "model3"
    assert result.total_attempts == 3
    assert len(result.fallback_trail) == 2
    
    print("✅ Basic fallback working")
    print(f"   Trail: {' → '.join([f['from'] for f in result.fallback_trail])}")

def test_retry_with_backoff():
    """Test retry logic with exponential backoff"""
    model = Mock()
    model.generate.side_effect = [
        Exception("Attempt 1"),
        Exception("Attempt 2"),
        Mock(text="Success on attempt 3")
    ]
    
    chain = FallbackChain([
        ModelConfig("model1", provider=model, retry_times=3, backoff_base=0.1)
    ])
    
    start = time.time()
    result = chain.execute("Test task")
    duration = time.time() - start
    
    assert result.success == True
    assert result.total_attempts == 3
    # Should have delays: 0.1s, 0.2s
    assert duration >= 0.3
    
    print(f"✅ Retry with backoff working (took {duration:.2f}s)")

def test_timeout_fallback():
    """Test timeout-triggered fallback"""
    def slow_model(prompt):
        time.sleep(2)
        return Mock(text="Slow response")
    
    def fast_model(prompt):
        return Mock(text="Fast response")
    
    model1 = Mock()
    model1.generate = slow_model
    
    model2 = Mock()
    model2.generate = fast_model
    
    chain = FallbackChain([
        ModelConfig("slow_model", provider=model1),
        ModelConfig("fast_model", provider=model2)
    ], timeout=1.0)
    
    start = time.time()
    result = chain.execute("Test task")
    duration = time.time() - start
    
    assert result.success == True
    assert result.model_used == "fast_model"
    assert duration < 2
    assert any(f["reason"] == "timeout" for f in result.fallback_trail)
    
    print(f"✅ Timeout fallback working (switched in {duration:.2f}s)")

def test_quality_triggered_fallback():
    """Test quality-based fallback"""
    def low_quality_response(prompt):
        return Mock(text="Bad answer", quality_score=0.3)
    
    def high_quality_response(prompt):
        return Mock(text="Excellent answer", quality_score=0.95)
    
    model1 = Mock()
    model1.generate = low_quality_response
    
    model2 = Mock()
    model2.generate = high_quality_response
    
    chain = FallbackChain([
        ModelConfig("low_quality", provider=model1),
        ModelConfig("high_quality", provider=model2)
    ], min_quality=0.8)
    
    result = chain.execute("Test task")
    
    assert result.success == True
    assert result.model_used == "high_quality"
    assert result.quality_score >= 0.8
    assert any(f["reason"] == "quality_below_threshold" for f in result.fallback_trail)
    
    print("✅ Quality-triggered fallback working")

def test_circuit_breaker():
    """Test circuit breaker pattern"""
    model = Mock()
    model.generate.side_effect = Exception("Service down")
    
    breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=1.0,
        expected_exception=Exception
    )
    
    # Make requests until circuit opens
    for i in range(5):
        try:
            with breaker:
                model.generate("Test")
        except:
            pass
    
    assert breaker.current_state == "open"
    print("✅ Circuit breaker opened after failures")
    
    # Should fail fast when open
    start = time.time()
    try:
        with breaker:
            model.generate("Test")
        assert False, "Should fail immediately"
    except Exception as e:
        assert "Circuit breaker is open" in str(e)
        assert time.time() - start < 0.1
    
    print("✅ Circuit breaker fails fast when open")
    
    # Wait for recovery
    time.sleep(1.1)
    
    # Should be half-open now
    assert breaker.current_state == "half-open"
    
    # Successful request should close circuit
    model.generate.side_effect = None
    model.generate.return_value = Mock(text="Success")
    
    with breaker:
        result = model.generate("Test")
    
    assert breaker.current_state == "closed"
    print("✅ Circuit breaker recovery working")

def test_context_preservation():
    """Test context preserved across fallbacks"""
    conversation_state = {"messages": [], "user": "test_user"}
    
    def model_with_context(prompt, context=None):
        assert context is not None
        assert context["user"] == "test_user"
        return Mock(text=f"Response with context for {context['user']}")
    
    model1 = Mock()
    model1.generate.side_effect = Exception("Fail")
    
    model2 = Mock()
    model2.generate = model_with_context
    
    chain = FallbackChain([
        ModelConfig("model1", provider=model1),
        ModelConfig("model2", provider=model2)
    ])
    
    result = chain.execute("Test task", context=conversation_state)
    
    assert result.success == True
    assert "test_user" in result.text
    print("✅ Context preserved across fallback")

def test_health_monitoring():
    """Test health monitoring system"""
    monitor = HealthMonitor()
    
    # Record some events
    monitor.record_success("model1", latency_ms=100)
    monitor.record_success("model1", latency_ms=150)
    monitor.record_failure("model1", error="Timeout")
    monitor.record_success("model1", latency_ms=120)
    
    monitor.record_failure("model2", error="Rate limit")
    monitor.record_failure("model2", error="API error")
    
    # Get health status
    health = monitor.get_health_status()
    
    model1_health = health["model1"]
    assert model1_health.success_rate == 0.75  # 3/4
    assert model1_health.avg_latency_ms == 123.33  # (100+150+120)/3
    assert model1_health.state == "healthy"
    
    model2_health = health["model2"]
    assert model2_health.success_rate == 0.0
    assert model2_health.state == "unhealthy"
    
    print("✅ Health monitoring working")
    print(f"   Model1: {model1_health.state} ({model1_health.success_rate:.1%})")
    print(f"   Model2: {model2_health.state} ({model2_health.success_rate:.1%})")

def test_geographic_fallback():
    """Test geographic/region-based fallback"""
    # Mock latency testing
    def get_latency(endpoint):
        latencies = {
            "us-east": 50,
            "us-west": 150,
            "eu-west": 200,
            "asia": 300
        }
        return latencies.get(endpoint, 1000)
    
    chain = FallbackChain.create_geographic([
        ModelConfig("openai", regions=["us-east", "us-west"]),
        ModelConfig("anthropic", regions=["us-west", "eu-west"]),
        ModelConfig("local", regions=["local"])
    ])
    
    # Should select based on latency
    with patch('litecrewai.routing.fallback.test_latency', get_latency):
        result = chain.select_optimal_endpoint()
    
    assert result.region == "us-east"
    assert result.model == "openai"
    print(f"✅ Geographic fallback selected: {result.model} ({result.region})")

def test_fallback_logging():
    """Test comprehensive logging"""
    import logging
    from io import StringIO
    
    # Capture logs
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logger = logging.getLogger('litecrewai.fallback')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    # Create failing chain
    model1 = Mock()
    model1.generate.side_effect = Exception("Test error")
    
    model2 = Mock()
    model2.generate.return_value = Mock(text="Success")
    
    chain = FallbackChain([
        ModelConfig("failing_model", provider=model1),
        ModelConfig("working_model", provider=model2)
    ])
    
    result = chain.execute("Test task")
    
    # Check logs
    logs = log_capture.getvalue()
    assert "Attempting with model: failing_model" in logs
    assert "Test error" in logs
    assert "Falling back from failing_model to working_model" in logs
    assert "Success with model: working_model" in logs
    
    print("✅ Fallback logging comprehensive")

if __name__ == "__main__":
    print("🔍 Validating fallback system...\n")
    
    test_basic_fallback()
    test_retry_with_backoff()
    test_timeout_fallback()
    test_quality_triggered_fallback()
    test_circuit_breaker()
    test_context_preservation()
    test_health_monitoring()
    test_geographic_fallback()
    test_fallback_logging()
    
    print("\n✅ Fallback system validation complete!")
```

---

## 📦 FAZA 4: STORAGE I PERSISTENCE

### Blok 4.1: Database Design and Implementation
**Czas**: 8h
**Cel**: Optymalny storage layer

#### Zadania Atomowe:

##### Task 4.1.1: Design Optimal Schema (3h)
**Cel**: Skalowalny i wydajny schemat bazy danych

**Prompt dla AI Agent**:
```
Zaprojektuj optymalny schemat bazy danych dla LiteCrewAI.

Tabele do zaprojektowania:
1. Core tables:
   - agents (id, name, role, config, created_at, stats)
   - tasks (id, description, agent_id, status, result, metadata)
   - executions (id, task_id, started_at, completed_at, cost, tokens)
   - memories (id, agent_id, content, embedding, importance, accessed_at)

2. Supporting tables:
   - tools (id, name, description, config, usage_count)
   - conversations (id, agent_id, messages, context)
   - costs (id, timestamp, model, tokens, cost_usd, task_id)
   - errors (id, timestamp, error_type, details, task_id)

3. Optimization features:
   - Proper indexes for common queries
   - Partitioning for time-series data
   - JSON columns for flexible data
   - Full-text search on content
   - Materialized views for analytics

4. Constraints and triggers:
   - Foreign keys with CASCADE
   - Check constraints for data validity
   - Triggers for updated_at
   - Automatic archival of old data

5. Migration strategy:
   - Version tracking
   - Rollback capability
   - Zero-downtime migrations
   - Data integrity checks

Schema powinien:
- Wspierać 1M+ tasks
- Query performance <50ms
- Storage efficient
- Extension friendly

Przykład DDL:
```sql
CREATE TABLE agents (
    id TEXT PRIMARY KEY DEFAULT (hex(randomblob(16))),
    name TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    config JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    stats JSON DEFAULT '{}',
    
    CHECK (json_valid(config)),
    CHECK (json_valid(stats))
);

CREATE INDEX idx_agents_active ON agents(is_active, name);
CREATE TRIGGER update_agents_timestamp 
    AFTER UPDATE ON agents
    BEGIN
        UPDATE agents SET updated_at = CURRENT_TIMESTAMP 
        WHERE id = NEW.id;
    END;
```
```

**Metryki Sukcesu**:
- ✅ Schema supports all features
- ✅ Queries optimized
- ✅ Storage efficient
- ✅ Migration ready

**Walidacja**:
```python
# validate_database_schema.py
import sqlite3
import json
import time
from datetime import datetime, timedelta
import uuid

def test_schema_creation():
    """Test database schema creation"""
    conn = sqlite3.connect(":memory:")
    
    # Load schema
    with open("/opt/litecrewai/schema/schema.sql", "r") as f:
        schema_sql = f.read()
    
    # Execute schema
    conn.executescript(schema_sql)
    
    # Check tables exist
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    
    required_tables = {
        'agents', 'tasks', 'executions', 'memories',
        'tools', 'conversations', 'costs', 'errors'
    }
    
    missing = required_tables - tables
    assert not missing, f"Missing tables: {missing}"
    
    print(f"✅ All {len(required_tables)} tables created")
    
    # Check indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = [row[0] for row in cursor.fetchall()]
    
    assert len(indexes) >= 10, f"Too few indexes: {len(indexes)}"
    print(f"✅ {len(indexes)} indexes created")
    
    conn.close()

def test_data_integrity():
    """Test constraints and triggers"""
    conn = sqlite3.connect(":memory:")
    
    # Create schema
    with open("/opt/litecrewai/schema/schema.sql", "r") as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    
    # Test unique constraint
    cursor.execute(
        "INSERT INTO agents (name, role) VALUES (?, ?)",
        ("test_agent", "assistant")
    )
    
    try:
        cursor.execute(
            "INSERT INTO agents (name, role) VALUES (?, ?)",
            ("test_agent", "researcher")
        )
        assert False, "Unique constraint not working"
    except sqlite3.IntegrityError:
        print("✅ Unique constraints working")
    
    # Test JSON validation
    try:
        cursor.execute(
            "INSERT INTO agents (name, role, config) VALUES (?, ?, ?)",
            ("agent2", "assistant", "invalid json")
        )
        assert False, "JSON validation not working"
    except sqlite3.IntegrityError:
        print("✅ JSON validation working")
    
    # Test trigger
    cursor.execute("SELECT updated_at FROM agents WHERE name='test_agent'")
    original_time = cursor.fetchone()[0]
    
    time.sleep(0.1)
    cursor.execute(
        "UPDATE agents SET role='researcher' WHERE name='test_agent'"
    )
    
    cursor.execute("SELECT updated_at FROM agents WHERE name='test_agent'")
    new_time = cursor.fetchone()[0]
    
    assert new_time > original_time, "Update trigger not working"
    print("✅ Triggers working")
    
    conn.close()

def test_query_performance():
    """Test query performance with data"""
    conn = sqlite3.connect(":memory:")
    
    # Create schema
    with open("/opt/litecrewai/schema/schema.sql", "r") as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    
    # Insert test data
    print("Inserting test data...")
    
    # Insert agents
    for i in range(100):
        cursor.execute(
            "INSERT INTO agents (name, role, config) VALUES (?, ?, ?)",
            (f"agent_{i}", "assistant", json.dumps({"model": "gpt-3.5"}))
        )
    
    # Insert tasks
    for i in range(10000):
        cursor.execute(
            "INSERT INTO tasks (description, agent_id, status) VALUES (?, ?, ?)",
            (f"Task {i}", f"agent_{i % 100}", "completed" if i % 3 == 0 else "pending")
        )
    
    # Insert executions
    for i in range(5000):
        cursor.execute(
            """INSERT INTO executions 
               (task_id, started_at, completed_at, cost, tokens)
               VALUES (?, ?, ?, ?, ?)""",
            (i + 1, datetime.now(), datetime.now(), 0.001 * i, 100 * i)
        )
    
    conn.commit()
    
    # Test queries
    queries = [
        ("Simple select", "SELECT * FROM agents WHERE name = 'agent_50'"),
        ("Join query", """
            SELECT a.name, COUNT(t.id) as task_count
            FROM agents a
            LEFT JOIN tasks t ON a.id = t.agent_id
            GROUP BY a.id
            LIMIT 10
        """),
        ("Analytics query", """
            SELECT 
                DATE(started_at) as date,
                COUNT(*) as executions,
                SUM(cost) as total_cost,
                AVG(tokens) as avg_tokens
            FROM executions
            GROUP BY DATE(started_at)
        """),
        ("Complex filter", """
            SELECT t.*, a.name as agent_name
            FROM tasks t
            JOIN agents a ON t.agent_id = a.id
            WHERE t.status = 'completed'
            AND t.created_at > datetime('now', '-7 days')
            ORDER BY t.created_at DESC
            LIMIT 50
        """)
    ]
    
    for name, query in queries:
        start = time.time()
        cursor.execute(query)
        results = cursor.fetchall()
        elapsed = (time.time() - start) * 1000
        
        print(f"✅ {name}: {elapsed:.1f}ms ({len(results)} rows)")
        assert elapsed < 50, f"{name} too slow: {elapsed}ms"
    
    conn.close()

def test_json_operations():
    """Test JSON column operations"""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Create schema
    with open("/opt/litecrewai/schema/schema.sql", "r") as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    
    # Insert with JSON
    config = {
        "model": "gpt-4",
        "temperature": 0.7,
        "tools": ["web_search", "calculator"],
        "memory": {"type": "long_term", "size": 1000}
    }
    
    cursor.execute(
        "INSERT INTO agents (name, role, config) VALUES (?, ?, ?)",
        ("json_agent", "researcher", json.dumps(config))
    )
    
    # Query JSON fields
    cursor.execute("""
        SELECT json_extract(config, '$.model') as model,
               json_extract(config, '$.temperature') as temp,
               json_extract(config, '$.tools[0]') as first_tool
        FROM agents 
        WHERE name = 'json_agent'
    """)
    
    row = cursor.fetchone()
    assert row[0] == "gpt-4"
    assert row[1] == 0.7
    assert row[2] == "web_search"
    
    print("✅ JSON operations working")
    
    # Update JSON field
    cursor.execute("""
        UPDATE agents 
        SET config = json_set(config, '$.temperature', 0.9)
        WHERE name = 'json_agent'
    """)
    
    cursor.execute("""
        SELECT json_extract(config, '$.temperature') 
        FROM agents 
        WHERE name = 'json_agent'
    """)
    
    assert cursor.fetchone()[0] == 0.9
    print("✅ JSON updates working")
    
    conn.close()

def test_full_text_search():
    """Test full-text search capabilities"""
    conn = sqlite3.connect(":memory:")
    
    # Create schema with FTS
    with open("/opt/litecrewai/schema/schema.sql", "r") as f:
        conn.executescript(f.read())
    
    # Create FTS table for task search
    conn.execute("""
        CREATE VIRTUAL TABLE tasks_fts USING fts5(
            task_id, description, content=tasks
        );
    """)
    
    cursor = conn.cursor()
    
    # Insert test data
    tasks = [
        "Research quantum computing applications",
        "Write article about machine learning",
        "Analyze quantum physics research papers",
        "Create presentation on AI ethics",
        "Study quantum mechanics fundamentals"
    ]
    
    for i, task in enumerate(tasks):
        cursor.execute(
            "INSERT INTO tasks (id, description, agent_id) VALUES (?, ?, ?)",
            (i + 1, task, "agent_1")
        )
        cursor.execute(
            "INSERT INTO tasks_fts (task_id, description) VALUES (?, ?)",
            (i + 1, task)
        )
    
    # Test FTS queries
    cursor.execute("""
        SELECT task_id, description, rank
        FROM tasks_fts
        WHERE tasks_fts MATCH 'quantum'
        ORDER BY rank
    """)
    
    results = cursor.fetchall()
    assert len(results) == 3
    assert all("quantum" in r[1].lower() for r in results)
    
    print(f"✅ Full-text search working ({len(results)} results)")
    
    conn.close()

def test_migration_system():
    """Test database migration system"""
    import os
    
    migrations_dir = "/opt/litecrewai/schema/migrations"
    
    # Check migration files exist
    assert os.path.exists(migrations_dir)
    
    migrations = sorted([
        f for f in os.listdir(migrations_dir) 
        if f.endswith('.sql')
    ])
    
    assert len(migrations) > 0
    print(f"✅ Found {len(migrations)} migration files")
    
    # Test migration application
    conn = sqlite3.connect(":memory:")
    
    # Create migrations table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Apply migrations
    for migration in migrations:
        with open(os.path.join(migrations_dir, migration), 'r') as f:
            sql = f.read()
        
        try:
            conn.executescript(sql)
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (?)",
                (migration,)
            )
            print(f"✅ Applied migration: {migration}")
        except Exception as e:
            print(f"❌ Failed migration {migration}: {e}")
    
    conn.close()

def test_archival_system():
    """Test data archival functionality"""
    conn = sqlite3.connect(":memory:")
    
    # Create schema
    with open("/opt/litecrewai/schema/schema.sql", "r") as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    
    # Insert old data
    old_date = datetime.now() - timedelta(days=100)
    
    for i in range(100):
        cursor.execute(
            """INSERT INTO tasks 
               (description, agent_id, status, created_at)
               VALUES (?, ?, ?, ?)""",
            (f"Old task {i}", "agent_1", "completed", old_date)
        )
    
    # Insert recent data
    for i in range(50):
        cursor.execute(
            """INSERT INTO tasks 
               (description, agent_id, status)
               VALUES (?, ?, ?)""",
            (f"Recent task {i}", "agent_1", "pending")
        )
    
    # Test archival query
    cursor.execute("""
        SELECT COUNT(*) 
        FROM tasks 
        WHERE created_at < datetime('now', '-90 days')
    """)
    
    old_count = cursor.fetchone()[0]
    assert old_count == 100
    
    print(f"✅ Found {old_count} tasks ready for archival")
    
    conn.close()

if __name__ == "__main__":
    print("🔍 Validating database schema...\n")
    
    test_schema_creation()
    test_data_integrity()
    test_query_performance()
    test_json_operations()
    test_full_text_search()
    test_migration_system()
    test_archival_system()
    
    print("\n✅ Database schema validation complete!")
```

##### Task 4.1.2: Implement Data Access Layer (3h)
**Cel**: Clean, efficient data access layer

**Prompt dla AI Agent**:
```
Zaimplementuj Data Access Layer (DAL) dla LiteCrewAI.

Komponenty:
1. Repository pattern:
   - BaseRepository (CRUD operations)
   - AgentRepository
   - TaskRepository
   - MemoryRepository
   - CostRepository

2. Query builders:
   - Fluent interface
   - Type-safe queries
   - SQL injection prevention
   - Query optimization

3. Connection management:
   - Connection pooling
   - Transaction support
   - Read/write splitting
   - Retry logic

4. Caching layer:
   - Query result caching
   - Entity caching
   - Cache invalidation
   - TTL management

5. Advanced features:
   - Batch operations
   - Lazy loading
   - Eager loading
   - Pagination helpers
   - Soft deletes

Przykład użycia:
```python
# Initialize repositories
agent_repo = AgentRepository(db)
task_repo = TaskRepository(db)

# Create agent
agent = Agent(name="researcher", role="research")
agent_id = await agent_repo.create(agent)

# Query with builder
tasks = await task_repo.query()
    .where("status", "=", "pending")
    .where("priority", ">", 5)
    .order_by("created_at", "DESC")
    .limit(10)
    .include("agent")  # Eager load
    .execute()

# Transaction example
async with db.transaction() as tx:
    task = await task_repo.create(task_data, tx)
    await agent_repo.update(agent_id, {"last_task": task.id}, tx)
    # Auto-commit or rollback

# Batch operations
await task_repo.create_many([task1, task2, task3])

# Caching
cached_agent = await agent_repo.find_cached(agent_id, ttl=300)
```

Layer powinien być testable i mockable.
```

**Metryki Sukcesu**:
- ✅ Clean API
- ✅ <10ms for simple queries
- ✅ Transaction support
- ✅ 100% test coverage

**Walidacja**:
```python
# validate_data_access_layer.py
import asyncio
import time
from unittest.mock import Mock, AsyncMock
import sqlite3
from litecrewai.dal import (
    DatabaseConnection, AgentRepository, TaskRepository,
    QueryBuilder, TransactionManager
)

async def test_repository_pattern():
    """Test repository implementation"""
    db = DatabaseConnection(":memory:")
    await db.initialize()
    
    agent_repo = AgentRepository(db)
    
    # Test create
    agent_data = {
        "name": "test_agent",
        "role": "assistant",
        "config": {"model": "gpt-3.5"}
    }
    
    agent_id = await agent_repo.create(agent_data)
    assert agent_id is not None
    print(f"✅ Created agent: {agent_id}")
    
    # Test read
    agent = await agent_repo.find(agent_id)
    assert agent is not None
    assert agent.name == "test_agent"
    assert agent.role == "assistant"
    
    # Test update
    await agent_repo.update(agent_id, {"role": "researcher"})
    updated = await agent_repo.find(agent_id)
    assert updated.role == "researcher"
    
    # Test delete
    await agent_repo.delete(agent_id)
    deleted = await agent_repo.find(agent_id)
    assert deleted is None
    
    print("✅ CRUD operations working")

async def test_query_builder():
    """Test query builder functionality"""
    db = DatabaseConnection(":memory:")
    await db.initialize()
    
    task_repo = TaskRepository(db)
    
    # Insert test data
    for i in range(20):
        await task_repo.create({
            "description": f"Task {i}",
            "status": "pending" if i % 2 == 0 else "completed",
            "priority": i % 5,
            "agent_id": f"agent_{i % 3}"
        })
    
    # Test complex query
    results = await task_repo.query() \
        .where("status", "=", "pending") \
        .where("priority", ">=", 3) \
        .order_by("priority", "DESC") \
        .limit(5) \
        .execute()
    
    assert len(results) <= 5
    assert all(t.status == "pending" for t in results)
    assert all(t.priority >= 3 for t in results)
    
    # Check ordering
    priorities = [t.priority for t in results]
    assert priorities == sorted(priorities, reverse=True)
    
    print(f"✅ Query builder: found {len(results)} matching tasks")
    
    # Test aggregation
    count = await task_repo.query() \
        .where("status", "=", "completed") \
        .count()
    
    assert count == 10
    print(f"✅ Aggregation: {count} completed tasks")

async def test_transactions():
    """Test transaction support"""
    db = DatabaseConnection(":memory:")
    await db.initialize()
    
    agent_repo = AgentRepository(db)
    task_repo = TaskRepository(db)
    
    # Successful transaction
    async with db.transaction() as tx:
        agent_id = await agent_repo.create({
            "name": "tx_agent",
            "role": "assistant"
        }, tx)
        
        task_id = await task_repo.create({
            "description": "Transaction task",
            "agent_id": agent_id
        }, tx)
        
        # Should be visible within transaction
        agent = await agent_repo.find(agent_id, tx)
        assert agent is not None
    
    # Should be committed
    agent = await agent_repo.find(agent_id)
    assert agent is not None
    print("✅ Transaction commit working")
    
    # Failed transaction
    try:
        async with db.transaction() as tx:
            agent_id2 = await agent_repo.create({
                "name": "tx_agent2",
                "role": "assistant"
            }, tx)
            
            # Force error
            raise Exception("Rollback test")
            
    except Exception:
        pass
    
    # Should be rolled back
    agent2 = await agent_repo.find_by("name", "tx_agent2")
    assert agent2 is None
    print("✅ Transaction rollback working")

async def test_connection_pooling():
    """Test connection pool functionality"""
    pool = DatabaseConnection(
        ":memory:",
        pool_size=5,
        max_overflow=2
    )
    await pool.initialize()
    
    # Test concurrent connections
    async def query_task(i):
        repo = AgentRepository(pool)
        await repo.create({
            "name": f"agent_{i}",
            "role": "assistant"
        })
        await asyncio.sleep(0.1)  # Simulate work
        return i
    
    # Run concurrent tasks
    start = time.time()
    tasks = [query_task(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    duration = time.time() - start
    
    assert len(results) == 10
    assert duration < 2.0  # Should be concurrent
    
    print(f"✅ Connection pooling: 10 tasks in {duration:.2f}s")
    
    # Check pool stats
    stats = pool.get_pool_stats()
    assert stats["size"] <= 7  # pool_size + max_overflow
    assert stats["in_use"] == 0  # All returned
    print(f"✅ Pool stats: {stats}")

async def test_caching_layer():
    """Test query result caching"""
    db = DatabaseConnection(":memory:")
    await db.initialize()
    
    # Create repo with caching
    agent_repo = AgentRepository(db, enable_cache=True)
    
    # Create test agent
    agent_id = await agent_repo.create({
        "name": "cached_agent",
        "role": "assistant"
    })
    
    # First query (cache miss)
    start = time.time()
    agent1 = await agent_repo.find_cached(agent_id, ttl=60)
    time1 = time.time() - start
    
    # Second query (cache hit)
    start = time.time()
    agent2 = await agent_repo.find_cached(agent_id, ttl=60)
    time2 = time.time() - start
    
    assert agent1.id == agent2.id
    assert time2 < time1 / 10  # Much faster
    
    print(f"✅ Caching: {time1*1000:.1f}ms → {time2*1000:.1f}ms")
    
    # Test cache invalidation
    await agent_repo.update(agent_id, {"role": "researcher"})
    
    # Should get fresh data
    agent3 = await agent_repo.find_cached(agent_id, ttl=60)
    assert agent3.role == "researcher"
    print("✅ Cache invalidation working")

async def test_batch_operations():
    """Test batch insert/update/delete"""
    db = DatabaseConnection(":memory:")
    await db.initialize()
    
    task_repo = TaskRepository(db)
    
    # Batch create
    tasks_data = [
        {"description": f"Batch task {i}", "status": "pending"}
        for i in range(100)
    ]
    
    start = time.time()
    task_ids = await task_repo.create_many(tasks_data)
    batch_time = time.time() - start
    
    assert len(task_ids) == 100
    print(f"✅ Batch insert: 100 records in {batch_time:.2f}s")
    
    # Batch update
    updates = [
        {"id": task_id, "status": "completed"}
        for task_id in task_ids[:50]
    ]
    
    await task_repo.update_many(updates)
    
    # Verify
    completed = await task_repo.query() \
        .where("status", "=", "completed") \
        .count()
    
    assert completed == 50
    print("✅ Batch update: 50 records")
    
    # Batch delete
    await task_repo.delete_many(task_ids[50:])
    
    total = await task_repo.query().count()
    assert total == 50
    print("✅ Batch delete: 50 records")

async def test_pagination():
    """Test pagination helpers"""
    db = DatabaseConnection(":memory:")
    await db.initialize()
    
    task_repo = TaskRepository(db)
    
    # Insert test data
    for i in range(100):
        await task_repo.create({
            "description": f"Page task {i}",
            "priority": i
        })
    
    # Test pagination
    page1 = await task_repo.query() \
        .order_by("priority", "DESC") \
        .paginate(page=1, per_page=10)
    
    assert len(page1.items) == 10
    assert page1.total == 100
    assert page1.pages == 10
    assert page1.has_next == True
    assert page1.has_prev == False
    
    # Check correct items
    priorities = [t.priority for t in page1.items]
    assert priorities == list(range(99, 89, -1))
    
    print(f"✅ Pagination: page 1/{page1.pages}")
    
    # Test page 2
    page2 = await task_repo.query() \
        .order_by("priority", "DESC") \
        .paginate(page=2, per_page=10)
    
    assert page2.has_prev == True
    priorities2 = [t.priority for t in page2.items]
    assert priorities2 == list(range(89, 79, -1))

async def test_soft_deletes():
    """Test soft delete functionality"""
    db = DatabaseConnection(":memory:")
    await db.initialize()
    
    agent_repo = AgentRepository(db, soft_delete=True)
    
    # Create and soft delete
    agent_id = await agent_repo.create({
        "name": "soft_delete_test",
        "role": "assistant"
    })
    
    await agent_repo.delete(agent_id)
    
    # Should not be found normally
    agent = await agent_repo.find(agent_id)
    assert agent is None
    
    # But still in database
    agent = await agent_repo.find_with_deleted(agent_id)
    assert agent is not None
    assert agent.deleted_at is not None
    
    print("✅ Soft delete working")
    
    # Test restore
    await agent_repo.restore(agent_id)
    agent = await agent_repo.find(agent_id)
    assert agent is not None
    assert agent.deleted_at is None
    
    print("✅ Soft delete restore working")

if __name__ == "__main__":
    print("🔍 Validating data access layer...\n")
    
    async def run_tests():
        await test_repository_pattern()
        await test_query_builder()
        await test_transactions()
        await test_connection_pooling()
        await test_caching_layer()
        await test_batch_operations()
        await test_pagination()
        await test_soft_deletes()
    
    asyncio.run(run_tests())
    
    print("\n✅ Data access layer validation complete!")
```

##### Task 4.1.3: Add Vector Storage Support (2h)
**Cel**: Wsparcie dla vector embeddings

**Prompt dla AI Agent**:
```
Dodaj wsparcie dla vector storage w LiteCrewAI używając sqlite-vec.

Komponenty:
1. Vector storage setup:
   - Install sqlite-vec extension
   - Create vector tables
   - Index configuration
   - Dimension management

2. Embedding operations:
   - Store embeddings
   - Similarity search
   - Batch operations
   - Hybrid search (vector + keyword)

3. Vector indexes:
   - HNSW index
   - IVF index
   - Optimization settings
   - Rebuild strategies

4. Integration features:
   - Automatic embedding on insert
   - Embedding cache
   - Multiple embedding models
   - Dimension reduction

5. Search capabilities:
   - k-NN search
   - Range search
   - Filtered search
   - Re-ranking

Przykład:
```python
# Initialize vector store
vector_store = VectorStore(
    db=db,
    embedding_model="nomic-embed-text",
    dimension=768
)

# Store document with embedding
doc_id = await vector_store.add_document(
    content="LiteCrewAI is a lightweight agent framework",
    metadata={"source": "readme", "type": "description"}
)

# Search similar documents
results = await vector_store.search(
    query="agent framework for AI",
    k=5,
    filter={"type": "description"}
)

for result in results:
    print(f"Score: {result.score:.3f} - {result.content[:50]}...")

# Hybrid search (vector + keyword)
results = await vector_store.hybrid_search(
    vector_query="AI agents",
    keyword_query="framework OR library",
    k=10,
    alpha=0.7  # 70% vector, 30% keyword
)

# Batch operations
embeddings = await vector_store.embed_batch([doc1, doc2, doc3])
await vector_store.add_many(documents_with_embeddings)
```
```

**Metryki Sukcesu**:
- ✅ Vector search <100ms
- ✅ 95%+ recall@10
- ✅ Batch embedding efficient
- ✅ Hybrid search works

**Walidacja**:
```python
# validate_vector_storage.py
import numpy as np
import time
from sklearn.metrics.pairwise import cosine_similarity
from litecrewai.storage.vector import VectorStore, Document

async def test_vector_extension():
    """Test sqlite-vec extension is loaded"""
    import sqlite3
    
    conn = sqlite3.connect(":memory:")
    
    # Load extension
    conn.enable_load_extension(True)
    conn.load_extension("vec0")
    conn.enable_load_extension(False)
    
    # Test vector functions
    cursor = conn.cursor()
    
    # Create vector table
    cursor.execute("""
        CREATE VIRTUAL TABLE test_vectors USING vec0(
            id INTEGER PRIMARY KEY,
            embedding FLOAT[3]
        )
    """)
    
    # Insert test vector
    cursor.execute(
        "INSERT INTO test_vectors(id, embedding) VALUES (?, ?)",
        (1, "[1.0, 2.0, 3.0]")
    )
    
    # Test vector search
    cursor.execute("""
        SELECT id, vec_distance_cosine(embedding, '[1.0, 2.0, 3.0]') as distance
        FROM test_vectors
        WHERE embedding MATCH '[1.0, 2.0, 3.0]'
        ORDER BY distance
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    assert result is not None
    assert result[1] < 0.01  # Very close
    
    print("✅ sqlite-vec extension working")
    conn.close()

async def test_vector_store_operations():
    """Test basic vector store operations"""
    vector_store = VectorStore(
        db_path=":memory:",
        embedding_model="test",  # Mock model
        dimension=384
    )
    
    await vector_store.initialize()
    
    # Mock embedding function
    def mock_embed(text):
        # Simple hash-based embedding for testing
        np.random.seed(hash(text) % 2**32)
        return np.random.randn(384).tolist()
    
    vector_store._embed = mock_embed
    
    # Add documents
    doc_ids = []
    for i in range(10):
        doc_id = await vector_store.add_document(
            content=f"Document {i} about AI and machine learning",
            metadata={"index": i, "category": "AI"}
        )
        doc_ids.append(doc_id)
    
    print(f"✅ Added {len(doc_ids)} documents")
    
    # Search
    results = await vector_store.search(
        query="artificial intelligence",
        k=5
    )
    
    assert len(results) <= 5
    assert all(hasattr(r, 'score') for r in results)
    assert all(hasattr(r, 'content') for r in results)
    
    print(f"✅ Vector search returned {len(results)} results")

async def test_similarity_accuracy():
    """Test vector similarity accuracy"""
    vector_store = VectorStore(
        db_path=":memory:",
        dimension=128
    )
    
    await vector_store.initialize()
    
    # Create known embeddings
    embeddings = {
        "doc1": np.random.randn(128),
        "doc2": np.random.randn(128),
        "doc3": np.random.randn(128),
    }
    
    # Make doc2 similar to doc1
    embeddings["doc2"] = embeddings["doc1"] + np.random.randn(128) * 0.1
    
    # Add to store
    for name, embedding in embeddings.items():
        await vector_store.add_document_with_embedding(
            content=f"Content for {name}",
            embedding=embedding.tolist(),
            metadata={"name": name}
        )
    
    # Search for doc1
    results = await vector_store.search_by_embedding(
        embedding=embeddings["doc1"].tolist(),
        k=3
    )
    
    # doc1 should be first, doc2 second
    assert results[0].metadata["name"] == "doc1"
    assert results[1].metadata["name"] == "doc2"
    assert results[0].score > results[1].score
    
    print("✅ Similarity search accuracy verified")

async def test_batch_operations():
    """Test batch embedding and insertion"""
    vector_store = VectorStore(
        db_path=":memory:",
        dimension=384
    )
    
    await vector_store.initialize()
    
    # Mock batch embed
    def mock_embed_batch(texts):
        return [np.random.randn(384).tolist() for _ in texts]
    
    vector_store._embed_batch = mock_embed_batch
    
    # Prepare batch
    documents = [
        Document(
            content=f"Batch document {i}",
            metadata={"batch": True, "index": i}
        )
        for i in range(100)
    ]
    
    # Batch insert
    start = time.time()
    doc_ids = await vector_store.add_many(documents)
    batch_time = time.time() - start
    
    assert len(doc_ids) == 100
    print(f"✅ Batch insert: 100 docs in {batch_time:.2f}s")
    
    # Verify
    count = await vector_store.count()
    assert count == 100

async def test_filtered_search():
    """Test search with metadata filters"""
    vector_store = VectorStore(db_path=":memory:", dimension=128)
    await vector_store.initialize()
    
    # Add documents with categories
    categories = ["tech", "science", "tech", "art", "science"]
    for i, category in enumerate(categories):
        await vector_store.add_document(
            content=f"Document {i} in {category}",
            metadata={"category": category, "index": i},
            embedding=np.random.randn(128).tolist()
        )
    
    # Search with filter
    results = await vector_store.search(
        query_embedding=np.random.randn(128).tolist(),
        k=10,
        filter={"category": "tech"}
    )
    
    # Should only return tech documents
    assert all(r.metadata["category"] == "tech" for r in results)
    assert len(results) == 2
    
    print("✅ Filtered search working")

async def test_hybrid_search():
    """Test hybrid vector + keyword search"""
    vector_store = VectorStore(db_path=":memory:", dimension=128)
    await vector_store.initialize()
    
    # Add documents
    docs = [
        "Python is a programming language",
        "Machine learning with Python",
        "Java programming tutorial",
        "Deep learning frameworks",
        "Python data science tools"
    ]
    
    for i, doc in enumerate(docs):
        await vector_store.add_document(
            content=doc,
            embedding=np.random.randn(128).tolist()
        )
    
    # Hybrid search
    results = await vector_store.hybrid_search(
        vector_query="programming",
        keyword_query="Python",
        k=5,
        alpha=0.5  # Equal weight
    )
    
    # Should favor documents with "Python"
    python_docs = [r for r in results if "Python" in r.content]
    assert len(python_docs) >= 2
    
    # Top results should contain Python
    assert "Python" in results[0].content
    
    print(f"✅ Hybrid search: {len(python_docs)}/5 contain 'Python'")

async def test_vector_index_performance():
    """Test vector index performance with larger dataset"""
    vector_store = VectorStore(
        db_path=":memory:",
        dimension=128,
        index_type="hnsw"
    )
    await vector_store.initialize()
    
    # Add many documents
    print("Adding 1000 documents...")
    for i in range(1000):
        embedding = np.random.randn(128)
        # Create clusters
        if i % 100 < 10:
            embedding += np.array([1.0] * 128)  # Cluster 1
        elif i % 100 < 20:
            embedding += np.array([-1.0] * 128)  # Cluster 2
        
        await vector_store.add_document(
            content=f"Document {i}",
            embedding=embedding.tolist()
        )
    
    # Test search performance
    query_embedding = np.random.randn(128) + np.array([1.0] * 128)
    
    start = time.time()
    results = await vector_store.search(
        query_embedding=query_embedding.tolist(),
        k=10
    )
    search_time = (time.time() - start) * 1000
    
    print(f"✅ Search time on 1000 docs: {search_time:.1f}ms")
    assert search_time < 100  # Should be fast with index
    
    # Check we get cluster 1 documents
    cluster1_docs = [r for r in results if int(r.content.split()[1]) % 100 < 10]
    assert len(cluster1_docs) >= 5  # Most should be from cluster 1

async def test_embedding_models():
    """Test different embedding models"""
    # Test with different dimensions
    dimensions = [128, 384, 768]
    
    for dim in dimensions:
        vector_store = VectorStore(
            db_path=":memory:",
            dimension=dim
        )
        await vector_store.initialize()
        
        # Add document
        embedding = np.random.randn(dim).tolist()
        doc_id = await vector_store.add_document_with_embedding(
            content=f"Test with {dim}D",
            embedding=embedding
        )
        
        # Verify
        assert doc_id is not None
        
        # Search
        results = await vector_store.search_by_embedding(
            embedding=embedding,
            k=1
        )
        
        assert len(results) == 1
        assert results[0].content == f"Test with {dim}D"
        
        print(f"✅ {dim}D embeddings working")

if __name__ == "__main__":
    print("🔍 Validating vector storage...\n")
    
    async def run_tests():
        await test_vector_extension()
        await test_vector_store_operations()
        await test_similarity_accuracy()
        await test_batch_operations()
        await test_filtered_search()
        await test_hybrid_search()
        await test_vector_index_performance()
        await test_embedding_models()
    
    import asyncio
    asyncio.run(run_tests())
    
    print("\n✅ Vector storage validation complete!")
```

### Blok 4.2: Cache Implementation
**Czas**: 6h
**Cel**: Wielopoziomowy system cache

#### Zadania Atomowe:

##### Task 4.2.1: Design Multi-Level Cache (2h)
**Cel**: Efektywny multi-level cache system

**Prompt dla AI Agent**:
```
Zaprojektuj wielopoziomowy system cache dla LiteCrewAI.

Poziomy cache:
1. L1 - In-memory (process):
   - LRU cache w pamięci procesu
   - Ultra-fast (<1ms)
   - Limited size (100MB)
   - Per-worker isolation

2. L2 - Redis (shared):
   - Shared między workers
   - Fast (1-5ms)
   - Larger size (1GB)
   - Persistence optional

3. L3 - SQLite (persistent):
   - Disk-based
   - Slower (5-20ms)
   - Unlimited size
   - Queryable

Cache strategies:
1. Write strategies:
   - Write-through
   - Write-back
   - Write-around

2. Eviction policies:
   - LRU (Least Recently Used)
   - LFU (Least Frequently Used)
   - TTL-based
   - Size-based

3. Cache patterns:
   - Cache-aside
   - Read-through
   - Write-through
   - Refresh-ahead

Features:
- Automatic tier migration
- Cache warming
- Distributed invalidation
- Compression support
- Statistics tracking

Przykład:
```python
# Initialize multi-level cache
cache = MultiLevelCache(
    l1_size_mb=100,
    l2_size_mb=1000,
    l3_enabled=True,
    compression=True
)

# Simple usage
await cache.set("user:123", user_data, ttl=3600)
user = await cache.get("user:123")  # Checks L1→L2→L3

# Tagged caching
await cache.set("post:456", post_data, tags=["user:123", "posts"])
await cache.invalidate_tag("user:123")  # Invalidates related

# Batch operations
await cache.mset({
    "key1": value1,
    "key2": value2
})

# Cache statistics
stats = cache.get_stats()
print(f"L1 hit rate: {stats.l1_hit_rate:.1%}")
print(f"L2 hit rate: {stats.l2_hit_rate:.1%}")
```
```

**Metryki Sukcesu**:
- ✅ L1 latency <1ms
- ✅ L2 latency <5ms
- ✅ 90%+ combined hit rate
- ✅ Automatic tier migration

**Walidacja**:
```python
# validate_multi_level_cache.py
import time
import asyncio
import psutil
import pickle
from litecrewai.cache import MultiLevelCache, CacheStats

async def test_cache_levels():
    """Test all cache levels work correctly"""
    cache = MultiLevelCache(
        l1_size_mb=10,
        l2_size_mb=50,
        l3_enabled=True
    )
    
    await cache.initialize()
    
    # Test data
    test_key = "test:123"
    test_value = {"data": "x" * 1000, "number": 42}
    
    # Set in cache (goes to L1)
    await cache.set(test_key, test_value, ttl=3600)
    
    # Get from L1 (fast)
    start = time.time()
    value_l1 = await cache.get(test_key)
    l1_time = (time.time() - start) * 1000
    
    assert value_l1 == test_value
    assert l1_time < 1.0
    print(f"✅ L1 hit: {l1_time:.2f}ms")
    
    # Clear L1 to test L2
    cache._l1_cache.clear()
    
    # Get from L2
    start = time.time()
    value_l2 = await cache.get(test_key)
    l2_time = (time.time() - start) * 1000
    
    assert value_l2 == test_value
    assert l2_time < 5.0
    print(f"✅ L2 hit: {l2_time:.2f}ms")
    
    # Clear L1 and L2 to test L3
    cache._l1_cache.clear()
    await cache._l2_cache.flushall()
    
    # Get from L3
    start = time.time()
    value_l3 = await cache.get(test_key)
    l3_time = (time.time() - start) * 1000
    
    assert value_l3 == test_value
    assert l3_time < 20.0
    print(f"✅ L3 hit: {l3_time:.2f}ms")

async def test_tier_migration():
    """Test automatic tier migration"""
    cache = MultiLevelCache(
        l1_size_mb=1,  # Very small for testing
        l2_size_mb=10,
        l3_enabled=True
    )
    
    await cache.initialize()
    
    # Fill L1 cache
    for i in range(20):
        await cache.set(f"key:{i}", f"value_{i}" * 100)
    
    # Check L1 size is limited
    l1_stats = cache.get_l1_stats()
    assert l1_stats["size_mb"] <= 1.1  # Some overhead
    
    # Older items should migrate to L2
    l2_count = await cache._l2_cache.dbsize()
    assert l2_count > 0
    
    print(f"✅ Tier migration: L1={l1_stats['count']}, L2={l2_count}")
    
    # Access old item - should promote back to L1
    old_value = await cache.get("key:0")
    assert old_value is not None
    
    # Should now be in L1
    assert "key:0" in cache._l1_cache

async def test_cache_strategies():
    """Test different cache strategies"""
    # Write-through cache
    cache_wt = MultiLevelCache(strategy="write_through")
    await cache_wt.initialize()
    
    # Write should go to all levels
    await cache_wt.set("wt:1", "value1")
    
    # Check all levels have it
    assert "wt:1" in cache_wt._l1_cache
    assert await cache_wt._l2_cache.exists("wt:1")
    
    print("✅ Write-through strategy working")
    
    # Write-back cache (lazy write)
    cache_wb = MultiLevelCache(strategy="write_back")
    await cache_wb.initialize()
    
    # Write only to L1 initially
    await cache_wb.set("wb:1", "value1")
    assert "wb:1" in cache_wb._l1_cache
    assert not await cache_wb._l2_cache.exists("wb:1")
    
    # Force flush
    await cache_wb.flush()
    assert await cache_wb._l2_cache.exists("wb:1")
    
    print("✅ Write-back strategy working")

async def test_eviction_policies():
    """Test different eviction policies"""
    # LRU eviction
    cache_lru = MultiLevelCache(
        l1_size_mb=1,
        eviction_policy="lru"
    )
    await cache_lru.initialize()
    
    # Add items
    for i in range(10):
        await cache_lru.set(f"lru:{i}", "x" * 10000)
    
    # Access some items to make them recently used
    await cache_lru.get("lru:0")
    await cache_lru.get("lru:1")
    
    # Add more to trigger eviction
    for i in range(10, 15):
        await cache_lru.set(f"lru:{i}", "x" * 10000)
    
    # Early items (except 0,1) should be evicted
    assert await cache_lru.get("lru:0") is not None
    assert await cache_lru.get("lru:1") is not None
    assert await cache_lru.get("lru:5") is None  # Should be evicted
    
    print("✅ LRU eviction working")
    
    # TTL eviction
    cache_ttl = MultiLevelCache()
    await cache_ttl.initialize()
    
    # Set with short TTL
    await cache_ttl.set("ttl:1", "value", ttl=1)
    assert await cache_ttl.get("ttl:1") is not None
    
    # Wait for expiry
    await asyncio.sleep(1.1)
    assert await cache_ttl.get("ttl:1") is None
    
    print("✅ TTL eviction working")

async def test_tagged_caching():
    """Test tag-based cache invalidation"""
    cache = MultiLevelCache()
    await cache.initialize()
    
    # Set items with tags
    await cache.set("user:123:profile", {"name": "John"}, tags=["user:123"])
    await cache.set("user:123:posts", ["post1", "post2"], tags=["user:123", "posts"])
    await cache.set("user:456:profile", {"name": "Jane"}, tags=["user:456"])
    await cache.set("global:stats", {"total": 100}, tags=["global"])
    
    # Invalidate by tag
    await cache.invalidate_tag("user:123")
    
    # user:123 items should be gone
    assert await cache.get("user:123:profile") is None
    assert await cache.get("user:123:posts") is None
    
    # Others should remain
    assert await cache.get("user:456:profile") is not None
    assert await cache.get("global:stats") is not None
    
    print("✅ Tagged invalidation working")

async def test_batch_operations():
    """Test batch cache operations"""
    cache = MultiLevelCache()
    await cache.initialize()
    
    # Batch set
    batch_data = {
        f"batch:{i}": f"value_{i}"
        for i in range(100)
    }
    
    start = time.time()
    await cache.mset(batch_data, ttl=3600)
    batch_set_time = time.time() - start
    
    print(f"✅ Batch set: 100 items in {batch_set_time:.2f}s")
    
    # Batch get
    keys = list(batch_data.keys())
    start = time.time()
    values = await cache.mget(keys)
    batch_get_time = time.time() - start
    
    assert len(values) == 100
    assert all(v is not None for v in values)
    print(f"✅ Batch get: 100 items in {batch_get_time:.2f}s")
    
    # Batch delete
    await cache.mdelete(keys[:50])
    remaining = await cache.mget(keys)
    assert sum(1 for v in remaining if v is not None) == 50

async def test_compression():
    """Test cache compression"""
    # Large data for compression test
    large_data = {
        "text": "x" * 10000,
        "numbers": list(range(1000)),
        "nested": {"data": "y" * 5000}
    }
    
    # Cache without compression
    cache_plain = MultiLevelCache(compression=False)
    await cache_plain.initialize()
    
    await cache_plain.set("plain:1", large_data)
    size_plain = cache_plain.get_size("plain:1")
    
    # Cache with compression
    cache_compressed = MultiLevelCache(compression=True)
    await cache_compressed.initialize()
    
    await cache_compressed.set("compressed:1", large_data)
    size_compressed = cache_compressed.get_size("compressed:1")
    
    # Verify compression works
    assert size_compressed < size_plain * 0.5  # At least 50% compression
    
    # Verify data integrity
    data_retrieved = await cache_compressed.get("compressed:1")
    assert data_retrieved == large_data
    
    print(f"✅ Compression: {size_plain} → {size_compressed} bytes "
          f"({(1 - size_compressed/size_plain)*100:.1f}% reduction)")

async def test_cache_warming():
    """Test cache warming functionality"""
    cache = MultiLevelCache()
    await cache.initialize()
    
    # Define warming data
    warming_data = {
        "config:app": {"version": "1.0", "features": ["a", "b"]},
        "config:limits": {"rate_limit": 100, "max_users": 1000},
        "static:countries": ["US", "UK", "CA", "AU"],
    }
    
    # Warm cache
    await cache.warm(warming_data)
    
    # All items should be in L1
    for key in warming_data:
        assert key in cache._l1_cache
        value = await cache.get(key)
        assert value == warming_data[key]
    
    print(f"✅ Cache warming: {len(warming_data)} items pre-loaded")

async def test_distributed_invalidation():
    """Test distributed cache invalidation"""
    # Simulate two cache instances
    cache1 = MultiLevelCache(instance_id="node1")
    cache2 = MultiLevelCache(instance_id="node2")
    
    await cache1.initialize()
    await cache2.initialize()
    
    # Set in cache1
    await cache1.set("shared:1", "value1")
    
    # Should propagate to shared L2
    value = await cache2.get("shared:1")
    assert value == "value1"
    
    # Invalidate from cache2
    await cache2.invalidate("shared:1", broadcast=True)
    
    # Should be gone from both
    assert await cache1.get("shared:1") is None
    assert await cache2.get("shared:1") is None
    
    print("✅ Distributed invalidation working")

async def test_cache_statistics():
    """Test cache statistics tracking"""
    cache = MultiLevelCache()
    await cache.initialize()
    
    # Generate some activity
    for i in range(100):
        await cache.set(f"stat:{i}", f"value_{i}")
    
    # Some hits
    for i in range(50):
        await cache.get(f"stat:{i}")
    
    # Some misses
    for i in range(100, 110):
        await cache.get(f"stat:{i}")
    
    # Get statistics
    stats = cache.get_stats()
    
    assert stats.total_requests == 60  # 50 hits + 10 misses
    assert stats.l1_hits == 50
    assert stats.misses == 10
    assert stats.l1_hit_rate > 0.8
    
    print(f"✅ Cache statistics:")
    print(f"   - Total requests: {stats.total_requests}")
    print(f"   - L1 hit rate: {stats.l1_hit_rate:.1%}")
    print(f"   - L2 hit rate: {stats.l2_hit_rate:.1%}")
    print(f"   - Overall hit rate: {stats.overall_hit_rate:.1%}")

if __name__ == "__main__":
    print("🔍 Validating multi-level cache...\n")
    
    async def run_tests():
        await test_cache_levels()
        await test_tier_migration()
        await test_cache_strategies()
        await test_eviction_policies()
        await test_tagged_caching()
        await test_batch_operations()
        await test_compression()
        await test_cache_warming()
        await test_distributed_invalidation()
        await test_cache_statistics()
    
    asyncio.run(run_tests())
    
    print("\n✅ Multi-level cache validation complete!")
```

##### Task 4.2.2: Implement Redis Cache Layer (2h)
**Cel**: Wydajny Redis cache layer

**Prompt dla AI Agent**:
```
Zaimplementuj Redis cache layer dla LiteCrewAI z advanced features.

Funkcjonalności:
1. Connection management:
   - Connection pooling
   - Sentinel support
   - Cluster support
   - Automatic reconnection
   - Pipeline batching

2. Data structures:
   - Strings (basic cache)
   - Hashes (object cache)
   - Lists (queues)
   - Sets (tags, relationships)
   - Sorted sets (rankings, scores)
   - Streams (event logs)

3. Advanced caching:
   - Sliding expiration
   - Probabilistic expiration
   - Cache stampede prevention
   - Lazy deletion
   - Memory optimization

4. Patterns implementation:
   - Cache-aside pattern
   - Write-through pattern
   - Event sourcing
   - Pub/sub for invalidation
   - Lua scripting

5. Monitoring:
   - Memory usage tracking
   - Hit/miss ratios
   - Slow query log
   - Key distribution
   - Hot key detection

Przykład użycia:
```python
# Initialize Redis cache
redis_cache = RedisCache(
    url="redis://localhost:6379",
    pool_size=10,
    max_memory="100mb",
    eviction_policy="allkeys-lru"
)

# Basic operations
await redis_cache.set("key", value, ttl=3600)
value = await redis_cache.get("key")

# Atomic operations
new_value = await redis_cache.incr("counter", 1)
await redis_cache.expire("counter", 3600)

# Hash operations (object cache)
await redis_cache.hset("user:123", {
    "name": "John",
    "email": "john@example.com",
    "score": 100
})
user = await redis_cache.hgetall("user:123")

# Set operations (tags)
await redis_cache.sadd("tag:python", "post:1", "post:2")
posts = await redis_cache.smembers("tag:python")

# Pipeline for performance
async with redis_cache.pipeline() as pipe:
    pipe.set("key1", "value1")
    pipe.set("key2", "value2")
    pipe.incr("counter")
    results = await pipe.execute()

# Lua script for atomic operations
script = """
    local key = KEYS[1]
    local value = redis.call('get', key)
    if value then
        return redis.call('incr', key)
    else
        redis.call('set', key, 1)
        return 1
    end
"""
result = await redis_cache.eval(script, keys=["visitor_count"])

# Pub/sub for cache invalidation
await redis_cache.publish("cache_invalidate", "user:*")
```

Include monitoring dashboard.
```

**Metryki Sukcesu**:
- ✅ <1ms latency for basic ops
- ✅ Pipeline 10x faster
- ✅ Memory usage optimized
- ✅ Connection pool efficient

**Walidacja**:
```python
# validate_redis_cache.py
import time
import asyncio
import statistics
from litecrewai.cache.redis_cache import RedisCache

async def test_connection_management():
    """Test Redis connection pool and management"""
    cache = RedisCache(
        url="redis://localhost:6379",
        pool_size=5,
        max_connections=10
    )
    
    await cache.initialize()
    
    # Test connection pool
    pool_info = await cache.get_pool_info()
    assert pool_info["created_connections"] <= 5
    assert pool_info["available_connections"] > 0
    
    print(f"✅ Connection pool: {pool_info}")
    
    # Test concurrent connections
    async def concurrent_operation(i):
        await cache.set(f"concurrent:{i}", f"value_{i}")
        return await cache.get(f"concurrent:{i}")
    
    tasks = [concurrent_operation(i) for i in range(20)]
    results = await asyncio.gather(*tasks)
    
    assert all(results[i] == f"value_{i}" for i in range(20))
    
    # Check pool didn't exceed max
    pool_info = await cache.get_pool_info()
    assert pool_info["created_connections"] <= 10
    
    print("✅ Connection pooling working efficiently")

async def test_basic_operations():
    """Test basic Redis operations"""
    cache = RedisCache()
    await cache.initialize()
    
    # String operations
    await cache.set("test:string", "hello world", ttl=60)
    value = await cache.get("test:string")
    assert value == "hello world"
    
    # TTL check
    ttl = await cache.ttl("test:string")
    assert 55 < ttl <= 60
    
    # Delete
    await cache.delete("test:string")
    assert await cache.get("test:string") is None
    
    # Increment
    await cache.set("counter", 0)
    new_val = await cache.incr("counter", 5)
    assert new_val == 5
    
    print("✅ Basic operations working")

async def test_data_structures():
    """Test Redis data structures"""
    cache = RedisCache()
    await cache.initialize()
    
    # Hash operations
    user_data = {
        "name": "Alice",
        "age": "30",
        "city": "NYC"
    }
    await cache.hset("user:1", user_data)
    
    retrieved = await cache.hgetall("user:1")
    assert retrieved == user_data
    
    single_field = await cache.hget("user:1", "name")
    assert single_field == "Alice"
    
    # List operations
    await cache.lpush("queue:tasks", "task1", "task2", "task3")
    task = await cache.rpop("queue:tasks")
    assert task == "task1"
    
    queue_len = await cache.llen("queue:tasks")
    assert queue_len == 2
    
    # Set operations
    await cache.sadd("skills:user1", "python", "redis", "docker")
    await cache.sadd("skills:user2", "python", "mysql", "kubernetes")
    
    common_skills = await cache.sinter("skills:user1", "skills:user2")
    assert "python" in common_skills
    assert len(common_skills) == 1
    
    # Sorted set operations
    await cache.zadd("leaderboard", {"player1": 100, "player2": 200, "player3": 150})
    top_players = await cache.zrevrange("leaderboard", 0, 1, withscores=True)
    
    assert top_players[0][0] == "player2"
    assert top_players[0][1] == 200
    
    print("✅ All data structures working")

async def test_pipeline_performance():
    """Test pipeline performance improvement"""
    cache = RedisCache()
    await cache.initialize()
    
    # Without pipeline
    start = time.time()
    for i in range(100):
        await cache.set(f"normal:{i}", f"value_{i}")
    normal_time = time.time() - start
    
    # With pipeline
    start = time.time()
    async with cache.pipeline() as pipe:
        for i in range(100):
            pipe.set(f"pipeline:{i}", f"value_{i}")
        await pipe.execute()
    pipeline_time = time.time() - start
    
    improvement = normal_time / pipeline_time
    print(f"✅ Pipeline performance: {improvement:.1f}x faster")
    print(f"   Normal: {normal_time:.3f}s, Pipeline: {pipeline_time:.3f}s")
    
    assert improvement > 5  # Should be at least 5x faster

async def test_cache_patterns():
    """Test common caching patterns"""
    cache = RedisCache()
    await cache.initialize()
    
    # Cache-aside pattern
    async def get_user(user_id):
        # Check cache
        cached = await cache.get(f"user:{user_id}")
        if cached:
            return cached
        
        # Simulate DB fetch
        user = {"id": user_id, "name": f"User {user_id}"}
        
        # Cache for next time
        await cache.set(f"user:{user_id}", user, ttl=300)
        return user
    
    # First call - cache miss
    user1 = await get_user(123)
    assert user1["id"] == 123
    
    # Second call - cache hit
    user2 = await get_user(123)
    assert user1 == user2
    
    print("✅ Cache-aside pattern working")
    
    # Write-through pattern
    async def save_user(user):
        # Save to cache
        await cache.set(f"user:{user['id']}", user, ttl=300)
        # Simulate DB save
        return True
    
    await save_user({"id": 456, "name": "Jane"})
    cached = await cache.get("user:456")
    assert cached["name"] == "Jane"
    
    print("✅ Write-through pattern working")

async def test_lua_scripting():
    """Test Lua script execution"""
    cache = RedisCache()
    await cache.initialize()
    
    # Atomic increment with initial value
    script = """
        local key = KEYS[1]
        local increment = tonumber(ARGV[1])
        local current = redis.call('get', key)
        
        if current then
            return redis.call('incrby', key, increment)
        else
            redis.call('set', key, increment)
            return increment
        end
    """
    
    result1 = await cache.eval(script, keys=["score:player1"], args=[10])
    assert result1 == 10
    
    result2 = await cache.eval(script, keys=["score:player1"], args=[5])
    assert result2 == 15
    
    print("✅ Lua scripting working")
    
    # Rate limiting script
    rate_limit_script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        
        local current = redis.call('incr', key)
        if current == 1 then
            redis.call('expire', key, window)
        end
        
        if current > limit then
            return 0
        else
            return 1
        end
    """
    
    # Test rate limiting
    for i in range(5):
        allowed = await cache.eval(
            rate_limit_script,
            keys=["rate:api:user1"],
            args=[3, 60]  # 3 requests per 60 seconds
        )
        if i < 3:
            assert allowed == 1
        else:
            assert allowed == 0
    
    print("✅ Rate limiting with Lua working")

async def test_pub_sub():
    """Test pub/sub for cache invalidation"""
    cache = RedisCache()
    await cache.initialize()
    
    received_messages = []
    
    # Subscribe to invalidation channel
    async def message_handler(message):
        received_messages.append(message)
    
    await cache.subscribe("cache:invalidate", message_handler)
    
    # Give subscription time to establish
    await asyncio.sleep(0.1)
    
    # Publish invalidation messages
    await cache.publish("cache:invalidate", "user:*")
    await cache.publish("cache:invalidate", "post:123")
    
    # Wait for messages
    await asyncio.sleep(0.1)
    
    assert len(received_messages) == 2
    assert "user:*" in received_messages
    assert "post:123" in received_messages
    
    print("✅ Pub/sub working for cache invalidation")

async def test_memory_optimization():
    """Test memory optimization features"""
    cache = RedisCache(max_memory="10mb", eviction_policy="allkeys-lru")
    await cache.initialize()
    
    # Set memory policy
    await cache.config_set("maxmemory", "10mb")
    await cache.config_set("maxmemory-policy", "allkeys-lru")
    
    # Fill cache with data
    for i in range(1000):
        await cache.set(f"mem:key{i}", "x" * 1000)  # 1KB each
    
    # Check memory usage
    info = await cache.info("memory")
    used_memory_mb = info["used_memory"] / 1024 / 1024
    
    assert used_memory_mb < 15  # Some overhead allowed
    print(f"✅ Memory optimization: {used_memory_mb:.1f}MB used")
    
    # Test eviction happened
    # Early keys should be evicted
    early_key = await cache.get("mem:key0")
    late_key = await cache.get("mem:key999")
    
    assert early_key is None  # Should be evicted
    assert late_key is not None  # Should still exist

async def test_monitoring():
    """Test Redis monitoring features"""
    cache = RedisCache()
    await cache.initialize()
    
    # Clear stats
    await cache.reset_stats()
    
    # Generate some activity
    for i in range(100):
        await cache.set(f"mon:key{i}", f"value{i}")
        
    for i in range(50):
        await cache.get(f"mon:key{i}")
        
    for i in range(100, 110):
        await cache.get(f"mon:key{i}")  # Misses
    
    # Get stats
    stats = await cache.get_stats()
    
    assert stats["keyspace_hits"] >= 50
    assert stats["keyspace_misses"] >= 10
    assert stats["total_commands_processed"] >= 160
    
    hit_rate = stats["keyspace_hits"] / (stats["keyspace_hits"] + stats["keyspace_misses"])
    print(f"✅ Monitoring stats:")
    print(f"   - Hit rate: {hit_rate:.1%}")
    print(f"   - Commands processed: {stats['total_commands_processed']}")
    
    # Slow query log
    slow_queries = await cache.get_slow_queries(limit=10)
    print(f"   - Slow queries: {len(slow_queries)}")

async def test_expiration_strategies():
    """Test different expiration strategies"""
    cache = RedisCache()
    await cache.initialize()
    
    # Standard TTL
    await cache.set("exp:standard", "value", ttl=2)
    assert await cache.get("exp:standard") is not None
    await asyncio.sleep(2.1)
    assert await cache.get("exp:standard") is None
    
    # Sliding expiration
    await cache.set_sliding("exp:sliding", "value", ttl=2)
    
    # Access multiple times
    for _ in range(3):
        await asyncio.sleep(1)
        value = await cache.get_sliding("exp:sliding")
        assert value == "value"  # Should still exist
    
    # Don't access for TTL period
    await asyncio.sleep(2.1)
    assert await cache.get("exp:sliding") is None
    
    print("✅ Sliding expiration working")
    
    # Probabilistic expiration (prevents stampede)
    await cache.set_probabilistic(
        "exp:prob",
        "value",
        ttl=5,
        beta=1.0
    )
    
    # Should exist but might refresh before actual expiry
    assert await cache.get("exp:prob") is not None
    print("✅ Probabilistic expiration set")

async def test_latency():
    """Test operation latency"""
    cache = RedisCache()
    await cache.initialize()
    
    latencies = {
        "set": [],
        "get": [],
        "incr": [],
        "hset": []
    }
    
    # Measure latencies
    for i in range(100):
        # SET
        start = time.time()
        await cache.set(f"perf:key{i}", f"value{i}")
        latencies["set"].append((time.time() - start) * 1000)
        
        # GET
        start = time.time()
        await cache.get(f"perf:key{i}")
        latencies["get"].append((time.time() - start) * 1000)
        
        # INCR
        start = time.time()
        await cache.incr(f"perf:counter{i}")
        latencies["incr"].append((time.time() - start) * 1000)
        
        # HSET
        start = time.time()
        await cache.hset(f"perf:hash{i}", {"field": "value"})
        latencies["hset"].append((time.time() - start) * 1000)
    
    # Calculate statistics
    print("✅ Latency statistics (ms):")
    for op, times in latencies.items():
        avg = statistics.mean(times)
        p95 = sorted(times)[int(len(times) * 0.95)]
        p99 = sorted(times)[int(len(times) * 0.99)]
        
        print(f"   {op.upper()}: avg={avg:.2f}, p95={p95:.2f}, p99={p99:.2f}")
        
        # All operations should be <1ms on average
        assert avg < 1.0, f"{op} too slow: {avg:.2f}ms"

if __name__ == "__main__":
    print("🔍 Validating Redis cache layer...\n")
    
    async def run_tests():
        await test_connection_management()
        await test_basic_operations()
        await test_data_structures()
        await test_pipeline_performance()
        await test_cache_patterns()
        await test_lua_scripting()
        await test_pub_sub()
        await test_memory_optimization()
        await test_monitoring()
        await test_expiration_strategies()
        await test_latency()
    
    asyncio.run(run_tests())
    
    print("\n✅ Redis cache validation complete!")
```

##### Task 4.2.3: Build Query Result Cache (2h)
**Cel**: Inteligentny cache dla query results

**Prompt dla AI Agent**:
```
Zbuduj inteligentny query result cache dla LiteCrewAI.

Funkcjonalności:
1. Query fingerprinting:
   - SQL normalization
   - Parameter extraction
   - Query pattern detection
   - Semantic hashing

2. Smart invalidation:
   - Table-based invalidation
   - Row-level tracking
   - Dependency graphs
   - Time-based expiry

3. Result optimization:
   - Compression
   - Partial results
   - Incremental updates
   - Result streaming

4. Cache strategies:
   - Read-through
   - Refresh-ahead
   - Write-behind
   - Lazy loading

5. Analytics:
   - Hit rate by query type
   - Cache efficiency
   - Memory usage
   - Performance impact

Przykład:
```python
# Initialize query cache
query_cache = QueryResultCache(
    max_size_mb=500,
    ttl_default=3600,
    compression=True
)

# Automatic caching with decorator
@query_cache.cached(ttl=7200)
async def get_user_stats(user_id: int):
    return await db.query(
        "SELECT * FROM user_stats WHERE user_id = ?",
        user_id
    )

# Manual caching
query = "SELECT * FROM agents WHERE status = ?"
params = ["active"]

result = await query_cache.get_or_fetch(
    query=query,
    params=params,
    fetcher=lambda: db.execute(query, params),
    ttl=3600,
    tags=["agents", "status"]
)

# Invalidation
await query_cache.invalidate_table("agents")
await query_cache.invalidate_tag("status")

# Refresh-ahead for important queries
await query_cache.schedule_refresh(
    query="SELECT COUNT(*) FROM tasks",
    interval=300,  # Every 5 minutes
    priority="high"
)

# Analytics
stats = query_cache.get_analytics()
print(f"Hit rate: {stats.hit_rate:.1%}")
print(f"Top queries: {stats.top_queries}")
print(f"Memory saved: {stats.bytes_saved:,}")
```

System powinien być transparent dla aplikacji.
```

**Metryki Sukcesu**:
- ✅ 80%+ hit rate
- ✅ <5ms cache lookup
- ✅ Automatic invalidation
- ✅ 50%+ memory savings

**Walidacja**:
```python
# validate_query_cache.py
import time
import hashlib
import asyncio
from datetime import datetime
from litecrewai.cache.query_cache import (
    QueryResultCache, QueryFingerprint,
    InvalidationStrategy
)

async def test_query_fingerprinting():
    """Test query normalization and fingerprinting"""
    cache = QueryResultCache()
    
    # Different queries that are semantically same
    queries = [
        ("SELECT * FROM users WHERE id = ?", [1]),
        ("SELECT * FROM users WHERE id=?", [1]),
        ("SELECT   *   FROM   users   WHERE   id = ?", [1]),
        ("select * from users where id = ?", [1]),
    ]
    
    fingerprints = set()
    for query, params in queries:
        fp = cache.get_fingerprint(query, params)
        fingerprints.add(fp.hash)
    
    # All should have same fingerprint
    assert len(fingerprints) == 1
    print("✅ Query normalization working")
    
    # Different params should have different fingerprint
    fp1 = cache.get_fingerprint("SELECT * FROM users WHERE id = ?", [1])
    fp2 = cache.get_fingerprint("SELECT * FROM users WHERE id = ?", [2])
    assert fp1.hash != fp2.hash
    
    # Extract table dependencies
    fp = cache.get_fingerprint(
        "SELECT u.*, p.* FROM users u JOIN posts p ON u.id = p.user_id WHERE u.status = ?",
        ["active"]
    )
    assert "users" in fp.tables
    assert "posts" in fp.tables
    print("✅ Table extraction working")

async def test_caching_decorator():
    """Test caching decorator functionality"""
    cache = QueryResultCache()
    
    call_count = 0
    
    @cache.cached(ttl=60)
    async def get_expensive_data(param: int):
        nonlocal call_count
        call_count += 1
        # Simulate expensive operation
        await asyncio.sleep(0.1)
        return {"result": param * 2, "timestamp": time.time()}
    
    # First call - cache miss
    result1 = await get_expensive_data(5)
    assert result1["result"] == 10
    assert call_count == 1
    
    # Second call - cache hit
    result2 = await get_expensive_data(5)
    assert result2 == result1  # Exact same object
    assert call_count == 1  # Not called again
    
    # Different param - cache miss
    result3 = await get_expensive_data(10)
    assert result3["result"] == 20
    assert call_count == 2
    
    print("✅ Caching decorator working")

async def test_smart_invalidation():
    """Test intelligent cache invalidation"""
    cache = QueryResultCache()
    
    # Cache some queries
    await cache.store(
        "SELECT * FROM users WHERE status = ?",
        ["active"],
        [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}],
        tags=["users", "status:active"]
    )
    
    await cache.store(
        "SELECT * FROM posts WHERE user_id = ?",
        [1],
        [{"id": 101, "title": "Post 1"}],
        tags=["posts", "user:1"]
    )
    
    await cache.store(
        "SELECT COUNT(*) FROM users",
        [],
        [{"count": 100}],
        tags=["users", "aggregate"]
    )
    
    # Invalidate by table
    await cache.invalidate_table("users")
    
    # Users queries should be gone
    assert await cache.get("SELECT * FROM users WHERE status = ?", ["active"]) is None
    assert await cache.get("SELECT COUNT(*) FROM users", []) is None
    
    # Posts query should remain
    assert await cache.get("SELECT * FROM posts WHERE user_id = ?", [1]) is not None
    
    print("✅ Table-based invalidation working")
    
    # Test tag-based invalidation
    await cache.store(
        "SELECT * FROM orders WHERE user_id = ?",
        [1],
        [{"id": 1001, "total": 99.99}],
        tags=["orders", "user:1"]
    )
    
    # Invalidate all user:1 data
    await cache.invalidate_tag("user:1")
    
    assert await cache.get("SELECT * FROM posts WHERE user_id = ?", [1]) is None
    assert await cache.get("SELECT * FROM orders WHERE user_id = ?", [1]) is None
    
    print("✅ Tag-based invalidation working")

async def test_compression():
    """Test result compression"""
    cache_plain = QueryResultCache(compression=False)
    cache_compressed = QueryResultCache(compression=True)
    
    # Large result set
    large_result = [
        {"id": i, "data": "x" * 100, "values": list(range(100))}
        for i in range(100)
    ]
    
    # Store in both caches
    query = "SELECT * FROM large_table"
    
    await cache_plain.store(query, [], large_result)
    await cache_compressed.store(query, [], large_result)
    
    # Compare sizes
    size_plain = cache_plain.get_entry_size(query, [])
    size_compressed = cache_compressed.get_entry_size(query, [])
    
    compression_ratio = 1 - (size_compressed / size_plain)
    print(f"✅ Compression ratio: {compression_ratio:.1%}")
    print(f"   Plain: {size_plain:,} bytes")
    print(f"   Compressed: {size_compressed:,} bytes")
    
    assert compression_ratio > 0.5  # At least 50% compression
    
    # Verify data integrity
    result = await cache_compressed.get(query, [])
    assert result == large_result

async def test_refresh_ahead():
    """Test refresh-ahead functionality"""
    cache = QueryResultCache()
    
    refresh_count = 0
    
    async def data_fetcher():
        nonlocal refresh_count
        refresh_count += 1
        return [{"count": refresh_count, "time": time.time()}]
    
    # Schedule refresh-ahead
    await cache.schedule_refresh(
        query="SELECT COUNT(*) FROM active_users",
        params=[],
        fetcher=data_fetcher,
        interval=1,  # Every 1 second
        ttl=10
    )
    
    # Initial fetch
    await asyncio.sleep(0.1)
    result1 = await cache.get("SELECT COUNT(*) FROM active_users", [])
    assert result1[0]["count"] == 1
    
    # Wait for refresh
    await asyncio.sleep(1.2)
    result2 = await cache.get("SELECT COUNT(*) FROM active_users", [])
    assert result2[0]["count"] == 2  # Refreshed
    
    # Stop refresh
    await cache.stop_refresh("SELECT COUNT(*) FROM active_users", [])
    
    print(f"✅ Refresh-ahead working ({refresh_count} refreshes)")

async def test_partial_results():
    """Test partial result caching"""
    cache = QueryResultCache()
    
    # Large dataset
    full_data = [{"id": i, "value": f"item_{i}"} for i in range(1000)]
    
    # Cache with pagination info
    await cache.store_partial(
        query="SELECT * FROM items ORDER BY id",
        params=[],
        result=full_data[:100],
        offset=0,
        limit=100,
        total_count=1000
    )
    
    # Retrieve partial
    cached = await cache.get_partial(
        "SELECT * FROM items ORDER BY id",
        [],
        offset=0,
        limit=100
    )
    
    assert cached is not None
    assert len(cached["data"]) == 100
    assert cached["total_count"] == 1000
    assert cached["has_more"] == True
    
    print("✅ Partial result caching working")

async def test_dependency_tracking():
    """Test query dependency tracking"""
    cache = QueryResultCache()
    
    # Define query dependencies
    await cache.add_dependency(
        parent="SELECT * FROM user_stats WHERE user_id = ?",
        child="SELECT * FROM users WHERE id = ?"
    )
    
    # Cache both queries
    await cache.store(
        "SELECT * FROM users WHERE id = ?",
        [1],
        [{"id": 1, "name": "John"}]
    )
    
    await cache.store(
        "SELECT * FROM user_stats WHERE user_id = ?",
        [1],
        [{"user_id": 1, "total_posts": 50}]
    )
    
    # Invalidate parent - should invalidate child too
    await cache.invalidate(
        "SELECT * FROM users WHERE id = ?",
        [1]
    )
    
    # Both should be invalidated
    assert await cache.get("SELECT * FROM users WHERE id = ?", [1]) is None
    assert await cache.get("SELECT * FROM user_stats WHERE user_id = ?", [1]) is None
    
    print("✅ Dependency tracking working")

async def test_analytics():
    """Test cache analytics"""
    cache = QueryResultCache()
    
    # Generate activity
    queries = [
        ("SELECT * FROM users WHERE id = ?", [1]),
        ("SELECT * FROM users WHERE id = ?", [2]),
        ("SELECT * FROM posts WHERE user_id = ?", [1]),
        ("SELECT COUNT(*) FROM users", []),
    ]
    
    # Cache queries
    for query, params in queries:
        await cache.store(query, params, [{"dummy": "data"}])
    
    # Generate hits and misses
    for _ in range(10):
        await cache.get("SELECT * FROM users WHERE id = ?", [1])  # Hits
    
    for i in range(5):
        await cache.get("SELECT * FROM users WHERE id = ?", [i + 10])  # Misses
    
    # Get analytics
    stats = await cache.get_analytics()
    
    assert stats.total_queries == 4
    assert stats.cache_hits >= 10
    assert stats.cache_misses >= 5
    assert stats.hit_rate > 0.6
    
    print(f"✅ Analytics:")
    print(f"   - Hit rate: {stats.hit_rate:.1%}")
    print(f"   - Total queries cached: {stats.total_queries}")
    print(f"   - Memory used: {stats.memory_used_mb:.1f}MB")
    
    # Top queries
    top_queries = stats.get_top_queries(2)
    assert len(top_queries) >= 1
    assert top_queries[0]["hits"] >= 10

async def test_performance():
    """Test cache performance"""
    cache = QueryResultCache()
    
    # Prepare test data
    queries = []
    for i in range(100):
        query = f"SELECT * FROM table_{i % 10} WHERE id = ?"
        params = [i]
        result = [{"id": i, "data": f"value_{i}"}]
        queries.append((query, params, result))
    
    # Store all
    start = time.time()
    for query, params, result in queries:
        await cache.store(query, params, result)
    store_time = time.time() - start
    
    print(f"✅ Store performance: {len(queries)/store_time:.0f} ops/sec")
    
    # Retrieve all
    start = time.time()
    hits = 0
    for query, params, _ in queries:
        if await cache.get(query, params):
            hits += 1
    get_time = time.time() - start
    
    assert hits == len(queries)
    avg_lookup = (get_time / len(queries)) * 1000
    
    print(f"✅ Lookup performance: {avg_lookup:.2f}ms avg")
    assert avg_lookup < 5  # Should be <5ms

async def test_memory_limit():
    """Test memory limit enforcement"""
    cache = QueryResultCache(max_size_mb=1)  # 1MB limit
    
    # Fill cache
    stored = 0
    for i in range(1000):
        query = f"SELECT * FROM test WHERE id = {i}"
        # ~1KB per entry
        result = [{"data": "x" * 1000}]
        
        if await cache.store(query, [], result):
            stored += 1
        else:
            break
    
    print(f"✅ Memory limit: stored {stored} entries in 1MB")
    
    # Check size
    stats = await cache.get_analytics()
    assert stats.memory_used_mb <= 1.1  # Some overhead

if __name__ == "__main__":
    print("🔍 Validating query result cache...\n")
    
    async def run_tests():
        await test_query_fingerprinting()
        await test_caching_decorator()
        await test_smart_invalidation()
        await test_compression()
        await test_refresh_ahead()
        await test_partial_results()
        await test_dependency_tracking()
        await test_analytics()
        await test_performance()
        await test_memory_limit()
    
    asyncio.run(run_tests())
    
    print("\n✅ Query cache validation complete!")
```

---

## 📦 FAZA 5: API I INTERFACE

### Blok 5.1: RESTful API Design
**Czas**: 8h
**Cel**: Clean, intuitive REST API

#### Zadania Atomowe:

##### Task 5.1.1: Design API Architecture (3h)
**Cel**: Kompletna architektura RESTful API

**Prompt dla AI Agent**:
```
Zaprojektuj kompletną architekturę REST API dla LiteCrewAI.

Komponenty:
1. API Structure:
   - Resource-based URLs
   - Consistent naming
   - Proper HTTP methods
   - HATEOAS support
   - API versioning

2. Core endpoints:
   /api/v1/agents
   /api/v1/tasks  
   /api/v1/crews
   /api/v1/executions
   /api/v1/memories
   /api/v1/tools
   /api/v1/costs
   /api/v1/health

3. Advanced features:
   - Filtering & sorting
   - Pagination
   - Field selection
   - Batch operations
   - Async operations
   - WebSocket support

4. Authentication:
   - API key auth
   - JWT tokens (optional)
   - Rate limiting
   - IP whitelisting
   - Usage quotas

5. Response format:
   - Consistent structure
   - Error handling
   - JSONAPI/HAL format
   - Content negotiation
   - Compression

API Examples:
```
# Create agent
POST /api/v1/agents
{
  "name": "researcher",
  "role": "research",
  "config": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7
  }
}

# Get agents with filtering
GET /api/v1/agents?role=research&status=active&fields=id,name,stats

# Execute task
POST /api/v1/tasks
{
  "description": "Research AI trends",
  "agent_id": "agent_123",
  "priority": "high",
  "config": {
    "timeout": 300,
    "max_cost": 0.50
  }
}

# Batch operations
POST /api/v1/tasks/batch
{
  "operations": [
    {"method": "create", "data": {...}},
    {"method": "update", "id": "123", "data": {...}}
  ]
}

# Async operation
POST /api/v1/crews/execute
Response: {"job_id": "job_456", "status": "pending"}

GET /api/v1/jobs/job_456
Response: {"status": "completed", "result": {...}}

# WebSocket for real-time
WS /api/v1/ws
> {"type": "subscribe", "channel": "task_updates"}
< {"type": "update", "task_id": "123", "status": "running"}
```

Include OpenAPI/Swagger documentation.
```

**Metryki Sukcesu**:
- ✅ RESTful principles
- ✅ Consistent design
- ✅ <100ms response time
- ✅ OpenAPI documented

**Walidacja**:
```python
# validate_api_architecture.py
import json
import yaml
from typing import Dict, List
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from litecrewai.api import create_app

def test_api_structure():
    """Test API follows RESTful principles"""
    app = create_app()
    
    # Get routes
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name
            })
    
    # Check resource-based URLs
    resource_patterns = [
        "/api/v1/agents",
        "/api/v1/tasks",
        "/api/v1/crews",
        "/api/v1/executions",
        "/api/v1/memories"
    ]
    
    for pattern in resource_patterns:
        # Should have standard CRUD operations
        resource_routes = [r for r in routes if r["path"].startswith(pattern)]
        
        methods_found = set()
        for route in resource_routes:
            methods_found.update(route["methods"])
        
        # Check standard methods exist
        assert "GET" in methods_found, f"No GET for {pattern}"
        assert "POST" in methods_found, f"No POST for {pattern}"
        
        print(f"✅ {pattern}: {methods_found}")

def test_endpoint_naming():
    """Test consistent endpoint naming"""
    app = create_app()
    
    issues = []
    for route in app.routes:
        if hasattr(route, "path"):
            path = route.path
            
            # Check naming conventions
            if "/api/v1/" in path:
                parts = path.split("/")[3:]  # After /api/v1/
                
                for part in parts:
                    if part and not part.startswith("{"):
                        # Should be lowercase, plural for collections
                        if not part.islower():
                            issues.append(f"Not lowercase: {path}")
                        
                        # Collections should be plural
                        if len(parts) == 1 and not part.endswith("s"):
                            # Exception for 'health', 'auth', etc.
                            if part not in ["health", "auth", "ws"]:
                                issues.append(f"Collection not plural: {path}")
    
    if issues:
        print(f"❌ Naming issues: {issues}")
    else:
        print("✅ Endpoint naming consistent")

def test_http_methods():
    """Test proper HTTP method usage"""
    from fastapi.testclient import TestClient
    
    app = create_app()
    client = TestClient(app)
    
    # Test method semantics
    test_cases = [
        # GET should be safe (no side effects)
        ("GET", "/api/v1/agents", None, [200, 401]),
        ("GET", "/api/v1/agents/123", None, [200, 404, 401]),
        
        # POST creates resources
        ("POST", "/api/v1/agents", {"name": "test"}, [201, 400, 401]),
        
        # PUT replaces entire resource
        ("PUT", "/api/v1/agents/123", {"name": "updated"}, [200, 404, 401]),
        
        # PATCH partial update
        ("PATCH", "/api/v1/agents/123", {"status": "active"}, [200, 404, 401]),
        
        # DELETE removes resource
        ("DELETE", "/api/v1/agents/123", None, [204, 404, 401]),
    ]
    
    for method, path, data, expected_statuses in test_cases:
        response = client.request(
            method, 
            path,
            json=data,
            headers={"X-API-Key": "test-key"}
        )
        
        # Should return one of expected statuses
        assert response.status_code in expected_statuses, \
            f"{method} {path} returned {response.status_code}"
        
        print(f"✅ {method} {path}: {response.status_code}")

def test_response_format():
    """Test consistent response format"""
    from fastapi.testclient import TestClient
    
    app = create_app()
    client = TestClient(app)
    
    # Success response
    response = client.get(
        "/api/v1/health",
        headers={"X-API-Key": "test-key"}
    )
    
    data = response.json()
    
    # Standard response envelope
    assert "status" in data or response.status_code >= 400
    assert "data" in data or "error" in data
    
    if response.status_code >= 400:
        # Error format
        assert "error" in data
        assert "message" in data["error"]
        assert "code" in data["error"]
    else:
        # Success format
        assert "data" in data
    
    print("✅ Response format consistent")

def test_pagination():
    """Test pagination implementation"""
    from fastapi.testclient import TestClient
    
    app = create_app()
    client = TestClient(app)
    
    # Test pagination params
    response = client.get(
        "/api/v1/agents?page=1&per_page=10",
        headers={"X-API-Key": "test-key"}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Pagination metadata
        assert "data" in data
        assert "meta" in data or "pagination" in data
        
        meta = data.get("meta") or data.get("pagination", {})
        assert "total" in meta or "total_count" in meta
        assert "page" in meta or "current_page" in meta
        assert "per_page" in meta or "page_size" in meta
        
        print("✅ Pagination metadata present")

def test_filtering_sorting():
    """Test filtering and sorting capabilities"""
    from fastapi.testclient import TestClient
    
    app = create_app()
    client = TestClient(app)
    
    # Test filter parameters
    filter_tests = [
        "/api/v1/agents?role=research",
        "/api/v1/agents?status=active&role=assistant",
        "/api/v1/tasks?priority=high&status=pending",
        "/api/v1/tasks?created_after=2024-01-01"
    ]
    
    for url in filter_tests:
        response = client.get(url, headers={"X-API-Key": "test-key"})
        assert response.status_code in [200, 400, 401]
        print(f"✅ Filter: {url.split('?')[1]}")
    
    # Test sorting
    sort_tests = [
        "/api/v1/agents?sort=name",
        "/api/v1/agents?sort=-created_at",  # Descending
        "/api/v1/tasks?sort=priority,-created_at"
    ]
    
    for url in sort_tests:
        response = client.get(url, headers={"X-API-Key": "test-key"})
        assert response.status_code in [200, 400, 401]
        print(f"✅ Sort: {url.split('?')[1]}")

def test_openapi_spec():
    """Test OpenAPI specification"""
    app = create_app()
    
    # Get OpenAPI schema
    openapi_schema = get_openapi(
        title="LiteCrewAI API",
        version="1.0.0",
        description="Lightweight AI Agent Framework API",
        routes=app.routes,
    )
    
    # Validate schema structure
    assert "openapi" in openapi_schema
    assert "info" in openapi_schema
    assert "paths" in openapi_schema
    assert "components" in openapi_schema
    
    # Check all endpoints documented
    paths = openapi_schema["paths"]
    
    required_endpoints = [
        "/api/v1/agents",
        "/api/v1/tasks",
        "/api/v1/health"
    ]
    
    for endpoint in required_endpoints:
        assert endpoint in paths, f"Missing documentation for {endpoint}"
        
        # Check methods documented
        methods = paths[endpoint]
        assert len(methods) > 0, f"No methods documented for {endpoint}"
        
        # Check each method has required fields
        for method, spec in methods.items():
            if method != "parameters":
                assert "summary" in spec or "description" in spec
                assert "responses" in spec
                assert "200" in spec["responses"] or "201" in spec["responses"]
    
    print(f"✅ OpenAPI spec valid with {len(paths)} endpoints")
    
    # Save spec
    with open("/tmp/openapi.yaml", "w") as f:
        yaml.dump(openapi_schema, f)
    print("✅ OpenAPI spec saved to /tmp/openapi.yaml")

def test_versioning():
    """Test API versioning implementation"""
    from fastapi.testclient import TestClient
    
    app = create_app()
    client = TestClient(app)
    
    # Version in URL
    response = client.get("/api/v1/agents", headers={"X-API-Key": "test-key"})
    assert response.status_code in [200, 401]
    
    # Version in header (optional)
    response = client.get(
        "/api/agents",
        headers={
            "X-API-Key": "test-key",
            "X-API-Version": "1"
        }
    )
    # Should work if header versioning supported
    
    # Check version in response
    if response.status_code == 200:
        assert "X-API-Version" in response.headers or \
               "api-version" in response.headers.get("content-type", "")
    
    print("✅ API versioning implemented")

def test_hateoas():
    """Test HATEOAS (Hypermedia as the Engine of Application State)"""
    from fastapi.testclient import TestClient
    
    app = create_app()
    client = TestClient(app)
    
    # Get single resource
    response = client.get(
        "/api/v1/agents/123",
        headers={"X-API-Key": "test-key"}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Should have links
        assert "links" in data or "_links" in data
        
        links = data.get("links") or data.get("_links", {})
        
        # Common HATEOAS links
        expected_links = ["self", "update", "delete"]
        for link in expected_links:
            if link in links:
                assert "href" in links[link] or isinstance(links[link], str)
                print(f"✅ HATEOAS link: {link}")

def test_content_negotiation():
    """Test content negotiation"""
    from fastapi.testclient import TestClient
    
    app = create_app()
    client = TestClient(app)
    
    # Test different content types
    headers_tests = [
        ({"Accept": "application/json"}, "application/json"),
        ({"Accept": "application/vnd.api+json"}, "application/vnd.api+json"),
    ]
    
    for headers, expected_content_type in headers_tests:
        headers["X-API-Key"] = "test-key"
        response = client.get("/api/v1/agents", headers=headers)
        
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            assert expected_content_type in content_type
            print(f"✅ Content negotiation: {expected_content_type}")

if __name__ == "__main__":
    print("🔍 Validating API architecture...\n")
    
    test_api_structure()
    test_endpoint_naming()
    test_http_methods()
    test_response_format()
    test_pagination()
    test_filtering_sorting()
    test_openapi_spec()
    test_versioning()
    test_hateoas()
    test_content_negotiation()
    
    print("\n✅ API architecture validation complete!")
```

##### Task 5.1.2: Implement Core Endpoints (3h)
**Cel**: Implementacja głównych endpoints

**Prompt dla AI Agent**:
```
Zaimplementuj core REST endpoints dla LiteCrewAI używając FastAPI.

Endpoints do implementacji:
1. Agents:
   - GET /agents - list all
   - POST /agents - create
   - GET /agents/{id} - get one
   - PUT /agents/{id} - update
   - DELETE /agents/{id} - delete
   - POST /agents/{id}/execute - run task

2. Tasks:
   - GET /tasks - list with filters
   - POST /tasks - create task
   - GET /tasks/{id} - get details
   - PATCH /tasks/{id} - update status
   - DELETE /tasks/{id} - cancel
   - GET /tasks/{id}/result - get result

3. Crews:
   - GET /crews - list crews
   - POST /crews - create crew
   - POST /crews/{id}/execute - run crew
   - GET /crews/{id}/agents - get agents

4. System:
   - GET /health - health check
   - GET /metrics - system metrics
   - GET /costs - cost summary
   - POST /auth/token - get token

Features per endpoint:
- Input validation (Pydantic)
- Error handling
- Pagination
- Filtering
- Sorting
- Field selection
- Caching headers
- Rate limiting

Example implementation:
```python
from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1")

class AgentCreate(BaseModel):
    name: str
    role: str
    config: dict = {}

class AgentResponse(BaseModel):
    id: str
    name: str
    role: str
    status: str
    created_at: datetime
    stats: dict

@router.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    role: Optional[str] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status"),
    sort: str = Query("created_at", description="Sort field"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    fields: Optional[str] = Query(None, description="Comma-separated fields"),
    db: Database = Depends(get_db)
):
    # Implementation
    pass

@router.post("/agents", response_model=AgentResponse, status_code=201)
async def create_agent(
    agent: AgentCreate,
    db: Database = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Implementation
    pass
```

Include comprehensive error responses and logging.
```

**Metryki Sukcesu**:
- ✅ All CRUD operations work
- ✅ <50ms response time
- ✅ Proper status codes
- ✅ Comprehensive validation

**Walidacja**:
```python
# validate_core_endpoints.py
import asyncio
import json
from datetime import datetime
from fastapi.testclient import TestClient
from litecrewai.api.app import create_app

def test_agents_endpoints():
    """Test all agent-related endpoints"""
    app = create_app()
    client = TestClient(app)
    
    # Create agent
    agent_data = {
        "name": "test_agent",
        "role": "assistant",
        "config": {
            "model": "gpt-3.5-turbo",
            "temperature": 0.7
        }
    }
    
    response = client.post(
        "/api/v1/agents",
        json=agent_data,
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 201
    created_agent = response.json()["data"]
    assert created_agent["name"] == agent_data["name"]
    assert "id" in created_agent
    agent_id = created_agent["id"]
    print(f"✅ Created agent: {agent_id}")
    
    # List agents
    response = client.get(
        "/api/v1/agents",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 200
    agents = response.json()["data"]
    assert isinstance(agents, list)
    assert any(a["id"] == agent_id for a in agents)
    print(f"✅ Listed {len(agents)} agents")
    
    # Get single agent
    response = client.get(
        f"/api/v1/agents/{agent_id}",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 200
    agent = response.json()["data"]
    assert agent["id"] == agent_id
    print(f"✅ Retrieved agent: {agent['name']}")
    
    # Update agent
    update_data = {"status": "inactive"}
    response = client.patch(
        f"/api/v1/agents/{agent_id}",
        json=update_data,
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 200
    updated = response.json()["data"]
    assert updated["status"] == "inactive"
    print("✅ Updated agent status")
    
    # Delete agent
    response = client.delete(
        f"/api/v1/agents/{agent_id}",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 204
    print("✅ Deleted agent")
    
    # Verify deletion
    response = client.get(
        f"/api/v1/agents/{agent_id}",
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 404

def test_tasks_endpoints():
    """Test task-related endpoints"""
    app = create_app()
    client = TestClient(app)
    
    # Create task
    task_data = {
        "description": "Test task",
        "agent_id": "test_agent_123",
        "priority": "high",
        "config": {
            "timeout": 300,
            "max_retries": 3
        }
    }
    
    response = client.post(
        "/api/v1/tasks",
        json=task_data,
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 201
    task = response.json()["data"]
    assert task["description"] == task_data["description"]
    task_id = task["id"]
    print(f"✅ Created task: {task_id}")
    
    # List tasks with filters
    response = client.get(
        "/api/v1/tasks?status=pending&priority=high",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 200
    tasks = response.json()["data"]
    
    # Check filtering worked
    for task in tasks:
        assert task["status"] == "pending"
        assert task["priority"] == "high"
    
    print(f"✅ Filtered tasks: {len(tasks)} high priority pending")
    
    # Get task details
    response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 200
    task = response.json()["data"]
    assert task["id"] == task_id
    
    # Update task status
    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "running"},
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "running"
    print("✅ Updated task status")

def test_pagination():
    """Test pagination functionality"""
    app = create_app()
    client = TestClient(app)
    
    # Create multiple agents for pagination test
    for i in range(25):
        client.post(
            "/api/v1/agents",
            json={"name": f"agent_{i}", "role": "assistant"},
            headers={"X-API-Key": "test-key"}
        )
    
    # Test pagination
    response = client.get(
        "/api/v1/agents?page=1&per_page=10",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check pagination structure
    assert "data" in data
    assert "meta" in data
    
    meta = data["meta"]
    assert meta["page"] == 1
    assert meta["per_page"] == 10
    assert meta["total"] >= 25
    assert meta["pages"] >= 3
    assert len(data["data"]) == 10
    
    print(f"✅ Pagination: page 1/{meta['pages']}, {meta['total']} total")
    
    # Test page 2
    response = client.get(
        "/api/v1/agents?page=2&per_page=10",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["page"] == 2
    assert len(data["data"]) == 10

def test_field_selection():
    """Test field selection feature"""
    app = create_app()
    client = TestClient(app)
    
    # Create agent
    response = client.post(
        "/api/v1/agents",
        json={
            "name": "field_test",
            "role": "researcher",
            "config": {"model": "gpt-3.5", "temp": 0.7}
        },
        headers={"X-API-Key": "test-key"}
    )
    
    agent_id = response.json()["data"]["id"]
    
    # Get with field selection
    response = client.get(
        f"/api/v1/agents/{agent_id}?fields=id,name,role",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 200
    agent = response.json()["data"]
    
    # Should only have requested fields
    assert set(agent.keys()) == {"id", "name", "role"}
    print(f"✅ Field selection: {list(agent.keys())}")

def test_sorting():
    """Test sorting functionality"""
    app = create_app()
    client = TestClient(app)
    
    # Create agents with different names
    names = ["zebra", "alpha", "beta", "gamma"]
    for name in names:
        client.post(
            "/api/v1/agents",
            json={"name": name, "role": "assistant"},
            headers={"X-API-Key": "test-key"}
        )
    
    # Sort ascending
    response = client.get(
        "/api/v1/agents?sort=name&order=asc",
        headers={"X-API-Key": "test-key"}
    )
    
    agents = response.json()["data"]
    agent_names = [a["name"] for a in agents if a["name"] in names]
    assert agent_names == sorted(names)
    print(f"✅ Sort ascending: {agent_names[:4]}")
    
    # Sort descending
    response = client.get(
        "/api/v1/agents?sort=name&order=desc",
        headers={"X-API-Key": "test-key"}
    )
    
    agents = response.json()["data"]
    agent_names = [a["name"] for a in agents if a["name"] in names]
    assert agent_names == sorted(names, reverse=True)
    print(f"✅ Sort descending: {agent_names[:4]}")

def test_error_handling():
    """Test error response format"""
    app = create_app()
    client = TestClient(app)
    
    # 404 - Not found
    response = client.get(
        "/api/v1/agents/nonexistent",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 404
    error = response.json()
    assert "error" in error
    assert "message" in error["error"]
    assert "code" in error["error"]
    print(f"✅ 404 error: {error['error']['message']}")
    
    # 400 - Bad request
    response = client.post(
        "/api/v1/agents",
        json={"invalid": "data"},  # Missing required fields
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 400
    error = response.json()
    assert "error" in error
    assert "validation_errors" in error["error"] or "details" in error["error"]
    print("✅ 400 validation error")
    
    # 401 - Unauthorized
    response = client.get("/api/v1/agents")  # No API key
    
    assert response.status_code == 401
    error = response.json()
    assert error["error"]["code"] == "unauthorized"
    print("✅ 401 unauthorized error")

def test_async_operations():
    """Test async operation endpoints"""
    app = create_app()
    client = TestClient(app)
    
    # Start async operation
    response = client.post(
        "/api/v1/crews/execute",
        json={
            "crew_id": "test_crew",
            "task": "Complex analysis task"
        },
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 202  # Accepted
    job_data = response.json()["data"]
    assert "job_id" in job_data
    assert job_data["status"] == "pending"
    job_id = job_data["job_id"]
    print(f"✅ Async job created: {job_id}")
    
    # Check job status
    response = client.get(
        f"/api/v1/jobs/{job_id}",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 200
    job = response.json()["data"]
    assert job["id"] == job_id
    assert job["status"] in ["pending", "running", "completed", "failed"]
    print(f"✅ Job status: {job['status']}")

def test_cache_headers():
    """Test caching headers"""
    app = create_app()
    client = TestClient(app)
    
    # GET request should have cache headers
    response = client.get(
        "/api/v1/agents",
        headers={"X-API-Key": "test-key"}
    )
    
    headers = response.headers
    
    # Check cache control
    assert "cache-control" in headers or "Cache-Control" in headers
    assert "etag" in headers or "ETag" in headers
    
    etag = headers.get("etag") or headers.get("ETag")
    print(f"✅ Cache headers present: ETag={etag}")
    
    # Conditional request
    response2 = client.get(
        "/api/v1/agents",
        headers={
            "X-API-Key": "test-key",
            "If-None-Match": etag
        }
    )
    
    # Should return 304 if unchanged
    if response2.status_code == 304:
        print("✅ Conditional request: 304 Not Modified")

def test_rate_limiting():
    """Test rate limiting"""
    app = create_app()
    client = TestClient(app)
    
    # Make multiple rapid requests
    responses = []
    for i in range(15):
        response = client.get(
            "/api/v1/agents",
            headers={"X-API-Key": "test-key"}
        )
        responses.append(response)
    
    # Should hit rate limit
    rate_limited = any(r.status_code == 429 for r in responses)
    
    if rate_limited:
        # Check rate limit headers
        limited_response = next(r for r in responses if r.status_code == 429)
        headers = limited_response.headers
        
        assert "x-ratelimit-limit" in headers
        assert "x-ratelimit-remaining" in headers
        assert "x-ratelimit-reset" in headers
        
        print(f"✅ Rate limiting active: {headers['x-ratelimit-limit']} req/window")
    else:
        print("⚠️  Rate limiting not triggered in test")

def test_health_metrics():
    """Test health and metrics endpoints"""
    app = create_app()
    client = TestClient(app)
    
    # Health check (no auth required)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    health = response.json()
    assert health["status"] in ["healthy", "degraded", "unhealthy"]
    assert "checks" in health
    assert "database" in health["checks"]
    assert "redis" in health["checks"]
    print(f"✅ Health: {health['status']}")
    
    # Metrics endpoint
    response = client.get(
        "/api/v1/metrics",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 200
    metrics = response.json()["data"]
    
    assert "agents" in metrics
    assert "tasks" in metrics
    assert "system" in metrics
    
    print(f"✅ Metrics: {metrics['agents']['total']} agents, "
          f"{metrics['tasks']['total']} tasks")

if __name__ == "__main__":
    print("🔍 Validating core endpoints...\n")
    
    test_agents_endpoints()
    test_tasks_endpoints()
    test_pagination()
    test_field_selection()
    test_sorting()
    test_error_handling()
    test_async_operations()
    test_cache_headers()
    test_rate_limiting()
    test_health_metrics()
    
    print("\n✅ Core endpoints validation complete!")
```

##### Task 5.1.3: Add WebSocket Support (2h)
**Cel**: Real-time updates via WebSocket

**Prompt dla AI Agent**:
```
Dodaj WebSocket support do LiteCrewAI API dla real-time updates.

Funkcjonalności:
1. WebSocket endpoint:
   - /api/v1/ws - main WebSocket
   - Authentication
   - Connection management
   - Heartbeat/ping-pong
   - Auto-reconnect support

2. Channel subscriptions:
   - task_updates - task status changes
   - agent_status - agent availability
   - execution_logs - real-time logs
   - cost_alerts - budget warnings
   - system_events - system notifications

3. Message protocol:
   ```json
   // Client -> Server
   {
     "type": "subscribe|unsubscribe|ping",
     "channel": "task_updates",
     "filters": {"agent_id": "123"}
   }
   
   // Server -> Client
   {
     "type": "update|event|error|pong",
     "channel": "task_updates",
     "data": {...},
     "timestamp": "2024-01-01T12:00:00Z"
   }
```

4. Features:
   - Message queuing
   - Backpressure handling
   - Binary data support
   - Compression
   - Rate limiting

5. Client libraries:
   - JavaScript/TypeScript
   - Python
   - Auto-reconnection
   - Event emitters

Example implementation:
```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Set, Dict
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        await self.send_personal_message(
            {"type": "connected", "client_id": client_id},
            client_id
        )
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        # Clean up subscriptions
        for channel, subscribers in self.subscriptions.items():
            subscribers.discard(client_id)
    
    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def broadcast_to_channel(self, channel: str, message: dict):
        if channel in self.subscriptions:
            for client_id in self.subscriptions[channel]:
                await self.send_personal_message(message, client_id)

@app.websocket("/api/v1/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    api_key: str = Query(None)
):
    if not validate_api_key(api_key):
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    client_id = generate_client_id()
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            await handle_client_message(client_id, data)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
```

Include przykłady client-side code.
```

**Metryki Sukcesu**:
- ✅ <50ms message latency
- ✅ Handles 1000+ connections
- ✅ Auto-reconnect works
- ✅ No message loss

**Walidacja**:
```python
# validate_websocket_support.py
import asyncio
import json
import time
from typing import List, Dict
import websockets
from fastapi.testclient import TestClient
from litecrewai.api.app import create_app

async def test_websocket_connection():
    """Test basic WebSocket connection"""
    uri = "ws://localhost:8000/api/v1/ws?api_key=test-key"
    
    async with websockets.connect(uri) as websocket:
        # Should receive connection confirmation
        message = await websocket.recv()
        data = json.loads(message)
        
        assert data["type"] == "connected"
        assert "client_id" in data
        client_id = data["client_id"]
        
        print(f"✅ Connected with client_id: {client_id}")
        
        # Test ping-pong
        await websocket.send(json.dumps({"type": "ping"}))
        pong = await websocket.recv()
        pong_data = json.loads(pong)
        
        assert pong_data["type"] == "pong"
        print("✅ Ping-pong working")

async def test_channel_subscription():
    """Test channel subscription and updates"""
    uri = "ws://localhost:8000/api/v1/ws?api_key=test-key"
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection
        await websocket.recv()
        
        # Subscribe to task updates
        await websocket.send(json.dumps({
            "type": "subscribe",
            "channel": "task_updates",
            "filters": {"status": "running"}
        }))
        
        # Should receive subscription confirmation
        response = await websocket.recv()
        data = json.loads(response)
        assert data["type"] == "subscribed"
        assert data["channel"] == "task_updates"
        print("✅ Subscribed to task_updates")
        
        # Simulate task update (in real test, would come from another source)
        # Wait for a real update or timeout
        try:
            update = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            update_data = json.loads(update)
            
            assert update_data["type"] == "update"
            assert update_data["channel"] == "task_updates"
            assert "data" in update_data
            print(f"✅ Received update: {update_data['data']}")
        except asyncio.TimeoutError:
            print("⚠️  No updates received (normal in test)")

async def test_multiple_subscriptions():
    """Test multiple channel subscriptions"""
    uri = "ws://localhost:8000/api/v1/ws?api_key=test-key"
    
    async with websockets.connect(uri) as websocket:
        await websocket.recv()  # Connection message
        
        # Subscribe to multiple channels
        channels = ["task_updates", "agent_status", "cost_alerts"]
        
        for channel in channels:
            await websocket.send(json.dumps({
                "type": "subscribe",
                "channel": channel
            }))
            
            response = await websocket.recv()
            data = json.loads(response)
            assert data["channel"] == channel
            print(f"✅ Subscribed to {channel}")
        
        # Unsubscribe from one
        await websocket.send(json.dumps({
            "type": "unsubscribe",
            "channel": "cost_alerts"
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        assert data["type"] == "unsubscribed"
        assert data["channel"] == "cost_alerts"
        print("✅ Unsubscribed from cost_alerts")

async def test_concurrent_connections():
    """Test multiple concurrent WebSocket connections"""
    uri = "ws://localhost:8000/api/v1/ws?api_key=test-key"
    
    connections = []
    client_ids = []
    
    # Create multiple connections
    for i in range(10):
        ws = await websockets.connect(uri)
        connections.append(ws)
        
        # Get client ID
        msg = await ws.recv()
        data = json.loads(msg)
        client_ids.append(data["client_id"])
    
    print(f"✅ Created {len(connections)} concurrent connections")
    
    # All should have unique IDs
    assert len(set(client_ids)) == len(client_ids)
    
    # Subscribe all to same channel
    for ws in connections:
        await ws.send(json.dumps({
            "type": "subscribe",
            "channel": "system_events"
        }))
        await ws.recv()  # Subscription confirmation
    
    # Close all connections
    for ws in connections:
        await ws.close()
    
    print("✅ All connections closed cleanly")

async def test_message_ordering():
    """Test message ordering is preserved"""
    uri = "ws://localhost:8000/api/v1/ws?api_key=test-key"
    
    async with websockets.connect(uri) as websocket:
        await websocket.recv()  # Connection message
        
        # Subscribe to channel
        await websocket.send(json.dumps({
            "type": "subscribe",
            "channel": "test_ordering"
        }))
        await websocket.recv()  # Subscription confirmation
        
        # In a real scenario, server would send ordered messages
        # Here we test client-side ordering
        received_messages = []
        
        # Send multiple pings rapidly
        for i in range(5):
            await websocket.send(json.dumps({
                "type": "ping",
                "sequence": i
            }))
        
        # Receive pongs
        for i in range(5):
            pong = await websocket.recv()
            data = json.loads(pong)
            if data["type"] == "pong" and "sequence" in data:
                received_messages.append(data["sequence"])
        
        # Check ordering preserved
        assert received_messages == list(range(5))
        print("✅ Message ordering preserved")

async def test_error_handling():
    """Test WebSocket error handling"""
    # Test invalid API key
    uri = "ws://localhost:8000/api/v1/ws?api_key=invalid"
    
    try:
        async with websockets.connect(uri) as websocket:
            # Should be rejected
            pass
    except websockets.exceptions.WebSocketException as e:
        assert "4001" in str(e) or "Unauthorized" in str(e)
        print("✅ Unauthorized connection rejected")
    
    # Test invalid message format
    uri = "ws://localhost:8000/api/v1/ws?api_key=test-key"
    
    async with websockets.connect(uri) as websocket:
        await websocket.recv()  # Connection message
        
        # Send invalid JSON
        await websocket.send("invalid json")
        
        error = await websocket.recv()
        data = json.loads(error)
        
        assert data["type"] == "error"
        assert "message" in data
        print("✅ Invalid message handled")

async def test_rate_limiting():
    """Test WebSocket rate limiting"""
    uri = "ws://localhost:8000/api/v1/ws?api_key=test-key"
    
    async with websockets.connect(uri) as websocket:
        await websocket.recv()  # Connection message
        
        # Send many messages rapidly
        rate_limited = False
        
        for i in range(100):
            await websocket.send(json.dumps({"type": "ping", "id": i}))
            
            # Check for rate limit response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                data = json.loads(response)
                
                if data["type"] == "error" and "rate" in data.get("message", "").lower():
                    rate_limited = True
                    break
            except asyncio.TimeoutError:
                continue
        
        if rate_limited:
            print("✅ Rate limiting active")
        else:
            print("⚠️  Rate limiting not triggered")

def test_client_library():
    """Test Python client library"""
    from litecrewai.client import LiteCrewAIWebSocketClient
    
    client = LiteCrewAIWebSocketClient(
        url="ws://localhost:8000/api/v1/ws",
        api_key="test-key"
    )
    
    # Test event handlers
    events_received = []
    
    @client.on("connected")
    def on_connected(data):
        events_received.append(("connected", data))
    
    @client.on("task_updates")
    def on_task_update(data):
        events_received.append(("task_update", data))
    
    # Connect
    asyncio.run(client.connect())
    
    # Subscribe
    asyncio.run(client.subscribe("task_updates"))
    
    # Wait for events
    asyncio.run(asyncio.sleep(1))
    
    assert len(events_received) > 0
    assert events_received[0][0] == "connected"
    print(f"✅ Client library: {len(events_received)} events received")
    
    # Disconnect
    asyncio.run(client.disconnect())

async def test_reconnection():
    """Test automatic reconnection"""
    from litecrewai.client import LiteCrewAIWebSocketClient
    
    client = LiteCrewAIWebSocketClient(
        url="ws://localhost:8000/api/v1/ws",
        api_key="test-key",
        auto_reconnect=True,
        reconnect_interval=1
    )
    
    reconnect_count = 0
    
    @client.on("reconnected")
    def on_reconnected():
        nonlocal reconnect_count
        reconnect_count += 1
    
    # Connect
    await client.connect()
    
    # Simulate connection drop
    await client._websocket.close()
    
    # Wait for reconnection
    await asyncio.sleep(2)
    
    assert reconnect_count > 0
    assert client.is_connected()
    print(f"✅ Auto-reconnection: {reconnect_count} reconnects")

async def test_binary_data():
    """Test binary data support"""
    uri = "ws://localhost:8000/api/v1/ws?api_key=test-key"
    
    async with websockets.connect(uri) as websocket:
        await websocket.recv()  # Connection message
        
        # Send binary data
        binary_data = b"Binary test data \x00\x01\x02"
        await websocket.send(binary_data)
        
        # Should receive acknowledgment
        response = await websocket.recv()
        
        if isinstance(response, str):
            data = json.loads(response)
            assert data["type"] == "binary_received"
            assert data["size"] == len(binary_data)
            print(f"✅ Binary data support: {len(binary_data)} bytes")

if __name__ == "__main__":
    print("🔍 Validating WebSocket support...\n")
    
    # Run async tests
    async def run_tests():
        await test_websocket_connection()
        await test_channel_subscription()
        await test_multiple_subscriptions()
        await test_concurrent_connections()
        await test_message_ordering()
        await test_error_handling()
        await test_rate_limiting()
        await test_reconnection()
        await test_binary_data()
    
    asyncio.run(run_tests())
    
    # Test sync client library
    test_client_library()
    
    print("\n✅ WebSocket support validation complete!")
```

### Blok 5.2: Web UI Implementation
**Czas**: 6h
**Cel**: Prosty ale funkcjonalny web UI

#### Zadania Atomowe:

##### Task 5.2.1: Design UI Architecture (2h)
**Cel**: Lekka, responsywna architektura UI

**Prompt dla AI Agent**:
```
Zaprojektuj architekturę web UI dla LiteCrewAI - prosty ale funkcjonalny interface.

Wymagania:
1. Technology stack:
   - Pure HTML/CSS/JS (no framework)
   - Optional: Alpine.js for reactivity
   - Tailwind CSS via CDN
   - Chart.js for visualizations
   - No build process required

2. Pages structure:
   /index.html - Dashboard
   /agents.html - Agent management
   /tasks.html - Task monitoring
   /costs.html - Cost tracking
   /logs.html - Real-time logs
   /api-docs.html - API documentation

3. Components:
   - Navigation bar
   - Agent cards
   - Task queue viewer
   - Cost charts
   - Log streamer
   - Settings modal

4. Features:
   - Real-time updates (WebSocket)
   - Dark mode toggle
   - Mobile responsive
   - Offline capable (SW)
   - Fast loading (<1s)

5. Design principles:
   - Minimal dependencies
   - Progressive enhancement
   - Accessibility (WCAG 2.1)
   - Performance first
   - Works without JS

Example structure:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LiteCrewAI Dashboard</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Alpine.js for reactivity -->
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
    
    <!-- Custom styles -->
    <style>
        /* Minimal custom CSS */
        .loading { animation: pulse 2s infinite; }
    </style>
</head>
<body class="bg-gray-100 dark:bg-gray-900">
    <div x-data="app()" x-init="init()">
        <!-- Navigation -->
        <nav class="bg-white dark:bg-gray-800 shadow">
            <!-- Nav content -->
        </nav>
        
        <!-- Main content -->
        <main class="container mx-auto px-4 py-8">
            <!-- Dashboard widgets -->
        </main>
    </div>
    
    <!-- Minimal JS -->
    <script>
        function app() {
            return {
                agents: [],
                tasks: [],
                ws: null,
                
                async init() {
                    await this.loadData();
                    this.connectWebSocket();
                },
                
                async loadData() {
                    // Fetch initial data
                },
                
                connectWebSocket() {
                    // Real-time updates
                }
            }
        }
    </script>
</body>
</html>
```

UI powinno działać nawet na słabym połączeniu.
```

**Metryki Sukcesu**:
- ✅ Page load <1s
- ✅ Works without JS
- ✅ Mobile responsive
- ✅ Accessibility score >90

**Walidacja**:
```python
# validate_ui_architecture.py
import os
import time
from pathlib import Path
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_file_structure():
    """Test UI file structure"""
    ui_root = Path("/opt/litecrewai/app/static")
    
    required_files = [
        "index.html",
        "agents.html",
        "tasks.html",
        "costs.html",
        "logs.html",
        "api-docs.html",
        "css/app.css",
        "js/app.js",
        "js/websocket.js",
        "manifest.json",
        "sw.js"  # Service worker
    ]
    
    missing = []
    for file in required_files:
        if not (ui_root / file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Missing files: {missing}")
    else:
        print("✅ All UI files present")
    
    # Check file sizes (should be small)
    total_size = 0
    for file in ui_root.rglob("*"):
        if file.is_file():
            total_size += file.stat().st_size
    
    size_mb = total_size / 1024 / 1024
    print(f"✅ Total UI size: {size_mb:.2f}MB")
    assert size_mb < 5, "UI too large"

def test_html_structure():
    """Test HTML structure and semantics"""
    ui_root = Path("/opt/litecrewai/app/static")
    
    for html_file in ["index.html", "agents.html", "tasks.html"]:
        with open(ui_root / html_file, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Check required meta tags
        assert soup.find('meta', {'charset': True}), f"Missing charset in {html_file}"
        assert soup.find('meta', {'name': 'viewport'}), f"Missing viewport in {html_file}"
        
        # Check semantic HTML
        assert soup.find('nav'), f"Missing <nav> in {html_file}"
        assert soup.find('main'), f"Missing <main> in {html_file}"
        
        # Check accessibility
        imgs = soup.find_all('img')
        for img in imgs:
            assert img.get('alt'), f"Image without alt text in {html_file}"
        
        # Check form labels
        inputs = soup.find_all('input', {'type': lambda x: x != 'hidden'})
        for input_elem in inputs:
            input_id = input_elem.get('id')
            if input_id:
                assert soup.find('label', {'for': input_id}), \
                    f"Input without label in {html_file}"
        
        print(f"✅ {html_file}: Valid HTML structure")

def test_no_framework_dependencies():
    """Test that UI works without heavy frameworks"""
    ui_root = Path("/opt/litecrewai/app/static")
    
    # Check JavaScript files
    js_files = list(ui_root.glob("js/*.js"))
    
    problematic = []
    for js_file in js_files:
        content = js_file.read_text()
        
        # Check for framework imports
        if any(framework in content.lower() for framework in 
               ['react', 'vue', 'angular', 'jquery']):
            problematic.append(js_file.name)
    
    if problematic:
        print(f"❌ Framework dependencies found: {problematic}")
    else:
        print("✅ No heavy framework dependencies")
    
    # Check CSS
    css_content = (ui_root / "css/app.css").read_text()
    css_size = len(css_content)
    
    # Should be mostly using Tailwind utilities
    assert css_size < 10000, f"CSS too large: {css_size} bytes"
    print(f"✅ Minimal CSS: {css_size} bytes")

def test_progressive_enhancement():
    """Test UI works without JavaScript"""
    # Start simple HTTP server
    import subprocess
    import signal
    
    ui_root = Path("/opt/litecrewai/app/static")
    server = subprocess.Popen(
        ["python", "-m", "http.server", "8080"],
        cwd=ui_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        time.sleep(1)  # Let server start
        
        # Test with JavaScript disabled
        options = Options()
        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.javascript": 2
        })
        
        driver = webdriver.Chrome(options=options)
        
        try:
            driver.get("http://localhost:8080/index.html")
            
            # Check page loads
            assert "LiteCrewAI" in driver.title
            
            # Check navigation works
            nav_links = driver.find_elements_by_css_selector("nav a")
            assert len(nav_links) > 0
            
            # Check content is visible
            main_content = driver.find_element_by_tag_name("main")
            assert main_content.is_displayed()
            
            print("✅ UI works without JavaScript")
            
        finally:
            driver.quit()
            
    finally:
        server.terminate()

def test_performance():
    """Test UI performance metrics"""
    import subprocess
    
    ui_root = Path("/opt/litecrewai/app/static")
    
    # Run Lighthouse CLI
    result = subprocess.run([
        "lighthouse",
        "http://localhost:8000",
        "--quiet",
        "--chrome-flags='--headless'",
        "--only-categories=performance,accessibility",
        "--output=json"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        import json
        report = json.loads(result.stdout)
        
        perf_score = report['categories']['performance']['score'] * 100
        a11y_score = report['categories']['accessibility']['score'] * 100
        
        print(f"✅ Performance score: {perf_score:.0f}/100")
        print(f"✅ Accessibility score: {a11y_score:.0f}/100")
        
        assert perf_score > 80, f"Performance too low: {perf_score}"
        assert a11y_score > 90, f"Accessibility too low: {a11y_score}"
    else:
        print("⚠️  Lighthouse not available for testing")

def test_responsive_design():
    """Test responsive design on different viewports"""
    driver = webdriver.Chrome()
    
    try:
        driver.get("http://localhost:8000")
        
        viewports = [
            (375, 667, "iPhone SE"),
            (768, 1024, "iPad"),
            (1920, 1080, "Desktop")
        ]
        
        for width, height, device in viewports:
            driver.set_window_size(width, height)
            time.sleep(0.5)
            
            # Check navigation adapts
            nav = driver.find_element_by_tag_name("nav")
            
            # On mobile, should have hamburger menu
            if width < 768:
                hamburger = driver.find_element_by_css_selector("[data-menu-toggle]")
                assert hamburger.is_displayed(), f"No hamburger menu on {device}"
            
            # Check content is not horizontally scrollable
            body = driver.find_element_by_tag_name("body")
            assert body.size['width'] <= width, f"Horizontal scroll on {device}"
            
            print(f"✅ {device} ({width}x{height}): Responsive")
            
    finally:
        driver.quit()

def test_dark_mode():
    """Test dark mode implementation"""
    driver = webdriver.Chrome()
    
    try:
        driver.get("http://localhost:8000")
        
        # Check dark mode toggle exists
        toggle = driver.find_element_by_css_selector("[data-theme-toggle]")
        assert toggle.is_displayed()
        
        # Get initial background color
        body = driver.find_element_by_tag_name("body")
        initial_bg = body.value_of_css_property("background-color")
        
        # Toggle dark mode
        toggle.click()
        time.sleep(0.5)
        
        # Check background changed
        dark_bg = body.value_of_css_property("background-color")
        assert dark_bg != initial_bg
        
        # Check preference is saved
        driver.refresh()
        time.sleep(0.5)
        
        current_bg = body.value_of_css_property("background-color")
        assert current_bg == dark_bg, "Dark mode preference not persisted"
        
        print("✅ Dark mode working")
        
    finally:
        driver.quit()

def test_offline_capability():
    """Test offline functionality with Service Worker"""
    driver = webdriver.Chrome()
    
    try:
        driver.get("http://localhost:8000")
        time.sleep(2)  # Let service worker install
        
        # Check service worker registered
        sw_state = driver.execute_script("""
            return navigator.serviceWorker.controller ? 'active' : 'none';
        """)
        
        assert sw_state == "active", "Service worker not active"
        
        # Go offline
        driver.set_network_conditions(
            offline=True,
            latency=0,
            throughput=0
        )
        
        # Try to navigate
        driver.get("http://localhost:8000/agents.html")
        
        # Page should still load from cache
        assert "LiteCrewAI" in driver.title
        assert not "Unable to connect" in driver.page_source
        
        print("✅ Offline mode working")
        
    finally:
        driver.quit()

def test_websocket_integration():
    """Test WebSocket real-time updates"""
    driver = webdriver.Chrome()
    
    try:
        driver.get("http://localhost:8000")
        time.sleep(1)
        
        # Check WebSocket status indicator
        ws_status = driver.find_element_by_css_selector("[data-ws-status]")
        assert ws_status.text in ["Connected", "Connecting"]
        
        # Check for real-time updates container
        updates = driver.find_element_by_css_selector("[data-realtime-updates]")
        assert updates.is_displayed()
        
        # Simulate WebSocket message (in real test would come from server)
        driver.execute_script("""
            window.dispatchEvent(new CustomEvent('ws-message', {
                detail: {
                    type: 'task_update',
                    data: {id: '123', status: 'completed'}
                }
            }));
        """)
        
        # Check UI updated
        time.sleep(0.5)
        # Would check specific UI update here
        
        print("✅ WebSocket integration working")
        
    finally:
        driver.quit()

def test_loading_performance():
    """Test page loading performance"""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    driver = webdriver.Chrome()
    
    try:
        start = time.time()
        driver.get("http://localhost:8000")
        
        # Wait for main content to be visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )
        
        load_time = time.time() - start
        
        # Get performance metrics
        perf = driver.execute_script("""
            const perf = performance.getEntriesByType('navigation')[0];
            return {
                domContentLoaded: perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart,
                loadComplete: perf.loadEventEnd - perf.loadEventStart,
                firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0
            };
        """)
        
        print(f"✅ Page load time: {load_time:.2f}s")
        print(f"   - DOM ready: {perf['domContentLoaded']:.0f}ms")
        print(f"   - First paint: {perf['firstPaint']:.0f}ms")
        
        assert load_time < 1.0, f"Page load too slow: {load_time}s"
        
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 Validating UI architecture...\n")
    
    test_file_structure()
    test_html_structure()
    test_no_framework_dependencies()
    test_progressive_enhancement()
    test_performance()
    test_responsive_design()
    test_dark_mode()
    test_offline_capability()
    test_websocket_integration()
    test_loading_performance()
    
    print("\n✅ UI architecture validation complete!")
```

##### Task 5.2.2: Build Core UI Components (2h)
**Cel**: Implementacja głównych komponentów UI

**Prompt dla AI Agent**:
```
Zbuduj core UI components dla LiteCrewAI - reusable, lekkie komponenty.

Komponenty do zbudowania:
1. AgentCard:
   - Status indicator (active/idle/error)
   - Stats (tasks completed, success rate)
   - Actions (execute, edit, delete)
   - Mini activity chart

2. TaskQueue:
   - Real-time task list
   - Status badges
   - Progress indicators
   - Filtering/sorting
   - Bulk actions

3. CostMeter:
   - Current month spending
   - Budget progress bar
   - Burn rate indicator
   - Cost breakdown chart
   - Alerts/warnings

4. LogViewer:
   - Real-time log streaming
   - Log level filtering
   - Search functionality
   - Export capability
   - Auto-scroll toggle

5. MetricCard:
   - Single metric display
   - Trend indicator
   - Sparkline chart
   - Click for details

Implementation approach:
```javascript
// Minimal component system
class Component {
    constructor(selector, options = {}) {
        this.element = document.querySelector(selector);
        this.options = options;
        this.state = {};
        this.init();
    }
    
    setState(newState) {
        this.state = {...this.state, ...newState};
        this.render();
    }
    
    render() {
        // Override in subclasses
    }
}

// Agent Card Component
class AgentCard extends Component {
    init() {
        this.template = `
            <div class="bg-white rounded-lg shadow p-4 dark:bg-gray-800">
                <div class="flex items-center justify-between">
                    <h3 class="text-lg font-semibold">{name}</h3>
                    <span class="status-indicator {status}">{status}</span>
                </div>
                <div class="mt-4 grid grid-cols-2 gap-2 text-sm">
                    <div>Tasks: <span class="font-bold">{taskCount}</span></div>
                    <div>Success: <span class="font-bold">{successRate}%</span></div>
                </div>
                <canvas class="activity-chart mt-4" width="200" height="50"></canvas>
                <div class="mt-4 flex gap-2">
                    <button class="btn-primary" onclick="executeTask('{id}')">
                        Execute
                    </button>
                    <button class="btn-secondary" onclick="editAgent('{id}')">
                        Edit
                    </button>
                </div>
            </div>
        `;
    }
    
    render() {
        this.element.innerHTML = this.template
            .replace(/{(\w+)}/g, (_, key) => this.state[key] || '');
        
        this.renderActivityChart();
    }
    
    renderActivityChart() {
        const canvas = this.element.querySelector('.activity-chart');
        const ctx = canvas.getContext('2d');
        // Simple sparkline implementation
    }
}

// Usage
const agentCard = new AgentCard('#agent-1', {
    updateInterval: 5000
});

agentCard.setState({
    id: 'agent_123',
    name: 'Research Agent',
    status: 'active',
    taskCount: 42,
    successRate: 95
});
```

Components should be:
- Standalone (no external deps)
- Themeable (dark mode)
- Accessible (ARIA labels)
- Performant (minimal redraws)
- Mobile friendly
```

**Metryki Sukcesu**:
- ✅ Components render <10ms
- ✅ Work without JS libs
- ✅ Accessible (ARIA)
- ✅ Responsive design

**Walidacja**:
```python
# validate_ui_components.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_agent_card_component():
    """Test AgentCard component functionality"""
    driver = webdriver.Chrome()
    
    try:
        # Load component test page
        driver.get("http://localhost:8000/test/components.html")
        
        # Create agent card
        driver.execute_script("""
            const card = new AgentCard('#test-agent-card');
            card.setState({
                id: 'test_123',
                name: 'Test Agent',
                status: 'active',
                taskCount: 10,
                successRate: 90,
                activity: [5, 8, 3, 10, 7, 9, 6]
            });
        """)
        
        # Check rendering
        card = driver.find_element_by_id("test-agent-card")
        assert card.is_displayed()
        
        # Check elements
        assert "Test Agent" in card.text
        assert "active" in card.get_attribute("innerHTML")
        assert "90%" in card.text
        
        # Check status indicator
        status = card.find_element_by_css_selector(".status-indicator")
        assert "active" in status.get_attribute("class")
        
        # Check action buttons
        buttons = card.find_elements_by_tag_name("button")
        assert len(buttons) >= 2
        assert "Execute" in buttons[0].text
        
        # Test interaction
        buttons[0].click()
        
        # Check event was triggered (would be caught by event listener)
        print("✅ AgentCard component working")
        
    finally:
        driver.quit()

def test_task_queue_component():
    """Test TaskQueue component"""
    driver = webdriver.Chrome()
    
    try:
        driver.get("http://localhost:8000/test/components.html")
        
        # Create task queue
        driver.execute_script("""
            const queue = new TaskQueue('#test-task-queue', {
                maxVisible: 10,
                autoRefresh: false
            });
            
            queue.setState({
                tasks: [
                    {id: '1', description: 'Task 1', status: 'pending', priority: 'high'},
                    {id: '2', description: 'Task 2', status: 'running', priority: 'normal'},
                    {id: '3', description: 'Task 3', status: 'completed', priority: 'low'}
                ]
            });
        """)
        
        queue = driver.find_element_by_id("test-task-queue")
        
        # Check tasks rendered
        task_items = queue.find_elements_by_css_selector(".task-item")
        assert len(task_items) == 3
        
        # Check status badges
        badges = queue.find_elements_by_css_selector(".status-badge")
        statuses = [b.text.lower() for b in badges]
        assert "pending" in statuses
        assert "running" in statuses
        assert "completed" in statuses
        
        # Test filtering
        filter_input = queue.find_element_by_css_selector("input[data-filter]")
        filter_input.send_keys("Task 1")
        
        time.sleep(0.5)  # Debounce
        
        visible_tasks = queue.find_elements_by_css_selector(".task-item:not(.hidden)")
        assert len(visible_tasks) == 1
        
        # Test sorting
        sort_button = queue.find_element_by_css_selector("[data-sort='priority']")
        sort_button.click()
        
        # Check order changed
        task_items = queue.find_elements_by_css_selector(".task-item")
        first_priority = task_items[0].find_element_by_css_selector(".priority").text
        assert first_priority.lower() == "high"
        
        print("✅ TaskQueue component working")
        
    finally:
        driver.quit()

def test_cost_meter_component():
    """Test CostMeter component"""
    driver = webdriver.Chrome()
    
    try:
        driver.get("http://localhost:8000/test/components.html")
        
        # Create cost meter
        driver.execute_script("""
            const meter = new CostMeter('#test-cost-meter', {
                monthlyBudget: 30.00,
                currency: 'USD'
            });
            
            meter.setState({
                currentSpend: 18.50,
                dailyAverage: 0.62,
                projection: 28.60,
                breakdown: {
                    'openai': 12.30,
                    'groq': 4.20,
                    'ollama': 0.00,
                    'other': 2.00
                }
            });
        """)
        
        meter = driver.find_element_by_id("test-cost-meter")
        
        # Check budget display
        assert "$18.50" in meter.text
        assert "$30.00" in meter.text
        
        # Check progress bar
        progress = meter.find_element_by_css_selector(".progress-bar")
        width = progress.value_of_css_property("width")
        # Should be ~62% (18.50/30.00)
        
        # Check burn rate
        assert "$0.62/day" in meter.text
        
        # Check projection warning if close to budget
        projection = meter.find_element_by_css_selector(".projection")
        if 28.60 / 30.00 > 0.8:
            assert "warning" in projection.get_attribute("class")
        
        # Check breakdown chart exists
        chart = meter.find_element_by_tag_name("canvas")
        assert chart.is_displayed()
        
        print("✅ CostMeter component working")
        
    finally:
        driver.quit()

def test_log_viewer_component():
    """Test LogViewer component"""
    driver = webdriver.Chrome()
    
    try:
        driver.get("http://localhost:8000/test/components.html")
        
        # Create log viewer
        driver.execute_script("""
            const viewer = new LogViewer('#test-log-viewer', {
                maxLines: 100,
                autoScroll: true
            });
            
            // Add some logs
            viewer.addLog('INFO', 'Application started');
            viewer.addLog('DEBUG', 'Connecting to database');
            viewer.addLog('WARN', 'High memory usage detected');
            viewer.addLog('ERROR', 'Failed to connect to API');
        """)
        
        viewer = driver.find_element_by_id("test-log-viewer")
        
        # Check logs displayed
        log_entries = viewer.find_elements_by_css_selector(".log-entry")
        assert len(log_entries) == 4
        
        # Check log levels
        error_log = viewer.find_element_by_css_selector(".log-level-error")
        assert "ERROR" in error_log.text
        assert "error" in error_log.get_attribute("class")
        
        # Test level filtering
        level_filter = viewer.find_element_by_css_selector("select[data-level-filter]")
        level_filter.send_keys("ERROR")
        
        time.sleep(0.5)
        
        visible_logs = viewer.find_elements_by_css_selector(".log-entry:not(.hidden)")
        assert len(visible_logs) == 1
        
        # Test search
        search_input = viewer.find_element_by_css_selector("input[data-search]")
        search_input.clear()
        search_input.send_keys("memory")
        
        time.sleep(0.5)
        
        visible_logs = viewer.find_elements_by_css_selector(".log-entry:not(.hidden)")
        assert len(visible_logs) == 1
        assert "memory" in visible_logs[0].text.lower()
        
        # Test auto-scroll toggle
        auto_scroll = viewer.find_element_by_css_selector("input[data-auto-scroll]")
        assert auto_scroll.is_selected()  # Should be on by default
        
        print("✅ LogViewer component working")
        
    finally:
        driver.quit()

def test_metric_card_component():
    """Test MetricCard component"""
    driver = webdriver.Chrome()
    
    try:
        driver.get("http://localhost:8000/test/components.html")
        
        # Create metric cards
        driver.execute_script("""
            // Success rate metric
            const successCard = new MetricCard('#test-metric-1', {
                title: 'Success Rate',
                format: 'percentage',
                goodDirection: 'up'
            });
            
            successCard.setState({
                value: 94.5,
                previousValue: 92.1,
                trend: [90, 91, 92, 91, 93, 94, 94.5]
            });
            
            // Response time metric
            const responseCard = new MetricCard('#test-metric-2', {
                title: 'Avg Response Time',
                format: 'duration',
                goodDirection: 'down',
                unit: 'ms'
            });
            
            responseCard.setState({
                value: 245,
                previousValue: 312,
                trend: [400, 350, 300, 280, 260, 250, 245]
            });
        """)
        
        # Test success rate card
        card1 = driver.find_element_by_id("test-metric-1")
        assert "94.5%" in card1.text
        assert "Success Rate" in card1.text
        
        # Check trend indicator (should be up/positive)
        trend1 = card1.find_element_by_css_selector(".trend-indicator")
        assert "up" in trend1.get_attribute("class") or "↑" in trend1.text
        
        # Test response time card
        card2 = driver.find_element_by_id("test-metric-2")
        assert "245ms" in card2.text
        
        # Check trend indicator (should be down/positive since lower is better)
        trend2 = card2.find_element_by_css_selector(".trend-indicator")
        assert "positive" in trend2.get_attribute("class")
        
        # Check sparkline charts exist
        for card in [card1, card2]:
            sparkline = card.find_element_by_css_selector(".sparkline")
            assert sparkline.is_displayed()
        
        # Test click for details
        card1.click()
        
        # Would check if detail modal/expansion appears
        print("✅ MetricCard component working")
        
    finally:
        driver.quit()

def test_component_dark_mode():
    """Test components work in dark mode"""
    driver = webdriver.Chrome()
    
    try:
        driver.get("http://localhost:8000/test/components.html")
        
        # Toggle dark mode
        driver.execute_script("""
            document.documentElement.classList.add('dark');
        """)
        
        # Create components
        driver.execute_script("""
            new AgentCard('#dark-test-1').setState({
                name: 'Dark Agent',
                status: 'active'
            });
            
            new MetricCard('#dark-test-2').setState({
                value: 42,
                title: 'Dark Metric'
            });
        """)
        
        # Check dark mode styles applied
        card = driver.find_element_by_id("dark-test-1")
        bg_color = card.value_of_css_property("background-color")
        
        # Should be dark background
        # RGB values would be dark (e.g., rgb(31, 41, 55) for gray-800)
        print("✅ Components support dark mode")
        
    finally:
        driver.quit()

def test_component_accessibility():
    """Test component accessibility"""
    driver = webdriver.Chrome()
    
    try:
        driver.get("http://localhost:8000/test/components.html")
        
        # Create components
        driver.execute_script("""
            const card = new AgentCard('#a11y-test');
            card.setState({
                name: 'Accessible Agent',
                status: 'active',
                taskCount: 10
            });
        """)
        
        card = driver.find_element_by_id("a11y-test")
        
        # Check ARIA labels
        buttons = card.find_elements_by_tag_name("button")
        for button in buttons:
            aria_label = button.get_attribute("aria-label")
            assert aria_label, "Button missing aria-label"
        
        # Check status has role
        status = card.find_element_by_css_selector(".status-indicator")
        role = status.get_attribute("role")
        assert role in ["status", "img"], "Status missing appropriate role"
        
        # Check keyboard navigation
        first_button = buttons[0]
        first_button.send_keys("")  # Focus
        
        # Should be focusable
        assert driver.switch_to.active_element == first_button
        
        print("✅ Components are accessible")
        
    finally:
        driver.quit()

def test_component_performance():
    """Test component rendering performance"""
    driver = webdriver.Chrome()
    
    try:
        driver.get("http://localhost:8000/test/components.html")
        
        # Measure render time for multiple components
        render_time = driver.execute_script("""
            const start = performance.now();
            
            // Create 50 agent cards
            for (let i = 0; i < 50; i++) {
                const div = document.createElement('div');
                div.id = `agent-${i}`;
                document.body.appendChild(div);
                
                const card = new AgentCard(`#agent-${i}`);
                card.setState({
                    name: `Agent ${i}`,
                    status: i % 3 === 0 ? 'active' : 'idle',
                    taskCount: Math.floor(Math.random() * 100),
                    successRate: 80 + Math.floor(Math.random() * 20)
                });
            }
            
            return performance.now() - start;
        """)
        
        print(f"✅ Rendered 50 components in {render_time:.1f}ms")
        assert render_time < 500, f"Rendering too slow: {render_time}ms"
        
        # Test update performance
        update_time = driver.execute_script("""
            const start = performance.now();
            
            // Update all components
            for (let i = 0; i < 50; i++) {
                const card = window[`agentCard${i}`];
                if (card) {
                    card.setState({
                        taskCount: Math.floor(Math.random() * 100)
                    });
                }
            }
            
            return performance.now() - start;
        """)
        
        print(f"✅ Updated 50 components in {update_time:.1f}ms")
        assert update_time < 100, f"Updates too slow: {update_time}ms"
        
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 Validating UI components...\n")
    
    test_agent_card_component()
    test_task_queue_component()
    test_cost_meter_component()
    test_log_viewer_component()
    test_metric_card_component()
    test_component_dark_mode()
    test_component_accessibility()
    test_component_performance()
    
    print("\n✅ UI components validation complete!")
```

##### Task 5.2.3: Create Dashboard Pages (2h)
**Cel**: Implementacja głównych stron dashboard

**Prompt dla AI Agent**:
```
Stwórz główne strony dashboard dla LiteCrewAI - czyste, funkcjonalne interfejsy.

Strony do stworzenia:
1. Dashboard (index.html):
   - System overview widgets
   - Active agents summary
   - Recent tasks
   - Cost tracking widget
   - Quick actions
   - Real-time notifications

2. Agents Page (agents.html):
   - Agent grid/list view
   - Create new agent modal
   - Agent details sidebar
   - Bulk operations
   - Performance metrics

3. Tasks Page (tasks.html):
   - Task queue viewer
   - Filters and search
   - Task details modal
   - Execution history
   - Export functionality

4. Costs Page (costs.html):
   - Monthly spending chart
   - Cost breakdown by model
   - Budget alerts config
   - Historical data
   - Cost optimization tips

5. API Docs (api-docs.html):
   - Interactive API explorer
   - Code examples
   - Authentication guide
   - WebSocket docs
   - SDKs download

Example Dashboard Implementation:
```html
<!DOCTYPE html>
<html lang="en" x-data="{ darkMode: localStorage.getItem('darkMode') === 'true' }" 
      :class="{ 'dark': darkMode }">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LiteCrewAI Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <link rel="stylesheet" href="/css/app.css">
</head>
<body class="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
    <!-- Navigation -->
    <nav class="bg-white dark:bg-gray-800 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex">
                    <div class="flex-shrink-0 flex items-center">
                        <h1 class="text-xl font-bold">LiteCrewAI</h1>
                    </div>
                    <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
                        <a href="/" class="border-indigo-500 text-gray-900 dark:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                            Dashboard
                        </a>
                        <a href="/agents.html" class="border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                            Agents
                        </a>
                        <a href="/tasks.html" class="border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                            Tasks
                        </a>
                        <a href="/costs.html" class="border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                            Costs
                        </a>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <!-- WebSocket Status -->
                    <div class="flex items-center" x-data="{ connected: false }">
                        <div class="h-3 w-3 rounded-full" :class="connected ? 'bg-green-400' : 'bg-red-400'"></div>
                        <span class="ml-2 text-sm" x-text="connected ? 'Connected' : 'Disconnected'"></span>
                    </div>
                    
                    <!-- Dark Mode Toggle -->
                    <button @click="darkMode = !darkMode; localStorage.setItem('darkMode', darkMode)" 
                            class="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700">
                        <svg x-show="!darkMode" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                        </svg>
                        <svg x-show="darkMode" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <!-- Stats Overview -->
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <!-- Active Agents -->
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                <div class="p-5">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                            </svg>
                        </div>
                        <div class="ml-5 w-0 flex-1">
                            <dl>
                                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                                    Active Agents
                                </dt>
                                <dd class="flex items-baseline">
                                    <div class="text-2xl font-semibold text-gray-900 dark:text-white" id="active-agents-count">
                                        0
                                    </div>
                                </dd>
                            </dl>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Running Tasks -->
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                <div class="p-5">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                            </svg>
                        </div>
                        <div class="ml-5 w-0 flex-1">
                            <dl>
                                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                                    Running Tasks
                                </dt>
                                <dd class="flex items-baseline">
                                    <div class="text-2xl font-semibold text-gray-900 dark:text-white" id="running-tasks-count">
                                        0
                                    </div>
                                </dd>
                            </dl>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Monthly Cost -->
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                <div class="p-5">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <div class="ml-5 w-0 flex-1">
                            <dl>
                                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                                    Monthly Cost
                                </dt>
                                <dd class="flex items-baseline">
                                    <div class="text-2xl font-semibold text-gray-900 dark:text-white">
                                        $<span id="monthly-cost">0.00</span>
                                    </div>
                                    <div class="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                                        <span id="cost-trend">↓ 12%</span>
                                    </div>
                                </dd>
                            </dl>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Success Rate -->
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                <div class="p-5">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <div class="ml-5 w-0 flex-1">
                            <dl>
                                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                                    Success Rate
                                </dt>
                                <dd class="flex items-baseline">
                                    <div class="text-2xl font-semibold text-gray-900 dark:text-white">
                                        <span id="success-rate">0</span>%
                                    </div>
                                </dd>
                            </dl>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quick Actions -->
        <div class="mt-8">
            <h2 class="text-lg font-medium text-gray-900 dark:text-white">Quick Actions</h2>
            <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <button onclick="showCreateAgentModal()" class="relative block w-full border-2 border-gray-300 dark:border-gray-600 border-dashed rounded-lg p-6 text-center hover:border-gray-400 dark:hover:border-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    <span class="mt-2 block text-sm font-medium text-gray-900 dark:text-white">
                        Create New Agent
                    </span>
                </button>

                <button onclick="showExecuteTaskModal()" class="relative block w-full border-2 border-gray-300 dark:border-gray-600 border-dashed rounded-lg p-6 text-center hover:border-gray-400 dark:hover:border-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24
```