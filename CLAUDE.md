# LiteCrewAI - Instrukcje dla Claude

## 🔒 Bezpieczeństwo - KRYTYCZNE

### NIGDY nie rób:
1. **NIE hardcoduj** żadnych haseł, kluczy API ani sekretów w kodzie
2. **NIE używaj** domyślnych wartości dla credentials (np. "admin", "changeme")
3. **NIE commituj** pliku .env - zawsze sprawdzaj przed commitem
4. **NIE loguj** wrażliwych danych (hasła, tokeny, klucze API)
5. **NIE zapisuj** sekretów w plikach konfiguracyjnych

### ZAWSZE rób:
1. **Używaj zmiennych środowiskowych** dla wszystkich sekretów
2. **Waliduj wszystkie dane wejściowe** (szczególnie z environment variables)
3. **Wymagaj autentykacji** dla wszystkich API endpoints
4. **Implementuj rate limiting** dla publicznych endpoints
5. **Używaj HTTPS/TLS** dla wszystkich połączeń
6. **Szyfruj wrażliwe dane** w bazie danych
7. **Sprawdzaj plik SECURITY.md** przed implementacją

### Struktura .env:
```bash
# Wszystkie sekrety TYLKO tutaj
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:password@localhost:5432/litecrewai
SECRET_KEY=long-random-string-here
```

## 📁 Struktura projektu

```
/Users/hretheum/dev/bezrobocie/crewAI/
├── masterplan/          # Dokumentacja techniczna (8 faz)
│   ├── src/            # Wyekstrahowany kod źródłowy
│   │   ├── faza-0/     # Skrypty walidacyjne infrastruktury
│   │   ├── faza-1/     # Fork i minimalizacja
│   │   ├── faza-2/     # Core engine
│   │   ├── faza-3/     # Integracja LLM
│   │   ├── faza-4/     # Storage layer
│   │   ├── faza-5/     # API i dashboard
│   │   ├── faza-6/     # Monitoring
│   │   └── faza-7/     # Deployment
│   └── *.md            # Dokumenty faz
├── .env.example        # Przykład zmiennych (TO commituj)
├── .env               # Rzeczywiste sekrety (NIE commituj!)
├── SECURITY.md        # Zasady bezpieczeństwa
└── README.md          # Dokumentacja główna
```

## 🎯 Cele projektu

1. **Lightweight**: <10MB pamięci per agent
2. **Fast**: <100ms startup time
3. **Privacy-first**: Brak telemetrii, lokalne dane
4. **Cost-effective**: <$30/miesiąc infrastruktura
5. **Secure**: Przestrzeganie najlepszych praktyk bezpieczeństwa

## 🛠️ Stack technologiczny

- Python 3.11+ (async/await everywhere)
- FastAPI (z pełną autentykacją)
- PostgreSQL + Redis
- OpenTelemetry + Prometheus
- Docker + Kubernetes

## 📝 Konwencje kodu

1. **Async first** - wszystko asynchroniczne
2. **Type hints** - 100% pokrycia
3. **Validation** - Pydantic dla wszystkich danych wejściowych
4. **Error handling** - Spójna hierarchia wyjątków
5. **Testing** - Minimum 80% code coverage

## 🚀 Workflow

1. Przed każdą zmianą sprawdź SECURITY.md
2. Używaj zmiennych środowiskowych dla konfiguracji
3. Testuj lokalnie z .env
4. Nigdy nie commituj prawdziwych sekretów
5. Zawsze waliduj dane wejściowe

## ✅ Status bezpieczeństwa

Wszystkie znane problemy bezpieczeństwa zostały naprawione:
- metrics_endpoint.py - wymaga METRICS_USERNAME/PASSWORD z .env
- websocket_api.py - wymaga tokenu autoryzacyjnego
- validate_droplet_setup.sh - waliduje format adresu IP

# Custom Commands / Aliasy

## /nakurwiaj <szczegóły>

Gdy użytkownik wpisze tę komendę, wykonaj następujące kroki:

1. Wczytaj numerowany blok zadań atomowych który użytkownik wskaże z podanego pliku
2. we wskazanym w <szczegóły> bloku zadań atomowych:
   a. Rozpocznij wykonywanie pierwszego zadania atomowego
   b. Po każdym zadaniu atomowym oznacz je jako wykonane (checkbox [x])
   c. Po ukończeniu wszystkich zadań w bloku:
      - Przeprowadź walidację kryteriów sukcesu metodami wskazanymi w dokumencie
      - Wykonaj code review
      - Wprowadź ewentualne poprawki
      - Wykonaj git add, commit bez push
        d. Zatrzymaj się
3. Używaj równoległych wywołań narzędzi gdzie to możliwe
4. Minimalizuj output - skupiaj się na wykonaniu, nie na opisywaniu


## /status

Pokaż:

- Aktualny dzień projektu
- Stan zadań z roadmapy na dziś
- Które bloki zadań są ukończone
- Co jest w trakcie realizacji
- Co pozostało do zrobienia

## /next

Przejdź do następnego zadania atomowego lub bloku zadań z roadmapy

## 🚀 DROPLET CONFIG - KURWA UŻYWAJ TEGO!

**IP**: 46.101.181.183
**USER**: litecrewai
**SSH KEY**: ~/.ssh/id_rag
**SSH COMMAND**: `ssh -p 2222 -i ~/.ssh/id_rag litecrewai@46.101.181.183`

⚠️ **NAKAZ**: ZAWSZE używaj powyższej konfiguracji SSH. NIE WYMYŚLAJ własnej!

## 🔗 Linki

- Repo: https://gitlab.com/eof3/litecrewai
- Dokumentacja: /masterplan/README.md
- Security: /SECURITY.md