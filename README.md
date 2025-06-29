# LiteCrewAI

Lekka, osobista platforma agentów AI - fork CrewAI zoptymalizowany pod kątem użytku indywidualnego.

## 📋 O projekcie

LiteCrewAI to uproszczona wersja CrewAI zaprojektowana dla:
- **Niskiego zużycia zasobów**: <10MB pamięci per agent
- **Szybkiego startu**: <100ms czas uruchomienia
- **Prywatności**: Brak telemetrii, lokalne dane
- **Niskich kosztów**: <$30/miesiąc infrastruktura
- **Łatwej rozbudowy**: System pluginów

## 🗂️ Struktura

- `masterplan/` - Kompletna dokumentacja techniczna projektu (8 faz rozwoju)
  - `src/common/` - Współdzielone skrypty walidacyjne
  - `src/faza-X/` - Kod źródłowy dla każdej fazy
- `crewai-fork/` - Fork CrewAI (237MB, bez telemetrii i enterprise)
- `scripts/` - Skrypty pomocnicze (fork, telemetry removal, enterprise removal)
- `docs/` - Dokumentacja dodatkowa i materiały pomocnicze
- `litecrewai-master-plan.md` - Monolityczny dokument ze wszystkimi fazami
- `SECURITY.md` - Wytyczne bezpieczeństwa projektu
- `CLAUDE.md` - Instrukcje dla asystentów AI
- `project-context.md` - Kontekst projektu i status
- `.env.example` - Szablon zmiennych środowiskowych

**Uwaga**: Treść w `litecrewai-master-plan.md` jest identyczna z plikami w `masterplan/`, ale w jednym dokumencie dla wygody.

## 🚀 Quick Start

Szczegółowa dokumentacja znajduje się w folderze `masterplan/`:

1. [Wprowadzenie](masterplan/00-wprowadzenie.md)
2. [Faza 0: Przygotowanie środowiska](masterplan/faza-0-przygotowanie-srodowiska.md)
3. [Faza 1: Fork i minimalizacja](masterplan/faza-1-fork.md)
4. [Faza 2: Core Engine](masterplan/faza-2-core-engine.md)
5. [Faza 3: Integracja LLM](masterplan/faza-3-LLM.md)
6. [Faza 4: Storage](masterplan/faza-4-storage.md)
7. [Faza 5: API](masterplan/faza-5-api.md)
8. [Faza 6: Monitoring](masterplan/faza-6-monitoring.md)
9. [Faza 7: Deployment](masterplan/faza-7-deployment.md)

## 📊 Status

- ✅ Dokumentacja: 100% kompletna
- ✅ Kod źródłowy: Wyekstrahowany do `masterplan/src/`
- ✅ Faza 0: Infrastruktura i środowisko (97% ukończone)
- ✅ Faza 1 Blok 1.1: Fork and Initial Cleanup (100% ukończone)
- 🚧 Faza 1 Blok 1.2: Dependency Optimization (następny krok)
- 🚧 Implementacja: W trakcie rozwoju

## 🛠️ Stack technologiczny

- Python 3.12
- FastAPI (local-only, bez auth)
- SQLite (główna baza danych)
- Redis (cache)
- Ollama/OpenAI/Anthropic (LLM providers)

## 📝 Licencja

MIT