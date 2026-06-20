@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo 汽水音乐：多线程剪贴板监听下载
echo ========================================
echo 复制汽水音乐分享链接后会自动加入下载队列。
echo 按 Ctrl+C 可停止监听。
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    py main.py --clipboard
) else (
    python main.py --clipboard
)

pause
