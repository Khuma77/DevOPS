#!/bin/bash

# Rollback script for Agro Shop

set -e

echo "🔄 Starting rollback process..."

# Get previous image tag
PREVIOUS_TAG=${1:-"previous"}

if [ "$PREVIOUS_TAG" = "previous" ]; then
    echo "❌ Please provide the previous image tag to rollback to"
    echo "Usage: ./rollback.sh <image-tag>"
    echo "Example: ./rollback.sh prod-abc123"
    exit 1
fi

echo "🔄 Rolling back to image tag: $PREVIOUS_TAG"

# Update environment variables
export DOCKER_HUB_USERNAME=${DOCKER_HUB_USERNAME:-"your-username"}
export IMAGE_TAG=$PREVIOUS_TAG
export GRAFANA_PASSWORD=${GRAFANA_PASSWORD:-"admin123"}

# Pull the previous image
echo "📥 Pulling previous image..."
docker pull ${DOCKER_HUB_USERNAME}/agro-shop:${PREVIOUS_TAG}

# Stop current containers
echo "🛑 Stopping current containers..."
docker-compose -f deploy/docker-compose.prod.yml down

# Start with previous image
echo "🚀 Starting containers with previous image..."
docker-compose -f deploy/docker-compose.prod.yml up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Health check
echo "🔍 Running health checks..."
for i in {1..5}; do
    if curl -f http://localhost/health > /dev/null 2>&1; then
        echo "✅ Rollback successful! Application is healthy."
        break
    else
        echo "⏳ Waiting for application... (attempt $i/5)"
        sleep 10
    fi
    
    if [ $i -eq 5 ]; then
        echo "❌ Rollback health check failed!"
        docker-compose -f deploy/docker-compose.prod.yml logs agro-shop
        exit 1
    fi
done

echo "✅ Rollback completed successfully!"
echo "🌐 Application: http://localhost"