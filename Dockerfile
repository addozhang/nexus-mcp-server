# Dockerfile for Nexus MCP Server (Sandboxed Development)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY tests/ ./tests/

# Install dependencies directly (no venv needed in container)
RUN pip install --upgrade pip && \
    pip install -e ".[dev]"

# Default command: run the MCP server
CMD ["python", "-m", "nexus_mcp"]
