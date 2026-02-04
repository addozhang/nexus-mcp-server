# Dockerfile for Nexus MCP Server
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install dependencies directly (no venv needed in container)
RUN pip install --upgrade pip && \
    pip install -e .

# Expose HTTP port
EXPOSE 8000

# Environment variables for configuration
ENV NEXUS_MCP_HOST=0.0.0.0
ENV NEXUS_MCP_PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command: run the MCP server
CMD ["python", "-m", "nexus_mcp"]
