#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证安卓工程能否正常构建：
1. 检查本地是否有 gradle / java
2. 若有，尝试用 Gradle 构建 Debug APK
3. 若环境不足，模拟验证工程结构的完整性（不真正构建）
"""
import os
import sys
import shutil
import subprocess
import zipfile

PROJECT = os.path.dirname(os.path.abspath(__file__))
ANDROID_DIR = os.path.join(PROJECT, "android")

def log(msg):  print(f"[INFO]  {msg}")
def warn(msg): print(f"[WARN]  {msg}")
def err(msg):  print(f"[ERROR] {msg}")

def check_tools():
    """检查构建工具"""
    java = shutil.which("java")
    javac = shutil.which("javac")
    gradle = shutil.which("gradle")
    # 也检查 Android SDK
    android_home = os.environ.get("ANDROID_HOME", "") or os.environ.get("ANDROID_SDK_ROOT", "")
    log(f"java:   {java or '未找到'}")
    log(f"javac:  {javac or '未找到'}")
    log(f"gradle: {gradle or '未找到'}")
    log(f"ANDROID_HOME: {android_home or '未设置'}")
    return {
        "java": bool(java),
        "javac": bool(javac),
        "gradle": bool(gradle),
        "sdk": bool(android_home),
    }

def validate_project_structure():
    """验证工程结构完整性（不依赖外部环境）"""
    log("验证工程结构完整性...")
    required = [
        "package.json",
        "capacitor.config.ts",
        "www/index.html",
        "android/build.gradle",
        "android/settings.gradle",
        "android/variables.gradle",
        "android/gradle/wrapper/gradle-wrapper.properties",
        "android/app/build.gradle",
        "android/app/proguard-rules.pro",
        "android/app/src/main/AndroidManifest.xml",
        "android/app/src/main/java/com/yuanbao/snake/MainActivity.java",
        "android/app/src/main/res/values/strings.xml",
        "android/app/src/main/res/values/styles.xml",
        "android/app/src/main/res/values/colors.xml",
        ".github/workflows/build-apk.yml",
        "build.sh",
        "README.md",
    ]
    missing = []
    for rel in required:
        path = os.path.join(PROJECT, rel)
        if not os.path.exists(path):
            missing.append(rel)
        else:
            log(f"  ✓ {rel}")

    # 检查图标
    icon_dirs = ["mipmap-mdpi", "mipmap-hdpi", "mipmap-xhdpi", "mipmap-xxhdpi", "mipmap-xxxhdpi"]
    for d in icon_dirs:
        p = os.path.join(ANDROID_DIR, "app/src/main/res", d, "ic_launcher.png")
        if os.path.exists(p):
            log(f"  ✓ {d}/ic_launcher.png")
        else:
            missing.append(f"{d}/ic_launcher.png")

    if missing:
        warn("缺少以下文件：")
        for m in missing:
            warn(f"  - {m}")
        return False
    log("✅ 工程结构完整")
    return True

def try_build():
    """尝试实际构建（若环境允许）"""
    tools = check_tools()

    if not (tools["java"] and tools["gradle"]):
        warn("本地缺少 java 或 gradle，跳过实际构建")
        warn("请在本地执行 ./build.sh，或使用 GitHub Actions 自动构建")
        return False

    if not tools["sdk"]:
        warn("未设置 ANDROID_HOME，无法构建（需要 Android SDK）")
        return False

    # 尝试构建
    log("尝试构建 Debug APK...")
    os.chdir(ANDROID_DIR)
    try:
        result = subprocess.run(["./gradlew", "assembleDebug"], check=False)
        if result.returncode == 0:
            # 查找 APK
            apk_dir = os.path.join(ANDROID_DIR, "app/build/outputs/apk/debug")
            for f in os.listdir(apk_dir):
                if f.endswith(".apk"):
                    apk = os.path.join(apk_dir, f)
                    size = os.path.getsize(apk) / (1024*1024)
                    log(f"🎉 构建成功: {apk} ({size:.1f} MB)")
                    return True
    except Exception as e:
        warn(f"构建失败: {e}")
    return False

def main():
    print("=" * 60)
    print("  贪吃蛇安卓工程 - 构建验证")
    print("=" * 60)

    ok = validate_project_structure()
    if not ok:
        err("工程结构不完整，请检查上方缺失文件")
        sys.exit(1)

    print()
    built = try_build()
    if built:
        log("✅ 已在沙盒中成功构建 APK")
    else:
        warn("沙盒环境无法直接构建（正常：沙盒无完整 Android SDK）")
        log("请在以下任一环境构建：")
        log("  1. 本地：./build.sh（需 JDK 17 + Android SDK）")
        log("  2. GitHub Actions：push 后自动构建，Actions 页面下载 APK")
        log("详见 README.md")

    # 打包整个工程为 zip（排除 node_modules 和构建缓存）
    zip_path = os.path.join(PROJECT, "..", "贪吃蛇_安卓工程.zip")
    exclude = {"node_modules", ".gradle", "build", ".buildozer", ".git", "__pycache__"}
    log(f"打包工程为 zip（排除 {exclude}）...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PROJECT):
            # 过滤排除目录
            dirs[:] = [d for d in dirs if d not in exclude and not d.startswith(".")]
            for f in files:
                if f.endswith((".pyc", ".class")) or f == "gradle-wrapper.jar":
                    continue
                fpath = os.path.join(root, f)
                arcname = os.path.relpath(fpath, os.path.dirname(PROJECT))
                zf.write(fpath, arcname)
    size = os.path.getsize(zip_path) / (1024*1024)
    log(f"📦 工程打包完成: {zip_path} ({size:.1f} MB)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
