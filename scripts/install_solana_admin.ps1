# Run this script as Administrator (right-click PowerShell -> Run as administrator).
# It installs Agave/Solana CLI and platform-tools so "anchor build" works on Windows.
# After it finishes, close this window, open a normal PowerShell, and run:
#   cd C:\Users\obourdo\AegisFlow
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
Write-Host "Install complete. Add Solana to PATH for this user:"
$solanaPath = "$env:USERPROFILE\.local\share\solana\install\active_release\bin"
if (Test-Path $solanaPath) {
    Write-Host "  $solanaPath"
    Write-Host "Add the above to your user PATH, or run:  `$env:PATH = `"$solanaPath;`$env:PATH`""
} else {
    Write-Host "  Check Agave docs for install path: https://docs.anza.xyz/cli/install/"
}
Write-Host ""
Write-Host "Then in a NEW (normal) terminal run:  cd AegisFlow; .\scripts\deploy_solana_devnet.ps1"
