# 🔬 Analiza: Czy LiteCrewAI Fork Nadaje się do Benchmarku?

## ✅ Co Mamy Obecnie

### 1. **Fork CrewAI** (w folderze crewai-fork)
- **Status**: Zoptymalizowany fork CrewAI
- **Telemetria**: ✅ Usunięta
- **Enterprise features**: ✅ Usunięte
- **Dependencies**: ✅ Zredukowane (263MB → 4MB core)
- **API**: ✅ Kompatybilne z CrewAI (te same klasy: Agent, Crew, Task)

### 2. **Co Zostało Zrobione**
- **98.5% redukcja rozmiaru** dependencies
- Usunięto telemetrię (9 plików zmodyfikowanych)
- Usunięto enterprise features (11 katalogów)
- Zachowano core functionality
- Modularyzacja dependencies (base/dev/optional)

### 3. **Czego Brakuje do Pełnego Benchmarku**

#### A. **Instalacja jako pakiet**
```bash
# Obecnie nie można zrobić:
pip install litecrewai

# Trzeba by dodać w crewai-fork:
cd crewai-fork
pip install -e .  # editable install
```

#### B. **Nazwa pakietu**
- Fork nadal używa `import crewai`
- Dla benchmarku może to być problem (konflikt nazw)
- Rozwiązanie: namespace lub rename

#### C. **Testy porównawcze**
- Brak dedykowanych testów benchmarkowych
- Trzeba napisać identyczne testy dla obu wersji

## 📊 Propozycja Benchmarku POC

### Opcja 1: **Benchmark Tylko Dependencies** ✅
```python
# Test 1: Czas importu
time_crewai = measure_import_time("crewai")  # ~2-3s
time_litecrewai = measure_import_time("litecrewai")  # ~0.1s?

# Test 2: Rozmiar na dysku
size_crewai = get_package_size("crewai")  # 263MB
size_litecrewai = get_package_size("litecrewai")  # 4MB

# Test 3: Memory footprint po imporcie
memory_crewai = measure_memory_after_import("crewai")  # ~200MB?
memory_litecrewai = measure_memory_after_import("litecrewai")  # ~20MB?
```

### Opcja 2: **Pełny Benchmark Runtime** 🔧
```python
# Test identycznych scenariuszy:
def test_minimal_agent():
    # CrewAI
    from crewai import Agent, Task, Crew
    agent = Agent(role="test", goal="test", backstory="test")
    # measure memory...
    
    # LiteCrewAI (z virtualenv)
    sys.path.insert(0, "/path/to/crewai-fork/src")
    from crewai import Agent, Task, Crew
    agent = Agent(role="test", goal="test", backstory="test")
    # measure memory...
```

### Opcja 3: **Benchmark z Docker** 🐳
```dockerfile
# Dockerfile.crewai
FROM python:3.11-slim
RUN pip install crewai==0.30.11

# Dockerfile.litecrewai  
FROM python:3.11-slim
COPY crewai-fork/requirements/base.txt .
RUN pip install -r base.txt
COPY crewai-fork/src .
```

## 🎯 Rekomendacja

### Dla POC (Szybki Dowód Konceptu):
1. **Użyj Opcji 1** - Benchmark tylko dependencies
2. **Pokaż różnicę**:
   - CrewAI: 263MB, 21 dependencies
   - LiteCrewAI: 4MB, 7 dependencies
   - **98.5% redukcja!**

### Dla Pełnego Benchmarku:
1. **Przygotuj fork**:
   ```bash
   cd crewai-fork
   # Zmień nazwę pakietu w pyproject.toml
   sed -i 's/name = "crewai"/name = "litecrewai"/' pyproject.toml
   
   # Zainstaluj lokalnie
   pip install -e .
   ```

2. **Uruchom testy**:
   - Import time
   - Memory usage
   - Startup time
   - Task execution

## ⚠️ Potencjalne Problemy

1. **LLM Dependencies**: Fork może nie mieć openai/anthropic w base.txt
2. **Import conflicts**: Oba pakiety używają `import crewai`
3. **Test coverage**: Fork ma tylko 2 pliki testowe

## ✅ Co Fork Ma Teraz

```bash
# Minimalne dependencies (base.txt):
pydantic>=2.4.2
click>=8.1.7
python-dotenv>=1.0.0
jsonref>=1.1.0
tomli>=2.0.2
blinker>=1.9.0

# Opcjonalne (optional.txt):
openai, litellm, instructor, etc.
```

## 🚀 Next Steps

### Jeśli chcesz szybki POC:
1. Napisz prosty skrypt porównujący rozmiary i dependencies
2. Pokaż wykres: 263MB vs 4MB
3. To wystarczy jako dowód konceptu

### Jeśli chcesz pełny benchmark:
1. Zainstaluj fork jako osobny pakiet
2. Napisz testy w `masterplan/faza-0-benchmark-research.md`
3. Uruchom na DigitalOcean droplet

**Moja ocena**: Fork jest **częściowo gotowy** do benchmarku. Dla POC wystarczy pokazać różnicę w dependencies. Dla pełnego benchmarku potrzeba ~2-4h pracy setup.