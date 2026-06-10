# GitHub Release Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare VisualDuipai for GitHub publication with Chinese-first user docs, MIT licensing, changelog, release instructions, and ignore rules that keep generated binaries out of Git.

**Architecture:** This is a documentation and repository hygiene cleanup. The application code and packaging script remain unchanged; the repository gains a GitHub-facing README, MIT license, changelog, maintainer release guide, and safer ignore rules for release artifacts.

**Tech Stack:** Markdown, Git, Python unittest, PowerShell build script documentation.

---

## File Structure

All paths are relative to repository root `D:/yzx/Documents/claude_code/duipai/visual_duipai`.

- Create: `README.md`
  - Chinese-first GitHub landing page for users and developers.
- Create: `LICENSE`
  - MIT License with copyright `2026 yzx`.
- Create: `CHANGELOG.md`
  - Version history starting with `v0.1.0`.
- Create: `docs/RELEASE.md`
  - Maintainer checklist for manual GitHub Release publishing.
- Modify: `.gitignore`
  - Add `*.zip` and `*.exe` so release artifacts are not accidentally committed.

Do not modify:

- `duipai_gui.py`
- `stress_core.py`
- `test_stress_core.py`
- `test_build_exe_script.py`
- `build_exe.ps1`
- `packaging/README.md`

---

### Task 1: Add GitHub README

**Files:**
- Create: `D:/yzx/Documents/claude_code/duipai/visual_duipai/README.md`

- [ ] **Step 1: Write `README.md`**

Create `README.md` with this exact content:

````markdown
# VisualDuipai

一个用于算法题本地对拍的 Windows GUI 工具。

VisualDuipai 帮你在本地反复运行“数据生成器 + 暴力程序 + 正解程序”，自动比较输出，方便在算法竞赛、刷题和调试时发现错误样例。

## 功能特点

- 选择或拖入三个 C++ 文件：
  - 暴力程序
  - 正解程序
  - 数据生成器
- 自动编译并运行本地对拍流程。
- 自动比较暴力程序和正解程序的输出。
- 发现不一致时保留输入、输出和 diff 信息，方便定位问题。
- 支持 Windows EXE 打包版本，也支持从源码运行。

## 推荐使用方式：下载 Windows 版本

在 GitHub 仓库的 Releases 页面下载：

```text
VisualDuipai-v0.1.0-windows-x64.zip
```

下载后：

1. 解压 zip 文件。
2. 双击 `VisualDuipai.exe`。
3. 在界面中选择或拖入暴力程序、正解程序和数据生成器。
4. 设置对拍轮数。
5. 点击开始运行。

## 运行要求

Windows EXE 包含 Python GUI 和 Python 依赖，但不包含 C++ 编译器。

运行对拍功能的电脑必须安装 `g++`，并且 `g++` 要在 `PATH` 中。可以在 PowerShell 中检查：

```powershell
g++ --version
```

如果没有安装 `g++`，界面可能可以打开，但开始对拍时会在编译阶段失败。

## 从源码运行

需要 Python 3 和依赖包。

```powershell
python -m pip install -r requirements.txt
python duipai_gui.py
```

## 从源码打包 Windows EXE

在项目根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```

成功后会生成：

```text
dist/VisualDuipai.exe
```

更多打包说明见 [`packaging/README.md`](packaging/README.md)。

## 常见问题

### Windows 提示“未知发布者”怎么办？

这是因为当前 EXE 没有代码签名。确认文件来自你信任的 Release 后，可以在 Windows SmartScreen 提示中选择“更多信息”然后继续运行。

### 杀毒软件误报怎么办？

PyInstaller 打包的一文件 EXE 偶尔会被杀毒软件误报。建议只从可信的 GitHub Release 下载，不要运行来源不明的 EXE。

### 提示找不到 `g++` 怎么办？

需要安装 MinGW、MSYS2、TDM-GCC 或其他提供 `g++` 的 C++ 编译环境，并确保 `g++` 已加入 `PATH`。安装后重新打开 PowerShell，运行：

```powershell
g++ --version
```

能看到版本信息后再运行 VisualDuipai。

### macOS 或 Linux 可以直接运行这个 EXE 吗？

不可以。Windows `.exe` 不能原生运行在 macOS 或 Linux 上。其他系统需要在对应系统上重新打包或直接从源码运行。

## 开发与测试

运行测试：

```powershell
python -m unittest discover -p "test*.py"
```

## License

本项目使用 MIT License。详见 [`LICENSE`](LICENSE)。
````

- [ ] **Step 2: Verify README content**

Run:

```bash
python -c "from pathlib import Path; text=Path('README.md').read_text(encoding='utf-8'); print('# VisualDuipai' in text, 'VisualDuipai-v0.1.0-windows-x64.zip' in text, 'g++ --version' in text, 'python duipai_gui.py' in text, 'LICENSE' in text)"
```

Expected output:

```text
True True True True True
```

- [ ] **Step 3: Commit README**

Run:

```bash
git add README.md
git commit -m "docs: add github readme"
```

Expected: commit succeeds.

---

### Task 2: Add MIT License

**Files:**
- Create: `D:/yzx/Documents/claude_code/duipai/visual_duipai/LICENSE`

- [ ] **Step 1: Write `LICENSE`**

Create `LICENSE` with this exact content:

```text
MIT License

Copyright (c) 2026 yzx

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Verify license content**

Run:

```bash
python -c 'from pathlib import Path; text=Path("LICENSE").read_text(encoding="utf-8"); print(text.startswith("MIT License"), "Copyright (c) 2026 yzx" in text, "THE SOFTWARE IS PROVIDED \"AS IS\"" in text)'
```

Expected output:

```text
True True True
```

- [ ] **Step 3: Commit license**

Run:

```bash
git add LICENSE
git commit -m "docs: add mit license"
```

Expected: commit succeeds.

---

### Task 3: Add Changelog

**Files:**
- Create: `D:/yzx/Documents/claude_code/duipai/visual_duipai/CHANGELOG.md`

- [ ] **Step 1: Write `CHANGELOG.md`**

Create `CHANGELOG.md` with this exact content:

```markdown
# Changelog

All notable changes to VisualDuipai will be documented in this file.

## v0.1.0 - 2026-06-10

### Added

- Initial VisualDuipai GUI for local algorithm stress testing.
- Support for selecting or dragging in brute-force solution, accepted/optimized solution, and generator C++ files.
- Local compile-run-compare workflow using `g++`.
- Failure artifacts for debugging mismatched outputs.
- Drag-and-drop support through `tkinterdnd2`.
- Windows PyInstaller packaging through `build_exe.ps1`.
- GitHub Release documentation for publishing `VisualDuipai.exe` as a zip asset.
```

- [ ] **Step 2: Verify changelog content**

Run:

```bash
python -c "from pathlib import Path; text=Path('CHANGELOG.md').read_text(encoding='utf-8'); print('## v0.1.0 - 2026-06-10' in text, 'build_exe.ps1' in text, 'tkinterdnd2' in text, 'GitHub Release' in text)"
```

Expected output:

```text
True True True True
```

- [ ] **Step 3: Commit changelog**

Run:

```bash
git add CHANGELOG.md
git commit -m "docs: add changelog"
```

Expected: commit succeeds.

---

### Task 4: Add Release Publishing Guide

**Files:**
- Create: `D:/yzx/Documents/claude_code/duipai/visual_duipai/docs/RELEASE.md`

- [ ] **Step 1: Write `docs/RELEASE.md`**

Create `docs/RELEASE.md` with this exact content:

````markdown
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
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
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
````

- [ ] **Step 2: Verify release guide content**

Run:

```bash
python -c "from pathlib import Path; text=Path('docs/RELEASE.md').read_text(encoding='utf-8'); print('VisualDuipai-v0.1.0-windows-x64.zip' in text, 'Compress-Archive' in text, 'Build succeeded!' in text, 'g++' in text, 'Do not commit generated' in text)"
```

Expected output:

```text
True True True True True
```

- [ ] **Step 3: Commit release guide**

Run:

```bash
git add docs/RELEASE.md
git commit -m "docs: add release guide"
```

Expected: commit succeeds.

---

### Task 5: Ignore Release Artifacts

**Files:**
- Modify: `D:/yzx/Documents/claude_code/duipai/visual_duipai/.gitignore`

- [ ] **Step 1: Update `.gitignore`**

Change `.gitignore` from:

```gitignore
__pycache__/
*.pyc
/.duipai_tmp/
/duipai_work/
/build/
/dist/
/VisualDuipai.spec
```

to:

```gitignore
__pycache__/
*.pyc
/.duipai_tmp/
/duipai_work/
/build/
/dist/
/VisualDuipai.spec
*.zip
*.exe
```

- [ ] **Step 2: Verify ignore content**

Run:

```bash
python -c "from pathlib import Path; text=Path('.gitignore').read_text(encoding='utf-8'); print('/build/' in text, '/dist/' in text, '/VisualDuipai.spec' in text, '*.zip' in text, '*.exe' in text)"
```

Expected output:

```text
True True True True True
```

- [ ] **Step 3: Verify sample release artifacts are ignored**

Run:

```bash
python -c "from pathlib import Path; Path('VisualDuipai-v0.1.0-windows-x64.zip').write_text('placeholder', encoding='utf-8'); Path('sample.exe').write_text('placeholder', encoding='utf-8')" && git status --short --ignored
```

Expected: output includes ignored entries for `VisualDuipai-v0.1.0-windows-x64.zip` and `sample.exe`, prefixed with `!!`.

- [ ] **Step 4: Remove sample release artifacts**

Run:

```bash
python -c "from pathlib import Path; Path('VisualDuipai-v0.1.0-windows-x64.zip').unlink(missing_ok=True); Path('sample.exe').unlink(missing_ok=True)"
```

Expected: command exits 0.

- [ ] **Step 5: Commit ignore update**

Run:

```bash
git add .gitignore
git commit -m "chore: ignore release artifacts"
```

Expected: commit succeeds.

---

### Task 6: Final Verification

**Files:**
- Use: all files in repository.

- [ ] **Step 1: Run unit tests**

Run:

```bash
python -m unittest discover -p "test*.py"
```

Expected: output contains `OK`.

- [ ] **Step 2: Verify required release files exist**

Run:

```bash
python -c "from pathlib import Path; required=['README.md','LICENSE','CHANGELOG.md','docs/RELEASE.md','packaging/README.md','build_exe.ps1']; print(all(Path(p).exists() for p in required))"
```

Expected output:

```text
True
```

- [ ] **Step 3: Verify generated artifacts are ignored**

Run:

```bash
python -c "from pathlib import Path; Path('VisualDuipai-v0.1.0-windows-x64.zip').write_text('placeholder', encoding='utf-8'); Path('sample.exe').write_text('placeholder', encoding='utf-8')" && git status --short --ignored
```

Expected: output includes `!! VisualDuipai-v0.1.0-windows-x64.zip` and `!! sample.exe`.

- [ ] **Step 4: Remove sample artifacts**

Run:

```bash
python -c "from pathlib import Path; Path('VisualDuipai-v0.1.0-windows-x64.zip').unlink(missing_ok=True); Path('sample.exe').unlink(missing_ok=True)"
```

Expected: command exits 0.

- [ ] **Step 5: Confirm source status is clean**

Run:

```bash
git status --short
```

Expected: no output.

- [ ] **Step 6: Optional packaging smoke check**

This cleanup does not modify `build_exe.ps1`. If extra confidence is desired, run:

```bash
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```

Expected: output contains `Build succeeded!`. This step may be skipped if only documentation and `.gitignore` changed and unit tests passed.

---

## Self-Review

- Spec coverage: This plan creates `README.md`, `LICENSE`, `CHANGELOG.md`, `docs/RELEASE.md`, and updates `.gitignore` with `*.zip` and `*.exe`. It keeps generated release assets out of Git and documents GitHub Releases as the binary distribution path.
- Placeholder scan: No `TBD`, `TODO`, incomplete commands, or vague implementation steps remain.
- Scope check: The plan does not add GitHub Actions, installers, code signing, issue templates, PR templates, screenshots, macOS/Linux builds, or application code changes.
- Type/name consistency: Version `v0.1.0`, zip name `VisualDuipai-v0.1.0-windows-x64.zip`, executable `VisualDuipai.exe`, project name `VisualDuipai`, and MIT copyright holder `yzx` are consistent across tasks.
