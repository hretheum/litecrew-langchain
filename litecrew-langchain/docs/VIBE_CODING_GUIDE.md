# Vibe Coding Guide - Praktyczna implementacja workflow w LiteCrew

## 🎯 Jak pracować z Claude w tym projekcie

### 1. Struktura pamięci projektu

#### 1.1 Hierarchia dokumentów
```
CLAUDE.md                    # Globalne instrukcje + komendy
├── project-context.md       # Aktualny stan projektu (CRITICAL!)
├── IMPLEMENTATION_ROADMAP.md # Co robić (fazy, bloki, zadania)
├── PROJECT_WORKFLOW.md      # Jak robić (procesy, narzędzia)
└── VIBE_CODING_GUIDE.md    # Ten dokument - praktyczne wskazówki
```

#### 1.2 Co gdzie trzymać

**project-context.md** - ZAWSZE AKTUALIZUJ:
```markdown
## Current Sprint
- Phase: 1 - Core Foundation
- Block: 1.2 - LiteAgent Implementation
- Day: 2/45
- Status: In Progress

## Completed Tasks
- [x] Project structure created
- [x] Poetry configured
- [ ] LiteAgent class - IN PROGRESS

## Current Metrics
- Import time: 0.008s ✅
- Memory usage: 15MB ✅
- Test coverage: 95% ✅

## Known Issues
- #123: Redis connection timeout in tests
- #124: Type hints missing in utils.py

## Next Up
- Complete LiteAgent.execute() method
- Add streaming support
- Write integration tests
```

### 2. Komendy dla Claude

Dodaj do CLAUDE.md:
```markdown
## /sprint-start <phase> <block>
Rozpocznij pracę nad blokiem:
1. Wczytaj IMPLEMENTATION_ROADMAP.md
2. Znajdź wskazany blok zadań
3. Stwórz draft MR w GitLab
4. Stwórz failing tests
5. Zaktualizuj project-context.md

## /task-check
Sprawdź czy aktualne zadanie spełnia kryteria:
1. Testy napisane first? ✓
2. Performance metrics met? ✓
3. Container works? ✓
4. Documentation updated? ✓

## /sprint-end
Zakończ blok zadań:
1. Run all tests
2. Check performance benchmarks
3. Update project-context.md
4. Create MR for review
5. Update roadmap checkboxes
```

### 3. Praktyczny workflow dla Claude

#### 3.1 Początek sesji
```python
# Claude automatycznie:
1. Read CLAUDE.md
2. Read project-context.md
3. Check git status
4. Read current block from IMPLEMENTATION_ROADMAP.md
5. Ask: "Continue with [current task] or start new?"
```

#### 3.2 Praca nad zadaniem

**ZAWSZE w tej kolejności:**

1. **Test First**
   ```bash
   # Create failing test
   touch tests/unit/test_current_feature.py
   # Write test that defines expected behavior
   # Commit: "test: add failing test for X feature"
   ```

2. **Check Container**
   ```bash
   # Ensure dev container is running
   docker-compose ps
   # Run test in container
   docker-compose run test pytest tests/unit/test_current_feature.py -v
   ```

3. **Implement**
   ```bash
   # Work on implementation
   # Keep running tests in container
   # Commit often: "feat: implement X part of Y"
   ```

4. **Benchmark**
   ```bash
   # After implementation
   docker-compose run test python benchmarks/check_metrics.py
   # Ensure no regression
   ```

5. **Update Docs**
   ```bash
   # Update project-context.md
   # Check off completed tasks in ROADMAP
   # Add any new findings
   ```

#### 3.3 Struktura commitów

```bash
# Conventional commits - Claude powinien używać:
feat: add LiteAgent execute method
fix: resolve memory leak in task context
test: add performance benchmarks for agent creation
docs: update API reference for LiteAgent
perf: optimize agent initialization (10ms -> 5ms)
refactor: extract common validation logic
chore: update dependencies
```

### 4. Integracja z GitLab

#### 4.1 Issue/MR References
W kodzie i commitach:
```python
# Implements #123 - Fast agent creation
class LiteAgent:
    """
    Lightweight agent implementation.
    
    Refs:
    - Issue #123: Performance requirements
    - MR !45: Initial implementation
    - Roadmap: Phase 1, Block 1.2
    """
```

#### 4.2 MR Description Template
```markdown
## What does this MR do?
Implements LiteAgent class with <10ms creation time

## Related issues
Closes #123, #124
Part of Phase 1, Block 1.2

## Performance impact
- Import time: no change
- Memory: +2MB
- Agent creation: 8ms (target: <10ms) ✅

## Tests
- [x] Unit tests added
- [x] Integration tests added
- [x] Performance benchmarks pass

## Checklist
- [x] Tested in container
- [x] Documentation updated
- [x] No hardcoded values
- [x] Type hints complete
```

### 5. Automatyzacja dla Claude

#### 5.1 Pre-work Script
Dodaj do projektu `scripts/claude-pre-work.sh`:
```bash
#!/bin/bash
# Run before starting work on new block

echo "🔍 Checking project state..."

# 1. Git status
echo "\n📊 Git Status:"
git status --short

# 2. Current metrics
echo "\n📈 Current Metrics:"
docker-compose run test python benchmarks/quick_check.py

# 3. Test status
echo "\n🧪 Test Status:"
docker-compose run test pytest --co -q | tail -n 5

# 4. Current block from context
echo "\n📋 Current Block:"
grep -A 5 "## Current Sprint" project-context.md

echo "\n✅ Ready to work!"
```

#### 5.2 Post-work Script
`scripts/claude-post-work.sh`:
```bash
#!/bin/bash
# Run after completing work session

echo "🔍 Validating work..."

# 1. Run all tests
docker-compose run test pytest

# 2. Check benchmarks
docker-compose run test python benchmarks/check_metrics.py

# 3. Update project-context
echo "\n📝 Remember to update:"
echo "- [ ] project-context.md"
echo "- [ ] ROADMAP checkboxes"
echo "- [ ] Any new issues found"

# 4. Git status
echo "\n📊 Git Status:"
git status

echo "\n💡 Next: commit, push, create/update MR"
```

### 6. Pamięć między sesjami

#### 6.1 Session Summary Template
Na koniec każdej sesji Claude powinien aktualizować `project-context.md`:

```markdown
## Last Session (2024-01-03)
### Completed
- Implemented LiteAgent.__init__ method
- Added role, goal, backstory properties
- Created basic test suite

### In Progress
- LiteAgent.execute() method - 70% done
- Need to add async support

### Discovered Issues
- LangChain 0.3.0 has breaking changes
- Need to pin to 0.2.x for now

### Next Session Should
1. Finish execute() method
2. Add streaming support
3. Run full benchmark suite
```

### 7. Debugging & Troubleshooting

#### 7.1 Common Issues Checklist
```markdown
## When things don't work:

1. **Container issues?**
   - docker-compose down && docker-compose up -d
   - Check logs: docker-compose logs

2. **Test failures?**
   - Run in container, not local
   - Check for missing env vars
   - Verify test fixtures

3. **Performance regression?**
   - git bisect to find problematic commit
   - Profile with benchmarks/profile_component.py
   - Check for blocking I/O

4. **Import errors?**
   - Verify PYTHONPATH in container
   - Check relative vs absolute imports
   - Ensure package installed with pip install -e .
```

### 8. Rekomendacje dla optymalnej współpracy

1. **Start każdej sesji:**
   ```
   User: "continue with litecrew development"
   Claude: [reads context] "I see we're on Phase 1, Block 1.2, 
           working on LiteAgent.execute(). Should I continue 
           with async support or start fresh task?"
   ```

2. **Częste checkpointy:**
   - Co 2-3 taski: update project-context.md
   - Co 5 commitów: push do GitLab
   - Co block: full test & benchmark run

3. **Jasna komunikacja:**
   ```
   User: "implement next task from roadmap"
   Claude: "Starting Block 1.3: LiteTask Implementation
           First, creating failing tests for task creation..."
   ```

4. **Performance first:**
   - Zawsze sprawdzaj metryki PO implementacji
   - Jeśli coś spowalnia - refactor IMMEDIATELY
   - Lepiej prostsza implementacja niż wolna

5. **Container discipline:**
   - NIGDY nie instaluj lokalnie
   - ZAWSZE testuj w kontenerze
   - Jeśli "works on my machine" - to nie działa

### 9. Emergency Procedures

Gdy Claude zgubi kontekst:
```bash
# Quick recovery
cat project-context.md | grep -A 10 "Current Sprint"
git log --oneline -10
docker-compose ps
```

Gdy pipeline failuje:
```bash
# Check GitLab CI logs
# Run locally exact same command as CI
docker-compose run test [failing command]
```

Gdy performance spada:
```bash
# Git bisect to find regression
git bisect start
git bisect bad HEAD
git bisect good [last-known-good-commit]
# Run benchmark at each step
```

---

## 🚀 TL;DR - Quick Reference

1. **Read**: project-context.md → current block from ROADMAP
2. **Test**: Write failing test first
3. **Container**: All work in Docker
4. **Implement**: Small commits, often
5. **Benchmark**: After each feature
6. **Update**: project-context.md before ending session
7. **Repeat**: Until block complete

Remember: Performance > Features. Better to have 5 fast features than 10 slow ones.