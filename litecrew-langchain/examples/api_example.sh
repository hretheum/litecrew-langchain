#!/bin/bash
# Przykład użycia LiteCrew API

API_KEY="${LITECREW_API_KEY:-your-api-key-here}"
API_URL="https://api.litecrew.app/api/v1"

# 1. Utwórz crew
echo "🚀 Tworzenie crew..."
CREW_RESPONSE=$(curl -s -X POST "$API_URL/crews" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "name": "Content Creation Crew",
    "description": "Crew do tworzenia treści",
    "agents": [
      {
        "role": "Researcher",
        "goal": "Znajdź najnowsze informacje na temat",
        "backstory": "Ekspert w research i analizie danych"
      },
      {
        "role": "Writer",
        "goal": "Napisz angażującą treść",
        "backstory": "Profesjonalny copywriter z 10-letnim doświadczeniem"
      },
      {
        "role": "Editor",
        "goal": "Popraw i wypoleruj treść",
        "backstory": "Redaktor z okiem do szczegółów"
      }
    ],
    "tasks": [
      {
        "description": "Zbadaj najnowsze trendy w AI i machine learning w 2025",
        "agent_role": "Researcher",
        "expected_output": "Raport z 5 najważniejszymi trendami"
      },
      {
        "description": "Napisz artykuł blog o trendach AI na podstawie research",
        "agent_role": "Writer",
        "expected_output": "Artykuł 800-1000 słów",
        "context": [0]
      },
      {
        "description": "Zredaguj i popraw artykuł",
        "agent_role": "Editor",
        "expected_output": "Finalny artykuł gotowy do publikacji",
        "context": [1]
      }
    ],
    "process": "sequential"
  }')

CREW_ID=$(echo $CREW_RESPONSE | jq -r '.crew_id')
echo "✅ Crew utworzony: $CREW_ID"

# 2. Wykonaj crew
echo ""
echo "🔄 Uruchamianie crew..."
EXECUTION_RESPONSE=$(curl -s -X POST "$API_URL/crews/$CREW_ID/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "inputs": {
      "topic": "AI i automatyzacja w 2025",
      "tone": "profesjonalny ale przystępny"
    },
    "async_execution": false
  }')

echo ""
echo "📝 Wynik:"
echo $EXECUTION_RESPONSE | jq -r '.result.raw'