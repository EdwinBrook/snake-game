# 🐍 贪吃蛇 - 安卓版

将贪吃蛇网页游戏打包成安卓 APK。基于 **Capacitor 5** + WebView，把现有 HTML/CSS/JS 游戏封装成原生安卓应用。

## 📁 工程结构

```
snake-android/
├── www/                    # 游戏网页（Capacitor 会打包进 APK）
│   └── index.html           # 游戏入口（已针对手机优化）
├── android/                 # 安卓原生工程（cap sync 生成/维护）
│   └── app/src/main/
│       ├── java/com/yuanbao/snake/MainActivity.java  # 自定义主界面
│       └── AndroidManifest.xml
├── .github/workflows/       # GitHub Actions 自动构建
│   └── build-apk.yml
├── capacitor.config.ts      # Capacitor 配置（包名/签名）
├── package.json
├── build.sh                 # 本地一键构建脚本
└── README.md
```

## 🚀 方式一：GitHub Actions（推荐，免配置环境）

无需本地安装 JDK/SDK，Push 代码后云端自动构建，下载 APK 即可。

1. 在 GitHub 上 **New repository** 创建新仓库（如 `snake-android`）
2. 把本目录所有文件 push 上去：
   ```bash
   cd snake-android
   git init
   git add .
   git commit -m "init"
   git remote add origin https://github.com/你的用户名/snake-android.git
   git push -u origin main
   ```
3. 进入仓库 → **Actions** 标签页 → 左侧选择 `Build Android APK` → **Run workflow**
4. 等待 10-30 分钟（首次需下载依赖）→ 构建完成后在 **Artifacts** 下载 `snake-game-apk`
5. 把下载的 `app-debug.apk` 传到手机安装即可

> 💡 Debug 版无需签名即可安装测试。发布到应用商店才需要 Release 签名（见下方）。

## 💻 方式二：本地构建（需要 JDK + Android SDK）

### 环境准备（一次性的）

**Windows / macOS / Linux：**

1. 安装 **Node.js 20+**：https://nodejs.org （LTS 版即可）
2. 安装 **JDK 17**：
   - Windows/macOS：https://adoptium.net 下载 Temurin 17
   - Ubuntu：`sudo apt install openjdk-17-jdk`
3. 安装 **Android Studio**：https://developer.android.com/studio
   - 打开后装 SDK（API 33）和 NDK（25.1.x）
   - 配置环境变量：
     ```bash
     # macOS/Linux 加到 ~/.zshrc 或 ~/.bashrc
     export JAVA_HOME="/path/to/jdk-17"
     export ANDROID_HOME="$HOME/Library/Android/sdk"   # macOS
     # export ANDROID_HOME="$HOME/Android/Sdk"         # Linux
     export PATH="$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools"
     ```
4. 验证：
   ```bash
   java -version     # 应显示 17.x
   adb version       # 应正常输出版本
   ```

### 开始构建

```bash
cd snake-android
chmod +x build.sh        # 首次给执行权限
./build.sh               # 构建 Debug 版
# 或
./build.sh release       # 构建 Release 版（需先配置签名）
```

成功后生成 `贪吃蛇_Snake_debug.apk`，脚本会打印完整路径。

### 安装到手机

```bash
# 用数据线连接手机（开启 USB 调试）
adb devices              # 确认设备已连接
adb install -r 贪吃蛇_Snake_debug.apk
```

或直接把 APK 传到手机，点击安装（若提示"未知来源"，去设置里允许）。

## 🔐 Release 签名（发布应用商店才需要）

Debug 版只能自己测试，上架应用商店需要签名：

1. 生成签名密钥：
   ```bash
   keytool -genkeypair -v \
     -keystore android/app/snake.keystore \
     -storepass 你的密码 -keypass 你的密码 \
     -alias snake -keyalg RSA -keysize 2048 -validity 10000
   ```
2. 在 `android/app/build.gradle` 的 `android.signingConfigs.release` 填入：
   ```groovy
   storeFile file("snake.keystore")
   storePassword "你的密码"
   keyAlias "snake"
   keyPassword "你的密码"
   ```
3. 构建 Release：`cd android && ./gradlew assembleRelease`
4. APK 位于 `android/app/build/outputs/apk/release/app-release.apk`

> ⚠️ 密钥文件 (`snake.keystore`) 和密码务必妥善保管，丢失后无法更新应用！

## ⚙️ 常用自定义

| 想改什么 | 改哪里 |
|---------|--------|
| 应用名称（桌面图标下的字） | `android/app/src/main/res/values/strings.xml` 的 `app_name` |
| 包名（必须唯一） | `capacitor.config.ts` 的 `appId` + `AndroidManifest.xml` 的 `package` |
| 图标 | `android/app/src/main/res/mipmap-*/ic_launcher*.png`（见下方生成） |
| 游戏内容/难度 | `www/index.html`（`speed`、颜色、计分规则等） |
| 启动页 | `android/app/src/main/res/drawable/launch_splash.xml` |

### 生成应用图标

用 `www/index.html` 里的 🐍 emoji 生成各分辨率图标：

```bash
cd snake-android
python3 scripts/generate_icons.py   # 生成到 android/app/src/main/res/mipmap-*/
```

## 📱 功能说明

- ✅ 方向键 / WASD 控制（电脑）
- ✅ 屏幕滑动控制（手机）
- ✅ 虚拟方向键（手机）
- ✅ 沉浸式全屏、适配刘海屏
- ✅ 最高分本地存储
- ✅ 返回键退出确认
- ✅ 支持 Android 5.0+（API 21+）

## ❓ 常见问题

**Q: Buildozer 和 Capacitor 选哪个？**
A: 本项目用 Capacitor。纯网页游戏用 Capacitor 更简单、构建快、包体小（约 5-10MB）。Buildozer 适合需要大量 Python 逻辑的场景，但构建慢、包体大（约 50MB+）。

**Q: 首次构建很慢？**
A: 是的，首次需下载 Gradle、Android SDK、依赖库（约 1-2GB），之后会缓存。

**Q: 提示 "SDK not found"？**
A: 确认 `ANDROID_HOME` 指向 SDK 目录，且已装 API 33 的 SDK Platform。

**Q: 游戏在 WebView 里卡顿？**
A: 已开启硬件加速。若仍卡，可降低 `speed`（在 `www/index.html` 的 `let speed = 150`）。

## 📄 许可

MIT License - 可自由修改分发
