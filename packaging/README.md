# VisualDuipai Packaging

This project is packaged with PyInstaller.

## Windows EXE

From PowerShell, run:

Replace <path-to-visual_duipai> with the folder where this repository is checked out.

```powershell
cd <path-to-visual_duipai>
.\build_exe.ps1
```

If PowerShell blocks script execution, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
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

## Linux AppImage

### 前提

- Linux 系统（推荐 Ubuntu 20.04+）
- `python3` 和 `pip` 已安装
- `g++` 已安装（仅用于构建检查，不打包进 AppImage）

### 一键打包

```bash
./build_linux.sh
```

输出：

```text
dist/VisualDuipai-x86_64.AppImage
```

### 手动验证

```bash
# 赋予执行权限
chmod +x dist/VisualDuipai-x86_64.AppImage

# 启动
./dist/VisualDuipai-x86_64.AppImage
```

### AppImage 运行要求

运行 AppImage 的系统需安装：
- `libfuse2`（大多数发行版内置；若缺失，运行 `sudo apt install libfuse2`）
- `g++` 并在 `PATH` 中

### 打包原理

1. PyInstaller 将 `duipai_gui.py` 和 Python 依赖打包为单文件二进制
2. 构建标准 AppDir 结构（AppRun + .desktop + 图标 + 二进制）
3. appimagetool 将 AppDir 封装为 AppImage

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
