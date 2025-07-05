# Multi-stage build dla LiteCrewAI
FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production image
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 litecrewai && \
    mkdir -p /app /data /logs /config && \
    chown -R litecrewai:litecrewai /app /data /logs /config

# Copy Python packages from builder
COPY --from=builder /root/.local /home/litecrewai/.local

# Set PATH
ENV PATH=/home/litecrewai/.local/bin:$PATH

# Switch to non-root user
USER litecrewai
WORKDIR /app

# Copy application code
COPY --chown=litecrewai:litecrewai ./litecrew-langchain /app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]