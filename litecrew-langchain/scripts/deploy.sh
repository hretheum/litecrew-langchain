#!/bin/bash
# LiteCrew Deployment Script

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_USER="litecrewai"
DEPLOY_HOST="46.101.181.183"
DEPLOY_PORT="2222"
DEPLOY_PATH="/opt/litecrewai/litecrew-langchain"
REPO_URL="https://gitlab.com/eof3/litecrewai.git"

echo -e "${GREEN}🚀 LiteCrew Deployment Script${NC}"
echo "================================"

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo -e "${RED}❌ Error: .env.production not found!${NC}"
    echo "Please create .env.production with production configuration"
    exit 1
fi

# Step 1: Build and test locally
echo -e "\n${YELLOW}📦 Building Docker image locally...${NC}"
docker build -t litecrew:test .

echo -e "\n${YELLOW}🧪 Running tests in container...${NC}"
docker run --rm litecrew:test python -m pytest tests/ -v

# Step 2: Push to GitLab
echo -e "\n${YELLOW}📤 Pushing to GitLab...${NC}"
git add -A
git commit -m "Deploy: $(date +%Y-%m-%d_%H-%M-%S)" || true
git push origin main

# Step 3: Deploy to Droplet
echo -e "\n${YELLOW}🌐 Deploying to Droplet...${NC}"

# Copy deployment script to server
cat << 'REMOTE_SCRIPT' | ssh -p $DEPLOY_PORT $DEPLOY_USER@$DEPLOY_HOST bash -s
set -e

# Navigate to deployment directory
cd /opt/litecrewai

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Navigate to litecrew-langchain
cd litecrew-langchain

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build new image
echo "🔨 Building new image..."
docker-compose build --no-cache

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for health check
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "✅ Deployment successful! Services are healthy."
else
    echo "❌ Health check failed! Rolling back..."
    docker-compose down
    docker-compose up -d --scale litecrew=0
    exit 1
fi

# Show logs
echo "📋 Recent logs:"
docker-compose logs --tail=50 litecrew

# Show status
echo "📊 Container status:"
docker-compose ps
REMOTE_SCRIPT

# Step 4: Copy production env file
echo -e "\n${YELLOW}📝 Copying production environment...${NC}"
scp -P $DEPLOY_PORT .env.production $DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH/.env

# Step 5: Final health check
echo -e "\n${YELLOW}🏥 Final health check...${NC}"
if ssh -p $DEPLOY_PORT $DEPLOY_USER@$DEPLOY_HOST "curl -f http://localhost:8000/api/v1/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
    echo -e "🌐 API: http://$DEPLOY_HOST:8000"
    echo -e "📚 Docs: http://$DEPLOY_HOST:8000/docs"
    echo -e "📊 Dashboard: http://$DEPLOY_HOST:8000/dashboard"
else
    echo -e "${RED}❌ Deployment failed! Check server logs.${NC}"
    exit 1
fi