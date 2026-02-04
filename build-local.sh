#!/bin/bash
# Build Docker image locally for testing (single architecture)

set -e

# Configuration
IMAGE_NAME="${IMAGE_NAME:-nexus-mcp-server}"
VERSION="${VERSION:-dev}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Building Nexus MCP Server Docker image (local)${NC}"
echo -e "${BLUE}Image: ${IMAGE_NAME}:${VERSION}${NC}"
echo ""

# Build for current platform only
docker build \
    --tag "${IMAGE_NAME}:${VERSION}" \
    --tag "${IMAGE_NAME}:latest" \
    .

echo ""
echo -e "${GREEN}✅ Build completed successfully!${NC}"
echo -e "${GREEN}Image: ${IMAGE_NAME}:${VERSION}${NC}"
echo ""
echo -e "${BLUE}To run the image:${NC}"
echo "  docker run -p 8000:8000 ${IMAGE_NAME}:${VERSION}"
echo ""
echo -e "${BLUE}To test with docker-compose:${NC}"
echo "  docker-compose up"
