# GitHub Release Cleanup Design

## Goal

Prepare `visual_duipai` for publication as a small GitHub open-source project named **VisualDuipai**.

The repository should be convenient for two audiences:

1. End users who download a packaged Windows zip from GitHub Releases and run `VisualDuipai.exe`.
2. Developers who clone the source repository, run the GUI from Python, run tests, or build the Windows executable themselves.

Generated artifacts such as `dist/VisualDuipai.exe`, `build/`, `VisualDuipai.spec`, and release zip files must stay out of Git history. Packaged binaries are published as GitHub Release attachments, not committed to the repository.

## Chosen Approach

Use a **standard GitHub Release repository layout**:

- Source code, tests, documentation, and build scripts are tracked in Git.
- Release binaries are built locally with `build_exe.ps1` and uploaded to GitHub Releases.
- Documentation is Chinese-first, because the expected users are Chinese algorithm contest / practice users.
- The project uses the MIT License.

This is intentionally lighter than a full open-source infrastructure setup. It does not add GitHub Actions, issue templates, PR templates, automatic release builds, installers, code signing, or cross-platform packages.

## Repository Structure

After cleanup, the repository should include:

```text
visual_duipai/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── docs/
│   ├── RELEASE.md
│   └── superpowers/
│       ├── plans/
│       └── specs/
├── packaging/
│   └── README.md
├── build_exe.ps1
├── duipai_gui.py
├── stress_core.py
├── test_stress_core.py
├── test_build_exe_script.py
├── requirements.txt
└── .gitignore
```

### New Files

- `README.md`
  - GitHub landing page for users and developers.
- `LICENSE`
  - MIT License.
- `CHANGELOG.md`
  - Version history starting with `v0.1.0`.
- `docs/RELEASE.md`
  - Maintainer instructions for building, packaging, and publishing GitHub Releases.

### Existing Files Kept

- `build_exe.ps1`
  - Windows build script for `dist/VisualDuipai.exe`.
- `packaging/README.md`
  - Lower-level packaging documentation.
- `duipai_gui.py`, `stress_core.py`, tests, and requirements.

## README Design

`README.md` should be Chinese-first and practical. It should contain:

1. Project title and short description:
   - `VisualDuipai`
   - `一个用于算法题本地对拍的 Windows GUI 工具`
2. Use cases:
   - Algorithm contest practice.
   - Local stress testing.
   - Verifying an optimized solution against a brute-force solution.
3. Feature summary:
   - Select or drag in brute-force solution, accepted/optimized solution, and generator C++ files.
   - Compile and run the three programs locally.
   - Compare outputs automatically.
   - Show failing input, outputs, and diff information when a mismatch appears.
4. Recommended user installation:
   - Download `VisualDuipai-v0.1.0-windows-x64.zip` from GitHub Releases.
   - Extract it.
   - Double-click `VisualDuipai.exe`.
5. Runtime requirement:
   - Windows.
   - `g++` installed and available in `PATH`.
   - The packaged EXE includes the Python GUI and Python dependencies, but does not include a C++ compiler.
6. Source usage:
   - Install dependencies with `python -m pip install -r requirements.txt`.
   - Run with `python duipai_gui.py`.
7. Build from source:
   - Use `powershell -ExecutionPolicy Bypass -File .\build_exe.ps1`.
8. FAQ:
   - Windows SmartScreen unknown publisher prompt.
   - Antivirus false positives from PyInstaller one-file EXEs.
   - `g++` not found.
   - macOS/Linux are not supported by the Windows EXE.
9. License:
   - MIT.

The README should not claim there is already a public GitHub URL unless one is known. It can refer generically to the repository's Releases page.

## Release Documentation Design

`docs/RELEASE.md` should describe the manual release process:

1. Start from a clean `main` checkout.
2. Run tests:
   ```powershell
   python -m unittest discover -p "test*.py"
   ```
3. Build the executable:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
   ```
4. Smoke-test the executable:
   - Confirm `dist/VisualDuipai.exe` exists.
   - Launch it briefly.
5. Create release zip:
   - Name format: `VisualDuipai-v0.1.0-windows-x64.zip`.
   - Include `VisualDuipai.exe` only.
   - Do not include generated build folders or source files in the release zip.
6. Create GitHub Release:
   - Tag: `v0.1.0`.
   - Title: `VisualDuipai v0.1.0`.
   - Upload the zip as the release asset.
7. Confirm release artifacts are ignored and not committed.

The release documentation is for maintainers, not end users.

## Changelog Design

`CHANGELOG.md` should start with `v0.1.0` and summarize:

- Initial VisualDuipai GUI release.
- Local C++ stress testing workflow.
- Windows PyInstaller packaging via `build_exe.ps1`.
- Drag-and-drop support through `tkinterdnd2`.

## License Design

Add `LICENSE` using the MIT License. Use the year `2026` and project owner name `yzx` unless the user provides a different copyright holder before implementation.

## Ignore Rules

The repository should ignore local/generated artifacts. Existing rules should be preserved:

```gitignore
__pycache__/
*.pyc
/.duipai_tmp/
/duipai_work/
/build/
/dist/
/VisualDuipai.spec
```

Add release artifact ignores:

```gitignore
*.zip
*.exe
```

Because the project should not commit generated executables, these broader ignores are acceptable for the current release model. If future sample executables are needed, they can be force-added explicitly or the ignore rules can be narrowed.

## Non-Goals

This cleanup will not add:

- GitHub Actions.
- Automatic PyInstaller builds.
- MSI installers.
- Code signing.
- macOS or Linux packages.
- Issue templates or PR templates.
- Screenshots generated during implementation.
- A public GitHub repository URL.

## Verification

After implementation:

1. Run unit tests:
   ```powershell
   python -m unittest discover -p "test*.py"
   ```
2. Optionally run the existing Windows build script if packaging behavior changed:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
   ```
3. Check Git status and ignored artifacts:
   ```powershell
   git status --short --ignored
   ```
4. Confirm tracked changes are limited to documentation, license, and ignore-rule updates.
5. Confirm generated artifacts such as `dist/`, `build/`, `VisualDuipai.spec`, `*.zip`, and `*.exe` are not staged.
