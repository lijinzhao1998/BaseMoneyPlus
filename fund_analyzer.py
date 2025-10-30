# -*- coding: utf-8 -*-
"""
基金收益分析和预测模块
"""
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from fund_data import FundDataFetcher
from moving_average_analyzer import MovingAverageAnalyzer

class FundAnalyzer:
    """基金分析器"""
    
    def __init__(self):
        self.fetcher = FundDataFetcher()
        self.ma_analyzer = MovingAverageAnalyzer()
    
    def calculate_returns(self, historical_data, cost_basis=1.0, amount=10000):
        """
        计算收益率和收益金额
        
        Args:
            historical_data: 历史数据列表
            cost_basis: 成本净值
            amount: 投资金额（元）
        """
        if not historical_data:
            return None
        
        latest_nav = historical_data[-1]["nav"] if historical_data else cost_basis
        
        # 计算收益率
        return_rate = ((latest_nav - cost_basis) / cost_basis) * 100
        
        # 计算收益金额
        profit = amount * (return_rate / 100)
        
        # 计算今日涨跌幅
        today_change = historical_data[-1]["change_rate"] if historical_data else 0
        
        # 计算今日收益
        today_profit = amount * (today_change / 100)
        
        # 计算持仓份额
        shares = amount / cost_basis
        
        # 计算持仓市值
        market_value = shares * latest_nav
        
        return {
            "return_rate": round(return_rate, 2),
            "total_profit": round(profit, 2),
            "today_change": round(today_change, 2),
            "today_profit": round(today_profit, 2),
            "market_value": round(market_value, 2),
            "shares": round(shares, 2),
            "cost_basis": cost_basis,
            "current_nav": round(latest_nav, 4)
        }
    
    def analyze_trend(self, historical_data):
        """
        分析趋势
        
        Returns:
            dict: 包含趋势分析的字典
        """
        if not historical_data or len(historical_data) < 5:
            return {
                "trend": "数据不足",
                "strength": 0,
                "volatility": 0
            }
        
        df = pd.DataFrame(historical_data)
        
        # 计算短期和长期移动平均线
        df['ma5'] = df['nav'].rolling(window=5).mean()
        df['ma10'] = df['nav'].rolling(window=10).mean()
        df['ma20'] = df['nav'].rolling(window=20).mean()
        
        latest = df.iloc[-1]
        
        # 判断趋势
        if latest['ma5'] > latest['ma10'] > latest['ma20']:
            trend = "上涨趋势"
            strength = 1
        elif latest['ma5'] < latest['ma10'] < latest['ma20']:
            trend = "下跌趋势"
            strength = -1
        else:
            trend = "震荡整理"
            strength = 0
        
        # 计算波动率
        volatility = df['change_rate'].std()
        
        # 计算趋势强度
        if len(df) >= 2:
            strength_value = (latest['nav'] - df['nav'].iloc[0]) / df['nav'].iloc[0] * 100
        else:
            strength_value = 0
        
        return {
            "trend": trend,
            "strength": round(strength_value, 2),
            "volatility": round(volatility, 2),
            "ma5": round(latest['ma5'], 4),
            "ma10": round(latest['ma10'], 4),
            "ma20": round(latest['ma20'], 4)
        }
    
    def predict_price(self, historical_data, days=5):
        """
        预测未来价格
        
        使用线性回归和移动平均进行简单预测
        
        Args:
            historical_data: 历史数据
            days: 预测未来几天
        """
        if not historical_data or len(historical_data) < 5:
            return None
        
        try:
            df = pd.DataFrame(historical_data)
            
            # 准备特征：使用过去的数据作为特征
            lookback = min(10, len(df) - 1)
            
            # 简单预测：使用线性回归
            X = np.arange(len(df) - lookback, len(df)).reshape(-1, 1)
            y = df['nav'].iloc[-lookback:].values
            
            if len(X) < 2:
                return None
            
            model = LinearRegression()
            model.fit(X, y)
            
            # 预测未来几天
            future_X = np.arange(len(df), len(df) + days).reshape(-1, 1)
            predictions = model.predict(future_X)
            
            # 获取当前净值
            current_nav = df['nav'].iloc[-1]
            
            # 计算预测的涨跌幅
            predicted_changes = [((pred - current_nav) / current_nav) * 100 
                               for pred in predictions]
            
            # 使用移动平均平滑预测
            if len(predictions) > 1:
                ma_predictions = []
                window = min(3, len(predictions))
                for i in range(len(predictions)):
                    start = max(0, i - window + 1)
                    ma_predictions.append(np.mean(predictions[start:i+1]))
                predictions = ma_predictions
            
            result = []
            for i, pred in enumerate(predictions):
                result.append({
                    "day": i + 1,
                    "predicted_nav": round(pred, 4),
                    "predicted_change": round(predicted_changes[i], 2)
                })
            
            return result
            
        except Exception as e:
            print(f"预测失败: {e}")
            return None
    
    def get_fund_analysis(self, fund_code, fund_name="", cost_basis=1.0, amount=10000, 
                          lookback_days=30, investment_start_date=None, include_ma_analysis=True):
        """
        获取完整的基金分析
        
        Args:
            fund_code: 基金代码
            fund_name: 基金名称
            cost_basis: 成本净值
            amount: 投资金额
            lookback_days: 回看天数
            investment_start_date: 投资开始日期 (YYYY-MM-DD)，用于准确计算历史收益
            include_ma_analysis: 是否包含均线分析
        """
        # 获取最新数据（用于判断是否是今天的数据）
        current_data = self.fetcher.get_fund_data(fund_code)
        is_today = current_data.get("is_today", False) if current_data else False
        data_date = current_data.get("date", "") if current_data else ""
        
        # 获取历史数据
        historical_data = self.fetcher.get_historical_data(fund_code, lookback_days)
        
        if not historical_data:
            return None
        
        # 计算收益
        returns = self.calculate_returns(historical_data, cost_basis, amount)
        
        # 分析趋势
        trend = self.analyze_trend(historical_data)
        
        # 预测未来
        prediction = self.predict_price(historical_data, days=5)
        
        result = {
            "code": fund_code,
            "name": fund_name,
            "returns": returns,
            "trend": trend,
            "prediction": prediction,
            "historical_data": historical_data,
            "is_today": is_today,
            "data_date": data_date
        }
        
        # 添加均线分析
        if include_ma_analysis:
            try:
                ma_analysis = self.ma_analyzer.analyze_fund(
                    fund_code, 
                    fund_name, 
                    investment_start_date
                )
                result["ma_analysis"] = ma_analysis
            except Exception as e:
                print(f"均线分析失败 {fund_code}: {str(e)}")
                result["ma_analysis"] = None
        
        return result
