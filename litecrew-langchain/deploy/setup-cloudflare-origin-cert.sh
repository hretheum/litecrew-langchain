#!/bin/bash
# Setup Cloudflare Origin Certificate dla LiteCrew API

echo "🔐 Konfiguracja Cloudflare Origin Certificate"
echo "==========================================="
echo ""
echo "1. Wklej Origin Certificate i Private Key na serwer:"
echo ""
cat << 'EOF'
# Na serwerze utwórz pliki:
sudo mkdir -p /etc/ssl/cloudflare
sudo nano /etc/ssl/cloudflare/cert.pem    # Wklej Origin Certificate
sudo nano /etc/ssl/cloudflare/key.pem     # Wklej Private Key
sudo chmod 600 /etc/ssl/cloudflare/key.pem
EOF

echo ""
echo "2. Zainstaluj Nginx jako reverse proxy z SSL:"
echo ""
cat << 'EOF'
# Instalacja Nginx
sudo apt update && sudo apt install -y nginx

# Konfiguracja Nginx z SSL
sudo tee /etc/nginx/sites-available/api-litecrew << 'NGINX'
server {
    listen 443 ssl;
    server_name api.litecrew.app;

    ssl_certificate /etc/ssl/cloudflare/cert.pem;
    ssl_certificate_key /etc/ssl/cloudflare/key.pem;

    # Cloudflare Origin SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.litecrew.app;
    return 301 https://$server_name$request_uri;
}
NGINX

# Włącz konfigurację
sudo ln -sf /etc/nginx/sites-available/api-litecrew /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
EOF

echo ""
echo "3. Dodaj porty 443 i 80 do UFW:"
echo ""
cat << 'EOF'
sudo ufw allow 443/tcp comment "HTTPS"
sudo ufw allow 80/tcp comment "HTTP redirect"
sudo ufw reload
EOF

echo ""
echo "4. W Cloudflare zmień SSL/TLS na 'Full (strict)'"
echo ""
echo "✅ Po wykonaniu tych kroków HTTPS powinno działać!"