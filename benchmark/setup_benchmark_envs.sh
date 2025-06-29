#!/bin/bash
# Setup benchmark environments on droplet

echo "📦 Setting up benchmark environments..."

# Create virtualenvs
echo "Creating virtual environments..."
python3 -m venv envs/crewai_official
python3 -m venv envs/langchain
python3 -m venv envs/pyautogen
python3 -m venv envs/crewai_full  # Pełny CrewAI dla porównania
python3 -m venv envs/litecrew_slim  # Twój odchudzony fork

# Install CrewAI Official
echo "Installing CrewAI Official..."
source envs/crewai_official/bin/activate
pip install crewai==0.134.0
deactivate

# Install LangChain
echo "Installing LangChain..."
source envs/langchain/bin/activate
pip install langchain langchain-openai
deactivate

# Install PyAutoGen
echo "Installing PyAutoGen..."
source envs/pyautogen/bin/activate
pip install pyautogen
deactivate

# CrewAI Full - identyczny jak official dla porównania
echo "Setting up CrewAI Full (dla pewności)..."
source envs/crewai_full/bin/activate
pip install crewai==0.134.0
deactivate

# LiteCrew Slim - PRAWDZIWY odchudzony fork
echo "Setting up LiteCrew Slim (YOUR OPTIMIZED FORK)..."
source envs/litecrew_slim/bin/activate
# Instalujemy tylko minimalne dependencies z requirements
if [ -f "../litecrew_minimal_requirements.txt" ]; then
    pip install -r ../litecrew_minimal_requirements.txt
else
    # Fallback - podstawowe dependencies
    pip install pydantic httpx python-dotenv click instructor
fi
# Kopiujemy kod źródłowy forka
if [ -d "../app/src/crewai" ]; then
    # Tworzymy link symboliczny do kodu
    site_packages=$(python -c "import site; print(site.getsitepackages()[0])")
    ln -sf /root/litecrewai/app/src/crewai $site_packages/crewai
    echo "✅ Linked optimized crewai fork to $site_packages/crewai"
else
    echo "❌ Fork source not found at ../app/src/crewai"
fi
deactivate

echo "✅ All environments ready!"
echo "📊 Mamy teraz:"
echo "   - crewai_official: Oficjalny CrewAI z PyPI"
echo "   - crewai_full: Ten sam CrewAI (dla double-check)" 
echo "   - litecrew_slim: TWÓJ ODCHUDZONY FORK"
echo "   - langchain: LangChain"
echo "   - pyautogen: Microsoft AutoGen"