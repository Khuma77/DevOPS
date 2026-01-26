@echo off
REM Docker run script for Agro Shop (Windows)

echo 🐳 Agro Shop Docker Management
echo ================================
echo.
echo Choose an option:
echo 1. Run Development (with hot reload)
echo 2. Run Production (optimized)
echo 3. Build images
echo 4. Stop all containers
echo 5. View logs
echo 6. Clean up (remove containers and images)
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo 🚀 Starting development environment...
    docker-compose -f docker-compose.dev.yml up -d
    echo.
    echo ✅ Development environment started!
    echo 📱 App: http://localhost:5000
    echo 📊 Grafana: http://localhost:3000 (admin/admin123)
    echo 📈 Prometheus: http://localhost:9090
    goto end
)

if "%choice%"=="2" (
    echo 🚀 Starting production environment...
    docker-compose up -d
    echo.
    echo ✅ Production environment started!
    echo 📱 App: http://localhost:5000
    echo 📊 Grafana: http://localhost:3000 (admin/admin123)
    echo 📈 Prometheus: http://localhost:9090
    goto end
)

if "%choice%"=="3" (
    echo 🔨 Building Docker images...
    call docker-build.bat
    goto end
)

if "%choice%"=="4" (
    echo 🛑 Stopping all containers...
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    echo ✅ All containers stopped!
    goto end
)

if "%choice%"=="5" (
    echo 📋 Viewing logs...
    echo Choose service:
    echo 1. Agro Shop App
    echo 2. Prometheus
    echo 3. Grafana
    echo 4. Loki
    echo.
    set /p service="Enter choice (1-4): "
    
    if "%service%"=="1" docker-compose logs -f agro-shop
    if "%service%"=="2" docker-compose logs -f prometheus
    if "%service%"=="3" docker-compose logs -f grafana
    if "%service%"=="4" docker-compose logs -f loki
    goto end
)

if "%choice%"=="6" (
    echo 🧹 Cleaning up...
    docker-compose down -v --rmi all
    docker-compose -f docker-compose.dev.yml down -v --rmi all
    docker system prune -f
    echo ✅ Cleanup completed!
    goto end
)

echo ❌ Invalid choice!

:end
echo.
echo Press any key to exit...
pause >nul