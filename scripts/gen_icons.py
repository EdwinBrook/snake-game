#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成安卓应用图标（mipmap 各分辨率）
用 🐍 贪吃蛇图案：深色圆角方块 + 绿色蛇身 + 红色食物

用法：python3 scripts/gen_icons.py
依赖：pip3 install Pillow
"""
import os

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("需要 Pillow：pip3 install Pillow")
    raise

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(PROJECT, "android", "app", "src", "main", "res")

# 普通启动图标分辨率
DENSITIES = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}

BG_COLOR = (30, 30, 46, 255)      # 深色背景 #1e1e2e
SNAKE_COLOR = (39, 174, 96, 255)  # 绿色蛇身
HEAD_COLOR = (241, 196, 15, 255)  # 黄色蛇头
FOOD_COLOR = (231, 76, 60, 255)   # 红色食物


def make_icon(size):
    """生成一个图标：圆角方块背景 + 贪吃蛇图案（4x4 网格蛇）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 圆角矩形背景
    draw.rounded_rectangle([0, 0, size, size], radius=size * 0.15, fill=BG_COLOR)

    # 蛇身格子（相对坐标 0~4，一条弯曲的蛇）
    snake_cells = [
        (0.5, 2.5), (1.5, 2.5), (2.5, 2.5), (2.5, 1.5), (3.0, 1.5)
    ]
    cell = size / 4.0
    m = cell * 0.08  # 格子内边距

    for i, (cx, cy) in enumerate(snake_cells):
        x = cx * cell
        y = cy * cell
        color = HEAD_COLOR if i == 0 else SNAKE_COLOR
        draw.rounded_rectangle(
            [x + m, y + m, x + cell - m, y + cell - m],
            radius=cell * 0.22,
            fill=color,
        )

    # 食物（红点）
    fx = 0.7 * cell
    fy = 0.7 * cell
    r = cell * 0.28
    draw.ellipse([fx - r, fy - r, fx + r, fy + r], fill=FOOD_COLOR)

    return img


def main():
    print("生成安卓应用图标...")
    for folder, size in DENSITIES.items():
        d = os.path.join(RES, folder)
        os.makedirs(d, exist_ok=True)
        img = make_icon(size)
        out = os.path.join(d, "ic_launcher.png")
        img.save(out)
        print(f"  ✓ {os.path.relpath(out, PROJECT)}  ({size}x{size})")

    # 自适应图标 foreground（内容居中在 66% 安全区）
    adaptive = {
        "drawable-mdpi": 108,
        "drawable-hdpi": 162,
        "drawable-xhdpi": 216,
        "drawable-xxhdpi": 324,
        "drawable-xxxhdpi": 432,
    }
    for folder, size in adaptive.items():
        d = os.path.join(RES, folder)
        os.makedirs(d, exist_ok=True)
        # foreground 只画内容（透明背景），背景色由 colors.xml 提供
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        safe = size * 0.66
        off = (size - safe) / 2
        cell = safe / 4.0
        m = cell * 0.08
        snake_cells = [(0.5,2.5),(1.5,2.5),(2.5,2.5),(2.5,1.5),(3.0,1.5)]
        for i, (cx, cy) in enumerate(snake_cells):
            x = off + cx * cell
            y = off + cy * cell
            color = HEAD_COLOR if i == 0 else SNAKE_COLOR
            draw.rounded_rectangle([x+m, y+m, x+cell-m, y+cell-m], radius=cell*0.22, fill=color)
        fx = off + 0.7 * cell
        fy = off + 0.7 * cell
        r = cell * 0.28
        draw.ellipse([fx-r, fy-r, fx+r, fy+r], fill=FOOD_COLOR)
        out = os.path.join(d, "ic_launcher_foreground.png")
        img.save(out)
        print(f"  ✓ {os.path.relpath(out, PROJECT)}  ({size}x{size})")

    # 自适应图标 XML（API 26+）
    bg_dir = os.path.join(RES, "mipmap-anydpi-v26")
    os.makedirs(bg_dir, exist_ok=True)
    with open(os.path.join(bg_dir, "ic_launcher.xml"), "w") as f:
        f.write('''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>
''')
    # 背景色
    values_dir = os.path.join(RES, "values")
    os.makedirs(values_dir, exist_ok=True)
    with open(os.path.join(values_dir, "colors.xml"), "w") as f:
        f.write('''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="ic_launcher_background">#1E1E2E</color>
</resources>
''')
    print(f"  ✓ {bg_dir}/ic_launcher.xml")
    print(f"  ✓ {values_dir}/colors.xml")
    print("\n🎉 图标生成完成！")


if __name__ == "__main__":
    main()
