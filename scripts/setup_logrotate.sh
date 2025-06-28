#!/bin/bash
# Setup logrotate configuration for LiteCrewAI logs

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Setting up logrotate for LiteCrewAI...${NC}"

# Create logrotate configuration
cat > /tmp/litecrewai_logrotate << 'EOF'
/opt/litecrewai/logs/*.log {
    daily
    rotate 30
    maxsize 100M
    compress
    delaycompress
    missingok
    notifempty
    create 0644 litecrewai litecrewai
    sharedscripts
    postrotate
        # Send SIGUSR1 to the application to reopen log files
        if [ -f /var/run/litecrewai.pid ]; then
            kill -USR1 $(cat /var/run/litecrewai.pid) 2>/dev/null || true
        fi
        
        # Restart any Python processes that might have the logs open
        pkill -USR1 -f "python.*litecrewai" || true
    endscript
}

# Special handling for error logs - keep longer
/opt/litecrewai/logs/error.log {
    daily
    rotate 90
    maxsize 100M
    compress
    delaycompress
    missingok
    notifempty
    create 0644 litecrewai litecrewai
    sharedscripts
    postrotate
        # Alert on critical errors
        if [ -s /opt/litecrewai/logs/error.log ]; then
            /opt/litecrewai/scripts/check_critical_errors.py || true
        fi
    endscript
}
EOF

# Install logrotate configuration
if [ -f /etc/logrotate.d/litecrewai ]; then
    echo -e "${YELLOW}Backing up existing logrotate config...${NC}"
    sudo cp /etc/logrotate.d/litecrewai /etc/logrotate.d/litecrewai.bak
fi

sudo mv /tmp/litecrewai_logrotate /etc/logrotate.d/litecrewai
sudo chmod 644 /etc/logrotate.d/litecrewai

echo -e "${GREEN}Testing logrotate configuration...${NC}"
sudo logrotate -d /etc/logrotate.d/litecrewai

echo -e "${GREEN}Logrotate setup complete!${NC}"
echo -e "${GREEN}Logs will be rotated daily, compressed after 1 day, and kept for 30 days.${NC}"