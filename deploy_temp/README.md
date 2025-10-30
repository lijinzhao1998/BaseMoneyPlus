# 基金管家系统

一个自动化的基金收益管理系统，能够每日监控你的基金持仓，计算收益，分析趋势，预测未来走势，并通过微信、企业微信或钉钉发送报告。

## ⚡ 快速开始

**重要提示：** 在 Windows 上，请使用 `py` 命令而不是 `python` 命令运行脚本。

```bash
# 运行测试脚本
py test.py

# 运行主程序
py main.py

# 或直接双击
run.bat
```

## 功能特性

✨ **核心功能**
- 📊 实时获取基金净值数据
- 💰 自动计算收益和涨跌幅
- 📈 技术分析（移动平均、趋势判断）
- 🔮 未来趋势预测（机器学习算法）
- 📱 多平台消息推送（微信、企业微信、钉钉）
- ⏰ 定时任务自动发送报告

## 基金列表

系统默认监控以下基金：
- 017811
- 002963
- 020640
- 002112
- 021095

## 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd BaseMoneyPlus
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置

编辑 `config.py` 文件，配置以下内容：

- **基金代码和持仓信息**：修改 `FUND_CODES` 和持仓金额
- **定时任务时间**：修改 `SCHEDULE_TIME`
- **消息推送配置**：配置推送服务的KEY

或者创建 `.env` 文件：

```env
# 服务器酱（微信推送）
SERVER_CHAN_KEY=your_server_chan_key

# 企业微信Webhook
WECHAT_WEBHOOK=your_wechat_webhook

# 钉钉Webhook
DINGTALK_WEBHOOK=your_dingtalk_webhook
```

### 4. 配置消息推送

#### 微信推送（Server酱）
1. 访问 http://sc.ftqq.com/3.version
2. 使用GitHub账号登录
3. 获取SCKEY
4. 在 `.env` 中配置 `SERVER_CHAN_KEY`

#### 企业微信推送
1. 在企业微信中创建群聊
2. 添加群机器人
3. 获取Webhook地址
4. 在 `.env` 中配置 `WECHAT_WEBHOOK`

#### 钉钉推送
1. 在钉钉中创建群聊
2. 添加自定义机器人
3. 获取Webhook地址
4. 在 `.env` 中配置 `DINGTALK_WEBHOOK`

## 使用方法

### 运行测试

```bash
py test.py
# 或者
python test.py  # 如果在Linux/Mac上
```

### 立即运行一次

```bash
py main.py
# 选择选项 1
```

### 启动定时任务（守护进程）

**方式一：使用主程序**
```bash
py main.py
# 选择选项 2
```

**方式二：使用守护进程管理脚本（推荐）**
```bash
# 启动守护进程
py daemon.py start

# 查看守护进程状态
py daemon.py status

# 停止守护进程
py daemon.py stop

# 重启守护进程
py daemon.py restart

# 查看帮助
py daemon.py help
```

程序将在后台运行，每天定时发送报告（默认 21:40）。

## 报告内容

每日报告包含以下信息：

- 📊 **当日涨跌**：今日净值涨跌幅
- 💰 **当日收益**：今日收益金额
- 📈 **累计收益**：总收益金额和收益率
- 📉 **趋势分析**：上涨/下跌/震荡趋势
- 🔮 **未来预测**：未来5天的净值预测

## 项目结构

```
BaseMoneyPlus/
├── main.py              # 主程序
├── daemon.py            # 守护进程管理脚本
├── config.py            # 配置文件
├── fund_data.py         # 基金数据获取模块
├── fund_analyzer.py     # 分析和预测模块
├── message_sender.py    # 消息推送模块
├── test.py              # 测试脚本
├── requirements.txt     # 依赖列表
├── README.md            # 说明文档
├── .env                 # 环境变量（需自行创建）
└── fund_manager.pid     # PID 文件（自动生成）
```

## 配置说明

### 修改持仓信息

在 `main.py` 中修改 `holdings` 字典：

```python
self.holdings = {
    "017811": {"cost_basis": 1.0, "amount": 10000},  # cost_basis: 成本净值, amount: 投资金额
    "002963": {"cost_basis": 1.5, "amount": 10000},
    # ...
}
```

### 修改定时时间

在 `config.py` 中修改：

```python
SCHEDULE_TIME = "21:40"  # 每天21:40发送报告
```

## 守护进程管理

系统支持守护进程模式，可以后台运行并自动管理进程状态。

### 功能特点

- ✅ **进程状态检测**：启动时自动检测守护进程是否已在运行
- ✅ **PID 文件管理**：自动创建和管理进程 PID 文件
- ✅ **优雅关闭**：支持 Ctrl+C 安全退出，自动清理 PID 文件
- ✅ **进程管理**：支持启动、停止、重启和状态查看

### 使用示例

```bash
# 查看守护进程状态
py daemon.py status

# 启动守护进程（如果已有进程运行会提示）
py daemon.py start

# 停止守护进程
py daemon.py stop

# 重启守护进程（先停止再启动）
py daemon.py restart
```

### 在主程序中管理守护进程

运行 `main.py` 时，程序会自动显示守护进程状态：

```
============================================================
基金管家系统
============================================================

🟢 守护进程运行中 (PID: 12345)     # 或 🔴 守护进程未运行

选择运行模式：
1. 立即运行一次（生成并发送报告）
2. 启动/重启定时任务（后台运行）
3. 停止守护进程
4. 退出
============================================================
```

## 依赖说明

主要依赖：
- `requests`：HTTP请求
- `pandas`：数据处理
- `numpy`：数值计算
- `scikit-learn`：机器学习
- `beautifulsoup4`：网页解析
- `schedule`：定时任务

## 注意事项

⚠️ **重要提示**
1. 基金数据来源于公开API，可能存在延迟
2. 预测结果仅供参考，不构成投资建议
3. 投资有风险，入市需谨慎
4. 建议将程序部署在服务器上24小时运行

## 常见问题

**Q: 为什么获取不到基金数据？**
A: 检查网络连接，API可能有限流，建议添加延迟。

**Q: 预测准确吗？**
A: 预测仅供参考，基于历史数据和简单的机器学习模型，不能保证准确。

**Q: 如何添加更多基金？**
A: 在 `config.py` 的 `FUND_CODES` 列表中添加基金代码，并在 `main.py` 的 `holdings` 中配置持仓信息。

## 免责声明

本项目仅供学习和参考使用，不构成任何投资建议。投资有风险，入市需谨慎。

## License

MIT License
