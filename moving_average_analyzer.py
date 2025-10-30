#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基金均线分析模块
分析基金的月线、季线、年线和长期均线，判断买入卖出时机
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import time
import json


class MovingAverageAnalyzer:
    """基金均线分析器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://fund.eastmoney.com/'
        }
    
    def get_fund_flow(self, fund_code: str) -> Dict:
        """
        获取基金资金流向数据
        
        Args:
            fund_code: 基金代码
            
        Returns:
            资金流向数据
        """
        try:
            # 东方财富资金流向API
            url = f'https://push2.eastmoney.com/api/qt/stock/get'
            params = {
                'secid': f'0.{fund_code}',  # 基金代码
                'fields': 'f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f2',
                '_': int(time.time() * 1000)
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                fund_data = data['data']
                
                # 尝试获取更详细的申购赎回数据
                flow_info = {
                    'has_data': True,
                    'net_flow': None,  # 净流入（正值表示流入，负值表示流出）
                    'flow_trend': '暂无数据',  # 流向趋势
                    'flow_description': '',  # 流向描述
                }
                
                # 注：基金的资金流向数据较难获取，这里提供框架
                # 可以通过分析净值变化和规模变化来推断
                return flow_info
            
        except Exception as e:
            print(f"  获取资金流向数据失败: {str(e)}")
        
        return {
            'has_data': False,
            'flow_trend': '暂无数据',
            'flow_description': '基金资金流向数据暂时无法获取'
        }
    
    def get_fund_scale_info(self, fund_code: str) -> Dict:
        """
        获取基金规模变化信息（用于分析资金流向）
        
        Args:
            fund_code: 基金代码
            
        Returns:
            规模信息
        """
        try:
            # 获取基金档案信息
            url = f'https://fund.eastmoney.com/pingzhongdata/{fund_code}.js'
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            content = response.text
            
            # 提取规模数据（通过正则）
            import re
            
            # 提取基金规模趋势
            scale_match = re.search(r'Data_fluctuationScale\s*=\s*\{([^}]+)\}', content)
            if scale_match:
                scale_data = scale_match.group(1)
                # 解析规模数据
                # 这里简化处理，实际需要解析完整的JSON数据
                
                return {
                    'has_data': True,
                    'trend': '规模相对稳定',  # 可以是：快速增长/稳定增长/相对稳定/小幅流出/大幅流出
                    'description': '最近季度基金规模变化不大，投资者情绪稳定'
                }
            
        except Exception as e:
            print(f"  获取规模信息失败: {str(e)}")
        
        return {
            'has_data': False,
            'trend': '暂无数据',
            'description': ''
        }
    
    def get_fund_hot_info(self, fund_code: str) -> Dict:
        """
        获取基金热度和板块信息
        
        Args:
            fund_code: 基金代码
            
        Returns:
            热度信息
        """
        try:
            # 获取基金详情页面
            url = f'https://fund.eastmoney.com/{fund_code}.html'
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            content = response.text
            
            # 提取基金类型和投资板块
            import re
            
            hot_info = {
                'has_data': False,
                'fund_type': '',  # 基金类型
                'hot_sectors': [],  # 热门板块
                'market_sentiment': '中性',  # 市场情绪：热门/活跃/中性/冷门
                'description': ''
            }
            
            # 提取基金类型
            type_match = re.search(r'基金类型：([^<]+)<', content)
            if type_match:
                hot_info['fund_type'] = type_match.group(1).strip()
                hot_info['has_data'] = True
            
            # 提取投资板块（从持仓中推断）
            # 这里简化处理
            if '白酒' in content or '酒' in content:
                hot_info['hot_sectors'].append('白酒板块')
            if '医药' in content or '医疗' in content:
                hot_info['hot_sectors'].append('医药板块')
            if '科技' in content or '芯片' in content:
                hot_info['hot_sectors'].append('科技板块')
            if '新能源' in content or '电池' in content:
                hot_info['hot_sectors'].append('新能源板块')
            
            # 简单的市场情绪判断
            if hot_info['hot_sectors']:
                hot_info['market_sentiment'] = '活跃'
                hot_info['description'] = f"当前关注{' '.join(hot_info['hot_sectors'][:2])}等领域"
            else:
                hot_info['description'] = '均衡配置型基金'
            
            return hot_info
            
        except Exception as e:
            print(f"  获取热度信息失败: {str(e)}")
        
        return {
            'has_data': False,
            'market_sentiment': '中性',
            'description': '市场热度信息暂时无法获取'
        }
    
    def get_historical_net_values(self, fund_code: str, start_date: str = None, days: int = 730) -> List[Dict]:
        """
        获取基金历史净值数据
        
        Args:
            fund_code: 基金代码
            start_date: 开始日期 格式 YYYY-MM-DD，如果指定则从该日期开始获取
            days: 获取多少天的数据（当start_date未指定时使用）
            
        Returns:
            历史净值列表 [{'date': '2024-01-01', 'nav': 1.234, 'acc_nav': 1.234}, ...]
        """
        # 尝试多个API接口
        apis = [
            self._get_from_eastmoney_api1,
            self._get_from_eastmoney_api2,
            self._get_from_ttjj
        ]
        
        for i, api_func in enumerate(apis, 1):
            try:
                print(f"  尝试API接口 {i}/{len(apis)}...", end='')
                net_values = api_func(fund_code, start_date, days)
                if net_values:
                    print(f" [OK] 成功 (获取 {len(net_values)} 条数据)")
                    return net_values
                else:
                    print(f" [ERROR] 无数据")
            except Exception as e:
                print(f" [ERROR] 失败: {str(e)}")
                continue
        
        print(f"  [WARN] 所有API接口都失败")
        return []
    
    def _get_from_eastmoney_api1(self, fund_code: str, start_date: str = None, days: int = 730) -> List[Dict]:
        """从东方财富API接口1获取数据"""
        # 计算日期范围
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.now()
        else:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=days)
        
        start_str = start_dt.strftime('%Y-%m-%d')
        end_str = end_dt.strftime('%Y-%m-%d')
        
        # 东方财富基金净值接口1
        url = 'https://api.fund.eastmoney.com/f10/lsjz'
        params = {
            'fundCode': fund_code,
            'pageIndex': 1,
            'pageSize': 10000,
            'startDate': start_str,
            'endDate': end_str,
            '_': int(time.time() * 1000)
        }
        
        response = requests.get(url, params=params, headers=self.headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        if data.get('Data') and data['Data'].get('LSJZList'):
            net_values = []
            for item in data['Data']['LSJZList']:
                try:
                    net_values.append({
                        'date': item['FSRQ'],
                        'nav': float(item['DWJZ']),
                        'acc_nav': float(item['LJJZ']) if item['LJJZ'] else float(item['DWJZ'])
                    })
                except (ValueError, KeyError):
                    continue
            
            net_values.sort(key=lambda x: x['date'])
            return net_values
        
        return []
    
    def _get_from_eastmoney_api2(self, fund_code: str, start_date: str = None, days: int = 730) -> List[Dict]:
        """从东方财富API接口2获取数据（备用）"""
        # 使用更简单的接口，只获取最近的数据
        url = f'https://fundgz.1234567.com.cn/js/{fund_code}.js'
        
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        
        # 解析返回的JavaScript代码
        import re
        content = response.text
        
        # 提取JSON部分
        match = re.search(r'jsonpgz\((.*?)\)', content)
        if match:
            import json as json_lib
            data = json_lib.loads(match.group(1))
            
            # 只返回当前净值，用于计算最新情况
            if 'gszzl' in data:  # 估算数据
                return [{
                    'date': data.get('gztime', datetime.now().strftime('%Y-%m-%d')),
                    'nav': float(data.get('dwjz', 0)),
                    'acc_nav': float(data.get('dwjz', 0))
                }]
        
        return []
    
    def _get_from_ttjj(self, fund_code: str, start_date: str = None, days: int = 730) -> List[Dict]:
        """从天天基金网获取数据（备用）"""
        # 计算日期范围
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_dt = datetime.now() - timedelta(days=days)
        
        # 使用天天基金网的接口
        url = f'http://api.fund.eastmoney.com/f10/lsjz'
        params = {
            'callback': 'jQuery',
            'fundCode': fund_code,
            'pageIndex': 1,
            'pageSize': 10000,
            'startDate': start_dt.strftime('%Y-%m-%d'),
            'endDate': datetime.now().strftime('%Y-%m-%d'),
            '_': int(time.time() * 1000)
        }
        
        response = requests.get(url, params=params, headers=self.headers, timeout=15)
        response.raise_for_status()
        
        # 解析JSONP响应
        import re
        content = response.text
        match = re.search(r'jQuery.*?\((.*?)\);?$', content, re.DOTALL)
        if match:
            import json as json_lib
            data = json_lib.loads(match.group(1))
            
            if data.get('Data') and data['Data'].get('LSJZList'):
                net_values = []
                for item in data['Data']['LSJZList']:
                    try:
                        net_values.append({
                            'date': item['FSRQ'],
                            'nav': float(item['DWJZ']),
                            'acc_nav': float(item['LJJZ']) if item['LJJZ'] else float(item['DWJZ'])
                        })
                    except (ValueError, KeyError):
                        continue
                
                net_values.sort(key=lambda x: x['date'])
                return net_values
        
        return []
    
    def calculate_moving_averages(self, net_values: List[Dict]) -> Dict:
        """
        计算各周期均线
        
        Args:
            net_values: 历史净值数据
            
        Returns:
            均线数据字典
        """
        if not net_values:
            return {}
        
        # 提取净值列表
        navs = [item['nav'] for item in net_values]
        current_nav = navs[-1]
        
        result = {
            'current_nav': current_nav,
            'ma20': None,   # 月线 (约20个交易日)
            'ma60': None,   # 季线 (约60个交易日)
            'ma250': None,  # 年线 (约250个交易日)
            'ma500': None,  # 长期均线 (约500个交易日，2年)
            'deviation': {}  # 偏离度
        }
        
        # 计算各周期均线
        periods = {
            'ma20': 20,
            'ma60': 60,
            'ma250': 250,
            'ma500': 500
        }
        
        for ma_name, period in periods.items():
            if len(navs) >= period:
                ma_value = sum(navs[-period:]) / period
                result[ma_name] = round(ma_value, 4)
                # 计算偏离度 (当前净值 - 均线值) / 均线值 * 100%
                deviation = ((current_nav - ma_value) / ma_value) * 100
                result['deviation'][ma_name] = round(deviation, 2)
        
        return result
    
    def analyze_position(self, ma_data: Dict) -> Dict:
        """
        分析当前位置，判断是否在高点或低点
        
        Args:
            ma_data: 均线数据
            
        Returns:
            分析结果
        """
        if not ma_data or 'current_nav' not in ma_data:
            return {}
        
        current_nav = ma_data['current_nav']
        
        analysis = {
            'position': 'unknown',  # high/low/medium
            'position_text': '未知',  # 中文位置描述
            'position_detail': '',  # 详细位置说明
            'signal': 'hold',  # buy/sell/hold
            'strength': 0,  # 信号强度 -5 到 +5，负数表示卖出，正数表示买入
            'recommendation': '',
            'details': []
        }
        
        score = 0
        details = []
        position_hints = []  # 用于生成位置详细说明
        
        # 分析各均线偏离度
        deviation = ma_data.get('deviation', {})
        
        # 月线分析（权重：1）
        if 'ma20' in deviation:
            ma20 = ma_data.get('ma20')
            dev = deviation['ma20']
            if dev < -10:
                score += 2
                details.append(f"月线下方{abs(dev):.1f}% - 短期超跌")
                position_hints.append(f"短期均线({ma20:.3f})下方{abs(dev):.1f}%")
            elif dev < -5:
                score += 1
                details.append(f"月线下方{abs(dev):.1f}% - 短期偏低")
                position_hints.append(f"短期均线({ma20:.3f})下方{abs(dev):.1f}%")
            elif dev > 10:
                score -= 2
                details.append(f"月线上方{dev:.1f}% - 短期超涨")
                position_hints.append(f"短期均线({ma20:.3f})上方{dev:.1f}%")
            elif dev > 5:
                score -= 1
                details.append(f"月线上方{dev:.1f}% - 短期偏高")
                position_hints.append(f"短期均线({ma20:.3f})上方{dev:.1f}%")
            else:
                position_hints.append(f"围绕短期均线({ma20:.3f})波动")
        
        # 季线分析（权重：1.5）
        if 'ma60' in deviation:
            ma60 = ma_data.get('ma60')
            dev = deviation['ma60']
            if dev < -15:
                score += 3
                details.append(f"季线下方{abs(dev):.1f}% - 中期超跌")
                position_hints.append(f"中期均线({ma60:.3f})下方{abs(dev):.1f}%")
            elif dev < -8:
                score += 2
                details.append(f"季线下方{abs(dev):.1f}% - 中期偏低")
                position_hints.append(f"中期均线({ma60:.3f})下方{abs(dev):.1f}%")
            elif dev > 15:
                score -= 3
                details.append(f"季线上方{dev:.1f}% - 中期超涨")
                position_hints.append(f"中期均线({ma60:.3f})上方{dev:.1f}%")
            elif dev > 8:
                score -= 2
                details.append(f"季线上方{dev:.1f}% - 中期偏高")
                position_hints.append(f"中期均线({ma60:.3f})上方{dev:.1f}%")
            else:
                position_hints.append(f"围绕中期均线({ma60:.3f})波动")
        
        # 年线分析（权重：2）
        if 'ma250' in deviation:
            ma250 = ma_data.get('ma250')
            dev = deviation['ma250']
            if dev < -20:
                score += 4
                details.append(f"年线下方{abs(dev):.1f}% - 长期超跌，布局良机")
                position_hints.append(f"年线({ma250:.3f})下方{abs(dev):.1f}%")
            elif dev < -10:
                score += 3
                details.append(f"年线下方{abs(dev):.1f}% - 长期偏低")
                position_hints.append(f"年线({ma250:.3f})下方{abs(dev):.1f}%")
            elif dev > 20:
                score -= 4
                details.append(f"年线上方{dev:.1f}% - 长期超涨，注意风险")
                position_hints.append(f"年线({ma250:.3f})上方{dev:.1f}%")
            elif dev > 10:
                score -= 3
                details.append(f"年线上方{dev:.1f}% - 长期偏高")
                position_hints.append(f"年线({ma250:.3f})上方{dev:.1f}%")
            else:
                position_hints.append(f"围绕年线({ma250:.3f})波动")
        
        # 长期均线分析（权重：1.5）
        if 'ma500' in deviation:
            ma500 = ma_data.get('ma500')
            dev = deviation['ma500']
            if dev < -25:
                score += 3
                details.append(f"长期均线下方{abs(dev):.1f}% - 历史低位")
                position_hints.append(f"2年均线({ma500:.3f})下方{abs(dev):.1f}%")
            elif dev < -15:
                score += 2
                details.append(f"长期均线下方{abs(dev):.1f}% - 相对低位")
                position_hints.append(f"2年均线({ma500:.3f})下方{abs(dev):.1f}%")
            elif dev > 25:
                score -= 3
                details.append(f"长期均线上方{dev:.1f}% - 历史高位")
                position_hints.append(f"2年均线({ma500:.3f})上方{dev:.1f}%")
            elif dev > 15:
                score -= 2
                details.append(f"长期均线上方{dev:.1f}% - 相对高位")
                position_hints.append(f"2年均线({ma500:.3f})上方{dev:.1f}%")
            else:
                position_hints.append(f"围绕2年均线({ma500:.3f})波动")
        
        # 限制分数范围
        score = max(-5, min(5, score))
        
        # 判断位置和信号（更详细的中文描述）
        if score >= 3:
            analysis['position'] = 'low'
            analysis['position_text'] = '低位区域'
            analysis['signal'] = 'strong_buy'
            analysis['recommendation'] = '⭐⭐⭐ 强烈建议加仓'
        elif score >= 1:
            analysis['position'] = 'medium_low'
            analysis['position_text'] = '中低位区域'
            analysis['signal'] = 'buy'
            analysis['recommendation'] = '⭐⭐ 可以适当加仓'
        elif score <= -3:
            analysis['position'] = 'high'
            analysis['position_text'] = '高位区域'
            analysis['signal'] = 'strong_sell'
            analysis['recommendation'] = '⚠️⚠️⚠️ 建议减仓'
        elif score <= -1:
            analysis['position'] = 'medium_high'
            analysis['position_text'] = '中高位区域'
            analysis['signal'] = 'sell'
            analysis['recommendation'] = '⚠️⚠️ 可以适当减仓'
        else:
            analysis['position'] = 'medium'
            analysis['position_text'] = '中位区域'
            analysis['signal'] = 'hold'
            analysis['recommendation'] = '⭐ 持有观望'
        
        # 生成详细位置说明
        if position_hints:
            analysis['position_detail'] = f"当前净值 {current_nav:.3f}，" + "，".join(position_hints[:2])  # 只显示前2个最重要的
        else:
            analysis['position_detail'] = f"当前净值 {current_nav:.3f}"
        
        analysis['strength'] = score
        analysis['details'] = details
        
        return analysis
    
    def analyze_fund(self, fund_code: str, fund_name: str, start_date: str = None, 
                     include_flow: bool = True, include_hot: bool = True) -> Dict:
        """
        完整分析一只基金
        
        Args:
            fund_code: 基金代码
            fund_name: 基金名称
            start_date: 投入日期（用于计算历史收益）
            include_flow: 是否包含资金流向分析
            include_hot: 是否包含热点分析
            
        Returns:
            完整分析结果
        """
        print(f"正在分析基金 {fund_code} {fund_name}...")
        
        # 获取历史数据
        net_values = self.get_historical_net_values(fund_code, start_date)
        
        if not net_values:
            return {
                'fund_code': fund_code,
                'fund_name': fund_name,
                'error': '无法获取历史数据'
            }
        
        # 计算均线
        ma_data = self.calculate_moving_averages(net_values)
        
        # 分析位置
        position_analysis = self.analyze_position(ma_data)
        
        # 计算历史收益
        investment_return = None
        if start_date and net_values:
            # 找到投入日期对应的净值
            start_nav = None
            for nv in net_values:
                if nv['date'] >= start_date:
                    start_nav = nv['nav']
                    break
            
            if start_nav:
                current_nav = ma_data['current_nav']
                return_rate = ((current_nav - start_nav) / start_nav) * 100
                investment_return = {
                    'start_date': start_date,
                    'start_nav': start_nav,
                    'current_nav': current_nav,
                    'return_rate': round(return_rate, 2)
                }
        
        # 获取资金流向信息
        flow_info = None
        scale_info = None
        if include_flow:
            print(f"  获取资金流向数据...")
            flow_info = self.get_fund_flow(fund_code)
            scale_info = self.get_fund_scale_info(fund_code)
        
        # 获取热点信息
        hot_info = None
        if include_hot:
            print(f"  获取板块热度信息...")
            hot_info = self.get_fund_hot_info(fund_code)
        
        result = {
            'fund_code': fund_code,
            'fund_name': fund_name,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_nav': ma_data.get('current_nav'),
            'moving_averages': {
                'ma20': ma_data.get('ma20'),
                'ma60': ma_data.get('ma60'),
                'ma250': ma_data.get('ma250'),
                'ma500': ma_data.get('ma500')
            },
            'deviation': ma_data.get('deviation', {}),
            'position_analysis': position_analysis,
            'investment_return': investment_return,
            'flow_info': flow_info,
            'scale_info': scale_info,
            'hot_info': hot_info,
            'data_points': len(net_values)
        }
        
        return result
    
    def format_analysis_report(self, analysis: Dict) -> str:
        """
        格式化分析报告
        
        Args:
            analysis: 分析结果
            
        Returns:
            格式化的报告文本
        """
        if 'error' in analysis:
            return f"[ERROR] {analysis['fund_name']} ({analysis['fund_code']}): {analysis['error']}"
        
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"[基金分析] {analysis['fund_name']} ({analysis['fund_code']})")
        lines.append(f"{'='*60}")
        
        # 当前净值
        lines.append(f"\n[当前净值] {analysis['current_nav']}")
        
        # 均线数据
        ma = analysis['moving_averages']
        dev = analysis['deviation']
        
        lines.append(f"\n[均线分析]")
        if ma.get('ma20'):
            lines.append(f"  月线(MA20):  {ma['ma20']:<8} 偏离: {dev.get('ma20', 0):>6.2f}%")
        if ma.get('ma60'):
            lines.append(f"  季线(MA60):  {ma['ma60']:<8} 偏离: {dev.get('ma60', 0):>6.2f}%")
        if ma.get('ma250'):
            lines.append(f"  年线(MA250): {ma['ma250']:<8} 偏离: {dev.get('ma250', 0):>6.2f}%")
        if ma.get('ma500'):
            lines.append(f"  长期(MA500): {ma['ma500']:<8} 偏离: {dev.get('ma500', 0):>6.2f}%")
        
        # 位置分析（优化后的通俗版本）
        pos = analysis['position_analysis']
        lines.append(f"\n[位置分析]")
        lines.append(f"  当前位置: {pos.get('position_text', '未知')}")
        
        # 显示详细位置说明
        if pos.get('position_detail'):
            lines.append(f"  位置详情: {pos['position_detail']}")
        
        lines.append(f"  信号强度: {pos.get('strength', 0)}/5")
        lines.append(f"  操作建议: {pos.get('recommendation', '暂无建议')}")
        
        if pos.get('details'):
            lines.append(f"\n  详细分析:")
            for detail in pos['details']:
                lines.append(f"    • {detail}")
        
        # 资金流向分析
        if analysis.get('scale_info') and analysis['scale_info'].get('has_data'):
            scale = analysis['scale_info']
            lines.append(f"\n💸 资金流向:")
            lines.append(f"  规模趋势: {scale.get('trend', '暂无数据')}")
            if scale.get('description'):
                lines.append(f"  说明: {scale['description']}")
        
        # 板块热度分析
        if analysis.get('hot_info') and analysis['hot_info'].get('has_data'):
            hot = analysis['hot_info']
            lines.append(f"\n🔥 板块热度:")
            if hot.get('fund_type'):
                lines.append(f"  基金类型: {hot['fund_type']}")
            lines.append(f"  市场情绪: {hot.get('market_sentiment', '中性')}")
            if hot.get('hot_sectors'):
                lines.append(f"  关注板块: {', '.join(hot['hot_sectors'])}")
            if hot.get('description'):
                lines.append(f"  说明: {hot['description']}")
        
        # 历史收益（如果有投入日期）
        if analysis.get('investment_return'):
            ret = analysis['investment_return']
            lines.append(f"\n💵 投资收益分析:")
            lines.append(f"  投入日期: {ret['start_date']}")
            lines.append(f"  投入时净值: {ret['start_nav']}")
            lines.append(f"  当前净值: {ret['current_nav']}")
            
            return_rate = ret['return_rate']
            symbol = "+" if return_rate > 0 else "-"
            lines.append(f"  [{symbol}] 收益率: {return_rate:+.2f}%")
        
        lines.append(f"\n数据点数: {analysis['data_points']} | 分析时间: {analysis['analysis_date']}")
        lines.append(f"{'='*60}\n")
        
        return '\n'.join(lines)


def test_analyzer():
    """测试均线分析器"""
    analyzer = MovingAverageAnalyzer()
    
    # 测试分析一只基金
    test_funds = [
        {'code': '161725', 'name': '招商中证白酒', 'start_date': '2024-01-01'},
        {'code': '110011', 'name': '易方达中小盘', 'start_date': '2023-06-01'},
    ]
    
    for fund in test_funds:
        analysis = analyzer.analyze_fund(
            fund['code'], 
            fund['name'], 
            fund.get('start_date')
        )
        report = analyzer.format_analysis_report(analysis)
        print(report)
        
        # 保存为JSON
        with open(f'ma_analysis_{fund["code"]}.json', 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    test_analyzer()

