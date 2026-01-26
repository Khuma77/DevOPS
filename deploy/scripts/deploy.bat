@echo off
REM Production deployment script for Agro Shop (Windows)

echo 🚀 Starting Agro Shop deployment...

REM Configuration
set DOCKER_HUB_USERNAME=%DOCKER_HUB_USERNAME%
if "%DOCKER_HUB_USERNAME%"=="" set DOCKER_HUB_USERNAME=your-username

set IMAGE_TAG=%IMAGE_TAG%
if "%IMAGE_TAG%"=="" set IMAGE_TAG=latest

set GRAFANA_PASSWORD=%GRAFANA_PASSWORD%
if "%GRAFANA_PASSWORD%"=="" set GRAFANA_PASSWORD=admin123

REM Create necessary directories
echo 📁 Creating directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "monitoring\grafana\dashboards" mkdir monitoring\grafana\dashboards
if not exist "deploy\nginx\ssl" mkdir deploy\nginx\ssl

REM Pull latest images
echo 📥 Pulling Docker images...
docker-compose -f deploy/docker-compose.prod.yml pull

REM Stop existing containers
echo 🛑 Stopping existing containers...
docker-compose -f deploy/docker-compose.prod.yml down

REM Start new containers
echo 🚀 Starting new containers...
docker-compose -f deploy/docker-compose.prod.yml up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak > nul

REM Health check
echo 🔍 Running health checks...
for /l %%i in (1,1,10) do (
    curl -f http://localhost/health > nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Application is healthy!
        goto :health_success
    ) else (
        echo ⏳ Waiting for application... (attempt %%i/10)
        timeout /t 10 /nobreak > nul
    )
)

echo ❌ Health check failed!
docker-compose -f deploy/docker-compose.prod.yml logs agro-shop
exit /b 1

:health_success

REM Test API endpoints
echo 🧪 Testing API endpoints...
curl -f http://localhost/api/v1/products || echo ⚠️ Products API test failed
curl -f http://localhost/api/v1/stats || echo ⚠️ Stats API test failed

REM Show running containers
echo 📊 Running containers:
docker-compose -f deploy/docker-compose.prod.yml ps

echo ✅ Deployment completed successfully!
echo.
echo 🌐 Application: http://localhost
echo 📊 Grafana: http://localhost:3000 (admin/%GRAFANA_PASSWORD%)
echo 📈 Prometheus: http://localhost:9090
echo 📋 Logs: docker-compose -f deploy/docker-compose.prod.yml logs -f

pause