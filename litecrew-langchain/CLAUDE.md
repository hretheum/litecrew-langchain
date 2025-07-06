# LiteCrew-LangChain - Instrukcje dla Claude

## 🎯 O projekcie
Lightweight alternatywa dla CrewAI na bazie LangChain. 
- **Status**: ✅ Production ready and deployed
- **Performance**: <0.05s import, <30MB RAM, 100% API compatibility achieved
- **Deployment**: https://api.litecrew.app (HTTPS enabled)
- **Direct access**: http://152.42.139.18:8000

## 🔥 WAŻNE: Pipeline Testing
**ZAWSZE uruchom pełny pipeline lokalnie PRZED commit+push:**
```bash
./run_pipeline_locally.sh
```
Skrypt testuje dokładnie to samo co GitLab CI:
- Lint stage (black, ruff, mypy)  
- Security stage (bandit, safety, pip-audit)
- Test stage (pytest z coverage >70%)

❌ **NIE COMMITUJ** bez uruchomienia tego skryptu!

## 🎉 Current Status (2025-07-06)
**Production deployment COMPLETE with HTTPS!**
- ✅ **Application live**: https://api.litecrew.app
- ✅ **HTTPS enabled**: Cloudflare proxy + Origin Certificate
- ✅ **445 tests passing** (was 406 failing)
- ✅ **72.7% coverage** (>70% requirement met)
- ✅ **Security implemented** (auth, rate limiting, CORS, SSL/TLS)
- ✅ **CI/CD pipeline operational** (lint, security, tests, deploy)
- ✅ **Local testing tooling** ready (`./run_pipeline_locally.sh`)
- ✅ **API Keys configured**: Production keys active

## 🔑 Production API Keys
```
prod-44c8a3026e05e84f44cd1f4cdda7b6ecaba64ccfb2dedd508a80a20405a54509
prod-92b8fba576057868543d3eb7302e6087dc202ea643720f516406cb9e1122497c
```
Use in header: `X-API-Key: [key]`

## 📁 Struktura dokumentacji
```
CLAUDE.md (ten plik)         # Instrukcje i komendy
project-context.md           # CRITICAL - aktualny stan (zawsze aktualizuj!)
docs/
├── IMPLEMENTATION_ROADMAP.md    # 45-dniowy plan (9 faz)
├── PROJECT_WORKFLOW.md          # Jak pracować (container-first)
├── VIBE_CODING_GUIDE.md        # Praktyczne wskazówki
├── CREWAI_FEATURES_COMPARISON.md # Co implementujemy
├── HTTPS_SETUP.md              # HTTPS configuration guide
└── POSTMAN_SETUP.md            # API testing setup
```

## 🚀 Workflow

### Początek sesji:
1. Przeczytaj project-context.md
2. Sprawdź current sprint/block
3. Kontynuuj lub zapytaj o nowe zadanie

### Podczas pracy:
1. **Test first** - zawsze pisz failing test najpierw
2. **Container only** - wszystko w Dockerze
3. **Small commits** - często, z conventional commits
4. **Check metrics** - po każdej implementacji
5. **Update context** - przed końcem sesji

### Koniec sesji:
1. Zaktualizuj project-context.md
2. Sprawdź metryki wydajności
3. Commit (bez push)

## 📝 Custom Commands

### /sprint-start <phase> <block>
Rozpocznij pracę nad blokiem:
1. Wczytaj IMPLEMENTATION_ROADMAP.md
2. Znajdź wskazany blok zadań
3. Stwórz failing tests first
4. Zaktualizuj project-context.md z current sprint info
5. Rozpocznij implementację w kontenerach

### /task-check
Sprawdź czy aktualne zadanie spełnia kryteria:
1. Testy napisane first? ✓
2. Performance metrics met? ✓ 
3. Container works? ✓
4. Documentation updated? ✓
5. Project-context.md current? ✓

### /sprint-end
Zakończ blok zadań:
1. Run all tests in container
2. Check performance benchmarks
3. Update project-context.md with completed items
4. Update roadmap checkboxes
5. Commit changes (no push)
6. Show summary of completed work

### /status
Pokaż:
- Current phase & block
- Completed tasks
- In progress items
- Performance metrics
- Next steps

### /next
Przejdź do następnego zadania z current block

## 🐳 Container Commands
```bash
# Start environment
docker-compose up -d

# Run tests
docker-compose run test pytest -v

# Check benchmarks
docker-compose run test python benchmarks/check_metrics.py

# Format code
docker-compose run dev black src/ tests/
```

## 📊 Performance Achieved
- Import time: <0.05s (current: ~0.009s ✅)
- Memory: <30MB (current: ~17MB ✅) 
- Agent creation: <10ms (current: <5ms ✅)
- Task execution overhead: <5% (current: <3% ✅)
- Test coverage: >70% (current: 72.7% ✅)
- Production: ✅ Deployed and operational

## 🔒 Security Rules
1. NO hardcoded secrets
2. Use environment variables
3. Validate all inputs
4. No telemetry/tracking
5. Local data only
6. HTTPS only in production

## 🏗️ Architecture Principles
1. **Async first** - wszystko async/await
2. **Type hints** - 100% coverage
3. **Minimal dependencies** - tylko necessary
4. **LangChain based** - leverage existing functionality
5. **CrewAI compatible** - same API surface

## 💡 Quick Tips
- Zawsze pracuj w kontenerze
- Test lokalnie przed commitem
- Małe, focused MRs
- Performance > features
- Document as you go
- Use HTTPS in production

## 🔗 Important Links
- **Production**: https://api.litecrew.app
- **Repo**: https://gitlab.com/eof3/litecrewai
- **Roadmap**: docs/IMPLEMENTATION_ROADMAP.md
- **Current context**: project-context.md
- **Domain**: litecrew.app (Cloudflare managed)

---
*Remember: Always update project-context.md before ending session!*