"""Configuration management for LiteCrew."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
# Priority: .env.local > .env > environment variables
env_path = Path(__file__).parent.parent.parent

# Try .env.local first (for local development with real keys)
local_env = env_path / ".env.local"
if local_env.exists():
    load_dotenv(local_env)
else:
    # Fall back to .env
    load_dotenv(env_path / ".env")


class Config:
    """Application configuration."""

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # GitLab
    GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./litecrew.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-change-in-production")

    # Additional providers
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        errors = []

        # Check required API keys based on environment
        if cls.ENVIRONMENT == "production":
            if (
                not cls.SECRET_KEY
                or cls.SECRET_KEY == "dev-secret-key-change-in-production"
            ):
                errors.append("SECRET_KEY must be set in production")
            if (
                not cls.JWT_SECRET
                or cls.JWT_SECRET == "dev-jwt-secret-change-in-production"
            ):
                errors.append("JWT_SECRET must be set in production")

        # Warn about missing API keys
        if not any([cls.OPENAI_API_KEY, cls.ANTHROPIC_API_KEY, cls.GROQ_API_KEY]):
            print("Warning: No LLM API keys configured. Some features may not work.")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of configured LLM providers."""
        providers = []
        if cls.OPENAI_API_KEY:
            providers.append("openai")
        if cls.ANTHROPIC_API_KEY:
            providers.append("anthropic")
        if cls.GROQ_API_KEY:
            providers.append("groq")
        if cls.AZURE_OPENAI_API_KEY:
            providers.append("azure_openai")
        if cls.COHERE_API_KEY:
            providers.append("cohere")
        if cls.HUGGINGFACE_API_TOKEN:
            providers.append("huggingface")
        return providers


# Validate configuration on import
Config.validate()
