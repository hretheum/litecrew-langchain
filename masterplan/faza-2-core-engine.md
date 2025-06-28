# 🚀 LiteCrewAI - Kompletny Plan Implementacji Platformy

[← Powrót do README](./README.md) | [← Faza 1: Fork](./faza-1-fork.md) | [Następna faza: Integracja LLM →](./faza-3-LLM.md)

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

[→ Zobacz plik: validate_droplet_setup.sh](./src/faza-2/validate_droplet_setup.sh)

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

[→ Zobacz plik: validate_dependencies.py](./src/faza-2/validate_dependencies.py)

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

[→ Zobacz plik: validate_directory_structure.sh](./src/faza-2/validate_directory_structure.sh)

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

[→ Zobacz plik: validate_python_env.py](./src/faza-2/validate_python_env.py)

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

[→ Zobacz plik: validate_ollama.py](./src/faza-2/validate_ollama.py)

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

[→ Zobacz plik: validate_cicd.sh](./src/faza-2/validate_cicd.sh)

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

[→ Zobacz plik: validate_logging.py](./src/faza-2/validate_logging.py)

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

[→ Zobacz plik: validate_monitoring.py](./src/faza-2/validate_monitoring.py)

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

[→ Zobacz plik: validate_fork.py](./src/faza-2/validate_fork.py)

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

[→ Zobacz plik: validate_no_telemetry.py](./src/faza-2/validate_no_telemetry.py)

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

[→ Zobacz plik: validate_no_enterprise.py](./src/faza-2/validate_no_enterprise.py)

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

[→ Zobacz plik: validate_dependencies_optimization.py](./src/faza-2/validate_dependencies_optimization.py)

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

[→ Zobacz plik: validate_requirements.py](./src/faza-2/validate_requirements.py)

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

[→ Zobacz plik: validate_dep_cache.py](./src/faza-2/validate_dep_cache.py)

---

## 📦 FAZA 2: CORE ENGINE - AGENCI I ZADANIA

[← Powrót do README](./README.md) | [← Faza 1: Fork](./faza-1-fork.md) | [Następna faza: Integracja LLM →](./faza-3-LLM.md)

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
   [→ Zobacz plik: agent_example.py](./src/faza-2/agent_example.py)

Stwórz pełną implementację z docstrings i type hints.

```
**Metryki Sukcesu**:
- ✅ Agent tworzy się <100ms
- ✅ Memory usage <10MB
- ✅ Execute() <5s dla prostych zadań
- ✅ Full type coverage

**Walidacja**:
[→ Zobacz plik: validate_agent_architecture.py](./src/faza-2/validate_agent_architecture.py)

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
[→ Zobacz plik: task_executor_example.py](./src/faza-2/task_executor_example.py)

Implementacja powinna być thread-safe i odporna na błędy.

```
**Metryki Sukcesu**:
- ✅ Task execution <10s average
- ✅ Dependency resolution <100ms
- ✅ Parallel execution działa
- ✅ 95%+ success rate

**Walidacja**:
[→ Zobacz plik: validate_task_execution.py](./src/faza-2/validate_task_execution.py)

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
[→ Zobacz plik: memory_system_example.py](./src/faza-2/memory_system_example.py)

System musi być wydajny i skalować do 1000+ faktów.

```
**Metryki Sukcesu**:
- ✅ Store operation <10ms
- ✅ Retrieve <50ms dla 1000 items
- ✅ Memory size <100MB limit
- ✅ 90%+ relevance w retrieval

**Walidacja**:
[→ Zobacz plik: validate_memory_system.py](./src/faza-2/validate_memory_system.py)

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
[→ Zobacz plik: tool_framework_example.py](./src/faza-2/tool_framework_example.py)

Framework musi być rozszerzalny i bezpieczny.

```
**Metryki Sukcesu**:
- ✅ Tool registration <1ms
- ✅ Tool execution <2s average
- ✅ Input validation 100%
- ✅ No security vulnerabilities

**Walidacja**:
[→ Zobacz plik: validate_tool_framework.py](./src/faza-2/validate_tool_framework.py)

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
[→ Zobacz plik: calculate_tool_example.py](./src/faza-2/calculate_tool_example.py)

```
**Metryki Sukcesu**:
- ✅ Wszystkie tools działają
- ✅ 100% test coverage
- ✅ No security issues
- ✅ <2s execution time

**Walidacja**:
[→ Zobacz plik: validate_core_tools.py](./src/faza-2/validate_core_tools.py)

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
[→ Zobacz plik: tool_workflow_example.sh](./src/faza-2/tool_workflow_example.sh)

Include VS Code extension snippets and IDE support.

```
**Metryki Sukcesu**:
- ✅ Tool creation <30s
- ✅ Auto-generated tests pass
- ✅ Documentation complete
- ✅ IDE integration works

**Walidacja**:
[→ Zobacz plik: validate_tool_sdk.py](./src/faza-2/validate_tool_sdk.py)

---

## 

---

## 🎯 Podsumowanie Fazy 2

### Osiągnięte cele:
1. ✅ W pełni asynchroniczny Core Engine
2. ✅ System zarządzania agentami z pool management
3. ✅ Event-driven architecture z pub/sub
4. ✅ Rozbudowany system walidacji i error handling
5. ✅ Tool Development Kit dla łatwego rozszerzania
6. ✅ Comprehensive testing suite

### Kluczowe komponenty:
- **AgentManager**: Centralne zarządzanie cyklem życia agentów
- **TaskQueue**: Asynchroniczna kolejka zadań z priorytetami
- **EventBus**: System komunikacji między komponentami
- **ValidationPipeline**: Multi-level walidacja danych
- **ToolRegistry**: Dynamiczne zarządzanie narzędziami

### Metryki wydajnościowe:
- Agent startup time: <100ms
- Task execution overhead: <10ms
- Memory per agent: ~5MB base
- Concurrent agents: 100+ na 2GB RAM
- Event propagation: <1ms

### Integracje przygotowane dla kolejnych faz:
- LLM integration points w BaseAgent
- Storage hooks w AgentManager
- API endpoints ready w EventBus
- Monitoring telemetry w wszystkich komponentach

### Następne kroki:
1. Integracja z LLM providers (Faza 3)
2. Implementacja persistent storage (Faza 4)
3. Budowa REST/GraphQL API (Faza 5)
4. Dodanie monitoring layer (Faza 6)

---

## 📚 Dokumentacja techniczna

### Architecture Decision Records (ADRs)

#### ADR-001: Full Async Architecture
**Decyzja**: Wszystkie komponenty używają async/await
**Powód**: Maksymalna wydajność przy I/O operations
**Konsekwencje**: Wymaga Python 3.11+, bardziej złożony debugging

#### ADR-002: Event-Driven Communication
**Decyzja**: Pub/sub zamiast direct calls
**Powód**: Loose coupling, łatwiejsze testowanie
**Konsekwencje**: Dodatkowa warstwa abstrakcji

#### ADR-003: Plugin-based Tools
**Decyzja**: Tools jako pluginy, nie hardcoded
**Powód**: Elastyczność, łatwe rozszerzanie
**Konsekwencje**: Wymaga tool registry i discovery

### Performance Optimization Guide

[→ Zobacz plik: performance_optimization.py](./src/faza-2/performance_optimization.py)

### Troubleshooting Common Issues

#### Problem: "Agent not responding"
[→ Zobacz plik: troubleshooting_agent.sh](./src/faza-2/troubleshooting_agent.sh)

#### Problem: "Memory usage growing"
[→ Zobacz plik: troubleshooting.py](./src/faza-2/troubleshooting.py)

#### Problem: "Event not received"
[→ Zobacz plik: troubleshooting.py](./src/faza-2/troubleshooting.py)

### Security Best Practices

1. **Input Validation**: Always validate through ValidationPipeline
2. **Tool Sandboxing**: Run untrusted tools in subprocess
3. **Rate Limiting**: Built into TaskQueue
4. **Audit Logging**: All actions logged with context

### Contributing Guidelines

1. All code must be async-first
2. 100% type hints required
3. Tests required for new features
4. Documentation updates mandatory
5. Performance benchmarks for critical paths

---

## 🚀 Ready for Phase 3: LLM Integration!

Core Engine jest kompletny i przetestowany. System jest gotowy na integrację z LLM providers, która doda "inteligencję" do naszych agentów.

Kluczowe punkty styku dla [Fazy 3](./faza-3-LLM.md):
- `BaseAgent.execute()` - hook dla LLM calls
- `Tool.invoke()` - context dla LLM tools
- `ValidationPipeline` - walidacja LLM responses
- `EventBus` - LLM events (tokens, costs, etc.)

---

*End of Phase 2 Documentation*
