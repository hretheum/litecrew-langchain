#!/bin/bash
# Rozwiązania dla błędu Cloudflare 521

echo "=== ROZWIĄZANIE 1: Sprawdź DigitalOcean Firewall ==="
echo "1. Zaloguj się do DigitalOcean"
echo "2. Idź do: Networking → Firewalls"
echo "3. Sprawdź czy droplet ma przypisany firewall"
echo "4. Jeśli tak, dodaj regułę:"
echo "   - Type: Custom"
echo "   - Protocol: TCP"
echo "   - Port: 8000"
echo "   - Sources: Cloudflare IPs (lub All IPv4/IPv6)"
echo ""

echo "=== ROZWIĄZANIE 2: Dodaj Cloudflare IPs do UFW ==="
echo "Uruchom na serwerze:"
echo ""
cat << 'EOF'
# Pobierz Cloudflare IPs i dodaj do UFW
for ip in $(curl -s https://www.cloudflare.com/ips-v4); do
    sudo ufw allow from $ip to any port 8000 comment "Cloudflare"
done

# Restart UFW
sudo ufw reload
EOF
echo ""

echo "=== ROZWIĄZANIE 3: Użyj standardowego portu 80 ==="
echo "Cloudflare może mieć problem z niestandardowymi portami:"
echo ""
cat << 'EOF'
# Stop current container
docker stop litecrew_api && docker rm litecrew_api

# Run on port 80
docker run -d \
  --name litecrew_api \
  -p 80:8000 \
  -e LITECREW_API_KEYS="${LITECREW_API_KEYS}" \
  registry.gitlab.com/eof3/litecrewai/litecrewai:5d8c83d0
EOF
echo ""

echo "=== ROZWIĄZANIE 4: Nginx Reverse Proxy ==="
echo "Zainstaluj Nginx jako proxy na porcie 80:"
echo ""
cat << 'EOF'
# Install nginx
sudo apt update && sudo apt install -y nginx

# Create config
sudo tee /etc/nginx/sites-available/api << 'NGINX'
server {
    listen 80;
    server_name api.litecrew.app;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

# Enable site
sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
EOF
echo ""

echo "=== ROZWIĄZANIE 5: Wyłącz proxy w Cloudflare ==="
echo "Jeśli nic nie działa, możesz:"
echo "1. Wyłączyć proxy (szara chmurka)"
echo "2. Używać HTTP: http://api.litecrew.app:8000"
echo "3. Lub dodać własny certyfikat Let's Encrypt"