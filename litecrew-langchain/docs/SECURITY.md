# Security Guidelines

## 🔐 API Keys Management

### Never commit API keys to Git!

1. **Use environment variables**
   - Copy `.env.example` to `.env.local`
   - Add your real API keys to `.env.local`
   - Never commit `.env.local` or `.env` with real keys

2. **File hierarchy**
   ```
   .env.local   # Your local keys (git ignored)
   .env         # Development defaults (no real keys!)
   .env.example # Template for others
   ```

3. **On production server**
   - Use environment variables directly
   - Or create `.env.production` (never commit!)
   - Use secrets management service (e.g., HashiCorp Vault)

## 🚨 If keys are exposed

1. **Immediately revoke the exposed keys**
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/
   - GitLab: Settings > Access Tokens

2. **Generate new keys**

3. **Clean Git history** (if needed)
   ```bash
   # Remove file from all commits
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```

## 🛡️ Best Practices

1. **Different keys for different environments**
   - Development: Limited budget keys
   - Staging: Separate keys with monitoring
   - Production: Production-only keys with alerts

2. **Key rotation**
   - Rotate keys regularly (monthly)
   - Use API key management tools
   - Monitor key usage

3. **Least privilege**
   - Create keys with minimal required permissions
   - Use read-only keys where possible
   - Separate keys for different services

## 🐳 Docker Security

1. **Build arguments vs Runtime environment**
   ```dockerfile
   # DON'T DO THIS
   ARG OPENAI_API_KEY
   ENV OPENAI_API_KEY=$OPENAI_API_KEY
   
   # DO THIS
   # Pass keys at runtime via docker-compose or -e flag
   ```

2. **Use .dockerignore**
   ```
   .env
   .env.local
   .env.*.local
   *.log
   .git
   ```

3. **Multi-stage builds**
   - Don't include source code with keys in final image
   - Use minimal base images

## 📝 Configuration Priority

The application loads configuration in this order:
1. Environment variables (highest priority)
2. `.env.local` (for local development)
3. `.env` (defaults only, no real keys)

## 🔍 Monitoring

1. **Set up alerts for:**
   - Unusual API usage
   - Budget thresholds
   - Failed authentication attempts

2. **Log security events**
   - But never log the keys themselves!
   - Log key usage patterns

3. **Regular audits**
   - Check for exposed keys in code
   - Review access logs
   - Update dependencies