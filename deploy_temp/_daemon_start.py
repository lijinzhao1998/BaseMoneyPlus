
import sys
import time
import schedule
from main import FundManager

# 创建基金管理器
fund_manager = FundManager()

# 启动定时任务
fund_manager.run_scheduler()
