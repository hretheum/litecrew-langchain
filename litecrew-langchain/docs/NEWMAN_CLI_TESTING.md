# Newman CLI Testing for LiteCrew API

Newman is Postman's command-line collection runner that allows you to run and test Postman collections directly from the command line.

## Installation

```bash
# Install Newman globally
npm install -g newman

# Or use npx without installation
npx newman run tests/postman/litecrew-api-tests.json
```

## Quick Start

```bash
# Run tests against local API
./scripts/test-api.sh

# Run tests against production
./scripts/test-api.sh --prod

# Run with multiple iterations
./scripts/test-api.sh --iterations 5

# Run with delay between requests
./scripts/test-api.sh --delay 100
```

## Manual Newman Commands

### Basic Test Run
```bash
newman run tests/postman/litecrew-api-tests.json \
  --environment tests/postman/environment.json
```

### Run with Custom Variables
```bash
newman run tests/postman/litecrew-api-tests.json \
  --env-var "base_url=http://localhost:8000" \
  --env-var "api_key=test-key-123"
```

### Generate HTML Report
```bash
# Install HTML reporter
npm install -g newman-reporter-html

# Run with HTML report
newman run tests/postman/litecrew-api-tests.json \
  --reporters cli,html \
  --reporter-html-export test-report.html
```

### CI/CD Integration

#### GitLab CI
```yaml
test-api:
  stage: test
  image: node:18
  before_script:
    - npm install -g newman
  script:
    - newman run tests/postman/litecrew-api-tests.json \
        --env-var "base_url=$API_URL" \
        --env-var "api_key=$API_KEY" \
        --reporters cli,junit \
        --reporter-junit-export results.xml
  artifacts:
    reports:
      junit: results.xml
```

#### GitHub Actions
```yaml
- name: Install Newman
  run: npm install -g newman

- name: Run API Tests
  run: |
    newman run tests/postman/litecrew-api-tests.json \
      --env-var "base_url=${{ secrets.API_URL }}" \
      --env-var "api_key=${{ secrets.API_KEY }}"
```

## Test Structure

Our test collection includes:

1. **Security Tests**
   - Unauthorized request handling
   - Invalid API key rejection
   - Rate limiting verification

2. **Functional Tests**
   - Health check endpoint
   - CRUD operations on crews
   - Task execution

3. **Performance Tests**
   - Response time validation
   - Rate limit header verification

## Environment Variables

For production testing, set:
```bash
export LITECREW_PROD_API_KEY="your-production-api-key"
./scripts/test-api.sh --prod
```

## Debugging

### Verbose Output
```bash
newman run tests/postman/litecrew-api-tests.json --verbose
```

### Export Results
```bash
newman run tests/postman/litecrew-api-tests.json \
  --reporters json \
  --reporter-json-export results.json
```

### Ignore SSL Errors (Development Only)
```bash
newman run tests/postman/litecrew-api-tests.json --insecure
```

## Parallel Testing

For load testing with multiple parallel instances:
```bash
# Run 5 parallel instances
for i in {1..5}; do
  newman run tests/postman/litecrew-api-tests.json \
    --env-var "api_key=test-key-$i" &
done
wait
```

## Custom Test Scenarios

Create specific test files for different scenarios:

- `tests/postman/security-tests.json` - Only security tests
- `tests/postman/performance-tests.json` - Performance benchmarks
- `tests/postman/integration-tests.json` - Full integration tests

## Troubleshooting

1. **Newman not found**
   ```bash
   npm install -g newman
   ```

2. **Permission denied**
   ```bash
   chmod +x scripts/test-api.sh
   ```

3. **Connection refused**
   - Ensure API is running: `docker-compose up`
   - Check URL: `curl http://localhost:8000/api/v1/health`

4. **Authentication errors**
   - Verify API key in environment
   - Check header name is exactly `X-API-Key`