# LiteCrew - Custom Commands dla Claude

## 🎯 O projekcie LiteCrew
Budujemy lightweight alternatywę dla CrewAI na bazie LangChain. 
- Cel: <0.05s import, <30MB RAM, 100% API compatibility
- Osiągnięto: 9ms import (363x szybszy niż CrewAI), ~17MB RAM
- Status: Phase 2 completed ✅, ready for Phase 3

## 📝 Custom Commands dla LiteCrew-LangChain

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

### /next-block
Przejdź do następnego zadania z current block

### /phase-run <phase>
Wykonuj całą fazę automatycznie:
1. Wczytaj IMPLEMENTATION_ROADMAP.md
2. Znajdź wszystkie bloki w podanej fazie
3. Dla każdego bloku po kolei:
   - Wykonaj pre-work (create issue, branch, update context)
   - Zrealizuj wszystkie zadania atomowe
   - Sprawdź metryki sukcesu
   - Wykonaj post-work
   - Automatycznie przejdź do następnego bloku
4. Po ukończeniu wszystkich bloków w fazie:
   - Podsumuj wyniki
   - Zamknij milestone
   - Przygotuj issues dla następnej fazy

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

## 📊 Performance Targets
- Import time: <0.05s (current: 9ms ✅)
- Memory: <30MB (current: ~17MB ✅)
- Agent creation: <10ms (current: <5ms ✅)
- Task execution overhead: <5% (current: <3% ✅)
- Test coverage: >90%

## 🔗 Project Links
- **LiteCrew-LangChain**: `/Users/hretheum/dev/bezrobocie/litecrew/litecrew-langchain/`
  - Roadmap: `docs/IMPLEMENTATION_ROADMAP.md`
  - Context: `project-context.md`
  - Workflow: `docs/PROJECT_WORKFLOW.md`
  - Repo: https://gitlab.com/eof3/litecrewai

## 🏁 Current Status
- Phase 0: Infrastructure ✅ (97%)
- Phase 1: Cleanup & Optimization ✅
- Phase 2: Core Engine ✅ (All 4 blocks completed)
- **Next**: Phase 3 Block 3.1 - Multi-LLM Support