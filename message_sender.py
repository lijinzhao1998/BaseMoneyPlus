# -*- coding: utf-8 -*-
"""
消息推送模块
支持微信、企业微信、钉钉等
"""
import requests
import json
from datetime import datetime
from config import SERVER_CHAN_KEY, WECHAT_WEBHOOK, DINGTALK_WEBHOOK

class MessageSender:
    """消息发送器"""
    
    @staticmethod
    def format_fund_report(analysis_results):
        """
        格式化基金报告
        
        Args:
            analysis_results: 分析结果列表
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"📊 基金管家日报 - {current_time}\n"
        report += "=" * 50 + "\n\n"
        
        total_profit = 0
        total_today_profit = 0
        
        for result in analysis_results:
            if not result or not result.get("returns"):
                continue
            
            returns = result["returns"]
            trend = result.get("trend", {})
            prediction = result.get("prediction", [])
            
            code = result["code"]
            fund_name = result.get("name", "未知基金")
            
            # 累计收益
            total_profit += returns.get("total_profit", 0)
            total_today_profit += returns.get("today_profit", 0)
            
            # 涨跌符号
            change_symbol = "📈" if returns["today_change"] > 0 else "📉" if returns["today_change"] < 0 else "➡️"
            
            # 判断是否是今天的数据
            is_today = result.get("is_today", False)
            data_date = result.get("data_date", "")
            
            # 如果数据不是今天的，显示提示
            if is_today:
                date_label = "今日涨跌"
                profit_label = "今日收益"
            else:
                date_label = f"{data_date}涨跌" if data_date else "最新涨跌"
                profit_label = f"{data_date}收益" if data_date else "最新收益"
            
            report += f"【{fund_name} {code}】{change_symbol}\n"
            report += f"  {date_label}: {returns['today_change']:+.2f}%\n"
            report += f"  {profit_label}: {returns['today_profit']:+.2f}元\n"
            report += f"  累计收益: {returns['total_profit']:+.2f}元 ({returns['return_rate']:+.2f}%)\n"
            report += f"  当前净值: {returns['current_nav']}\n"
            report += f"  趋势: {trend.get('trend', '未知')}\n"
            
            # 预测信息
            if prediction and len(prediction) > 0:
                avg_prediction = sum([p['predicted_change'] for p in prediction]) / len(prediction)
                report += f"  预测趋势: {avg_prediction:+.2f}% (未来{len(prediction)}天平均)\n"
            
            report += "\n"
        
        # 总结
        report += "=" * 50 + "\n"
        report += f"📊 总资产收益: {total_profit:+.2f}元\n"
        
        # 判断是否所有数据都是今天的
        all_today = all(result.get("is_today", False) for result in analysis_results if result)
        if all_today:
            report += f"📈 今日总收益: {total_today_profit:+.2f}元\n"
        else:
            report += f"📈 最新总收益: {total_today_profit:+.2f}元（注：部分基金净值未更新）\n"
        
        report += "=" * 50 + "\n"
        report += "\n⚠️ 风险提示：投资有风险，入市需谨慎\n"
        
        return report
    
    @staticmethod
    def send_serverchan(title, content):
        """
        发送到Server酱（微信推送）
        注册地址: http://sc.ftqq.com/3.version
        """
        if not SERVER_CHAN_KEY:
            print("未配置Server酱KEY")
            return False
        
        url = f"https://sctapi.ftqq.com/{SERVER_CHAN_KEY}.send"
        
        data = {
            "title": title,
            "desp": content
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                print("Server酱推送成功")
                return True
            else:
                print(f"Server酱推送失败: {response.text}")
                return False
        except Exception as e:
            print(f"Server酱推送异常: {e}")
            return False
    
    @staticmethod
    def send_wechat_work(title, content):
        """
        发送到企业微信
        """
        if not WECHAT_WEBHOOK:
            print("未配置企业微信webhook")
            return False
        
        # 转换为markdown格式
        markdown_content = f"## {title}\n\n{content}"
        
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": markdown_content
            }
        }
        
        try:
            response = requests.post(
                WECHAT_WEBHOOK, 
                json=data, 
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                print("企业微信推送成功")
                return True
            else:
                print(f"企业微信推送失败: {response.text}")
                return False
        except Exception as e:
            print(f"企业微信推送异常: {e}")
            return False
    
    @staticmethod
    def send_dingtalk(title, content):
        """
        发送到钉钉
        """
        if not DINGTALK_WEBHOOK:
            print("未配置钉钉webhook")
            return False
        
        # 转换为markdown格式
        markdown_content = f"### {title}\n\n{content}"
        
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": markdown_content
            }
        }
        
        try:
            response = requests.post(
                DINGTALK_WEBHOOK,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                print("钉钉推送成功")
                return True
            else:
                print(f"钉钉推送失败: {response.text}")
                return False
        except Exception as e:
            print(f"钉钉推送异常: {e}")
            return False
    
    @staticmethod
    def send_all(title, content):
        """尝试所有推送方式"""
        results = []
        results.append(MessageSender.send_serverchan(title, content))
        results.append(MessageSender.send_wechat_work(title, content))
        results.append(MessageSender.send_dingtalk(title, content))
        return any(results)
