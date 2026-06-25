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
check_cmd wget
ok "构建环境检查完毕"

# ── 步骤 2: 安装 Python 依赖 ────────────────────────────
step 2 "安装 Python 依赖..."
python3 -m pip install --break-system-packages -r "$REQUIREMENTS" pyinstaller 2>&1 | tail -3
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
