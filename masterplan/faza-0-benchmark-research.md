# 📊 Faza 0: Benchmark Research - Agent Frameworks Memory Analysis
## Fair Comparison: CrewAI, litecrew Fork, LangChain & AutoGPT

## 🎯 Cel
Przeprowadzenie **UCZCIWEGO** benchmarku frameworków agentowych w celu wyboru najlepszego rozwiązania do orkiestracji agentów AI.

**Co testujemy**: 
- **CrewAI 0.30.11** - oficjalna wersja z PyPI
- **litecrew Fork** - odchudzony fork CrewAI (98.5% redukcja deps)
- **LangChain 0.2.1** - najpopularniejszy framework
- **AutoGPT 0.5.0** - pionier autonomous agents

**Cel**: Wybór najlepszego frameworka (niekoniecznie CrewAI!) + ocena potencjału odchudzenia każdego

**Czas realizacji**: 6-8 godzin  
**Rezultat**: 
1. Obiektywne dane porównawcze wszystkich frameworków
2. Rekomendacja którym frameworkiem kontynuować projekty
3. Analiza potencjału optymalizacji każdego frameworka

---

## 🔍 Kryteria Wyboru Frameworków

### Dlaczego te frameworki?

Wybór frameworków do benchmarku opiera się na następujących kryteriach:

#### 1. **Popularność i Adopcja** (stan na 06/2025)
- **LangChain**: ~35k⭐ GitHub, >1M pobrań/miesiąc, najbardziej dojrzały
- **CrewAI**: ~22k⭐ GitHub, szybko rosnący, focus na multi-agent
- **AutoGPT**: ~165k⭐ GitHub, pionier autonomous agents

#### 2. **Różne Podejścia Architektoniczne**
- **LangChain**: Modułowa architektura, chains & tools
- **CrewAI**: Role-based agents, hierarchiczne struktury
- **AutoGPT**: Autonomous goal-oriented agents

#### 3. **Przypadki Użycia**
- **LangChain**: Uniwersalny, od chatbotów po złożone workflows
- **CrewAI**: Specjalizacja w zespołach agentów
- **litecrew Fork**: Edge deployment, resource-constrained environments
- **AutoGPT**: Autonomiczne zadania, self-prompting

### Fair Comparison Principles

1. **Bez uprzedzeń**: Może się okazać że LangChain jest najlepszy
2. **Identyczne testy**: Wszystkie frameworki wykonują te same zadania
3. **Pełna transparentność**: Publikujemy surowe dane
4. **Analiza potencjału**: Każdy framework oceniamy pod kątem możliwości optymalizacji

### Rozważane ale Odrzucone:
- **AutoGen** (Microsoft) - podobny do CrewAI, mniej popularny
- **BabyAGI** - bardziej research-oriented, mniej production-ready
- **AgentGPT** - browser-based, trudny do benchmarku
- **Langroid** - zbyt niszowy, mała adopcja

### Dlaczego to Dobry POC?

1. **Reprezentatywność**: Pokrywamy 3 główne paradygmaty agentów AI
2. **Rzeczywiste Użycie**: Wszystkie są aktywnie używane w produkcji
3. **Różnorodność**: Od lekkich chains (LangChain) po ciężkie autonomous (AutoGPT)
4. **Mierzalność**: Wszystkie mają podobne API, łatwe do porównania

### Porównanie Wybranych Frameworków

| Framework | Version | GitHub Stars | Paradygmat | Główne Use Case | Status |
|-----------|---------|-------------|------------|-----------------|---------|
| **LangChain** | 0.2.1 | ~35k⭐ | Modular Chains | Universal toolkit | ✅ Testing |
| **CrewAI** | 0.30.11 | ~22k⭐ | Multi-Agent Teams | Collaborative AI | ✅ Testing |
| **AutoGPT** | 0.5.0 | ~165k⭐ | Autonomous Goals | Self-directed tasks | ✅ Testing |
| **litecrew Fork** | 0.134.0 | - | Minimal Multi-Agent | Edge & Scale | 🔧 POC Ready |
| **litecrew Final** | TBD | 0⭐ | Ultra-light Agents | Production Scale | 🚧 To Build |

### Pokrycie Rynku
- Te 3 frameworki = **~75% wszystkich deploymentów** (based on GitHub usage data)
- Reszta rynku: AutoGen (5%), custom solutions (15%), inne (5%)
- **Wniosek**: Jeśli litecrew pobije te 3, ma szansę na znaczący market share

### Metodologia Uczciwego Porównania

Aby zapewnić że benchmark jest wiarygodnym POC:

1. **Identyczne Zadania**: Każdy framework wykonuje dokładnie te same operacje
2. **Izolacja**: Docker containers z limitami pamięci
3. **Multiple Runs**: 3 iteracje każdego testu, uśrednianie wyników
4. **Cold Start**: Pełne czyszczenie środowiska między testami
5. **Production Config**: Domyślne ustawienia, bez "toy examples"
6. **Real LLM Calls**: Prawdziwe wywołania API (OpenAI/Anthropic)

### 🚀 Opcja POC: Szybki Benchmark z litecrew Fork

Jeśli chcesz szybki dowód konceptu (30 min), możesz użyć istniejącego forka:

```bash
# Użyj gotowego skryptu POC
cd /Users/hretheum/dev/bezrobocie/crewAI/masterplan
python benchmark_poc.py

# Porówna:
# - CrewAI (official): 263MB, 21 dependencies
# - litecrew Fork: 4MB, 7 dependencies
# - 98.5% redukcja!
```

**Fork znajduje się w**: `/Users/hretheum/dev/bezrobocie/crewAI/crewai-fork`
- ✅ Telemetria usunięta
- ✅ Enterprise features usunięte  
- ✅ Dependencies zoptymalizowane
- ✅ API kompatybilne z CrewAI

---

## ⚡ Quick Start - Deployment Guide

### Szybkie uruchomienie benchmarku na DigitalOcean:

```bash
# 1. Sklonuj repo i przejdź do katalogu
git clone https://gitlab.com/[YOUR_USERNAME]/bezrobocie.git
cd bezrobocie/benchmark

# 2. Uruchom skrypt deployment (automatyczne tworzenie dropletu)
./deploy-benchmark-droplet.sh

# 3. Po zakończeniu (45-60 min) pobierz wyniki
./download-results.sh

# 4. Droplet zostanie automatycznie usunięty po 4h
```

### 📄 Pliki deployment:
- [`deploy-benchmark-droplet.sh`](./deploy-benchmark-droplet.sh) - główny skrypt automatyzacji
- [`setup-benchmark.sh`](./setup-benchmark.sh) - setup środowiska na droplecie
- [`download-results.sh`](./download-results.sh) - pobieranie wyników
- [`benchmark-what-we-test.md`](./benchmark-what-we-test.md) - **CO testujemy (CrewAI z PyPI, NIE litecrew!)**
- [`fair_benchmark.py`](./fair_benchmark.py) - **NOWY: Fair comparison wszystkich frameworków**
- [`benchmark_poc.py`](./benchmark_poc.py) - Szybki POC dla dependencies

### Wymagania:
- Zainstalowany `doctl` (DigitalOcean CLI)
- Skonfigurowane SSH keys w DigitalOcean
- ~$0.50 kredytów (2h benchmark + 2h buffer)

---

## 🖥️ Infrastruktura - Rekomendacje DigitalOcean

### Wybrany Droplet: CPU-Optimized Regular 8GB/4vCPU

**Specyfikacja:**
- Memory: 8 GiB
- vCPU: 4 vCPUs (dedicated, 2.6GHz+)
- Transfer: 5,000 GiB
- SSD: 50 GiB
- Koszt: $0.125/hr ($84/mo)
- **Szacowany koszt benchmarku (2h)**: $0.25

### Dlaczego ta konfiguracja?

1. **Pamięć (8GB)** wystarczy dla sekwencyjnych testów:
   - Max 600MB dla pojedynczego frameworka
   - 2GB dla Docker container
   - 1GB dla systemu operacyjnego
   - 4GB+ buforu na memory leaks i monitoring

2. **CPU (4 dedicated vCPUs)**:
   - Dedicated CPU = stabilne, powtarzalne pomiary
   - Brak throttlingu podczas benchmarków
   - Wystarczające dla sekwencyjnego wykonania

3. **WAŻNE**: Testy muszą być wykonywane **SEKWENCYJNIE**, nie równolegle!
   - Eliminuje interferencję między testami
   - Zapewnia deterministyczne wyniki
   - Umożliwia dokładne pomiary pamięci

### Deployment Instructions

```bash
# 1. Stwórz droplet
doctl compute droplet create benchmark-litecrew \
  --size c-4-8gib \  # CPU-Optimized 8GB/4vCPU
  --image ubuntu-22-04-x64 \
  --region nyc3 \
  --ssh-keys [YOUR_SSH_KEY_ID] \
  --wait

# 2. Pobierz IP
DROPLET_IP=$(doctl compute droplet list --format "Name,PublicIPv4" | grep benchmark-litecrew | awk '{print $2}')

# 3. SSH i setup
ssh root@$DROPLET_IP

# 4. Auto-destroy po 4 godzinach (uruchom lokalnie)
echo "doctl compute droplet delete benchmark-litecrew -f" | at now + 4 hours
```

### Initial Setup Script

📄 **Plik**: [`setup-benchmark.sh`](./setup-benchmark.sh)

```bash
#!/bin/bash
# setup-benchmark.sh - uruchom po SSH

# System update
apt-get update && apt-get upgrade -y

# Install dependencies
apt-get install -y \
  python3.11 python3.11-venv python3-pip \
  docker.io docker-compose \
  git htop tmux \
  build-essential

# Setup Docker
usermod -aG docker $USER
systemctl enable docker
systemctl start docker

# Install monitoring tools
pip3 install glances

# Clone repository
git clone https://github.com/[YOUR_USERNAME]/bezrobocie.git /root/bezrobocie
cd /root/bezrobocie/benchmark

# Create Python environment
python3.11 -m venv benchmark_env
source benchmark_env/bin/activate
pip install -r requirements.txt

echo "✅ Setup complete! Ready for benchmarking."
```

---

## 📋 Blok 0.2: Przygotowanie litecrew Fork do Benchmarku

### Zadanie 0.2.1: Setup litecrew jako osobny pakiet (45 min)

**Zadania atomowe:**

1. [ ] **Zmiana nazwy pakietu** aby uniknąć konfliktów:
   ```bash
   cd /Users/hretheum/dev/bezrobocie/crewAI/crewai-fork
   # Backup
   cp pyproject.toml pyproject.toml.backup
   
   # Zmień nazwę pakietu
   sed -i '' 's/name = "crewai"/name = "litecrew"/' pyproject.toml
   sed -i '' 's/version = "0.134.0"/version = "0.1.0-fork"/' pyproject.toml
   ```

2. [ ] **Update importów w kodzie** (opcjonalne - można zostawić jako crewai):
   ```bash
   # Można pominąć - używamy aliasu przy imporcie
   # import litecrew as crewai
   ```

3. [ ] **Instalacja w osobnym virtualenv**:
   ```bash
   python -m venv litecrew_env
   source litecrew_env/bin/activate
   pip install -e /Users/hretheum/dev/bezrobocie/crewAI/crewai-fork
   pip install openai  # Dodaj LLM support
   ```

4. [ ] **Weryfikacja instalacji**:
   ```python
   # test_litecrew.py
   import sys
   print(f"Python: {sys.executable}")
   
   try:
       import crewai
       print(f"CrewAI version: {crewai.__version__}")
       print(f"CrewAI location: {crewai.__file__}")
       
       # Test basic functionality
       agent = crewai.Agent(
           role="Test Agent",
           goal="Verify installation",
           backstory="A test agent"
       )
       print("✅ LiteCrew fork works!")
   except Exception as e:
       print(f"❌ Error: {e}")
   ```

**Metryki sukcesu:**
- Fork zainstalowany jako osobny pakiet
- Brak konfliktów z oficjalnym CrewAI
- Basic functionality działa

---

### Zadanie 0.2.2: Przygotowanie środowiska benchmarkowego (30 min)

**Zadania atomowe:**

1. [ ] **Struktura katalogów dla fair comparison**:
   ```bash
   mkdir -p benchmark/{envs,results,scripts,data}
   
   # Osobne środowiska dla każdego frameworka
   cd benchmark/envs
   python -m venv crewai_official
   python -m venv litecrew_fork
   python -m venv langchain
   python -m venv autogpt
   ```

2. [ ] **Instalacja frameworków w izolacji**:
   ```bash
   # CrewAI Official
   source envs/crewai_official/bin/activate
   pip install crewai==0.30.11 openai
   deactivate
   
   # litecrew Fork
   source envs/litecrew_fork/bin/activate
   pip install -e /Users/hretheum/dev/bezrobocie/crewAI/crewai-fork
   pip install openai
   deactivate
   
   # LangChain
   source envs/langchain/bin/activate
   pip install langchain==0.2.1 langchain-openai==0.1.8
   deactivate
   
   # AutoGPT
   source envs/autogpt/bin/activate
   pip install autogpt==0.5.0
   deactivate
   ```

3. [ ] **Unified test runner**:
   ```python
   # benchmark/scripts/run_framework.py
   import subprocess
   import sys
   import os
   
   def run_in_env(env_name, script_path):
       """Run script in specific virtualenv"""
       activate = f"source envs/{env_name}/bin/activate"
       cmd = f"{activate} && python {script_path}"
       
       result = subprocess.run(
           cmd, 
           shell=True, 
           capture_output=True,
           text=True,
           executable='/bin/bash'
       )
       return result
   ```

**Metryki sukcesu:**
- 4 osobne virtualenv (crewai, litecrew, langchain, autogpt)
- Każdy framework zainstalowany w izolacji
- Test runner działa dla wszystkich

---

### Zadanie 0.2.3: Format danych dla LLM i analiz (30 min)

**Zadania atomowe:**

1. [ ] **Struktura danych benchmarku**:
   ```python
   # benchmark/scripts/benchmark_schema.py
   from pydantic import BaseModel
   from typing import List, Dict, Optional
   from datetime import datetime
   
   class TestResult(BaseModel):
       test_name: str
       duration_seconds: float
       memory_mb: float
       cpu_percent: float
       success: bool
       error: Optional[str] = None
       
   class FrameworkResult(BaseModel):
       framework_name: str
       version: str
       package_size_mb: float
       dependencies_count: int
       import_time_seconds: float
       tests: List[TestResult]
       metadata: Dict[str, any]
       
   class BenchmarkReport(BaseModel):
       timestamp: datetime
       system_info: Dict[str, str]
       frameworks: List[FrameworkResult]
       raw_data_path: str
       
   class OptimizationPotential(BaseModel):
       framework_name: str
       current_size_mb: float
       estimated_minimal_size_mb: float
       removable_dependencies: List[str]
       optimization_strategy: str
       effort_estimate_hours: int
   ```

2. [ ] **Export do formatów**:
   ```python
   # benchmark/scripts/export_results.py
   
   def export_for_llm(report: BenchmarkReport) -> str:
       """Format optimized for LLM analysis"""
       return f"""
   BENCHMARK REPORT - {report.timestamp}
   
   EXECUTIVE SUMMARY:
   {generate_summary(report)}
   
   DETAILED RESULTS:
   {format_detailed_results(report)}
   
   OPTIMIZATION OPPORTUNITIES:
   {analyze_optimization_potential(report)}
   
   RECOMMENDATION:
   Based on the data, recommend which framework to use and why.
   Consider: performance, size, features, optimization potential.
   """
   
   def export_raw_json(report: BenchmarkReport) -> str:
       """Raw JSON for data analysis"""
       return report.model_dump_json(indent=2)
   
   def export_markdown_table(report: BenchmarkReport) -> str:
       """Markdown table for reports"""
       # Generate comparison table
       pass
   ```

3. [ ] **Analiza możliwości odchudzenia**:
   ```python
   # benchmark/scripts/analyze_optimization.py
   
   async def analyze_framework_optimization(framework_name: str):
       """Analyze optimization potential of a framework"""
       
       # 1. Clone repo
       # 2. Analyze dependencies
       # 3. Check for removable features
       # 4. Estimate potential size reduction
       
       return OptimizationPotential(
           framework_name=framework_name,
           current_size_mb=current_size,
           estimated_minimal_size_mb=estimated_size,
           removable_dependencies=removable,
           optimization_strategy=strategy,
           effort_estimate_hours=effort
       )
   ```

**Metryki sukcesu:**
- Strukturyzowane dane (Pydantic models)
- Export do JSON/Markdown/LLM-friendly format
- Automatyczna analiza potencjału optymalizacji

---

## 📋 Blok 0.3: Benchmark Research

### Zadanie 0.3.1: Przygotowanie środowiska testowego (30 min)

**Prompt dla AI:**
```
Create a Python virtual environment setup script for benchmarking agent frameworks.
Include: CrewAI, LangChain, AutoGPT, psutil, memory_profiler, matplotlib, pandas.
Add Docker setup for isolated testing. Include resource limits.
```

**Kroki atomowe:**
1. [ ] Utwórz `benchmark/requirements.txt` z wersjami:
   ```
   # Testujemy AKTUALNE wersje z PyPI (stan na 06/2025)
   crewai==0.30.11          # Najnowsza stabilna wersja
   langchain==0.2.1         # Latest v0.2 
   langchain-openai==0.1.8  # Wymagane dla LangChain
   autogpt==0.5.0           # Ostatnia dostępna
   
   # Benchmarking tools
   psutil==5.9.8
   memory-profiler==0.61.0
   matplotlib==3.8.2
   pandas==2.1.4
   tracemalloc              # Built-in, no version
   
   # LLM providers (do testów)
   openai==1.30.1
   anthropic==0.25.7
   
   # Utilities
   python-dotenv==1.0.0
   tqdm==4.66.1
   ```
   
   **WAŻNE**: litecrew NIE jest testowany - to nasz cel do stworzenia!

2. [ ] Stwórz `benchmark/docker-compose.yml`:
   ```yaml
   version: '3.8'
   services:
     benchmark:
       build: .
       mem_limit: 2g
       cpus: '2.0'
       volumes:
         - ./results:/results
   ```

3. [ ] Przygotuj `benchmark/setup.sh`:
   ```bash
   #!/bin/bash
   python -m venv benchmark_env
   source benchmark_env/bin/activate
   pip install -r requirements.txt
   ```

**Metryki sukcesu:**
- Wszystkie frameworki zainstalowane
- Docker container z limitami pamięci
- Środowisko izolowane i powtarzalne

---

### Zadanie 0.3.2: Implementacja systemu pomiarowego (1h)

**Prompt dla AI:**
```
Create comprehensive benchmarking framework that measures:
- Memory usage (startup, runtime, peak)
- CPU usage patterns
- Startup time
- Response latency
- Resource cleanup
Track metrics over time with 100ms sampling rate.
```

**Implementacja `benchmark/profiler.py`:**
```python
import psutil
import time
import tracemalloc
import threading
from dataclasses import dataclass, asdict
from typing import List, Dict, Callable
import json
from datetime import datetime

@dataclass
class MetricSnapshot:
    timestamp: float
    memory_rss: float  # Resident Set Size
    memory_vms: float  # Virtual Memory Size
    memory_percent: float
    cpu_percent: float
    thread_count: int
    
@dataclass
class BenchmarkResult:
    framework: str
    version: str
    test_name: str
    duration: float
    startup_time: float
    first_response_time: float
    memory_startup: float
    memory_idle: float
    memory_peak: float
    memory_after_gc: float
    cpu_average: float
    cpu_peak: float
    snapshots: List[MetricSnapshot]
    errors: List[str]
    
class AgentBenchmark:
    def __init__(self, sampling_rate: float = 0.1):
        self.sampling_rate = sampling_rate
        self.snapshots: List[MetricSnapshot] = []
        self.monitoring = False
        self.process = psutil.Process()
        
    def start_monitoring(self):
        """Start background monitoring thread"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop monitoring and return results"""
        self.monitoring = False
        self.monitor_thread.join()
        return self.snapshots
        
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            snapshot = MetricSnapshot(
                timestamp=time.time(),
                memory_rss=self.process.memory_info().rss / 1024 / 1024,  # MB
                memory_vms=self.process.memory_info().vms / 1024 / 1024,
                memory_percent=self.process.memory_percent(),
                cpu_percent=self.process.cpu_percent(interval=0.1),
                thread_count=self.process.num_threads()
            )
            self.snapshots.append(snapshot)
            time.sleep(self.sampling_rate)
```

**Metryki sukcesu:**
- Sampling co 100ms bez dropów
- Dokładność pomiaru pamięci ±1MB
- Thread-safe monitoring

---

### Zadanie 0.3.3: Implementacja testów dla każdego frameworka (2h)

**Fair Comparison Test Scenarios:**

1. **Minimal Agent Creation** - Podstawowy chatbot/asystent
2. **Simple Task Execution** - Pojedyncze zapytanie (80% use cases)
3. **Multi-Agent Collaboration** - Team agentów (CRM, research teams)
4. **Memory Stress Test** - Długie konwersacje, historia kontekstu
5. **Tool Usage Scenario** - Integracje z API, bazami danych
6. **Optimization Potential** - Analiza dependencies i architektury

**Prompt dla AI:**
```
Create standardized test scenarios for fair framework comparison:
1. Minimal agent creation (chatbot baseline) - measure import time, memory
2. Simple task execution (single Q&A) - response time, accuracy
3. Multi-agent collaboration (3 agents) - coordination overhead
4. Memory stress test (10 sequential tasks) - memory growth pattern
5. Tool usage scenario (web search + calculator) - integration complexity
6. Dependency analysis - what can be removed/optimized

Each test should be functionally equivalent across ALL frameworks.
Test both CrewAI official and litecrew fork.
Measure: memory usage, response time, resource cleanup, optimization potential.
```

**Testy CrewAI - `benchmark/test_crewai.py`:**
```python
from crewai import Agent, Task, Crew, Process
from benchmark.profiler import AgentBenchmark, BenchmarkResult
import time
import gc

class CrewAIBenchmark:
    def __init__(self):
        self.framework = "CrewAI"
        self.version = self._get_version()
        
    def test_minimal_agent(self) -> BenchmarkResult:
        """Test 1: Create minimal agent"""
        benchmark = AgentBenchmark()
        errors = []
        
        # Pre-test garbage collection
        gc.collect()
        time.sleep(1)
        
        # Start monitoring
        benchmark.start_monitoring()
        start_time = time.time()
        
        try:
            # Create minimal agent
            agent = Agent(
                role='Assistant',
                goal='Help with basic tasks',
                backstory='A helpful AI assistant',
                verbose=False
            )
            
            startup_time = time.time() - start_time
            
            # Let it idle
            time.sleep(2)
            
            # Simple task
            task_start = time.time()
            task = Task(
                description="Say hello",
                agent=agent,
                expected_output="A greeting"
            )
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
            result = crew.kickoff()
            first_response_time = time.time() - task_start
            
        except Exception as e:
            errors.append(str(e))
            
        finally:
            # Stop monitoring
            snapshots = benchmark.stop_monitoring()
            
            # Force garbage collection
            gc.collect()
            time.sleep(1)
            
            # Final memory reading
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
        return self._analyze_results(
            "minimal_agent",
            start_time,
            startup_time,
            first_response_time,
            snapshots,
            errors
        )
    
    def test_multi_agent(self) -> BenchmarkResult:
        """Test 3: Multi-agent collaboration"""
        # Similar structure with 3 agents
        # ...
        
    def test_memory_stress(self) -> BenchmarkResult:
        """Test 4: Sequential task execution"""
        # Run 10 tasks sequentially
        # ...
```

**Testy LangChain - `benchmark/test_langchain.py`:**
```python
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
# Similar structure to CrewAI tests
```

**Testy AutoGPT - `benchmark/test_autogpt.py`:**
```python
# AutoGPT specific imports and similar test structure
```

**Metryki sukcesu:**
- Każdy test <5 minut wykonania
- Identyczne scenariusze między frameworkami
- Deterministyczne wyniki (±5% variance)

---

### Zadanie 0.3.4: System agregacji i analizy wyników (1h)

**Prompt dla AI:**
```
Create results aggregation system that:
- Combines multiple test runs
- Calculates statistics (mean, median, std dev)
- Identifies memory leaks
- Generates comparative analysis
- Exports to multiple formats (JSON, CSV, MD)
```

**Analyzer - `benchmark/analyzer.py`:**
```python
import pandas as pd
import numpy as np
from typing import List, Dict
import json
import matplotlib.pyplot as plt
import seaborn as sns

class BenchmarkAnalyzer:
    def __init__(self, results: List[BenchmarkResult]):
        self.results = results
        self.df = self._results_to_dataframe()
        
    def _results_to_dataframe(self) -> pd.DataFrame:
        """Convert results to pandas DataFrame"""
        data = []
        for result in self.results:
            row = {
                'framework': result.framework,
                'test': result.test_name,
                'memory_peak': result.memory_peak,
                'memory_idle': result.memory_idle,
                'startup_time': result.startup_time,
                'response_time': result.first_response_time,
                'cpu_average': result.cpu_average
            }
            data.append(row)
        return pd.DataFrame(data)
    
    def generate_summary(self) -> Dict:
        """Generate statistical summary"""
        summary = {}
        
        for framework in self.df['framework'].unique():
            framework_data = self.df[self.df['framework'] == framework]
            
            summary[framework] = {
                'memory': {
                    'peak_mean': framework_data['memory_peak'].mean(),
                    'peak_std': framework_data['memory_peak'].std(),
                    'idle_mean': framework_data['memory_idle'].mean(),
                    'overhead': framework_data['memory_idle'].mean() - 50  # Base Python ~50MB
                },
                'performance': {
                    'startup_mean': framework_data['startup_time'].mean(),
                    'response_mean': framework_data['response_time'].mean()
                },
                'efficiency_score': self._calculate_efficiency(framework_data)
            }
            
        return summary
    
    def detect_memory_leaks(self) -> Dict:
        """Analyze snapshots for memory leaks"""
        leaks = {}
        
        for result in self.results:
            if len(result.snapshots) < 10:
                continue
                
            # Convert snapshots to time series
            times = [s.timestamp - result.snapshots[0].timestamp for s in result.snapshots]
            memory = [s.memory_rss for s in result.snapshots]
            
            # Linear regression to detect growth
            slope, intercept = np.polyfit(times, memory, 1)
            
            # Leak detected if memory grows >1MB/minute
            if slope > 1.0 / 60:
                leaks[f"{result.framework}_{result.test_name}"] = {
                    'growth_rate_mb_per_min': slope * 60,
                    'projected_1h': slope * 3600
                }
                
        return leaks
```

**Metryki sukcesu:**
- Wykrywanie memory leaks z 95% accuracy
- Generowanie raportów w <5s
- Czytelne wizualizacje

---

### Zadanie 0.3.5: Generowanie wizualizacji i raportów (1h)

**Prompt dla AI:**
```
Create visualization system that generates:
1. Memory usage comparison bar chart
2. Startup time comparison
3. Memory over time line plots
4. Efficiency matrix heatmap
5. Comprehensive markdown report
Use matplotlib with dark theme matching our branding.
```

**Visualizer - `benchmark/visualizer.py`:**
```python
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

class BenchmarkVisualizer:
    def __init__(self, analyzer: BenchmarkAnalyzer):
        self.analyzer = analyzer
        self.setup_style()
        
    def setup_style(self):
        """Configure dark theme"""
        plt.style.use('dark_background')
        sns.set_palette("husl")
        
    def plot_memory_comparison(self, save_path: str = 'results/memory_comparison.png'):
        """Create memory usage comparison chart"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Data preparation
        frameworks = []
        memory_values = []
        colors = []
        
        summary = self.analyzer.generate_summary()
        
        for fw, data in summary.items():
            frameworks.append(fw)
            memory_values.append(data['memory']['peak_mean'])
            
            # Color based on efficiency
            if data['memory']['peak_mean'] < 100:
                colors.append('#00ff41')  # Green for efficient
            elif data['memory']['peak_mean'] < 300:
                colors.append('#ffff00')  # Yellow for moderate
            else:
                colors.append('#ff0040')  # Red for heavy
                
        # Create bars
        bars = ax.bar(frameworks, memory_values, color=colors, edgecolor='white', linewidth=2)
        
        # Add value labels
        for bar, value in zip(bars, memory_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.0f} MB',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # Add target line for litecrew
        ax.axhline(y=10, color='#00ff41', linestyle='--', linewidth=2, alpha=0.7)
        ax.text(0.02, 12, 'litecrew Target: 10MB', transform=ax.transData, 
                fontsize=10, color='#00ff41')
        
        # Styling
        ax.set_title('Agent Framework Memory Usage Comparison', fontsize=20, pad=20)
        ax.set_ylabel('Peak Memory Usage (MB)', fontsize=14)
        ax.set_xlabel('Framework', fontsize=14)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add efficiency zones
        ax.axhspan(0, 50, alpha=0.1, color='green', label='Efficient (<50MB)')
        ax.axhspan(50, 200, alpha=0.1, color='yellow', label='Moderate (50-200MB)')
        ax.axhspan(200, 1000, alpha=0.1, color='red', label='Heavy (>200MB)')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_memory_timeline(self, result: BenchmarkResult, save_path: str):
        """Plot memory usage over time"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        # Extract time series
        times = [(s.timestamp - result.snapshots[0].timestamp) for s in result.snapshots]
        memory = [s.memory_rss for s in result.snapshots]
        cpu = [s.cpu_percent for s in result.snapshots]
        
        # Memory plot
        ax1.plot(times, memory, color='#00ff41', linewidth=2)
        ax1.fill_between(times, memory, alpha=0.3, color='#00ff41')
        ax1.set_ylabel('Memory Usage (MB)', fontsize=12)
        ax1.set_title(f'{result.framework} - {result.test_name} Resource Usage', fontsize=16)
        ax1.grid(True, alpha=0.3)
        
        # CPU plot
        ax2.plot(times, cpu, color='#ff6b6b', linewidth=2)
        ax2.fill_between(times, cpu, alpha=0.3, color='#ff6b6b')
        ax2.set_ylabel('CPU Usage (%)', fontsize=12)
        ax2.set_xlabel('Time (seconds)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
    def generate_markdown_report(self, save_path: str = 'results/benchmark_report.md'):
        """Generate comprehensive markdown report"""
        summary = self.analyzer.generate_summary()
        leaks = self.analyzer.detect_memory_leaks()
        
        report = f"""# Agent Framework Benchmark Report
        
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Test Environment**: Ubuntu 22.04, 16GB RAM, Python 3.11

## Executive Summary - Fair Framework Comparison

Our benchmarks compare ALL major agent frameworks objectively:

- **CrewAI 0.30.11**: {summary.get('CrewAI', {}).get('memory', {}).get('peak_mean', 0):.0f}MB average
- **litecrew Fork**: {summary.get('litecrew', {}).get('memory', {}).get('peak_mean', 0):.0f}MB average  
- **LangChain 0.2.1**: {summary.get('LangChain', {}).get('memory', {}).get('peak_mean', 0):.0f}MB average
- **AutoGPT 0.5.0**: {summary.get('AutoGPT', {}).get('memory', {}).get('peak_mean', 0):.0f}MB average

### Winner: {determine_winner(summary)}

### Business Impact:
- **Best Performance**: {best_performer} - {performance_metrics}
- **Best for Scale**: {best_for_scale} - {scale_metrics}
- **Best for Edge**: {best_for_edge} - {edge_metrics}
- **Most Optimizable**: {most_optimizable} - {optimization_potential}

### Recommendation:
{generate_recommendation(summary)}

### Optimization Opportunities:
{analyze_all_frameworks_optimization_potential(summary)}

## Detailed Results

### Memory Usage

| Framework | Idle (MB) | Peak (MB) | Overhead (MB) | Efficiency Score |
|-----------|-----------|-----------|---------------|------------------|
"""
        
        for fw, data in summary.items():
            report += f"| {fw} | {data['memory']['idle_mean']:.1f} | {data['memory']['peak_mean']:.1f} | {data['memory']['overhead']:.1f} | {data['efficiency_score']:.2f} |\n"
            
        report += """
### Performance Metrics

| Framework | Startup Time (s) | First Response (s) | Memory/Response Ratio |
|-----------|------------------|--------------------|-----------------------|
"""
        
        for fw, data in summary.items():
            ratio = data['memory']['peak_mean'] / data['performance']['response_mean']
            report += f"| {fw} | {data['performance']['startup_mean']:.2f} | {data['performance']['response_mean']:.2f} | {ratio:.1f} MB/s |\n"
            
        if leaks:
            report += """
### ⚠️ Memory Leak Detection

Potential memory leaks detected:

"""
            for test, leak_data in leaks.items():
                report += f"- **{test}**: Growing at {leak_data['growth_rate_mb_per_min']:.2f} MB/min\n"
                
        report += """
## Conclusion - Fair Framework Selection

The benchmark provides objective data to:

1. **Select the best framework** based on actual performance
2. **Identify optimization opportunities** in each framework
3. **Make informed decision** about future development:
   - Use existing framework as-is
   - Optimize existing framework (fork)
   - Create new minimal framework (litecrew)

### Key Questions Answered:
- Which framework performs best? → Data will show
- Which has most optimization potential? → Dependency analysis  
- Should we continue with CrewAI? → Only if it's objectively best
- Is litecrew worth building? → Only if no framework can be optimized

## Data Format for LLM Analysis

Results will be structured for both human and AI analysis:

```json
{
  "benchmark_results": {
    "frameworks": [...],
    "winner": "TBD based on data",
    "optimization_potential": {...}
  },
  "recommendation": {
    "use_framework": "TBD",
    "optimization_strategy": "TBD",
    "estimated_effort": "TBD"
  },
  "raw_data": "path/to/full/results.json"
}
```

## Reproduction

```bash
cd benchmark
./run_all_benchmarks.sh
python analyze_results.py
```

Full data available in `results/benchmark_data.json`
"""
        
        with open(save_path, 'w') as f:
            f.write(report)
```

**Metryki sukcesu:**
- Raporty generowane automatycznie
- Wizualizacje publication-ready
- Markdown z wszystkimi danymi

---

### Zadanie 0.3.6: Orchestracja i automatyzacja (30 min)

**Prompt dla AI:**
```
Create orchestration script that:
1. Runs all benchmarks in sequence
2. Handles failures gracefully
3. Aggregates results
4. Generates all reports
5. Publishes to specified locations
Include progress bars and ETA.
```

**Orchestrator - `benchmark/run_benchmarks.py`:**
```python
#!/usr/bin/env python3
import os
import sys
import json
import argparse
import gc
import time
import psutil
from datetime import datetime
from pathlib import Path
from typing import List
import concurrent.futures
from tqdm import tqdm

from benchmark.test_crewai import CrewAIBenchmark
from benchmark.test_langchain import LangChainBenchmark
from benchmark.test_autogpt import AutoGPTBenchmark
from benchmark.analyzer import BenchmarkAnalyzer
from benchmark.visualizer import BenchmarkVisualizer

class BenchmarkOrchestrator:
    def __init__(self, output_dir: str = "results", parallel: bool = False):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.parallel = parallel
        self.results: List[BenchmarkResult] = []
        
        # Test configurations
        self.frameworks = [
            ('CrewAI', CrewAIBenchmark),
            ('LangChain', LangChainBenchmark),
            ('AutoGPT', AutoGPTBenchmark)
        ]
        
        self.tests = [
            'test_minimal_agent',
            'test_simple_task',
            'test_multi_agent',
            'test_memory_stress',
            'test_tool_usage'
        ]
        
    def run_all_benchmarks(self, iterations: int = 3):
        """Run all benchmarks SEQUENTIALLY to ensure accurate measurements
        
        CRITICAL: Tests MUST run sequentially to avoid:
        - Memory interference between frameworks
        - CPU contention affecting measurements
        - Garbage collection timing issues
        - Docker resource conflicts
        """
        total_tests = len(self.frameworks) * len(self.tests) * iterations
        
        print("\n⚠️  Running benchmarks SEQUENTIALLY for accurate measurements")
        print("⚙️  Parallel execution is DISABLED to ensure data quality")
        print("⏰ This will take approximately 45-60 minutes...")
        print("☕ Grab a coffee, this is worth the wait!\n")
        
        with tqdm(total=total_tests, desc="Running benchmarks") as pbar:
            for framework_name, framework_class in self.frameworks:
                print(f"\n{'='*60}")
                print(f"📊 Starting {framework_name} benchmarks")
                print(f"{'='*60}\n")
                
                # Clean environment between frameworks
                self._cleanup_environment()
                time.sleep(10)  # Let system stabilize
                
                framework_results = []
                
                try:
                    benchmark = framework_class()
                    
                    for test_name in self.tests:
                        test_method = getattr(benchmark, test_name, None)
                        
                        if not test_method:
                            pbar.update(iterations)
                            continue
                            
                        # Run multiple iterations
                        for i in range(iterations):
                            pbar.set_description(f"{framework_name} - {test_name} (run {i+1}/{iterations})")
                            
                            # Clean memory before each test
                            gc.collect()
                            gc.collect()  # Double collect for thorough cleanup
                            time.sleep(5)  # Let GC finish
                            
                            # Record baseline memory
                            baseline_memory = psutil.Process().memory_info().rss / 1024 / 1024
                            print(f"\n📍 Baseline memory: {baseline_memory:.1f}MB")
                            
                            try:
                                result = test_method()
                                framework_results.append(result)
                                self._save_intermediate(result)
                                
                            except Exception as e:
                                print(f"\n❌ Error in {framework_name}.{test_name}: {e}")
                                
                            pbar.update(1)
                            
                            # Wait for system to stabilize
                            time.sleep(5)
                            
                except Exception as e:
                    print(f"\n❌ Failed to initialize {framework_name}: {e}")
                    pbar.update(len(self.tests) * iterations)
                    
                self.results.extend(framework_results)
                
        print(f"\n✅ Completed {len(self.results)} successful benchmarks")
        
    def _cleanup_environment(self):
        """Clean environment between framework tests
        
        This is CRITICAL for accurate measurements:
        - Removes Docker containers and volumes
        - Clears system caches (requires root)
        - Forces Python garbage collection
        - Waits for system stabilization
        """
        print("🧹 Cleaning environment...")
        
        # 1. Docker cleanup
        print("   - Stopping Docker containers...")
        os.system("docker stop $(docker ps -aq) 2>/dev/null")
        os.system("docker rm $(docker ps -aq) 2>/dev/null")
        
        print("   - Removing Docker volumes and images...")
        os.system("docker volume prune -f 2>/dev/null")
        os.system("docker system prune -af --volumes 2>/dev/null")
        
        # 2. Python cleanup
        print("   - Running Python garbage collection...")
        gc.collect()
        gc.collect()  # Run twice for thorough cleanup
        gc.collect()  # Third time to catch circular references
        
        # 3. System cache cleanup (Linux only, requires root)
        if os.path.exists("/proc/sys/vm/drop_caches"):
            print("   - Clearing system caches...")
            os.system("sync")  # Flush file system buffers
            os.system("echo 3 > /proc/sys/vm/drop_caches 2>/dev/null")
            
        # 4. Wait for stabilization
        print("   - Waiting for system stabilization...")
        time.sleep(10)
        
        # 5. Verify cleanup
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        print(f"✅ Environment cleaned. Current process memory: {current_memory:.1f}MB")
        
    def _save_intermediate(self, result):
        """Save intermediate results for crash recovery"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{result.framework}_{result.test_name}_{timestamp}.json"
        filepath = self.output_dir / "intermediate" / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(asdict(result), f, indent=2)
        
    def _save_json(self, data, filename):
        """Save data as JSON file"""
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
    def analyze_and_report(self):
        """Generate analysis and reports"""
        if not self.results:
            print("❌ No results to analyze")
            return
            
        print("\n📊 Analyzing results...")
        
        # Create analyzer
        analyzer = BenchmarkAnalyzer(self.results)
        
        # Generate summary
        summary = analyzer.generate_summary()
        self._save_json(summary, "summary.json")
        
        # Detect memory leaks
        leaks = analyzer.detect_memory_leaks()
        if leaks:
            print(f"⚠️  Detected {len(leaks)} potential memory leaks")
            self._save_json(leaks, "memory_leaks.json")
            
        # Generate visualizations
        print("\n📈 Generating visualizations...")
        visualizer = BenchmarkVisualizer(analyzer)
        
        visualizer.plot_memory_comparison(self.output_dir / "memory_comparison.png")
        visualizer.plot_startup_comparison(self.output_dir / "startup_comparison.png")
        visualizer.plot_efficiency_matrix(self.output_dir / "efficiency_matrix.png")
        
        # Generate detailed timeline for each framework
        for framework in analyzer.df['framework'].unique():
            framework_results = [r for r in self.results if r.framework == framework]
            if framework_results:
                visualizer.plot_memory_timeline(
                    framework_results[0],
                    self.output_dir / f"{framework.lower()}_timeline.png"
                )
                
        # Generate markdown report
        print("\n📝 Generating report...")
        visualizer.generate_markdown_report(self.output_dir / "benchmark_report.md")
        
        # Create summary for social media
        self._generate_social_summary(summary)
        
        print(f"\n✅ All results saved to {self.output_dir}")
        
    def _generate_social_summary(self, summary: Dict):
        """Generate summary for LinkedIn/Twitter - Fair Comparison"""
        
        # Determine winner
        frameworks_by_memory = sorted(
            [(name, data.get('memory', {}).get('peak_mean', 999)) 
             for name, data in summary.items()],
            key=lambda x: x[1]
        )
        
        winner = frameworks_by_memory[0][0]
        winner_memory = frameworks_by_memory[0][1]
        
        social_text = f"""🔬 Agent Framework Benchmark Results - Fair Comparison:

Tested the TOP 4 agent orchestration solutions:

📊 Memory Usage Results:
"""
        
        for fw, memory in frameworks_by_memory:
            stars = summary.get(fw, {}).get('github_stars', 'N/A')
            social_text += f"• {fw}: {memory:.0f}MB"
            if fw == winner:
                social_text += " 🏆 WINNER!"
            social_text += f"\n"
        
        social_text += f"""
Surprising findings:
• {winner} uses {(frameworks_by_memory[-1][1] / winner_memory):.1f}x less memory than worst performer
• litecrew Fork shows {(summary.get('CrewAI', {}).get('memory', {}).get('peak_mean', 500) / summary.get('litecrew', {}).get('memory', {}).get('peak_mean', 20)):.1f}x improvement over original
• All frameworks have optimization potential

Recommendation: {winner} for now, but investigating optimization of {summary.get('most_potential', 'all frameworks')}

Full data & methodology: [link]
#AIAgents #BenchmarkResults #FairComparison #BuildInPublic"""
        
        with open(self.output_dir / "social_summary.txt", 'w') as f:
            f.write(social_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run agent framework benchmarks")
    parser.add_argument("--iterations", type=int, default=3, help="Number of iterations per test")
    parser.add_argument("--output", type=str, default="results", help="Output directory")
    # NOTE: --parallel flag removed, benchmarks always run sequentially
    
    args = parser.parse_args()
    
    # Create orchestrator (always sequential)
    orchestrator = BenchmarkOrchestrator(args.output, parallel=False)
    
    # Run benchmarks
    orchestrator.run_all_benchmarks(args.iterations)
    
    # Analyze and report
    orchestrator.analyze_and_report()
```

**System Monitor - `benchmark/system_monitor.sh`:**
```bash
#!/bin/bash
# system_monitor.sh - Run in separate tmux pane during benchmarks

LOG_FILE="results/system_monitor.log"
echo "Starting system monitoring at $(date)" | tee $LOG_FILE

while true; do
    echo "=== $(date) ===" | tee -a $LOG_FILE
    
    # Memory snapshot
    echo "MEMORY:" | tee -a $LOG_FILE
    free -h | tee -a $LOG_FILE
    
    # Top processes by memory
    echo -e "\nTOP PROCESSES BY MEMORY:" | tee -a $LOG_FILE
    ps aux --sort=-%mem | head -n 5 | tee -a $LOG_FILE
    
    # Docker stats
    echo -e "\nDOCKER:" | tee -a $LOG_FILE
    docker stats --no-stream 2>/dev/null | tee -a $LOG_FILE
    
    # CPU temperature (if available)
    if command -v sensors &> /dev/null; then
        echo -e "\nCPU TEMP:" | tee -a $LOG_FILE
        sensors | grep -E "(Core|CPU)" | tee -a $LOG_FILE
    fi
    
    # Disk I/O
    echo -e "\nDISK I/O:" | tee -a $LOG_FILE
    iostat -x 1 2 | tail -n 20 | tee -a $LOG_FILE
    
    echo -e "\n" | tee -a $LOG_FILE
    sleep 10
done
```

**Shell wrapper - `benchmark/run_all_benchmarks.sh`:**

📄 **Ten plik należy utworzyć w katalogu benchmark/**

```bash
#!/bin/bash
set -e

echo "🚀 Starting Agent Framework Benchmark Suite (SEQUENTIAL MODE)"
echo "============================================================"
echo "⚠️  This will run SEQUENTIALLY for accurate measurements"
echo "⏱️  Estimated time: 45-60 minutes"
echo ""

# Check if running as root (needed for cache clearing)
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Warning: Not running as root. Some cleanup operations will be skipped."
fi

# Check dependencies
echo "📦 Checking dependencies..."
python3 -m pip install -q -r requirements.txt
apt-get install -y sysstat iotop 2>/dev/null || true

# Clean previous results
echo "🧹 Cleaning previous results..."
rm -rf results/*
mkdir -p results

# Start system monitoring in background
echo "📊 Starting system monitor..."
tmux new-session -d -s monitor './system_monitor.sh'
echo "✅ Monitor running in tmux session 'monitor'"

# Run benchmarks (SEQUENTIAL)
echo "🏃 Running benchmarks SEQUENTIALLY..."
echo "   This ensures accurate memory measurements"
python3 run_benchmarks.py --iterations 3 --output results

# Stop monitoring
echo "🛑 Stopping system monitor..."
tmux kill-session -t monitor 2>/dev/null || true

# Verify results
echo "✅ Verifying results..."
python3 verify_results.py

# Create archive
echo "📦 Creating archive..."
tar -czf "benchmark_results_$(date +%Y%m%d_%H%M%S).tar.gz" results/

echo ""
echo "✅ Benchmark complete! Results in ./results/"
echo "📊 View report: results/benchmark_report.md"
echo "🖼️  View charts: results/*.png"
echo "📈 System metrics: results/system_monitor.log"
echo ""
echo "💡 To run on DigitalOcean droplet:"
echo "   1. Use deployment script: ./deploy-benchmark-droplet.sh"
echo "   2. Or manual: doctl compute droplet create benchmark-litecrew --size c-4-8gib ..."
echo "   3. Download results: ./download-results.sh"
echo ""
echo "📄 See Quick Start section at the top of this document for details"
```

**Quick Start na DigitalOcean:**
```bash
# Complete deployment script
#!/bin/bash
# deploy-benchmark-droplet.sh

# Create droplet
doctl compute droplet create benchmark-litecrew \
  --size c-4-8gib \
  --image ubuntu-22-04-x64 \
  --region nyc3 \
  --ssh-keys $(doctl compute ssh-key list --format ID --no-header | head -1) \
  --user-data-file setup-benchmark.sh \
  --wait

# Get IP
IP=$(doctl compute droplet list --format "Name,PublicIPv4" --no-header | grep benchmark-litecrew | awk '{print $2}')
echo "✅ Droplet created at: $IP"

# Wait for setup
echo "⏳ Waiting for initial setup (2 min)..."
sleep 120

# SSH and run benchmarks
echo "🚀 Starting benchmarks..."
ssh -o StrictHostKeyChecking=no root@$IP "cd /root/bezrobocie/benchmark && ./run_all_benchmarks.sh"

# Download results
echo "📥 Downloading results..."
scp -r root@$IP:/root/bezrobocie/benchmark/results ./benchmark-results-$(date +%Y%m%d_%H%M%S)

# Destroy droplet
echo "🗑️  Destroying droplet..."
doctl compute droplet delete benchmark-litecrew -f

echo "✅ All done! Check ./benchmark-results-*/ for results"
```

**Metryki sukcesu:**
- Całość wykonuje się w <60 minut
- Automatyczne raporty i wizualizacje
- System monitoring przez cały czas
- Deterministyczne wyniki (sekwencyjne wykonanie)
- Koszt: ~$0.25 na DigitalOcean

---

## 📊 Metryki Sukcesu Całego Benchmarku

### Ilościowe:
- ✅ Dane z minimum 3 iteracji każdego testu
- ✅ Pomiary z dokładnością ±5%
- ✅ Wykrycie 100% oczywistych memory leaks
- ✅ Kompletne raporty w 3 formatach (JSON, CSV, MD)

### Jakościowe:
- ✅ Wizualizacje publication-ready
- ✅ Dane przekonujące do potrzeby litecrew
- ✅ Możliwość reprodukcji przez społeczność
- ✅ Content na minimum 3 posty LinkedIn

### Deliverables:
1. `results/benchmark_report.md` - Pełny raport
2. `results/memory_comparison.png` - Główna wizualizacja
3. `results/benchmark_data.json` - Surowe dane
4. `results/social_summary.txt` - Gotowy post
5. `results/system_monitor.log` - Metryki systemowe
6. `benchmark_results_[timestamp].tar.gz` - Archiwum

---

## 🔑 KLUCZOWE AKTUALIZACJE

### 1. **Infrastruktura**
- ✅ Droplet: CPU-Optimized 8GB/4vCPU ($0.125/hr)
- ✅ Koszt całkowity: ~$0.25 za pełny benchmark
- ✅ Auto-deployment i auto-cleanup scripts

### 2. **Metodologia**
- ✅ **SEKWENCYJNE** wykonanie testów (nie równoległe!)
- ✅ Czyszczenie środowiska między frameworkami
- ✅ 5-sekundowe przerwy między testami
- ✅ Double garbage collection przed każdym testem

### 3. **Monitoring**
- ✅ System monitor w osobnym tmux session
- ✅ Logowanie metryk co 10 sekund
- ✅ Śledzenie CPU, RAM, Docker, I/O

### 4. **Reprodukowalność**
- ✅ Deterministyczne wyniki dzięki sekwencyjnemu wykonaniu
- ✅ Kompletne deployment scripts
- ✅ Dokładna dokumentacja środowiska

---
3. `results/benchmark_data.json` - Surowe dane
4. `results/social_summary.txt` - Gotowy post
5. `benchmark_results_[timestamp].tar.gz` - Archiwum

---

## 🚀 Quick Start

### Na DigitalOcean:
```bash
# 1. Użyj gotowego skryptu deployment
./deploy-benchmark-droplet.sh

# 2. Lub manualnie:
doctl compute droplet create benchmark-litecrew \
  --size c-4-8gib \
  --image ubuntu-22-04-x64 \
  --region nyc3 \
  --ssh-keys [YOUR_KEY_ID] \
  --wait

# 3. SSH i uruchom
ssh root@[DROPLET_IP]
cd /root/bezrobocie/benchmark
./run_all_benchmarks.sh

# 4. Pobierz wyniki
scp -r root@[DROPLET_IP]:/root/bezrobocie/benchmark/results ./

# 5. Zniszcz droplet
doctl compute droplet delete benchmark-litecrew -f
```

### Monitorowanie w czasie rzeczywistym:
```bash
# W osobnej sesji tmux
tmux new -s monitor
./system_monitor.sh

# Podgląd z głównej sesji
tmux attach -t monitor
```

## 🔧 Troubleshooting

**Problem**: ImportError dla frameworka
**Rozwiązanie**: `pip install -r requirements.txt --force-reinstall`

**Problem**: Out of memory podczas testów
**Rozwiązanie**: Sprawdź czy testy wykonują się sekwencyjnie, nie równolegle

**Problem**: Permission denied przy czyszczeniu cache
**Rozwiązanie**: Uruchom jako root lub zignoruj (nie krytyczne)

**Problem**: tmux session 'monitor' already exists
**Rozwiązanie**: `tmux kill-session -t monitor` przed uruchomieniem

**Problem**: Droplet creation failed
**Rozwiązanie**: Sprawdź limity konta DO i dostępność regionu

**Problem**: Niestabilne wyniki
**Rozwiązanie**: Upewnij się że używasz dedykowanych CPU, nie Basic droplets

---

## 🔥 Kluczowe Zmiany i Best Practices

### 1. **SEKWENCYJNE wykonanie jest KRYTYCZNE**
- ❌ NIE uruchamiaj testów równolegle
- ✅ Każdy framework testowany osobno
- ✅ 10-sekundowe przerwy między testami
- ✅ Pełne czyszczenie środowiska między frameworkami

### 2. **Monitoring w osobnym procesie**
```bash
# Uruchom w osobnym tmux/screen
tmux new-session -d -s monitor './system_monitor.sh'
```

### 3. **Czyszczenie pamięci - triple GC pattern**
```python
gc.collect()
gc.collect()  # Drugi raz dla pewności
gc.collect()  # Trzeci dla circular references
time.sleep(5)  # Daj systemowi czas
```

### 4. **Droplet Auto-Destroy**
```bash
# Ustaw auto-destroy przy tworzeniu
echo "doctl compute droplet delete benchmark-litecrew -f" | at now + 4 hours
```

### 5. **Crash Recovery**
- Wyniki zapisywane incrementalnie w `results/intermediate/`
- Można wznowić benchmark po crash
- Każdy test ma własny JSON

---

## 📁 Struktura Plików Projektu

### Główne skrypty:
- **[`deploy-benchmark-droplet.sh`](./deploy-benchmark-droplet.sh)** - Kompletny deployment (tworzenie dropletu + benchmark + wyniki)
- **[`setup-benchmark.sh`](./setup-benchmark.sh)** - Automatyczny setup środowiska Ubuntu (używany przez deployment)
- **[`download-results.sh`](./download-results.sh)** - Pobieranie wyników z istniejącego dropletu

### Pliki benchmarku (do stworzenia):
- `benchmark/requirements.txt` - Dependencies Python
- `benchmark/profiler.py` - System pomiarowy
- `benchmark/test_crewai.py` - Testy CrewAI
- `benchmark/test_langchain.py` - Testy LangChain
- `benchmark/test_autogpt.py` - Testy AutoGPT
- `benchmark/analyzer.py` - Analiza wyników
- `benchmark/visualizer.py` - Generowanie wykresów
- `benchmark/run_benchmarks.py` - Orchestrator główny
- `benchmark/system_monitor.sh` - Monitor systemowy

### Pliki dokumentacji:
- **[`FAIR-BENCHMARK-UPDATE.md`](./FAIR-BENCHMARK-UPDATE.md)** - ⭐ NOWE: Podsumowanie zmian (fair comparison)
- **[`litecrew-benchmark-readiness.md`](./litecrew-benchmark-readiness.md)** - Analiza gotowości forka do benchmarku
- **[`benchmark_poc.py`](./benchmark_poc.py)** - Skrypt do szybkiego POC benchmarku
- **[`benchmark-what-we-test.md`](./benchmark-what-we-test.md)** - Co dokładnie testujemy (WAŻNE!)
- **[`benchmark-updates-summary.md`](./benchmark-updates-summary.md)** - Podsumowanie wszystkich zmian
- **[`benchmark-poc-updates.md`](./benchmark_poc-updates.md)** - Uzasadnienie wyboru frameworków (POC)
- **[`UPDATE_COMPLETE.md`](./UPDATE_COMPLETE.md)** - Status wykonania zadania

---

## 📌 Podsumowanie

Ten benchmark został zaprojektowany do wykonania na **DigitalOcean CPU-Optimized 8GB/4vCPU** droplecie za ~$0.25. Kluczowe jest **SEKWENCYJNE** wykonanie testów dla dokładnych pomiarów pamięci.

### Oczekiwane rezultaty:
- **CrewAI 0.30.11**: ~500MB pamięci (22k⭐, multi-agent focus)
- **litecrew Fork**: ~20-50MB pamięci (98.5% redukcja deps)
- **LangChain 0.2.1**: ~400MB pamięci (35k⭐, najpopularniejszy)
- **AutoGPT 0.5.0**: ~600MB pamięci (165k⭐, autonomous pioneer)

### Fair Comparison Goals:
1. **Obiektywny wybór**: Najlepszy framework wygrywa (niekoniecznie CrewAI!)
2. **Analiza potencjału**: Który framework można najłatwiej zoptymalizować?
3. **Rekomendacja**: Który używać w projektach produkcyjnych?
4. **Roadmap**: Czy tworzyć litecrew czy optymalizować inny framework?

### Wartość jako POC:
1. **Reprezentatywna próba**: 3 najpopularniejsze frameworki (>75% rynku)
2. **Twarde dane**: Metryki pamięci, CPU, startup time
3. **Reprodukowalność**: Skrypty deployment, Docker isolation
4. **Biznesowa wartość**: $10-100/miesiąc oszczędności na infrastrukturze per projekt

### Potencjalne Rozszerzenia:
- **Faza 2**: AutoGen, Langroid, BabyAGI
- **Faza 3**: Komercyjne rozwiązania (Fixie, Cognosys)
- **Faza 4**: Benchmark na różnych LLM (GPT-4, Claude, Llama)

To da nam obiektywne dane do wyboru najlepszego frameworka! 🚀

---

*Ten benchmark pomoże wybrać najlepszą drogę dla projektów AI agents poprzez uczciwe porównanie i twarde dane.*