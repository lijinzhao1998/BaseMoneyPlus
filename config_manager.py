#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基金配置管理工具
提供增加、删除、修改基金配置的功能
"""

import json
import os
from datetime import datetime


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_file='holdings_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            return {
                'holdings': {},
                'watchlist': {},
                'notes': '配置说明：\n1. holdings: 已投入的基金，会计算实际收益\n2. watchlist: 观察中的基金，通过均线分析判断买入时机'
            }
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return {
                'holdings': {},
                'watchlist': {},
                'notes': ''
            }
    
    def save_config(self):
        """保存配置文件"""
        try:
            # 备份原文件
            if os.path.exists(self.config_file):
                backup_file = f"{self.config_file}.backup"
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # 保存新配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 配置已保存到 {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")
            return False
    
    def add_holding(self, fund_code, name, cost_basis, amount, purchase_date, investment_start_date=None):
        """
        添加持仓基金
        
        Args:
            fund_code: 基金代码
            name: 基金名称
            cost_basis: 成本净值
            amount: 持有金额
            purchase_date: 购买日期
            investment_start_date: 投入日期（用于收益计算）
        """
        if fund_code in self.config['holdings']:
            print(f"⚠️ 基金 {fund_code} 已存在于持仓中")
            choice = input("是否覆盖？(y/n): ").strip().lower()
            if choice != 'y':
                return False
        
        self.config['holdings'][fund_code] = {
            'name': name,
            'cost_basis': float(cost_basis),
            'amount': float(amount),
            'purchase_date': purchase_date,
            'invested': True,
            'investment_start_date': investment_start_date or purchase_date
        }
        
        print(f"✅ 已添加持仓基金: {name} ({fund_code})")
        return self.save_config()
    
    def add_watchlist(self, fund_code, name, watch_start_date=None, note=''):
        """
        添加观察基金
        
        Args:
            fund_code: 基金代码
            name: 基金名称
            watch_start_date: 开始观察日期
            note: 备注
        """
        if fund_code in self.config['watchlist']:
            print(f"⚠️ 基金 {fund_code} 已存在于观察列表中")
            choice = input("是否覆盖？(y/n): ").strip().lower()
            if choice != 'y':
                return False
        
        if not watch_start_date:
            watch_start_date = datetime.now().strftime('%Y-%m-%d')
        
        self.config['watchlist'][fund_code] = {
            'name': name,
            'invested': False,
            'watch_start_date': watch_start_date,
            'note': note
        }
        
        print(f"✅ 已添加观察基金: {name} ({fund_code})")
        return self.save_config()
    
    def remove_fund(self, fund_code, fund_type='holding'):
        """
        删除基金
        
        Args:
            fund_code: 基金代码
            fund_type: 'holding' 或 'watchlist'
        """
        if fund_type == 'holding':
            if fund_code in self.config['holdings']:
                fund_name = self.config['holdings'][fund_code].get('name', fund_code)
                del self.config['holdings'][fund_code]
                print(f"✅ 已删除持仓基金: {fund_name} ({fund_code})")
                return self.save_config()
            else:
                print(f"❌ 持仓中未找到基金 {fund_code}")
                return False
        elif fund_type == 'watchlist':
            if fund_code in self.config['watchlist']:
                fund_name = self.config['watchlist'][fund_code].get('name', fund_code)
                del self.config['watchlist'][fund_code]
                print(f"✅ 已删除观察基金: {fund_name} ({fund_code})")
                return self.save_config()
            else:
                print(f"❌ 观察列表中未找到基金 {fund_code}")
                return False
        else:
            print(f"❌ 无效的基金类型: {fund_type}")
            return False
    
    def batch_delete_funds(self, fund_codes, fund_type='holding'):
        """
        批量删除基金
        
        Args:
            fund_codes: 基金代码列表
            fund_type: 'holding' 或 'watchlist' 或 'both'
        """
        deleted_count = 0
        failed_codes = []
        
        for fund_code in fund_codes:
            deleted = False
            
            if fund_type in ['holding', 'both']:
                if fund_code in self.config['holdings']:
                    name = self.config['holdings'][fund_code]['name']
                    del self.config['holdings'][fund_code]
                    print(f"✅ 已从持仓中删除: {name} ({fund_code})")
                    deleted = True
            
            if fund_type in ['watchlist', 'both']:
                if fund_code in self.config['watchlist']:
                    name = self.config['watchlist'][fund_code]['name']
                    del self.config['watchlist'][fund_code]
                    print(f"✅ 已从观察列表中删除: {name} ({fund_code})")
                    deleted = True
            
            if deleted:
                deleted_count += 1
            else:
                failed_codes.append(fund_code)
        
        if deleted_count > 0:
            self.save_config()
            print(f"\n✅ 成功删除 {deleted_count} 个基金")
        
        if failed_codes:
            print(f"❌ 以下基金代码未找到: {', '.join(failed_codes)}")
        
        return deleted_count > 0
    
    def batch_add_holdings(self, holdings_list):
        """
        批量添加持仓基金
        
        Args:
            holdings_list: 持仓列表，每项包含 (fund_code, name, cost_basis, amount, purchase_date, investment_start_date)
        """
        added_count = 0
        failed_items = []
        
        for item in holdings_list:
            try:
                fund_code, name, cost_basis, amount, purchase_date, investment_start_date = item
                
                self.config['holdings'][fund_code] = {
                    'name': name,
                    'cost_basis': float(cost_basis),
                    'amount': float(amount),
                    'purchase_date': purchase_date,
                    'invested': True,
                    'investment_start_date': investment_start_date or purchase_date
                }
                
                print(f"✅ 已添加持仓基金: {name} ({fund_code})")
                added_count += 1
            except Exception as e:
                failed_items.append((fund_code if 'fund_code' in locals() else 'Unknown', str(e)))
        
        if added_count > 0:
            self.save_config()
            print(f"\n✅ 成功添加 {added_count} 个持仓基金")
        
        if failed_items:
            print(f"\n❌ 以下基金添加失败:")
            for code, error in failed_items:
                print(f"   {code}: {error}")
        
        return added_count > 0
    
    def batch_add_watchlist(self, watchlist_items):
        """
        批量添加观察基金
        
        Args:
            watchlist_items: 观察列表，每项包含 (fund_code, name, watch_start_date, note)
        """
        added_count = 0
        failed_items = []
        
        for item in watchlist_items:
            try:
                fund_code, name, watch_start_date, note = item
                
                self.config['watchlist'][fund_code] = {
                    'name': name,
                    'invested': False,
                    'watch_start_date': watch_start_date or datetime.now().strftime('%Y-%m-%d'),
                    'note': note or ''
                }
                
                print(f"✅ 已添加观察基金: {name} ({fund_code})")
                added_count += 1
            except Exception as e:
                failed_items.append((fund_code if 'fund_code' in locals() else 'Unknown', str(e)))
        
        if added_count > 0:
            self.save_config()
            print(f"\n✅ 成功添加 {added_count} 个观察基金")
        
        if failed_items:
            print(f"\n❌ 以下基金添加失败:")
            for code, error in failed_items:
                print(f"   {code}: {error}")
        
        return added_count > 0
    
    def clear_holdings(self):
        """清除所有持仓基金"""
        count = len(self.config['holdings'])
        if count == 0:
            print("⚠️ 持仓列表已经是空的")
            return False
        
        print(f"⚠️ 即将清除 {count} 个持仓基金:")
        for code, info in self.config['holdings'].items():
            print(f"   - {info['name']} ({code})")
        
        confirm = input("\n确认清除所有持仓？此操作不可恢复！(输入 YES 确认): ").strip()
        if confirm != 'YES':
            print("❌ 操作已取消")
            return False
        
        self.config['holdings'] = {}
        self.save_config()
        print(f"✅ 已清除 {count} 个持仓基金")
        return True
    
    def clear_watchlist(self):
        """清除所有观察基金"""
        count = len(self.config['watchlist'])
        if count == 0:
            print("⚠️ 观察列表已经是空的")
            return False
        
        print(f"⚠️ 即将清除 {count} 个观察基金:")
        for code, info in self.config['watchlist'].items():
            print(f"   - {info['name']} ({code})")
        
        confirm = input("\n确认清除所有观察基金？此操作不可恢复！(输入 YES 确认): ").strip()
        if confirm != 'YES':
            print("❌ 操作已取消")
            return False
        
        self.config['watchlist'] = {}
        self.save_config()
        print(f"✅ 已清除 {count} 个观察基金")
        return True
    
    def clear_all(self):
        """清除所有配置数据"""
        holdings_count = len(self.config['holdings'])
        watchlist_count = len(self.config['watchlist'])
        total = holdings_count + watchlist_count
        
        if total == 0:
            print("⚠️ 配置已经是空的")
            return False
        
        print(f"⚠️ 即将清除所有配置数据:")
        print(f"   - 持仓基金: {holdings_count} 个")
        print(f"   - 观察基金: {watchlist_count} 个")
        print(f"   - 总计: {total} 个")
        
        confirm = input("\n确认清除所有配置？此操作不可恢复！(输入 YES 确认): ").strip()
        if confirm != 'YES':
            print("❌ 操作已取消")
            return False
        
        self.config['holdings'] = {}
        self.config['watchlist'] = {}
        self.save_config()
        print(f"✅ 已清除所有配置数据 (共 {total} 个基金)")
        return True
    
    def update_holding(self, fund_code, **kwargs):
        """
        更新持仓基金信息
        
        Args:
            fund_code: 基金代码
            **kwargs: 要更新的字段
        """
        if fund_code not in self.config['holdings']:
            print(f"❌ 持仓中未找到基金 {fund_code}")
            return False
        
        allowed_fields = ['name', 'cost_basis', 'amount', 'purchase_date', 'investment_start_date']
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                if key in ['cost_basis', 'amount'] and value is not None:
                    self.config['holdings'][fund_code][key] = float(value)
                elif value is not None:
                    self.config['holdings'][fund_code][key] = value
        
        print(f"✅ 已更新持仓基金: {self.config['holdings'][fund_code]['name']} ({fund_code})")
        return self.save_config()
    
    def update_watchlist(self, fund_code, **kwargs):
        """
        更新观察基金信息
        
        Args:
            fund_code: 基金代码
            **kwargs: 要更新的字段
        """
        if fund_code not in self.config['watchlist']:
            print(f"❌ 观察列表中未找到基金 {fund_code}")
            return False
        
        allowed_fields = ['name', 'watch_start_date', 'note']
        
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                self.config['watchlist'][fund_code][key] = value
        
        print(f"✅ 已更新观察基金: {self.config['watchlist'][fund_code]['name']} ({fund_code})")
        return self.save_config()
    
    def move_to_holding(self, fund_code, cost_basis, amount, purchase_date):
        """
        将观察基金转为持仓基金
        
        Args:
            fund_code: 基金代码
            cost_basis: 成本净值
            amount: 持有金额
            purchase_date: 购买日期
        """
        if fund_code not in self.config['watchlist']:
            print(f"❌ 观察列表中未找到基金 {fund_code}")
            return False
        
        watch_info = self.config['watchlist'][fund_code]
        
        # 添加到持仓
        self.config['holdings'][fund_code] = {
            'name': watch_info['name'],
            'cost_basis': float(cost_basis),
            'amount': float(amount),
            'purchase_date': purchase_date,
            'invested': True,
            'investment_start_date': purchase_date
        }
        
        # 从观察列表删除
        del self.config['watchlist'][fund_code]
        
        print(f"✅ 已将 {watch_info['name']} ({fund_code}) 从观察列表转为持仓")
        return self.save_config()
    
    def move_to_watchlist(self, fund_code, note=''):
        """
        将持仓基金转为观察基金
        
        Args:
            fund_code: 基金代码
            note: 备注
        """
        if fund_code not in self.config['holdings']:
            print(f"❌ 持仓中未找到基金 {fund_code}")
            return False
        
        holding_info = self.config['holdings'][fund_code]
        
        # 添加到观察列表
        self.config['watchlist'][fund_code] = {
            'name': holding_info['name'],
            'invested': False,
            'watch_start_date': datetime.now().strftime('%Y-%m-%d'),
            'note': note or f"原持仓基金，成本{holding_info['cost_basis']}"
        }
        
        # 从持仓删除
        del self.config['holdings'][fund_code]
        
        print(f"✅ 已将 {holding_info['name']} ({fund_code}) 从持仓转为观察列表")
        return self.save_config()
    
    def list_all(self):
        """列出所有基金"""
        print("\n" + "="*60)
        print("📊 持仓基金")
        print("="*60)
        
        if not self.config['holdings']:
            print("  （暂无持仓）")
        else:
            for code, info in self.config['holdings'].items():
                print(f"\n  基金代码: {code}")
                print(f"  基金名称: {info.get('name', '未知')}")
                print(f"  成本净值: {info.get('cost_basis', 'N/A')}")
                print(f"  持有金额: {info.get('amount', 'N/A')}")
                print(f"  购买日期: {info.get('purchase_date', 'N/A')}")
                print(f"  投入日期: {info.get('investment_start_date', 'N/A')}")
        
        print("\n" + "="*60)
        print("👀 观察基金")
        print("="*60)
        
        if not self.config['watchlist']:
            print("  （暂无观察）")
        else:
            for code, info in self.config['watchlist'].items():
                print(f"\n  基金代码: {code}")
                print(f"  基金名称: {info.get('name', '未知')}")
                print(f"  观察日期: {info.get('watch_start_date', 'N/A')}")
                print(f"  备注: {info.get('note', '无')}")
        
        print("\n" + "="*60 + "\n")


def interactive_menu():
    """交互式菜单"""
    manager = ConfigManager()
    
    while True:
        print("\n" + "="*60)
        print("📝 基金配置管理工具 v2.2")
        print("="*60)
        print("\n【基本操作】")
        print("1. 查看所有基金")
        print("2. 添加持仓基金")
        print("3. 添加观察基金")
        print("4. 删除基金")
        print("5. 更新基金信息")
        print("6. 观察基金转持仓")
        print("7. 持仓基金转观察")
        print("\n【批量操作】")
        print("8. 批量删除基金")
        print("9. 批量添加持仓基金")
        print("10. 批量添加观察基金")
        print("\n【清除操作】")
        print("11. 清除所有持仓")
        print("12. 清除所有观察")
        print("13. 清除所有配置 ⚠️")
        print("\n0. 退出")
        
        choice = input("\n请选择操作 (0-13): ").strip()
        
        if choice == '0':
            print("退出程序")
            break
        
        elif choice == '1':
            manager.list_all()
        
        elif choice == '2':
            print("\n--- 添加持仓基金 ---")
            fund_code = input("基金代码: ").strip()
            if not fund_code:
                print("❌ 基金代码不能为空")
                continue
            
            name = input("基金名称: ").strip()
            if not name:
                print("❌ 基金名称不能为空")
                continue
            
            try:
                cost_basis = float(input("成本净值: ").strip())
                amount = float(input("持有金额: ").strip())
                purchase_date = input("购买日期 (YYYY-MM-DD): ").strip()
                investment_start_date = input("投入日期 (YYYY-MM-DD，可选，直接回车使用购买日期): ").strip()
                
                manager.add_holding(
                    fund_code, name, cost_basis, amount, 
                    purchase_date, investment_start_date or None
                )
            except ValueError as e:
                print(f"❌ 输入格式错误: {e}")
        
        elif choice == '3':
            print("\n--- 添加观察基金 ---")
            fund_code = input("基金代码: ").strip()
            if not fund_code:
                print("❌ 基金代码不能为空")
                continue
            
            name = input("基金名称: ").strip()
            if not name:
                print("❌ 基金名称不能为空")
                continue
            
            watch_start_date = input("开始观察日期 (YYYY-MM-DD，可选): ").strip()
            note = input("备注 (可选): ").strip()
            
            manager.add_watchlist(fund_code, name, watch_start_date or None, note)
        
        elif choice == '4':
            print("\n--- 删除基金 ---")
            fund_code = input("基金代码: ").strip()
            if not fund_code:
                print("❌ 基金代码不能为空")
                continue
            
            print("从哪里删除？")
            print("1. 持仓")
            print("2. 观察列表")
            type_choice = input("选择 (1-2): ").strip()
            
            if type_choice == '1':
                manager.remove_fund(fund_code, 'holding')
            elif type_choice == '2':
                manager.remove_fund(fund_code, 'watchlist')
            else:
                print("❌ 无效选项")
        
        elif choice == '5':
            print("\n--- 更新基金信息 ---")
            fund_code = input("基金代码: ").strip()
            if not fund_code:
                print("❌ 基金代码不能为空")
                continue
            
            print("更新哪种类型的基金？")
            print("1. 持仓")
            print("2. 观察列表")
            type_choice = input("选择 (1-2): ").strip()
            
            if type_choice == '1':
                if fund_code not in manager.config['holdings']:
                    print(f"❌ 持仓中未找到基金 {fund_code}")
                    continue
                
                print("\n留空表示不修改该字段")
                name = input("基金名称: ").strip()
                cost_basis = input("成本净值: ").strip()
                amount = input("持有金额: ").strip()
                purchase_date = input("购买日期 (YYYY-MM-DD): ").strip()
                investment_start_date = input("投入日期 (YYYY-MM-DD): ").strip()
                
                kwargs = {}
                if name: kwargs['name'] = name
                if cost_basis: kwargs['cost_basis'] = float(cost_basis)
                if amount: kwargs['amount'] = float(amount)
                if purchase_date: kwargs['purchase_date'] = purchase_date
                if investment_start_date: kwargs['investment_start_date'] = investment_start_date
                
                if kwargs:
                    manager.update_holding(fund_code, **kwargs)
                else:
                    print("⚠️ 未修改任何字段")
            
            elif type_choice == '2':
                if fund_code not in manager.config['watchlist']:
                    print(f"❌ 观察列表中未找到基金 {fund_code}")
                    continue
                
                print("\n留空表示不修改该字段")
                name = input("基金名称: ").strip()
                watch_start_date = input("开始观察日期 (YYYY-MM-DD): ").strip()
                note = input("备注: ").strip()
                
                kwargs = {}
                if name: kwargs['name'] = name
                if watch_start_date: kwargs['watch_start_date'] = watch_start_date
                if note: kwargs['note'] = note
                
                if kwargs:
                    manager.update_watchlist(fund_code, **kwargs)
                else:
                    print("⚠️ 未修改任何字段")
            else:
                print("❌ 无效选项")
        
        elif choice == '6':
            print("\n--- 观察基金转持仓 ---")
            fund_code = input("基金代码: ").strip()
            if not fund_code:
                print("❌ 基金代码不能为空")
                continue
            
            try:
                cost_basis = float(input("成本净值: ").strip())
                amount = float(input("持有金额: ").strip())
                purchase_date = input("购买日期 (YYYY-MM-DD): ").strip()
                
                manager.move_to_holding(fund_code, cost_basis, amount, purchase_date)
            except ValueError as e:
                print(f"❌ 输入格式错误: {e}")
        
        elif choice == '7':
            print("\n--- 持仓基金转观察 ---")
            fund_code = input("基金代码: ").strip()
            if not fund_code:
                print("❌ 基金代码不能为空")
                continue
            
            note = input("备注 (可选): ").strip()
            manager.move_to_watchlist(fund_code, note)
        
        elif choice == '8':
            print("\n--- 批量删除基金 ---")
            print("输入基金代码，用逗号分隔 (如: 161725,161726,000001)")
            codes_input = input("基金代码: ").strip()
            if not codes_input:
                print("❌ 基金代码不能为空")
                continue
            
            fund_codes = [code.strip() for code in codes_input.split(',')]
            
            print("\n删除范围：")
            print("1. 仅持仓")
            print("2. 仅观察列表")
            print("3. 持仓和观察列表都删")
            type_choice = input("选择 (1-3): ").strip()
            
            if type_choice == '1':
                manager.batch_delete_funds(fund_codes, 'holding')
            elif type_choice == '2':
                manager.batch_delete_funds(fund_codes, 'watchlist')
            elif type_choice == '3':
                manager.batch_delete_funds(fund_codes, 'both')
            else:
                print("❌ 无效选项")
        
        elif choice == '9':
            print("\n--- 批量添加持仓基金 ---")
            print("每行一个基金，格式: 代码,名称,成本净值,金额,购买日期,投入日期")
            print("示例: 161725,招商白酒,1.0,10000,2024-01-01,2024-01-01")
            print("输入完成后，单独一行输入 END")
            
            holdings_list = []
            while True:
                line = input().strip()
                if line.upper() == 'END':
                    break
                if not line:
                    continue
                
                try:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) == 5:
                        parts.append(parts[4])  # 投入日期默认使用购买日期
                    elif len(parts) != 6:
                        print(f"❌ 格式错误，跳过: {line}")
                        continue
                    
                    holdings_list.append(tuple(parts))
                except Exception as e:
                    print(f"❌ 解析失败，跳过: {line} ({e})")
            
            if holdings_list:
                manager.batch_add_holdings(holdings_list)
            else:
                print("❌ 没有有效的数据")
        
        elif choice == '10':
            print("\n--- 批量添加观察基金 ---")
            print("每行一个基金，格式: 代码,名称,观察日期,备注")
            print("示例: 161726,招商食品,2024-01-01,等待回调")
            print("输入完成后，单独一行输入 END")
            
            watchlist_items = []
            while True:
                line = input().strip()
                if line.upper() == 'END':
                    break
                if not line:
                    continue
                
                try:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) == 2:
                        parts.extend(['', ''])  # 添加默认日期和备注
                    elif len(parts) == 3:
                        parts.append('')  # 添加默认备注
                    elif len(parts) != 4:
                        print(f"❌ 格式错误，跳过: {line}")
                        continue
                    
                    watchlist_items.append(tuple(parts))
                except Exception as e:
                    print(f"❌ 解析失败，跳过: {line} ({e})")
            
            if watchlist_items:
                manager.batch_add_watchlist(watchlist_items)
            else:
                print("❌ 没有有效的数据")
        
        elif choice == '11':
            print("\n--- 清除所有持仓 ---")
            manager.clear_holdings()
        
        elif choice == '12':
            print("\n--- 清除所有观察 ---")
            manager.clear_watchlist()
        
        elif choice == '13':
            print("\n--- 清除所有配置 ⚠️ ---")
            manager.clear_all()
        
        else:
            print("❌ 无效选项")


if __name__ == '__main__':
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n程序已中断")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()

