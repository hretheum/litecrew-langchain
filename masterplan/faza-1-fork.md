# 🚀 LiteCrewAI - Kompletny Plan Implementacji Platformy

[← Powrót do README](./README.md) | [← Faza 0: Przygotowanie](./faza-0-przygotowanie-srodowiska.md) | [Następna faza: Core Engine →](./faza-2-core-engine.md)

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

[→ Zobacz plik: validate_droplet_setup.sh](./src/faza-1/validate_droplet_setup.sh)

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

[→ Zobacz plik: validate_dependencies.py](./src/faza-1/validate_dependencies.py)

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

[→ Zobacz plik: validate_directory_structure.sh](./src/faza-1/validate_directory_structure.sh)

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

[→ Zobacz plik: validate_python_env.py](./src/faza-1/validate_python_env.py)

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

[→ Zobacz plik: validate_ollama.py](./src/faza-1/validate_ollama.py)

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

[→ Zobacz plik: validate_cicd.sh](./src/faza-1/validate_cicd.sh)

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

[→ Zobacz plik: validate_logging.py](./src/faza-1/validate_logging.py)

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

[→ Zobacz plik: validate_monitoring.py](./src/faza-1/validate_monitoring.py)

---

## 📦 FAZA 1: FORK I MINIMALIZACJA CREWAI

[← Powrót do README](./README.md) | [← Faza 0: Przygotowanie](./faza-0-przygotowanie-srodowiska.md) | [Następna faza: Core Engine →](./faza-2-core-engine.md)

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

[→ Zobacz plik: validate_fork.py](./src/faza-1/validate_fork.py)

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

[→ Zobacz plik: validate_no_telemetry.py](./src/faza-1/validate_no_telemetry.py)

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

[→ Zobacz plik: validate_no_enterprise.py](./src/faza-1/validate_no_enterprise.py)

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

[→ Zobacz plik: validate_dependencies_optimization.py](./src/faza-1/validate_dependencies_optimization.py)

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

[→ Zobacz plik: validate_requirements.py](./src/faza-1/validate_requirements.py)

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

[→ Zobacz plik: validate_dep_cache.py](./src/faza-1/validate_dep_cache.py)

---

## 

---

[← Powrót do README](./README.md) | [← Faza 0: Przygotowanie](./faza-0-przygotowanie-srodowiska.md) | [Następna faza: Core Engine →](./faza-2-core-engine.md)
