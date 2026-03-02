# ETF 穿透分析工具 / ETF Penetration Analysis Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 📖 项目简介 / Project Overview

**中文**  
ETF 穿透分析工具是一个基于 Web 的应用程序，帮助投资者查看 ETF 基金的底层持仓结构。通过上传持仓 Excel 文件，系统会自动分析每只 ETF 的底层股票持仓，计算穿透后的实际资产分布，并按行业分类统计。

**English**  
ETF Penetration Analysis Tool is a web-based application that helps investors analyze the underlying holdings of ETF funds. By uploading a portfolio Excel file, the system automatically analyzes the underlying stock holdings of each ETF, calculates the penetrated asset distribution, and provides industry classification statistics.

---

## ✨ 核心功能 / Key Features

### 中文
- **ETF 自动识别**：自动识别持仓中的 ETF 基金（支持 51/15/56 开头的代码）
- **持仓穿透计算**：根据 ETF 持仓权重，计算每只底层股票的实际穿透金额
- **行业智能分类**：基于股票名称自动识别所属行业（支持 1800+ 只 A 股/港股/美股）
- **可视化展示**：饼图 + 柱状图展示行业分布和前十大持仓
- **隐私保护**：支持隐藏金额模式，保护敏感财务数据
- **一键导出**：导出完整的穿透分析结果 Excel

### English
- **ETF Auto-Detection**: Automatically identifies ETF funds in portfolio (supports codes starting with 51/15/56)
- **Penetration Calculation**: Calculates actual penetrated amount for each underlying stock based on ETF holdings weight
- **Smart Industry Classification**: Automatically identifies industry based on stock name (supports 1800+ A-share/HK-share/US-share)
- **Visual Display**: Pie chart + Bar chart for industry distribution and top 10 holdings
- **Privacy Protection**: Amount hiding mode to protect sensitive financial data
- **One-Click Export**: Export complete penetration analysis results to Excel

---

## 🚀 快速开始 / Quick Start

### 安装依赖 / Install Dependencies

```bash
# 进入后端目录 / Navigate to backend directory
cd backend

# 安装 Python 依赖 / Install Python dependencies
pip3 install -r requirements.txt
```

### 启动服务 / Start Server

```bash
# 启动 Flask 服务 / Start Flask server
python3 app.py
```

### 访问应用 / Access Application

```
http://localhost:5001
```

---

## 📁 项目结构 / Project Structure

```
etf-penetration-website/
├── backend/
│   ├── app.py                    # Flask 后端 API / Flask Backend API
│   ├── llm_industry.py           # DeepSeek 行业识别（可选） / DeepSeek Industry Recognition (Optional)
│   ├── batch_identify.py         # 批量股票行业识别脚本 / Batch Stock Industry Identification Script
│   ├── requirements.txt          # Python 依赖 / Python Dependencies
│   └── .env                      # 环境变量（API Key） / Environment Variables (API Key)
├── static/
│   ├── css/
│   │   └── style.css            # 样式文件 / Stylesheet
│   └── js/
│       └── app.js               # 前端逻辑 / Frontend Logic
├── templates/
│   └── index.html               # 主页面 / Main Page
├── data/
│   └── industry_map.json        # 股票 - 行业映射 / Stock-Industry Mapping
└── README.md                    # 项目说明 / Project Documentation
```

---

## 📊 使用说明 / Usage Guide

### 1. 上传持仓文件 / Upload Portfolio File

**中文**
1. 点击或拖拽上传持仓 Excel 文件
2. 支持格式：`.xlsx`, `.xls`
3. Excel 需包含列：`代码`、`名称`、`持有金额`


> 💡 **提示**：`汇总持仓_示例.xlsx` 是从 **同花顺投资账本网页端** 直接导出的原始文件，未做任何修改，可以直接使用测试。
> 
> **同花顺投资账本导出步骤**：
> 1. 访问 https://fund.10jqka.com.cn/
> 2. 登录后进入"我的持仓"
> 3. 点击"导出"按钮
> 4. 选择"Excel"格式下载
**English**
1. Click or drag-drop to upload portfolio Excel file
2. Supported formats: `.xlsx`, `.xls`
3. Excel must contain columns: `代码` (Code), `名称` (Name), `持有金额` (Holding Amount)

### 2. 确认 ETF 列表 / Confirm ETF List

**中文**
- 系统自动识别 ETF（51/15/56 开头）
- 显示 ETF 列表和持仓金额
- 点击"开始穿透分析"

**English**
- System automatically identifies ETFs (codes starting with 51/15/56)
- Displays ETF list and holding amounts
- Click "开始穿透分析" (Start Penetration Analysis)

### 3. 查看分析结果 / View Analysis Results

**中文**
- **汇总卡片**：穿透股票数、总穿透金额、覆盖度
- **集中度分析**：Top 50/100/200/500 持仓占比
- **行业分布饼图**：前 10 大行业分布
- **前十大持仓柱状图**：穿透金额最大的 10 只个股
- **持仓表格**：前 500 大底层持仓明细

**English**
- **Summary Cards**: Number of penetrated stocks, total penetrated amount, coverage
- **Concentration Analysis**: Top 50/100/200/500 holdings percentage
- **Industry Pie Chart**: Top 10 industry distribution
- **Top 10 Bar Chart**: Top 10 individual stocks by penetrated amount
- **Holdings Table**: Top 500 underlying holdings details

### 4. 金额显示开关 / Amount Display Toggle

**中文**
- 默认**不显示金额**（保护隐私）
- 点击开关**打开** → 显示所有金额
- 点击开关**关闭** → 显示 `******`

**English**
- Default: **Amounts hidden** (privacy protection)
- Toggle **ON** → Display all amounts
- Toggle **OFF** → Display `******`

### 5. 导出结果 / Export Results

**中文**
- 点击右上角"📥 导出 Excel"按钮
- 下载完整的穿透分析结果

**English**
- Click "📥 导出 Excel" button in top-right corner
- Download complete penetration analysis results

---

## 🗺️ 行业映射 / Industry Mapping

### 中文
系统内置**1800+ 只股票**的行业映射，覆盖：

| 行业大类 | 细分行业示例 | 股票数 |
|---------|------------|--------|
| 医药医疗 | 创新药、CXO、中药、疫苗、医疗器械 | 400+ |
| 互联网科技 | 电商、社交、游戏、本地生活、OTA | 100+ |
| 大消费 | 白酒、啤酒、乳业、调味品、零食 | 150+ |
| 金融 | 银行、证券、保险 | 100+ |
| 新能源 | 电池、光伏、新能源汽车 | 80+ |
| 半导体 | 设计、制造、代工、设备 | 50+ |
| ... | ... | ... |

**智能分类规则**：
- 基于股票名称关键词自动判断
- 例如："药明康德" → 医药-CXO，"腾讯" → 互联网 - 社交平台

### English
System includes **1800+ stocks** industry mapping, covering:

| Industry Category | Sub-Industry Examples | Stock Count |
|------------------|----------------------|-------------|
| Pharmaceutical & Healthcare | Innovative Drugs, CXO, TCM, Vaccines, Medical Devices | 400+ |
| Internet & Technology | E-commerce, Social Media, Gaming, Local Services, OTA | 100+ |
| Consumer | Baijiu, Beer, Dairy, Condiments, Snacks | 150+ |
| Financial | Banking, Securities, Insurance | 100+ |
| New Energy | Battery, Solar, EV | 80+ |
| Semiconductor | Design, Manufacturing, Foundry, Equipment | 50+ |
| ... | ... | ... |

**Smart Classification Rules**:
- Automatically identifies industry based on stock name keywords
- Examples: "药明康德" → Pharma-CXO, "腾讯" → Internet-Social Platform

---

## 🔧 高级功能 / Advanced Features

### DeepSeek 大模型行业识别（可选） / DeepSeek LLM Industry Recognition (Optional)

**中文**
如果遇到本地映射没有的股票，可以使用 DeepSeek 大模型自动识别：

1. 注册 DeepSeek 账号：https://platform.deepseek.com/
2. 获取 API Key
3. 配置环境变量：
   ```bash
   # 编辑 .env 文件 / Edit .env file
   DEEPSEEK_API_KEY=sk-your-api-key-here
   ```
4. 安装依赖：
   ```bash
   pip3 install openai python-dotenv tenacity
   ```
5. 运行批量识别：
   ```bash
   python3 batch_identify.py
   ```

**成本估算**：
- 单次识别：约 ¥0.00024
- 1000 只股票：约 ¥0.24
- 首次识别后保存到本地，后续分析零成本

**English**
For stocks not in local mapping, use DeepSeek LLM for automatic recognition:

1. Register DeepSeek account: https://platform.deepseek.com/
2. Get API Key
3. Configure environment variable:
   ```bash
   # Edit .env file
   DEEPSEEK_API_KEY=sk-your-api-key-here
   ```
4. Install dependencies:
   ```bash
   pip3 install openai python-dotenv tenacity
   ```
5. Run batch identification:
   ```bash
   python3 batch_identify.py
   ```

**Cost Estimate**:
- Single recognition: ~¥0.00024
- 1000 stocks: ~¥0.24
- Saved locally after first recognition, zero cost for subsequent analysis

---

## 📝 API 接口 / API Endpoints

| 接口 / Endpoint | 方法 / Method | 说明 / Description |
|----------------|--------------|-------------------|
| `/api/upload` | POST | 上传持仓文件 / Upload portfolio file |
| `/api/analyze` | POST | 分析 ETF 持仓 / Analyze ETF holdings |
| `/api/export` | POST | 导出结果 / Export results |
| `/api/industry-map` | GET | 获取行业映射 / Get industry mapping |
| `/api/industry-map` | POST | 更新行业映射 / Update industry mapping |

---

## 🛠️ 技术栈 / Tech Stack

### 后端 / Backend
- **Flask** - Python Web 框架 / Python Web Framework
- **Pandas** - 数据处理 / Data Processing
- **AkShare** - 金融数据接口 / Financial Data API
- **OpenAI** - DeepSeek 大模型集成 / DeepSeek LLM Integration

### 前端 / Frontend
- **原生 HTML/CSS/JavaScript** - 无框架依赖 / No Framework Dependencies
- **Chart.js** - 图表库 / Chart Library
- **Chart.js Plugin DataLabels** - 图表标签插件 / Chart Labels Plugin

---

## ⚠️ 注意事项 / Notes

### 中文
1. **ETF 仓位**：ETF 通常持有 85-95% 股票，剩余为现金，因此穿透金额 < 总持仓
2. **数据时效性**：ETF 持仓数据来自东方财富，可能存在 1-2 季度延迟
3. **行业分类**：基于公开信息和股票名称智能判断，可能与实际有偏差
4. **重复计算**：同一只股票可能在多只 ETF 中出现，穿透后会合并计算

### English
1. **ETF Position**: ETFs typically hold 85-95% stocks, rest is cash, so penetrated amount < total holding
2. **Data Timeliness**: ETF holdings data from Eastmoney, may have 1-2 quarters delay
3. **Industry Classification**: Based on public information and smart name analysis, may differ from actual
4. **Duplicate Calculation**: Same stock may appear in multiple ETFs, will be merged after penetration

---

## 📄 许可证 / License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🤝 贡献 / Contributing

欢迎提交 Issue 和 Pull Request！

Issues and Pull Requests are welcome!

---

## 📧 联系方式 / Contact

如有问题或建议，请提交 Issue 或联系作者。

For questions or suggestions, please submit an Issue or contact the author.

---

## 📊 示例截图 / Screenshots

### 上传页面 / Upload Page
（待添加 / TBD）

### 分析结果 / Analysis Results
（待添加 / TBD）

### 金额隐藏模式 / Amount Hidden Mode
（待添加 / TBD）

---

**最后更新 / Last Updated**: 2024 年 2 月 / February 2024
