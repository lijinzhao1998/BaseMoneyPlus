# -*- coding: utf-8 -*-
"""
基金管家配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 基金代码列表
FUND_CODES = [
    "017811",  # 基金代码
    "002963",
    "020640",
    "002112",
    "021095"
]

# 基金名称映射（可选，用于显示）
FUND_NAMES = {
    "017811": "东方人工智能主题混合C",
    "002963": "易方达黄金ETF联接C",
    "020640": "广发半导体",
    "002112": "德邦鑫星",
    "021095": "东方低碳经济"
}

# 基金当前持有市值（元）- 用于计算份额和收益
# 请根据您的实际持仓修改此处的金额
FUND_AMOUNTS = {
    "017811": 10000.0,   # 东方人工智能主题混合C - 请修改为您的持仓金额
    "002963": 10000.0,   # 易方达黄金ETF联接C - 请修改为您的持仓金额
    "020640": 10000.0,   # 广发半导体 - 请修改为您的持仓金额
    "002112": 10000.0,   # 德邦鑫星 - 请修改为您的持仓金额
    "021095": 10000.0    # 东方低碳经济 - 请修改为您的持仓金额
}

# 基金成本净值（买入时的净值，用于计算收益率）
# 请根据您的实际买入价格修改此处的成本净值
FUND_COST_BASIS = {
    "017811": 1.0,       # 请修改为您的买入净值
    "002963": 1.5,       # 请修改为您的买入净值
    "020640": 1.2,       # 请修改为您的买入净值
    "002112": 0.9,       # 请修改为您的买入净值
    "021095": 1.1        # 请修改为您的买入净值
}

# 每日任务执行时间
SCHEDULE_TIME = "21:40"  # 晚上9点40分发送日报

# 服务器酱配置（用于微信推送，需要注册 http://sc.ftqq.com/3.version）
SERVER_CHAN_KEY = os.getenv("SERVER_CHAN_KEY", "")

# 企业微信配置
WECHAT_WEBHOOK = os.getenv("WECHAT_WEBHOOK", "")

# 钉钉配置
DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK", "")

# 数据库配置（可选）
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "fund_manager"),
}

# 预测模型参数
PREDICTION_DAYS = 5  # 预测未来几天
LOOKBACK_DAYS = 30   # 使用过去多少天的数据

# 日志配置
LOG_FILE = "fund_manager.log"
LOG_LEVEL = "INFO"
