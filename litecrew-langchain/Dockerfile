# Multi-stage Dockerfile for LiteCrew-LangChain

# Stage 1: Base Python image
FROM python:3.12-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Stage 2: Development environment
FROM base as development

# Install development tools
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    iputils-ping \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Install Python development dependencies
RUN pip install --no-cache-dir \
    ipython \
    ipdb \
    pytest-watch \
    watchdog \
    black \
    ruff \
    mypy

# Set development environment
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=development

# Keep container running for development
CMD ["sleep", "infinity"]

# Stage 3: Test runner
FROM base as test

# Copy requirements first for better caching
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt 2>/dev/null || \
    pip install --no-cache-dir pytest pytest-cov pytest-asyncio

# Copy source code
COPY . .

# Install package in editable mode
RUN pip install -e . 2>/dev/null || echo "Package will be installed when pyproject.toml is ready"

# Default command runs tests
CMD ["pytest", "-v", "--cov=litecrew", "--cov-report=term-missing"]

# Stage 4: Builder for production
FROM base as builder

# Copy requirements
COPY requirements*.txt ./
COPY pyproject.toml* setup.py* ./

# Install dependencies
RUN pip install --no-cache-dir --user \
    langchain \
    langchain-openai \
    fastapi \
    uvicorn \
    redis \
    sqlalchemy \
    aiosqlite

# Copy source code
COPY src/ ./src/

# Install package
RUN if [ -f pyproject.toml ]; then pip install --no-cache-dir --user .; fi

# Stage 5: Production runtime
FROM python:3.12-slim as production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 litecrew

# Copy installed packages from builder
COPY --from=builder /root/.local /home/litecrew/.local

# Copy application
COPY --from=builder /app/src /app/src

# Set user and environment
USER litecrew
ENV PATH=/home/litecrew/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "litecrew.api:app", "--host", "0.0.0.0", "--port", "8000"]