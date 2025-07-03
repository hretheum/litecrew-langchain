# LiteCrew LLM Providers Configuration Guide

## Quick Start

```python
from litecrew import LiteAgent

# OpenAI (default)
agent = LiteAgent(
    role="Researcher",
    goal="Find information",
    backstory="Expert researcher",
    llm_provider="openai",
    llm_config={"model": "gpt-4-turbo-preview", "temperature": 0.7}
)

# Anthropic
agent = LiteAgent(
    role="Writer",
    goal="Write content",
    backstory="Professional writer",
    llm_provider="anthropic",
    llm_config={"model": "claude-3-opus-20240229"}
)

# Local Ollama
agent = LiteAgent(
    role="Analyst",
    goal="Analyze data",
    backstory="Data analyst",
    llm_provider="ollama",
    llm_config={"model": "llama2", "api_base": "http://localhost:11434"}
)
```

## Provider Configuration Examples

### OpenAI
```python
llm_config = {
    "model": "gpt-4-turbo-preview",  # or gpt-3.5-turbo
    "temperature": 0.7,
    "max_tokens": 1000,
    "api_key": "sk-...",  # Optional, uses env var OPENAI_API_KEY
    "api_base": "https://api.openai.com/v1",  # Optional
    "streaming": True
}
```

### Anthropic
```python
llm_config = {
    "model": "claude-3-opus-20240229",  # or claude-3-sonnet-20240229
    "temperature": 0.7,
    "max_tokens": 1000,
    "api_key": "sk-ant-...",  # Optional, uses env var ANTHROPIC_API_KEY
    "streaming": True
}
```

### Groq
```python
llm_config = {
    "model": "mixtral-8x7b-32768",  # or llama2-70b-4096
    "temperature": 0.7,
    "max_tokens": 1000,
    "api_key": "gsk_...",  # Optional, uses env var GROQ_API_KEY
    "streaming": True
}
```

### Ollama (Local)
```python
llm_config = {
    "model": "llama2",  # or mistral, codellama, etc.
    "temperature": 0.7,
    "api_base": "http://localhost:11434"  # Ollama server URL
}
```

### Cohere
```python
llm_config = {
    "model": "command",  # or command-light
    "temperature": 0.7,
    "max_tokens": 1000,
    "api_key": "...",  # Optional, uses env var COHERE_API_KEY
}
```

### Azure OpenAI
```python
llm_config = {
    "model": "gpt-4",  # Your deployment name
    "temperature": 0.7,
    "extra_params": {
        "azure_endpoint": "https://your-resource.openai.azure.com/",
        "api_version": "2024-02-01",
        "azure_deployment": "your-deployment-name"
    }
}
```

### AWS Bedrock
```python
llm_config = {
    "model": "anthropic.claude-v2",  # or amazon.titan-text-express-v1
    "temperature": 0.7,
    "extra_params": {
        "region_name": "us-east-1",
        "model_kwargs": {"max_tokens_to_sample": 1000}
    }
}
```

### Google Vertex AI
```python
llm_config = {
    "model": "gemini-pro",  # or chat-bison
    "temperature": 0.7,
    "extra_params": {
        "project": "your-project-id",
        "location": "us-central1"
    }
}
```

### HuggingFace
```python
llm_config = {
    "model": "microsoft/DialoGPT-medium",  # Any HF model
    "temperature": 0.7,
    "extra_params": {
        "task": "text-generation",
        "model_kwargs": {"max_new_tokens": 100}
    }
}
```

### Together AI
```python
llm_config = {
    "model": "togethercomputer/llama-2-70b-chat",
    "temperature": 0.7,
    "max_tokens": 1000,
    "api_key": "...",  # Optional, uses env var TOGETHER_API_KEY
}
```

## Advanced Features

### Provider Fallback
```python
agent = LiteAgent(
    role="Assistant",
    goal="Help users",
    backstory="AI assistant",
    llm_provider="openai",
    fallback_providers=["anthropic", "groq", "ollama"],
    llm_config={"model": "gpt-4-turbo-preview"}
)
```

### Response Caching
```python
agent = LiteAgent(
    role="Researcher",
    goal="Research topics",
    backstory="Research expert",
    cache_responses=True,  # Enable caching
    llm_provider="openai"
)
```

### Streaming Responses
```python
agent = LiteAgent(
    role="Writer",
    goal="Write content",
    backstory="Content creator",
    streaming=True,
    on_chunk=lambda chunk: print(chunk, end=""),
    llm_provider="anthropic"
)

# Use streaming
async for chunk in agent.stream_execute("Write a story"):
    print(chunk, end="", flush=True)
```

### Dynamic Provider Switching
```python
# Start with OpenAI
agent = LiteAgent(
    role="Assistant",
    goal="Help users",
    backstory="AI assistant",
    llm_provider="openai"
)

# Switch to Anthropic
agent.switch_llm_provider("anthropic", {
    "model": "claude-3-opus-20240229",
    "temperature": 0.5
})
```

## Environment Variables

Set these environment variables to avoid hardcoding API keys:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Groq
export GROQ_API_KEY="gsk_..."

# Cohere
export COHERE_API_KEY="..."

# Azure OpenAI
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"

# AWS (for Bedrock)
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"

# Google Cloud (for Vertex AI)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

# HuggingFace
export HUGGINGFACEHUB_API_TOKEN="hf_..."

# Together AI
export TOGETHER_API_KEY="..."
```

## Performance Tips

1. **Use Groq** for fastest inference (up to 10x faster than OpenAI)
2. **Use Ollama** for local/offline operation with no API costs
3. **Enable caching** to avoid repeated API calls
4. **Use smaller models** (gpt-3.5-turbo, claude-instant) for simple tasks
5. **Batch requests** when processing multiple tasks

## Troubleshooting

### Missing Dependencies
If you get an import error, install the required package:
```bash
# The error message will tell you exactly what to install
pip install langchain-openai  # For OpenAI
pip install langchain-anthropic  # For Anthropic
# etc.
```

### API Key Issues
1. Check environment variable is set: `echo $OPENAI_API_KEY`
2. Verify key is valid on provider's dashboard
3. Check for typos or extra spaces

### Connection Issues
1. For Ollama: ensure server is running (`ollama serve`)
2. For Azure/AWS/GCP: check credentials and permissions
3. Check firewall/proxy settings

### Model Not Found
1. Verify model name is correct (case-sensitive)
2. Check model is available in your region (AWS/Azure/GCP)
3. For Ollama: pull model first (`ollama pull llama2`)