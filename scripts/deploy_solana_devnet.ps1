# Deploy AegisFlow to Solana Devnet and verify.
# Prereqs: Rust, Solana CLI, Anchor CLI (see docs/DEPLOYMENT_CHECKLIST.md).
# Run from repo root: .\scripts\deploy_solana_devnet.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }

# Prepend Solana/Agave bin so anchor build finds cargo-build-sbf and solana
$agaveBin = "$env:USERPROFILE\.local\share\solana\install\active_release\bin"
$solanaBin = "$env:LOCALAPPDATA\solana\solana-release\bin"
if (Test-Path (Join-Path $agaveBin "solana.exe")) { $env:PATH = "$agaveBin;$env:PATH" }
elseif (Test-Path (Join-Path $solanaBin "solana.exe")) { $env:PATH = "$solanaBin;$env:PATH" }

Write-Host "=== AegisFlow Solana Devnet deploy ===" -ForegroundColor Cyan
Write-Host ""

# 1. Check tools
$anchorOk = $false
$solanaOk = $false
try { $null = Get-Command anchor -ErrorAction Stop; $anchorOk = $true } catch {}
try { $null = Get-Command solana -ErrorAction Stop; $solanaOk = $true } catch {}

if (-not $solanaOk) {
    Write-Host "Solana CLI not found. Install: https://docs.solana.com/cli/install" -ForegroundColor Yellow
    Write-Host "Or extract solana-release to $env:LOCALAPPDATA\solana\ and re-run." -ForegroundColor Yellow
    Write-Host "On Windows, if anchor build fails with privilege error, use WSL (see docs/DEPLOY_WINDOWS.md)." -ForegroundColor Yellow
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
# Ensure HOME is set so cargo-build-sbf uses a valid cache path (Windows)
if (-not $env:HOME) { $env:HOME = $env:USERPROFILE }

Push-Location (Join-Path $root "contracts-solana")
try {
    solana config set --url devnet
    Write-Host "Building Anchor program..." -ForegroundColor Cyan
    $buildOut = & anchor build 2>&1
    $buildExit = $LASTEXITCODE
    $buildOut | Out-Host
    if ($buildExit -ne 0) {
        if ($buildOut -match "platform-tools|1314|privilege") {
            Write-Host ""
            Write-Host "*** Platform-tools install needs elevated rights on Windows. ***" -ForegroundColor Yellow
            Write-Host "Fix: Right-click PowerShell -> Run as administrator, then run:" -ForegroundColor Yellow
            Write-Host "  cd `"$root`"" -ForegroundColor White
            Write-Host "  .\scripts\install_solana_admin.ps1" -ForegroundColor White
            Write-Host "Then close that window, open a new normal terminal, and run this script again." -ForegroundColor Yellow
            Write-Host "Alternatively, build and deploy from WSL (see docs/DEPLOY_WINDOWS.md)." -ForegroundColor Yellow
        }
        throw "anchor build failed"
    }
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
