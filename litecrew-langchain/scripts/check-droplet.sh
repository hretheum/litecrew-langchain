#!/bin/bash
# Script to check droplet status

DROPLET_IP="152.42.139.18"
SSH_KEY="~/.ssh/id_rag"
USER="litecrewai"

echo "🔍 Checking LiteCrew Droplet Status..."
echo "=================================="

# Check connection
echo "📡 Testing SSH connection..."
if ssh -i $SSH_KEY -o ConnectTimeout=5 $USER@$DROPLET_IP "echo 'Connected successfully'" > /dev/null 2>&1; then
    echo "✅ SSH connection successful"
else
    echo "❌ SSH connection failed"
    exit 1
fi

# Check system info
echo ""
echo "💻 System Information:"
ssh -i $SSH_KEY $USER@$DROPLET_IP "uname -a"
ssh -i $SSH_KEY $USER@$DROPLET_IP "free -h | grep Mem"
ssh -i $SSH_KEY $USER@$DROPLET_IP "df -h | grep /dev/root"

# Check Docker
echo ""
echo "🐳 Docker Status:"
ssh -i $SSH_KEY $USER@$DROPLET_IP "docker --version"
ssh -i $SSH_KEY $USER@$DROPLET_IP "docker-compose --version"
ssh -i $SSH_KEY $USER@$DROPLET_IP "docker ps -a"

# Check ports
echo ""
echo "🔌 Open Ports:"
ssh -i $SSH_KEY $USER@$DROPLET_IP "sudo netstat -tlnp | grep LISTEN | grep -E ':(22|80|443|8000)'"

# Check firewall
echo ""
echo "🔥 Firewall Status:"
ssh -i $SSH_KEY $USER@$DROPLET_IP "sudo ufw status numbered"

echo ""
echo "✅ Droplet check completed!"