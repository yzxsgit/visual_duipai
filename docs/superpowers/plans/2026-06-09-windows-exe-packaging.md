# Windows EXE Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Windows-first PyInstaller packaging workflow that builds `dist/VisualDuipai.exe` from the existing visual duipai GUI.

**Architecture:** The packaging workflow is kept separate from the application code. `build_exe.ps1` performs environment checks, dependency installation, cleanup, PyInstaller execution, and output verification; `packaging/README.md` documents Windows usage and future macOS/Linux principles; `.gitignore` excludes generated build artifacts.

**Tech Stack:** PowerShell, Python, pip, PyInstaller, customtkinter, tkinterdnd2.

---

## File Structure

All paths are relative to repository root `D:/yzx/Documents/claude_code/duipai/visual_duipai`.

- Create: `build_exe.ps1`
  - Windows one-command build script for `dist/VisualDuipai.exe`.
- Create: `packaging/README.md`
  - Packaging documentation for Windows and future macOS/Linux direction.
- Modify: `.gitignore`
  - Add PyInstaller temporary and output artifacts.

Do not modify:

- `duipai_gui.py`
- `stress_core.py`
- `test_stress_core.py`
- Parent directory files: `../force.cpp`, `../gptanswer.cpp`, `../gen.cpp`, `../duipai.sh`

---

### Task 1: Add Windows Build Script

**Files:**
- Create: `D:/yzx/Documents/claude_code/duipai/visual_duipai/build_exe.ps1`

- [ ] **Step 1: Write `build_exe.ps1`**

Write this exact file content:

```powershell
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
```

- [ ] **Step 2: Verify PowerShell script parses**

Run from `D:/yzx/Documents/claude_code/duipai/visual_duipai`:

```bash
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [scriptblock]::Create((Get-Content -Raw .\build_exe.ps1)) | Out-Null; Write-Host 'parse ok'"
```

Expected: output contains `parse ok` and command exits 0.

- [ ] **Step 3: Commit build script**

Run:

```bash
git add build_exe.ps1
git commit -m "feat: add windows exe build script"
```

Expected: commit succeeds.

---

### Task 2: Add Packaging Documentation

**Files:**
- Create: `D:/yzx/Documents/claude_code/duipai/visual_duipai/packaging/README.md`

- [ ] **Step 1: Write packaging README**

Write this exact file content:

```markdown
# VisualDuipai Packaging

This project is packaged with PyInstaller.

## Windows EXE

From PowerShell, run:

```powershell
cd D:\yzx\Documents\claude_code\duipai\visual_duipai
.\build_exe.ps1
```

The output is:

```text
dist/VisualDuipai.exe
```

Double-click `dist/VisualDuipai.exe` to launch the GUI.

## Requirements on the target machine

The packaged EXE includes the Python GUI and Python dependencies, but it does not include a C++ compiler.

The machine running the EXE must have `g++` installed and available in `PATH`:

```powershell
g++ --version
```

If `g++` is missing, the GUI can open, but stress testing will fail during compilation and show the compiler error in the log.

## Drag-and-drop support

The Windows build collects `tkinterdnd2` resources with PyInstaller:

```powershell
--collect-all tkinterdnd2
```

If the build fails because `--collect-all` is unsupported, upgrade PyInstaller:

```powershell
python -m pip install --upgrade pyinstaller
```

## macOS and Linux

Windows `.exe` files do not run natively on macOS or Linux.

Future platform builds should be created on the target OS:

- macOS: run PyInstaller on macOS and produce a macOS executable or `.app` bundle.
- Linux: run PyInstaller on Linux and produce a Linux executable, with optional AppImage packaging later.

This project does not cross-compile macOS or Linux builds from Windows.
```

- [ ] **Step 2: Verify README exists and contains Windows command**

Run:

```bash
python -c "from pathlib import Path; p=Path('packaging/README.md'); text=p.read_text(encoding='utf-8'); print(p.exists(), '.\\build_exe.ps1' in text, 'dist/VisualDuipai.exe' in text)"
```

Expected:

```text
True True True
```

- [ ] **Step 3: Commit packaging README**

Run:

```bash
git add packaging/README.md
git commit -m "docs: add packaging instructions"
```

Expected: commit succeeds.

---

### Task 3: Ignore PyInstaller Artifacts

**Files:**
- Modify: `D:/yzx/Documents/claude_code/duipai/visual_duipai/.gitignore`

- [ ] **Step 1: Update `.gitignore`**

Change `.gitignore` from:

```gitignore
__pycache__/
*.pyc
/.duipai_tmp/
/duipai_work/
```

to:

```gitignore
__pycache__/
*.pyc
/.duipai_tmp/
/duipai_work/
/build/
/dist/
*.spec
```

- [ ] **Step 2: Verify ignore file content**

Run:

```bash
python -c "from pathlib import Path; text=Path('.gitignore').read_text(encoding='utf-8'); print('/build/' in text, '/dist/' in text, '*.spec' in text)"
```

Expected:

```text
True True True
```

- [ ] **Step 3: Commit ignore update**

Run:

```bash
git add .gitignore
git commit -m "chore: ignore pyinstaller artifacts"
```

Expected: commit succeeds.

---

### Task 4: Build and Verify Windows EXE

**Files:**
- Use: `D:/yzx/Documents/claude_code/duipai/visual_duipai/build_exe.ps1`
- Use: `D:/yzx/Documents/claude_code/duipai/visual_duipai/dist/VisualDuipai.exe`

- [ ] **Step 1: Run unit tests before packaging**

Run:

```bash
python -m unittest discover -p "test*.py"
```

Expected: output contains `OK`.

- [ ] **Step 2: Run Windows build script**

Run from `D:/yzx/Documents/claude_code/duipai/visual_duipai`:

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_exe.ps1
```

Expected:

- command exits 0
- output contains `Build succeeded!`
- output path contains `dist\VisualDuipai.exe` or `dist/VisualDuipai.exe`

If PyInstaller fails because `--collect-all` is unsupported, run:

```bash
python -m pip install --upgrade pyinstaller
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_exe.ps1
```

Expected after upgrade: build succeeds.

- [ ] **Step 3: Verify EXE exists**

Run:

```bash
powershell -NoProfile -Command "Test-Path .\dist\VisualDuipai.exe"
```

Expected:

```text
True
```

- [ ] **Step 4: Verify EXE can start briefly**

Run:

```bash
powershell -NoProfile -Command "$p = Start-Process -FilePath .\dist\VisualDuipai.exe -PassThru; Start-Sleep -Seconds 3; if (-not $p.HasExited) { $p.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 1 }; if (-not $p.HasExited) { $p.Kill() }; Write-Host 'exe launch checked'"
```

Expected: command exits 0 and prints `exe launch checked`. The GUI may appear briefly.

- [ ] **Step 5: Verify artifacts are ignored and source tree is clean**

Run:

```bash
git status --short --ignored
```

Expected:

- `build/`, `dist/`, and `VisualDuipai.spec` are ignored if present.
- normal `git status --short` is clean.

Run:

```bash
git status --short
```

Expected: no output.

---

## Self-Review

- Spec coverage: The plan adds `build_exe.ps1`, `packaging/README.md`, updates `.gitignore`, installs/checks PyInstaller, uses `--collect-all tkinterdnd2`, builds `dist/VisualDuipai.exe`, verifies the file exists, checks a brief launch, documents g++ requirement, and records macOS/Linux future packaging principles.
- Placeholder scan: No placeholders, `TBD`, `TODO`, or incomplete commands remain.
- Scope check: The plan is focused on Windows EXE packaging only; macOS/Linux scripts, AppImage, MSI, custom icon, and bundling g++ are not included.
- Type/name consistency: The output name is consistently `VisualDuipai.exe`; the script name is consistently `build_exe.ps1`; artifact directories are consistently `/build/` and `/dist/`.
