#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
环境检查脚本 - 检查是否满足 GUI v2.4 运行要求
"""

import sys
import os
import io

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("✗ Python 版本过低，需要 3.7+")
        return False
    else:
        print("✓ Python 版本满足要求")
        return True

def check_module(module_name):
    """检查模块是否可以导入"""
    try:
        __import__(module_name)
        print(f"✓ {module_name}")
        return True
    except ImportError as e:
        print(f"✗ {module_name} - {str(e)}")
        return False

def check_required_modules():
    """检查必需的模块"""
    print("\n检查必需的 Python 模块:")
    
    modules = [
        'tkinter',
        'json',
        'threading',
        'datetime',
        'subprocess',
    ]
    
    all_ok = True
    for module in modules:
        if not check_module(module):
            all_ok = False
    
    return all_ok

def check_project_files():
    """检查项目文件"""
    print("\n检查项目文件:")
    
    files = [
        'gui_manager_v2.4.py',
        'config_manager.py',
        'report_generator.py',
        'fund_analyzer.py',
        'message_sender.py',
        'moving_average_analyzer.py',
    ]
    
    all_ok = True
    for file in files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - 文件不存在")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 50)
    print("基金管理系统 v2.4 环境检查")
    print("=" * 50)
    print()
    
    # 检查 Python 版本
    python_ok = check_python_version()
    
    # 检查必需模块
    modules_ok = check_required_modules()
    
    # 检查项目文件
    files_ok = check_project_files()
    
    # 总结
    print("\n" + "=" * 50)
    print("检查结果:")
    print("=" * 50)
    
    if python_ok and modules_ok and files_ok:
        print("✓ 所有检查通过！")
        print("\n可以运行以下命令启动程序：")
        print("  py gui_manager_v2.4.py")
        print("或双击：")
        print("  run_gui_v2.4.bat")
        return 0
    else:
        print("✗ 检查未通过，请解决上述问题")
        print("\n建议：")
        if not python_ok:
            print("  1. 升级到 Python 3.7 或更高版本")
        if not modules_ok:
            print("  2. 安装缺失的模块：pip install -r requirements.txt")
        if not files_ok:
            print("  3. 确保所有项目文件完整")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

