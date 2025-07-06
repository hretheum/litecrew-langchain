# HTTPS Setup dla LiteCrew API

## Co potrzebujemy:

### 1. Certyfikat SSL
**Opcje:**
- **Let's Encrypt** (darmowy, automatyczne odnawianie)
- **Cloudflare** (darmowy z proxy)
- **Własny certyfikat** (np. z DigitalOcean)

### 2. Reverse Proxy
**Opcje:**
- **Nginx** (najpopularniejszy)
- **Traefik** (automatyczne certyfikaty)
- **Caddy** (najprostszy, auto-HTTPS)

### 3. Domena
- Potrzebna własna domena (np. `litecrew.example.com`)
- Rekord DNS typu A wskazujący na IP: `152.42.139.18`

## Rekomendowane rozwiązanie: Nginx + Let's Encrypt

### Krok 1: Instalacja Nginx i Certbot
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

### Krok 2: Konfiguracja Nginx
```nginx
# /etc/nginx/sites-available/litecrew
server {
    listen 80;
    server_name litecrew.example.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Krok 3: Certyfikat Let's Encrypt
```bash
sudo certbot --nginx -d litecrew.example.com
```

### Krok 4: Automatyczne odnawianie
```bash
sudo systemctl enable certbot.timer
```

## Alternatywa: Caddy (najprostsze)

### docker-compose.yml z Caddy:
```yaml
version: '3.8'

services:
  litecrew:
    image: registry.gitlab.com/eof3/litecrewai/litecrewai:5d8c83d0
    environment:
      - LITECREW_API_KEYS=${LITECREW_API_KEYS}
    expose:
      - "8000"
    
  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - litecrew

volumes:
  caddy_data:
  caddy_config:
```

### Caddyfile:
```
litecrew.example.com {
    reverse_proxy litecrew:8000
}
```

## Cloudflare (bez zmian na serwerze)

1. Dodaj domenę do Cloudflare (darmowe)
2. Zmień DNS na Cloudflare
3. Włącz "Proxy" (pomarańczowa chmurka)
4. W SSL/TLS ustaw "Flexible" lub "Full"
5. Gotowe - HTTPS działa automatycznie

### Zalety Cloudflare:
- Zero konfiguracji na serwerze
- DDoS protection
- CDN
- Darmowy certyfikat SSL
- Automatyczne odnawianie

## Zmiany w aplikacji

### 1. Update CORS w FastAPI:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://litecrew.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Trust proxy headers:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["litecrew.example.com", "*.litecrew.example.com"]
)
```

### 3. Secure cookies (jeśli używasz):
```python
response.set_cookie(
    key="session",
    value=token,
    secure=True,  # tylko HTTPS
    httponly=True,
    samesite="strict"
)
```

## Testowanie HTTPS

```bash
# Test certyfikatu
curl -I https://litecrew.example.com/api/v1/health

# Test SSL/TLS
openssl s_client -connect litecrew.example.com:443 -servername litecrew.example.com

# Test security headers
curl -I https://litecrew.example.com | grep -i "strict-transport"
```

## Security Headers (dodatkowe)

W Nginx dodaj:
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

## Podsumowanie

**Najprostsze rozwiązanie**: Cloudflare (5 minut setup)
**Najbardziej kontrolowane**: Nginx + Let's Encrypt
**Najłatwiejsze w docker**: Caddy

Wszystkie opcje są darmowe i zapewniają automatyczne odnawianie certyfikatów.