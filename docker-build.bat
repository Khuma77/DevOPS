@echo off
REM Docker build script for Agro Shop (Windows)

echo 🐳 Building Agro Shop Docker images...

REM Build development image
echo 📦 Building development image...
docker build -t agro-shop:dev .

REM Build production image
echo 🚀 Building production image...
docker build -f Dockerfile.production -t agro-shop:prod .

REM Build with version tag
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "VERSION=%dt:~0,8%-%dt:~8,6%"
echo 🏷️ Tagging with version: %VERSION%
docker tag agro-shop:prod agro-shop:%VERSION%

echo ✅ Build completed!
echo.
echo Available images:
docker images | findstr agro-shop

echo.
echo 🚀 To run development:
echo docker run -p 5000:5000 agro-shop:dev
echo.
echo 🚀 To run production:
echo docker run -p 5000:5000 agro-shop:prod
echo.
echo 🚀 To run with monitoring:
echo docker-compose up -d

pause