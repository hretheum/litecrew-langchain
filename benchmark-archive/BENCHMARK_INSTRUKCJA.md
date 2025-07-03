# 🚀 Instrukcja uruchomienia benchmarku LiteCrew

## Przegląd sytuacji

Benchmark został przygotowany ale **extended_benchmark się wysypał** z powodu braku zainstalowanych pakietów w środowiskach wirtualnych. Lokalne środowiska są puste.

## ✅ Co już mamy

1. **Visual benchmark działa** - pokazuje podstawowe metryki:
   - CrewAI Official: 551.5MB, 2.926s import
   - LiteCrew Slim: 8.4MB, 0.000s import 
   - LangChain: 97.3MB, 0.135s import

2. **Fork CrewAI** znajduje się w: `/Users/hretheum/dev/bezrobocie/litecrew/crewai-fork`

3. **Skrypty deployment** są gotowe

## 🎯 Jak uruchomić pełny benchmark

### Opcja 1: Deployment na DigitalOcean (REKOMENDOWANE)

```bash
cd /Users/hretheum/dev/bezrobocie/litecrew/benchmark

# Uruchom prosty deployment
./deploy-benchmark-simple.sh
```

Skrypt automatycznie:
1. Przygotuje pakiet z kodem
2. Utworzy droplet na DigitalOcean ($0.125/h)
3. Zainstaluje środowisko
4. Uruchomi benchmark
5. Pobierze wyniki
6. Zapyta czy usunąć droplet

### Opcja 2: Ręczny deployment

```bash
# 1. Przygotuj pakiet
./prepare-benchmark-package.sh

# 2. Stwórz droplet
doctl compute droplet create benchmark-litecrew \
  --size c-4-8gib \
  --image ubuntu-22-04-x64 \
  --region nyc3 \
  --ssh-keys $(doctl compute ssh-key list --format ID --no-header | head -1) \
  --wait

# 3. Pobierz IP
DROPLET_IP=$(doctl compute droplet list --format "Name,PublicIPv4" --no-header | grep benchmark-litecrew | awk '{print $2}')

# 4. Skopiuj i uruchom
scp /tmp/litecrew-benchmark-package.tar.gz root@$DROPLET_IP:/tmp/
ssh root@$DROPLET_IP 'cd /root && tar -xzf /tmp/litecrew-benchmark-package.tar.gz && ./install_and_run.sh'

# 5. Pobierz wyniki
scp root@$DROPLET_IP:/root/benchmark/benchmark_results.json ./
```

## 📊 Co testuje benchmark

1. **Import time** - czas ładowania frameworka
2. **Package size** - rozmiar zainstalowanych pakietów
3. **Memory usage** - zużycie pamięci podczas pracy
4. **CPU usage** - obciążenie procesora
5. **Task execution** - czas wykonania prostego zadania

## 🔍 Frameworki w teście

- **CrewAI Official** (0.134.0) - oficjalna wersja z PyPI
- **LiteCrew Fork** - odchudzony fork (98.5% redukcja)
- **LangChain** - najpopularniejszy framework
- **PyAutoGen** - Microsoft AutoGen

## ⚠️ Wymagania

- Konto DigitalOcean z kredytami (~$0.50 na test)
- Zainstalowany `doctl` i skonfigurowany
- SSH key dodany do DigitalOcean

## 💡 Wskazówki

1. **Droplet auto-usunie się po 4 godzinach** jeśli zapomnisz
2. **Benchmark trwa ~45-60 minut** dla pełnego testu
3. **Koszt**: około $0.25-0.50 za pełny benchmark

## 🎯 Cel benchmarku

Podjęcie decyzji:
- Czy używać **CrewAI fork** (lekki ale może brakować funkcji)?
- Czy przejść na **LangChain** (popularny, dobrze wspierany)?
- Czy zostać przy **oryginalnym CrewAI** (ciężki ale pełny)?

## 📈 Oczekiwane wyniki

Na podstawie wstępnych testów:
- **Najmniejszy**: LiteCrew Fork (~10MB)
- **Najszybszy start**: LiteCrew Fork (0s)
- **Najbardziej funkcjonalny**: CrewAI Official
- **Najlepszy kompromis**: LangChain?

Pełny benchmark da nam twarde dane do podjęcia decyzji.