#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基金管理系统 - 图形化界面 v2.4
改进：
1. 优化批量添加 - 简化输入格式，支持导入文件
2. 自动显示报告 - 分析完成后直接显示完整报告
3. 优化界面布局 - 主要功能更突出，次要功能折叠
4. 添加帮助和免责声明
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import os
import sys
import io
import threading
import time
from datetime import datetime
from config_manager import ConfigManager
from report_generator import ReportGenerator
from fund_analyzer import FundAnalyzer
from message_sender import MessageSender
from moving_average_analyzer import MovingAverageAnalyzer
import subprocess

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, ValueError):
        # 如果已经是 TextIOWrapper 或在 GUI 环境中，忽略错误
        pass


class FundManagerGUI:
    """基金管理系统图形化界面 v2.4"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("基金管理系统 v2.4")
        self.root.geometry("1200x800")
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 初始化分析器
        self.fund_analyzer = FundAnalyzer()
        self.message_sender = MessageSender()
        self.ma_analyzer = MovingAverageAnalyzer()
        
        # 显示启动免责声明
        self.show_disclaimer()
        
        # 设置主题
        self.setup_style()
        
        # 创建界面
        self.create_widgets()
        
        # 加载数据
        self.refresh_data()
    
    def show_disclaimer(self):
        """显示免责声明"""
        disclaimer = """
⚠️ 免责声明

本软件仅供参考，不构成投资建议。

• 本软件提供的所有分析和数据仅供参考
• 投资有风险，决策需谨慎
• 历史数据不代表未来表现
• 任何投资决策都应该基于您自己的判断
• 使用本软件产生的任何损失，作者不承担任何责任

请理性投资，谨慎决策！

首次启动提示：
• 点击右上角 ❓ 按钮可查看使用说明
• 主要功能在顶部快捷操作区
• 批量添加支持简化输入格式
"""
        
        # 检查是否已经显示过
        disclaimer_file = '.disclaimer_shown'
        if os.path.exists(disclaimer_file):
            return
        
        result = messagebox.showinfo("免责声明", disclaimer)
        
        # 标记已显示
        with open(disclaimer_file, 'w', encoding='utf-8') as f:
            f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    def setup_style(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置颜色
        style.configure('Title.TLabel', font=('微软雅黑', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('微软雅黑', 12, 'bold'), foreground='#34495e')
        style.configure('TButton', font=('微软雅黑', 10), padding=5)
        style.configure('Primary.TButton', font=('微软雅黑', 11, 'bold'), foreground='white', background='#3498db')
        style.configure('Success.TButton', font=('微软雅黑', 10), foreground='white', background='#27ae60')
        style.configure('Danger.TButton', font=('微软雅黑', 10), foreground='white', background='#e74c3c')
        style.configure('Warning.TButton', font=('微软雅黑', 10), foreground='white', background='#f39c12')
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置grid权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 顶部：标题和帮助
        self.create_header(main_frame)
        
        # 中部：快捷操作区（主要功能）
        self.create_quick_actions(main_frame)
        
        # 底部：数据显示和详细功能
        self.create_main_content(main_frame)
    
    def create_header(self, parent):
        """创建顶部标题和帮助区"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        # 标题
        title_label = ttk.Label(header_frame, text="📊 基金管理系统 v2.4", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # 帮助按钮
        help_button = ttk.Button(header_frame, text="❓ 帮助", command=self.show_help, width=10)
        help_button.grid(row=0, column=1, padx=5)
        
        # 免责声明按钮
        disclaimer_button = ttk.Button(header_frame, text="⚠️ 免责声明", 
                                       command=self.show_disclaimer_dialog, width=12)
        disclaimer_button.grid(row=0, column=2, padx=5)
    
    def create_quick_actions(self, parent):
        """创建快捷操作区（主要功能）"""
        quick_frame = ttk.LabelFrame(parent, text="⚡ 快捷操作", padding="15")
        quick_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 创建两行按钮
        # 第一行：基金管理
        row1_frame = ttk.Frame(quick_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(row1_frame, text="📝 基金管理:", style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(row1_frame, text="➕ 快速添加基金", 
                  command=self.quick_add_fund_dialog, 
                  style='Success.TButton', width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(row1_frame, text="📦 批量导入", 
                  command=self.batch_import_dialog, 
                  style='Success.TButton', width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(row1_frame, text="✏️ 修改基金", 
                  command=self.edit_fund_dialog, 
                  width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(row1_frame, text="🗑️ 删除基金", 
                  command=self.delete_fund_dialog, 
                  width=12).pack(side=tk.LEFT, padx=5)
        
        # 第二行：分析报告
        row2_frame = ttk.Frame(quick_frame)
        row2_frame.pack(fill=tk.X)
        
        ttk.Label(row2_frame, text="📊 分析报告:", style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(row2_frame, text="📈 一键生成完整报告", 
                  command=self.one_click_analysis, 
                  style='Primary.TButton', width=18).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(row2_frame, text="📊 均线分析", 
                  command=self.run_ma_analysis_quick, 
                  style='Primary.TButton', width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(row2_frame, text="📁 查看报告", 
                  command=self.open_reports_folder, 
                  width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(row2_frame, text="🔄 刷新数据", 
                  command=self.refresh_data, 
                  style='Success.TButton', width=12).pack(side=tk.LEFT, padx=5)
    
    def create_main_content(self, parent):
        """创建主内容区"""
        content_frame = ttk.Frame(parent)
        content_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # 左侧：详细功能（可折叠）
        self.create_advanced_panel(content_frame)
        
        # 右侧：数据显示
        self.create_data_panel(content_frame)
    
    def create_advanced_panel(self, parent):
        """创建高级功能面板"""
        advanced_frame = ttk.LabelFrame(parent, text="🔧 高级功能", padding="10")
        advanced_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # 使用滚动条
        canvas = tk.Canvas(advanced_frame, width=200)
        scrollbar = ttk.Scrollbar(advanced_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 添加功能按钮
        buttons = [
            ("【配置管理】", None, 'Subtitle.TLabel'),
            ("添加持仓基金", self.add_holding_dialog, None),
            ("添加观察基金", self.add_watchlist_dialog, None),
            ("观察→持仓", self.move_to_holding_dialog, None),
            ("持仓→观察", self.move_to_watchlist_dialog, None),
            ("", None, None),  # 分隔
            ("【批量操作】", None, 'Subtitle.TLabel'),
            ("批量添加持仓", self.batch_add_holdings_dialog, None),
            ("批量添加观察", self.batch_add_watchlist_dialog, None),
            ("批量删除", self.batch_delete_dialog, None),
            ("", None, None),  # 分隔
            ("【清除操作】", None, 'Subtitle.TLabel'),
            ("清除所有持仓", self.clear_holdings, 'Danger.TButton'),
            ("清除所有观察", self.clear_watchlist, 'Danger.TButton'),
            ("清除所有配置", self.clear_all, 'Danger.TButton'),
        ]
        
        for i, (text, command, style) in enumerate(buttons):
            if not text:
                ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=5)
            elif style == 'Subtitle.TLabel':
                ttk.Label(scrollable_frame, text=text, style='Subtitle.TLabel').pack(anchor=tk.W, pady=(10, 5))
            elif command:
                ttk.Button(scrollable_frame, text=text, command=command, 
                          width=18, style=style).pack(fill=tk.X, pady=2)
    
    def create_data_panel(self, parent):
        """创建数据显示面板"""
        data_frame = ttk.Frame(parent)
        data_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        data_frame.rowconfigure(1, weight=1)
        
        # 持仓基金表格
        holdings_frame = ttk.LabelFrame(data_frame, text="💰 持仓基金", padding="5")
        holdings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        self.holdings_tree = self.create_treeview(
            holdings_frame,
            columns=('代码', '名称', '成本净值', '持有金额', '购买日期'),
            widths=(80, 180, 90, 100, 110)
        )
        
        # 观察基金表格
        watchlist_frame = ttk.LabelFrame(data_frame, text="👀 观察基金", padding="5")
        watchlist_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.watchlist_tree = self.create_treeview(
            watchlist_frame,
            columns=('代码', '名称', '观察日期', '备注'),
            widths=(80, 180, 110, 180)
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
                info.get('purchase_date', 'N/A')
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
        self.root.title(f"基金管理系统 v2.4 - 持仓:{len(holdings)} | 观察:{len(watchlist)} | 总计:{total}")
    
    # ============= 帮助和免责声明 =============
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
📖 基金管理系统使用指南

【快速开始】
1. 点击"快速添加基金"添加单个基金
2. 点击"批量导入"批量添加多个基金
3. 点击"一键生成完整报告"开始分析

【简化输入格式】
批量添加时支持简化格式，用空格或逗号分隔：

持仓基金：
  代码 名称 成本 金额 日期
  示例: 161725 招商白酒 1.0 10000 2024-01-01

观察基金：
  代码 名称
  示例: 161726 招商食品

【主要功能】
• 快速添加基金 - 单个添加持仓/观察基金
• 批量导入 - 从文本或文件导入多个基金
• 一键生成完整报告 - 自动分析并显示报告
• 均线分析 - 专门的均线技术分析
• 查看报告 - 打开报告目录查看历史报告

【高级功能】
• 左侧面板包含详细的配置和批量操作
• 支持持仓和观察基金互相转换
• 支持批量删除和清空操作

【报告说明】
• 分析完成后会自动显示完整报告
• 报告同时保存在 reports/ 目录
• 支持导出多种格式(TXT/HTML/JSON)

【风险提示】
⚠️ 本软件仅供参考，不构成投资建议
⚠️ 投资有风险，决策需谨慎
⚠️ 历史数据不代表未来表现

【联系方式】
如有问题，请查看 README.md 文档
"""
        
        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("使用帮助")
        help_dialog.geometry("700x600")
        
        frame = ttk.Frame(help_dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=('微软雅黑', 10))
        text.pack(fill=tk.BOTH, expand=True, pady=10)
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)
        
        ttk.Button(frame, text="关闭", command=help_dialog.destroy).pack(pady=5)
    
    def show_disclaimer_dialog(self):
        """显示免责声明对话框"""
        disclaimer_text = """
⚠️ 免责声明

本软件仅供学习和参考使用，不构成任何投资建议。

【重要提示】
1. 本软件提供的所有分析、数据、报告仅供参考
2. 任何投资决策都应该基于您自己的独立判断
3. 历史数据和技术分析不能保证未来表现
4. 投资有风险，入市需谨慎

【数据来源】
• 基金净值数据来自公开渠道（如天天基金网）
• 数据可能存在延迟或误差
• 请以基金公司官方数据为准

【分析说明】
• 均线分析、趋势预测等仅为技术参考
• 不能作为买卖决策的唯一依据
• 建议结合基本面分析、市场环境等综合判断

【责任限制】
• 使用本软件产生的任何投资损失，作者不承担任何责任
• 用户应自行承担投资风险
• 请理性投资，合理配置资产

【使用条款】
使用本软件即表示您已阅读并同意上述免责声明。

祝您投资顺利！但请务必谨慎决策。
"""
        
        disclaimer_dialog = tk.Toplevel(self.root)
        disclaimer_dialog.title("免责声明")
        disclaimer_dialog.geometry("700x500")
        
        frame = ttk.Frame(disclaimer_dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="⚠️ 请仔细阅读以下免责声明", 
                 style='Title.TLabel', foreground='red').pack(pady=10)
        
        text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=('微软雅黑', 10))
        text.pack(fill=tk.BOTH, expand=True, pady=10)
        text.insert(tk.END, disclaimer_text)
        text.config(state=tk.DISABLED)
        
        ttk.Button(frame, text="我已阅读并理解", 
                  command=disclaimer_dialog.destroy,
                  style='Primary.TButton').pack(pady=5)
    
    # ============= 优化的添加功能 =============
    
    def quick_add_fund_dialog(self):
        """快速添加基金（统一入口）"""
        dialog = tk.Toplevel(self.root)
        dialog.title("快速添加基金")
        dialog.geometry("500x400")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="📝 快速添加基金", style='Title.TLabel').pack(pady=10)
        
        # 选择类型
        ttk.Label(frame, text="选择类型:", font=('微软雅黑', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        fund_type_var = tk.StringVar(value='holding')
        ttk.Radiobutton(frame, text="💰 持仓基金（已买入）", 
                       variable=fund_type_var, value='holding').pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(frame, text="👀 观察基金（待买入）", 
                       variable=fund_type_var, value='watchlist').pack(anchor=tk.W, padx=20)
        
        # 基本信息
        ttk.Label(frame, text="\n基本信息:", font=('微软雅黑', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        fields_frame = ttk.Frame(frame)
        fields_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(fields_frame, text="基金代码:").grid(row=0, column=0, sticky=tk.W, pady=3)
        code_entry = ttk.Entry(fields_frame, width=30)
        code_entry.grid(row=0, column=1, pady=3, padx=5)
        
        ttk.Label(fields_frame, text="基金名称:").grid(row=1, column=0, sticky=tk.W, pady=3)
        name_entry = ttk.Entry(fields_frame, width=30)
        name_entry.grid(row=1, column=1, pady=3, padx=5)
        
        # 持仓信息（条件显示）
        holding_frame = ttk.Frame(frame)
        holding_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(holding_frame, text="\n持仓信息（仅持仓基金需要填写）:", 
                 font=('微软雅黑', 10, 'bold'), foreground='gray').pack(anchor=tk.W)
        
        holding_fields = ttk.Frame(holding_frame)
        holding_fields.pack(fill=tk.X, pady=5)
        
        ttk.Label(holding_fields, text="成本净值:").grid(row=0, column=0, sticky=tk.W, pady=3)
        cost_entry = ttk.Entry(holding_fields, width=30)
        cost_entry.grid(row=0, column=1, pady=3, padx=5)
        
        ttk.Label(holding_fields, text="持有金额:").grid(row=1, column=0, sticky=tk.W, pady=3)
        amount_entry = ttk.Entry(holding_fields, width=30)
        amount_entry.grid(row=1, column=1, pady=3, padx=5)
        
        ttk.Label(holding_fields, text="购买日期:").grid(row=2, column=0, sticky=tk.W, pady=3)
        date_entry = ttk.Entry(holding_fields, width=30)
        date_entry.grid(row=2, column=1, pady=3, padx=5)
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        def on_submit():
            code = code_entry.get().strip()
            name = name_entry.get().strip()
            
            if not code or not name:
                messagebox.showerror("错误", "基金代码和名称不能为空")
                return
            
            if fund_type_var.get() == 'holding':
                try:
                    cost = float(cost_entry.get().strip())
                    amount = float(amount_entry.get().strip())
                    date = date_entry.get().strip()
                    
                    success = self.config_manager.add_holding(code, name, cost, amount, date, date)
                    if success:
                        messagebox.showinfo("成功", f"✓ 已添加持仓基金: {name}")
                        self.refresh_data()
                        dialog.destroy()
                except ValueError:
                    messagebox.showerror("错误", "请输入有效的数字")
            else:
                success = self.config_manager.add_watchlist(code, name, None, '')
                if success:
                    messagebox.showinfo("成功", f"✓ 已添加观察基金: {name}")
                    self.refresh_data()
                    dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="确定", command=on_submit, 
                  style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def batch_import_dialog(self):
        """批量导入基金（优化版）"""
        dialog = tk.Toplevel(self.root)
        dialog.title("批量导入基金")
        dialog.geometry("800x600")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="📦 批量导入基金", style='Title.TLabel').pack(pady=10)
        
        # 选择类型
        type_frame = ttk.Frame(frame)
        type_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(type_frame, text="导入类型:", font=('微软雅黑', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        fund_type_var = tk.StringVar(value='holding')
        ttk.Radiobutton(type_frame, text="持仓基金", 
                       variable=fund_type_var, value='holding').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="观察基金", 
                       variable=fund_type_var, value='watchlist').pack(side=tk.LEFT, padx=5)
        
        # 格式说明
        help_frame = ttk.LabelFrame(frame, text="✏️ 输入格式（简化版）", padding="10")
        help_frame.pack(fill=tk.X, pady=10)
        
        help_text = """
【持仓基金】每行格式（用空格或逗号分隔）：
  代码 名称 成本净值 持有金额 购买日期
  示例: 161725 招商白酒 1.0 10000 2024-01-01
  或: 161725,招商白酒,1.0,10000,2024-01-01

【观察基金】每行格式：
  代码 名称
  示例: 161726 招商食品
  或: 161726,招商食品

支持混合使用空格和逗号，系统会自动识别！
"""
        ttk.Label(help_frame, text=help_text, font=('微软雅黑', 9), 
                 foreground='blue', justify=tk.LEFT).pack(anchor=tk.W)
        
        # 输入区
        ttk.Label(frame, text="请输入基金数据（每行一个）:", 
                 font=('微软雅黑', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        text_area = scrolledtext.ScrolledText(frame, width=80, height=15, font=('Consolas', 10))
        text_area.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        def on_import_file():
            """从文件导入"""
            file_path = filedialog.askopenfilename(
                title="选择导入文件",
                filetypes=[("文本文件", "*.txt"), ("CSV文件", "*.csv"), ("所有文件", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    text_area.delete('1.0', tk.END)
                    text_area.insert('1.0', content)
                    messagebox.showinfo("成功", "文件导入成功！请检查数据后点击导入。")
                except Exception as e:
                    messagebox.showerror("错误", f"文件读取失败：{str(e)}")
        
        def on_submit():
            content = text_area.get('1.0', tk.END).strip()
            if not content:
                messagebox.showerror("错误", "内容不能为空")
                return
            
            fund_type = fund_type_var.get()
            success_count = 0
            fail_count = 0
            
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # 智能解析：支持空格和逗号混合
                    # 先尝试用逗号分割
                    if ',' in line:
                        parts = [p.strip() for p in line.split(',')]
                    else:
                        # 用空格分割
                        parts = line.split()
                    
                    if fund_type == 'holding':
                        if len(parts) >= 5:
                            code, name, cost, amount, date = parts[:5]
                            self.config_manager.add_holding(code, name, float(cost), float(amount), date, date)
                            success_count += 1
                        else:
                            fail_count += 1
                    else:
                        if len(parts) >= 2:
                            code, name = parts[:2]
                            self.config_manager.add_watchlist(code, name, None, '')
                            success_count += 1
                        else:
                            fail_count += 1
                            
                except Exception as e:
                    fail_count += 1
                    print(f"导入失败: {line}, 错误: {str(e)}")
            
            result_msg = f"导入完成！\n成功: {success_count} 个\n失败: {fail_count} 个"
            messagebox.showinfo("导入结果", result_msg)
            
            if success_count > 0:
                self.refresh_data()
            
            if fail_count == 0:
                dialog.destroy()
        
        ttk.Button(button_frame, text="📁 从文件导入", 
                  command=on_import_file, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✓ 开始导入", 
                  command=on_submit, style='Success.TButton', width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", 
                  command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)
    
    # ============= 优化的分析功能 =============
    
    def one_click_analysis(self):
        """一键生成完整报告（优化版 - 自动显示）"""
        if not self.config_manager.config.get('holdings') and not self.config_manager.config.get('watchlist'):
            messagebox.showwarning("提示", "请先添加基金再进行分析")
            return
        
        # 直接开始分析，不显示选项对话框
        self.generate_full_report_auto()
    
    def generate_full_report_auto(self):
        """自动生成完整报告（直接显示结果）"""
        
        # 创建进度窗口
        progress_dialog = tk.Toplevel(self.root)
        progress_dialog.title("正在分析...")
        progress_dialog.geometry("600x400")
        progress_dialog.grab_set()  # 模态窗口
        
        progress_frame = ttk.Frame(progress_dialog, padding="20")
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(progress_frame, text="📊 正在生成完整分析报告", 
                 style='Title.TLabel').pack(pady=10)
        
        ttk.Label(progress_frame, text="请稍候，这可能需要几分钟时间...", 
                 font=('微软雅黑', 10)).pack(pady=5)
        
        progress_text = scrolledtext.ScrolledText(progress_frame, height=15, width=70)
        progress_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        def log_progress(msg):
            """记录进度"""
            progress_text.insert(tk.END, msg + "\n")
            progress_text.see(tk.END)
            progress_text.update()
        
        def run_analysis():
            """后台分析线程"""
            try:
                log_progress(f"> 开始分析 - {datetime.now().strftime('%H:%M:%S')}")
                
                analysis_results = []
                ma_reports = []
                
                # 获取基金
                holdings = self.config_manager.config.get('holdings', {})
                watchlist = self.config_manager.config.get('watchlist', {})
                
                total_funds = len(holdings) + len(watchlist)
                current = 0
                
                # 分析持仓
                log_progress(f"\n【1/2】分析持仓基金 ({len(holdings)} 只)...")
                for code, holding in holdings.items():
                    current += 1
                    log_progress(f"  [{current}/{total_funds}] {code} {holding.get('name', 'N/A')}...")
                    
                    try:
                        # 均线分析
                        ma_analysis = self.ma_analyzer.analyze_fund(
                            code,
                            holding.get("name", f"基金{code}"),
                            holding.get("investment_start_date"),
                            include_flow=True,
                            include_hot=True
                        )
                        
                        if ma_analysis and 'error' not in ma_analysis:
                            ma_report = self.ma_analyzer.format_analysis_report(ma_analysis)
                            ma_reports.append(ma_report)
                            log_progress(f"  [OK] 完成")
                        else:
                            log_progress(f"  [FAIL] 失败")
                    except Exception as e:
                        log_progress(f"  [ERROR] 错误: {str(e)}")
                    
                    time.sleep(1.5)  # 避免请求过快
                
                # 分析观察
                log_progress(f"\n【2/2】分析观察基金 ({len(watchlist)} 只)...")
                for code, watch_info in watchlist.items():
                    current += 1
                    log_progress(f"  [{current}/{total_funds}] {code} {watch_info.get('name', 'N/A')}...")
                    
                    try:
                        ma_analysis = self.ma_analyzer.analyze_fund(
                            code,
                            watch_info.get("name", f"基金{code}"),
                            watch_info.get("watch_start_date"),
                            include_flow=True,
                            include_hot=True
                        )
                        
                        if ma_analysis and 'error' not in ma_analysis:
                            ma_report = self.ma_analyzer.format_analysis_report(ma_analysis)
                            ma_reports.append(ma_report)
                            log_progress(f"  [OK] 完成")
                        else:
                            log_progress(f"  [FAIL] 失败")
                    except Exception as e:
                        log_progress(f"  [ERROR] 错误: {str(e)}")
                    
                    time.sleep(1.5)
                
                if not ma_reports:
                    log_progress("\n[WARN] 没有生成任何分析结果")
                    messagebox.showerror("错误", "没有生成任何分析结果，请检查网络连接")
                    progress_dialog.destroy()
                    return
                
                # 生成完整报告
                log_progress("\n> 正在生成报告...")
                
                report_parts = []
                report_parts.append("="*60)
                report_parts.append(f"基金分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                report_parts.append("="*60)
                report_parts.append(f"\n持仓基金: {len(holdings)} 只")
                report_parts.append(f"观察基金: {len(watchlist)} 只")
                report_parts.append(f"总计: {total_funds} 只\n")
                report_parts.append("="*60)
                report_parts.append("\n")
                report_parts.extend(ma_reports)
                
                report = "\n".join(report_parts)
                
                # 保存报告
                log_progress("> 正在保存报告...")
                reports_dir = 'reports'
                if not os.path.exists(reports_dir):
                    os.makedirs(reports_dir)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_file = os.path.join(reports_dir, f'analysis_{timestamp}.txt')
                
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                log_progress(f"[OK] 报告已保存: {report_file}")
                log_progress("\n[DONE] 分析完成！")
                
                # 关闭进度窗口
                progress_dialog.destroy()
                
                # 自动显示报告
                self.show_report_preview(report, report_file)
                
            except Exception as e:
                log_progress(f"\n[ERROR] 分析出错: {str(e)}")
                messagebox.showerror("错误", f"分析过程中出现错误：\n{str(e)}")
                if progress_dialog.winfo_exists():
                    progress_dialog.destroy()
        
        # 在后台线程运行
        thread = threading.Thread(target=run_analysis, daemon=True)
        thread.start()
    
    def show_report_preview(self, report, report_file=None):
        """显示报告预览（优化版）"""
        preview_dialog = tk.Toplevel(self.root)
        preview_dialog.title("分析报告")
        preview_dialog.geometry("900x700")
        
        frame = ttk.Frame(preview_dialog, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="📊 完整分析报告", 
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        if report_file:
            ttk.Label(title_frame, text=f"已保存: {os.path.basename(report_file)}", 
                     font=('微软雅黑', 9), foreground='green').pack(side=tk.RIGHT)
        
        # 报告内容
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, report)
        text.config(state=tk.DISABLED)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="📁 打开报告目录", 
                  command=lambda: [preview_dialog.destroy(), self.open_reports_folder()],
                  width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📋 复制到剪贴板", 
                  command=lambda: self.copy_to_clipboard(report),
                  width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="关闭", 
                  command=preview_dialog.destroy,
                  style='Primary.TButton', width=15).pack(side=tk.LEFT, padx=5)
    
    def copy_to_clipboard(self, text):
        """复制到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("成功", "报告已复制到剪贴板")
    
    def run_ma_analysis_quick(self):
        """快速均线分析"""
        if not self.config_manager.config.get('holdings') and not self.config_manager.config.get('watchlist'):
            messagebox.showwarning("提示", "请先添加基金再进行分析")
            return
        
        # 直接调用一键分析
        self.one_click_analysis()
    
    # ============= 保留原有功能（兼容性） =============
    
    def add_holding_dialog(self):
        """添加持仓基金对话框"""
        self.quick_add_fund_dialog()
    
    def add_watchlist_dialog(self):
        """添加观察基金对话框"""
        self.quick_add_fund_dialog()
    
    def edit_fund_dialog(self):
        """编辑基金（简化版）"""
        messagebox.showinfo("提示", "请在配置文件中直接修改，或删除后重新添加")
    
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
        type_var = tk.StringVar(value='both')
        ttk.Radiobutton(frame, text="持仓和观察都删", variable=type_var, value='both').grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(frame, text="仅持仓", variable=type_var, value='holding').grid(row=2, column=1, sticky=tk.W)
        ttk.Radiobutton(frame, text="仅观察", variable=type_var, value='watchlist').grid(row=3, column=1, sticky=tk.W)
        
        def on_submit():
            code = code_entry.get().strip()
            if not code:
                messagebox.showerror("错误", "基金代码不能为空")
                return
            
            if messagebox.askyesno("确认", f"确定要删除基金 {code} 吗？"):
                delete_type = type_var.get()
                success = False
                
                if delete_type in ['holding', 'both']:
                    if self.config_manager.remove_fund(code, 'holding'):
                        success = True
                
                if delete_type in ['watchlist', 'both']:
                    if self.config_manager.remove_fund(code, 'watchlist'):
                        success = True
                
                if success:
                    messagebox.showinfo("成功", "删除成功")
                    self.refresh_data()
                    dialog.destroy()
                else:
                    messagebox.showerror("失败", "删除失败，请检查代码是否正确")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
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
            if key == 'purchase_date':
                entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
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
        """批量添加持仓基金"""
        self.batch_import_dialog()
    
    def batch_add_watchlist_dialog(self):
        """批量添加观察基金"""
        self.batch_import_dialog()
    
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
        type_var = tk.StringVar(value='both')
        ttk.Radiobutton(frame, text="持仓和观察都删", variable=type_var, value='both').pack(anchor=tk.W)
        ttk.Radiobutton(frame, text="仅持仓", variable=type_var, value='holding').pack(anchor=tk.W)
        ttk.Radiobutton(frame, text="仅观察", variable=type_var, value='watchlist').pack(anchor=tk.W)
        
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
    
    def open_reports_folder(self):
        """打开报告目录"""
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            messagebox.showinfo("提示", "报告目录已创建，但还没有任何报告。\n请先运行分析。")
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
    
    def run_ma_analysis(self):
        """运行均线分析（兼容旧版）"""
        self.one_click_analysis()
    
    # ============= 清除功能 =============
    
    def clear_holdings(self):
        """清除所有持仓"""
        if messagebox.askyesno("警告", "⚠️ 确定要清除所有持仓基金吗？\n此操作不可恢复！"):
            if self.config_manager.clear_holdings():
                messagebox.showinfo("成功", "已清除所有持仓基金")
                self.refresh_data()
    
    def clear_watchlist(self):
        """清除所有观察"""
        if messagebox.askyesno("警告", "⚠️ 确定要清除所有观察基金吗？\n此操作不可恢复！"):
            if self.config_manager.clear_watchlist():
                messagebox.showinfo("成功", "已清除所有观察基金")
                self.refresh_data()
    
    def clear_all(self):
        """清除所有配置"""
        if messagebox.askyesno("警告", "⚠️⚠️⚠️ 确定要清除所有配置数据吗？\n包括持仓和观察基金！\n此操作不可恢复！"):
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

