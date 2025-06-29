#!/bin/bash
# download-results.sh - Download benchmark results from droplet

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if droplet info exists
if [ ! -f /tmp/benchmark-droplet-ip ]; then
    echo -e "${RED}❌ No droplet info found!${NC}"
    echo "Run deploy-benchmark-droplet.sh first"
    exit 1
fi

DROPLET_IP=$(cat /tmp/benchmark-droplet-ip)
DROPLET_NAME=$(cat /tmp/benchmark-droplet-name)

echo -e "${YELLOW}Downloading results from $DROPLET_NAME ($DROPLET_IP)...${NC}"

# Create results directory
RESULTS_DIR="benchmark-results-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RESULTS_DIR"

# Download results
scp -r -o StrictHostKeyChecking=no root@$DROPLET_IP:/root/benchmark/results/* "$RESULTS_DIR/" || {
    echo -e "${RED}❌ Failed to download results${NC}"
    exit 1
}

# Create archive
tar -czf "$RESULTS_DIR.tar.gz" "$RESULTS_DIR"

echo -e "${GREEN}✅ Results downloaded successfully!${NC}"
echo -e "   Directory: $RESULTS_DIR/"
echo -e "   Archive: $RESULTS_DIR.tar.gz"

# Show summary if available
if [ -f "$RESULTS_DIR/benchmark_report.md" ]; then
    echo -e "\n${YELLOW}=== Quick Summary ===${NC}"
    grep -A5 "Executive Summary" "$RESULTS_DIR/benchmark_report.md" || true
fi

echo -e "\n${YELLOW}View full report:${NC} $RESULTS_DIR/benchmark_report.md"
echo -e "${YELLOW}View charts:${NC} $RESULTS_DIR/*.png"