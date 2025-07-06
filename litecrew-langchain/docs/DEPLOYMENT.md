# LiteCrew Deployment Guide

## 🚀 Current Production Deployment

**URL**: https://api.litecrew.app  
**Server**: DigitalOcean Droplet (Ubuntu 24.04, 2GB RAM)  
**Container**: Docker running on port 8000  
**Reverse Proxy**: Nginx on port 443  
**SSL/TLS**: Cloudflare proxy with Origin Certificate  

## 📋 Prerequisites

- Domain name (we use litecrew.app)
- DigitalOcean account or similar VPS
- GitLab account for CI/CD
- Cloudflare account (free tier works)

## 🔧 Server Setup

### 1. Create DigitalOcean Droplet

```bash
# Specs used:
- Ubuntu 24.04 LTS
- 2GB RAM / 1 vCPU
- 50GB SSD
- Region: Choose closest to your users
```

### 2. Initial Server Configuration

```bash
# SSH to server
ssh root@your-server-ip

# Create user
adduser litecrewai
usermod -aG sudo litecrewai
usermod -aG docker litecrewai

# Setup SSH key for user
su - litecrewai
mkdir ~/.ssh
chmod 700 ~/.ssh
# Add your SSH public key to ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Test Docker
docker run hello-world
```

### 4. Configure Firewall

```bash
# Enable UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # API (optional, for direct access)
sudo ufw enable

# Add Cloudflare IPs (important!)
for ip in $(curl -s https://www.cloudflare.com/ips-v4); do
    sudo ufw allow from $ip to any port 8000 comment "Cloudflare"
done
```

## 🔐 HTTPS Setup with Cloudflare

### 1. Configure Domain

1. Add domain to Cloudflare
2. Create A record: `api` → `your-server-ip`
3. Enable proxy (orange cloud)

### 2. Generate Origin Certificate

1. In Cloudflare: SSL/TLS → Origin Server → Create Certificate
2. Save certificate and private key
3. Copy to server:

```bash
# On server
sudo mkdir -p /etc/ssl/cloudflare
sudo nano /etc/ssl/cloudflare/cert.pem  # Paste certificate
sudo nano /etc/ssl/cloudflare/key.pem   # Paste private key
sudo chmod 600 /etc/ssl/cloudflare/key.pem
```

### 3. Install and Configure Nginx

```bash
# Install Nginx
sudo apt update && sudo apt install -y nginx

# Create configuration
sudo nano /etc/nginx/sites-available/api-litecrew
```

Nginx configuration:
```nginx
server {
    listen 443 ssl;
    server_name api.litecrew.app;

    ssl_certificate /etc/ssl/cloudflare/cert.pem;
    ssl_certificate_key /etc/ssl/cloudflare/key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

server {
    listen 80;
    server_name api.litecrew.app;
    return 301 https://$server_name$request_uri;
}
```

Enable the site:
```bash
sudo ln -sf /etc/nginx/sites-available/api-litecrew /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
```

### 4. Set Cloudflare SSL Mode

In Cloudflare dashboard:
- SSL/TLS → Overview → Set to "Full (strict)"

## 🐳 Deploy Application

### 1. Using GitLab CI/CD (Recommended)

The project includes `.gitlab-ci.yml` for automated deployment:

```bash
# In GitLab:
1. Go to Settings → CI/CD → Variables
2. Add:
   - DOCKER_REGISTRY_USER (your GitLab username)
   - DOCKER_REGISTRY_PASS (GitLab access token)
   - DEPLOY_HOST (your server IP)
   - DEPLOY_USER (litecrewai)
   - DEPLOY_KEY (private SSH key for server)

# Trigger deployment:
1. Push to master branch
2. Go to CI/CD → Pipelines
3. Click "Run Pipeline" on deploy stage
```

### 2. Manual Deployment

```bash
# On server
# Pull latest image (if using registry)
docker login registry.gitlab.com
docker pull registry.gitlab.com/eof3/litecrewai/litecrewai:latest

# Or build locally
git clone https://gitlab.com/eof3/litecrewai.git
cd litecrewai/litecrew-langchain
docker build -t litecrew-api .

# Run container
docker run -d \
  --name litecrew_api \
  -p 8000:8000 \
  -e LITECREW_API_KEYS="your-api-key-1,your-api-key-2" \
  -e OPENAI_API_KEY="your-openai-key" \
  -e ENVIRONMENT="production" \
  --restart unless-stopped \
  litecrew-api:latest
```

## 🔑 API Key Configuration

Generate secure API keys:
```bash
# Generate random keys
openssl rand -hex 32
```

Set in environment:
```bash
LITECREW_API_KEYS="key1,key2,key3"
```

## 📊 Monitoring

### Check Application Status

```bash
# Check container
docker ps
docker logs litecrew_api

# Check API health
curl https://api.litecrew.app/api/v1/health

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### System Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop ncdu

# Check resources
htop
df -h
docker stats
```

## 🔄 Updates and Maintenance

### Update Application

```bash
# Pull new image
docker pull registry.gitlab.com/eof3/litecrewai/litecrewai:latest

# Stop old container
docker stop litecrew_api
docker rm litecrew_api

# Start new container
docker run -d --name litecrew_api ... (same as above)
```

### Backup

```bash
# Backup data (if using volumes)
docker run --rm -v litecrew_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/litecrew-backup-$(date +%Y%m%d).tar.gz /data
```

### SSL Certificate Renewal

Cloudflare Origin Certificates are valid for 15 years, but if using Let's Encrypt:
```bash
sudo certbot renew --dry-run
```

## 🚨 Troubleshooting

### Container Won't Start
```bash
docker logs litecrew_api
# Check for missing environment variables or port conflicts
```

### 502 Bad Gateway
```bash
# Check if container is running
docker ps

# Check if app is listening
sudo netstat -tlnp | grep 8000

# Restart container
docker restart litecrew_api
```

### Cloudflare Error 521
- Check UFW rules include Cloudflare IPs
- Verify Nginx is running
- Check SSL certificate paths
- Ensure port 443 is open

### Performance Issues
```bash
# Check memory
free -h

# Check disk
df -h

# Check Docker
docker system prune -a  # Clean up unused images
```

## 🔒 Security Best Practices

1. **Regular Updates**
   ```bash
   sudo apt update && sudo apt upgrade
   sudo reboot  # If kernel updated
   ```

2. **Fail2ban** (optional)
   ```bash
   sudo apt install fail2ban
   ```

3. **Backup Strategy**
   - Regular snapshots (DigitalOcean feature)
   - Database backups if using persistent storage
   - Configuration backups

4. **Monitoring**
   - Set up alerts in DigitalOcean
   - Use external monitoring (UptimeRobot, etc.)
   - Monitor logs for suspicious activity

## 📝 Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| LITECREW_API_KEYS | Comma-separated API keys | Yes |
| OPENAI_API_KEY | OpenAI API key | If using OpenAI |
| ANTHROPIC_API_KEY | Anthropic API key | If using Claude |
| GROQ_API_KEY | Groq API key | If using Groq |
| ENVIRONMENT | "development" or "production" | No |
| DEBUG | "true" or "false" | No |
| DATABASE_URL | PostgreSQL connection string | No |
| REDIS_URL | Redis connection string | No |

## 🎯 Production Checklist

- [ ] Domain configured in Cloudflare
- [ ] SSL certificate installed
- [ ] Nginx configured and running
- [ ] Firewall rules set (including Cloudflare IPs)
- [ ] Docker container running
- [ ] API keys configured
- [ ] Health check passing
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] Documentation updated

---

For support, check the [main documentation](https://api.litecrew.app/docs) or create an issue on [GitLab](https://gitlab.com/eof3/litecrewai/issues).