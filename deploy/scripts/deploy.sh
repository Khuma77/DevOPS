#!/bin/bash

# Production deployment script for Agro Shop

set -e  # Exit on any error

echo "🚀 Starting Agro Shop deployment..."

# Configuration
DOCKER_HUB_USERNAME=${DOCKER_HUB_USERNAME:-"your-username"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}
GRAFANA_PASSWORD=${GRAFANA_PASSWORD:-"admin123"}

# Export environment variables
export DOCKER_HUB_USERNAME
export IMAGE_TAG
export GRAFANA_PASSWORD

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data monitoring/grafana/dashboards deploy/nginx/ssl

# Pull latest images
echo "📥 Pulling Docker images..."
docker-compose -f deploy/docker-compose.prod.yml pull

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f deploy/docker-compose.prod.yml down

# Start new containers
echo "🚀 Starting new containers..."
docker-compose -f deploy/docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Health check
echo "🔍 Running health checks..."
for i in {1..10}; do
    if curl -f http://localhost/health > /dev/null 2>&1; then
        echo "✅ Application is healthy!"
        break
    else
        echo "⏳ Waiting for application... (attempt $i/10)"
        sleep 10
    fi
    
    if [ $i -eq 10 ]; then
        echo "❌ Health check failed!"
        docker-compose -f deploy/docker-compose.prod.yml logs agro-shop
        exit 1
    fi
done

# Test API endpoints
echo "🧪 Testing API endpoints..."
curl -f http://localhost/api/v1/products || echo "⚠️ Products API test failed"
curl -f http://localhost/api/v1/stats || echo "⚠️ Stats API test failed"

# Show running containers
echo "📊 Running containers:"
docker-compose -f deploy/docker-compose.prod.yml ps

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Application: http://localhost"
echo "📊 Grafana: http://localhost:3000 (admin/${GRAFANA_PASSWORD})"
echo "📈 Prometheus: http://localhost:9090"
echo "📋 Logs: docker-compose -f deploy/docker-compose.prod.yml logs -f"