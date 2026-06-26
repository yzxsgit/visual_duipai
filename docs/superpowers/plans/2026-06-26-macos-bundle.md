# macOS .app Bundle 打包 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 VisualDuipai 增加 GitHub Actions 自动构建 macOS .app Bundle，支持 Apple Silicon Mac

**Architecture:** GitHub Actions workflow（`.github/workflows/build_macos.yml`）在 `macos-latest` runner 上执行 PyInstaller 打包 → 构建 .app Bundle 结构 → 生成 Info.plist + ICNS 图标 → 上传 Artifact。GUI 层加一行 macOS `open` 命令回退。

**Tech Stack:** GitHub Actions, Python 3.12, PyInstaller, `iconutil`（macOS 自带）, `sips`（macOS 自带）

## Global Constraints

- 构建环境：GitHub Actions `macos-latest`（ARM runner，产物仅适用 Apple Silicon Mac）
- PyInstaller 参数与 Linux/Windows 对齐：`--onefile --noconsole --name VisualDuipai --collect-all tkinterdnd2`
- g++ 不打包进 .app，用户系统自行通过 `xcode-select --install` 安装
- .app 产物命名：`VisualDuipai.app`，zip 后命名 `VisualDuipai.app.zip`
- 图标：从 `assets/VisualDuipai.png`（256x256 PNG）用 `sips` + `iconutil` 转换为 ICNS
- .app 最低系统版本：macOS 10.15

---

### Task 1: 增加 macOS `open` 命令支持

**Files:**
- Modify: `duipai_gui.py`（_open_work_dir 方法）

**Interfaces:**
- Consumes: 已有的 `_open_work_dir` 方法（第 296-307 行）
- Produces: 修改后的方法支持 macOS `open` 命令

**说明：** 当前代码 `os.startfile()` 失败时回退到 `xdg-open`。macOS 上应使用 `open` 命令。需要在 `except AttributeError` 块中加上尝试 `open` 的逻辑。

- [ ] **Step 1: 读取 duipai_gui.py 当前 _open_work_dir 方法**

```bash
cd "/home/yzx/文档/claude code/visual_duipai" && grep -n -A12 "def _open_work_dir" duipai_gui.py
```

- [ ] **Step 2: 修改 _open_work_dir 方法**

将 `except AttributeError` 块从：

```python
        except AttributeError:
            import subprocess
            subprocess.Popen(["xdg-open", str(paths.work_dir)])
```

改为：

```python
        except AttributeError:
            import subprocess
            import sys as _sys
            try:
                if _sys.platform == "darwin":
                    subprocess.Popen(["open", str(paths.work_dir)])
                else:
                    subprocess.Popen(["xdg-open", str(paths.work_dir)])
            except FileNotFoundError:
                subprocess.Popen(["xdg-open", str(paths.work_dir)])
```

- [ ] **Step 3: 验证修改**

```bash
$ cd "/home/yzx/文档/claude code/visual_duipai" && python3 -c "
import ast, sys
with open('duipai_gui.py') as f:
    tree = ast.parse(f.read())
# Check that _open_work_dir references 'open' for darwin
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_open_work_dir':
        source = ast.get_source_segment(open('duipai_gui.py').read(), node)
        assert 'if _sys.platform == \"darwin\"' in source, 'Missing darwin check'
        assert '\"open\"' in source, 'Missing open command'
        assert '\"xdg-open\"' in source, 'Missing xdg-open fallback'
        print('PASS: _open_work_dir handles macOS + Linux')
        break
"
```

预期输出: `PASS: _open_work_dir handles macOS + Linux`

- [ ] **Step 4: 运行测试确保没破坏现有逻辑**

```bash
cd "/home/yzx/文档/claude code/visual_duipai" && python3 -m unittest discover -p "test*.py"
```

预期输出: `OK`（16 tests pass）

- [ ] **Step 5: 提交**

```bash
cd "/home/yzx/文档/claude code/visual_duipai" && git add duipai_gui.py && git commit -m "fix: add macOS 'open' command support for opening work directory"
```

---

### Task 2: 创建 GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/build_macos.yml`

**Interfaces:**
- Consumes: `assets/VisualDuipai.png`（图标源文件）
- Produces: GitHub Actions 自动构建产出 `VisualDuipai.app.zip`

- [ ] **Step 1: 创建目录和 workflow 文件**

```bash
mkdir -p "/home/yzx/文档/claude code/visual_duipai/.github/workflows"
```

```yaml
# .github/workflows/build_macos.yml
name: Build macOS .app Bundle

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: macos-latest
    strategy:
      matrix:
        python-version: ["3.12"]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt pyinstaller

      - name: Run tests
        run: |
          python -m unittest discover -p "test*.py"

      - name: Build with PyInstaller
        run: |
          rm -rf build dist
          python -m PyInstaller \
            --onefile \
            --noconsole \
            --name VisualDuipai \
            --collect-all tkinterdnd2 \
            duipai_gui.py

      - name: Verify PyInstaller output
        run: |
          test -f dist/VisualDuipai && echo "PASS: binary exists" || { echo "FAIL: binary missing"; exit 1; }

      - name: Create .app bundle structure
        run: |
          mkdir -p "VisualDuipai.app/Contents/MacOS"
          mkdir -p "VisualDuipai.app/Contents/Resources"
          cp dist/VisualDuipai "VisualDuipai.app/Contents/MacOS/VisualDuipai"

      - name: Convert PNG to ICNS
        run: |
          mkdir -p VisualDuipai.iconset
          # Create all required sizes from the 256x256 source
          sips -z 16 16 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_16x16.png
          sips -z 32 32 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_16x16@2x.png
          sips -z 32 32 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_32x32.png
          sips -z 64 64 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_32x32@2x.png
          sips -z 128 128 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_128x128.png
          sips -z 256 256 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_128x128@2x.png
          sips -z 256 256 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_256x256.png
          sips -z 512 512 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_256x256@2x.png
          iconutil -c icns VisualDuipai.iconset -o VisualDuipai.icns
          cp VisualDuipai.icns "VisualDuipai.app/Contents/Resources/VisualDuipai.icns"

      - name: Create Info.plist
        run: |
          cat > "VisualDuipai.app/Contents/Info.plist" << 'EOF'
          <?xml version="1.0" encoding="UTF-8"?>
          <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
          <plist version="1.0">
          <dict>
              <key>CFBundleExecutable</key>
              <string>VisualDuipai</string>
              <key>CFBundleIdentifier</key>
              <string>com.visualduipai.app</string>
              <key>CFBundleName</key>
              <string>VisualDuipai</string>
              <key>CFBundleDisplayName</key>
              <string>对拍可视化工具</string>
              <key>CFBundleIconFile</key>
              <string>VisualDuipai.icns</string>
              <key>CFBundlePackageType</key>
              <string>APPL</string>
              <key>CFBundleShortVersionString</key>
              <string>0.2.0</string>
              <key>LSMinimumSystemVersion</key>
              <string>10.15</string>
              <key>NSHighResolutionCapable</key>
              <true/>
          </dict>
          </plist>
          EOF

      - name: Verify .app bundle structure
        run: |
          test -f "VisualDuipai.app/Contents/MacOS/VisualDuipai" && echo "PASS: binary in .app"
          test -f "VisualDuipai.app/Contents/Resources/VisualDuipai.icns" && echo "PASS: icns in .app"
          test -f "VisualDuipai.app/Contents/Info.plist" && echo "PASS: Info.plist in .app"
          plutil -lint "VisualDuipai.app/Contents/Info.plist" && echo "PASS: Info.plist valid"

      - name: Package .app as zip
        run: |
          zip -r VisualDuipai.app.zip VisualDuipai.app
          ls -lh VisualDuipai.app.zip

      - name: Upload .app artifact
        uses: actions/upload-artifact@v4
        with:
          name: VisualDuipai-macos-${{ github.sha }}
          path: VisualDuipai.app.zip
          retention-days: 7
```

- [ ] **Step 2: 验证 workflow 关键内容**

```bash
$ cd "/home/yzx/文档/claude code/visual_duipai" && \
  echo "--- Trigger events ---" && \
  grep -q "push:" .github/workflows/build_macos.yml && echo "PASS: push trigger" && \
  grep -q "workflow_dispatch" .github/workflows/build_macos.yml && echo "PASS: manual trigger" && \
  echo "--- Runner ---" && \
  grep -q "macos-latest" .github/workflows/build_macos.yml && echo "PASS: correct runner" && \
  echo "--- Key steps ---" && \
  grep -q "actions/checkout@v4" .github/workflows/build_macos.yml && echo "PASS: checkout" && \
  grep -q "setup-python@v5" .github/workflows/build_macos.yml && echo "PASS: setup-python" && \
  grep -q "PyInstaller" .github/workflows/build_macos.yml && echo "PASS: PyInstaller" && \
  grep -q "Create .app bundle" .github/workflows/build_macos.yml && echo "PASS: bundle step" && \
  grep -q "iconutil" .github/workflows/build_macos.yml && echo "PASS: icon conversion" && \
  grep -q "Info.plist" .github/workflows/build_macos.yml && echo "PASS: Info.plist" && \
  grep -q "upload-artifact@v4" .github/workflows/build_macos.yml && echo "PASS: artifact upload" && \
  echo "--- PyInstaller params ---" && \
  grep -q "onefile" .github/workflows/build_macos.yml && echo "PASS: --onefile" && \
  grep -q "collect-all" .github/workflows/build_macos.yml && echo "PASS: --collect-all" && \
  echo "=== ALL PASS ==="
```

预期输出：`=== ALL PASS ===`（中间无 FAIL）

- [ ] **Step 3: 提交**

```bash
cd "/home/yzx/文档/claude code/visual_duipai" && git add .github/workflows/build_macos.yml && git commit -m "feat: add GitHub Actions workflow for macOS .app bundle build"
```

---

### Task 3: 更新文档

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `packaging/README.md`
- Modify: `docs/RELEASE.md`

- [ ] **Step 1: 更新 README.md — 增加 macOS 使用说明**

在 `## 推荐使用方式：下载 Linux 版本` 之前（或之后）插入 macOS 章节：

```markdown
## 推荐使用方式：下载 macOS 版本

在 GitHub 仓库的 Releases 页面下载：

```text
VisualDuipai.app.zip
```

下载后：

1. 解压 zip 文件得到 `VisualDuipai.app`。
2. 右键 → 打开（首次需要绕过 Gatekeeper）。
3. 在界面中选择或拖入暴力程序、正解程序和数据生成器。
4. 设置对拍轮数。
5. 点击开始运行。

### 依赖

系统必须安装 Xcode Command Line Tools（提供 `g++` / `clang++`）。

```bash
xcode-select --install
```
```

- [ ] **Step 2: 更新 CHANGELOG.md**

在 `## Unreleased` 下追加：

```markdown
### Added

- macOS .app Bundle 打包支持，通过 GitHub Actions 自动构建
- macOS 打开工作目录支持（`open` 命令）
```

- [ ] **Step 3: 更新 packaging/README.md**

在 `## Linux AppImage` 之后（文件末尾）追加：

```markdown
## macOS .app Bundle

### 打包方式

使用 GitHub Actions 自动构建，无需本地 macOS 环境。

1. 推送代码到 GitHub（`main` 分支或 `v*` tag）
2. Workflow `.github/workflows/build_macos.yml` 自动在 `macos-latest` runner 上执行
3. 构建产物 `VisualDuipai.app.zip` 以 CI Artifact 形式保存

### workflow 步骤

1. Checkout code → Setup Python → Install dependencies → Run tests
2. PyInstaller 打包为单文件二进制
3. 构建 .app Bundle 目录结构
4. 将 PNG 图标转换为 ICNS 格式（`sips` + `iconutil`）
5. 生成 Info.plist 元数据
6. 打包为 zip 并上传 Artifact

### 运行要求

- Apple Silicon Mac（GitHub 的 `macos-latest` runner 为 ARM 架构）
- Xcode Command Line Tools（`xcode-select --install`）

### 注意事项

- 未签名的 .app 首次启动会被 Gatekeeper 阻止，右键 → 打开即可
- 如果需要在 Intel Mac 上运行，需在 `macos-13`（Intel）runner 上单独构建
```

- [ ] **Step 4: 更新 docs/RELEASE.md**

在 `## Linux AppImage release checklist` 之后追加：

```markdown
## macOS .app Bundle release checklist

### 1. Trigger the build

- Push a tag `v0.2.0` to GitHub, or
- Use GitHub Actions manual trigger (`workflow_dispatch`)

### 2. Confirm the build passes

- Navigate to Actions → Build macOS .app Bundle
- Confirm all steps pass

### 3. Download the artifact

- From the completed workflow run, download `VisualDuipai-macos-<sha>.zip`
- Rename to `VisualDuipai-v0.2.0-macos-arm64.zip`

### 4. Add to GitHub Release

Upload `VisualDuipai-v0.2.0-macos-arm64.zip` as a Release asset alongside the existing Windows and Linux assets.
```

- [ ] **Step 5: 提交**

```bash
cd "/home/yzx/文档/claude code/visual_duipai" && git add README.md CHANGELOG.md packaging/README.md docs/RELEASE.md && git commit -m "docs: add macOS .app bundle usage, release, and packaging instructions"
```

---
