# Contributing to LiteCrewAI

## 🤝 Jak pomóc

Cieszymy się, że chcesz przyczynić się do rozwoju LiteCrewAI!

### Zgłaszanie błędów

1. Sprawdź czy problem nie został już zgłoszony w [Issues](https://gitlab.com/eof3/litecrewai/-/issues)
2. Opisz dokładnie problem, dodaj logi i kroki reprodukcji
3. Użyj template'u dla bug report

### Proponowanie funkcji

1. Otwórz dyskusję w [Issues](https://gitlab.com/eof3/litecrewai/-/issues) z tagiem `enhancement`
2. Opisz use case i korzyści
3. Poczekaj na feedback przed implementacją

### Pull Requests

1. Fork projektu
2. Stwórz branch: `git checkout -b feature/nazwa-funkcji`
3. Commituj zmiany: `git commit -m 'Add: opis funkcji'`
4. Push: `git push origin feature/nazwa-funkcji`
5. Otwórz Merge Request

### Kod

- Python 3.12+
- Async/await everywhere
- Type hints required
- Black + Ruff formatting
- 80% test coverage minimum

### Testy

```bash
pytest tests/ -v --cov=app --cov-report=term
```

### Commit Messages

Format: `<type>: <description>`

Types:
- `Add:` nowa funkcjonalność
- `Fix:` naprawa błędu
- `Update:` aktualizacja istniejącej funkcji
- `Refactor:` refaktoryzacja kodu
- `Test:` dodanie/update testów
- `Docs:` dokumentacja
- `Chore:` maintenance, dependencies

### Code Review

Każdy MR przechodzi przez:
1. Automated tests (CI/CD)
2. Code review
3. Performance check
4. Security review

## 📜 Licencja

Kontrybuując zgadzasz się na licencję MIT projektu.