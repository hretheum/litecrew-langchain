#!/bin/bash
# Setup benchmark environments on droplet

echo "📦 Setting up benchmark environments..."

# Create virtualenvs
echo "Creating virtual environments..."
python3 -m venv envs/crewai_official
python3 -m venv envs/langchain
python3 -m venv envs/pyautogen
python3 -m venv envs/litecrew_fork

# Install CrewAI
echo "Installing CrewAI..."
source envs/crewai_official/bin/activate
pip install crewai
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

# LiteCrew - for now just copy CrewAI
echo "Setting up LiteCrew (simulated)..."
source envs/litecrew_fork/bin/activate
pip install crewai
deactivate

echo "✅ All environments ready!"