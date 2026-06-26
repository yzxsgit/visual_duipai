# macOS .app Bundle 打包设计

日期: 2026-06-26
状态: 待审查

## 目标

为 VisualDuipai 增加 macOS 打包支持，通过 GitHub Actions 在 macOS runner 上自动构建 `.app` Bundle。用户下载 `.app` 文件即可运行，无需安装 Python 依赖。g++ 仍需用户系统提供（`xcode-select --install`），和其他平台一致。

## 整体流程

GitHub Actions workflow（`.github/workflows/build_macos.yml`）在 `macos-latest` runner 上执行：

```
checkout → 安装依赖 → PyInstaller 打包 → 构建 .app Bundle → 上传 Artifact
```

产物：`VisualDuipai.app`，zip 后作为 CI Artifact 或 Release asset。

## .app Bundle 结构

```
VisualDuipai.app/
└── Contents/
    ├── Info.plist              ← 应用元数据
    ├── MacOS/
    │   └── VisualDuipai        ← PyInstaller 单文件二进制
    └── Resources/
        └── VisualDuipai.icns   ← macOS 图标
```

### Info.plist

```xml
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
```

## 图标转换

`assets/VisualDuipai.png`（256x256 RGBA PNG）→ `VisualDuipai.icns`。

macOS 要求 `.icns` 格式，支持多种分辨率。将 PNG 转换为 ICNS 有两种方式：

1. **GitHub Actions runner 上**：macOS 自带 `iconutil`，需先将 PNG 转为 `.iconset` 目录，再用 `iconutil -c icns` 生成
2. **Python Pillow 生成**：用 `pip install pillow` 的 `png2icns`（但不够可靠）

推荐方案 1，因为 GitHub Actions 的 macOS runner 自带 `iconutil`。

转换步骤：
```bash
# 创建 iconset 目录
mkdir -p VisualDuipai.iconset
# macOS iconset 需要 16x16 ~ 512x512@2x 多种尺寸
# 从 256x256 缩放到所需尺寸
sips -z 16 16 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_16x16.png
sips -z 32 32 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_16x16@2x.png
sips -z 32 32 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_32x32.png
sips -z 64 64 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_32x32@2x.png
sips -z 128 128 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_128x128.png
sips -z 256 256 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_128x128@2x.png
sips -z 256 256 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_256x256.png
# 512是放大 256 的，效果可接受
sips -z 512 512 assets/VisualDuipai.png --out VisualDuipai.iconset/icon_256x256@2x.png
# 转为 icns
iconutil -c icns VisualDuipai.iconset -o VisualDuipai.icns
```

## PyInstaller 参数

与 Linux/Windows 对齐。macOS 的 `--noconsole` 无效但加上无副作用：

```bash
python3 -m PyInstaller \
    --onefile \
    --noconsole \
    --name VisualDuipai \
    --collect-all tkinterdnd2 \
    duipai_gui.py
```

产物：`dist/VisualDuipai`（单文件二进制）

## GitHub Actions Workflow

### 文件位置

`.github/workflows/build_macos.yml`

### 触发条件

```yaml
on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:
```

### Job 步骤

1. **Checkout** — `actions/checkout@v4`
2. **安装 Python** — `actions/setup-python@v5`，Python 3.12
3. **安装依赖** — `pip install -r requirements.txt pyinstaller`
4. **PyInstaller 打包** — 产出单文件二进制
5. **构建 .app Bundle** — 创建目录结构、写入 Info.plist、转换图标
6. **打包为 zip** — `zip -r VisualDuipai.app.zip VisualDuipai.app`
7. **上传 Artifact** — `actions/upload-artifact@v4`

### On Release（tag push）

仅在有 tag 时额外添加 Release 步骤：

1. 创建 GitHub Release
2. 上传 `.app.zip` 为 Release asset

## GUI 适配

macOS 上 `os.startfile()` 不存在，目前代码已有 `xdg-open` 回退逻辑（用于 Linux）。macOS 需要用 `open` 命令。需要修改 `duipai_gui.py` 的 `_open_work_dir` 方法：

```python
# 在 except AttributeError 块中
try:
    import os
    os.startfile(paths.work_dir)
except AttributeError:
    import subprocess
    try:
        # macOS
        subprocess.Popen(["open", str(paths.work_dir)])
    except FileNotFoundError:
        # Linux
        subprocess.Popen(["xdg-open", str(paths.work_dir)])
```

## 与 Linux/Windows 的差异

| 项 | Windows | Linux | macOS |
|---|---|---|---|
| 构建方式 | 本地脚本 | 本地脚本 | GitHub Actions |
| 构建脚本 | `build_exe.ps1` | `build_linux.sh` | `.github/workflows/build_macos.yml` |
| 产物 | `VisualDuipai.exe` | `VisualDuipai-x86_64.AppImage` | `VisualDuipai.app.zip` |
| 图标格式 | 无需 | PNG 256x256 | ICNS |
| 元数据 | 无 | .desktop 文件 | Info.plist |
| 打开目录 | `os.startfile()` | `xdg-open` | `open` |
| g++ 依赖 | 用户系统装 MinGW | 用户系统装 g++ | 用户装 Xcode CLI |

## 代码改动

### 新增文件

- `.github/workflows/build_macos.yml` — GitHub Actions workflow

### 修改文件

- `duipai_gui.py` — 增加 macOS `open` 命令支持
- `README.md` — 增加 macOS 使用说明
- `CHANGELOG.md` — 记录
- `packaging/README.md` — 增加 macOS 打包说明
- `docs/RELEASE.md` — 增加 macOS 发布 checklist

### 不改动

- `stress_core.py` — 无需改动
- `build_linux.sh` — 无需改动
- `build_exe.ps1` — 无需改动
- `assets/generate_icon.py` — 无需改动（图标生成在 workflow 中处理）

## 注意事项

1. **macOS Gatekeeper**：未签名的 .app 在 macOS 上首次启动会被阻止，需要用户右键 → 打开。这是 macOS 安全策略，和 Windows SmartScreen 类似。
2. **arch 问题**：ARM Mac（Apple Silicon）可以运行 x86_64 二进制（Rosetta），但如果构建在 ARM runner 上，产出的二进制不兼容 Intel Mac。`macos-latest` 目前是 ARM runner，产物仅适用于 Apple Silicon Mac。如果需要同时支持两种架构，需要分两个 job 构建，或者等 GitHub 提供 multi-arch runner。
3. **tcl/tk 兼容性**：macOS 自带的 Tcl/Tk 可能版本较老，建议 PyInstaller 打包时带上 tcl/tk 依赖。`--collect-all tkinterdnd2` 已经处理了。
4. **可维护性**：GitHub Actions 的 free tier 有 2000 分钟/月，每次构建约 3-5 分钟，足够日常使用。
