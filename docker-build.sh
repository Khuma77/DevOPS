#!/bin/bash

# Docker build script for Agro Shop

echo "🐳 Building Agro Shop Docker images..."

# Build development image
echo "📦 Building development image..."
docker build -t agro-shop:dev .

# Build production image
echo "🚀 Building production image..."
docker build -f Dockerfile.production -t agro-shop:prod .

# Build with version tag
VERSION=$(date +%Y%m%d-%H%M%S)
echo "🏷️ Tagging with version: $VERSION"
docker tag agro-shop:prod agro-shop:$VERSION

echo "✅ Build completed!"
echo ""
echo "Available images:"
docker images | grep agro-shop

echo ""
echo "🚀 To run development:"
echo "docker run -p 5000:5000 agro-shop:dev"
echo ""
echo "🚀 To run production:"
echo "docker run -p 5000:5000 agro-shop:prod"
echo ""
echo "🚀 To run with monitoring:"
echo "docker-compose up -d"