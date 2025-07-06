# LiteCrew Security Setup Guide

## 🔒 Overview

This guide explains how to secure your LiteCrew deployment to prevent unauthorized access and abuse.

## 🔑 API Key Authentication

### 1. Generate API Keys

```bash
# Generate secure API keys
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Configure Environment Variables

Add to your `.env` file or GitLab CI/CD variables:

```bash
# Comma-separated list of valid API keys
LITECREW_API_KEYS=your-api-key-1,your-api-key-2,your-api-key-3
```

### 3. Using API Keys

Include the API key in request headers:

```bash
curl -H "X-API-Key: your-api-key-1" http://152.42.139.18:8000/api/v1/crews
```

Python example:
```python
import requests

headers = {"X-API-Key": "your-api-key-1"}
response = requests.get("http://152.42.139.18:8000/api/v1/crews", headers=headers)
```

### 4. Excluded Endpoints

These endpoints remain public:
- `/docs` - API documentation
- `/openapi.json` - OpenAPI specification
- `/api/v1/health` - Health check
- `/auth/*` - Authentication endpoints

## 🔐 Google OAuth for Dashboard

### 1. Create Google OAuth Application

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: 
     - `http://localhost:8000/auth/google/callback` (development)
     - `http://152.42.139.18:8000/auth/google/callback` (production)

### 2. Configure Environment Variables

```bash
# Google OAuth credentials
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://152.42.139.18:8000/auth/google/callback

# JWT configuration
JWT_SECRET=your-jwt-secret-key  # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SESSION_SECRET=your-session-secret  # Generate similarly

# Access restrictions (optional)
ALLOWED_EMAIL_DOMAINS=yourdomain.com,anotherdomain.com  # Comma-separated
ALLOWED_EMAILS=user1@gmail.com,user2@gmail.com  # Specific emails

# Dashboard authentication
REQUIRE_DASHBOARD_AUTH=true  # Set to false to disable auth
```

### 3. Authentication Flow

1. User visits dashboard (`/`)
2. If not authenticated, redirected to `/auth/google/login`
3. User authenticates with Google
4. Callback to `/auth/google/callback`
5. JWT token set as httpOnly cookie
6. User redirected to dashboard

### 4. Logout

Visit `/auth/logout` to clear authentication.

## 🚦 Rate Limiting

### Default Limits

- **Unauthenticated**: 60 requests/minute
- **Authenticated (API Key)**: 600 requests/minute
- **Burst allowance**: 10 requests in 10 seconds

### Headers

Rate limit information in response headers:
```
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 599
X-RateLimit-Reset: 1704123456
```

### Custom Limits

Configure in environment:
```bash
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=20
RATE_LIMIT_AUTH_MULTIPLIER=10
```

## 🌐 CORS Configuration

### Production Setup

```bash
# Comma-separated allowed origins
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# In development, defaults to allow all (*)
```

## 🛡️ Security Headers

Automatically applied headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security` (production only)

## 🏠 Host Header Validation

Prevent host header attacks in production:

```bash
# Comma-separated allowed hosts
ALLOWED_HOSTS=152.42.139.18,yourdomain.com
```

## 📋 Complete Environment Example

```bash
# API Security
LITECREW_API_KEYS=key1,key2,key3

# Google OAuth
GOOGLE_CLIENT_ID=123456789.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
GOOGLE_REDIRECT_URI=http://152.42.139.18:8000/auth/google/callback
ALLOWED_EMAIL_DOMAINS=yourdomain.com
ALLOWED_EMAILS=admin@gmail.com

# JWT & Sessions
JWT_SECRET=your-jwt-secret-32-chars-minimum
SESSION_SECRET=your-session-secret-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Security Settings
REQUIRE_DASHBOARD_AUTH=true
ENVIRONMENT=production
CORS_ORIGINS=http://152.42.139.18:8000
ALLOWED_HOSTS=152.42.139.18

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10
RATE_LIMIT_AUTH_MULTIPLIER=10
```

## 🚀 Deployment Steps

1. **Update GitLab CI/CD Variables**:
   - Add all security-related environment variables
   - Mark sensitive ones as "masked"

2. **Test Locally**:
   ```bash
   # Run with security enabled
   docker run -p 8000:8000 \
     -e LITECREW_API_KEYS=test-key \
     -e GOOGLE_CLIENT_ID=your-client-id \
     -e GOOGLE_CLIENT_SECRET=your-secret \
     registry.gitlab.com/eof3/litecrewai/litecrewai:latest
   ```

3. **Deploy**:
   - Push changes to trigger pipeline
   - Verify security headers: `curl -I http://152.42.139.18:8000/api/v1/health`

## 🧪 Testing Security

### Test API Key Auth
```bash
# Should fail (401)
curl http://152.42.139.18:8000/api/v1/crews

# Should succeed
curl -H "X-API-Key: your-key" http://152.42.139.18:8000/api/v1/crews
```

### Test Rate Limiting
```bash
# Send many requests quickly
for i in {1..100}; do
  curl -H "X-API-Key: your-key" http://152.42.139.18:8000/api/v1/health
done
```

### Test Dashboard Auth
1. Visit http://152.42.139.18:8000/
2. Should redirect to Google login
3. After auth, should see dashboard

## 📊 Monitoring

Check security status in logs:
```bash
ssh litecrewai@152.42.139.18 "sudo docker logs litecrew_app | grep Security"
```

Output should show:
```
🔒 Security Configuration:
  - API Keys: Configured
  - Google OAuth: Configured
  - Dashboard Auth: Required
  - CORS Origins: ['http://152.42.139.18:8000']
  - Environment: production
```