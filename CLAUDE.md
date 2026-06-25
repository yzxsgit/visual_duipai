# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

VisualDuipai（对拍可视化工具）是一个算法竞赛本地对拍 GUI 工具。用户选择三个 C++ 源文件（暴力程序、正解程序、数据生成器），工具自动编译后在循环中：生成数据 → 分别运行两个程序 → 比较输出，发现不一致时保留输入/输出/diff 文件。

技术栈：Python 3 + customtkinter + tkinterdnd2，Windows 上通过 PyInstaller 打包为单文件 EXE。

## 常用命令

```powershell
# 运行 GUI
python duipai_gui.py

# 安装依赖
python -m pip install -r requirements.txt

# 运行所有测试
python -m unittest discover -p "test*.py"

# 打包 Windows EXE
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```

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

### 路径约定

`StressPaths` 数据类集中管理工作目录下所有文件路径（可执行文件、input.txt、force.out、answer.out、diff.out）。`ensure_work_dir()` 创建目录并返回绝对路径的 `StressPaths` 实例。

### 打包

`build_exe.ps1` 通过 `Invoke-NativeCommand` 封装所有外部命令调用，检查 `$LASTEXITCODE` 确保错误传播。PyInstaller 使用 `--onefile --noconsole --collect-all tkinterdnd2` 参数。打包产物（`dist/`、`build/`、`*.spec`）不提交 Git。

## 平台注意

- 目标平台是 Windows，GUI 和打包脚本均为 Windows 设计。
- `os.startfile()` 用于打开工作目录，Linux/macOS 回退到 `xdg-open`。
- `executable_name()` 在 Windows 上追加 `.exe` 后缀。
- 运行对拍需要系统安装 `g++` 且在 PATH 中——EXE 不含编译器。
