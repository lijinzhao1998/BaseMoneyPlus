# -*- coding: utf-8 -*-
# 部署脚本 - 华为云服务器部署

param(
    [string]$ServerIP = "your_server_ip",
    [string]$Username = "root",
    [string]$Password = "your_password",
    [string]$RemotePath = "/opt/fund_manager",
    [string]$LocalPath = "."
)

# 颜色输出函数
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput "基金管家 - 华为云服务器部署" "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput ""

# 检查SSH和SCP是否可用
$sshAvailable = Get-Command ssh -ErrorAction SilentlyContinue
$scpAvailable = Get-Command scp -ErrorAction SilentlyContinue

if (-not $sshAvailable -or -not $scpAvailable) {
    Write-ColorOutput "❌ 未检测到SSH/SCP工具" "Red"
    Write-ColorOutput "请安装OpenSSH客户端或使用WinSCP等工具手动部署" "Yellow"
    exit 1
}

Write-ColorOutput "✓ SSH/SCP工具已就绪" "Green"
Write-ColorOutput ""

# 需要上传的文件列表（排除不必要的文件）
$filesToUpload = @(
    "*.py",
    "requirements.txt",
    "README.md",
    "使用说明.md",
    "DAEMON.md",
    "holdings_config.json"
)

# 在服务器上执行的命令
$remoteCommands = @"
# 创建项目目录
mkdir -p $RemotePath

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "安装Python3..."
    # 根据系统选择安装命令
    if [ -f /etc/redhat-release ]; then
        yum install -y python3 python3-pip
    elif [ -f /etc/debian_version ]; then
        apt-get update
        apt-get install -y python3 python3-pip
    fi
fi

# 安装依赖
cd $RemotePath
if [ -f requirements.txt ]; then
    pip3 install -r requirements.txt
fi

# 设置权限
chmod +x *.py

echo "✓ 部署完成！"
"@

# 上传文件
Write-ColorOutput "正在上传文件到服务器..." "Yellow"
$uploadFailed = $false

foreach ($pattern in $filesToUpload) {
    $files = Get-ChildItem -Path $LocalPath -Filter $pattern -File
    
    foreach ($file in $files) {
        $fileName = $file.Name
        Write-ColorOutput "  上传: $fileName" "Gray"
        
        try {
            # 使用expect或expect-like工具处理密码输入（需要安装额外工具）
            # 这里使用sshpass（需要Linux/Mac）或WinSCP的批处理
            Write-ColorOutput "    请手动使用SCP或SFTP工具上传文件" "Yellow"
            Write-ColorOutput "    目标路径: root@${ServerIP}:${RemotePath}/" "Gray"
            $uploadFailed = $true
        } catch {
            Write-ColorOutput "    上传失败: $_" "Red"
            $uploadFailed = $true
        }
    }
}

if ($uploadFailed) {
    Write-ColorOutput ""
    Write-ColorOutput "由于安全原因，请手动上传文件" "Yellow"
    Write-ColorOutput ""
    Write-ColorOutput "方法1: 使用WinSCP" "Cyan"
    Write-ColorOutput "  1. 下载安装WinSCP" "White"
    Write-ColorOutput "  2. 连接到 $ServerIP (用户名: $Username, 密码: $Password)" "White"
    Write-ColorOutput "  3. 上传项目文件到 $RemotePath" "White"
    Write-ColorOutput ""
    Write-ColorOutput "方法2: 使用命令行SCP（需要SSH密钥配置）" "Cyan"
    Write-ColorOutput "  scp -r * root@${ServerIP}:${RemotePath}/" "White"
    Write-ColorOutput ""
}

Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput "部署说明" "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput ""
Write-ColorOutput "在服务器上执行以下命令来完成部署:" "Yellow"
Write-ColorOutput ""
Write-ColorOutput "1. 连接到服务器:" "Green"
Write-ColorOutput "   ssh $Username@$ServerIP" "White"
Write-ColorOutput ""
Write-ColorOutput "2. 创建项目目录:" "Green"
Write-ColorOutput "   mkdir -p $RemotePath" "White"
Write-ColorOutput "   cd $RemotePath" "White"
Write-ColorOutput ""
Write-ColorOutput "3. 上传项目文件（使用上述方法）" "Green"
Write-ColorOutput ""
Write-ColorOutput "4. 安装依赖:" "Green"
Write-ColorOutput "   pip3 install -r requirements.txt" "White"
Write-ColorOutput ""
Write-ColorOutput "5. 配置环境变量:" "Green"
Write-ColorOutput "   cp .env.example .env  # 如果存在" "White"
Write-ColorOutput "   vi .env  # 编辑配置" "White"
Write-ColorOutput ""
Write-ColorOutput "6. 启动守护进程:" "Green"
Write-ColorOutput "   python3 daemon.py start" "White"
Write-ColorOutput ""
Write-ColorOutput "7. 查看状态:" "Green"
Write-ColorOutput "   python3 daemon.py status" "White"
Write-ColorOutput ""