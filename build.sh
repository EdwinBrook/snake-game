#!/bin/bash
# ============================================================
#  贪吃蛇安卓 APK 一键构建脚本
#  ----------------------------------------------------------
#  用法：
#    ./build.sh           # 构建 Debug 版（可直接安装测试）
#    ./build.sh release   # 构建 Release 版（需先配置签名）
#
#  首次运行会自动：
#    1. npm install 安装依赖
#    2. 准备 Gradle Wrapper（若本地有 gradle 则用它生成 wrapper；
#       否则尝试下载 Gradle 8.4）
# ============================================================
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

MODE="${1:-debug}"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# --- 0. 环境检查 ---
log "检查环境..."
command -v node >/dev/null 2>&1 || err "未安装 Node.js（需 >=16）。请先安装：https://nodejs.org"
command -v npm  >/dev/null 2>&1 || err "未安装 npm"
command -v java >/dev/null 2>&1 || warn "未检测到 java，Android 构建需要 JDK 17"

NODE_VER=$(node -v | cut -d. -f1 | tr -d 'v')
[ "$NODE_VER" -ge 16 ] || warn "Node.js 版本较低 ($(node -v))，建议 >=16"

# --- 1. 安装 npm 依赖 ---
if [ ! -d "node_modules" ]; then
    log "安装 npm 依赖（首次较慢）..."
    npm install || err "npm install 失败"
else
    log "node_modules 已存在，跳过安装"
fi

# --- 2. 同步 Capacitor 安卓工程（生成 capacitor 相关文件） ---
if [ -d "node_modules/@capacitor/cli" ]; then
    log "同步 Capacitor 安卓工程（cap sync android）..."
    npx cap sync android || warn "cap sync 失败（可忽略，若 android/ 已完整）"
fi

# --- 3. 准备 Gradle Wrapper ---
cd android

prepare_wrapper() {
    # 情况 A：已有 gradlew，直接用
    if [ -x "gradlew" ]; then
        log "使用已有 gradlew"
        return 0
    fi

    # 情况 B：系统装了 gradle，用它生成 wrapper
    if command -v gradle >/dev/null 2>&1; then
        log "检测到系统 gradle，生成 wrapper..."
        gradle wrapper --gradle-version 8.4 || return 1
        chmod +x gradlew
        return 0
    fi

    # 情况 C：下载 Gradle 8.4 到临时目录并生成 wrapper
    warn "未检测到 gradle，尝试下载 Gradle 8.4（约 130MB，仅首次）..."
    local tmp="$(mktemp -d)"
    local url="https://services.gradle.org/distributions/gradle-8.4-bin.zip"
    if command -v curl >/dev/null 2>&1; then
        curl -L -o "$tmp/gradle.zip" "$url" || return 1
    elif command -v wget >/dev/null 2>&1; then
        wget -O "$tmp/gradle.zip" "$url" || return 1
    else
        return 1
    fi
    unzip -q "$tmp/gradle.zip" -d "$tmp"
    local gradle_bin="$tmp/gradle-8.4/bin/gradle"
    "$gradle_bin" wrapper --gradle-version 8.4 || return 1
    chmod +x gradlew
    log "Gradle wrapper 生成完成"
    return 0
}

if ! prepare_wrapper; then
    warn "无法自动准备 Gradle wrapper。"
    echo "  请手动安装 Gradle >=8.0："
    echo "    macOS:  brew install gradle"
    echo "    Linux:  sudo apt install gradle"
    echo "    Windows: https://gradle.org/install/"
    echo "  安装后重新运行 ./build.sh"
    exit 1
fi

cd "$PROJECT_DIR"

# --- 4. 构建 APK ---
log "开始构建 ${MODE^^} APK（首次会下载依赖，可能耗时 10-30 分钟）..."

if [ "$MODE" = "release" ]; then
    ./android/gradlew -p android assembleRelease || err "Release 构建失败"
    APK_PATH="android/app/build/outputs/apk/release"
else
    ./android/gradlew -p android assembleDebug || err "Debug 构建失败"
    APK_PATH="android/app/build/outputs/apk/debug"
fi

# --- 5. 复制 APK 到工程根目录 ---
APK_FILE=$(find "$APK_PATH" -name "*.apk" 2>/dev/null | head -n 1)
if [ -z "$APK_FILE" ]; then
    err "未找到生成的 APK 文件，请检查上方日志"
fi

OUT_NAME="贪吃蛇_Snake_${MODE}.apk"
cp "$APK_FILE" "$OUT_NAME"
log "🎉 构建成功！APK 位置："
echo -e "   ${GREEN}${PROJECT_DIR}/${OUT_NAME}${NC}"
echo ""
log "安装到手机：adb install -r \"$OUT_NAME\""
echo ""
warn "Release 签名说明："
echo "  1. keytool -genkeypair -v -keystore android/app/snake.keystore \\"
echo "       -storepass 123456 -keypass 123456 -alias snake \\"
echo "       -keyalg RSA -keysize 2048 -validity 10000"
echo "  2. ./build.sh release"

exit 0
