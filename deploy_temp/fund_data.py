# -*- coding: utf-8 -*-
"""
基金数据获取模块
"""
import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import random
from fake_useragent import UserAgent

class FundDataFetcher:
    """基金数据获取器"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        
    def get_fund_data(self, fund_code):
        """
        获取基金实时数据
        使用天天基金网API
        """
        try:
            # 基金净值API（天天基金）
            url = f"http://fund.eastmoney.com/{fund_code}.html"
            
            # 使用备用API - 基金估值API
            api_url = f"http://api.fund.eastmoney.com/f10/lsjz"
            params = {
                "callback": "jQuery18308287199182460985_1699000000000",
                "fundCode": fund_code,
                "pageIndex": "1",
                "pageSize": "100",
                "startDate": "",
                "endDate": "",
                "_": int(time.time() * 1000)
            }
            
            headers = {
                "User-Agent": self.ua.random,
                "Referer": f"http://fund.eastmoney.com/{fund_code}.html"
            }
            
            # 获取基金净值数据
            response = self.session.get(api_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # 解析JSON数据
                text = response.text
                
                # 尝试解析纯JSON
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    # 如果不是纯JSON，尝试解析JSONP
                    start = text.find('(')
                    end = text.rfind(')')
                    if start != -1 and end != -1:
                        json_str = text[start+1:end]
                        data = json.loads(json_str)
                    else:
                        data = None
                
                if data and data.get("Data") and len(data["Data"]["LSJZList"]) > 0:
                    latest = data["Data"]["LSJZList"][0]
                    fund_data = {
                        "code": fund_code,
                        "date": latest["FSRQ"],
                        "nav": float(latest["DWJZ"]),  # 单位净值
                        "change_rate": float(latest.get("JZZZL", 0)),  # 涨跌幅
                        "change_amount": float(latest.get("LJJZ", 0)) - float(latest.get("DWJZ", 0)) if latest.get("LJJZ") else 0
                    }
                    # 检查是否是今天的数据
                    from datetime import datetime
                    today = datetime.now().strftime("%Y-%m-%d")
                    fund_data["is_today"] = latest["FSRQ"] == today
                    return fund_data
            
            # 如果上面失败，尝试另一个API
            return self._get_fund_data_alternative(fund_code)
            
        except Exception as e:
            print(f"获取基金 {fund_code} 数据失败: {e}")
            return None
    
    def _get_fund_data_alternative(self, fund_code):
        """备用方案：使用东方财富实时接口"""
        try:
            url = f"http://fundgz.1234567.com.cn/js/{fund_code}.js"
            headers = {
                "User-Agent": self.ua.random
            }
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                text = response.text
                # 解析JSONP
                start = text.find('(')
                end = text.rfind(')')
                if start != -1 and end != -1:
                    json_str = text[start+1:end]
                    data = json.loads(json_str)
                    
                    fund_data = {
                        "code": fund_code,
                        "date": data.get("gztime", ""),
                        "nav": float(data.get("gsz", 0)),
                        "change_rate": float(data.get("gszzl", 0)),
                        "change_amount": 0,
                        "name": data.get("name", "")
                    }
                    # 备用API返回的是实时估值，标记为非今日正式数据
                    fund_data["is_today"] = False
                    return fund_data
        except Exception as e:
            print(f"备用方案也失败: {e}")
        
        return None
    
    def get_historical_data(self, fund_code, days=30):
        """
        获取历史数据
        """
        try:
            api_url = f"http://api.fund.eastmoney.com/f10/lsjz"
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            params = {
                "fundCode": fund_code,
                "pageIndex": "1",
                "pageSize": str(days),
                "startDate": start_date,
                "endDate": end_date,
                "_": int(time.time() * 1000)
            }
            
            headers = {
                "User-Agent": self.ua.random,
                "Referer": f"http://fund.eastmoney.com/{fund_code}.html"
            }
            
            response = self.session.get(api_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                text = response.text
                
                # 尝试解析纯JSON
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    # 如果不是纯JSON，尝试解析JSONP
                    start = text.find('(')
                    end = text.rfind(')')
                    if start != -1 and end != -1:
                        json_str = text[start+1:end]
                        data = json.loads(json_str)
                    else:
                        data = None
                
                if data:
                    records = []
                    if data.get("Data") and data["Data"].get("LSJZList"):
                        for item in reversed(data["Data"]["LSJZList"]):
                            records.append({
                                "date": item["FSRQ"],
                                "nav": float(item["DWJZ"]),
                                "change_rate": float(item.get("JZZZL", 0))
                            })
                    
                    return records
        except Exception as e:
            print(f"获取历史数据失败: {e}")
        
        return []
    
    def get_all_funds_data(self, fund_codes):
        """获取所有基金的数据"""
        all_data = {}
        for code in fund_codes:
            data = self.get_fund_data(code)
            if data:
                all_data[code] = data
            time.sleep(1)  # 避免请求过快
        return all_data
