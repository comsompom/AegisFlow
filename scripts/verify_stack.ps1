# Verify AegisFlow backend and (optionally) that the server responds.
# Run from repo root. Ensure backend deps are installed: pip install -r backend\requirements.txt

$ErrorActionPreference = "Stop"
$root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
$backendDir = Join-Path $root "backend"

Write-Host "=== Verify AegisFlow stack ===" -ForegroundColor Cyan

# 1. Backend imports
Push-Location $backendDir
try {
    $venvActivate = Join-Path $backendDir "venv\Scripts\Activate.ps1"
    if (Test-Path $venvActivate) { & $venvActivate }
    python -c "from app.main import app; print('Backend imports: OK')"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Install deps: pip install -r backend\requirements.txt" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Backend imports: OK" -ForegroundColor Green
} finally {
    Pop-Location
}

# 2. If backend is already running, hit health
try {
    $r = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get -TimeoutSec 2 -ErrorAction Stop
    Write-Host "Backend /health: $($r.status)" -ForegroundColor Green
} catch {
    Write-Host "Backend not running. Start it: cd backend; uvicorn app.main:app --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "To deploy on Solana Devnet: install Rust, Solana CLI, Anchor CLI, then run .\scripts\deploy_solana_devnet.ps1" -ForegroundColor Cyan
