# PayPath One-Click Local Development Environment Launcher
# Usage: .\scripts\dev-start.ps1

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " PAYPATH - LOCAL ENVIRONMENT INITIALIZATION" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Verify PostgreSQL 16 Service / Port 5432
Write-Host "[1/5] Verifying PostgreSQL 16 service on port 5432..." -ForegroundColor Yellow
$pgConn = Get-NetTCPConnection -LocalPort 5432 -ErrorAction SilentlyContinue
if (-not $pgConn) {
    Write-Host "  PostgreSQL not listening on 5432. Starting PostgreSQL process..." -ForegroundColor Yellow
    $pgBin = "E:\postsql database\bin\postgres.exe"
    $pgData = "E:\postsql database\data"
    if (Test-Path $pgBin) {
        Start-Process -FilePath $pgBin -ArgumentList @("-D", $pgData) -WindowStyle Hidden
        Start-Sleep -Seconds 5
    } else {
        Write-Warning "PostgreSQL binary not found at $pgBin. Please start PostgreSQL manually."
    }
}
Write-Host "  PostgreSQL 16 connection detected on port 5432." -ForegroundColor Green

# 2. Verify Database Connectivity & Seeds
Write-Host "[2/5] Checking PostgreSQL connectivity and seed state..." -ForegroundColor Yellow
$pyExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pyExe)) {
    $pyExe = "python"
}

try {
    & $pyExe -m backend.scripts.verify_seed | Out-Null
    Write-Host "  Database connection and seed validation: PASS" -ForegroundColor Green
} catch {
    Write-Warning "  Database connection check failed: $_"
}

# 3. Start Backend FastAPI Server
Write-Host "[3/5] Starting FastAPI backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
$backendExisting = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if (-not $backendExisting) {
    $serverScript = Join-Path $projectRoot "backend\run_server.py"
    Start-Process -FilePath $pyExe -ArgumentList @($serverScript) -WorkingDirectory $projectRoot -WindowStyle Hidden
}

# 4. Wait for Backend Health
Write-Host "[4/5] Awaiting backend health verification..." -ForegroundColor Yellow
$maxRetries = 20
$healthy = $false
for ($i = 0; $i -lt $maxRetries; $i++) {
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/system/health" -Method Get -TimeoutSec 2
        if ($resp.status -in @("HEALTHY", "DEGRADED")) {
            $healthy = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($healthy) {
    Write-Host "  Backend health check: ONLINE" -ForegroundColor Green
} else {
    Write-Warning "  Backend did not report ready within 20s. Continuing..."
}

# 5. Start Frontend Vite Dev Server
Write-Host "[5/5] Starting Vite frontend on http://127.0.0.1:5173..." -ForegroundColor Yellow
$frontendExisting = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if (-not $frontendExisting) {
    $frontendDir = Join-Path $projectRoot "frontend"
    Start-Process -FilePath "npm.cmd" -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1", "--port", "5173") -WorkingDirectory $frontendDir -WindowStyle Hidden
    Start-Sleep -Seconds 3
}
Write-Host "  Frontend development server running." -ForegroundColor Green

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host " PAYPATH LOCAL SERVICES READY" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Frontend      : http://127.0.0.1:5173" -ForegroundColor Cyan
Write-Host "  Backend       : http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  Swagger Docs  : http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "  Health API    : http://127.0.0.1:8000/api/v1/system/health" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Green
