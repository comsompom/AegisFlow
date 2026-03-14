# Run this script as Administrator (right-click PowerShell -> Run as administrator).
# Run ONCE to install platform-tools so "anchor build" works in normal terminals.
# Use this if you already ran install_solana_admin.ps1 but still get error 1314.
# Run from repo root:  cd C:\Users\obourdo\AegisFlow  then  .\scripts\install_platform_tools_admin.ps1

$ErrorActionPreference = "Continue"
$repoRoot = Split-Path -Parent $PSScriptRoot
$contractsDir = Join-Path $repoRoot "contracts-solana"

# Find Solana/Agave bin (cargo-build-sbf required for anchor build). Check several locations.
$solanaPath = $null
$candidates = @(
    "$env:USERPROFILE\.local\share\solana\install\active_release\bin",
    "$env:LOCALAPPDATA\solana\solana-release\bin"
)
foreach ($c in $candidates) {
    if (Test-Path (Join-Path $c "cargo-build-sbf.exe")) { $solanaPath = $c; break }
}
# If active_release missing (symlink failed), look for versioned folder under install
if (-not $solanaPath) {
    $installDir = "$env:USERPROFILE\.local\share\solana\install"
    if (Test-Path $installDir) {
        foreach ($dir in (Get-ChildItem -Path $installDir -Directory -ErrorAction SilentlyContinue)) {
            $binPath = Join-Path $dir.FullName "bin"
            if (Test-Path (Join-Path $binPath "cargo-build-sbf.exe")) { $solanaPath = $binPath; break }
        }
    }
}
if (-not $solanaPath) {
    Write-Host "Solana (cargo-build-sbf) not found. Tried:" -ForegroundColor Red
    $candidates | ForEach-Object { Write-Host "  $_" }
    Write-Host "Run install_solana_admin.ps1 first, or extract solana-release to $env:LOCALAPPDATA\solana\." -ForegroundColor Red
    exit 1
}
Write-Host "Using Solana bin: $solanaPath" -ForegroundColor Gray
if (-not (Test-Path (Join-Path $contractsDir "Anchor.toml"))) {
    Write-Host "Not found: $contractsDir. Run from repo root." -ForegroundColor Red
    exit 1
}

$env:PATH = "$solanaPath;$env:PATH"
Write-Host "Running anchor build (installs platform-tools with admin rights)..." -ForegroundColor Cyan
Push-Location $contractsDir
try {
    & anchor build 2>&1 | Out-Host
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Done. In a NEW normal terminal run:  cd `"$repoRoot`"; .\scripts\deploy_solana_devnet.ps1" -ForegroundColor Green
    } else {
        Write-Host "Build exited with $LASTEXITCODE. Check output above." -ForegroundColor Yellow
    }
} finally {
    Pop-Location
}
