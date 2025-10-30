@echo off
chcp 65001 >nul
echo ========================================
echo 基金管家 - 华为云服务器部署
echo ========================================
echo.

set SERVER_IP=your_server_ip
set USERNAME=your_username
set PASSWORD=your_password
set REMOTE_PATH=/opt/fund_manager

echo 正在打包项目文件...
echo.

REM 创建临时打包目录
if exist deploy_temp rmdir /s /q deploy_temp
mkdir deploy_temp

REM 复制需要的文件
copy *.py deploy_temp\ >nul 2>&1
copy requirements.txt deploy_temp\ >nul 2>&1
copy README.md deploy_temp\ >nul 2>&1
copy 使用说明.md deploy_temp\ >nul 2>&1
copy DAEMON.md deploy_temp\ >nul 2>&1
copy holdings_config.json deploy_temp\ >nul 2>&1

echo ✓ 文件打包完成
echo.
echo ========================================
echo 部署步骤
echo ========================================
echo.
echo 方法1: 使用 WinSCP (推荐)
echo   1. 下载安装 WinSCP: https://winscp.net/eng/download.php
echo   2. 连接到 %SERVER_IP% (用户名: %USERNAME%, 密码: %PASSWORD%)
echo   3. 上传 deploy_temp 文件夹中的文件到服务器 %REMOTE_PATH%
echo.
echo 方法2: 使用命令行 SCP
echo   如果你已配置 SSH 密钥，可以运行:
echo   scp -r deploy_temp\* %USERNAME%@%SERVER_IP%:%REMOTE_PATH%/
echo.
echo 部署完成后，在服务器上执行:
echo.
echo   # 连接到服务器
echo   ssh %USERNAME%@%SERVER_IP%
echo.
echo   # 创建目录
echo   mkdir -p %REMOTE_PATH%
echo   cd %REMOTE_PATH%
echo.
echo   # 安装依赖
echo   pip3 install -r requirements.txt
echo.
echo   # 配置环境变量
echo   vi .env
echo   # 按 i 进入编辑模式，添加以下内容:
echo   # SERVER_CHAN_KEY=你的密钥
echo   # 按 ESC，输入 :wq 保存退出
echo.
echo   # 启动守护进程
echo   python3 daemon.py start
echo.
echo   # 查看状态
echo   python3 daemon.py status
echo.
echo ========================================
pause