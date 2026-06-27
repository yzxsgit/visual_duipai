#!/bin/bash
# =============================================================================
# build_macos.sh — VisualDuipai macOS .app Bundle 本地构建脚本
# =============================================================================
# 用法:
#   ./build_macos.sh              # 完整构建
#   ./build_macos.sh --debug      # 构建后从终端运行以便查看崩溃日志
#   ./build_macos.sh --no-sign    # 跳过 ad-hoc 签名
#
# 依赖:
#   - macOS 11+ (Apple Silicon 或 Intel)
#   - Python 3.10+
#   - Xcode Command Line Tools (xcode-select --install)
# =============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ── 颜色 ──────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }
step()  { echo; echo -e "${GREEN}==>${NC} $*"; }

# ── 解析参数 ──────────────────────────────────────────────────────────────────
DO_DEBUG=false
DO_SIGN=true
for arg in "$@"; do
    case "$arg" in
        --debug)    DO_DEBUG=true ;;
        --no-sign)  DO_SIGN=false ;;
        --help|-h)
            echo "用法: $0 [--debug] [--no-sign]"
            echo "  --debug     构建后在终端运行（可看到崩溃日志）"
            echo "  --no-sign   跳过 ad-hoc 签名"
            exit 0
            ;;
    esac
done

# ── 检查依赖 ──────────────────────────────────────────────────────────────────
step "检查依赖"

if ! command -v python3 &>/dev/null; then
    error "python3 未找到。请安装 Python 3.10+：https://www.python.org/downloads/"
    exit 1
fi
info "python3: $(python3 --version)"

if ! command -v g++ &>/dev/null && ! command -v clang++ &>/dev/null; then
    warn "g++/clang++ 未找到。对拍需要 C++ 编译器。"
    warn "请运行: xcode-select --install"
fi

if ! command -v sips &>/dev/null; then
    error "sips 未找到（这是 macOS 自带工具，不应缺失）"
    exit 1
fi

if ! command -v iconutil &>/dev/null; then
    error "iconutil 未找到（这是 macOS 自带工具，不应缺失）"
    exit 1
fi

info "所有依赖满足"

# ── 安装 Python 依赖 ─────────────────────────────────────────────────────────
step "安装 Python 依赖"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt pyinstaller
info "依赖安装完成"

# ── 运行测试 ──────────────────────────────────────────────────────────────────
step "运行测试"
python3 -m unittest discover -p "test*.py"
info "测试通过"

# ── PyInstaller 打包 ──────────────────────────────────────────────────────────
step "PyInstaller 打包（--onefile）"
rm -rf build dist
python3 -m PyInstaller \
    --onefile \
    --noconsole \
    --name VisualDuipai \
    --collect-all customtkinter \
    --collect-all tkinterdnd2 \
    duipai_gui.py

if [[ ! -f dist/VisualDuipai ]]; then
    error "PyInstaller 打包失败：dist/VisualDuipai 未生成"
    exit 1
fi
info "PyInstaller 输出: $(ls -lh dist/VisualDuipai | awk '{print $5}')"

# ── 构建 .app Bundle ──────────────────────────────────────────────────────────
step "构建 .app Bundle 结构"
APP_BUNDLE="VisualDuipai.app"
rm -rf "$APP_BUNDLE"
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"
cp dist/VisualDuipai "$APP_BUNDLE/Contents/MacOS/VisualDuipai"

# ── 转换图标 ──────────────────────────────────────────────────────────────────
step "转换图标（PNG → ICNS）"
ICONSET="VisualDuipai.iconset"
mkdir -p "$ICONSET"
sips -z 16 16 assets/VisualDuipai.png --out "$ICONSET/icon_16x16.png" >/dev/null
sips -z 32 32 assets/VisualDuipai.png --out "$ICONSET/icon_16x16@2x.png" >/dev/null
sips -z 32 32 assets/VisualDuipai.png --out "$ICONSET/icon_32x32.png" >/dev/null
sips -z 64 64 assets/VisualDuipai.png --out "$ICONSET/icon_32x32@2x.png" >/dev/null
sips -z 128 128 assets/VisualDuipai.png --out "$ICONSET/icon_128x128.png" >/dev/null
sips -z 256 256 assets/VisualDuipai.png --out "$ICONSET/icon_128x128@2x.png" >/dev/null
sips -z 256 256 assets/VisualDuipai.png --out "$ICONSET/icon_256x256.png" >/dev/null
sips -z 512 512 assets/VisualDuipai.png --out "$ICONSET/icon_256x256@2x.png" >/dev/null
iconutil -c icns "$ICONSET" -o VisualDuipai.icns
cp VisualDuipai.icns "$APP_BUNDLE/Contents/Resources/VisualDuipai.icns"
rm -rf "$ICONSET" VisualDuipai.icns
info "图标转换完成"

# ── 创建 Info.plist ──────────────────────────────────────────────────────────
step "创建 Info.plist"
cat > "$APP_BUNDLE/Contents/Info.plist" << 'EOF'
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
plutil -lint "$APP_BUNDLE/Contents/Info.plist" >/dev/null
info "Info.plist 有效"

# ── Ad-hoc 签名 ───────────────────────────────────────────────────────────────
if "$DO_SIGN"; then
    step "Ad-hoc 签名 .app Bundle"
    codesign --force --deep --sign - "$APP_BUNDLE"
    info "签名完成"
else
    warn "跳过 ad-hoc 签名"
fi

# ── 验证 ──────────────────────────────────────────────────────────────────────
step "验证 .app Bundle"
echo "  Bundle 路径: $PWD/$APP_BUNDLE"
echo "  大小: $(du -sh "$APP_BUNDLE" | awk '{print $1}')"
test -f "$APP_BUNDLE/Contents/MacOS/VisualDuipai" && info "  ✓ 二进制文件存在"
test -f "$APP_BUNDLE/Contents/Resources/VisualDuipai.icns" && info "  ✓ ICNS 图标存在"
test -f "$APP_BUNDLE/Contents/Info.plist" && info "  ✓ Info.plist 存在"

# ── 打包 ──────────────────────────────────────────────────────────────────────
step "打包为 .zip"
ZIP_NAME="VisualDuipai.app.zip"
rm -f "$ZIP_NAME"
zip -r "$ZIP_NAME" "$APP_BUNDLE" >/dev/null
echo "  产物: $PWD/$ZIP_NAME ($(ls -lh "$ZIP_NAME" | awk '{print $5}'))"

echo
info "构建完成!"

if "$DO_DEBUG"; then
    step "调试模式：从终端启动 .app（以便查看崩溃日志）"
    echo "  $APP_BUNDLE/Contents/MacOS/VisualDuipai"
    echo "  如果闪退，崩溃日志位于: ~/Library/Logs/VisualDuipai/crash.log"
    echo
    "$APP_BUNDLE/Contents/MacOS/VisualDuipai" 2>&1 || true
else
    echo
    echo "  启动方式: open $APP_BUNDLE"
    echo "  调试模式: $0 --debug"
    echo "  崩溃日志: ~/Library/Logs/VisualDuipai/crash.log"
fi
