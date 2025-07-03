# LiteCrew-LangChain - Instrukcje dla Claude

## 🎯 O projekcie
Budujemy lightweight alternatywę dla CrewAI na bazie LangChain. Cel: <0.05s import, <30MB RAM, 100% API compatibility.

## 📁 Struktura dokumentacji
```
CLAUDE.md (ten plik)         # Instrukcje i komendy
project-context.md           # CRITICAL - aktualny stan (zawsze aktualizuj!)
docs/
├── IMPLEMENTATION_ROADMAP.md    # 45-dniowy plan (9 faz)
├── PROJECT_WORKFLOW.md          # Jak pracować (container-first)
├── VIBE_CODING_GUIDE.md        # Praktyczne wskazówki
└── CREWAI_FEATURES_COMPARISON.md # Co implementujemy
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

## 📊 Performance Targets
- Import time: <0.05s (current: ~0.008s ✅)
- Memory: <30MB (current: ~17MB ✅)
- Agent creation: <10ms
- Task execution overhead: <5%
- Test coverage: >90%

## 🔒 Security Rules
1. NO hardcoded secrets
2. Use environment variables
3. Validate all inputs
4. No telemetry/tracking
5. Local data only

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

## 🔗 Important Links
- Repo: https://gitlab.com/eof3/litecrewai
- Roadmap: docs/IMPLEMENTATION_ROADMAP.md
- Current context: project-context.md

---
*Remember: Always update project-context.md before ending session!*