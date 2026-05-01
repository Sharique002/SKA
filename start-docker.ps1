#!/usr/bin/env powershell
# Smart Knowledge Assistant - Docker Startup Script
# cd d:\files\OneDrive\Desktop\SKA_01\ska_project
# .\start-docker.ps1
Write-Host "🚀 Starting SKA with Docker..." -ForegroundColor Green
Write-Host ""

# Check if Docker is running
$dockerStatus = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Start containers
Write-Host "📦 Starting containers..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Containers started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3

    Write-Host ""
    Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "🔌 Backend:  http://localhost:5000" -ForegroundColor Cyan
    Write-Host ""

    # Open links in default browser
    Write-Host "📂 Opening application in browser..." -ForegroundColor Green
    Start-Process "http://localhost:3000"

    Write-Host ""
    Write-Host "📊 View logs: docker-compose logs" -ForegroundColor Yellow
    Write-Host "🛑 Stop:      docker-compose down" -ForegroundColor Yellow
} else {
    Write-Host "❌ Failed to start containers" -ForegroundColor Red
    exit 1
}

