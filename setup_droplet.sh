#!/bin/bash
# setup_droplet.sh - Konfiguracja DigitalOcean Droplet dla LiteCrewAI
set -euo pipefail

# Kolory dla outputu
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== LiteCrewAI Droplet Setup ===${NC}"
echo "Starting at: $(date)"

# Funkcja do logowania
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

# 1. Aktualizacja systemu
log "Updating system packages..."
apt update && apt upgrade -y

# 2. Tworzenie użytkownika litecrewai
if ! id "litecrewai" &>/dev/null; then
    log "Creating user litecrewai..."
    useradd -m -s /bin/bash litecrewai
    
    # Kopiowanie SSH keys z root
    mkdir -p /home/litecrewai/.ssh
    cp /root/.ssh/authorized_keys /home/litecrewai/.ssh/
    chown -R litecrewai:litecrewai /home/litecrewai/.ssh
    chmod 700 /home/litecrewai/.ssh
    chmod 600 /home/litecrewai/.ssh/authorized_keys
    
    log "User litecrewai created"
else
    log "User litecrewai already exists"
fi

# 3. Konfiguracja sudo bez hasła
log "Configuring passwordless sudo for litecrewai..."
echo "litecrewai ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/litecrewai
chmod 440 /etc/sudoers.d/litecrewai

# 4. Konfiguracja SSH
log "Configuring SSH security..."
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Disable root login i password authentication
sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config

# Restart SSH
systemctl restart sshd

# 5. Konfiguracja firewall (UFW)
log "Setting up firewall..."
apt install -y ufw

# Reset firewall rules
ufw --force reset

# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH, HTTP, HTTPS
ufw allow 22/tcp comment "SSH"
ufw allow 80/tcp comment "HTTP"
ufw allow 443/tcp comment "HTTPS"

# Enable firewall
echo "y" | ufw enable

log "Firewall status:"
ufw status verbose

# 6. Instalacja i konfiguracja fail2ban
log "Installing fail2ban..."
apt install -y fail2ban

# Konfiguracja fail2ban dla SSH
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# 7. Konfiguracja automatycznych aktualizacji
log "Setting up automatic security updates..."
apt install -y unattended-upgrades apt-listchanges

# Konfiguracja unattended-upgrades
cat > /etc/apt/apt.conf.d/50unattended-upgrades <<'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Automatic-Reboot-Time "03:00";
EOF

# Włączenie automatycznych aktualizacji
cat > /etc/apt/apt.conf.d/20auto-upgrades <<EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
EOF

# 8. Podstawowe narzędzia
log "Installing basic tools..."
apt install -y \
    curl \
    wget \
    vim \
    htop \
    tmux \
    git \
    net-tools \
    software-properties-common

# 9. Tworzenie pliku MOTD
cat > /etc/motd <<'EOF'

╦  ╦╔╦╗╔═╗╔═╗╦═╗╔═╗╦ ╦╔═╗╦
║  ║ ║ ║╣ ║  ╠╦╝║╣ ║║║╠═╣║
╩═╝╩ ╩ ╚═╝╚═╝╩╚═╚═╝╚╩╝╩ ╩╩

Welcome to LiteCrewAI Server!
Remember: Always use 'litecrewai' user for operations.

EOF

# 10. Podsumowanie
log "${GREEN}=== Setup Complete ===${NC}"
log "Security configurations:"
log "✓ User 'litecrewai' created with passwordless sudo"
log "✓ SSH hardened (no root login, no password auth)"
log "✓ Firewall enabled (ports: 22, 80, 443)"
log "✓ Fail2ban protecting SSH"
log "✓ Automatic security updates enabled"

echo -e "${YELLOW}IMPORTANT:${NC} You must now:"
echo "1. Exit and reconnect as 'litecrewai' user:"
echo "   ssh -i ~/.ssh/id_rag litecrewai@46.101.181.183"
echo "2. Test sudo access: sudo whoami"
echo ""
echo -e "${RED}WARNING:${NC} Root SSH access is now disabled!"