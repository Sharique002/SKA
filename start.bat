@echo off
REM Smart Knowledge Assistant - Docker Startup Script (Batch)

color 0A
echo.
echo ====================================
echo    SKA - Docker Quick Start
echo ====================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop first.
    echo.
    pause
    exit /b 1
)

echo Starting containers...
echo.
docker-compose up -d

timeout /t 3 /nobreak

color 0A
echo.
echo ====================================
echo    SUCCESS! SKA is running
echo ====================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:5000
echo.
echo Opening application in browser...
echo.

REM Open frontend in default browser
start http://localhost:3000

echo.
echo Useful commands:
echo   docker-compose logs     - View logs
echo   docker-compose down     - Stop application
echo.
pause
