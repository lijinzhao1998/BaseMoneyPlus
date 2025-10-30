# -*- coding: utf-8 -*-
"""
自动部署到华为云服务器
使用 paramiko 库进行SSH和SFTP连接
"""

import os
import sys
import paramiko
from pathlib import Path

# 服务器配置
SERVER_CONFIG = {
    'hostname': '121.36.30.215',
    'username': 'root',
    'password': 'Ljz751227',
    'port': 22,
}

REMOTE_PATH = '/opt/fund_manager'

# 需要上传的文件列表
FILES_TO_UPLOAD = [
    '*.py',
    'requirements.txt',
    'README.md',
    '使用说明.md',
    'DAEMON.md',
    'holdings_config.json',
]


def print_colored(text, color='white'):
    """彩色输出"""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'cyan': '\033[96m',
        'white': '\033[0m',
    }
    print(f"{colors.get(color, colors['white'])}{text}\033[0m")


def connect_ssh():
    """连接SSH服务器"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print_colored(f"正在连接到服务器 {SERVER_CONFIG['hostname']}...", 'cyan')
        ssh.connect(
            hostname=SERVER_CONFIG['hostname'],
            username=SERVER_CONFIG['username'],
            password=SERVER_CONFIG['password'],
            port=SERVER_CONFIG['port'],
            timeout=10
        )
        print_colored("✓ SSH连接成功", 'green')
        return ssh
    except Exception as e:
        print_colored(f"❌ SSH连接失败: {e}", 'red')
        return None


def upload_files(sftp, local_dir='.'):
    """上传文件到服务器"""
    local_path = Path(local_dir)
    
    # 收集需要上传的文件
    files_to_upload = []
    for pattern in FILES_TO_UPLOAD:
        files = list(local_path.glob(pattern))
        files_to_upload.extend(files)
    
    # 去重
    files_to_upload = list(set(files_to_upload))
    
    print_colored(f"\n准备上传 {len(files_to_upload)} 个文件...", 'yellow')
    
    uploaded_count = 0
    for file_path in files_to_upload:
        if file_path.is_file():
            remote_file = f"{REMOTE_PATH}/{file_path.name}"
            try:
                print_colored(f"  上传: {file_path.name}", 'white')
                sftp.put(str(file_path), remote_file)
                uploaded_count += 1
            except Exception as e:
                print_colored(f"    ❌ 上传失败: {e}", 'red')
    
    print_colored(f"\n✓ 成功上传 {uploaded_count}/{len(files_to_upload)} 个文件", 'green')


def execute_command(ssh, command, show_output=True):
    """执行远程命令"""
    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        if show_output and output:
            print(output, end='')
        if show_output and error:
            print(error, end='', file=sys.stderr)
        
        return stdout.channel.recv_exit_status() == 0
    except Exception as e:
        print_colored(f"执行命令失败: {e}", 'red')
        return False


def main():
    """主函数"""
    print_colored("=" * 60, 'cyan')
    print_colored("基金管家 - 自动部署到华为云服务器", 'cyan')
    print_colored("=" * 60, 'cyan')
    print()
    
    # 检查paramiko是否安装
    try:
        import paramiko
    except ImportError:
        print_colored("❌ 未安装 paramiko 库", 'red')
        print_colored("请运行: pip install paramiko", 'yellow')
        return
    
    # 连接SSH
    ssh = connect_ssh()
    if not ssh:
        print_colored("\n建议使用WinSCP手动上传文件", 'yellow')
        print_colored("部署指南请查看: 部署指南.md", 'yellow')
        return
    
    try:
        # 创建远程目录
        print_colored("\n创建远程目录...", 'cyan')
        execute_command(ssh, f"mkdir -p {REMOTE_PATH}")
        execute_command(ssh, f"chmod 755 {REMOTE_PATH}")
        
        # 上传文件
        sftp = ssh.open_sftp()
        print_colored("\n上传文件...", 'cyan')
        upload_files(sftp)
        sftp.close()
        
        # 安装依赖
        print_colored("\n检查Python和依赖...", 'cyan')
        execute_command(ssh, "which python3", show_output=False)
        execute_command(ssh, f"cd {REMOTE_PATH} && pip3 install -r requirements.txt -q")
        
        # 设置执行权限
        print_colored("\n设置文件权限...", 'cyan')
        execute_command(ssh, f"cd {REMOTE_PATH} && chmod +x *.py")
        
        print_colored("\n" + "=" * 60, 'green')
        print_colored("部署完成！", 'green')
        print_colored("=" * 60, 'green')
        print()
        print_colored("下一步操作：", 'yellow')
        print()
        print(f"1. 连接到服务器: ssh {SERVER_CONFIG['username']}@{SERVER_CONFIG['hostname']}")
        print(f"2. 进入项目目录: cd {REMOTE_PATH}")
        print("3. 配置环境变量:")
        print("   vi .env")
        print("   添加: SERVER_CHAN_KEY=SCT300665TP5m4iVzbn4fnmYQCT2okZvg3")
        print("4. 启动守护进程: python3 daemon.py start")
        print("5. 查看状态: python3 daemon.py status")
        print()
        
    except Exception as e:
        print_colored(f"\n❌ 部署过程出错: {e}", 'red')
    finally:
        ssh.close()


if __name__ == '__main__':
    main()