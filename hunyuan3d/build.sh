#!/bin/bash
# Build script for Hunyuan3D-2 Docker image

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="${IMAGE_NAME:-hunyuan3d}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-}"
PUSH_IMAGE="${PUSH_IMAGE:-false}"

echo -e "${GREEN}=== Hunyuan3D-2 Docker Image Builder ===${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: Git is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker found: $(docker --version)${NC}"
echo -e "${GREEN}✓ Git found: $(git --version)${NC}"
echo ""

# Clone repository if not exists
REPO_DIR="Hunyuan3D-2"
if [ ! -d "$REPO_DIR" ]; then
    echo -e "${YELLOW}Cloning Hunyuan3D-2 repository...${NC}"
    git clone https://github.com/Tencent-Hunyuan/Hunyuan3D-2.git
    echo -e "${GREEN}✓ Repository cloned${NC}"
else
    echo -e "${YELLOW}Repository already exists, pulling latest changes...${NC}"
    cd "$REPO_DIR"
    git pull
    cd ..
    echo -e "${GREEN}✓ Repository updated${NC}"
fi
echo ""

# Copy Docker files
echo -e "${YELLOW}Copying Docker configuration files...${NC}"
cp Dockerfile "$REPO_DIR/"
cp entrypoint.sh "$REPO_DIR/"
cp .dockerignore "$REPO_DIR/"
chmod +x "$REPO_DIR/entrypoint.sh"
echo -e "${GREEN}✓ Files copied${NC}"
echo ""

# Build image
echo -e "${YELLOW}Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}${NC}"
echo "This may take 15-30 minutes depending on your internet connection..."
echo ""

cd "$REPO_DIR"
docker build \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -t "${IMAGE_NAME}:${IMAGE_TAG}" \
    -f Dockerfile \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Image built successfully: ${IMAGE_NAME}:${IMAGE_TAG}${NC}"
    
    # Show image size
    IMAGE_SIZE=$(docker images "${IMAGE_NAME}:${IMAGE_TAG}" --format "{{.Size}}")
    echo -e "${GREEN}  Image size: ${IMAGE_SIZE}${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi
echo ""

# Tag for registry if specified
if [ -n "$REGISTRY" ]; then
    echo -e "${YELLOW}Tagging image for registry: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}${NC}"
    docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    echo -e "${GREEN}✓ Image tagged${NC}"
    echo ""
fi

# Push to registry if requested
if [ "$PUSH_IMAGE" = "true" ] && [ -n "$REGISTRY" ]; then
    echo -e "${YELLOW}Pushing image to registry...${NC}"
    docker push "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Image pushed successfully${NC}"
    else
        echo -e "${RED}✗ Push failed${NC}"
        exit 1
    fi
    echo ""
fi

# Security scan (if trivy is installed)
if command -v trivy &> /dev/null; then
    echo -e "${YELLOW}Running security scan with Trivy...${NC}"
    trivy image --severity HIGH,CRITICAL "${IMAGE_NAME}:${IMAGE_TAG}"
    echo ""
fi

# Summary
echo -e "${GREEN}=== Build Summary ===${NC}"
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "Size: ${IMAGE_SIZE}"
if [ -n "$REGISTRY" ]; then
    echo "Registry: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
fi
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Test the image:"
echo "   docker run --gpus all -p 7860:7860 ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "2. Or use docker-compose:"
echo "   docker-compose up -d"
echo ""
echo "3. For Kubernetes deployment:"
echo "   kubectl apply -f kubernetes/deployment.yaml"
echo ""
echo -e "${GREEN}Build complete!${NC}"
