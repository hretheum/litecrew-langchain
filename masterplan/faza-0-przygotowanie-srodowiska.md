# FAZA 0: PRZYGOTOWANIE ŚRODOWISKA

[← Powrót do README](./README.md) | [← Wprowadzenie](./00-wprowadzenie.md) | [Następna faza: Fork i Minimalizacja →](./faza-1-fork.md)

**Czas**: 3 dni  
**Cel**: Przygotowanie kompletnej infrastruktury i środowiska developerskiego

## Milestones
- M0.1: Infrastruktura DigitalOcean gotowa
- M0.2: Środowisko developerskie skonfigurowane
- M0.3: CI/CD pipeline działający

---

## Blok 0.1: Setup DigitalOcean Infrastructure
**Czas**: 8h
**Cel**: Przygotowanie kompletnej infrastruktury cloud

### Zadania Atomowe:

#### Task 0.1.1: Utworzenie i Konfiguracja Droplet (2h)
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
[→ Zobacz skrypt: validate_droplet_setup.sh](./src/faza-0/validate_droplet_setup.sh)

#### Task 0.1.2: Instalacja Core Dependencies (3h)
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
[→ Zobacz skrypt: validate_dependencies.py](./src/faza-0/validate_dependencies.py)

#### Task 0.1.3: Setup Project Directory Structure (1h)
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
[→ Zobacz skrypt: validate_directory_structure.sh](./src/faza-0/validate_directory_structure.sh)

---

## Blok 0.2: Development Environment Setup
**Czas**: 6h
**Cel**: Kompletne środowisko developerskie lokalne i na serwerze

### Zadania Atomowe:

#### Task 0.2.1: Python Virtual Environment (2h)
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
[→ Zobacz skrypt: validate_python_env.py](./src/faza-0/validate_python_env.py)

#### Task 0.2.2: Local Ollama Setup (2h)
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
[→ Zobacz skrypt: validate_ollama.py](./src/faza-0/validate_ollama.py)

#### Task 0.2.3: Git Repository and CI/CD Setup (2h)
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
[→ Zobacz skrypt: validate_cicd.sh](./src/faza-0/validate_cicd.sh)

---

## Blok 0.3: Monitoring and Logging Infrastructure
**Czas**: 4h
**Cel**: Kompletny system monitorowania od początku

### Zadania Atomowe:

#### Task 0.3.1: Setup Logging System (2h)
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
[→ Zobacz skrypt: validate_logging.py](./src/faza-0/validate_logging.py)

#### Task 0.3.2: Setup Monitoring and Metrics (2h)
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
[→ Zobacz skrypt: validate_monitoring.py](./src/faza-0/validate_monitoring.py)

---

## Podsumowanie Fazy 0

Faza 0 tworzy solidne fundamenty dla całego projektu LiteCrewAI:

1. **Infrastruktura**: Bezpieczny serwer na DigitalOcean z wszystkimi zależnościami
2. **Środowisko**: Profesjonalne środowisko Python z narzędziami QA
3. **LLM**: Lokalna instalacja Ollama z modelami
4. **CI/CD**: Automatyzacja deploymentu przez GitHub Actions
5. **Monitoring**: Kompletny system logowania i monitorowania

Po ukończeniu tej fazy mamy gotową platformę do rozwoju właściwej aplikacji LiteCrewAI.


---

[← Powrót do README](./README.md) | [← Wprowadzenie](./00-wprowadzenie.md) | [Następna faza: Fork i Minimalizacja →](./faza-1-fork.md)
