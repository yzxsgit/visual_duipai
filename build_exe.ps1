$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$AppEntry = Join-Path $ProjectRoot "duipai_gui.py"
$Requirements = Join-Path $ProjectRoot "requirements.txt"
$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build"
$ExePath = Join-Path $DistDir "VisualDuipai.exe"

Write-Host "VisualDuipai Windows EXE build" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot"

if (-not (Test-Path $AppEntry)) {
    Write-Error "duipai_gui.py not found. Please run this script from the visual_duipai project."
}

if (-not (Test-Path $Requirements)) {
    Write-Error "requirements.txt not found."
}

Write-Host "Checking Python..." -ForegroundColor Cyan
python --version

Write-Host "Installing runtime dependencies..." -ForegroundColor Cyan
python -m pip install -r $Requirements

Write-Host "Installing PyInstaller..." -ForegroundColor Cyan
python -m pip install pyinstaller

Write-Host "Cleaning old build outputs..." -ForegroundColor Cyan
if (Test-Path $BuildDir) {
    Remove-Item $BuildDir -Recurse -Force
}
if (Test-Path $DistDir) {
    Remove-Item $DistDir -Recurse -Force
}
if (Test-Path (Join-Path $ProjectRoot "VisualDuipai.spec")) {
    Remove-Item (Join-Path $ProjectRoot "VisualDuipai.spec") -Force
}

Write-Host "Building VisualDuipai.exe..." -ForegroundColor Cyan
python -m PyInstaller `
    --noconsole `
    --onefile `
    --name VisualDuipai `
    --collect-all tkinterdnd2 `
    duipai_gui.py

if (-not (Test-Path $ExePath)) {
    Write-Error "Build failed: $ExePath was not created. If PyInstaller reported that --collect-all is unsupported, upgrade it with: python -m pip install --upgrade pyinstaller"
}

Write-Host "Build succeeded!" -ForegroundColor Green
Write-Host "Output: $ExePath" -ForegroundColor Green
Write-Host "Note: VisualDuipai.exe still requires g++ to be installed and available in PATH when running duipai." -ForegroundColor Yellow
