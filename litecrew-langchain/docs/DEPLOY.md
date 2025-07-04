# Plan Deployment na Droplet - LiteCrew

## 📋 Plan działania krok po kroku

### Krok 1: Zabezpieczenie kluczy API ✅
- [x] Stwórz .env.example
- [x] Stwórz config.py do zarządzania konfiguracją
- [x] Stwórz SECURITY.md z wytycznymi
- [ ] Zmień klucze API (do zrobienia ręcznie)

### Krok 2: Uzupełnienie zależności
Dodać do pyproject.toml:
- [ ] fastapi
- [ ] uvicorn[standard]
- [ ] redis
- [ ] httpx
- [ ] sqlalchemy
- [ ] psycopg2-binary (dla PostgreSQL)
- [ ] aiofiles (dla static files)
- [ ] websockets

### Krok 3: Stworzenie requirements.txt
- [ ] Wyeksportować wszystkie zależności z pyproject.toml
- [ ] Dodać brakujące zależności API

### Krok 4: Stworzenie skryptu run_server.py
- [ ] Entry point dla uvicorn
- [ ] Konfiguracja host/port
- [ ] Opcje dla development/production

### Krok 5: Stworzenie Dockerfile
- [ ] Multi-stage build dla optymalizacji
- [ ] Python 3.11 slim base
- [ ] Proper user permissions
- [ ] Health check

### Krok 6: Stworzenie docker-compose.yml
- [ ] Service dla LiteCrew
- [ ] Redis service
- [ ] PostgreSQL service (opcjonalnie)
- [ ] Volumes dla persistence
- [ ] Environment variables

### Krok 7: Dodatkowe pliki
- [ ] .dockerignore
- [ ] docker-compose.override.yml (dla development)
- [ ] scripts/deploy.sh (automatyzacja)

### Krok 8: Testowanie lokalne
- [ ] Build image
- [ ] Run w kontenerze
- [ ] Test API endpoints
- [ ] Test WebSocket
- [ ] Test dashboard

### Krok 9: Przygotowanie Droplet
- [ ] Update system
- [ ] Install Docker & Docker Compose
- [ ] Setup firewall (UFW)
- [ ] Configure nginx as reverse proxy
- [ ] Setup SSL with Let's Encrypt

### Krok 10: Deployment
- [ ] Push code to GitLab
- [ ] SSH to Droplet
- [ ] Clone repository
- [ ] Configure production .env
- [ ] docker-compose up -d
- [ ] Test production endpoints

## 🚀 Rozpoczynamy implementację...