@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo 正在安装依赖，请不要关闭窗口
echo ========================================

where py >nul 2>nul
if %errorlevel%==0 (
    py -m ensurepip --upgrade
    py -m pip install --upgrade pip
    py -m pip install -r requirements.txt
    goto END
)

where python >nul 2>nul
if %errorlevel%==0 (
    python -m ensurepip --upgrade
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    goto END
)

echo.
echo 未检测到 Python。
echo 请先安装 Python，并勾选 Add python.exe to PATH。
echo.

:END
echo.
echo 依赖安装命令已执行完成。
pause
