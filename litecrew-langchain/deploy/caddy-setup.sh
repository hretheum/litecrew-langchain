#!/bin/bash
# Quick HTTPS setup with Caddy

# Create Caddyfile
cat > Caddyfile << 'EOF'
api.litecrew.pl {
    reverse_proxy localhost:8000
}
EOF

# Run Caddy in Docker
docker run -d \
  --name caddy \
  -p 80:80 \
  -p 443:443 \
  -v $PWD/Caddyfile:/etc/caddy/Caddyfile \
  -v caddy_data:/data \
  caddy:2-alpine

echo "HTTPS będzie działać automatycznie po ustawieniu DNS!"