#!/bin/bash
# API Testing Script using Newman (Postman CLI)

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🧪 LiteCrew API Testing Script${NC}"
echo "================================"

# Check if newman is installed
if ! command -v newman &> /dev/null; then
    echo -e "${RED}❌ Newman is not installed!${NC}"
    echo "Install it with: npm install -g newman"
    exit 1
fi

# Default values
ENVIRONMENT="local"
COLLECTION="tests/postman/litecrew-api-tests.json"
ENV_FILE="tests/postman/environment.json"
ITERATIONS=1
DELAY=0

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --prod|--production)
            ENVIRONMENT="production"
            shift
            ;;
        --iterations|-n)
            ITERATIONS="$2"
            shift 2
            ;;
        --delay|-d)
            DELAY="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --prod, --production    Run tests against production"
            echo "  --iterations, -n NUM    Number of iterations (default: 1)"
            echo "  --delay, -d MS         Delay between requests in ms (default: 0)"
            echo "  --help, -h             Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Set environment variables based on target
if [ "$ENVIRONMENT" = "production" ]; then
    echo -e "${YELLOW}🌐 Testing against PRODUCTION${NC}"
    export BASE_URL="http://152.42.139.18"
    # Note: Set your production API key in the environment
    if [ -z "$LITECREW_PROD_API_KEY" ]; then
        echo -e "${RED}❌ LITECREW_PROD_API_KEY environment variable not set!${NC}"
        echo "Set it with: export LITECREW_PROD_API_KEY=your-prod-key"
        exit 1
    fi
    export API_KEY="$LITECREW_PROD_API_KEY"
else
    echo -e "${YELLOW}🏠 Testing against LOCAL${NC}"
    export BASE_URL="http://localhost:8000"
    export API_KEY="test-key-123"
    
    # Check if local server is running
    if ! curl -s "$BASE_URL/api/v1/health" > /dev/null; then
        echo -e "${RED}❌ Local server is not running!${NC}"
        echo "Start it with: docker-compose up"
        exit 1
    fi
fi

# Create temp environment file with actual values
TEMP_ENV=$(mktemp)
cat > "$TEMP_ENV" <<EOF
{
  "id": "litecrew-test-env-runtime",
  "name": "LiteCrew Runtime Environment",
  "values": [
    {
      "key": "base_url",
      "value": "$BASE_URL",
      "enabled": true
    },
    {
      "key": "api_key",
      "value": "$API_KEY",
      "enabled": true
    }
  ]
}
EOF

# Run tests
echo -e "\n${GREEN}🚀 Running API tests...${NC}"
echo "Collection: $COLLECTION"
echo "Environment: $ENVIRONMENT"
echo "Base URL: $BASE_URL"
echo "Iterations: $ITERATIONS"
echo "Delay: ${DELAY}ms"
echo ""

# Run newman with options
newman run "$COLLECTION" \
    --environment "$TEMP_ENV" \
    --iteration-count "$ITERATIONS" \
    --delay-request "$DELAY" \
    --reporters cli,json \
    --reporter-json-export "test-results-$(date +%Y%m%d-%H%M%S).json" \
    --color on \
    --verbose

# Capture exit code
TEST_RESULT=$?

# Cleanup
rm -f "$TEMP_ENV"

# Report results
echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed!${NC}"
fi

exit $TEST_RESULT