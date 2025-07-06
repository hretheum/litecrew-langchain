# LiteCrew Deployment Guide

## 🏗️ Architecture Overview

Cała aplikacja działa w kontenerach Docker:
- **LiteCrew API**: FastAPI application
- **Redis**: Cache and session storage
- **PostgreSQL**: Persistent data storage
- **Nginx**: Reverse proxy with SSL termination

## 🚀 Deployment Flow

### 1. Automatic Deployment (Recommended)

```mermaid
graph LR
    A[Push to main] --> B[GitLab CI/CD]
    B --> C[Run Tests]
    C --> D[Build Docker Image]
    D --> E[Push to Registry]
    E --> F[Deploy to Droplet]
    F --> G[Update Containers]
```

**Steps:**
1. Push code to `main` branch
2. GitLab CI/CD automatically:
   - Runs tests
   - Builds Docker image
   - Pushes to GitLab Container Registry
3. Manual trigger deployment job
4. CI/CD SSHs to Droplet and updates containers

### 2. GitLab CI/CD Configuration

Pipeline stages:
- **test**: Run pytest in Docker
- **build**: Build and push Docker image
- **deploy**: SSH to Droplet and update containers

Required CI/CD Variables:
```bash
# GitLab Settings > CI/CD > Variables
CI_REGISTRY_USER        # GitLab username
CI_REGISTRY_PASSWORD    # GitLab token
SSH_PRIVATE_KEY        # SSH key for Droplet access
DROPLET_IP            # 152.42.139.18
OPENAI_API_KEY        # Your OpenAI key
ANTHROPIC_API_KEY     # Your Anthropic key (optional)
GROQ_API_KEY         # Your Groq key (optional)
SECRET_KEY           # Random secret for sessions
JWT_SECRET           # Random secret for JWT
DB_PASSWORD          # PostgreSQL password
```

### 3. First-time Setup on Droplet

```bash
# SSH to Droplet
ssh -p 2222 litecrewai@152.42.139.18

# Create deployment directory
sudo mkdir -p /opt/litecrewai/litecrew-langchain
sudo chown -R litecrewai:litecrewai /opt/litecrewai

# Install Docker if not already installed
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker litecrewai

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Setup SSL with Certbot (one-time)
sudo snap install --classic certbot
sudo certbot certonly --standalone -d your-domain.com
```

### 4. Manual Emergency Deployment

Only use when CI/CD is unavailable:

```bash
# On local machine
./scripts/deploy.sh

# This will:
# 1. Check you're on main branch
# 2. Run tests
# 3. Build image locally
# 4. Show manual deployment instructions
```

## 🔒 Security Considerations

1. **No source code on production server**
   - Only Docker images are deployed
   - Source code stays in GitLab

2. **Secrets management**
   - All secrets in GitLab CI/CD variables
   - Never commit secrets to repository
   - Use `.env.example` as template

3. **Network security**
   - All services communicate via Docker network
   - Only Nginx exposed to internet (ports 80, 443)
   - PostgreSQL and Redis not exposed externally

4. **SSL/TLS**
   - Nginx handles SSL termination
   - Auto-redirect HTTP to HTTPS
   - Let's Encrypt certificates

## 📊 Monitoring

### Check deployment status:
```bash
# SSH to Droplet
ssh -p 2222 litecrewai@152.42.139.18

# Check containers
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f litecrew

# Health check
curl http://localhost/health
```

### Endpoints:
- Health: https://your-domain.com/health
- API Docs: https://your-domain.com/docs
- Dashboard: https://your-domain.com/

## 🔧 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs litecrew

# Common issues:
# - Missing environment variables
# - Port already in use
# - Database connection failed
```

### Database issues
```bash
# Connect to PostgreSQL
docker exec -it litecrew_postgres psql -U litecrew

# Check Redis
docker exec -it litecrew_redis redis-cli ping
```

### Rollback deployment
```bash
# List available images
docker images | grep litecrewai

# Update docker-compose.prod.yml with previous image tag
# Then restart
docker-compose -f docker-compose.prod.yml up -d
```

## 🔄 Backup Strategy

### Automated backups:
```yaml
# Add to docker-compose.prod.yml
backup:
  image: postgres:15-alpine
  volumes:
    - ./backups:/backups
    - postgres_data:/data
  command: |
    sh -c 'pg_dump -h postgres -U litecrew litecrew | gzip > /backups/backup_$$(date +%Y%m%d_%H%M%S).sql.gz'
  depends_on:
    - postgres
```

### Manual backup:
```bash
# Backup database
docker exec litecrew_postgres pg_dump -U litecrew litecrew | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup Redis
docker exec litecrew_redis redis-cli SAVE
docker cp litecrew_redis:/data/dump.rdb ./redis_backup_$(date +%Y%m%d).rdb
```

## 📝 Maintenance

### Update dependencies:
1. Update requirements.txt locally
2. Test thoroughly
3. Push to main
4. CI/CD will rebuild and deploy

### Scale horizontally:
```yaml
# In docker-compose.prod.yml
litecrew:
  scale: 3  # Run 3 instances
```

### Monitor resources:
```bash
# Check container stats
docker stats

# Check disk usage
df -h

# Clean up old images
docker image prune -a -f
```