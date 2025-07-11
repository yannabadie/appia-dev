@echo off
REM JARVYS_AI Windows Deployment Script

echo Starting JARVYS_AI Windows Deployment...

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

REM Check for .env file
if not exist .env (
    echo Creating .env file from template...
    copy .env.template .env
    echo.
    echo IMPORTANT: Please edit .env file with your API keys before continuing.
    echo Press any key when you have updated the .env file...
    pause
)

REM Build and run JARVYS_AI
echo Building JARVYS_AI Docker image...
docker build -f Dockerfile.jarvys_ai -t jarvys_ai:latest .

if %errorlevel% neq 0 (
    echo Error: Docker build failed.
    pause
    exit /b 1
)

echo Starting JARVYS_AI...
docker-compose -f docker-compose.windows.yml up -d

if %errorlevel% neq 0 (
    echo Error: Failed to start JARVYS_AI.
    pause
    exit /b 1
)

echo.
echo ✅ JARVYS_AI deployed successfully!
echo 🌐 Web interface: http://localhost:8000
echo 🎤 Voice interface will be available on your audio devices
echo 📝 Check logs: docker-compose -f docker-compose.windows.yml logs -f
echo.
pause
