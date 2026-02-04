#!/bin/bash
# Build multi-architecture Docker images for Nexus MCP Server

set -e

# Configuration
IMAGE_NAME="${IMAGE_NAME:-addozhang/nexus-mcp-server}"
VERSION="${VERSION:-latest}"
PLATFORMS="linux/amd64,linux/arm64"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Building Nexus MCP Server Docker image${NC}"
echo -e "${BLUE}Image: ${IMAGE_NAME}:${VERSION}${NC}"
echo -e "${BLUE}Platforms: ${PLATFORMS}${NC}"
echo ""

# Check if buildx is available
if ! docker buildx version > /dev/null 2>&1; then
    echo -e "${YELLOW}Docker buildx not found. Installing...${NC}"
    docker buildx create --use
fi

# Create buildx builder if it doesn't exist
BUILDER_NAME="nexus-mcp-builder"
if ! docker buildx ls | grep -q "$BUILDER_NAME"; then
    echo -e "${YELLOW}Creating buildx builder: ${BUILDER_NAME}${NC}"
    docker buildx create --name "$BUILDER_NAME" --use
else
    echo -e "${GREEN}Using existing builder: ${BUILDER_NAME}${NC}"
    docker buildx use "$BUILDER_NAME"
fi

# Bootstrap builder
docker buildx inspect --bootstrap

# Build and push multi-arch image
echo -e "${BLUE}Building multi-architecture image...${NC}"
docker buildx build \
    --platform "$PLATFORMS" \
    --tag "${IMAGE_NAME}:${VERSION}" \
    --tag "${IMAGE_NAME}:latest" \
    --push \
    .

echo ""
echo -e "${GREEN}✅ Build completed successfully!${NC}"
echo -e "${GREEN}Image pushed: ${IMAGE_NAME}:${VERSION}${NC}"
echo -e "${GREEN}Image pushed: ${IMAGE_NAME}:latest${NC}"
echo ""
echo -e "${BLUE}To run the image:${NC}"
echo "  docker run -p 8000:8000 ${IMAGE_NAME}:${VERSION}"
