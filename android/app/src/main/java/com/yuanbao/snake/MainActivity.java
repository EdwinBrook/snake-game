package com.yuanbao.snake;

import android.os.Bundle;
import android.view.Window;
import android.view.WindowManager;
import androidx.appcompat.app.AlertDialog;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // 沉浸式状态栏：让游戏铺满屏幕顶部
        Window window = getWindow();
        window.setFlags(
                WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN
        );
    }

    /**
     * 拦截返回键：双击返回退出，或弹出确认对话框
     */
    private long lastBackPressTime = 0;

    @Override
    public void onBackPressed() {
        long currentTime = System.currentTimeMillis();
        if (currentTime - lastBackPressTime < 2000) {
            // 2秒内再次按返回键，退出应用
            super.onBackPressed();
            finish();
        } else {
            lastBackPressTime = currentTime;
            new AlertDialog.Builder(this)
                    .setTitle("退出游戏")
                    .setMessage("确定要退出贪吃蛇吗？")
                    .setPositiveButton("退出", (dialog, which) -> finish())
                    .setNegativeButton("继续玩", null)
                    .show();
        }
    }
}
