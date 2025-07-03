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

### ⚠️ WAŻNE - Działania ręczne:
**ZAWSZE ZATRZYMAJ SIĘ** gdy potrzebne jest działanie użytkownika:
- Ustawienie GITLAB_TOKEN lub innych credentials
- Konfiguracja w GitLab UI (labels, milestones, settings)
- Instalacja narzędzi systemowych
- Tworzenie kont zewnętrznych (API keys)
- Weryfikacja działania (np. "sprawdź czy Docker działa")

**Format zatrzymania:**
```
⚠️ WYMAGANE DZIAŁANIE RĘCZNE:
1. Co zrobić: [dokładna instrukcja]
2. Gdzie: [URL lub ścieżka]
3. Przykład: [komenda lub screenshot]
4. Weryfikacja: [jak sprawdzić czy działa]

Gdy wykonasz, wpisz "done" aby kontynuować.
```

### Koniec sesji:
1. Zaktualizuj project-context.md
2. Sprawdź metryki wydajności
3. Commit (bez push)

## 📝 Custom Commands

⚠️ **Aliasy przeniesione do głównego pliku**: `/Users/hretheum/dev/bezrobocie/litecrew/CLAUDE.md`

Wszystkie custom commands (/sprint-start, /task-check, /sprint-end, /status, /next, /phase-run) 
znajdują się teraz w głównym pliku CLAUDE.md dla łatwiejszego dostępu z każdego projektu.

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