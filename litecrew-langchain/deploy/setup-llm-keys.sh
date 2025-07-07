#!/bin/bash
# Setup LLM API keys on production

echo "🔧 Konfiguracja LLM API Keys dla LiteCrew"
echo "========================================="
echo ""
echo "Aktualnie LiteCrew wspiera:"
echo "- OpenAI (GPT-4, GPT-3.5)"
echo "- Anthropic (Claude 3 Opus, Sonnet, Haiku)"
echo "- Groq (Mixtral, Llama)"
echo "- Ollama (lokalne modele)"
echo "- Google (Gemini)"
echo "- Cohere"
echo "- HuggingFace"
echo "- Together AI"
echo "- Replicate"
echo ""

echo "🚀 SZYBKA KONFIGURACJA (uruchom na serwerze):"
echo ""
cat << 'EOF'
# 1. Zatrzymaj kontener
docker stop litecrew_api && docker rm litecrew_api

# 2. Uruchom z API keys
docker run -d \
  --name litecrew_api \
  -p 8000:8000 \
  -e LITECREW_API_KEYS="${LITECREW_API_KEYS}" \
  -e OPENAI_API_KEY="sk-..." \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e GROQ_API_KEY="gsk_..." \
  -e GOOGLE_API_KEY="..." \
  -e COHERE_API_KEY="..." \
  -e HUGGINGFACE_API_TOKEN="hf_..." \
  -e TOGETHER_API_KEY="..." \
  -e REPLICATE_API_TOKEN="..." \
  -e LITECREW_DEFAULT_PROVIDER="anthropic" \
  -e LITECREW_DEFAULT_MODEL="claude-3-opus-20240229" \
  --restart unless-stopped \
  registry.gitlab.com/eof3/litecrewai/litecrewai:5d8c83d0
EOF

echo ""
echo "📝 ALTERNATYWA - Użyj pliku .env:"
echo ""
cat << 'EOF'
# 1. Stwórz plik .env na serwerze
cat > /home/litecrewai/.env << 'ENV'
# LiteCrew API Keys
LITECREW_API_KEYS=your-api-key-here

# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...

# Default LLM
LITECREW_DEFAULT_PROVIDER=anthropic
LITECREW_DEFAULT_MODEL=claude-3-opus-20240229
ENV

# 2. Uruchom z plikiem .env
docker run -d \
  --name litecrew_api \
  -p 8000:8000 \
  --env-file /home/litecrewai/.env \
  --restart unless-stopped \
  registry.gitlab.com/eof3/litecrewai/litecrewai:5d8c83d0
EOF

echo ""
echo "🎯 JAK UŻYWAĆ KONKRETNYCH MODELI:"
echo ""
cat << 'PYTHON'
from litecrew import LiteAgent

# Claude 3 Opus (najlepszy)
agent_opus = LiteAgent(
    role="Expert Analyst",
    goal="Provide deep analysis",
    llm_config={
        "provider": "anthropic",
        "model": "claude-3-opus-20240229",
        "temperature": 0.7
    }
)

# GPT-4 Turbo
agent_gpt4 = LiteAgent(
    role="Creative Writer",
    goal="Write engaging content",
    llm_config={
        "provider": "openai", 
        "model": "gpt-4-turbo-preview",
        "temperature": 0.8
    }
)

# Mixtral (szybki i tani)
agent_mixtral = LiteAgent(
    role="Quick Responder",
    goal="Provide fast answers",
    llm_config={
        "provider": "groq",
        "model": "mixtral-8x7b-32768",
        "temperature": 0.5
    }
)
PYTHON

echo ""
echo "⚠️ WAŻNE:"
echo "- Bez API keys używane są tylko placeholdery!"
echo "- Każdy provider wymaga swojego klucza"
echo "- Anthropic Claude Opus 4 nie istnieje jeszcze - użyj claude-3-opus-20240229"
echo "- Groq jest najszybszy, Anthropic najlepszy, OpenAI najbardziej uniwersalny"
EOF

chmod +x /Users/hretheum/dev/bezrobocie/litecrew/litecrew-langchain/deploy/setup-llm-keys.sh