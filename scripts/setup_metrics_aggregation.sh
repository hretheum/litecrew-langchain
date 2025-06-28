#!/bin/bash
# Setup systemd timer for metrics aggregation

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Setting up metrics aggregation timer...${NC}"

# Create systemd service
cat > /tmp/litecrewai-metrics-aggregation.service << 'EOF'
[Unit]
Description=LiteCrewAI Metrics Aggregation
After=network.target

[Service]
Type=oneshot
User=litecrewai
Group=litecrewai
WorkingDirectory=/opt/litecrewai
Environment="PYTHONPATH=/opt/litecrewai"
ExecStart=/opt/litecrewai/venv/bin/python /opt/litecrewai/scripts/aggregate_metrics.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create systemd timer
cat > /tmp/litecrewai-metrics-aggregation.timer << 'EOF'
[Unit]
Description=Run LiteCrewAI metrics aggregation every minute
Requires=litecrewai-metrics-aggregation.service

[Timer]
OnBootSec=1min
OnUnitActiveSec=1min
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Install service and timer
sudo mv /tmp/litecrewai-metrics-aggregation.service /etc/systemd/system/
sudo mv /tmp/litecrewai-metrics-aggregation.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start timer
sudo systemctl enable litecrewai-metrics-aggregation.timer
sudo systemctl start litecrewai-metrics-aggregation.timer

echo -e "${GREEN}Metrics aggregation timer installed!${NC}"
echo -e "${GREEN}Check status with: sudo systemctl status litecrewai-metrics-aggregation.timer${NC}"