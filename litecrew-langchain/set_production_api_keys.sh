#!/bin/bash
# Script to set API keys on production server

echo "Setting up API keys on production server..."

# Generate secure random API keys
API_KEY_1=$(openssl rand -hex 32)
API_KEY_2=$(openssl rand -hex 32)

echo "Generated API keys:"
echo "Key 1: prod-$API_KEY_1"
echo "Key 2: prod-$API_KEY_2"

# Command to run on server
echo ""
echo "Run this command on the server:"
echo ""
echo "docker stop litecrew_app && docker rm litecrew_app && docker run -d --name litecrew_app -p 8000:8000 -e LITECREW_API_KEYS=\"prod-$API_KEY_1,prod-$API_KEY_2\" registry.gitlab.com/eof3/litecrewai/litecrew-langchain:latest"
echo ""
echo "Then use one of these keys in Postman's X-API-Key header"