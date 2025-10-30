#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基金分析报告生成器
支持导出为TXT、HTML、Markdown等格式
"""

from datetime import datetime
from typing import Dict, List
import os


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.report_dir = "reports"
        self._ensure_report_dir()
    
    def _ensure_report_dir(self):
        """确保报告目录存在"""
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
    
    def generate_txt_report(self, analysis_results: List[Dict], filename: str = None) -> str:
        """
        生成TXT格式报告
        
        Args:
            analysis_results: 分析结果列表
            filename: 文件名（可选）
            
        Returns:
            保存的文件路径
        """
        if not filename:
            filename = f"fund_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        filepath = os.path.join(self.report_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # 标题
            f.write("=" * 80 + "\n")
            f.write("基金均线分析报告\n".center(78))
            f.write("=" * 80 + "\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"分析基金数量: {len(analysis_results)}\n")
            f.write("=" * 80 + "\n\n")
            
            # 汇总统计
            strong_buy = []
            buy = []
            hold = []
            sell = []
            strong_sell = []
            errors = []
            
            for result in analysis_results:
                if 'error' in result:
                    errors.append(result)
                    continue
                
                pos = result.get('position_analysis', {})
                signal = pos.get('signal', 'hold')
                fund_info = f"{result['fund_name']} ({result['fund_code']})"
                
                if signal == 'strong_buy':
                    strong_buy.append(result)
                elif signal == 'buy':
                    buy.append(result)
                elif signal == 'strong_sell':
                    strong_sell.append(result)
                elif signal == 'sell':
                    sell.append(result)
                else:
                    hold.append(result)
            
            # 操作建议汇总
            f.write("【操作建议汇总】\n\n")
            
            if strong_buy:
                f.write("⭐⭐⭐ 强烈建议加仓:\n")
                for result in strong_buy:
                    f.write(f"  • {result['fund_name']} ({result['fund_code']})\n")
                f.write("\n")
            
            if buy:
                f.write("⭐⭐ 可以适当加仓:\n")
                for result in buy:
                    f.write(f"  • {result['fund_name']} ({result['fund_code']})\n")
                f.write("\n")
            
            if hold:
                f.write("⭐ 持有观望:\n")
                for result in hold:
                    f.write(f"  • {result['fund_name']} ({result['fund_code']})\n")
                f.write("\n")
            
            if sell:
                f.write("⚠️⚠️ 可以适当减仓:\n")
                for result in sell:
                    f.write(f"  • {result['fund_name']} ({result['fund_code']})\n")
                f.write("\n")
            
            if strong_sell:
                f.write("⚠️⚠️⚠️ 建议减仓:\n")
                for result in strong_sell:
                    f.write(f"  • {result['fund_name']} ({result['fund_code']})\n")
                f.write("\n")
            
            if errors:
                f.write("❌ 分析失败:\n")
                for result in errors:
                    f.write(f"  • {result['fund_name']} ({result['fund_code']}): {result['error']}\n")
                f.write("\n")
            
            f.write("=" * 80 + "\n\n")
            
            # 详细分析
            f.write("【详细分析】\n\n")
            
            for result in analysis_results:
                if 'error' in result:
                    f.write(f"基金: {result['fund_name']} ({result['fund_code']})\n")
                    f.write(f"错误: {result['error']}\n")
                    f.write("-" * 80 + "\n\n")
                    continue
                
                f.write(f"基金: {result['fund_name']} ({result['fund_code']})\n")
                f.write(f"当前净值: {result['current_nav']}\n")
                f.write(f"分析时间: {result['analysis_date']}\n\n")
                
                # 均线数据
                ma = result['moving_averages']
                dev = result['deviation']
                
                f.write("均线分析:\n")
                if ma.get('ma20'):
                    f.write(f"  月线(MA20):  {ma['ma20']:<8}  偏离: {dev.get('ma20', 0):>6.2f}%\n")
                if ma.get('ma60'):
                    f.write(f"  季线(MA60):  {ma['ma60']:<8}  偏离: {dev.get('ma60', 0):>6.2f}%\n")
                if ma.get('ma250'):
                    f.write(f"  年线(MA250): {ma['ma250']:<8}  偏离: {dev.get('ma250', 0):>6.2f}%\n")
                if ma.get('ma500'):
                    f.write(f"  长期(MA500): {ma['ma500']:<8}  偏离: {dev.get('ma500', 0):>6.2f}%\n")
                
                # 位置分析
                pos = result['position_analysis']
                f.write(f"\n位置分析:\n")
                f.write(f"  当前位置: {pos.get('position', 'unknown')}\n")
                f.write(f"  信号强度: {pos.get('strength', 0)}/5\n")
                f.write(f"  操作建议: {pos.get('recommendation', '暂无建议')}\n")
                
                if pos.get('details'):
                    f.write(f"\n  详细分析:\n")
                    for detail in pos['details']:
                        f.write(f"    • {detail}\n")
                
                # 历史收益
                if result.get('investment_return'):
                    ret = result['investment_return']
                    f.write(f"\n投资收益:\n")
                    f.write(f"  投入日期: {ret['start_date']}\n")
                    f.write(f"  投入时净值: {ret['start_nav']}\n")
                    f.write(f"  当前净值: {ret['current_nav']}\n")
                    f.write(f"  收益率: {ret['return_rate']:+.2f}%\n")
                
                f.write("\n" + "-" * 80 + "\n\n")
            
            # 风险提示
            f.write("=" * 80 + "\n")
            f.write("【风险提示】\n\n")
            f.write("本报告基于技术分析生成，仅供参考，不构成投资建议。\n")
            f.write("投资有风险，决策需谨慎！\n")
            f.write("=" * 80 + "\n")
        
        return filepath
    
    def generate_html_report(self, analysis_results: List[Dict], filename: str = None) -> str:
        """
        生成HTML格式报告
        
        Args:
            analysis_results: 分析结果列表
            filename: 文件名（可选）
            
        Returns:
            保存的文件路径
        """
        if not filename:
            filename = f"fund_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        filepath = os.path.join(self.report_dir, filename)
        
        # 汇总统计
        strong_buy = []
        buy = []
        hold = []
        sell = []
        strong_sell = []
        errors = []
        
        for result in analysis_results:
            if 'error' in result:
                errors.append(result)
                continue
            
            pos = result.get('position_analysis', {})
            signal = pos.get('signal', 'hold')
            
            if signal == 'strong_buy':
                strong_buy.append(result)
            elif signal == 'buy':
                buy.append(result)
            elif signal == 'strong_sell':
                strong_sell.append(result)
            elif signal == 'sell':
                sell.append(result)
            else:
                hold.append(result)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # HTML头部
            f.write("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>基金均线分析报告</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .summary {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
        }
        
        .summary h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .signal-group {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 8px;
            background: white;
        }
        
        .signal-group h3 {
            margin-bottom: 10px;
            font-size: 1.3em;
        }
        
        .signal-group.strong-buy {
            border-left: 5px solid #28a745;
        }
        
        .signal-group.buy {
            border-left: 5px solid #17a2b8;
        }
        
        .signal-group.hold {
            border-left: 5px solid #6c757d;
        }
        
        .signal-group.sell {
            border-left: 5px solid #ffc107;
        }
        
        .signal-group.strong-sell {
            border-left: 5px solid #dc3545;
        }
        
        .fund-item {
            padding: 8px 15px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 5px;
        }
        
        .fund-card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .fund-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }
        
        .fund-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        
        .fund-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        
        .info-item {
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        
        .info-item label {
            font-weight: bold;
            color: #555;
            display: block;
            margin-bottom: 5px;
        }
        
        .info-item value {
            color: #333;
            font-size: 1.1em;
        }
        
        .ma-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        .ma-table th,
        .ma-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        
        .ma-table th {
            background: #667eea;
            color: white;
            font-weight: bold;
        }
        
        .ma-table tr:hover {
            background: #f8f9fa;
        }
        
        .deviation-positive {
            color: #dc3545;
            font-weight: bold;
        }
        
        .deviation-negative {
            color: #28a745;
            font-weight: bold;
        }
        
        .recommendation {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            font-size: 1.2em;
            text-align: center;
        }
        
        .details {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .details ul {
            list-style: none;
            padding-left: 0;
        }
        
        .details li {
            padding: 8px 0;
            border-bottom: 1px solid #dee2e6;
        }
        
        .details li:last-child {
            border-bottom: none;
        }
        
        .details li:before {
            content: "• ";
            color: #667eea;
            font-weight: bold;
            font-size: 1.5em;
            margin-right: 10px;
        }
        
        .footer {
            background: #333;
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .footer p {
            margin: 5px 0;
        }
        
        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .badge-success {
            background: #28a745;
            color: white;
        }
        
        .badge-danger {
            background: #dc3545;
            color: white;
        }
        
        .badge-warning {
            background: #ffc107;
            color: #333;
        }
        
        .badge-info {
            background: #17a2b8;
            color: white;
        }
        
        .badge-secondary {
            background: #6c757d;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 基金均线分析报告</h1>
            <p>生成时间: """ + datetime.now().strftime('%Y年%m月%d日 %H:%M:%S') + """</p>
            <p>分析基金数量: """ + str(len(analysis_results)) + """</p>
        </div>
        
        <div class="content">
            <div class="summary">
                <h2>📈 操作建议汇总</h2>
""")
            
            # 操作建议汇总
            if strong_buy:
                f.write('                <div class="signal-group strong-buy">\n')
                f.write('                    <h3>⭐⭐⭐ 强烈建议加仓</h3>\n')
                for result in strong_buy:
                    f.write(f'                    <div class="fund-item">{result["fund_name"]} ({result["fund_code"]})</div>\n')
                f.write('                </div>\n')
            
            if buy:
                f.write('                <div class="signal-group buy">\n')
                f.write('                    <h3>⭐⭐ 可以适当加仓</h3>\n')
                for result in buy:
                    f.write(f'                    <div class="fund-item">{result["fund_name"]} ({result["fund_code"]})</div>\n')
                f.write('                </div>\n')
            
            if hold:
                f.write('                <div class="signal-group hold">\n')
                f.write('                    <h3>⭐ 持有观望</h3>\n')
                for result in hold:
                    f.write(f'                    <div class="fund-item">{result["fund_name"]} ({result["fund_code"]})</div>\n')
                f.write('                </div>\n')
            
            if sell:
                f.write('                <div class="signal-group sell">\n')
                f.write('                    <h3>⚠️⚠️ 可以适当减仓</h3>\n')
                for result in sell:
                    f.write(f'                    <div class="fund-item">{result["fund_name"]} ({result["fund_code"]})</div>\n')
                f.write('                </div>\n')
            
            if strong_sell:
                f.write('                <div class="signal-group strong-sell">\n')
                f.write('                    <h3>⚠️⚠️⚠️ 建议减仓</h3>\n')
                for result in strong_sell:
                    f.write(f'                    <div class="fund-item">{result["fund_name"]} ({result["fund_code"]})</div>\n')
                f.write('                </div>\n')
            
            if errors:
                f.write('                <div class="signal-group" style="border-left: 5px solid #dc3545;">\n')
                f.write('                    <h3>❌ 分析失败</h3>\n')
                for result in errors:
                    f.write(f'                    <div class="fund-item">{result["fund_name"]} ({result["fund_code"]}): {result["error"]}</div>\n')
                f.write('                </div>\n')
            
            f.write("""            </div>
            
            <h2 style="margin: 30px 0 20px 0; color: #333; font-size: 1.8em; border-bottom: 3px solid #667eea; padding-bottom: 10px;">📊 详细分析</h2>
""")
            
            # 详细分析
            for result in analysis_results:
                if 'error' in result:
                    f.write(f'''            <div class="fund-card">
                <h3>{result["fund_name"]} ({result["fund_code"]})</h3>
                <p style="color: #dc3545;">❌ 错误: {result["error"]}</p>
            </div>
''')
                    continue
                
                ma = result['moving_averages']
                dev = result['deviation']
                pos = result['position_analysis']
                
                f.write(f'''            <div class="fund-card">
                <h3>{result["fund_name"]} ({result["fund_code"]})</h3>
                
                <div class="fund-info">
                    <div class="info-item">
                        <label>当前净值</label>
                        <value>{result["current_nav"]}</value>
                    </div>
                    <div class="info-item">
                        <label>分析时间</label>
                        <value>{result["analysis_date"]}</value>
                    </div>
                    <div class="info-item">
                        <label>数据点数</label>
                        <value>{result["data_points"]} 条</value>
                    </div>
                </div>
                
                <h4 style="margin: 20px 0 10px 0; color: #555;">均线分析</h4>
                <table class="ma-table">
                    <thead>
                        <tr>
                            <th>周期</th>
                            <th>均线值</th>
                            <th>偏离度</th>
                        </tr>
                    </thead>
                    <tbody>
''')
                
                if ma.get('ma20'):
                    dev_class = 'deviation-positive' if dev.get('ma20', 0) > 0 else 'deviation-negative'
                    f.write(f'''                        <tr>
                            <td>月线 (MA20)</td>
                            <td>{ma["ma20"]}</td>
                            <td class="{dev_class}">{dev.get("ma20", 0):+.2f}%</td>
                        </tr>
''')
                
                if ma.get('ma60'):
                    dev_class = 'deviation-positive' if dev.get('ma60', 0) > 0 else 'deviation-negative'
                    f.write(f'''                        <tr>
                            <td>季线 (MA60)</td>
                            <td>{ma["ma60"]}</td>
                            <td class="{dev_class}">{dev.get("ma60", 0):+.2f}%</td>
                        </tr>
''')
                
                if ma.get('ma250'):
                    dev_class = 'deviation-positive' if dev.get('ma250', 0) > 0 else 'deviation-negative'
                    f.write(f'''                        <tr>
                            <td>年线 (MA250)</td>
                            <td>{ma["ma250"]}</td>
                            <td class="{dev_class}">{dev.get("ma250", 0):+.2f}%</td>
                        </tr>
''')
                
                if ma.get('ma500'):
                    dev_class = 'deviation-positive' if dev.get('ma500', 0) > 0 else 'deviation-negative'
                    f.write(f'''                        <tr>
                            <td>长期 (MA500)</td>
                            <td>{ma["ma500"]}</td>
                            <td class="{dev_class}">{dev.get("ma500", 0):+.2f}%</td>
                        </tr>
''')
                
                f.write('''                    </tbody>
                </table>
                
''')
                
                f.write(f'''                <div class="recommendation">
                    {pos.get("recommendation", "暂无建议")} (信号强度: {pos.get("strength", 0)}/5)
                </div>
''')
                
                if pos.get('details'):
                    f.write('''                <div class="details">
                    <h4 style="margin-bottom: 10px; color: #555;">详细分析</h4>
                    <ul>
''')
                    for detail in pos['details']:
                        f.write(f'                        <li>{detail}</li>\n')
                    f.write('''                    </ul>
                </div>
''')
                
                if result.get('investment_return'):
                    ret = result['investment_return']
                    badge_class = 'badge-success' if ret['return_rate'] > 0 else 'badge-danger'
                    f.write(f'''                <div class="details">
                    <h4 style="margin-bottom: 10px; color: #555;">投资收益</h4>
                    <div class="fund-info">
                        <div class="info-item">
                            <label>投入日期</label>
                            <value>{ret["start_date"]}</value>
                        </div>
                        <div class="info-item">
                            <label>投入时净值</label>
                            <value>{ret["start_nav"]}</value>
                        </div>
                        <div class="info-item">
                            <label>当前净值</label>
                            <value>{ret["current_nav"]}</value>
                        </div>
                        <div class="info-item">
                            <label>收益率</label>
                            <value><span class="badge {badge_class}">{ret["return_rate"]:+.2f}%</span></value>
                        </div>
                    </div>
                </div>
''')
                
                f.write('            </div>\n\n')
            
            # HTML尾部
            f.write("""        </div>
        
        <div class="footer">
            <p><strong>⚠️ 风险提示</strong></p>
            <p>本报告基于技术分析生成，仅供参考，不构成投资建议。</p>
            <p>投资有风险，决策需谨慎！</p>
        </div>
    </div>
</body>
</html>
""")
        
        return filepath
    
    def generate_markdown_report(self, analysis_results: List[Dict], filename: str = None) -> str:
        """
        生成Markdown格式报告
        
        Args:
            analysis_results: 分析结果列表
            filename: 文件名（可选）
            
        Returns:
            保存的文件路径
        """
        if not filename:
            filename = f"fund_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        filepath = os.path.join(self.report_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # 标题
            f.write("# 基金均线分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
            f.write(f"**分析基金数量**: {len(analysis_results)}\n\n")
            f.write("---\n\n")
            
            # 汇总统计
            strong_buy = []
            buy = []
            hold = []
            sell = []
            strong_sell = []
            errors = []
            
            for result in analysis_results:
                if 'error' in result:
                    errors.append(result)
                    continue
                
                pos = result.get('position_analysis', {})
                signal = pos.get('signal', 'hold')
                
                if signal == 'strong_buy':
                    strong_buy.append(result)
                elif signal == 'buy':
                    buy.append(result)
                elif signal == 'strong_sell':
                    strong_sell.append(result)
                elif signal == 'sell':
                    sell.append(result)
                else:
                    hold.append(result)
            
            # 操作建议汇总
            f.write("## 📊 操作建议汇总\n\n")
            
            if strong_buy:
                f.write("### ⭐⭐⭐ 强烈建议加仓\n\n")
                for result in strong_buy:
                    f.write(f"- **{result['fund_name']}** (`{result['fund_code']}`)\n")
                f.write("\n")
            
            if buy:
                f.write("### ⭐⭐ 可以适当加仓\n\n")
                for result in buy:
                    f.write(f"- **{result['fund_name']}** (`{result['fund_code']}`)\n")
                f.write("\n")
            
            if hold:
                f.write("### ⭐ 持有观望\n\n")
                for result in hold:
                    f.write(f"- **{result['fund_name']}** (`{result['fund_code']}`)\n")
                f.write("\n")
            
            if sell:
                f.write("### ⚠️⚠️ 可以适当减仓\n\n")
                for result in sell:
                    f.write(f"- **{result['fund_name']}** (`{result['fund_code']}`)\n")
                f.write("\n")
            
            if strong_sell:
                f.write("### ⚠️⚠️⚠️ 建议减仓\n\n")
                for result in strong_sell:
                    f.write(f"- **{result['fund_name']}** (`{result['fund_code']}`)\n")
                f.write("\n")
            
            if errors:
                f.write("### ❌ 分析失败\n\n")
                for result in errors:
                    f.write(f"- **{result['fund_name']}** (`{result['fund_code']}`): {result['error']}\n")
                f.write("\n")
            
            f.write("---\n\n")
            
            # 详细分析
            f.write("## 📈 详细分析\n\n")
            
            for result in analysis_results:
                if 'error' in result:
                    f.write(f"### {result['fund_name']} (`{result['fund_code']}`)\n\n")
                    f.write(f"❌ **错误**: {result['error']}\n\n")
                    continue
                
                f.write(f"### {result['fund_name']} (`{result['fund_code']}`)\n\n")
                f.write(f"**当前净值**: {result['current_nav']}  \n")
                f.write(f"**分析时间**: {result['analysis_date']}  \n")
                f.write(f"**数据点数**: {result['data_points']} 条\n\n")
                
                # 均线数据
                ma = result['moving_averages']
                dev = result['deviation']
                
                f.write("#### 均线分析\n\n")
                f.write("| 周期 | 均线值 | 偏离度 |\n")
                f.write("|------|--------|--------|\n")
                
                if ma.get('ma20'):
                    f.write(f"| 月线 (MA20) | {ma['ma20']} | {dev.get('ma20', 0):+.2f}% |\n")
                if ma.get('ma60'):
                    f.write(f"| 季线 (MA60) | {ma['ma60']} | {dev.get('ma60', 0):+.2f}% |\n")
                if ma.get('ma250'):
                    f.write(f"| 年线 (MA250) | {ma['ma250']} | {dev.get('ma250', 0):+.2f}% |\n")
                if ma.get('ma500'):
                    f.write(f"| 长期 (MA500) | {ma['ma500']} | {dev.get('ma500', 0):+.2f}% |\n")
                
                # 位置分析
                pos = result['position_analysis']
                f.write(f"\n#### 位置分析\n\n")
                f.write(f"**操作建议**: {pos.get('recommendation', '暂无建议')}  \n")
                f.write(f"**信号强度**: {pos.get('strength', 0)}/5  \n")
                f.write(f"**当前位置**: {pos.get('position', 'unknown')}\n\n")
                
                if pos.get('details'):
                    f.write("**详细分析**:\n\n")
                    for detail in pos['details']:
                        f.write(f"- {detail}\n")
                    f.write("\n")
                
                # 历史收益
                if result.get('investment_return'):
                    ret = result['investment_return']
                    f.write(f"#### 投资收益\n\n")
                    f.write(f"- **投入日期**: {ret['start_date']}\n")
                    f.write(f"- **投入时净值**: {ret['start_nav']}\n")
                    f.write(f"- **当前净值**: {ret['current_nav']}\n")
                    f.write(f"- **收益率**: **{ret['return_rate']:+.2f}%**\n\n")
                
                f.write("---\n\n")
            
            # 风险提示
            f.write("## ⚠️ 风险提示\n\n")
            f.write("本报告基于技术分析生成，仅供参考，不构成投资建议。  \n")
            f.write("**投资有风险，决策需谨慎！**\n")
        
        return filepath


if __name__ == '__main__':
    # 测试代码
    test_results = [
        {
            'fund_code': '161725',
            'fund_name': '招商中证白酒',
            'analysis_date': '2024-10-30 10:00:00',
            'current_nav': 0.8234,
            'moving_averages': {
                'ma20': 0.8567,
                'ma60': 0.9123,
                'ma250': 1.0234,
                'ma500': 1.1456
            },
            'deviation': {
                'ma20': -3.89,
                'ma60': -9.74,
                'ma250': -19.55,
                'ma500': -28.12
            },
            'position_analysis': {
                'position': 'low',
                'signal': 'strong_buy',
                'strength': 4,
                'recommendation': '⭐⭐⭐ 强烈建议加仓',
                'details': [
                    '月线下方3.89% - 短期偏低',
                    '季线下方9.74% - 中期偏低',
                    '年线下方19.55% - 长期偏低',
                    '长期均线下方28.12% - 历史低位'
                ]
            },
            'investment_return': {
                'start_date': '2024-01-01',
                'start_nav': 1.1234,
                'current_nav': 0.8234,
                'return_rate': -26.70
            },
            'data_points': 250
        }
    ]
    
    generator = ReportGenerator()
    
    # 生成TXT报告
    txt_file = generator.generate_txt_report(test_results)
    print(f"✅ TXT报告已生成: {txt_file}")
    
    # 生成HTML报告
    html_file = generator.generate_html_report(test_results)
    print(f"✅ HTML报告已生成: {html_file}")
    
    # 生成Markdown报告
    md_file = generator.generate_markdown_report(test_results)
    print(f"✅ Markdown报告已生成: {md_file}")

