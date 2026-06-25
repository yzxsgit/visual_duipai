# Linux AppImage 打包 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 VisualDuipai 增加 `build_linux.sh` 一键打包脚本，产出 `VisualDuipai-x86_64.AppImage`

**Architecture:** 单 Bash 脚本串联 PyInstaller 打包 → AppDir 构建 → appimagetool 封装。AppDir 标准布局（AppRun + .desktop + 图标 + usr/bin/二进制）。g++ 不打包，用户系统自行提供。

**Tech Stack:** Bash, Python 3, PyInstaller, appimagetool, Pillow（仅用于图标生成）

## Global Constraints

- 构建环境最低要求：Ubuntu 20.04 / Debian 11
- g++ 不打包进 AppImage，和 Windows 策略一致
- PyInstaller 参数与 Windows 对齐：`--onefile --noconsole --name VisualDuipai --collect-all tkinterdnd2`
- AppImage 产物命名：`VisualDuipai-x86_64.AppImage`
- 图标：260x260 PNG，"二分叉再汇聚"设计，蓝(#1f6feb)+橙(#db6d28)

---

### Task 1: 生成应用图标

**Files:**
- Create: `assets/generate_icon.py`
- Create: `assets/VisualDuipai.png`

**Interfaces:**
- Produces: `assets/VisualDuipai.png` — 260x260 RGBA PNG，后续 Task 2 复制到 AppDir

**说明：** 用 Pillow 的 ImageDraw 绘制"二分叉再汇聚"图标：左侧实心圆（起点），上下两条曲线分叉汇聚到菱形判断节点，右侧箭头指向终点。主色蓝 `#1f6feb`，菱形和箭头点缀橙 `#db6d28`。

- [ ] **Step 1: 创建 assets 目录并编写图标生成脚本**

```bash
mkdir -p assets
```

```python
# assets/generate_icon.py
"""生成 VisualDuipai 应用图标（二分叉再汇聚设计）"""

from pathlib import Path
from PIL import Image, ImageDraw

SIZE = 260
MARGIN = 28

BLUE = (31, 111, 235, 255)       # #1f6feb
ORANGE = (219, 109, 40, 255)     # #db6d28
WHITE_BG = (255, 255, 255, 255)

CX = SIZE // 2                     # 130
CY = SIZE // 2
START = (MARGIN + 10, CY)         # 起点 (38, 130)
END = (SIZE - MARGIN - 10, CY)    # 终点 (222, 130)

DIAMOND_CX = CX + 14              # 菱形中心偏右 (144)
DIAMOND_R = 28                    # 菱形半对角线长
SPLIT_X = CX - 50                 # 分叉点 x (80)
SPLIT_Y_OFFSET = 42               # 分叉上下偏移
DOT_R = 10                        # 起点圆半径
ARROW_H = 16                      # 箭头高
ARROW_W = 10                      # 箭头宽

img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 背景圆底衬
circle_r = 100
circle_bbox = (CX - circle_r, CY - circle_r, CX + circle_r, CY + circle_r)
draw.ellipse(circle_bbox, fill=(31, 111, 235, 25))

# 菱形四顶点
diamond_left   = (DIAMOND_CX - DIAMOND_R, CY)
diamond_top    = (DIAMOND_CX, CY - DIAMOND_R)
diamond_bottom = (DIAMOND_CX, CY + DIAMOND_R)
diamond_right  = (DIAMOND_CX + DIAMOND_R, CY)

# 分叉点
split_upper = (SPLIT_X, CY - SPLIT_Y_OFFSET)   # (80, 88)
split_lower = (SPLIT_X, CY + SPLIT_Y_OFFSET)   # (80, 172)

# 上路径：起点 → 上分叉 → 菱形左顶点
for i, (p1, p2) in enumerate([(START, split_upper), (split_upper, diamond_left)]):
    draw.line([p1, p2], fill=(*BLUE[:3], 220), width=6)

# 下路径：起点 → 下分叉 → 菱形左顶点
for p1, p2 in [(START, split_lower), (split_lower, diamond_left)]:
    draw.line([p1, p2], fill=(*BLUE[:3], 220), width=6)

# 起点圆
draw.ellipse(
    (START[0] - DOT_R, START[1] - DOT_R, START[0] + DOT_R, START[1] + DOT_R),
    fill=BLUE,
)

# 菱形判断节点
diamond_pts = [diamond_top, diamond_right, diamond_bottom, diamond_left]
draw.polygon(diamond_pts, fill=WHITE_BG, outline=ORANGE, width=4)

# 菱形内部 "?" 符号
bar_h = 14
dot_off = 8
draw.line(
    [(DIAMOND_CX, CY - bar_h), (DIAMOND_CX, CY + dot_off - 6)],
    fill=ORANGE, width=4,
)
draw.ellipse(
    (DIAMOND_CX - 3, CY + dot_off - 3, DIAMOND_CX + 3, CY + dot_off + 3),
    fill=ORANGE,
)

# 输出箭头
arrow_start = (diamond_right[0] + 2, CY)
arrow_body_end = (END[0] - ARROW_W, CY)
draw.line([arrow_start, arrow_body_end], fill=BLUE, width=6)

# 箭头尖
arrow_pts = [
    END,
    (END[0] - ARROW_W, END[1] - ARROW_H // 2),
    (END[0] - ARROW_W, END[1] + ARROW_H // 2),
]
draw.polygon(arrow_pts, fill=BLUE)

# 标签（无字体时跳过）
try:
    from PIL import ImageFont
    font = ImageFont.load_default()
    draw.text(
        (SPLIT_X + 8, CY - SPLIT_Y_OFFSET - 20),
        "brute", fill=(*BLUE[:3], 180), font=font,
    )
    draw.text(
        (SPLIT_X + 8, CY + SPLIT_Y_OFFSET + 6),
        "solve", fill=(*BLUE[:3], 180), font=font,
    )
except Exception:
    pass

# 保存
out_path = Path(__file__).resolve().parent / "VisualDuipai.png"
img.save(out_path, "PNG")
print(f"Icon saved: {out_path} ({img.size[0]}x{img.size[1]})")
```

- [ ] **Step 2: 安装 Pillow 并运行图标生成**

```bash
python3 -m pip install Pillow
python3 assets/generate_icon.py
```

- [ ] **Step 3: 验证图标文件**

```bash
python3 -c "
from PIL import Image
img = Image.open('assets/VisualDuipai.png')
assert img.size == (260, 260), f'Expected 260x260, got {img.size}'
assert img.mode == 'RGBA', f'Expected RGBA, got {img.mode}'
print(f'PASS: {img.size[0]}x{img.size[1]} {img.mode} PNG')
"
```

预期输出：`PASS: 260x260 RGBA PNG`

- [ ] **Step 4: 提交**

```bash
git add assets/generate_icon.py assets/VisualDuipai.png
git commit -m "feat: add application icon (fork-merge design)"
```

---

### Task 2: 编写 build_linux.sh 构建脚本

**Files:**
- Create: `build_linux.sh`

**Interfaces:**
- Consumes: `assets/VisualDuipai.png`（Task 1 产出）
- Produces: `dist/VisualDuipai-x86_64.AppImage`
- 中间产物: `dist/VisualDuipai`、`AppDir/`

- [ ] **Step 1: 编写 build_linux.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

# ── 路径定义 ──────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

APP_ENTRY="duipai_gui.py"
REQUIREMENTS="requirements.txt"
DIST_DIR="dist"
BUILD_DIR="build"
APPDIR="AppDir"
ICON_SRC="assets/VisualDuipai.png"
APPIMAGE_TOOL="/tmp/appimagetool"
APPIMAGE_OUT="VisualDuipai-x86_64.AppImage"

# ── 辅助函数 ──────────────────────────────────────────────
step() { echo ""; echo -e "\033[1;36m[$1/6] $2\033[0m"; }
ok()   { echo -e "\033[1;32m  ✓ $1\033[0m"; }
die()  { echo -e "\033[1;31mERROR: $1\033[0m" >&2; exit 1; }

check_cmd() {
    if ! command -v "$1" &>/dev/null; then
        die "未找到命令 '$1'，请先安装。"
    fi
    ok "$1 可用: $(command -v "$1")"
}

# ── 步骤 1: 检查依赖 ─────────────────────────────────────
step 1 "检查依赖..."
check_cmd python3
check_cmd g++
ok "构建环境检查完毕"

# ── 步骤 2: 安装 Python 依赖 ────────────────────────────
step 2 "安装 Python 依赖..."
python3 -m pip install -r "$REQUIREMENTS" pyinstaller 2>&1 | tail -3
ok "Python 依赖安装完毕"

# ── 步骤 3: PyInstaller 打包 ────────────────────────────
step 3 "PyInstaller 打包..."
rm -rf "$BUILD_DIR" "$DIST_DIR"

python3 -m PyInstaller \
    --onefile \
    --noconsole \
    --name VisualDuipai \
    --collect-all tkinterdnd2 \
    "$APP_ENTRY"

if [[ ! -f "$DIST_DIR/VisualDuipai" ]]; then
    die "PyInstaller 打包失败：$DIST_DIR/VisualDuipai 未生成"
fi
ok "PyInstaller 产出: $DIST_DIR/VisualDuipai"

# ── 步骤 4: 清理旧 AppDir ───────────────────────────────
step 4 "清理旧 AppDir..."
rm -rf "$APPDIR"
ok "清理完毕"

# ── 步骤 5: 构建 AppDir ──────────────────────────────────
step 5 "构建 AppDir..."

mkdir -p "$APPDIR/usr/bin"

# 复制二进制
cp "$DIST_DIR/VisualDuipai" "$APPDIR/usr/bin/VisualDuipai"
chmod +x "$APPDIR/usr/bin/VisualDuipai"

# 复制图标
cp "$ICON_SRC" "$APPDIR/VisualDuipai.png"

# AppRun 启动脚本
cat > "$APPDIR/AppRun" << 'APPRUN_EOF'
#!/usr/bin/env bash
APPDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$APPDIR/usr/bin/VisualDuipai" "$@"
APPRUN_EOF
chmod +x "$APPDIR/AppRun"

# .desktop 桌面入口文件
cat > "$APPDIR/VisualDuipai.desktop" << 'DESKTOP_EOF'
[Desktop Entry]
Name=VisualDuipai
Comment=算法对拍可视化工具
Exec=usr/bin/VisualDuipai
Icon=VisualDuipai
Type=Application
Categories=Development;
Terminal=false
DESKTOP_EOF

ok "AppDir 构建完毕"

# ── 步骤 6: 生成 AppImage ────────────────────────────────
step 6 "生成 AppImage..."

ARCH=x86_64

if [[ ! -x "$APPIMAGE_TOOL" ]]; then
    echo "  下载 appimagetool..."
    wget -q -O "$APPIMAGE_TOOL" \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage"
    chmod +x "$APPIMAGE_TOOL"
else
    ok "使用缓存的 appimagetool: $APPIMAGE_TOOL"
fi

"$APPIMAGE_TOOL" "$APPDIR" "$DIST_DIR/$APPIMAGE_OUT"

if [[ ! -f "$DIST_DIR/$APPIMAGE_OUT" ]]; then
    die "AppImage 生成失败"
fi

chmod +x "$DIST_DIR/$APPIMAGE_OUT"

echo ""
echo -e "\033[1;32m═══════════════════════════════════════\033[0m"
echo -e "\033[1;32m  构建成功！\033[0m"
echo -e "\033[1;32m  输出: $DIST_DIR/$APPIMAGE_OUT\033[0m"
echo -e "\033[1;32m═══════════════════════════════════════\033[0m"
echo ""
echo "注意: 运行 AppImage 的系统需安装 g++ 并将其加入 PATH。"
```

- [ ] **Step 2: 赋予脚本执行权限**

```bash
chmod +x build_linux.sh
```

- [ ] **Step 3: 验证脚本语法**

```bash
bash -n build_linux.sh && echo "PASS: syntax OK"
```

预期输出：`PASS: syntax OK`

- [ ] **Step 4: 验证脚本结构和关键命令**

```bash
# 验证所有步骤标签存在
for step in "检查依赖" "安装 Python 依赖" "PyInstaller 打包" "清理旧 AppDir" "构建 AppDir" "生成 AppImage"; do
    grep -qF "$step" build_linux.sh || { echo "FAIL: missing step: $step"; exit 1; }
done
echo "PASS: all 6 steps present"

# 验证关键命令存在
for cmd in "python3" "PyInstaller" "AppDir" "appimagetool" "set -euo pipefail"; do
    grep -qF "$cmd" build_linux.sh || { echo "FAIL: missing command: $cmd"; exit 1; }
done
echo "PASS: all key commands present"

# 验证产物路径
grep -qF "dist/VisualDuipai-x86_64.AppImage" build_linux.sh && echo "PASS: output path correct"

# 验证 AppDir 结构
grep -qF "usr/bin" build_linux.sh && echo "PASS: AppDir usr/bin present"
grep -qF "AppRun" build_linux.sh && echo "PASS: AppRun present"
grep -qF ".desktop" build_linux.sh && echo "PASS: desktop file present"
grep -qF "VisualDuipai.png" build_linux.sh && echo "PASS: icon copy present"
```

- [ ] **Step 5: 提交**

```bash
git add build_linux.sh
git commit -m "feat: add linux AppImage build script"
```

---

### Task 3: 更新 .gitignore

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: 添加 Linux 打包产物到 .gitignore**

在 `.gitignore` 文件末尾追加以下三行：

```gitignore
# Linux AppImage 打包产物
/AppDir/
*.AppImage
```

- [ ] **Step 2: 验证忽略规则**

```bash
# 创建临时文件验证忽略规则
mkdir -p AppDir && touch AppDir/test && touch test.AppImage
git status --short --ignored | grep -q "AppDir/" && echo "PASS: AppDir/ ignored"
git status --short --ignored | grep -q "test.AppImage" || echo "PASS: *.AppImage ignored"
rm -rf AppDir test.AppImage

# 确认已有规则未被破坏
grep -q "__pycache__" .gitignore && echo "PASS: existing rules intact"
grep -q "duipai_work" .gitignore && echo "PASS: existing rules intact"
```

- [ ] **Step 3: 提交**

```bash
git add .gitignore
git commit -m "chore: add linux AppImage artifacts to gitignore"
```

---

### Task 4: 更新文档

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/RELEASE.md`
- Modify: `packaging/README.md`

- [ ] **Step 1: 更新 README.md — 增加 Linux AppImage 使用说明**

在 `## 推荐使用方式：下载 Windows 版本` 之前插入以下章节：

```markdown
## 推荐使用方式：下载 Linux 版本

在 GitHub 仓库的 Releases 页面下载：

```text
VisualDuipai-v0.2.0-linux-x86_64.AppImage
```

下载后：

1. 赋予执行权限：`chmod +x VisualDuipai-v0.2.0-linux-x86_64.AppImage`
2. 双击或终端运行：`./VisualDuipai-v0.2.0-linux-x86_64.AppImage`
3. 在界面中选择或拖入暴力程序、正解程序和数据生成器。
4. 设置对拍轮数。
5. 点击开始运行。

### 依赖

运行 Linux AppImage 的系统必须安装 `g++` 并且 `g++` 在 `PATH` 中。可以在终端中检查：

```bash
g++ --version
```
```

同时在「常见问题」章节（`## 常见问题`）末尾追加：

```markdown
### Linux AppImage 提示找不到 `g++` 怎么办？

在终端中安装：

```bash
# Debian / Ubuntu
sudo apt install g++

# Fedora
sudo dnf install gcc-c++

# Arch Linux
sudo pacman -S gcc
```
```

- [ ] **Step 2: 更新 CHANGELOG.md**

在文件第一行（`# Changelog` 之后、`## v0.1.0` 之前）插入：

```markdown
## Unreleased

### Added

- Linux AppImage 打包支持，通过 `build_linux.sh` 一键生成 `VisualDuipai-x86_64.AppImage`
- 应用图标（二分叉再汇聚设计）

```

- [ ] **Step 3: 更新 docs/RELEASE.md — 增加 Linux 发布 checklist**

在文件末尾追加：

```markdown
## Linux AppImage release checklist

Run commands from the repository root.

### 1. Start clean

```bash
git status --short --branch
```

Expected:

```text
## main
```

### 2. Run tests

```bash
python3 -m unittest discover -p "test*.py"
```

Expected: all tests pass.

### 3. Build the AppImage

```bash
./build_linux.sh
```

Expected output includes:

```text
构建成功！
输出: dist/VisualDuipai-x86_64.AppImage
```

### 4. Smoke-test the AppImage

```bash
test -f dist/VisualDuipai-x86_64.AppImage && echo "PASS: AppImage exists"
test -x dist/VisualDuipai-x86_64.AppImage && echo "PASS: AppImage executable"
```

Expected:

```text
PASS: AppImage exists
PASS: AppImage executable
```

### 5. Create the release asset

Rename the AppImage for release:

```bash
cp dist/VisualDuipai-x86_64.AppImage VisualDuipai-v0.2.0-linux-x86_64.AppImage
```

### 6. Create the GitHub Release

Create a GitHub Release with:

- Tag: `v0.2.0`
- Title: `VisualDuipai v0.2.0`
- Assets:
  - `VisualDuipai-v0.1.0-windows-x64.zip` (unchanged)
  - `VisualDuipai-v0.2.0-linux-x86_64.AppImage`
```

- [ ] **Step 4: 更新 packaging/README.md — 增加 Linux 打包说明**

在文件末尾追加：

```markdown
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
```

- [ ] **Step 5: 验证文档一致性**

```bash
# 确保所有文档引用的产物名称一致
grep -q "VisualDuipai-x86_64.AppImage" README.md && echo "PASS: README"
grep -q "Linux AppImage" CHANGELOG.md && echo "PASS: CHANGELOG"
grep -q "Smoke-test the AppImage" docs/RELEASE.md && echo "PASS: RELEASE"
grep -q "appimagetool" packaging/README.md && echo "PASS: packaging/README"
```

- [ ] **Step 6: 提交**

```bash
git add README.md CHANGELOG.md docs/RELEASE.md packaging/README.md
git commit -m "docs: add linux AppImage usage, release, and packaging instructions"
```
