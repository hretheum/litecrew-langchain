# Multi-stage build for optimized image
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 litecrewai && \
    mkdir -p /app /data /logs /config && \
    chown -R litecrewai:litecrewai /app /data /logs /config

# Copy installed packages from builder
COPY --from=builder /root/.local /home/litecrewai/.local

# Set working directory
WORKDIR /app

# Copy entire application (src, setup.py, etc.)
COPY --chown=litecrewai:litecrewai . /app/

# Install the package in development mode
RUN pip install --user -e .

# Update PATH
ENV PATH=/home/litecrewai/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Switch to non-root user
USER litecrewai

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default command
CMD ["python", "run_server.py"]