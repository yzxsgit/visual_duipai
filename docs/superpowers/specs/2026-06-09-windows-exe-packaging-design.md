# Windows EXE 打包设计

## 背景

`visual_duipai/` 已有 Python 桌面 GUI 对拍工具：

- `duipai_gui.py`：GUI 入口。
- `stress_core.py`：编译、运行、比较、停止等核心逻辑。
- `requirements.txt`：运行依赖。

新目标是提供一个通用打包框架，先支持 Windows `.exe`，未来可扩展 macOS / Linux 打包方式。

## 采用方案

使用 PyInstaller 做 Windows 打包。

新增文件：

- `build_exe.ps1`：Windows 一键打包脚本。
- `packaging/README.md`：打包说明，记录 Windows 当前支持方式，以及 macOS / Linux 未来扩展原则。

修改文件：

- `.gitignore`：忽略 PyInstaller 生成的临时目录和产物目录。

不修改：

- `duipai_gui.py`
- `stress_core.py`
- `test_stress_core.py`
- 父目录已有 `force.cpp`、`gptanswer.cpp`、`gen.cpp`、`duipai.sh`

## Windows 打包流程

用户在 PowerShell 中进入仓库目录：

```powershell
cd D:\yzx\Documents\claude_code\duipai\visual_duipai
.\build_exe.ps1
```

脚本执行：

1. 检查当前目录存在 `duipai_gui.py`。
2. 检查 Python 可用。
3. 安装或确认运行依赖：
   ```powershell
   python -m pip install -r requirements.txt
   ```
4. 安装或确认 PyInstaller：
   ```powershell
   python -m pip install pyinstaller
   ```
5. 清理旧打包输出：
   - `build/`
   - `dist/`
6. 执行 PyInstaller：
   ```powershell
   python -m PyInstaller --noconsole --onefile --name VisualDuipai duipai_gui.py
   ```
7. 如果打包成功，输出：
   ```text
   dist/VisualDuipai.exe
   ```

## tkinterdnd2 处理

`tkinterdnd2` 有时需要 PyInstaller 额外收集资源。

本阶段采用优先简单策略：

```powershell
python -m PyInstaller --noconsole --onefile --name VisualDuipai --collect-all tkinterdnd2 duipai_gui.py
```

如果目标环境的 PyInstaller 不支持 `--collect-all`，脚本应提示用户升级 PyInstaller，而不是静默失败。

## 产物与忽略规则

打包生成内容：

- `build/`
- `dist/VisualDuipai.exe`
- `VisualDuipai.spec`

本阶段不定制 `.spec` 文件，因此 `.spec` 作为临时产物忽略。

`.gitignore` 增加：

```gitignore
/build/
/dist/
*.spec
```

如果后续需要定制 spec 文件以修复资源收集问题，再把固定 `.spec` 纳入版本管理。

## 使用限制

打包后的 `.exe` 包含 GUI 程序本身和 Python 依赖，但不包含 C++ 编译器。

因此使用者电脑仍需要安装并配置：

```powershell
g++ --version
```

如果 `g++` 不可用，GUI 可以启动，但开始对拍时会在日志中提示找不到编译器。

## 多平台原则

`.exe` 只适用于 Windows。

未来扩展：

- macOS：在 macOS 上使用 PyInstaller 打包 `.app` 或 macOS 可执行文件。
- Linux：在 Linux 上使用 PyInstaller 打包 Linux 可执行文件，或进一步封装为 AppImage。

不在 Windows 上交叉打包 macOS / Linux 产物。

## 验证方式

实现后验证：

1. 运行测试：
   ```powershell
   python -m unittest discover -p "test*.py"
   ```
2. 运行打包脚本：
   ```powershell
   .\build_exe.ps1
   ```
3. 确认文件存在：
   ```powershell
   Test-Path .\dist\VisualDuipai.exe
   ```
4. 启动 exe：
   ```powershell
   .\dist\VisualDuipai.exe
   ```
5. 确认 GUI 窗口能打开。

如果无法在自动化环境中长期保持 GUI 打开，至少执行短启动或用户手动双击验证。

## 非目标

本次不实现：

- macOS 打包脚本。
- Linux 打包脚本。
- AppImage。
- 安装包 MSI。
- 自动内置 g++。
- 自定义图标。

这些作为后续增强。