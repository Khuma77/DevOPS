# 🐳 Docker Setup Guide - Agro Shop

## 📦 Container Registry Options

### Option 1: GitHub Container Registry (Recommended - Free)
```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/khuma77/agro-shop:prod-latest

# Run with GitHub Container Registry
docker-compose -f docker-compose.ghcr.yml up -d
```

### Option 2: Docker Hub (Requires credentials)
```bash
# Pull from Docker Hub (if configured)
docker pull your-username/agro-shop:prod-latest

# Run with Docker Hub
docker-compose up -d
```

### Option 3: Local Build (No registry needed)
```bash
# Build locally
docker build -f Dockerfile.production -t agro-shop:local .

# Run locally built image
docker run -p 5000:5000 agro-shop:local
```

## 🚀 Quick Start

### 1. GitHub Container Registry (No Docker Hub needed)
```bash
# Clone repository
git clone https://github.com/Khuma77/DevOPS.git
cd DevOPS

# Create necessary directories
mkdir -p logs data

# Run with GitHub Container Registry
docker-compose -f docker-compose.ghcr.yml up -d

# Check status
docker-compose -f docker-compose.ghcr.yml ps
```

### 2. Local Development
```bash
# Build and run development version
docker-compose -f docker-compose.dev.yml up -d

# Or build locally
docker build -t agro-shop:dev .
docker run -p 5000:5000 -v $(pwd)/logs:/app/logs agro-shop:dev
```

## 🔧 Configuration

### Environment Variables
```bash
# Set Grafana password
export GRAFANA_PASSWORD=your-secure-password

# Set image tag (optional)
export IMAGE_TAG=prod-latest
```

### Docker Compose Files
- `docker-compose.yml` - Production with Docker Hub
- `docker-compose.ghcr.yml` - Production with GitHub Container Registry
- `docker-compose.dev.yml` - Development with hot reload

## 📊 Access URLs

After running docker-compose:

- **Application**: http://localhost:5000
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **API Docs**: http://localhost:5000/api/v1/
- **Health Check**: http://localhost:5000/health

## 🔍 Troubleshooting

### 1. Image Pull Issues
```bash
# If GitHub Container Registry fails
docker login ghcr.io -u your-github-username

# If Docker Hub fails
docker login -u your-dockerhub-username

# Build locally instead
docker build -f Dockerfile.production -t agro-shop:local .
```

### 2. Permission Issues
```bash
# Fix log directory permissions
sudo chown -R $USER:$USER logs/
chmod 755 logs/
```

### 3. Port Conflicts
```bash
# Check what's using ports
netstat -tulpn | grep :5000
netstat -tulpn | grep :3000

# Stop conflicting services
sudo systemctl stop apache2  # if using port 80
sudo systemctl stop nginx    # if using port 80
```

### 4. Container Health Check
```bash
# Check container status
docker-compose -f docker-compose.ghcr.yml ps

# View logs
docker-compose -f docker-compose.ghcr.yml logs agro-shop

# Restart services
docker-compose -f docker-compose.ghcr.yml restart agro-shop
```

## 🔄 Updates

### Pull Latest Images
```bash
# GitHub Container Registry
docker-compose -f docker-compose.ghcr.yml pull
docker-compose -f docker-compose.ghcr.yml up -d

# Docker Hub
docker-compose pull
docker-compose up -d
```

### Rollback
```bash
# Use specific version
docker-compose -f docker-compose.ghcr.yml down
export IMAGE_TAG=prod-abc123  # previous working version
docker-compose -f docker-compose.ghcr.yml up -d
```

## 📝 Notes

- **GitHub Container Registry** is free and doesn't require Docker Hub credentials
- **Images are automatically built** by GitHub Actions on every push
- **Public images** are available at: https://github.com/Khuma77/DevOPS/pkgs/container/agro-shop
- **Monitoring stack** includes Prometheus, Grafana, and Loki
- **Production setup** includes Nginx load balancer and Redis caching

## 🆘 Support

If you encounter issues:

1. Check GitHub Actions logs: https://github.com/Khuma77/DevOPS/actions
2. View container logs: `docker-compose logs`
3. Check image availability: https://github.com/Khuma77/DevOPS/pkgs/container/agro-shop
4. Build locally as fallback: `docker build -f Dockerfile.production -t agro-shop:local .`