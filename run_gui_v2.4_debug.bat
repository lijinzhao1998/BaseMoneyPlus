@echo off
chcp 65001 >nul
echo ====================================
echo 基金管理系统 GUI v2.4 (调试版)
echo ====================================
echo.
echo 正在检查 Python 环境...
echo.

:: 检查 py 命令
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 找到 py 命令
    echo.
    echo 正在启动图形化界面...
    echo.
    py gui_manager_v2.4.py
    if %errorlevel% neq 0 (
        echo.
        echo ✗ 启动失败，显示详细错误信息：
        echo.
        py gui_manager_v2.4.py 2>&1
    )
    goto end
)

:: 检查 python 命令
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 找到 python 命令
    echo.
    echo 正在启动图形化界面...
    echo.
    python gui_manager_v2.4.py
    if %errorlevel% neq 0 (
        echo.
        echo ✗ 启动失败，显示详细错误信息：
        echo.
        python gui_manager_v2.4.py 2>&1
    )
    goto end
)

:: 都没找到
echo ✗ 未找到 Python
echo.
echo 请确保已安装 Python 3.7+ 并添加到系统路径
echo 下载地址：https://www.python.org/downloads/
echo.

:end
echo.
pause

