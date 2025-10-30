#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基金管理系统 - 图形化界面
集成配置管理和均线分析功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import os
import sys
import threading
import time
from datetime import datetime
from config_manager import ConfigManager
from report_generator import ReportGenerator
from fund_analyzer import FundAnalyzer
from message_sender import MessageSender
from moving_average_analyzer import MovingAverageAnalyzer
import subprocess


class FundManagerGUI:
    """基金管理系统图形化界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("基金管理系统 v2.3")
        self.root.geometry("1200x800")
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 初始化分析器
        self.fund_analyzer = FundAnalyzer()
        self.message_sender = MessageSender()
        self.ma_analyzer = MovingAverageAnalyzer()
        
        # 设置主题
        self.setup_style()
        
        # 创建界面
        self.create_widgets()
        
        # 加载数据
        self.refresh_data()
    
    def setup_style(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置颜色
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('Primary.TButton', foreground='white', background='#3498db')
        style.configure('Success.TButton', foreground='white', background='#27ae60')
        style.configure('Danger.TButton', foreground='white', background='#e74c3c')
        style.configure('Warning.TButton', foreground='white', background='#f39c12')
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置grid权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="📊 基金管理系统", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # 左侧：功能按钮区
        self.create_button_panel(main_frame)
        
        # 右侧：数据显示区
        self.create_data_panel(main_frame)
    
    def create_button_panel(self, parent):
        """创建功能按钮面板"""
        button_frame = ttk.LabelFrame(parent, text="功能菜单", padding="10")
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # 配置管理
        config_label = ttk.Label(button_frame, text="【配置管理】", style='Subtitle.TLabel')
        config_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        ttk.Button(button_frame, text="➕ 添加持仓基金", 
                  command=self.add_holding_dialog, width=20).grid(row=1, column=0, pady=2, sticky=tk.W+tk.E)
        
        ttk.Button(button_frame, text="👀 添加观察基金", 
                  command=self.add_watchlist_dialog, width=20).grid(row=2, column=0, pady=2, sticky=tk.W+tk.E)
        
        ttk.Button(button_frame, text="✏️ 更新基金信息", 
                  command=self.update_fund_dialog, width=20).grid(row=3, column=0, pady=2, sticky=tk.W+tk.E)
        
        ttk.Button(button_frame, text="🗑️ 删除基金", 
                  command=self.delete_fund_dialog, width=20).grid(row=4, column=0, pady=2, sticky=tk.W+tk.E)
        
        ttk.Button(button_frame, text="🔄 观察→持仓", 
                  command=self.move_to_holding_dialog, width=20).grid(row=5, column=0, pady=2, sticky=tk.W+tk.E)
        
        ttk.Button(button_frame, text="🔄 持仓→观察", 
                  command=self.move_to_watchlist_dialog, width=20).grid(row=6, column=0, pady=2, sticky=tk.W+tk.E)
        
        # 批量操作
        ttk.Separator(button_frame, orient='horizontal').grid(row=7, column=0, sticky=tk.W+tk.E, pady=10)
        
        batch_label = ttk.Label(button_frame, text="【批量操作】", style='Subtitle.TLabel')
        batch_label.grid(row=8, column=0, sticky=tk.W, pady=(0, 5))
        
        ttk.Button(button_frame, text="📦 批量添加持仓", 
                  command=self.batch_add_holdings_dialog, width=20).grid(row=9, column=0, pady=2, sticky=tk.W+tk.E)
        
        ttk.Button(button_frame, text="📦 批量添加观察", 
                  command=self.batch_add_watchlist_dialog, width=20).grid(row=10, column=0, pady=2, sticky=tk.W+tk.E)
        
        ttk.Button(button_frame, text="🗑️ 批量删除基金", 
                  command=self.batch_delete_dialog, width=20).grid(row=11, column=0, pady=2, sticky=tk.W+tk.E)
        
        # 分析与报告
        ttk.Separator(button_frame, orient='horizontal').grid(row=12, column=0, sticky=tk.W+tk.E, pady=10)
        
        analysis_label = ttk.Label(button_frame, text="【分析与报告】", style='Subtitle.TLabel')
        analysis_label.grid(row=13, column=0, sticky=tk.W, pady=(0, 5))
        
        ttk.Button(button_frame, text="📊 完整分析报告", 
                  command=self.run_full_analysis, width=20, style='Primary.TButton').grid(row=14, column=0, pady=2, sticky=tk.W+tk.E)
        
        ttk.Button(button_frame, text="📈 运行均线分析", 
                  command=self.run_ma_analysis, width=20, style='Primary.TButton').grid(row=15, column=0, pady=2, sticky=tk.W+tk.E)
        
        ttk.Button(button_frame, text="📊 导出报告", 
                  command=self.export_report_dialog, width=20, style='Success.TButton').grid(row=16, column=0, pady=2, sticky=tk.W+tk.E)
        
        ttk.Button(button_frame, text="📁 打开报告目录", 
                  command=self.open_reports_folder, width=20).grid(row=17, column=0, pady=2, sticky=tk.W+tk.E)
        
        # 清除操作
        ttk.Separator(button_frame, orient='horizontal').grid(row=18, column=0, sticky=tk.W+tk.E, pady=10)
        
        clear_label = ttk.Label(button_frame, text="【清除操作】", style='Subtitle.TLabel')
        clear_label.grid(row=19, column=0, sticky=tk.W, pady=(0, 5))
        
        ttk.Button(button_frame, text="⚠️ 清除所有持仓", 
                  command=self.clear_holdings, width=20, style='Danger.TButton').grid(row=20, column=0, pady=2, sticky=tk.W+tk.E)
        
        ttk.Button(button_frame, text="⚠️ 清除所有观察", 
                  command=self.clear_watchlist, width=20, style='Danger.TButton').grid(row=21, column=0, pady=2, sticky=tk.W+tk.E)
        
        ttk.Button(button_frame, text="⚠️ 清除所有配置", 
                  command=self.clear_all, width=20, style='Danger.TButton').grid(row=22, column=0, pady=2, sticky=tk.W+tk.E)
        
        # 刷新按钮
        ttk.Separator(button_frame, orient='horizontal').grid(row=23, column=0, sticky=tk.W+tk.E, pady=10)
        
        ttk.Button(button_frame, text="🔄 刷新数据", 
                  command=self.refresh_data, width=20, style='Success.TButton').grid(row=24, column=0, pady=2, sticky=tk.W+tk.E)
    
    def create_data_panel(self, parent):
        """创建数据显示面板"""
        data_frame = ttk.Frame(parent)
        data_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        data_frame.rowconfigure(1, weight=1)
        
        # 持仓基金表格
        holdings_frame = ttk.LabelFrame(data_frame, text="持仓基金", padding="5")
        holdings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        self.holdings_tree = self.create_treeview(
            holdings_frame,
            columns=('代码', '名称', '成本净值', '持有金额', '购买日期', '投入日期'),
            widths=(80, 150, 80, 100, 100, 100)
        )
        
        # 观察基金表格
        watchlist_frame = ttk.LabelFrame(data_frame, text="观察基金", padding="5")
        watchlist_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.watchlist_tree = self.create_treeview(
            watchlist_frame,
            columns=('代码', '名称', '观察日期', '备注'),
            widths=(80, 150, 100, 200)
        )
    
    def create_treeview(self, parent, columns, widths):
        """创建表格视图"""
        # 创建滚动条
        scrollbar_y = ttk.Scrollbar(parent, orient='vertical')
        scrollbar_x = ttk.Scrollbar(parent, orient='horizontal')
        
        # 创建Treeview
        tree = ttk.Treeview(parent, columns=columns, show='headings',
                           yscrollcommand=scrollbar_y.set,
                           xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=tree.yview)
        scrollbar_x.config(command=tree.xview)
        
        # 设置列
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor='center')
        
        # 布局
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        return tree
    
    def refresh_data(self):
        """刷新数据显示"""
        # 重新加载配置
        self.config_manager = ConfigManager()
        
        # 清空表格
        for item in self.holdings_tree.get_children():
            self.holdings_tree.delete(item)
        
        for item in self.watchlist_tree.get_children():
            self.watchlist_tree.delete(item)
        
        # 加载持仓基金
        holdings = self.config_manager.config.get('holdings', {})
        for code, info in holdings.items():
            self.holdings_tree.insert('', 'end', values=(
                code,
                info.get('name', 'N/A'),
                info.get('cost_basis', 'N/A'),
                info.get('amount', 'N/A'),
                info.get('purchase_date', 'N/A'),
                info.get('investment_start_date', 'N/A')
            ))
        
        # 加载观察基金
        watchlist = self.config_manager.config.get('watchlist', {})
        for code, info in watchlist.items():
            self.watchlist_tree.insert('', 'end', values=(
                code,
                info.get('name', 'N/A'),
                info.get('watch_start_date', 'N/A'),
                info.get('note', '')
            ))
        
        # 更新窗口标题
        total = len(holdings) + len(watchlist)
        self.root.title(f"基金管理系统 v2.3 - 持仓:{len(holdings)} | 观察:{len(watchlist)} | 总计:{total}")
    
    # ============= 对话框功能 =============
    
    def add_holding_dialog(self):
        """添加持仓基金对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加持仓基金")
        dialog.geometry("400x350")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入字段
        fields = [
            ('基金代码:', 'code'),
            ('基金名称:', 'name'),
            ('成本净值:', 'cost_basis'),
            ('持有金额:', 'amount'),
            ('购买日期:', 'purchase_date'),
            ('投入日期:', 'investment_start_date')
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(frame, width=30)
            entry.grid(row=i, column=1, pady=5, padx=5)
            entries[key] = entry
            
            # 添加提示
            if key in ['purchase_date', 'investment_start_date']:
                ttk.Label(frame, text="(YYYY-MM-DD)", foreground='gray').grid(row=i, column=2, sticky=tk.W)
        
        # 按钮
        def on_submit():
            try:
                code = entries['code'].get().strip()
                name = entries['name'].get().strip()
                cost_basis = float(entries['cost_basis'].get().strip())
                amount = float(entries['amount'].get().strip())
                purchase_date = entries['purchase_date'].get().strip()
                investment_start_date = entries['investment_start_date'].get().strip() or None
                
                if not code or not name:
                    messagebox.showerror("错误", "基金代码和名称不能为空")
                    return
                
                success = self.config_manager.add_holding(
                    code, name, cost_basis, amount, purchase_date, investment_start_date
                )
                
                if success:
                    messagebox.showinfo("成功", f"已添加持仓基金: {name}")
                    self.refresh_data()
                    dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=len(fields), column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="确定", command=on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_watchlist_dialog(self):
        """添加观察基金对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加观察基金")
        dialog.geometry("400x250")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入字段
        fields = [
            ('基金代码:', 'code'),
            ('基金名称:', 'name'),
            ('观察日期:', 'watch_start_date'),
            ('备注:', 'note')
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(frame, width=30)
            entry.grid(row=i, column=1, pady=5, padx=5)
            entries[key] = entry
            
            if key == 'watch_start_date':
                ttk.Label(frame, text="(可选)", foreground='gray').grid(row=i, column=2, sticky=tk.W)
        
        # 按钮
        def on_submit():
            code = entries['code'].get().strip()
            name = entries['name'].get().strip()
            watch_start_date = entries['watch_start_date'].get().strip() or None
            note = entries['note'].get().strip()
            
            if not code or not name:
                messagebox.showerror("错误", "基金代码和名称不能为空")
                return
            
            success = self.config_manager.add_watchlist(code, name, watch_start_date, note)
            
            if success:
                messagebox.showinfo("成功", f"已添加观察基金: {name}")
                self.refresh_data()
                dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=len(fields), column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="确定", command=on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def delete_fund_dialog(self):
        """删除基金对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("删除基金")
        dialog.geometry("400x200")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="基金代码:").grid(row=0, column=0, sticky=tk.W, pady=5)
        code_entry = ttk.Entry(frame, width=30)
        code_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="删除范围:").grid(row=1, column=0, sticky=tk.W, pady=5)
        type_var = tk.StringVar(value='holding')
        ttk.Radiobutton(frame, text="持仓", variable=type_var, value='holding').grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(frame, text="观察", variable=type_var, value='watchlist').grid(row=2, column=1, sticky=tk.W)
        
        def on_submit():
            code = code_entry.get().strip()
            if not code:
                messagebox.showerror("错误", "基金代码不能为空")
                return
            
            if messagebox.askyesno("确认", f"确定要删除基金 {code} 吗？"):
                success = self.config_manager.remove_fund(code, type_var.get())
                if success:
                    messagebox.showinfo("成功", "删除成功")
                    self.refresh_data()
                    dialog.destroy()
                else:
                    messagebox.showerror("失败", "删除失败，请检查代码是否正确")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def update_fund_dialog(self):
        """更新基金信息对话框"""
        messagebox.showinfo("提示", "请在配置文件中直接修改，或使用命令行工具")
    
    def move_to_holding_dialog(self):
        """观察基金转持仓对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("观察基金转持仓")
        dialog.geometry("400x250")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ('基金代码:', 'code'),
            ('成本净值:', 'cost_basis'),
            ('持有金额:', 'amount'),
            ('购买日期:', 'purchase_date')
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(frame, width=30)
            entry.grid(row=i, column=1, pady=5, padx=5)
            entries[key] = entry
        
        def on_submit():
            try:
                code = entries['code'].get().strip()
                cost_basis = float(entries['cost_basis'].get().strip())
                amount = float(entries['amount'].get().strip())
                purchase_date = entries['purchase_date'].get().strip()
                
                if not code:
                    messagebox.showerror("错误", "基金代码不能为空")
                    return
                
                success = self.config_manager.move_to_holding(code, cost_basis, amount, purchase_date)
                
                if success:
                    messagebox.showinfo("成功", "已转为持仓")
                    self.refresh_data()
                    dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def move_to_watchlist_dialog(self):
        """持仓基金转观察对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("持仓基金转观察")
        dialog.geometry("400x150")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="基金代码:").grid(row=0, column=0, sticky=tk.W, pady=5)
        code_entry = ttk.Entry(frame, width=30)
        code_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="备注:").grid(row=1, column=0, sticky=tk.W, pady=5)
        note_entry = ttk.Entry(frame, width=30)
        note_entry.grid(row=1, column=1, pady=5, padx=5)
        
        def on_submit():
            code = code_entry.get().strip()
            note = note_entry.get().strip()
            
            if not code:
                messagebox.showerror("错误", "基金代码不能为空")
                return
            
            success = self.config_manager.move_to_watchlist(code, note)
            
            if success:
                messagebox.showinfo("成功", "已转为观察")
                self.refresh_data()
                dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def batch_add_holdings_dialog(self):
        """批量添加持仓基金对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("批量添加持仓基金")
        dialog.geometry("600x400")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="每行一个基金，格式: 代码,名称,成本净值,金额,购买日期,投入日期",
                 foreground='blue').pack(anchor=tk.W, pady=5)
        ttk.Label(frame, text="示例: 161725,招商白酒,1.0,10000,2024-01-01,2024-01-01",
                 foreground='gray').pack(anchor=tk.W, pady=5)
        
        text_area = scrolledtext.ScrolledText(frame, width=70, height=15)
        text_area.pack(fill=tk.BOTH, expand=True, pady=10)
        
        def on_submit():
            content = text_area.get('1.0', tk.END).strip()
            if not content:
                messagebox.showerror("错误", "内容不能为空")
                return
            
            holdings_list = []
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                parts = [p.strip() for p in line.split(',')]
                if len(parts) == 5:
                    parts.append(parts[4])
                if len(parts) == 6:
                    holdings_list.append(tuple(parts))
            
            if holdings_list:
                self.config_manager.batch_add_holdings(holdings_list)
                messagebox.showinfo("成功", f"已添加 {len(holdings_list)} 个持仓基金")
                self.refresh_data()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "没有有效的数据")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="确定", command=on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def batch_add_watchlist_dialog(self):
        """批量添加观察基金对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("批量添加观察基金")
        dialog.geometry("600x400")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="每行一个基金，格式: 代码,名称,观察日期,备注",
                 foreground='blue').pack(anchor=tk.W, pady=5)
        ttk.Label(frame, text="示例: 161726,招商食品,2024-01-01,等待回调",
                 foreground='gray').pack(anchor=tk.W, pady=5)
        
        text_area = scrolledtext.ScrolledText(frame, width=70, height=15)
        text_area.pack(fill=tk.BOTH, expand=True, pady=10)
        
        def on_submit():
            content = text_area.get('1.0', tk.END).strip()
            if not content:
                messagebox.showerror("错误", "内容不能为空")
                return
            
            watchlist_items = []
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                parts = [p.strip() for p in line.split(',')]
                if len(parts) == 2:
                    parts.extend(['', ''])
                elif len(parts) == 3:
                    parts.append('')
                if len(parts) == 4:
                    watchlist_items.append(tuple(parts))
            
            if watchlist_items:
                self.config_manager.batch_add_watchlist(watchlist_items)
                messagebox.showinfo("成功", f"已添加 {len(watchlist_items)} 个观察基金")
                self.refresh_data()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "没有有效的数据")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="确定", command=on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def batch_delete_dialog(self):
        """批量删除基金对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("批量删除基金")
        dialog.geometry("400x250")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="输入基金代码，用逗号分隔:",
                 foreground='blue').pack(anchor=tk.W, pady=5)
        ttk.Label(frame, text="示例: 161725,161726,000001",
                 foreground='gray').pack(anchor=tk.W, pady=5)
        
        code_entry = ttk.Entry(frame, width=50)
        code_entry.pack(fill=tk.X, pady=10)
        
        ttk.Label(frame, text="删除范围:").pack(anchor=tk.W, pady=5)
        type_var = tk.StringVar(value='holding')
        ttk.Radiobutton(frame, text="仅持仓", variable=type_var, value='holding').pack(anchor=tk.W)
        ttk.Radiobutton(frame, text="仅观察", variable=type_var, value='watchlist').pack(anchor=tk.W)
        ttk.Radiobutton(frame, text="持仓和观察都删", variable=type_var, value='both').pack(anchor=tk.W)
        
        def on_submit():
            codes_input = code_entry.get().strip()
            if not codes_input:
                messagebox.showerror("错误", "基金代码不能为空")
                return
            
            fund_codes = [code.strip() for code in codes_input.split(',')]
            
            if messagebox.askyesno("确认", f"确定要删除 {len(fund_codes)} 个基金吗？"):
                self.config_manager.batch_delete_funds(fund_codes, type_var.get())
                messagebox.showinfo("成功", "批量删除完成")
                self.refresh_data()
                dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="确定", command=on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    # ============= 分析和报告功能 =============
    
    def run_ma_analysis(self):
        """运行均线分析"""
        if messagebox.askyesno("确认", "是否运行均线分析？这可能需要几分钟时间。"):
            # 在新线程中运行，避免界面冻结
            threading.Thread(target=self._run_ma_analysis_thread, daemon=True).start()
    
    def _run_ma_analysis_thread(self):
        """在后台线程运行均线分析"""
        try:
            # 运行分析脚本
            result = subprocess.run([sys.executable, 'ma_analysis.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.root.after(0, lambda: messagebox.showinfo("成功", "均线分析完成！"))
            else:
                self.root.after(0, lambda: messagebox.showerror("错误", f"分析失败:\n{result.stderr}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"运行失败: {str(e)}"))
    
    def export_report_dialog(self):
        """导出报告对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("导出报告")
        dialog.geometry("400x250")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="选择报告格式:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        format_var = tk.StringVar(value='html')
        
        formats = [
            ('HTML格式 (推荐)', 'html'),
            ('TXT格式', 'txt'),
            ('Markdown格式', 'markdown'),
            ('JSON格式', 'json')
        ]
        
        for text, value in formats:
            ttk.Radiobutton(frame, text=text, variable=format_var, value=value).pack(anchor=tk.W, pady=5)
        
        def on_export():
            messagebox.showinfo("提示", "请使用均线分析工具完成分析后，选择导出格式。\n或直接查看 reports 目录中的报告。")
            dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="确定", command=on_export).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def open_reports_folder(self):
        """打开报告目录"""
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            messagebox.showinfo("提示", "报告目录已创建，但还没有任何报告。\n请先运行均线分析。")
        else:
            # Windows
            if sys.platform == 'win32':
                os.startfile(reports_dir)
            # macOS
            elif sys.platform == 'darwin':
                subprocess.run(['open', reports_dir])
            # Linux
            else:
                subprocess.run(['xdg-open', reports_dir])
    
    # ============= 完整分析报告功能 =============
    
    def run_full_analysis(self):
        """运行完整分析报告（集成main.py功能）"""
        # 创建选项对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("完整分析报告")
        dialog.geometry("500x400")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="📊 完整分析报告设置", style='Subtitle.TLabel').pack(pady=10)
        
        # 选项
        include_ma_var = tk.BooleanVar(value=True)
        send_wechat_var = tk.BooleanVar(value=False)
        save_report_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(frame, text="包含均线分析（推荐）", 
                       variable=include_ma_var).pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(frame, text="推送到微信", 
                       variable=send_wechat_var).pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(frame, text="保存报告文件", 
                       variable=save_report_var).pack(anchor=tk.W, pady=5)
        
        ttk.Label(frame, text="\n说明：", foreground='gray').pack(anchor=tk.W, pady=(10, 0))
        ttk.Label(frame, text="• 完整分析将分析所有持仓和观察基金", 
                 foreground='gray', wraplength=400).pack(anchor=tk.W, padx=20)
        ttk.Label(frame, text="• 包含收益分析、趋势预测、均线信号等", 
                 foreground='gray', wraplength=400).pack(anchor=tk.W, padx=20)
        ttk.Label(frame, text="• 微信推送需要配置 config.py 中的推送参数", 
                 foreground='gray', wraplength=400).pack(anchor=tk.W, padx=20)
        ttk.Label(frame, text="• 报告将保存到 reports/ 目录", 
                 foreground='gray', wraplength=400).pack(anchor=tk.W, padx=20)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        def on_submit():
            dialog.destroy()
            self.generate_full_report(
                include_ma_analysis=include_ma_var.get(),
                send_wechat=send_wechat_var.get(),
                save_report=save_report_var.get()
            )
        
        ttk.Button(button_frame, text="开始分析", command=on_submit, 
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def generate_full_report(self, include_ma_analysis=True, send_wechat=False, save_report=True):
        """生成完整分析报告（后台线程）"""
        
        def run_analysis():
            try:
                # 显示进度对话框
                progress_dialog = tk.Toplevel(self.root)
                progress_dialog.title("正在分析...")
                progress_dialog.geometry("400x200")
                
                progress_frame = ttk.Frame(progress_dialog, padding="20")
                progress_frame.pack(fill=tk.BOTH, expand=True)
                
                progress_label = ttk.Label(progress_frame, text="正在分析基金数据，请稍候...", 
                                          style='Subtitle.TLabel')
                progress_label.pack(pady=20)
                
                progress_text = scrolledtext.ScrolledText(progress_frame, height=8, width=50)
                progress_text.pack(fill=tk.BOTH, expand=True)
                
                def log_progress(msg):
                    progress_text.insert(tk.END, msg + "\n")
                    progress_text.see(tk.END)
                    progress_text.update()
                
                log_progress(f"开始生成完整分析报告... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                analysis_results = []
                ma_reports = []
                
                # 获取持仓和观察基金
                holdings = self.config_manager.config.get('holdings', {})
                watchlist = self.config_manager.config.get('watchlist', {})
                
                # 分析持仓基金
                log_progress(f"\n分析 {len(holdings)} 只持仓基金...")
                for code, holding in holdings.items():
                    log_progress(f"正在分析基金 {code} - {holding.get('name', 'N/A')}...")
                    
                    try:
                        analysis = self.fund_analyzer.get_fund_analysis(
                            fund_code=code,
                            fund_name=holding.get("name", f"基金{code}"),
                            cost_basis=holding.get("cost_basis", 1.0),
                            amount=holding.get("amount", 10000),
                            lookback_days=30,
                            investment_start_date=holding.get("investment_start_date"),
                            include_ma_analysis=include_ma_analysis
                        )
                        
                        if analysis:
                            analysis_results.append(analysis)
                            
                            # 如果有均线分析，添加到报告中
                            if include_ma_analysis and analysis.get("ma_analysis"):
                                ma_report = self.ma_analyzer.format_analysis_report(analysis["ma_analysis"])
                                ma_reports.append(ma_report)
                            
                            log_progress(f"✓ 基金 {code} 分析完成")
                        else:
                            log_progress(f"✗ 基金 {code} 分析失败")
                    except Exception as e:
                        log_progress(f"✗ 基金 {code} 分析出错: {str(e)}")
                    
                    # 避免请求过快
                    time.sleep(2)
                
                # 分析观察基金
                if watchlist and include_ma_analysis:
                    log_progress(f"\n分析 {len(watchlist)} 只观察基金...")
                    for code, watch_info in watchlist.items():
                        log_progress(f"正在分析观察基金 {code} - {watch_info.get('name', 'N/A')}...")
                        
                        try:
                            ma_analysis = self.ma_analyzer.analyze_fund(
                                code,
                                watch_info.get("name", f"基金{code}"),
                                watch_info.get("watch_start_date")
                            )
                            
                            if ma_analysis and 'error' not in ma_analysis:
                                ma_report = self.ma_analyzer.format_analysis_report(ma_analysis)
                                ma_reports.append(ma_report)
                                log_progress(f"✓ 观察基金 {code} 分析完成")
                            else:
                                log_progress(f"✗ 观察基金 {code} 分析失败")
                        except Exception as e:
                            log_progress(f"✗ 观察基金 {code} 分析出错: {str(e)}")
                        
                        # 避免请求过快
                        time.sleep(2)
                
                if not analysis_results and not ma_reports:
                    log_progress("\n⚠️ 没有生成任何分析结果")
                    messagebox.showerror("错误", "没有生成任何分析结果")
                    progress_dialog.destroy()
                    return
                
                # 生成报告
                log_progress("\n正在生成报告...")
                report_parts = []
                
                if analysis_results:
                    basic_report = self.message_sender.format_fund_report(analysis_results)
                    report_parts.append(basic_report)
                
                # 添加均线分析报告
                if ma_reports:
                    report_parts.append("\n" + "="*60)
                    report_parts.append("\n📊 均线分析报告")
                    report_parts.append("="*60 + "\n")
                    report_parts.append("\n".join(ma_reports))
                
                report = "\n".join(report_parts)
                
                # 保存报告文件
                if save_report:
                    log_progress("正在保存报告文件...")
                    reports_dir = 'reports'
                    if not os.path.exists(reports_dir):
                        os.makedirs(reports_dir)
                    
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    report_file = os.path.join(reports_dir, f'full_report_{timestamp}.txt')
                    
                    with open(report_file, 'w', encoding='utf-8') as f:
                        f.write(report)
                    
                    log_progress(f"✓ 报告已保存: {report_file}")
                
                # 发送微信推送
                if send_wechat:
                    log_progress("正在推送到微信...")
                    title = f"基金管家日报 - {datetime.now().strftime('%Y-%m-%d')}"
                    
                    try:
                        success = self.message_sender.send_all(title, report)
                        if success:
                            log_progress("✓ 微信推送成功")
                        else:
                            log_progress("✗ 微信推送失败")
                    except Exception as e:
                        log_progress(f"✗ 微信推送出错: {str(e)}")
                
                log_progress("\n✅ 完整分析报告生成完成！")
                
                # 显示报告预览
                ttk.Button(progress_frame, text="查看完整报告", 
                          command=lambda: self.show_report_preview(report)).pack(pady=10)
                ttk.Button(progress_frame, text="打开报告目录", 
                          command=lambda: [progress_dialog.destroy(), self.open_reports_folder()]).pack(pady=5)
                ttk.Button(progress_frame, text="关闭", 
                          command=progress_dialog.destroy).pack(pady=5)
                
            except Exception as e:
                messagebox.showerror("错误", f"分析过程中出现错误：\n{str(e)}")
                if 'progress_dialog' in locals():
                    progress_dialog.destroy()
        
        # 在后台线程运行
        thread = threading.Thread(target=run_analysis, daemon=True)
        thread.start()
    
    def show_report_preview(self, report):
        """显示报告预览"""
        preview_dialog = tk.Toplevel(self.root)
        preview_dialog.title("报告预览")
        preview_dialog.geometry("800x600")
        
        frame = ttk.Frame(preview_dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="📊 完整分析报告", style='Title.TLabel').pack(pady=10)
        
        text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=('Courier', 10))
        text.pack(fill=tk.BOTH, expand=True, pady=10)
        text.insert(tk.END, report)
        text.config(state=tk.DISABLED)
        
        ttk.Button(frame, text="关闭", command=preview_dialog.destroy).pack(pady=5)
    
    # ============= 清除功能 =============
    
    def clear_holdings(self):
        """清除所有持仓"""
        if messagebox.askyesno("警告", "确定要清除所有持仓基金吗？\n此操作不可恢复！"):
            if self.config_manager.clear_holdings():
                messagebox.showinfo("成功", "已清除所有持仓基金")
                self.refresh_data()
    
    def clear_watchlist(self):
        """清除所有观察"""
        if messagebox.askyesno("警告", "确定要清除所有观察基金吗？\n此操作不可恢复！"):
            if self.config_manager.clear_watchlist():
                messagebox.showinfo("成功", "已清除所有观察基金")
                self.refresh_data()
    
    def clear_all(self):
        """清除所有配置"""
        if messagebox.askyesno("警告", "⚠️ 确定要清除所有配置数据吗？\n包括持仓和观察基金！\n此操作不可恢复！"):
            if self.config_manager.clear_all():
                messagebox.showinfo("成功", "已清除所有配置数据")
                self.refresh_data()


def main():
    """主函数"""
    root = tk.Tk()
    app = FundManagerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

