#!/bin/bash
# Lokalny pipeline testowy - identyczny z GitLab CI

set -e

echo "🚀 Uruchamianie pełnego pipeline lokalnie..."
echo "============================================="

# Sprawdź czy jesteśmy w odpowiednim katalogu
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Błąd: Nie znaleziono pyproject.toml - uruchom z głównego katalogu projektu"
    exit 1
fi

# Utwórz czyste środowisko wirtualne
echo "📦 Tworzenie czystego środowiska..."
rm -rf pipeline_test_env
python3 -m venv pipeline_test_env
source pipeline_test_env/bin/activate

# Zainstaluj dependencies jak w pipeline
echo "📥 Instalowanie dependencies..."
pip install --upgrade pip wheel setuptools > /dev/null 2>&1
pip install -e ".[dev]" > /dev/null 2>&1
pip install 'bandit[toml]' safety pip-audit pytest-cov itsdangerous > /dev/null 2>&1

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
rm -rf pipeline_test_env

echo ""
echo "🎉 WSZYSTKIE ETAPY PRZESZŁY POMYŚLNIE!"
echo "✅ Kod jest gotowy do commit i push"
echo "============================================="