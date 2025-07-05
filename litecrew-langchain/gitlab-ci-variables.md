# GitLab CI/CD Variables Configuration

## Production Environment Variables

Set these in GitLab: **Settings → CI/CD → Variables**

```
SSH_PRIVATE_KEY     = [paste content of ~/.ssh/id_rag]
DROPLET_IP          = 152.42.139.18
CI_REGISTRY_USER    = [your GitLab username]
CI_REGISTRY_PASSWORD = [GitLab Personal Access Token with read_registry, write_registry]
OPENAI_API_KEY      = [your OpenAI API key]
ANTHROPIC_API_KEY   = [optional - Anthropic API key]
GROQ_API_KEY        = [optional - Groq API key]
SECRET_KEY          = [generate secure random string]
JWT_SECRET          = [generate another secure random string]
DB_PASSWORD         = [generate secure password]
```

## Droplet Access Information

- **IP**: 152.42.139.18
- **User**: litecrewai
- **SSH Key**: id_rag
- **SSH Command**: `ssh -i ~/.ssh/id_rag litecrewai@152.42.139.18`
- **Root Access**: User has passwordless sudo

## Docker Status

- **Docker**: 28.3.1 ✅
- **Docker Compose**: 1.29.2 ✅
- **User in docker group**: Yes ✅
- **Project Directory**: /opt/litecrewai/litecrew-langchain

## Next Steps

1. Set all variables in GitLab CI/CD
2. Create GitLab Personal Access Token
3. Merge CI/CD fix branch
4. Trigger deployment pipeline