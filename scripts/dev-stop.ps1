# PayPath Local Development Environment Stopper
# Usage: .\scripts\dev-stop.ps1

$ErrorActionPreference = "SilentlyContinue"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " PAYPATH - STOPPING LOCAL PROJECT PROCESSES" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Stop Backend (Port 8000)
$backendConn = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($backendConn) {
    $pids = $backendConn | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($p in $pids) {
        if ($p -gt 0) {
            Write-Host "  Stopping backend process on port 8000 (PID: $p)..." -ForegroundColor Yellow
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Host "  Backend stopped." -ForegroundColor Green
} else {
    Write-Host "  No active backend process detected on port 8000." -ForegroundColor Gray
}

# Stop Frontend (Port 5173)
$frontendConn = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if ($frontendConn) {
    $pids = $frontendConn | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($p in $pids) {
        if ($p -gt 0) {
            Write-Host "  Stopping frontend process on port 5173 (PID: $p)..." -ForegroundColor Yellow
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Host "  Frontend stopped." -ForegroundColor Green
} else {
    Write-Host "  No active frontend process detected on port 5173." -ForegroundColor Gray
}

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " PAYPATH PROJECT PROCESSES STOPPED SAFELY" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
