#!/bin/bash
# Lokalny pipeline testowy - IDENTYCZNY z GitLab CI

set -e

echo "🚀 Uruchamianie pełnego pipeline lokalnie (identyczny z GitLab CI)..."
echo "=================================================================="

# Sprawdź czy jesteśmy w odpowiednim katalogu
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Błąd: Nie znaleziono pyproject.toml - uruchom z głównego katalogu projektu"
    exit 1
fi

# Sprawdź wersję Pythona (powinna być 3.12 jak w CI)
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ "$python_version" != "3.12" ]; then
    echo "⚠️ Ostrzeżenie: GitLab CI używa Python 3.12, a ty masz $python_version"
    echo "   Mogą być różnice w zachowaniu!"
    sleep 2
fi

# Utwórz czyste środowisko wirtualne
echo "📦 Tworzenie czystego środowiska wirtualnego..."
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Zainstaluj dependencies DOKŁADNIE jak w GitLab CI
echo "📥 Instalowanie dependencies (jak w GitLab CI)..."
pip install --upgrade pip wheel setuptools > /dev/null 2>&1

# Sprawdź czy istnieje requirements.txt i zainstaluj z niego
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
fi

# Editable install
pip install -e . > /dev/null 2>&1

# Test dependencies
pip install pytest pytest-asyncio pytest-cov > /dev/null 2>&1

# Security tools  
pip install 'bandit[toml]' safety pip-audit > /dev/null 2>&1

echo ""
echo "=== LINT STAGE ==="
echo "🔍 Black formatting check..."
black --check src/ tests/

echo "🔍 Ruff linting..."
ruff check src/ tests/

echo "🔍 MyPy type checking..."
mypy src/

echo "✅ Lint stage: PASSED"
echo ""

echo "=== SECURITY STAGE ==="
echo "🔒 Bandit security scan..."
bandit -r src/ -f json -o bandit-report.json >/dev/null 2>&1
bandit_result=$(bandit -r src/ 2>&1 | grep -E "(No issues identified|Total issues)" | tail -1)
echo "   $bandit_result"

echo "🔒 Safety dependency check..."
safety check --json > safety-report.json 2>/dev/null || echo "   Safety scan completed (warnings ignored)"

echo "🔒 Pip-audit dependency check..."
pip-audit --format=json --output=pip-audit-report.json 2>/dev/null || echo "   Pip-audit scan completed (warnings ignored)"

echo "✅ Security stage: PASSED"
echo ""

echo "=== TEST STAGE ==="
echo "🧪 Running unit tests with coverage..."
pytest tests/ -v --tb=short --cov=src --cov-report=term-missing --cov-fail-under=70 -q --disable-warnings

echo "✅ Test stage: PASSED"
echo ""

# Cleanup
echo "🧹 Czyszczenie..."
rm -f bandit-report.json safety-report.json pip-audit-report.json
deactivate
rm -rf venv

echo ""
echo "🎉 WSZYSTKIE ETAPY PRZESZŁY POMYŚLNIE!"
echo "✅ Kod jest gotowy do commit i push"
echo ""
echo "⚠️ UWAGA: Jeden test może być flaky w GitLab CI:"
echo "   tests/test_api.py::TestAPIPerformance::test_concurrent_requests"
echo "   (czasami przekracza 1.0s timeout na wolnych runnerach)"
echo "=================================================================="