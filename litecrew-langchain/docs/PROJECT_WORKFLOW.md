# LiteCrew Project Workflow - Container-First Development

## 🎯 Filozofia pracy

Jako zespół pracujemy w filozofii:
- **Container-first**: Wszystko działa w kontenerach od dnia 1
- **GitLab-native**: Maksymalne wykorzystanie funkcjonalności GitLab
- **Test-driven**: Testy przed implementacją
- **Milestone-driven**: Każda faza = milestone z concrete delivery
- **Automated everything**: CI/CD od początku

---

## 📋 1. Struktura GitLab

### 1.1 Milestones (1 per fazę)
```
Milestone: "Phase 1 - Core Foundation" (5 dni)
├── Due date: 2025-01-08
├── Description: LiteAgent + LiteTask implementation
└── Deliverables: Working agents with <10ms creation time

Milestone: "Phase 2 - Core Engine" (5 dni)
├── Due date: 2025-01-15
├── Description: LiteCrew orchestration
└── Deliverables: Full orchestration with <50MB memory
```

### 1.2 Labels System
```yaml
# Priority labels
- P0-Critical (blocker)
- P1-High (this sprint)
- P2-Medium (next sprint)
- P3-Low (backlog)

# Type labels
- type::feature
- type::bug
- type::test
- type::docs
- type::performance

# Component labels
- component::agent
- component::task
- component::crew
- component::api
- component::memory

# Status labels
- status::ready
- status::in-progress
- status::review
- status::blocked
```

### 1.3 Issue Templates

**Feature Issue Template:**
```markdown
## Feature: [Component] Brief description

### Acceptance Criteria
- [ ] Metric 1: Import time <10ms
- [ ] Metric 2: Memory usage <5MB
- [ ] Test coverage >90%
- [ ] Documentation updated

### Technical Details
- Affects: src/litecrew/[component].py
- Dependencies: #123, #124
- Roadmap ref: Phase X, Block X.X

### Test Scenarios
1. Unit: test_[component]_performance()
2. Integration: test_[component]_with_[other]()
3. E2E: test_full_flow_with_[component]()

### Definition of Done
- [ ] Code implemented
- [ ] Tests passing (unit/integration/e2e)
- [ ] Performance benchmarks met
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Deployed to staging
```

---

## 🐳 2. Container-First Development

### 2.1 Development Containers

**/.devcontainer/devcontainer.json:**
```json
{
  "name": "LiteCrew Dev",
  "dockerComposeFile": "docker-compose.yml",
  "service": "dev",
  "workspaceFolder": "/workspace",
  "features": {
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.12"
    }
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff",
        "ms-python.black-formatter"
      ]
    }
  },
  "postCreateCommand": "pip install -e '.[dev]'",
  "forwardPorts": [8000, 6379, 5432]
}
```

**/.devcontainer/docker-compose.yml:**
```yaml
version: '3.8'

services:
  dev:
    build:
      context: ..
      dockerfile: .devcontainer/Dockerfile
    volumes:
      - ..:/workspace:cached
      - ~/.ssh:/home/vscode/.ssh:ro
    environment:
      - ENVIRONMENT=development
    command: sleep infinity

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: litecrewai_dev
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  test-llm:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  postgres_data:
  ollama_data:
```

### 2.2 Multi-Stage Production Dockerfile

**/Dockerfile:**
```dockerfile
# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /build
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* ./
RUN pip install --upgrade pip poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

# Stage 2: Test Runner
FROM builder as test

COPY . .
RUN poetry install --no-interaction --no-ansi --with dev \
    && python -m pytest tests/ --cov=litecrew --cov-report=xml \
    && python -m mypy src/litecrew \
    && python -m ruff check src/

# Stage 3: Production
FROM python:3.12-slim as production

RUN useradd -m -u 1000 litecrew
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --chown=litecrew:litecrew src/ ./src/

USER litecrew
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["uvicorn", "litecrew.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🚀 3. GitLab CI/CD Pipeline

**/.gitlab-ci.yml:**
```yaml
stages:
  - build
  - test
  - benchmark
  - deploy
  - release

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""
  IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  LATEST_TAG: $CI_REGISTRY_IMAGE:latest

# Build stage
build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build --target test -t $IMAGE_TAG-test .
    - docker build --target production -t $IMAGE_TAG .
    - docker push $IMAGE_TAG-test
    - docker push $IMAGE_TAG
  rules:
    - if: $CI_MERGE_REQUEST_ID
    - if: $CI_COMMIT_BRANCH == "master"

# Test jobs
test:unit:
  stage: test
  image: $IMAGE_TAG-test
  script:
    - pytest tests/unit -v --cov=litecrew --cov-report=term --cov-report=xml
    - coverage xml
  coverage: '/TOTAL.+?(\d+\%)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  rules:
    - if: $CI_MERGE_REQUEST_ID
    - if: $CI_COMMIT_BRANCH == "master"

test:integration:
  stage: test
  image: $IMAGE_TAG-test
  services:
    - redis:7-alpine
    - postgres:15-alpine
  variables:
    REDIS_URL: redis://redis:6379
    DATABASE_URL: postgresql://test:test@postgres/test
  script:
    - pytest tests/integration -v
  rules:
    - if: $CI_MERGE_REQUEST_ID
    - if: $CI_COMMIT_BRANCH == "master"

test:e2e:
  stage: test
  image: $IMAGE_TAG-test
  services:
    - redis:7-alpine
    - postgres:15-alpine
    - ollama/ollama:latest
  script:
    - pytest tests/e2e -v --timeout=300
  rules:
    - if: $CI_MERGE_REQUEST_ID
    - if: $CI_COMMIT_BRANCH == "master"

# Benchmark stage
benchmark:performance:
  stage: benchmark
  image: $IMAGE_TAG-test
  script:
    - python -m pytest benchmarks/ -v --benchmark-only
    - python benchmarks/compare_with_baseline.py
  artifacts:
    reports:
      performance: benchmark-results.json
    paths:
      - benchmark-results/
  rules:
    - if: $CI_MERGE_REQUEST_ID
    - if: $CI_COMMIT_BRANCH == "master"

benchmark:memory:
  stage: benchmark
  image: $IMAGE_TAG-test
  script:
    - python benchmarks/memory_profiler.py
    - python benchmarks/check_memory_limits.py
  artifacts:
    paths:
      - memory-profile/
  rules:
    - if: $CI_MERGE_REQUEST_ID
      when: manual
    - if: $CI_COMMIT_BRANCH == "master"

# Deploy stages
deploy:staging:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache curl
    - |
      curl -X POST https://staging.litecrewai.com/api/deploy \
        -H "Authorization: Bearer $STAGING_DEPLOY_TOKEN" \
        -d "image=$IMAGE_TAG"
  environment:
    name: staging
    url: https://staging.litecrewai.com
  rules:
    - if: $CI_COMMIT_BRANCH == "master"

deploy:production:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache curl
    - |
      curl -X POST https://api.litecrewai.com/api/deploy \
        -H "Authorization: Bearer $PROD_DEPLOY_TOKEN" \
        -d "image=$IMAGE_TAG"
  environment:
    name: production
    url: https://api.litecrewai.com
  rules:
    - if: $CI_COMMIT_TAG
  when: manual

# Release stage
release:
  stage: release
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker pull $IMAGE_TAG
    - docker tag $IMAGE_TAG $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
    - docker tag $IMAGE_TAG $LATEST_TAG
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
    - docker push $LATEST_TAG
  rules:
    - if: $CI_COMMIT_TAG
```

---

## 🧪 4. Test Strategy

### 4.1 Test Structure
```
tests/
├── unit/              # Fast, isolated tests
│   ├── test_agent.py
│   ├── test_task.py
│   └── test_crew.py
├── integration/       # Component integration
│   ├── test_agent_task_integration.py
│   └── test_crew_orchestration.py
├── e2e/              # Full flows
│   ├── test_simple_crew_flow.py
│   └── test_complex_delegation.py
├── benchmarks/       # Performance tests
│   ├── test_import_time.py
│   ├── test_memory_usage.py
│   └── test_latency.py
└── fixtures/         # Shared test data
```

### 4.2 Test-First Workflow

**Dla każdego issue:**
1. **Write failing test first**
   ```python
   # tests/unit/test_agent.py
   def test_agent_creation_performance():
       start = time.perf_counter()
       agent = LiteAgent(role="Test", goal="Test", backstory="Test")
       duration = time.perf_counter() - start
       assert duration < 0.01  # This will fail initially
   ```

2. **Create MR with WIP: prefix**
   ```bash
   git checkout -b feature/123-fast-agent-creation
   git add tests/
   git commit -m "test: Add performance test for agent creation"
   git push -u origin feature/123-fast-agent-creation
   # Create MR via GitLab UI or CLI
   ```

3. **Implement until test passes**
4. **Remove WIP: when ready for review**

---

## 🔄 5. Daily Workflow

### 5.1 Sprint Planning (co 5 dni = 1 faza)
```markdown
## Sprint X Planning (Phase X)

### Goals
- Complete all Phase X blocks
- Achieve all performance metrics
- 100% test coverage for new code

### Issue Assignment
- Developer A: Block X.1 (#101, #102, #103)
- Developer B: Block X.2 (#104, #105)
- Developer C: Block X.3 (#106, #107, #108)

### Daily Standup Topics
- Blockers?
- Performance metrics status?
- Test coverage?
- Need pair programming?
```

### 5.2 Daily Development Flow

**Morning:**
1. Pull latest master
2. Check CI/CD dashboard
3. Review assigned issues
4. Start with failing test

**Development:**
1. Work in feature branch
2. Commit often with conventional commits
3. Push for CI feedback
4. Create draft MR early

**End of day:**
1. Push all WIP
2. Update issue status
3. Check benchmark results
4. Plan tomorrow

### 5.3 Code Review Process

**MR Checklist:**
```markdown
## Code Review Checklist

### Automated Checks ✅
- [ ] All CI/CD pipelines pass
- [ ] Test coverage >90%
- [ ] Performance benchmarks pass
- [ ] No security vulnerabilities

### Manual Review
- [ ] Code follows project conventions
- [ ] Tests are meaningful (not just coverage)
- [ ] Documentation updated
- [ ] No hardcoded values
- [ ] Error handling appropriate

### Performance
- [ ] Import time impact checked
- [ ] Memory usage profiled
- [ ] No blocking operations
- [ ] Async where appropriate
```

---

## 📊 6. Monitoring & Metrics

### 6.1 GitLab Dashboards

**Performance Dashboard:**
- Import time trend (target: <0.05s)
- Memory usage trend (target: <30MB)
- Test execution time
- Code coverage trend

**Project Health:**
- Open issues by priority
- MR cycle time
- Pipeline success rate
- Deployment frequency

### 6.2 Automated Alerts

**Slack/Discord Integration:**
```yaml
# .gitlab-ci.yml addition
notify:failed:
  stage: .post
  image: appropriate/curl
  script:
    - |
      curl -X POST $DISCORD_WEBHOOK \
        -H "Content-Type: application/json" \
        -d "{\"content\": \"❌ Pipeline failed: $CI_PIPELINE_URL\"}"
  when: on_failure

notify:performance_regression:
  stage: .post
  image: appropriate/curl
  script:
    - |
      if [ -f "benchmark-regression.txt" ]; then
        curl -X POST $DISCORD_WEBHOOK \
          -H "Content-Type: application/json" \
          -d "{\"content\": \"⚠️ Performance regression detected!\"}"
      fi
  when: on_success
```

---

## 🚢 7. Release Process

### 7.1 Release Checklist
```markdown
## Release X.Y.Z Checklist

### Pre-release
- [ ] All Phase X issues closed
- [ ] All tests passing
- [ ] Performance metrics met
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

### Release
- [ ] Create release MR to master
- [ ] Tag release (triggers deploy)
- [ ] Monitor production metrics
- [ ] Announce in Discord/Slack

### Post-release
- [ ] Close milestone
- [ ] Create next milestone
- [ ] Retrospective meeting
- [ ] Update roadmap if needed
```

### 7.2 Versioning Strategy
- **Major (X.0.0)**: Breaking API changes
- **Minor (0.X.0)**: New features (end of each phase)
- **Patch (0.0.X)**: Bug fixes

---

## 🎯 8. Success Metrics

### 8.1 Per-Sprint Metrics
- Issues completed vs planned
- Test coverage maintained >90%
- Performance benchmarks green
- Zero P0/P1 bugs in production

### 8.2 Per-Phase Metrics
- All blocks completed
- All success criteria met
- Documentation complete
- Stakeholder demo successful

### 8.3 Project-wide Metrics
- Time to market: 45 days ✓
- Performance: 10x better than CrewAI ✓
- Adoption: X users in first month
- Stability: <0.1% error rate

---

## 💡 Pro Tips

1. **Always work in containers** - "Works on my machine" is not acceptable
2. **Test locally before push** - Use `docker-compose run test pytest`
3. **Small, focused MRs** - Easier to review, faster to merge
4. **Benchmark everything** - Performance is a feature
5. **Document as you go** - Not after
6. **Pair program on complex tasks** - Two heads better than one
7. **Celebrate milestones** - 45 days is a marathon, not a sprint

---

## 🔧 Quick Commands

```bash
# Start dev environment
docker-compose up -d

# Run tests locally
docker-compose run test pytest -v

# Run specific benchmark
docker-compose run test python -m pytest benchmarks/test_import_time.py

# Check coverage
docker-compose run test pytest --cov=litecrew --cov-report=html

# Format code
docker-compose run dev black src/ tests/
docker-compose run dev ruff check --fix src/ tests/

# Build production image
docker build --target production -t litecrew:local .

# Run production locally
docker run -p 8000:8000 litecrew:local
```