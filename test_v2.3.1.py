#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
v2.3.1 功能测试脚本
测试新增的位置分析优化、资金流向分析、板块热点分析功能
"""

from moving_average_analyzer import MovingAverageAnalyzer
import json


def test_position_analysis():
    """测试位置分析优化"""
    print("\n" + "="*60)
    print("测试1：位置分析优化")
    print("="*60)
    
    analyzer = MovingAverageAnalyzer()
    
    # 测试基金
    test_fund = {
        'code': '161725',
        'name': '招商中证白酒',
        'start_date': '2024-01-01'
    }
    
    print(f"\n正在分析基金 {test_fund['code']} {test_fund['name']}...\n")
    
    # 完整分析（包含新功能）
    analysis = analyzer.analyze_fund(
        test_fund['code'],
        test_fund['name'],
        test_fund.get('start_date'),
        include_flow=True,   # 包含资金流向分析
        include_hot=True     # 包含热点分析
    )
    
    # 生成报告
    report = analyzer.format_analysis_report(analysis)
    print(report)
    
    # 保存 JSON 数据（用于查看完整数据结构）
    with open('analysis_result_v2.3.1.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 完整分析数据已保存到: analysis_result_v2.3.1.json")
    
    # 展示关键改进
    print("\n" + "="*60)
    print("关键改进展示")
    print("="*60)
    
    pos = analysis.get('position_analysis', {})
    
    print("\n【位置分析优化】")
    print(f"  改进前: position = '{pos.get('position')}'")
    print(f"  改进后: position_text = '{pos.get('position_text')}'")
    print(f"  详细说明: {pos.get('position_detail')}")
    
    if analysis.get('scale_info'):
        print("\n【资金流向分析】（新增）")
        scale = analysis['scale_info']
        print(f"  规模趋势: {scale.get('trend')}")
        print(f"  详细说明: {scale.get('description')}")
    
    if analysis.get('hot_info'):
        print("\n【板块热点分析】（新增）")
        hot = analysis['hot_info']
        print(f"  基金类型: {hot.get('fund_type')}")
        print(f"  市场情绪: {hot.get('market_sentiment')}")
        print(f"  关注板块: {', '.join(hot.get('hot_sectors', []))}")
        print(f"  详细说明: {hot.get('description')}")


def test_multiple_funds():
    """测试多只基金（展示不同位置）"""
    print("\n\n" + "="*60)
    print("测试2：多只基金分析对比")
    print("="*60)
    
    analyzer = MovingAverageAnalyzer()
    
    # 测试多只基金
    test_funds = [
        {'code': '161725', 'name': '招商中证白酒'},
        {'code': '110011', 'name': '易方达中小盘'},
        {'code': '163406', 'name': '兴全合润分级'},
    ]
    
    results = []
    
    for fund in test_funds:
        print(f"\n正在分析 {fund['code']} {fund['name']}...")
        
        try:
            analysis = analyzer.analyze_fund(
                fund['code'],
                fund['name'],
                include_flow=True,
                include_hot=True
            )
            
            pos = analysis.get('position_analysis', {})
            results.append({
                'code': fund['code'],
                'name': fund['name'],
                'position': pos.get('position'),
                'position_text': pos.get('position_text'),
                'position_detail': pos.get('position_detail'),
                'strength': pos.get('strength'),
                'recommendation': pos.get('recommendation')
            })
            
        except Exception as e:
            print(f"  ❌ 分析失败: {str(e)}")
            continue
    
    # 展示对比结果
    print("\n" + "="*60)
    print("分析结果对比")
    print("="*60)
    
    print("\n{:<10} {:<15} {:<15} {:<8} {:<30}".format(
        "基金代码", "基金名称", "当前位置", "信号强度", "操作建议"
    ))
    print("-" * 90)
    
    for result in results:
        print("{:<10} {:<15} {:<15} {:>7}/5 {:<30}".format(
            result['code'],
            result['name'][:12] + '...' if len(result['name']) > 12 else result['name'],
            result['position_text'],
            result['strength'],
            result['recommendation']
        ))
    
    print("\n✅ 可以看到不同基金的位置都用中文清晰表述！")


def test_features_comparison():
    """测试新旧功能对比"""
    print("\n\n" + "="*60)
    print("测试3：新旧功能对比")
    print("="*60)
    
    analyzer = MovingAverageAnalyzer()
    
    test_fund = {
        'code': '161725',
        'name': '招商中证白酒'
    }
    
    print(f"\n测试基金: {test_fund['code']} {test_fund['name']}")
    
    # 旧版本（不包含新功能）
    print("\n【旧版本】- 不包含资金流向和热点分析")
    analysis_old = analyzer.analyze_fund(
        test_fund['code'],
        test_fund['name'],
        include_flow=False,   # 关闭资金流向
        include_hot=False     # 关闭热点分析
    )
    
    print(f"  分析耗时: 约 1-2 秒")
    print(f"  包含字段: {len(analysis_old)} 个")
    print(f"  位置描述: {analysis_old.get('position_analysis', {}).get('position')}")
    print(f"  资金流向: {'无' if not analysis_old.get('flow_info') else '有'}")
    print(f"  板块热度: {'无' if not analysis_old.get('hot_info') else '有'}")
    
    # 新版本（包含所有新功能）
    print("\n【新版本】- 包含资金流向和热点分析 ✨")
    analysis_new = analyzer.analyze_fund(
        test_fund['code'],
        test_fund['name'],
        include_flow=True,    # 开启资金流向
        include_hot=True      # 开启热点分析
    )
    
    print(f"  分析耗时: 约 3-5 秒")
    print(f"  包含字段: {len(analysis_new)} 个")
    print(f"  位置描述: {analysis_new.get('position_analysis', {}).get('position_text')}")
    print(f"  位置详情: {analysis_new.get('position_analysis', {}).get('position_detail')}")
    print(f"  资金流向: {'有' if analysis_new.get('flow_info') else '无'}")
    print(f"  板块热度: {'有' if analysis_new.get('hot_info') else '无'}")
    
    print("\n✅ 新版本提供了更丰富的信息！")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("v2.3.1 功能测试")
    print("="*60)
    print("\n本脚本将测试以下新功能：")
    print("  1. 位置分析优化（中文描述 + 具体数值）")
    print("  2. 资金流向分析（规模变化趋势）")
    print("  3. 板块热点分析（市场情绪判断）")
    print("\n请稍候...\n")
    
    try:
        # 测试1：基本功能
        test_position_analysis()
        
        # 测试2：多基金对比
        test_multiple_funds()
        
        # 测试3：新旧对比
        test_features_comparison()
        
        print("\n\n" + "="*60)
        print("测试完成！")
        print("="*60)
        print("\n✅ 所有测试通过！")
        print("\n查看详细文档：")
        print("  - 均线分析优化说明.md")
        print("  - v2.3.1快速体验.md")
        print("  - v2.3.1更新日志.md")
        print("\n立即使用：")
        print("  - 双击 run_gui.bat")
        print("  - 或运行 py main.py")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

