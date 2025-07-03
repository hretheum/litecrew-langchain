#!/bin/bash
# prepare-benchmark-package.sh - Przygotowuje pakiet benchmarku do deployment na DO

set -e

echo "📦 Przygotowuję pakiet benchmarku..."

# Tworzymy tymczasowy katalog
TEMP_DIR="/tmp/litecrew-benchmark-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$TEMP_DIR/benchmark"

# Kopiujemy niezbędne pliki
echo "Kopiuję pliki benchmarku..."
cp -r /Users/hretheum/dev/bezrobocie/litecrew/benchmark/*.py "$TEMP_DIR/benchmark/" 2>/dev/null || true
cp -r /Users/hretheum/dev/bezrobocie/litecrew/benchmark/*.sh "$TEMP_DIR/benchmark/" 2>/dev/null || true
cp -r /Users/hretheum/dev/bezrobocie/litecrew/benchmark/scripts "$TEMP_DIR/benchmark/" 2>/dev/null || true
cp -r /Users/hretheum/dev/bezrobocie/litecrew/benchmark/requirements*.txt "$TEMP_DIR/benchmark/" 2>/dev/null || true

# Kopiujemy fork CrewAI
echo "Kopiuję litecrew fork..."
mkdir -p "$TEMP_DIR/crewai-fork"
cp -r /Users/hretheum/dev/bezrobocie/litecrew/crewai-fork/* "$TEMP_DIR/crewai-fork/" 2>/dev/null || true

# Tworzymy główny skrypt benchmarku
cat > "$TEMP_DIR/benchmark/run_full_benchmark.py" << 'EOF'
#!/usr/bin/env python3
"""
Full benchmark comparing frameworks
"""
import subprocess
import json
import time
import os
import sys
from pathlib import Path

def setup_environments():
    """Setup all virtual environments"""
    frameworks = {
        'crewai_official': 'crewai==0.134.0',
        'langchain': 'langchain langchain-openai',
        'pyautogen': 'pyautogen',
        'litecrew_fork': '../crewai-fork'  # Local fork
    }
    
    for env_name, package in frameworks.items():
        print(f"\n📦 Setting up {env_name}...")
        
        # Create venv
        subprocess.run([sys.executable, '-m', 'venv', f'envs/{env_name}'])
        
        # Install package
        if env_name == 'litecrew_fork':
            # Install local fork
            subprocess.run([
                f'envs/{env_name}/bin/pip', 'install', '-e', package
            ])
        else:
            subprocess.run([
                f'envs/{env_name}/bin/pip', 'install'] + package.split()
            )

def run_benchmark():
    """Run benchmark tests"""
    results = []
    
    # Test każdego frameworka
    for env_name in ['crewai_official', 'langchain', 'pyautogen', 'litecrew_fork']:
        print(f"\n🧪 Testing {env_name}...")
        
        start_time = time.time()
        
        # Prosty test importu i utworzenia agenta
        test_script = f"""
import time
start = time.time()

try:
    if '{env_name}' in ['crewai_official', 'litecrew_fork']:
        from crewai import Agent, Task, Crew
        agent = Agent(role="Test", goal="Test", backstory="Test")
        print("SUCCESS")
    elif '{env_name}' == 'langchain':
        from langchain.agents import AgentExecutor
        print("SUCCESS")
    elif '{env_name}' == 'pyautogen':
        import autogen
        print("SUCCESS")
except Exception as e:
    print(f"ERROR: {{e}}")

print(f"Import time: {{time.time() - start}}")
"""
        
        # Zapisz i uruchom test
        with open('/tmp/test_framework.py', 'w') as f:
            f.write(test_script)
            
        result = subprocess.run(
            [f'envs/{env_name}/bin/python', '/tmp/test_framework.py'],
            capture_output=True,
            text=True
        )
        
        results.append({
            'framework': env_name,
            'output': result.stdout,
            'error': result.stderr,
            'duration': time.time() - start_time
        })
    
    # Zapisz wyniki
    with open('benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Benchmark zakończony!")
    
if __name__ == "__main__":
    print("🚀 LiteCrew Benchmark Runner")
    print("=" * 50)
    
    # Utwórz katalogi
    Path("envs").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    
    # Setup i benchmark
    setup_environments()
    run_benchmark()
EOF

# Tworzymy skrypt instalacyjny dla dropletu
cat > "$TEMP_DIR/install_and_run.sh" << 'EOF'
#!/bin/bash
set -e

echo "🚀 Instalacja i uruchomienie benchmarku na droplecie..."

# Instaluj wymagania systemowe
apt-get update -qq
apt-get install -y python3.11 python3.11-venv python3-pip git

# Przejdź do katalogu benchmark
cd /root/benchmark

# Uruchom benchmark
python3.11 run_full_benchmark.py

# Pokaż wyniki
echo ""
echo "📊 WYNIKI BENCHMARKU:"
cat benchmark_results.json

echo ""
echo "✅ Benchmark zakończony!"
EOF

chmod +x "$TEMP_DIR/install_and_run.sh"
chmod +x "$TEMP_DIR/benchmark/run_full_benchmark.py"

# Tworzę archiwum
ARCHIVE_NAME="litecrew-benchmark-package.tar.gz"
cd "$TEMP_DIR"
tar -czf "/tmp/$ARCHIVE_NAME" .

echo ""
echo "✅ Pakiet przygotowany: /tmp/$ARCHIVE_NAME"
echo ""
echo "📋 Kolejne kroki:"
echo "1. Stwórz droplet: doctl compute droplet create benchmark-litecrew --size c-4-8gib --image ubuntu-22-04-x64 --region nyc3 --ssh-keys [YOUR_KEY_ID] --wait"
echo "2. Skopiuj pakiet: scp /tmp/$ARCHIVE_NAME root@[DROPLET_IP]:/tmp/"
echo "3. Rozpakuj: ssh root@[DROPLET_IP] 'cd /root && tar -xzf /tmp/$ARCHIVE_NAME'"
echo "4. Uruchom: ssh root@[DROPLET_IP] 'cd /root && ./install_and_run.sh'"
echo ""
echo "💡 Lub użyj: ./deploy-benchmark-simple.sh"