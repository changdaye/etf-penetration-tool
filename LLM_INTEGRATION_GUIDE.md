# ETF 穿透分析 - 大模型行业分类集成指南

## 方案概述

使用大模型（如 DeepSeek、文心一言、Kimi 等）自动识别股票所属行业，避免手动维护映射关系。

---

## 方案一：调用国内大模型 API（推荐）

### 1. 准备工作

#### 申请 API Key
- **DeepSeek**: https://platform.deepseek.com/ （免费额度充足）
- **文心一言**: https://cloud.baidu.com/product/wenxinworkshop
- **Kimi 月之暗面**: https://platform.moonshot.cn/
- **通义千问**: https://dashscope.aliyun.com/

#### 推荐选择 DeepSeek
- 免费注册送 ¥10 额度
- API 兼容 OpenAI 格式
- 中文理解能力强
- 响应速度快

### 2. 后端集成

创建文件：`backend/llm_industry.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用大模型识别股票所属行业
"""
from openai import OpenAI
import json
import os

# DeepSeek 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'your-api-key-here')
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)

# 行业分类提示词
PROMPT_TEMPLATE = """
请判断以下股票所属的行业分类。

股票信息：
- 代码：{code}
- 名称：{name}

请从以下行业分类中选择最合适的一个：
互联网、电子商务、社交平台、本地生活、在线旅游、在线教育、在线医疗、
金融科技、游戏、短视频、搜索、广告、软件服务、
消费电子、手机、电脑、光学、半导体、芯片设计、芯片制造、芯片设备、
新能源汽车、电池、光伏、风电、储能、
医药、创新药、中药、生物制药、CXO、医疗器械、医疗服务、疫苗、
食品饮料、白酒、啤酒、饮料、食品、乳业、调味品、
金融、银行、证券、保险、房地产、
通信、运营商、设备、
能源、石油、煤炭、天然气、
有色金属、铜、铝、黄金、
农业、养殖、种植、饲料、
家电、白电、黑电、小家电、
工业、机械、化工、建材、
运输、航运、物流、

只需要返回行业名称，不要其他内容。
"""

def get_industry_by_llm(code: str, name: str) -> str:
    """
    使用大模型识别股票行业
    """
    try:
        prompt = PROMPT_TEMPLATE.format(code=code, name=name)
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的股票行业分类助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=50
        )
        
        industry = response.choices[0].message.content.strip()
        return industry
    
    except Exception as e:
        print(f"LLM 识别失败：{e}")
        return "其他"

def batch_get_industry(stock_list: list) -> dict:
    """
    批量识别股票行业
    
    Args:
        stock_list: [{'code': '00700', 'name': '腾讯控股'}, ...]
    
    Returns:
        {'00700': '互联网 - 社交平台', ...}
    """
    results = {}
    
    for stock in stock_list:
        code = stock['code']
        name = stock['name']
        
        industry = get_industry_by_llm(code, name)
        results[code] = industry
        
        print(f"{code} - {name} -> {industry}")
    
    return results

if __name__ == '__main__':
    # 测试
    test_stocks = [
        {'code': '00700', 'name': '腾讯控股'},
        {'code': '600519', 'name': '贵州茅台'},
        {'code': '300760', 'name': '迈瑞医疗'},
    ]
    
    results = batch_get_industry(test_stocks)
    print(json.dumps(results, ensure_ascii=False, indent=2))
```

### 3. 修改后端 API

修改 `backend/app.py`，在分析时调用大模型：

```python
from llm_industry import get_industry_by_llm

# 在 get_industry 函数中添加 LLM  fallback
def get_industry(code, name):
    """获取股票所属行业"""
    code = str(code).zfill(6)
    
    # 1. 先查本地映射
    if code in INDUSTRY_MAP:
        return INDUSTRY_MAP[code]
    
    # 2. 本地没有，调用 LLM 识别
    print(f"本地映射未找到 {code} - {name}，调用 LLM 识别...")
    industry = get_industry_by_llm(code, name)
    
    # 3. 保存到本地映射
    if industry and industry != '其他':
        INDUSTRY_MAP[code] = industry
        save_industry_map(INDUSTRY_MAP)
    
    return industry
```

### 4. 配置环境变量

创建文件：`backend/.env`

```bash
DEEPSEEK_API_KEY=sk-your-api-key-here
```

### 5. 安装依赖

修改 `requirements.txt`：

```txt
flask==3.0.0
flask-cors==4.0.0
pandas==2.1.4
akshare==1.18.30
openpyxl==3.1.2
xlsxwriter==3.1.9
openai==1.12.0
python-dotenv==1.0.0
```

安装：
```bash
pip3 install -r requirements.txt
```

---

## 方案二：离线批量预处理（省钱方案）

如果你已经有很多股票需要识别，可以离线批量处理。

### 1. 导出未映射的股票列表

```python
# 脚本：scripts/export_unknown_stocks.py
import pandas as pd
import json

# 读取已有的行业映射
with open('../data/industry_map.json', 'r') as f:
    known_map = json.load(f)

# 读取历史分析结果中的股票
df = pd.read_excel('../data/analysis_history.xlsx')
unknown_stocks = df[~df['股票代码'].isin(known_map.keys())][['股票代码', '股票名称']].drop_duplicates()

# 导出为 CSV
unknown_stocks.to_csv('unknown_stocks.csv', index=False)
print(f"导出 {len(unknown_stocks)} 只未映射股票")
```

### 2. 批量调用大模型

```python
# 脚本：scripts/batch_classify.py
import pandas as pd
import json
from llm_industry import get_industry_by_llm

# 读取未知股票
df = pd.read_csv('unknown_stocks.csv')

results = {}
for idx, row in df.iterrows():
    code = str(row['股票代码']).zfill(6)
    name = row['股票名称']
    
    industry = get_industry_by_llm(code, name)
    results[code] = industry
    
    print(f"[{idx+1}/{len(df)}] {code} - {name} -> {industry}")

# 合并到已有映射
with open('../data/industry_map.json', 'r') as f:
    existing_map = json.load(f)

existing_map.update(results)

with open('../data/industry_map.json', 'w') as f:
    json.dump(existing_map, f, ensure_ascii=False, indent=2)

print(f"\n已保存 {len(results)} 条新映射")
```

### 3. 使用建议

- **首次运行**：批量预处理历史数据（约 1000 只股票）
- **日常使用**：遇到新股票时自动调用 LLM
- **定期清理**：每月运行一次批量脚本，更新映射库

---

## 成本估算

### DeepSeek 价格（2024 年）
- 输入：¥1 / 百万 tokens
- 输出：¥2 / 百万 tokens

### 单次识别成本
- Prompt: ~200 tokens
- Response: ~20 tokens
- 单次成本：约 ¥0.00024

### 1000 只股票成本
- 总成本：约 ¥0.24
- 首次映射后永久使用

**结论**：成本极低，可以忽略不计！

---

## 最佳实践

### 1. 混合策略（推荐）

```python
def get_industry(code, name):
    # 优先级 1: 本地缓存
    if code in INDUSTRY_MAP:
        return INDUSTRY_MAP[code]
    
    # 优先级 2: LLM 识别
    industry = get_industry_by_llm(code, name)
    
    # 优先级 3: 保存结果
    if industry and industry != '其他':
        INDUSTRY_MAP[code] = industry
        save_industry_map(INDUSTRY_MAP)
    
    return industry
```

### 2. 错误处理

```python
# 添加重试机制
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def get_industry_by_llm(code, name):
    # ... LLM 调用代码
```

### 3. 缓存优化

```python
# 使用 Redis 或 SQLite 缓存
import sqlite3

def cache_industry(code, industry):
    conn = sqlite3.connect('industry_cache.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR REPLACE INTO industry_map (code, industry, created_at) VALUES (?, ?, datetime("now"))',
        (code, industry)
    )
    conn.commit()
    conn.close()
```

---

## 快速开始

### 1. 注册 DeepSeek
https://platform.deepseek.com/

### 2. 获取 API Key
登录后在控制台创建 API Key

### 3. 配置环境变量
```bash
export DEEPSEEK_API_KEY=sk-your-key-here
```

### 4. 测试
```bash
cd backend
python3 llm_industry.py
```

### 5. 重启网站
```bash
python3 app.py
```

---

## 总结

| 方案 | 优点 | 缺点 | 推荐场景 |
|------|------|------|----------|
| **实时调用** | 无需维护映射 | 需要网络 | 新用户、少量股票 |
| **批量预处理** | 离线可用、速度快 | 需要一次性处理 | 已有大量数据 |
| **混合策略** | 最佳体验 | 需要简单配置 | ⭐ 推荐 |

**建议**：先实时调用，积累一定数据后批量预处理更新映射库。
