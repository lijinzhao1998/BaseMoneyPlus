@echo off
chcp 65001 >nul
echo ====================================
echo 环境检查工具
echo ====================================
echo.

py check_environment.py

if %errorlevel% neq 0 (
    python check_environment.py 2>nul
)

echo.
pause

