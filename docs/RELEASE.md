# Release Guide

This document is for maintainers publishing a VisualDuipai GitHub Release.

Release binaries should be uploaded as GitHub Release assets. Do not commit generated `dist/`, `build/`, `.spec`, `.exe`, or `.zip` files to Git.

## v0.1.0 Windows release checklist

Run commands from the repository root.

### 1. Start clean

```powershell
git status --short --branch
```

Expected source state before building:

```text
## main
```

Ignored generated files may appear when running `git status --short --ignored`; they should not be staged.

### 2. Run tests

```powershell
python -m unittest discover -p "test*.py"
```

Expected: all tests pass.

### 3. Build the EXE

```powershell
powershell -ExecutionPolicy Bypass -File .uild_exe.ps1
```

Expected output includes:

```text
Build succeeded!
dist\VisualDuipai.exe
```

### 4. Smoke-test the EXE

Confirm the file exists:

```powershell
Test-Path .\dist\VisualDuipai.exe
```

Expected:

```text
True
```

Launch it briefly:

```powershell
$p = Start-Process -FilePath .\dist\VisualDuipai.exe -PassThru; Start-Sleep -Seconds 3; if (-not $p.HasExited) { $p.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 1 }; if (-not $p.HasExited) { $p.Kill() }; Write-Host "exe launch checked"
```

Expected: the GUI opens briefly and the command prints `exe launch checked`.

### 5. Create the release zip

Create a zip containing only `VisualDuipai.exe`:

```powershell
Compress-Archive -Path .\dist\VisualDuipai.exe -DestinationPath .\VisualDuipai-v0.1.0-windows-x64.zip -Force
```

The zip should not contain source files, `build/`, `dist/`, or `VisualDuipai.spec`.

### 6. Create the GitHub Release

Create a GitHub Release with:

- Tag: `v0.1.0`
- Title: `VisualDuipai v0.1.0`
- Asset: `VisualDuipai-v0.1.0-windows-x64.zip`

Suggested release notes:

```markdown
## VisualDuipai v0.1.0

Initial Windows release.

### Highlights

- Windows GUI for local algorithm stress testing.
- Select or drag in brute-force solution, accepted/optimized solution, and generator C++ files.
- Automatically compiles and compares outputs.
- Packaged as a single `VisualDuipai.exe` inside the release zip.

### Requirements

- Windows.
- `g++` installed and available in `PATH`.
```

### 7. Confirm generated files remain untracked

```powershell
git status --short --ignored
```

Expected:

- `build/`, `dist/`, `VisualDuipai.spec`, `VisualDuipai-v0.1.0-windows-x64.zip`, and `*.exe` artifacts are ignored if present.
- `git status --short` has no tracked or untracked source changes after release documentation is committed.
