# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

VisualDuipai（对拍可视化工具）是一个算法竞赛本地对拍 GUI 工具，支持 Windows 和 Linux。用户选择三个 C++ 源文件（暴力程序、正解程序、数据生成器），工具自动编译后在循环中：生成数据 → 分别运行两个程序 → 比较输出，发现不一致时保留输入/输出/diff 文件。

技术栈：Python 3 + customtkinter + tkinterdnd2，通过 PyInstaller 打包为单文件可执行程序。

## 常用命令

```bash
# 运行 GUI
python3 duipai_gui.py

# 安装依赖
python3 -m pip install --break-system-packages -r requirements.txt

# 运行所有测试
python3 -m unittest discover -p "test*.py"

# 打包 Windows EXE（PowerShell）
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1

# 打包 Linux AppImage
./build_linux.sh
```

## 打包

### Linux AppImage

运行 `./build_linux.sh`，产出 `dist/VisualDuipai-x86_64.AppImage`。

脚本 6 个步骤：检查依赖（python3/g++/wget）→ pip install → PyInstaller 打包 → 构建 AppDir → 下载 appimagetool → 生成 AppImage。

PyInstaller 参数与 Windows 对齐：`--onefile --noconsole --name VisualDuipai --collect-all tkinterdnd2`。

**构建环境要求**：
- `sudo apt install python3-tk libfuse2`（tkinter 是 PyInstaller 打包时需要的，libfuse2 是 appimagetool 运行时需要的）
- `pip install` 需要 `--break-system-packages`（PEP 668 环境）

**AppDir 布局**：标准的 `AppRun` + `VisualDuipai.desktop`（`Exec=usr/bin/VisualDuipai`）+ `usr/bin/VisualDuipai`。

图标复制到 4 个位置以兼容不同桌面环境：
- `VisualDuipai.png` — .desktop 文件引用
- `.DirIcon` — 文件管理器缩略图
- `usr/share/icons/hicolor/256x256/apps/VisualDuipai.png` — 桌面菜单集成
- `usr/share/pixmaps/VisualDuipai.png` — 部分 DE/FM 图标查找路径

**产物管理**：`/AppDir/`、`*.AppImage`、`/build/`、`/dist/`、`/squashfs-root/` 均在 `.gitignore` 中。

**常见构建问题**：
| 症状 | 原因 | 解决 |
|---|---|---|
| `pip install` 报 PEP 668 错误 | 新版 Linux Python 拒绝系统级 pip | 已加 `--break-system-packages` |
| `ModuleNotFoundError: tkinter` | PyInstaller 打包时缺少 tkinter | `sudo apt install python3-tk` |
| appimagetool 报 `libfuse.so.2` | 缺少 FUSE 库 | `sudo apt install libfuse2` |
| AppImage 图标不显示 | 尺寸/路径不符合标准 | 图标 256x256 + 四处路径 |

### Windows EXE

`build_exe.ps1` 通过 PyInstaller 产出 `dist/VisualDuipai.exe`。详见 `packaging/README.md`。

## 架构

### 模块分工

- **`stress_core.py`** — 纯逻辑层，无 GUI 依赖。包含编译、运行子进程、输出比较、diff 生成。所有函数接受可选的 `stop_event: threading.Event` 用于外部中断。
- **`duipai_gui.py`** — GUI 层，使用 customtkinter。通过 `threading.Thread` + `queue.Queue` 将后台对拍工作与 UI 线程解耦。

### 线程模型

GUI 是单主线程（tkinter 要求）。点击"开始对拍"后启动一个 daemon worker 线程执行 `_worker()`，worker 通过 `self.events` 队列向主线程发送 `("log", msg)` 和 `("progress", ratio)` 事件。主线程通过 `after(100, _drain_events)` 定时轮询队列并更新 UI。

**关键约束**：worker 线程绝不能直接操作 tkinter widget，所有 UI 更新必须通过事件队列。

### 子进程管理

`stress_core.run_command()` 用一个轮询循环（`time.sleep(0.05)`）同时监控超时和 stop_event。被中断时先 `terminate()`，1 秒后未退出则 `kill()`。finally 块确保进程资源释放。

### 输出比较策略

`compare_outputs()` 按字节级别比较，但忽略行尾 ASCII 空白字符（空格、制表符、回车）和文件末尾空行。这意味着 `"1  \n2\n"` 和 `"1\n2\n"` 被视为一致。设计理由是算法题评测通常忽略行末空白。

### GUI 样式

- 暗色主题（`ctk.set_appearance_mode("dark")`）
- 标题"对拍可视化工具"和副标题使用 `text_color="black"` 以确保在暗色背景上清晰可读
- 三个 DropCard 支持拖入 `.cpp` 文件或点击选择

### 路径约定

`StressPaths` 数据类集中管理工作目录下所有文件路径（可执行文件、input.txt、force.out、answer.out、diff.out）。`ensure_work_dir()` 创建目录并返回绝对路径的 `StressPaths` 实例。

### 图标

`assets/VisualDuipai.png` — 256x256 RGBA PNG，"二分叉再汇聚"设计。由 `assets/generate_icon.py` 用 Pillow 生成。

## 平台注意

- 运行对拍需要系统安装 `g++` 且在 PATH 中——AppImage/EXE 均不含编译器。
- `os.startfile()` 用于打开工作目录，Linux/macOS 回退到 `xdg-open`。
- `executable_name()` 在 Windows 上追加 `.exe` 后缀。
- Linux 构建需要 `python3-tk` 和 `libfuse2` 系统包。

## 设计文档

设计文档和实现计划位于 `docs/superpowers/` 目录下：
- `specs/` — 功能设计规格
- `plans/` — 实现任务计划
