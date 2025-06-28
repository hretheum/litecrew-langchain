#!/bin/bash
# validate_droplet_setup.sh
set -e

echo "🔍 Validating DigitalOcean Droplet Setup..."

# Test SSH access
ssh -o ConnectTimeout=5 litecrewai@$DROPLET_IP "echo '✅ SSH Access OK'" || exit 1

# Test firewall
ssh litecrewai@$DROPLET_IP "sudo ufw status" | grep -q "Status: active" || exit 1

# Test fail2ban
ssh litecrewai@$DROPLET_IP "sudo systemctl is-active fail2ban" || exit 1

# Test auto-updates
ssh litecrewai@$DROPLET_IP "cat /etc/apt/apt.conf.d/50unattended-upgrades" | grep -q "Unattended-Upgrade::Allowed-Origins" || exit 1

echo "✅ All droplet checks passed!"