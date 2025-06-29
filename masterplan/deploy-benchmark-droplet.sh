#!/bin/bash
# deploy-benchmark-droplet.sh - Complete DigitalOcean Benchmark Deployment
# This script creates a droplet, runs benchmarks, and downloads results

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DROPLET_NAME="benchmark-litecrewai-$(date +%Y%m%d-%H%M%S)"
DROPLET_SIZE="c-4"  # CPU-Optimized 8GB/4vCPU
DROPLET_IMAGE="ubuntu-22-04-x64"
DROPLET_REGION="nyc3"  # Change if needed
BENCHMARK_TIMEOUT="120m"  # 2 hours max
GITLAB_REPO="https://gitlab.com/eof3/litecrewai.git"

# Functions
print_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║          LiteCrewAI Benchmark Deployment Script            ║"
    echo "║                                                            ║"
    echo "║  This script will:                                         ║"
    echo "║  1. Create a DigitalOcean droplet                         ║"
    echo "║  2. Setup benchmark environment                           ║"
    echo "║  3. Run all framework benchmarks                          ║"
    echo "║  4. Download results                                      ║"
    echo "║  5. Destroy droplet                                      ║"
    echo "║                                                            ║"
    echo "║  Estimated time: 60-90 minutes                           ║"
    echo "║  Estimated cost: $0.25-0.50                              ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"
    
    # Check doctl
    if ! command -v doctl &> /dev/null; then
        echo -e "${RED}❌ doctl not found!${NC}"
        echo "Install with: brew install doctl (macOS) or snap install doctl (Linux)"
        exit 1
    fi
    
    # Check if authenticated
    if ! doctl auth list &> /dev/null; then
        echo -e "${RED}❌ doctl not authenticated!${NC}"
        echo "Run: doctl auth init"
        exit 1
    fi
    
    # Check SSH keys
    SSH_KEYS=$(doctl compute ssh-key list --format ID --no-header)
    if [ -z "$SSH_KEYS" ]; then
        echo -e "${RED}❌ No SSH keys found in DigitalOcean!${NC}"
        echo "Add your SSH key: doctl compute ssh-key create [name] --public-key-file ~/.ssh/id_rsa.pub"
        exit 1
    fi
    SSH_KEY_ID=$(echo "$SSH_KEYS" | head -1)
    
    echo -e "${GREEN}✅ All dependencies satisfied${NC}"
    echo -e "   - doctl: $(doctl version)"
    echo -e "   - SSH Key ID: $SSH_KEY_ID"
}

create_droplet() {
    echo -e "\n${YELLOW}Creating droplet...${NC}"
    echo -e "   Name: $DROPLET_NAME"
    echo -e "   Size: $DROPLET_SIZE"
    echo -e "   Region: $DROPLET_REGION"
    
    # Create user data script
    cat > /tmp/user-data.sh << 'EOF'
#!/bin/bash# Initial setup
apt-get update -qq
apt-get install -y -qq git python3-pip

# Clone and run setup
cd /root
git clone GITLAB_REPO_PLACEHOLDER /root/bezrobocie
cd /root/bezrobocie/benchmark
chmod +x setup-benchmark.sh
./setup-benchmark.sh
EOF
    
    # Replace placeholder with actual repo
    sed -i '' "s|GITLAB_REPO_PLACEHOLDER|$GITLAB_REPO|g" /tmp/user-data.sh
    
    # Create droplet
    doctl compute droplet create "$DROPLET_NAME" \
        --size "$DROPLET_SIZE" \
        --image "$DROPLET_IMAGE" \
        --region "$DROPLET_REGION" \
        --ssh-keys "$SSH_KEY_ID" \
        --user-data-file /tmp/user-data.sh \
        --wait
    
    # Get droplet IP
    DROPLET_IP=$(doctl compute droplet list --format "Name,PublicIPv4" --no-header | grep "$DROPLET_NAME" | awk '{print $2}')
    
    if [ -z "$DROPLET_IP" ]; then
        echo -e "${RED}❌ Failed to get droplet IP!${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Droplet created successfully!${NC}"
    echo -e "   IP: $DROPLET_IP"
    
    # Save droplet info
    echo "$DROPLET_NAME" > /tmp/benchmark-droplet-name
    echo "$DROPLET_IP" > /tmp/benchmark-droplet-ip
}

wait_for_setup() {
    echo -e "\n${YELLOW}Waiting for initial setup to complete...${NC}"
    echo -e "This usually takes 3-5 minutes..."
    
    # Wait for SSH to be available
    echo -n "Waiting for SSH..."
    while ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@$DROPLET_IP "echo 'SSH ready'" &> /dev/null; do
        echo -n "."
        sleep 10
    done
    echo -e " ${GREEN}Ready!${NC}"
    
    # Wait for setup script to complete
    echo -n "Waiting for environment setup..."
    while ! ssh -o StrictHostKeyChecking=no root@$DROPLET_IP "test -f /root/benchmark/README.md" &> /dev/null; do
        echo -n "."
        sleep 10
    done
    echo -e " ${GREEN}Complete!${NC}"
}

run_benchmarks() {
    echo -e "\n${YELLOW}Running benchmarks...${NC}"
    echo -e "This will take 45-60 minutes. Starting at $(date)"
    
    # Create benchmark script
    cat > /tmp/run-benchmark-remote.sh << 'EOF'
#!/bin/bash
cd /root/benchmark

# Start system monitor
tmux new-session -d -s monitor './system_monitor.sh'

# Create run script if not exists
cat > run_all_benchmarks.sh << 'SCRIPT'
#!/bin/bash
source benchmark_env/bin/activate
python run_benchmarks.py --iterations 3 --output results
SCRIPT
chmod +x run_all_benchmarks.sh

# Run benchmarks
timeout 90m ./run_all_benchmarks.sh

# Stop monitor
tmux kill-session -t monitor 2>/dev/null || true

# Create summary
echo "Benchmark completed at $(date)" > results/completion.txt
find results/ -type f -name "*.json" | wc -l >> results/completion.txt
EOF
    
    # Copy and execute script
    scp -o StrictHostKeyChecking=no /tmp/run-benchmark-remote.sh root@$DROPLET_IP:/root/
    
    # Run benchmarks with timeout
    echo -e "${BLUE}Starting benchmark execution...${NC}"
    if ssh -o StrictHostKeyChecking=no root@$DROPLET_IP "timeout $BENCHMARK_TIMEOUT bash /root/run-benchmark-remote.sh"; then
        echo -e "${GREEN}✅ Benchmarks completed successfully!${NC}"
    else
        echo -e "${YELLOW}⚠️  Benchmarks timed out or encountered an error${NC}"
        echo -e "Attempting to download partial results..."
    fi
}

download_results() {
    echo -e "\n${YELLOW}Downloading results...${NC}"
    
    # Create local results directory
    RESULTS_DIR="benchmark-results-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$RESULTS_DIR"
    
    # Download all results
    echo "Downloading from $DROPLET_IP to $RESULTS_DIR/"
    scp -r -o StrictHostKeyChecking=no root@$DROPLET_IP:/root/benchmark/results/* "$RESULTS_DIR/" || true
    
    # Create archive
    ARCHIVE_NAME="benchmark-results-$(date +%Y%m%d-%H%M%S).tar.gz"
    tar -czf "$ARCHIVE_NAME" "$RESULTS_DIR"
    
    echo -e "${GREEN}✅ Results downloaded to:${NC}"
    echo -e "   Directory: $RESULTS_DIR/"
    echo -e "   Archive: $ARCHIVE_NAME"
    
    # Quick summary
    if [ -f "$RESULTS_DIR/benchmark_report.md" ]; then
        echo -e "\n${BLUE}Quick Summary:${NC}"
        head -n 20 "$RESULTS_DIR/benchmark_report.md" | grep -E "(CrewAI|LangChain|AutoGPT|Target)" || true
    fi
}

destroy_droplet() {
    echo -e "\n${YELLOW}Destroying droplet...${NC}"
    
    if [ -f /tmp/benchmark-droplet-name ]; then
        DROPLET_NAME=$(cat /tmp/benchmark-droplet-name)
        doctl compute droplet delete "$DROPLET_NAME" --force
        echo -e "${GREEN}✅ Droplet destroyed${NC}"
        
        # Cleanup temp files
        rm -f /tmp/benchmark-droplet-name /tmp/benchmark-droplet-ip
    else
        echo -e "${YELLOW}⚠️  No droplet info found${NC}"
    fi
}

main() {
    print_banner
    
    # Check if resuming
    if [ -f /tmp/benchmark-droplet-ip ]; then
        echo -e "${YELLOW}Found existing droplet info. Resume previous run? (y/n)${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            DROPLET_IP=$(cat /tmp/benchmark-droplet-ip)
            DROPLET_NAME=$(cat /tmp/benchmark-droplet-name)
            echo -e "Resuming with droplet: $DROPLET_NAME ($DROPLET_IP)"
        else
            destroy_droplet
        fi
    fi
    
    # Full run
    if [ -z "$DROPLET_IP" ]; then
        check_dependencies
        create_droplet
        wait_for_setup
    fi
    
    run_benchmarks
    download_results
    
    # Ask before destroying
    echo -e "\n${YELLOW}Destroy droplet now? (y/n)${NC}"
    echo -e "Note: It will auto-destroy in 4 hours anyway"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        destroy_droplet
    else
        echo -e "${BLUE}Droplet kept alive at: $DROPLET_IP${NC}"
        echo -e "SSH: ssh root@$DROPLET_IP"
        echo -e "Destroy later: doctl compute droplet delete $DROPLET_NAME --force"
    fi
    
    echo -e "\n${GREEN}🎉 Benchmark deployment complete!${NC}"
    echo -e "Check your results in: $RESULTS_DIR/"
}

# Run main function
main "$@"