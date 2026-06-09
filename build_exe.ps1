$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$AppEntry = Join-Path $ProjectRoot "duipai_gui.py"
$Requirements = Join-Path $ProjectRoot "requirements.txt"
$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build"
$SpecPath = Join-Path $ProjectRoot "VisualDuipai.spec"
$ExePath = Join-Path $DistDir "VisualDuipai.exe"

function Remove-PathWithRetry {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [int]$Attempts = 5,
        [int]$SleepMilliseconds = 500
    )

    if (-not (Test-Path $Path)) {
        return
    }

    for ($Attempt = 1; $Attempt -le $Attempts; $Attempt++) {
        try {
            Remove-Item $Path -Recurse -Force
            return
        }
        catch {
            if ($Attempt -eq $Attempts) {
                throw
            }

            Write-Host "Remove failed for $Path (attempt $Attempt/$Attempts). Retrying..." -ForegroundColor Yellow
            Start-Sleep -Milliseconds $SleepMilliseconds
        }
    }
}

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

Write-Host "Stopping any running VisualDuipai process..." -ForegroundColor Cyan
$RunningProcesses = Get-Process -Name "VisualDuipai" -ErrorAction SilentlyContinue
if ($RunningProcesses) {
    Write-Host "Stopping $($RunningProcesses.Count) running VisualDuipai process(es)..." -ForegroundColor Yellow
    $RunningProcesses | Stop-Process -Force
}
else {
    Write-Host "No running VisualDuipai process found."
}

Write-Host "Cleaning old build outputs..." -ForegroundColor Cyan
Remove-PathWithRetry $BuildDir
Remove-PathWithRetry $DistDir
Remove-PathWithRetry $SpecPath

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
