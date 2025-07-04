#!/bin/bash
# Manual deployment helper script
# Note: Production deployment should use GitLab CI/CD!

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 LiteCrew Manual Deployment Helper${NC}"
echo "====================================="
echo -e "${YELLOW}⚠️  Note: This is for emergency manual deployment only!${NC}"
echo -e "${YELLOW}⚠️  Normal deployment should use GitLab CI/CD pipeline${NC}"
echo ""

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${RED}❌ Error: Not on main branch!${NC}"
    echo "Current branch: $CURRENT_BRANCH"
    echo "Switch to main branch first: git checkout main"
    exit 1
fi

# Run tests locally
echo -e "\n${YELLOW}🧪 Running tests...${NC}"
docker build -t litecrew:test .
docker run --rm litecrew:test python -m pytest tests/ -v || {
    echo -e "${RED}❌ Tests failed! Fix before deploying.${NC}"
    exit 1
}

# Build and tag image
echo -e "\n${YELLOW}📦 Building production image...${NC}"
IMAGE_TAG="registry.gitlab.com/eof3/litecrewai:$(git rev-parse --short HEAD)"
docker build -t $IMAGE_TAG .

echo -e "\n${GREEN}✅ Build successful!${NC}"
echo "Image tagged as: $IMAGE_TAG"
echo ""
echo "To deploy:"
echo "1. Push to GitLab: git push origin main"
echo "2. Go to GitLab CI/CD pipelines"
echo "3. Manually trigger the deploy job"
echo ""
echo "For emergency manual deployment:"
echo "1. docker save $IMAGE_TAG | ssh -p 2222 litecrewai@46.101.181.183 'docker load'"
echo "2. SSH to server and update docker-compose.prod.yml with new image tag"
echo "3. docker-compose -f docker-compose.prod.yml up -d"