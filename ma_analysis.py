#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基金均线分析独立运行脚本
可以单独运行此脚本来分析基金的均线情况
"""

import json
import os
import sys
from moving_average_analyzer import MovingAverageAnalyzer
from report_generator import ReportGenerator


def load_config():
    """加载配置文件"""
    if not os.path.exists('holdings_config.json'):
        print("❌ 未找到 holdings_config.json 配置文件")
        print("请先配置基金信息")
        return None, None
    
    try:
        with open('holdings_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('holdings', {}), config.get('watchlist', {})
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return None, None


def analyze_single_fund(analyzer, fund_code, fund_name, start_date=None):
    """分析单只基金"""
    print(f"\n{'='*60}")
    print(f"分析基金: {fund_name} ({fund_code})")
    print(f"{'='*60}")
    
    analysis = analyzer.analyze_fund(fund_code, fund_name, start_date)
    report = analyzer.format_analysis_report(analysis)
    print(report)
    
    return analysis


def main():
    """主函数"""
    print("="*60)
    print("基金均线分析工具")
    print("="*60)
    
    analyzer = MovingAverageAnalyzer()
    
    print("\n选择分析模式：")
    print("1. 分析配置文件中的所有基金")
    print("2. 分析单只基金（手动输入代码）")
    print("3. 退出")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        # 分析配置文件中的基金
        holdings, watchlist = load_config()
        
        if holdings is None:
            return
        
        all_results = []
        
        # 分析持仓基金
        if holdings:
            print(f"\n{'='*60}")
            print("📈 持仓基金分析")
            print(f"{'='*60}")
            
            for code, info in holdings.items():
                try:
                    analysis = analyze_single_fund(
                        analyzer,
                        code,
                        info.get('name', f'基金{code}'),
                        info.get('investment_start_date')
                    )
                    all_results.append(analysis)
                except Exception as e:
                    print(f"❌ 分析失败: {e}")
                
                import time
                time.sleep(1)  # 避免请求过快
        
        # 分析观察基金
        if watchlist:
            print(f"\n{'='*60}")
            print("👀 观察基金分析")
            print(f"{'='*60}")
            
            for code, info in watchlist.items():
                try:
                    analysis = analyze_single_fund(
                        analyzer,
                        code,
                        info.get('name', f'基金{code}'),
                        info.get('watch_start_date')
                    )
                    all_results.append(analysis)
                except Exception as e:
                    print(f"❌ 分析失败: {e}")
                
                import time
                time.sleep(1)  # 避免请求过快
        
        # 汇总建议
        print(f"\n{'='*60}")
        print("📊 操作建议汇总")
        print(f"{'='*60}\n")
        
        strong_buy = []
        buy = []
        hold = []
        sell = []
        strong_sell = []
        
        for result in all_results:
            if 'error' in result:
                continue
            
            pos = result.get('position_analysis', {})
            signal = pos.get('signal', 'hold')
            fund_info = f"{result['fund_name']} ({result['fund_code']})"
            
            if signal == 'strong_buy':
                strong_buy.append(fund_info)
            elif signal == 'buy':
                buy.append(fund_info)
            elif signal == 'strong_sell':
                strong_sell.append(fund_info)
            elif signal == 'sell':
                sell.append(fund_info)
            else:
                hold.append(fund_info)
        
        if strong_buy:
            print("⭐⭐⭐ 强烈建议加仓:")
            for fund in strong_buy:
                print(f"  • {fund}")
            print()
        
        if buy:
            print("⭐⭐ 可以适当加仓:")
            for fund in buy:
                print(f"  • {fund}")
            print()
        
        if sell:
            print("⚠️⚠️ 可以适当减仓:")
            for fund in sell:
                print(f"  • {fund}")
            print()
        
        if strong_sell:
            print("⚠️⚠️⚠️ 建议减仓:")
            for fund in strong_sell:
                print(f"  • {fund}")
            print()
        
        if hold:
            print("⭐ 持有观望:")
            for fund in hold:
                print(f"  • {fund}")
            print()
        
        # 保存完整报告
        print("\n是否保存分析报告到文件?")
        print("1. TXT格式 (文本文件)")
        print("2. HTML格式 (网页文件，推荐)")
        print("3. Markdown格式 (适合GitHub)")
        print("4. JSON格式 (原始数据)")
        print("5. 全部格式")
        print("0. 不保存")
        
        save_choice = input("\n请选择 (0-5): ").strip()
        
        if save_choice != '0':
            generator = ReportGenerator()
            saved_files = []
            
            if save_choice == '1' or save_choice == '5':
                txt_file = generator.generate_txt_report(all_results)
                saved_files.append(txt_file)
                print(f"✅ TXT报告已保存: {txt_file}")
            
            if save_choice == '2' or save_choice == '5':
                html_file = generator.generate_html_report(all_results)
                saved_files.append(html_file)
                print(f"✅ HTML报告已保存: {html_file}")
            
            if save_choice == '3' or save_choice == '5':
                md_file = generator.generate_markdown_report(all_results)
                saved_files.append(md_file)
                print(f"✅ Markdown报告已保存: {md_file}")
            
            if save_choice == '4' or save_choice == '5':
                from datetime import datetime
                filename = f"reports/ma_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                os.makedirs('reports', exist_ok=True)
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(all_results, f, ensure_ascii=False, indent=2)
                saved_files.append(filename)
                print(f"✅ JSON报告已保存: {filename}")
            
            if saved_files:
                print(f"\n✅ 共保存 {len(saved_files)} 个报告文件")
                print(f"📁 报告目录: {os.path.abspath('reports')}")
    
    elif choice == "2":
        # 手动输入基金代码分析
        fund_code = input("\n请输入基金代码: ").strip()
        if not fund_code:
            print("❌ 基金代码不能为空")
            return
        
        fund_name = input("请输入基金名称（可选，直接回车跳过）: ").strip()
        if not fund_name:
            fund_name = f"基金{fund_code}"
        
        start_date = input("请输入投入日期（格式：YYYY-MM-DD，可选）: ").strip()
        if not start_date:
            start_date = None
        
        try:
            analysis = analyze_single_fund(analyzer, fund_code, fund_name, start_date)
            
            # 保存结果
            print("\n是否保存分析报告到文件?")
            print("1. TXT格式")
            print("2. HTML格式 (推荐)")
            print("3. Markdown格式")
            print("4. JSON格式")
            print("5. 全部格式")
            print("0. 不保存")
            
            save_choice = input("\n请选择 (0-5): ").strip()
            
            if save_choice != '0':
                generator = ReportGenerator()
                saved_files = []
                
                if save_choice == '1' or save_choice == '5':
                    txt_file = generator.generate_txt_report([analysis], f"{fund_code}_analysis.txt")
                    saved_files.append(txt_file)
                    print(f"✅ TXT报告已保存: {txt_file}")
                
                if save_choice == '2' or save_choice == '5':
                    html_file = generator.generate_html_report([analysis], f"{fund_code}_analysis.html")
                    saved_files.append(html_file)
                    print(f"✅ HTML报告已保存: {html_file}")
                
                if save_choice == '3' or save_choice == '5':
                    md_file = generator.generate_markdown_report([analysis], f"{fund_code}_analysis.md")
                    saved_files.append(md_file)
                    print(f"✅ Markdown报告已保存: {md_file}")
                
                if save_choice == '4' or save_choice == '5':
                    filename = f"reports/{fund_code}_analysis.json"
                    os.makedirs('reports', exist_ok=True)
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(analysis, f, ensure_ascii=False, indent=2)
                    saved_files.append(filename)
                    print(f"✅ JSON报告已保存: {filename}")
                
                if saved_files:
                    print(f"\n✅ 共保存 {len(saved_files)} 个报告文件")
                    print(f"📁 报告目录: {os.path.abspath('reports')}")
        
        except Exception as e:
            print(f"❌ 分析失败: {e}")
    
    elif choice == "3":
        print("退出程序")
    else:
        print("❌ 无效选项")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已中断")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()

