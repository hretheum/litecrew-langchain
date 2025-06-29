#!/bin/bash
# setup-benchmark.sh - DigitalOcean Droplet Initial Setup
# This script runs automatically when droplet is created

set -e

echo "🚀 Starting Benchmark Environment Setup"
echo "====================================="
echo "Time: $(date)"
echo "User: $(whoami)"
echo "System: $(uname -a)"
echo ""

# 1. System Update
echo "📦 Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq \
    build-essential \
    software-properties-common \
    curl \
    wget \
    git \
    htop \
    tmux \
    iotop \
    sysstat \
    lm-sensors

# 2. Python 3.11 Installation
echo "🐍 Installing Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y
apt-get update -qq
apt-get install -y -qq \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip

# Set Python 3.11 as default
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
update-alternatives --set python3 /usr/bin/python3.11

# 3. Docker Installation
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker root
systemctl enable docker
systemctl start docker

# Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 4. System Monitoring Tools
echo "📊 Installing monitoring tools..."
pip3 install --upgrade pip
pip3 install glances psutil memory-profiler

# 5. Configure System Limits
echo "⚙️ Configuring system limits..."
cat >> /etc/security/limits.conf << EOF
* soft nofile 65536
* hard nofile 65536
* soft nproc 65536
* hard nproc 65536
EOF

# Configure sysctl for better performance
cat >> /etc/sysctl.conf << EOF
# Benchmark optimizations
vm.swappiness = 10
vm.vfs_cache_pressure = 50
fs.file-max = 65536
EOF
sysctl -p

# 6. Create benchmark user and directory
echo "👤 Setting up benchmark environment..."
mkdir -p /root/benchmark
cd /root

# 7. Clone repository (placeholder - update with actual repo)
echo "📥 Cloning benchmark repository..."
# git clone https://gitlab.com/eof3/litecrewai.git /root/bezrobocie

# 8. Create Python virtual environment
echo "🔧 Creating Python virtual environment..."
cd /root/benchmark
python3.11 -m venv benchmark_env

# Create requirements.txt if not exists
cat > requirements.txt << EOF
# Testing CURRENT versions from PyPI (as of 06/2025)
crewai==0.30.11          # Latest stable CrewAI
langchain==0.2.1         # Latest LangChain v0.2
langchain-openai==0.1.8  # Required for LangChain
autogpt==0.5.0           # Latest available AutoGPT

# Benchmarking tools
psutil==5.9.8
memory-profiler==0.61.0
matplotlib==3.8.2
pandas==2.1.4
numpy==1.26.2
seaborn==0.13.0
tqdm==4.66.1

# LLM providers for testing
openai==1.30.1
anthropic==0.25.7

# Utilities
python-dotenv==1.0.0
docker==7.0.0
EOF

# Activate and install packages
source benchmark_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 9. Create helper scripts
echo "📝 Creating helper scripts..."

# System monitor script
cat > /root/benchmark/system_monitor.sh << 'EOF'
#!/bin/bash
LOG_FILE="/root/benchmark/results/system_monitor.log"
mkdir -p /root/benchmark/results

echo "Starting system monitoring at $(date)" | tee $LOG_FILE

while true; do
    echo "=== $(date) ===" | tee -a $LOG_FILE
    
    # Memory snapshot
    echo "MEMORY:" | tee -a $LOG_FILE
    free -h | tee -a $LOG_FILE
    
    # Top processes by memory
    echo -e "\nTOP PROCESSES BY MEMORY:" | tee -a $LOG_FILE
    ps aux --sort=-%mem | head -n 5 | tee -a $LOG_FILE
    
    # CPU usage
    echo -e "\nCPU USAGE:" | tee -a $LOG_FILE
    mpstat 1 1 | tee -a $LOG_FILE
    
    # Docker stats
    echo -e "\nDOCKER:" | tee -a $LOG_FILE
    docker stats --no-stream 2>/dev/null | tee -a $LOG_FILE
    
    # Disk I/O
    echo -e "\nDISK I/O:" | tee -a $LOG_FILE
    iostat -x 1 2 | tail -n 20 | tee -a $LOG_FILE
    
    echo -e "\n" | tee -a $LOG_FILE
    sleep 10
done
EOF
chmod +x /root/benchmark/system_monitor.sh

# Quick test script
cat > /root/benchmark/test_setup.py << 'EOF'
#!/usr/bin/env python3
import sys
import psutil
import docker

print("🔍 Testing Benchmark Setup")
print("=" * 50)

# Python version
print(f"✅ Python: {sys.version}")

# Memory available
mem = psutil.virtual_memory()
print(f"✅ Memory: {mem.total / (1024**3):.1f} GB total, {mem.available / (1024**3):.1f} GB available")

# CPU info
print(f"✅ CPU: {psutil.cpu_count()} cores")

# Docker
try:
    client = docker.from_env()
    print(f"✅ Docker: {client.version()['Version']}")
except:
    print("❌ Docker: Not available")

# Disk space
disk = psutil.disk_usage('/')
print(f"✅ Disk: {disk.free / (1024**3):.1f} GB free")

print("\n✅ Setup complete! Ready for benchmarking.")
EOF
chmod +x /root/benchmark/test_setup.py

# 10. Setup auto-cleanup
echo "⏰ Setting up auto-cleanup..."
echo "doctl compute droplet delete $(hostname) -f" | at now + 4 hours 2>/dev/null || true

# 11. Final verification
echo ""
echo "🔍 Running setup verification..."
cd /root/benchmark
source benchmark_env/bin/activate
python test_setup.py

# 12. Create README
cat > /root/benchmark/README.md << EOF
# Benchmark Environment Ready!

## Quick Start

1. Activate environment:
   \`\`\`bash
   cd /root/benchmark
   source benchmark_env/bin/activate
   \`\`\`

2. Run benchmarks:
   \`\`\`bash
   ./run_all_benchmarks.sh
   \`\`\`

3. Monitor system:
   \`\`\`bash
   tmux new-session -d -s monitor './system_monitor.sh'
   \`\`\`

## Results
Results will be saved to \`/root/benchmark/results/\`

## Auto-cleanup
This droplet will auto-destroy in 4 hours.
EOF

echo ""
echo "✅ SETUP COMPLETE!"
echo "================="
echo "📍 Benchmark directory: /root/benchmark"
echo "🐍 Python environment: /root/benchmark/benchmark_env"
echo "📊 To start monitoring: tmux new -s monitor './system_monitor.sh'"
echo "🚀 To run benchmarks: cd /root/benchmark && ./run_all_benchmarks.sh"
echo "⏰ Auto-destroy scheduled in 4 hours"
echo ""
echo "Happy benchmarking! 🎉"