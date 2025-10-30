@echo off
chcp 65001 >nul
echo ====================================
echo 基金管理系统 GUI v2.4
echo ====================================
echo.
echo 正在启动图形化界面...
echo.

:: 尝试 py 命令
py gui_manager_v2.4.py >nul 2>&1
if %errorlevel% equ 0 goto end

:: 尝试 python 命令
python gui_manager_v2.4.py >nul 2>&1
if %errorlevel% equ 0 goto end

:: 启动失败，显示错误信息
echo.
echo ✗ 启动失败
echo.
echo 可能的原因：
echo   1. Python 未安装或未添加到系统路径
echo   2. 缺少必需的依赖包
echo   3. 程序文件损坏
echo.
echo 解决方法：
echo   1. 运行 run_gui_v2.4_debug.bat 查看详细错误
echo   2. 确保已安装 Python 3.7+
echo   3. 运行 pip install -r requirements.txt 安装依赖
echo.
pause

:end

