# Deploy AegisFlow to Solana Devnet and verify.
# Prereqs: Rust, Solana CLI, Anchor CLI (see docs/DEPLOYMENT_CHECKLIST.md).
# Run from repo root: .\scripts\deploy_solana_devnet.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }

Write-Host "=== AegisFlow Solana Devnet deploy ===" -ForegroundColor Cyan
Write-Host ""

# 1. Check tools
$anchorOk = $false
$solanaOk = $false
try { $null = Get-Command anchor -ErrorAction Stop; $anchorOk = $true } catch {}
try { $null = Get-Command solana -ErrorAction Stop; $solanaOk = $true } catch {}

if (-not $solanaOk) {
    Write-Host "Solana CLI not found. Install: https://docs.solana.com/cli/install" -ForegroundColor Yellow
    Write-Host "On Windows you may need WSL (Ubuntu) and run: curl ... solana-install ... | bash" -ForegroundColor Yellow
    exit 1
}
if (-not $anchorOk) {
    Write-Host "Anchor CLI not found. Install: https://www.anchor-lang.com/docs/installation" -ForegroundColor Yellow
    exit 1
}

Write-Host "Solana: $(solana --version)"
Write-Host "Anchor: $(anchor --version)"
Write-Host ""

# 2. Build and deploy program
Push-Location (Join-Path $root "contracts-solana")
try {
    solana config set --url devnet
    Write-Host "Building Anchor program..." -ForegroundColor Cyan
    anchor build
    if ($LASTEXITCODE -ne 0) { throw "anchor build failed" }
    $programId = (anchor keys list 2>$null) -replace '.*\s+', ''
    if ($programId) { Write-Host "Program ID: $programId" -ForegroundColor Green }
    Write-Host "Deploying to Devnet..." -ForegroundColor Cyan
    anchor deploy --provider.cluster devnet
    if ($LASTEXITCODE -ne 0) { throw "anchor deploy failed" }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "Deploy done. Next: set SOLANA_PROGRAM_ID in backend\.env and run init." -ForegroundColor Green
Write-Host "  cd backend"
Write-Host "  python -m scripts.init_solana_program"
Write-Host "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
Write-Host ""
