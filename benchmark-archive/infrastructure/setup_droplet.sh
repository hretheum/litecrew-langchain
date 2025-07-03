#!/bin/bash
# setup_droplet.sh - Automatyczny setup środowiska benchmarkowego

set -e

# Kolory
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 LiteCrew Full Benchmark - Infrastructure Setup${NC}"
echo "=================================================="

# 1. Sprawdzenie zależności
echo -e "\n${YELLOW}Checking dependencies...${NC}"
command -v doctl >/dev/null 2>&1 || { echo -e "${RED}doctl required but not installed.${NC}"; exit 1; }
command -v ssh >/dev/null 2>&1 || { echo -e "${RED}ssh required but not installed.${NC}"; exit 1; }

# 2. Konfiguracja
DROPLET_NAME="benchmark-full-$(date +%Y%m%d-%H%M%S)"
DROPLET_SIZE="c-4"  # 8 vCPU, 16GB RAM
DROPLET_IMAGE="docker-20-04"
DROPLET_REGION="nyc3"
SSH_KEY_ID=$(doctl compute ssh-key list --format ID --no-header | head -1)

echo -e "${GREEN}Configuration:${NC}"
echo "  Name: $DROPLET_NAME"
echo "  Size: $DROPLET_SIZE (8 vCPU, 16GB RAM)"
echo "  Image: $DROPLET_IMAGE"
echo "  SSH Key: $SSH_KEY_ID"

# 3. Tworzenie dropletu
echo -e "\n${YELLOW}Creating droplet...${NC}"
DROPLET_ID=$(doctl compute droplet create "$DROPLET_NAME" \
    --size "$DROPLET_SIZE" \
    --image "$DROPLET_IMAGE" \
    --region "$DROPLET_REGION" \
    --ssh-keys "$SSH_KEY_ID" \
    --enable-monitoring \
    --format ID \
    --no-header \
    --wait)

# Pobierz IP
DROPLET_IP=$(doctl compute droplet get "$DROPLET_ID" --format PublicIPv4 --no-header)
echo -e "${GREEN}✅ Droplet created: $DROPLET_IP${NC}"

# 4. Czekaj na SSH
echo -e "\n${YELLOW}Waiting for SSH...${NC}"
while ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@"$DROPLET_IP" "echo 'SSH ready'" &>/dev/null; do
    echo -n "."
    sleep 5
done
echo -e " ${GREEN}Ready!${NC}"

# 5. Zapisz konfigurację
cat > benchmark_config.env << EOF
DROPLET_NAME=$DROPLET_NAME
DROPLET_ID=$DROPLET_ID
DROPLET_IP=$DROPLET_IP
CREATED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF

echo -e "\n${GREEN}✅ Infrastructure ready!${NC}"
echo "SSH: ssh root@$DROPLET_IP"
echo "Config saved to: benchmark_config.env"
echo ""
echo "Next step: ./deploy_monitoring.sh"