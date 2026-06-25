# Linux AppImage 打包设计

日期: 2026-06-25
状态: 待审查

## 目标

为 VisualDuipai 增加 Linux AppImage 打包支持。用户下载单个 `.AppImage` 文件即可运行，无需安装 Python 依赖。g++ 仍需用户系统提供，和 Windows 版本保持一致。

## 整体流程

`build_linux.sh` 一键完成全部步骤：

```
依赖检查 → pip 安装 → PyInstaller 打包 → 构建 AppDir → 下载 appimagetool → 生成 AppImage
```

产物：`dist/VisualDuipai-x86_64.AppImage`

## 脚本设计

### 语言与错误处理

- Bash 脚本，`#!/usr/bin/env bash`
- `set -euo pipefail` 确保任何命令失败即退出
- 每个步骤打印 `[N/6] 描述...` 进度提示

### 步骤拆分

1. **依赖检查** — 检查 `python3` 和 `pip` 可用性；检查 `g++` 可用性（提醒用户打包环境需有 g++ 才能跑对拍功能，但 g++ 不打包进 AppImage）
2. **安装 Python 依赖** — `pip install -r requirements.txt pyinstaller`
3. **PyInstaller 打包** — 产出 `dist/VisualDuipai` 单文件二进制。参数与 Windows 对齐：
   ```
   --onefile --noconsole --name VisualDuipai --collect-all tkinterdnd2 duipai_gui.py
   ```
4. **清理旧 AppDir** — 移除 `AppDir/` 目录（如存在）
5. **构建 AppDir** — 标准 AppImage 目录结构（见下）
6. **生成 AppImage** — 下载 `appimagetool`（如未缓存则从 GitHub 获取），运行封装，产出 `dist/VisualDuipai-x86_64.AppImage`

### AppDir 布局

```
AppDir/
├── AppRun                    ← 启动脚本（#!/bin/bash）
├── VisualDuipai.desktop      ← 桌面入口文件
├── VisualDuipai.png          ← 应用图标（256x256 PNG）
└── usr/
    └── bin/
        └── VisualDuipai      ← PyInstaller 产物
```

- **AppRun**：简单的 `#!/bin/bash` 脚本，定位自身所在目录，`exec "$APPDIR/usr/bin/VisualDuipai" "$@"`
- **.desktop** 内容：
  ```
  [Desktop Entry]
  Name=VisualDuipai
  Comment=算法对拍可视化工具
  Exec=VisualDuipai
  Icon=VisualDuipai
  Type=Application
  Categories=Development;
  Terminal=false
  ```
- **图标**：260x260 PNG，设计为"二分叉再汇聚"——箭头分叉为两条路径，经菱形判断节点后汇聚，表达对拍工作流。图标文件放在项目根目录 `assets/VisualDuipai.png`，构建时复制进 AppDir

### appimagetool 获取策略

- 下载到 `/tmp/appimagetool`（`/tmp` 在重启后自动清理，适合缓存）
- 如果已存在且可执行则跳过下载
- 下载地址：`https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-$(uname -m).AppImage`
- 构建命令：`ARCH=x86_64 /tmp/appimagetool AppDir dist/VisualDuipai-x86_64.AppImage`

## 与 Windows 脚本的差异

| 项 | Windows (`build_exe.ps1`) | Linux (`build_linux.sh`) |
|---|---|---|
| 脚本语言 | PowerShell | Bash |
| 错误处理 | `Invoke-NativeCommand` + `$LASTEXITCODE` | `set -euo pipefail` |
| 输出文件 | `dist/VisualDuipai.exe` | `dist/VisualDuipai-x86_64.AppImage` |
| 进程管理 | 构建前杀旧 VisualDuipai 进程 | 不杀进程（Linux 上构建和运行通常不同环境） |
| 打包工具 | PyInstaller 直接出 EXE | PyInstaller 出二进制 → appimagetool 封装 |
| 额外步骤 | 无 | 构建 AppDir、下载 appimagetool |
| 图标 | 无需（Windows EXE 无图标需求） | 需要 PNG 图标嵌入 AppImage |

## 图标设计

二分叉再汇聚：

- 左侧一个实心圆点（起点），分出上下两条路径（弧线或折线）
- 上路径标注 "暴力"，下路径标注 "正解"
- 右侧一个菱形节点，两条路径汇聚到菱形
- 菱形右侧一个箭头指向终点
- 配色：蓝色系（`#1f6feb`）为主，橙色（`#db6d28`）为点缀
- 格式：260x260 PNG，透明背景

存放位置：`assets/VisualDuipai.png`

## 代码改动

### 新增文件

- `build_linux.sh` — 构建脚本
- `assets/VisualDuipai.png` — 应用图标

### 修改文件

- `README.md` — 在"推荐使用方式"下增加 Linux AppImage 使用说明
- `CHANGELOG.md` — 记录 Linux AppImage 打包支持
- `docs/RELEASE.md` — 增加 Linux 发布 checklist
- `packaging/README.md` — 增加 Linux 打包说明
- `.gitignore` — 添加 `AppDir/` 和 `*.AppImage`

### 不改动

- `stress_core.py` — 无需改动
- `duipai_gui.py` — 无需改动（`xdg-open` 回退已存在）
- `build_exe.ps1` — 无需改动

## 测试策略

### 构建环境测试

在构建完成后，手动执行：

```bash
# 确认 AppImage 可执行
chmod +x dist/VisualDuipai-x86_64.AppImage
test -f dist/VisualDuipai-x86_64.AppImage && echo "PASS: AppImage exists"

# 确认 AppRun 可执行
chmod +x AppDir/AppRun
test -x AppDir/AppRun && echo "PASS: AppRun executable"

# 确认图标存在
test -f assets/VisualDuipai.png && echo "PASS: icon present"

# 确认 .desktop 文件有效
grep -q "Name=VisualDuipai" AppDir/VisualDuipai.desktop && echo "PASS: desktop file valid"
```

### 功能验证

在 Linux 桌面环境上：

1. 启动 AppImage，GUI 正常打开
2. 选择三个 C++ 文件，执行对拍，输出正确
3. "打开工作目录"按钮可用（调用 xdg-open）
4. 拖拽文件功能正常

### 兼容性验证

- 在 Ubuntu 20.04 上构建
- 在 Ubuntu 22.04 / 24.04 上运行测试
- 在 Debian 11 / 12 上运行测试

## 兼容性要求

- 构建环境：Ubuntu 20.04 或 Debian 11
- 运行时：g++ 在 PATH 中
- AppImage 不捆绑 glibc 等系统库，依赖宿主系统的 libfuse2（大多数 Linux 发行版已内置或可安装）
