#!/bin/bash
# Update LiteCrew with Anthropic API key

echo "🚀 Aktualizacja LiteCrew z Anthropic API"
echo "========================================"
echo ""
echo "Uruchom te komendy na serwerze:"
echo ""
cat << 'EOF'
# 1. Zatrzymaj obecny kontener
docker stop litecrew_api && docker rm litecrew_api

# 2. Uruchom z Anthropic API key
docker run -d \
  --name litecrew_api \
  -p 8000:8000 \
  -e LITECREW_API_KEYS="${LITECREW_API_KEYS}" \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -e LITECREW_DEFAULT_PROVIDER="anthropic" \
  -e LITECREW_DEFAULT_MODEL="claude-3-opus-20240229" \
  --restart unless-stopped \
  registry.gitlab.com/eof3/litecrewai/litecrewai:5d8c83d0

# 3. Sprawdź logi
docker logs -f litecrew_api
EOF

echo ""
echo "✅ Po uruchomieniu agenci będą używać Claude 3 Opus!"