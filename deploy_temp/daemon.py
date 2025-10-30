# -*- coding: utf-8 -*-
"""
基金管家守护进程管理脚本
用于启动、停止、查看守护进程状态
"""
import os
import sys
import subprocess
import time

# PID 文件路径
PID_FILE = "fund_manager.pid"

def get_pid_from_file():
    """从 PID 文件读取进程 ID"""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r', encoding='utf-8') as f:
                pid = int(f.read().strip())
            return pid
        except Exception:
            return None
    return None

def is_process_running(pid):
    """检查进程是否在运行"""
    if sys.platform == 'win32':
        try:
            result = subprocess.run(
                ['tasklist', '/FI', f'PID eq {pid}'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            return 'INFO:' not in result.stdout
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

def check_status():
    """查看守护进程状态"""
    pid = get_pid_from_file()
    if pid is None:
        print("🔴 守护进程未运行")
        return False
    
    is_running = is_process_running(pid)
    if is_running:
        print(f"🟢 守护进程运行中 (PID: {pid})")
        return True
    else:
        print(f"🔴 守护进程已停止 (PID: {pid}, PID 文件残留)")
        # 清理残留的 PID 文件
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return False

def start_daemon():
    """启动守护进程"""
    # 先检查是否已有进程运行
    pid = get_pid_from_file()
    if pid and is_process_running(pid):
        print(f"❌ 守护进程已在运行 (PID: {pid})")
        print("💡 如需重启，请先使用 'py daemon.py stop' 停止")
        return False
    
    print("正在启动守护进程...")
    
    # 清理可能存在的旧 PID 文件
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
    
    # 启动守护进程，自动选择选项 2（启动定时任务）
    if sys.platform == 'win32':
        # Windows: 创建新进程，输入 "2" 启动定时任务模式
        # 使用 START /B 后台运行，并将输入重定向到进程
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        # 创建一个临时脚本文件来启动守护进程
        script_content = '''
import sys
import time
import schedule
from main import FundManager

# 创建基金管理器
fund_manager = FundManager()

# 启动定时任务
fund_manager.run_scheduler()
'''
        with open('_daemon_start.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 在新进程中启动
        process = subprocess.Popen(
            [sys.executable, '_daemon_start.py'],
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 保存 PID
        with open(PID_FILE, 'w', encoding='utf-8') as f:
            f.write(str(process.pid))
            
    else:
        # Linux/Mac: 使用 nohup 启动
        # 同样创建临时脚本
        script_content = '''
import sys
import time
import schedule
from main import FundManager

# 创建基金管理器
fund_manager = FundManager()

# 启动定时任务
fund_manager.run_scheduler()
'''
        with open('_daemon_start.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        process = subprocess.Popen(
            ['nohup', sys.executable, '_daemon_start.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 保存 PID
        with open(PID_FILE, 'w', encoding='utf-8') as f:
            f.write(str(process.pid))
    
    print("✅ 守护进程已启动")
    time.sleep(2)  # 等待进程启动
    
    # 再次检查状态
    check_status()
    return True

def stop_daemon():
    """停止守护进程"""
    pid = get_pid_from_file()
    if pid is None:
        print("❌ 未找到 PID 文件，守护进程可能未运行")
        return False
    
    is_running = is_process_running(pid)
    if not is_running:
        print("❌ 守护进程未运行")
        # 清理 PID 文件
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return False
    
    try:
        if sys.platform == 'win32':
            subprocess.run(
                ['taskkill', '/F', '/PID', str(pid)],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        else:
            os.kill(pid, 15)
        
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        
        print(f"✅ 已停止守护进程 (PID: {pid})")
        return True
    except Exception as e:
        print(f"❌ 停止守护进程失败: {e}")
        return False

def restart_daemon():
    """重启守护进程"""
    print("正在重启守护进程...")
    if check_status():
        stop_daemon()
        time.sleep(1)
    start_daemon()

def show_menu():
    """显示帮助菜单"""
    print("=" * 60)
    print("基金管家守护进程管理")
    print("=" * 60)
    print()
    print("使用方法:")
    print("  py daemon.py start    - 启动守护进程")
    print("  py daemon.py stop     - 停止守护进程")
    print("  py daemon.py restart  - 重启守护进程")
    print("  py daemon.py status   - 查看守护进程状态")
    print("  py daemon.py help     - 显示此帮助")
    print()

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_menu()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        start_daemon()
    elif command == 'stop':
        stop_daemon()
    elif command == 'restart':
        restart_daemon()
    elif command == 'status':
        check_status()
    elif command in ['help', '-h', '--help']:
        show_menu()
    else:
        print(f"❌ 未知命令: {command}")
        show_menu()

if __name__ == "__main__":
    main()
