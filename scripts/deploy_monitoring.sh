#!/bin/bash
# Deploy monitoring and logging infrastructure to DigitalOcean droplet

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Droplet configuration from CLAUDE.md
DROPLET_IP="46.101.181.183"
SSH_KEY="$HOME/.ssh/id_rag"
REMOTE_USER="litecrewai"

echo -e "${GREEN}=== Deploying Monitoring & Logging to DigitalOcean ===${NC}"

# Function to execute commands on droplet
remote_exec() {
    ssh -i ${SSH_KEY} ${REMOTE_USER}@${DROPLET_IP} "$@"
}

# Function to copy files to droplet
remote_copy() {
    scp -i ${SSH_KEY} -r "$1" ${REMOTE_USER}@${DROPLET_IP}:"$2"
}

echo -e "${YELLOW}Step 1: Creating directories on droplet...${NC}"
remote_exec "mkdir -p /opt/litecrewai/{logs,data,scripts} && chown -R litecrewai:litecrewai /opt/litecrewai"

echo -e "${YELLOW}Step 2: Copying monitoring scripts...${NC}"
# Copy all monitoring scripts
remote_copy "scripts/log_dashboard.py" "/opt/litecrewai/scripts/"
remote_copy "scripts/check_critical_errors.py" "/opt/litecrewai/scripts/"
remote_copy "scripts/aggregate_metrics.py" "/opt/litecrewai/scripts/"
remote_copy "scripts/setup_logrotate.sh" "/opt/litecrewai/scripts/"
remote_copy "scripts/setup_metrics_aggregation.sh" "/opt/litecrewai/scripts/"

echo -e "${YELLOW}Step 3: Copying validation scripts...${NC}"
remote_exec "mkdir -p /opt/litecrewai/masterplan/src/faza-0"
remote_copy "masterplan/src/faza-0/validate_logging.py" "/opt/litecrewai/masterplan/src/faza-0/"
remote_copy "masterplan/src/faza-0/validate_monitoring.py" "/opt/litecrewai/masterplan/src/faza-0/"

echo -e "${YELLOW}Step 4: Setting up logrotate...${NC}"
remote_exec "cd /opt/litecrewai && sudo ./scripts/setup_logrotate.sh"

echo -e "${YELLOW}Step 5: Setting up metrics aggregation timer...${NC}"
remote_exec "cd /opt/litecrewai && sudo ./scripts/setup_metrics_aggregation.sh"

echo -e "${YELLOW}Step 6: Creating monitoring service...${NC}"
# Create systemd service for monitoring dashboard
cat << 'EOF' | ssh -i ${SSH_KEY} ${REMOTE_USER}@${DROPLET_IP} "cat > /tmp/litecrewai-monitoring.service"
[Unit]
Description=LiteCrewAI Monitoring Dashboard
After=network.target

[Service]
Type=simple
User=litecrewai
Group=litecrewai
WorkingDirectory=/opt/litecrewai
Environment="PYTHONPATH=/opt/litecrewai"
ExecStart=/opt/litecrewai/venv/bin/python scripts/log_dashboard.py --hours 24
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

remote_exec "sudo mv /tmp/litecrewai-monitoring.service /etc/systemd/system/"
remote_exec "sudo systemctl daemon-reload"

echo -e "${YELLOW}Step 7: Setting up cron jobs...${NC}"
# Setup cron for error checking
cat << 'EOF' | ssh -i ${SSH_KEY} ${REMOTE_USER}@${DROPLET_IP} "crontab -u litecrewai -"
# Check for critical errors every 5 minutes
*/5 * * * * /opt/litecrewai/venv/bin/python /opt/litecrewai/scripts/check_critical_errors.py

# Generate log dashboard report every hour
0 * * * * /opt/litecrewai/venv/bin/python /opt/litecrewai/scripts/log_dashboard.py > /opt/litecrewai/logs/dashboard_report.txt

# Run validation checks daily at 6 AM
0 6 * * * /opt/litecrewai/venv/bin/python /opt/litecrewai/masterplan/src/faza-0/validate_logging.py > /opt/litecrewai/logs/validation_logging.txt 2>&1
0 6 * * * /opt/litecrewai/venv/bin/python /opt/litecrewai/masterplan/src/faza-0/validate_monitoring.py > /opt/litecrewai/logs/validation_monitoring.txt 2>&1
EOF

echo -e "${YELLOW}Step 8: Setting proper permissions...${NC}"
remote_exec "chown -R litecrewai:litecrewai /opt/litecrewai/scripts /opt/litecrewai/masterplan"
remote_exec "chmod +x /opt/litecrewai/scripts/*.py /opt/litecrewai/scripts/*.sh"
remote_exec "chmod +x /opt/litecrewai/masterplan/src/faza-0/*.py"

echo -e "${YELLOW}Step 9: Running initial validation...${NC}"
echo -e "${GREEN}Running logging validation...${NC}"
remote_exec "cd /opt/litecrewai && sudo -u litecrewai /opt/litecrewai/venv/bin/python /opt/litecrewai/masterplan/src/faza-0/validate_logging.py" || true

echo -e "${GREEN}Running monitoring validation...${NC}"
remote_exec "cd /opt/litecrewai && sudo -u litecrewai /opt/litecrewai/venv/bin/python /opt/litecrewai/masterplan/src/faza-0/validate_monitoring.py" || true

echo -e "${GREEN}=== Monitoring Deployment Complete! ===${NC}"
echo -e "${GREEN}Check status:${NC}"
echo "  - Logs: ssh -i ${SSH_KEY} ${REMOTE_USER}@${DROPLET_IP} 'ls -la /opt/litecrewai/logs/'"
echo "  - Metrics DB: ssh -i ${SSH_KEY} ${REMOTE_USER}@${DROPLET_IP} 'ls -la /opt/litecrewai/data/'"
echo "  - Dashboard: ssh -i ${SSH_KEY} ${REMOTE_USER}@${DROPLET_IP} '/opt/litecrewai/venv/bin/python /opt/litecrewai/scripts/log_dashboard.py'"
echo "  - Aggregation timer: ssh -i ${SSH_KEY} ${REMOTE_USER}@${DROPLET_IP} 'sudo systemctl status litecrewai-metrics-aggregation.timer'"