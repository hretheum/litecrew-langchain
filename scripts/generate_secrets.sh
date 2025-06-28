#!/bin/bash
# generate_secrets.sh - Generate secure secrets for .env file

echo "🔐 Generating secure secrets for LiteCrewAI..."

# Generate SECRET_KEY (32 bytes, base64)
SECRET_KEY=$(openssl rand -base64 32)
echo "SECRET_KEY=$SECRET_KEY"

# Generate JWT_SECRET (32 bytes, hex)
JWT_SECRET=$(openssl rand -hex 32)
echo "JWT_SECRET=$JWT_SECRET"

# Generate BACKUP_ENCRYPTION_KEY (24 bytes, base64)
BACKUP_ENCRYPTION_KEY=$(openssl rand -base64 24)
echo "BACKUP_ENCRYPTION_KEY=$BACKUP_ENCRYPTION_KEY"

# Generate METRICS_PASSWORD (16 bytes, alphanumeric)
METRICS_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)
echo "METRICS_PASSWORD=$METRICS_PASSWORD"

echo ""
echo "✅ Add these to your .env file and GitLab CI/CD variables!"
echo "⚠️  Keep these values secret and never commit them!"