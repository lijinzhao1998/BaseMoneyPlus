# -*- coding: utf-8 -*-
"""
基金管家主程序
"""
import schedule
import time
import logging
import os
import sys
import subprocess
import json
from datetime import datetime
from config import FUND_CODES, FUND_NAMES, SCHEDULE_TIME, FUND_AMOUNTS, FUND_COST_BASIS
from fund_analyzer import FundAnalyzer
from message_sender import MessageSender
from moving_average_analyzer import MovingAverageAnalyzer

# PID 文件路径
PID_FILE = "fund_manager.pid"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fund_manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def is_process_running(pid):
    """检查进程是否在运行"""
    if sys.platform == 'win32':
        try:
            # 使用 tasklist 命令检查进程
            result = subprocess.run(
                ['tasklist', '/FI', f'PID eq {pid}'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            return 'INFO:' not in result.stdout
        except Exception as e:
            logger.error(f"检查进程状态失败: {e}")
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

def get_pid_from_file():
    """从 PID 文件读取进程 ID"""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r', encoding='utf-8') as f:
                pid = int(f.read().strip())
            return pid
        except Exception as e:
            logger.error(f"读取 PID 文件失败: {e}")
            return None
    return None

def write_pid_file(pid):
    """写入 PID 文件"""
    try:
        with open(PID_FILE, 'w', encoding='utf-8') as f:
            f.write(str(pid))
    except Exception as e:
        logger.error(f"写入 PID 文件失败: {e}")

def remove_pid_file():
    """删除 PID 文件"""
    if os.path.exists(PID_FILE):
        try:
            os.remove(PID_FILE)
        except Exception as e:
            logger.error(f"删除 PID 文件失败: {e}")

def check_daemon_status():
    """检查守护进程状态"""
    pid = get_pid_from_file()
    if pid is None:
        return False, None
    is_running = is_process_running(pid)
    return is_running, pid

def stop_daemon():
    """停止守护进程"""
    is_running, pid = check_daemon_status()
    if not is_running:
        print("❌ 守护进程未运行")
        return False
    
    try:
        if sys.platform == 'win32':
            # Windows 使用 taskkill
            subprocess.run(
                ['taskkill', '/F', '/PID', str(pid)],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        else:
            os.kill(pid, 15)  # 发送 SIGTERM
        
        remove_pid_file()
        print(f"✅ 已停止守护进程 (PID: {pid})")
        return True
    except Exception as e:
        logger.error(f"停止守护进程失败: {e}")
        print(f"❌ 停止守护进程失败: {e}")
        return False

class FundManager:
    """基金管家主类"""
    
    def __init__(self):
        self.analyzer = FundAnalyzer()
        self.sender = MessageSender()
        self.ma_analyzer = MovingAverageAnalyzer()
        
        # 基金持仓信息（从配置文件读取）
        self.holdings = {}
        self.watchlist = {}
        
        # 尝试从 holdings_config.json 加载配置
        self.load_holdings_config()
        
        # 如果没有配置文件，使用默认配置
        if not self.holdings:
            for code in FUND_CODES:
                self.holdings[code] = {
                    "name": FUND_NAMES.get(code, f"基金{code}"),
                    "cost_basis": FUND_COST_BASIS.get(code, 1.0),
                    "amount": FUND_AMOUNTS.get(code, 10000),
                    "invested": True,
                    "investment_start_date": None
                }
    
    def load_holdings_config(self):
        """从 holdings_config.json 加载配置"""
        try:
            if os.path.exists('holdings_config.json'):
                with open('holdings_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.holdings = config.get('holdings', {})
                    self.watchlist = config.get('watchlist', {})
                    logger.info(f"加载配置成功：{len(self.holdings)} 只持仓基金，{len(self.watchlist)} 只观察基金")
        except Exception as e:
            logger.warning(f"加载 holdings_config.json 失败: {e}")
            self.holdings = {}
            self.watchlist = {}
    
    def generate_daily_report(self, include_ma_analysis=True):
        """生成并发送每日报告"""
        logger.info("开始生成每日基金报告...")
        
        analysis_results = []
        ma_reports = []
        
        # 分析持仓基金
        logger.info(f"分析 {len(self.holdings)} 只持仓基金...")
        for code, holding in self.holdings.items():
            logger.info(f"正在分析基金 {code}...")
            
            analysis = self.analyzer.get_fund_analysis(
                fund_code=code,
                fund_name=holding.get("name", f"基金{code}"),
                cost_basis=holding.get("cost_basis", 1.0),
                amount=holding.get("amount", 10000),
                lookback_days=30,
                investment_start_date=holding.get("investment_start_date"),
                include_ma_analysis=include_ma_analysis
            )
            
            if analysis:
                analysis_results.append(analysis)
                
                # 如果有均线分析，添加到报告中
                if include_ma_analysis and analysis.get("ma_analysis"):
                    ma_report = self.ma_analyzer.format_analysis_report(analysis["ma_analysis"])
                    ma_reports.append(ma_report)
                
                logger.info(f"基金 {code} 分析完成")
            else:
                logger.warning(f"基金 {code} 分析失败")
            
            # 避免请求过快
            time.sleep(2)
        
        # 分析观察基金
        if self.watchlist and include_ma_analysis:
            logger.info(f"\n分析 {len(self.watchlist)} 只观察基金...")
            for code, watch_info in self.watchlist.items():
                logger.info(f"正在分析观察基金 {code}...")
                
                ma_analysis = self.ma_analyzer.analyze_fund(
                    code,
                    watch_info.get("name", f"基金{code}"),
                    watch_info.get("watch_start_date")
                )
                
                if ma_analysis and 'error' not in ma_analysis:
                    ma_report = self.ma_analyzer.format_analysis_report(ma_analysis)
                    ma_reports.append(ma_report)
                    logger.info(f"观察基金 {code} 分析完成")
                else:
                    logger.warning(f"观察基金 {code} 分析失败")
                
                # 避免请求过快
                time.sleep(2)
        
        if analysis_results or ma_reports:
            # 生成基础报告
            report_parts = []
            
            if analysis_results:
                basic_report = self.sender.format_fund_report(analysis_results)
                report_parts.append(basic_report)
            
            # 添加均线分析报告
            if ma_reports:
                report_parts.append("\n" + "="*60)
                report_parts.append("\n📊 均线分析报告")
                report_parts.append("="*60 + "\n")
                report_parts.append("\n".join(ma_reports))
            
            report = "\n".join(report_parts)
            
            logger.info("报告生成完成")
            logger.info("\n" + report)
            
            # 发送报告
            title = f"基金管家日报 - {datetime.now().strftime('%Y-%m-%d')}"
            success = self.sender.send_all(title, report)
            
            if success:
                logger.info("报告发送成功")
            else:
                logger.warning("报告发送失败")
        else:
            logger.error("没有生成任何分析结果")
    
    def run_once(self):
        """立即运行一次报告生成"""
        logger.info("立即运行报告生成...")
        self.generate_daily_report()
    
    def run_scheduler(self):
        """运行定时任务"""
        # 写入当前进程的 PID
        write_pid_file(os.getpid())
        logger.info(f"守护进程启动 (PID: {os.getpid()})")
        
        logger.info(f"设置定时任务：每天 {SCHEDULE_TIME} 执行")
        schedule.every().day.at(SCHEDULE_TIME).do(self.generate_daily_report)
        
        logger.info("基金管家启动成功，等待定时任务...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭...")
        finally:
            remove_pid_file()
            logger.info("守护进程已关闭")

def main():
    """主函数"""
    fund_manager = FundManager()
    
    # 检查守护进程状态
    is_running, pid = check_daemon_status()
    
    print("=" * 60)
    print("基金管家系统")
    print("=" * 60)
    
    # 显示守护进程状态
    if is_running:
        print(f"\n🟢 守护进程运行中 (PID: {pid})")
    else:
        print("\n🔴 守护进程未运行")
    
    print("\n选择运行模式：")
    print("1. 立即运行一次（生成并发送报告）")
    print("2. 启动/重启定时任务（后台运行）")
    print("3. 停止守护进程")
    print("4. 退出")
    print("\n" + "=" * 60)
    
    choice = input("请输入选项 (1-4): ").strip()
    
    if choice == "1":
        fund_manager.run_once()
        print("\n执行完成！")
    elif choice == "2":
        # 如果已有守护进程在运行，先停止
        if is_running:
            print(f"\n⚠️  检测到守护进程正在运行 (PID: {pid})")
            print("正在停止旧进程...")
            stop_daemon()
            time.sleep(1)
        
        print("\n定时任务已启动，程序将后台运行...")
        print(f"每天 {SCHEDULE_TIME} 将自动发送报告")
        print("按 Ctrl+C 退出\n")
        try:
            fund_manager.run_scheduler()
        except KeyboardInterrupt:
            print("\n程序已停止")
    elif choice == "3":
        stop_daemon()
    elif choice == "4":
        print("退出程序")
    else:
        print("无效选项")

if __name__ == "__main__":
    main()
