# Docker Deployment Guide

## Quick Start

### Local Development

1. **Build locally:**
   ```bash
   ./build-local.sh
   ```

2. **Run with docker-compose:**
   ```bash
   docker-compose up
   ```

3. **Access the server:**
   - Health check: http://localhost:8000/health
   - SSE endpoint: http://localhost:8000/sse

### Production Deployment

1. **Build multi-architecture images:**
   ```bash
   # Set your Docker Hub username
   export IMAGE_NAME=yourusername/nexus-mcp-server
   export VERSION=1.0.0
   
   ./build-docker.sh
   ```

2. **Deploy with docker-compose:**
   ```bash
   docker-compose up -d
   ```

## Build Scripts

### `build-local.sh`
Builds a single-architecture image for local testing:
- No push to registry
- Fast build
- Tagged as `nexus-mcp-server:latest` and `nexus-mcp-server:dev`

**Environment variables:**
- `IMAGE_NAME`: Docker image name (default: `nexus-mcp-server`)
- `VERSION`: Image tag (default: `dev`)
- `PYTHON_VERSION`: Python base image version (default: `3.11`)

**Example:**
```bash
# Build with default Python 3.11
./build-local.sh

# Build with Python 3.12
export PYTHON_VERSION=3.12
./build-local.sh

# Build with custom image name
export IMAGE_NAME=my-nexus-mcp
export VERSION=test
./build-local.sh
```

### `build-docker.sh`
Builds multi-architecture images and pushes to Docker Hub:
- Supports: `linux/amd64`, `linux/arm64`
- Pushes to registry
- Uses Docker buildx

**Environment variables:**
- `IMAGE_NAME`: Docker image name (default: `addozhang/nexus-mcp-server`)
- `VERSION`: Image tag (default: `latest`)
- `PYTHON_VERSION`: Python base image version (default: `3.11`)

**Example:**
```bash
# Build with default Python 3.11
export IMAGE_NAME=myorg/nexus-mcp-server
export VERSION=1.2.3
./build-docker.sh

# Build with Python 3.12
export IMAGE_NAME=myorg/nexus-mcp-server
export VERSION=1.2.3
export PYTHON_VERSION=3.12
./build-docker.sh
```

## Docker Compose Files

### `docker-compose.yml`
Production configuration:
- Uses pre-built image from Docker Hub
- Includes Nginx reverse proxy
- SSL/TLS support
- Health checks
- Resource limits
- Restart policies
- Better logging

**Setup:**
1. Create SSL certificates:
   ```bash
   mkdir -p ssl
   # Copy your cert.pem and key.pem to ssl/
   ```

2. Update `nginx.conf`:
   - Change `server_name` to your domain
   - Adjust SSL settings if needed

3. Deploy:
   ```bash
   docker-compose up -d
   ```

### `docker-compose.dev.yml`
Development/testing configuration:
- Builds image locally
- Exposes port 8000
- Includes health check
- Resource limits configured
- Suitable for local testing

**Usage:**
```bash
# Start
docker-compose -f docker-compose.dev.yml up

# Start in background
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop
docker-compose -f docker-compose.dev.yml down
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXUS_MCP_HOST` | Host to bind to | `0.0.0.0` |
| `NEXUS_MCP_PORT` | Port to listen on | `8000` |

### Credentials

**Important:** Do NOT hardcode credentials in docker-compose!

Credentials should be passed per-request via HTTP headers:
- `X-Nexus-Url`
- `X-Nexus-Username`
- `X-Nexus-Password`
- `X-Nexus-Verify-SSL` (optional, set to `false` for self-signed certs)

## Health Check

The server provides a health check endpoint:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "nexus-mcp",
  "version": "0.1.0"
}
```

## Resource Limits

### Development (docker-compose.dev.yml)
- CPU: 0.25-1.0 cores
- Memory: 128MB-512MB

### Production (docker-compose.yml)
- CPU: 0.5-2.0 cores
- Memory: 256MB-1GB

Adjust based on your workload and server capacity.

## Networking

### Port Mapping
- **Development:** `8000:8000` (direct access)
- **Production:** `443:443`, `80:80` (via Nginx)

### Internal Network
All services communicate via `nexus-mcp-network` bridge network.

## Logs

View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f nexus-mcp-server

# Last 100 lines
docker-compose logs --tail=100
```

Log configuration:
- Max size: 10MB (dev), 50MB (prod)
- Max files: 3 (dev), 5 (prod)
- Driver: json-file

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs nexus-mcp-server

# Check container status
docker ps -a

# Inspect container
docker inspect nexus-mcp-server
```

### Health check failing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Check if port is accessible
netstat -tulpn | grep 8000
```

### SSL/TLS issues (production)
```bash
# Verify nginx config
docker-compose exec nginx nginx -t

# Check SSL certificate
openssl x509 -in ssl/cert.pem -text -noout
```

## Security Best Practices

1. **Never hardcode credentials** in docker-compose files
2. **Use SSL/TLS** in production (nginx reverse proxy)
3. **Limit resources** to prevent DoS
4. **Keep images updated** regularly
5. **Use secrets management** for production (Docker Secrets, Vault, etc.)
6. **Network isolation** - don't expose MCP server port directly

## Example: Claude Desktop with Docker

Update your Claude Desktop config (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "nexus": {
      "url": "http://localhost:8000/sse",
      "headers": {
        "X-Nexus-Url": "https://nexus.company.com",
        "X-Nexus-Username": "admin",
        "X-Nexus-Password": "secret123"
      }
    }
  }
}
```

For production with SSL:
```json
{
  "mcpServers": {
    "nexus": {
      "url": "https://nexus-mcp.example.com/sse",
      "headers": {
        "X-Nexus-Url": "https://nexus.company.com",
        "X-Nexus-Username": "admin",
        "X-Nexus-Password": "secret123"
      }
    }
  }
}
```
