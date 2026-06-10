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
