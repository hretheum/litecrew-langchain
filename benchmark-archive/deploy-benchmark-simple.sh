#!/bin/bash
# deploy-benchmark-simple.sh - Prosty deployment benchmarku na DigitalOcean

set -e

# Kolory
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        LiteCrew Benchmark - Deployment na DigitalOcean     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Sprawdź doctl
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}❌ doctl nie znaleziony!${NC}"
    echo "Zainstaluj: brew install doctl (macOS) lub snap install doctl (Linux)"
    exit 1
fi

# Pobierz SSH key ID
SSH_KEY_ID=$(doctl compute ssh-key list --format ID --no-header | head -1)
if [ -z "$SSH_KEY_ID" ]; then
    echo -e "${RED}❌ Brak SSH keys w DigitalOcean!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ SSH Key ID: $SSH_KEY_ID${NC}"

# Przygotuj pakiet
echo -e "\n${YELLOW}1. Przygotowuję pakiet benchmarku...${NC}"
./prepare-benchmark-package.sh

# Stwórz droplet
DROPLET_NAME="benchmark-litecrew-$(date +%Y%m%d-%H%M)"
echo -e "\n${YELLOW}2. Tworzę droplet: $DROPLET_NAME${NC}"

doctl compute droplet create "$DROPLET_NAME" \
    --size c-4 \
    --image ubuntu-22-04-x64 \
    --region nyc3 \
    --ssh-keys "$SSH_KEY_ID" \
    --wait

# Pobierz IP
DROPLET_IP=$(doctl compute droplet list --format "Name,PublicIPv4" --no-header | grep "$DROPLET_NAME" | awk '{print $2}')
echo -e "${GREEN}✅ Droplet utworzony: $DROPLET_IP${NC}"

# Czekaj na SSH
echo -e "\n${YELLOW}3. Czekam na dostępność SSH...${NC}"
sleep 30
while ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@$DROPLET_IP "echo 'SSH OK'" &> /dev/null; do
    echo -n "."
    sleep 5
done
echo -e " ${GREEN}Gotowe!${NC}"

# Kopiuj pakiet
echo -e "\n${YELLOW}4. Kopiuję pakiet na droplet...${NC}"
scp -o StrictHostKeyChecking=no /tmp/litecrew-benchmark-package.tar.gz root@$DROPLET_IP:/tmp/

# Rozpakuj i uruchom
echo -e "\n${YELLOW}5. Rozpakowuję i uruchamiam benchmark...${NC}"
ssh -o StrictHostKeyChecking=no root@$DROPLET_IP << 'EOF'
cd /root
tar -xzf /tmp/litecrew-benchmark-package.tar.gz
chmod +x install_and_run.sh
./install_and_run.sh
EOF

# Pobierz wyniki
echo -e "\n${YELLOW}6. Pobieram wyniki...${NC}"
RESULTS_DIR="benchmark-results-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RESULTS_DIR"
scp -o StrictHostKeyChecking=no root@$DROPLET_IP:/root/benchmark/benchmark_results.json "$RESULTS_DIR/"

# Pokaż wyniki
echo -e "\n${BLUE}📊 WYNIKI BENCHMARKU:${NC}"
cat "$RESULTS_DIR/benchmark_results.json"

# Zapytaj o usunięcie
echo -e "\n${YELLOW}Usunąć droplet? (t/n)${NC}"
read -r response
if [[ "$response" =~ ^[Tt]$ ]]; then
    doctl compute droplet delete "$DROPLET_NAME" --force
    echo -e "${GREEN}✅ Droplet usunięty${NC}"
else
    echo -e "${BLUE}Droplet pozostawiony: ssh root@$DROPLET_IP${NC}"
    echo -e "${YELLOW}Auto-usunięcie za 4 godziny${NC}"
    ssh -o StrictHostKeyChecking=no root@$DROPLET_IP "echo 'doctl compute droplet delete $DROPLET_NAME -f' | at now + 4 hours"
fi

echo -e "\n${GREEN}✅ Benchmark zakończony!${NC}"
echo -e "Wyniki w: $RESULTS_DIR/"