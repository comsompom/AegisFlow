# Run this script as Administrator (right-click PowerShell -> Run as administrator).
# It installs Agave/Solana CLI and platform-tools so "anchor build" works on Windows.
# Run from your repo root, e.g.:  cd C:\Users\obourdo\AegisFlow  then  .\scripts\install_solana_admin.ps1
# After it finishes, close this window, open a normal PowerShell, cd to the same repo, and run:
#   .\scripts\deploy_solana_devnet.ps1

$ErrorActionPreference = "Stop"
$installer = "$env:LOCALAPPDATA\solana-install-tmp\agave-install-init.exe"
if (-not (Test-Path $installer)) {
    Write-Host "Downloading Agave installer..."
    New-Item -ItemType Directory -Force -Path (Split-Path $installer) | Out-Null
    $ProgressPreference = "SilentlyContinue"
    Invoke-WebRequest -Uri "https://github.com/anza-xyz/agave/releases/download/v3.1.10/agave-install-init-x86_64-pc-windows-msvc.exe" -OutFile $installer -UseBasicParsing
}
Write-Host "Running Agave installer (v3.1.10)..."
& $installer v3.1.10
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host ""

$solanaPath = "$env:USERPROFILE\.local\share\solana\install\active_release\bin"
# Refresh PATH in this session so we can run anchor/cargo-build-sbf
$env:PATH = "$solanaPath;$env:PATH"
$repoRoot = Split-Path -Parent $PSScriptRoot
$contractsDir = Join-Path $repoRoot "contracts-solana"

if ((Test-Path $solanaPath) -and (Test-Path (Join-Path $contractsDir "Anchor.toml"))) {
    Write-Host "Installing platform-tools (one-time, needs admin)... Run anchor build in this admin window." -ForegroundColor Cyan
    Push-Location $contractsDir
    try {
        & anchor build 2>&1 | Out-Host
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Platform-tools and build OK. You can now use a normal terminal to deploy." -ForegroundColor Green
        } else {
            Write-Host "Build had errors; platform-tools may still have been installed. Try deploy from a new terminal." -ForegroundColor Yellow
        }
    } finally {
        Pop-Location
    }
    Write-Host ""
} else {
    Write-Host "Solana bin path: $solanaPath" -ForegroundColor Gray
}

Write-Host "In a NEW (normal) terminal run:"
Write-Host "  cd `"$repoRoot`""
Write-Host "  .\scripts\deploy_solana_devnet.ps1"
