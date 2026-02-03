# Dockerfile for Nexus MCP Server (Sandboxed Development)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Create virtual environment and install dependencies
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -e ".[dev]"

# Default command (can be overridden)
CMD ["/bin/bash"]
