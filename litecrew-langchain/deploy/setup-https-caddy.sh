#!/bin/bash
# HTTPS setup dla api.litecrew.app z Caddy

echo "🚀 Konfiguracja HTTPS dla api.litecrew.app"

# Komenda do uruchomienia na serwerze
cat << 'EOF'

# 1. Zatrzymaj obecny kontener na porcie 8000
docker stop litecrew_app

# 2. Uruchom ponownie bez mapowania portu (tylko expose)
docker run -d \
  --name litecrew_api \
  --network host \
  -e LITECREW_API_KEYS="prod-44c8a3026e05e84f44cd1f4cdda7b6ecaba64ccfb2dedd508a80a20405a54509,prod-92b8fba576057868543d3eb7302e6087dc202ea643720f516406cb9e1122497c" \
  registry.gitlab.com/eof3/litecrewai/litecrewai:5d8c83d0

# 3. Utwórz Caddyfile
cat > /home/litecrewai/Caddyfile << 'CADDYFILE'
api.litecrew.app {
    reverse_proxy localhost:8000
    
    # Security headers
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        X-XSS-Protection "1; mode=block"
    }
}
CADDYFILE

# 4. Uruchom Caddy
docker run -d \
  --name caddy \
  --network host \
  -v /home/litecrewai/Caddyfile:/etc/caddy/Caddyfile \
  -v caddy_data:/data \
  -v caddy_config:/config \
  caddy:2-alpine

echo "✅ HTTPS powinno działać w ciągu 1-2 minut!"
echo "🔒 Sprawdź: https://api.litecrew.app/api/v1/health"

EOF