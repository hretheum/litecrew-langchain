#!/bin/bash
# Setup AutoGPT for benchmark

echo "📦 Setting up AutoGPT..."

# Create separate directory
mkdir -p frameworks
cd frameworks

# Clone AutoGPT
if [ ! -d "AutoGPT" ]; then
    echo "Cloning AutoGPT..."
    git clone https://github.com/Significant-Gravitas/AutoGPT.git
    cd AutoGPT
    git checkout stable  # Use stable branch
else
    echo "AutoGPT already cloned"
    cd AutoGPT
    git pull
fi

# Create venv for AutoGPT
echo "Creating AutoGPT virtual environment..."
python3 -m venv autogpt_env
source autogpt_env/bin/activate

# Install dependencies
echo "Installing AutoGPT dependencies..."
pip install -e .

echo "✅ AutoGPT setup complete!"
echo "Note: AutoGPT requires configuration in .env file"