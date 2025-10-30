# -*- coding: utf-8 -*-
"""
快速启动脚本 - 立即运行一次报告
"""
from main import FundManager
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("=" * 60)
    print("基金管家系统 - 快速启动")
    print("=" * 60)
    print("\n正在生成基金报告...\n")
    
    fund_manager = FundManager()
    fund_manager.run_once()
    
    print("\n完成！")

if __name__ == "__main__":
    main()
