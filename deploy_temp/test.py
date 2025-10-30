# -*- coding: utf-8 -*-
"""
测试脚本
"""
from fund_data import FundDataFetcher
from fund_analyzer import FundAnalyzer
from message_sender import MessageSender

def test_fund_data():
    """测试基金数据获取"""
    print("=" * 60)
    print("测试基金数据获取")
    print("=" * 60)
    
    fetcher = FundDataFetcher()
    
    # 测试单个基金
    fund_code = "017811"
    print(f"\n获取基金 {fund_code} 的数据...")
    data = fetcher.get_fund_data(fund_code)
    print(data)
    
    # 测试历史数据
    print(f"\n获取基金 {fund_code} 的历史数据...")
    historical = fetcher.get_historical_data(fund_code, days=10)
    print(f"获取到 {len(historical)} 条历史记录")
    if historical:
        print("最新5条记录：")
        for record in historical[-5:]:
            print(record)

def test_analyzer():
    """测试分析器"""
    print("\n" + "=" * 60)
    print("测试基金分析器")
    print("=" * 60)
    
    analyzer = FundAnalyzer()
    fund_code = "017811"
    cost_basis = 1.0
    amount = 10000
    
    print(f"\n分析基金 {fund_code}...")
    analysis = analyzer.get_fund_analysis(
        fund_code=fund_code,
        cost_basis=cost_basis,
        amount=amount,
        lookback_days=30
    )
    
    if analysis:
        print("\n收益分析：")
        print(analysis["returns"])
        
        print("\n趋势分析：")
        print(analysis["trend"])
        
        print("\n价格预测：")
        if analysis["prediction"]:
            for pred in analysis["prediction"]:
                print(f"第{pred['day']}天: {pred['predicted_nav']:.4f} ({pred['predicted_change']:+.2f}%)")
        else:
            print("预测失败")
    else:
        print("分析失败")

def test_message():
    """测试消息发送"""
    print("\n" + "=" * 60)
    print("测试消息发送")
    print("=" * 60)
    
    # 模拟分析结果
    mock_results = [
        {
            "code": "017811",
            "name": "测试基金",
            "returns": {
                "return_rate": 5.25,
                "total_profit": 525.00,
                "today_change": 1.23,
                "today_profit": 123.45,
                "market_value": 10525.00,
                "shares": 10000.0,
                "cost_basis": 1.0,
                "current_nav": 1.0525
            },
            "trend": {
                "trend": "上涨趋势",
                "strength": 5.25,
                "volatility": 1.5
            },
            "prediction": [
                {"day": 1, "predicted_nav": 1.0550, "predicted_change": 0.24},
                {"day": 2, "predicted_nav": 1.0575, "predicted_change": 0.48}
            ]
        }
    ]
    
    # 格式化报告
    report = MessageSender.format_fund_report(mock_results)
    print("\n生成的报告：")
    print(report)
    
    # 测试发送（如果有配置）
    print("\n测试发送消息...")
    title = "测试报告"
    # MessageSender.send_all(title, report)

if __name__ == "__main__":
    print("\n基金管家系统 - 测试脚本\n")
    
    # 选择测试
    print("选择测试：")
    print("1. 测试数据获取")
    print("2. 测试分析器")
    print("3. 测试消息发送")
    print("4. 全部测试")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == "1":
        test_fund_data()
    elif choice == "2":
        test_analyzer()
    elif choice == "3":
        test_message()
    elif choice == "4":
        test_fund_data()
        test_analyzer()
        test_message()
    else:
        print("无效选项")
    
    print("\n测试完成！")
