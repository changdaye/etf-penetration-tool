# ETF 穿透分析 - JSON API 版本

## 📖 概述

本项目已支持纯 JSON 格式的 ETF 穿透分析，可以通过 API 直接调用，无需前端界面。

## 🚀 快速开始

### 1. 启动后端服务

```bash
cd backend
pip3 install -r requirements.txt
python3 app.py
```

访问 http://localhost:5001 查看 Web 界面

访问 http://localhost:5001/json-api 查看 JSON API 测试页面

---

## 📡 API 接口

### 接口 1：一键式完整分析（推荐）

**POST** `/api/full-json-analysis`

直接上传持仓 JSON，返回完整的穿透分析结果。

#### 请求格式

```json
{
  "positions": [
    {
      "code": "513050",
      "name": "易方达中证海外互联 ETF",
      "holding_amount": 50000.00
    },
    {
      "code": "159915",
      "name": "易方达创业板 ETF",
      "holding_amount": 30000.00
    },
    {
      "code": "510300",
      "name": "华泰柏瑞沪深 300ETF",
      "holding_amount": 40000.00
    }
  ]
}
```

#### 返回格式

```json
{
  "success": true,
  "timestamp": "2024-02-01T10:30:00",
  "input": {
    "etf_count": 3,
    "total_holding_amount": 120000.0
  },
  "output": {
    "basic_info": {
      "penetration_stock_count": 85,
      "total_penetration_amount": 102000.50,
      "coverage_rate": 85.0
    },
    "concentration_analysis": {
      "top50_pct": 65.5,
      "top100_pct": 78.2,
      "top200_pct": 85.1,
      "top500_pct": 92.3
    },
    "industry_distribution": [
      {
        "所属行业": "互联网 - 社交平台",
        "穿透金额": 15000.25,
        "占比": 14.7
      }
    ],
    "top_holdings": [...],
    "all_holdings": [...]
  }
}
```

---

### 接口 2：分步 - 上传 JSON 数据

**POST** `/api/json-upload`

上传 JSON 格式持仓数据，返回识别到的 ETF 列表（不执行穿透分析）。

#### 请求格式

```json
{
  "positions": [
    {
      "code": "513050",
      "name": "易方达中证海外互联 ETF",
      "holding_amount": 50000.00,
      "total_profit": 5000.00,
      "holding_profit": 3000.00
    }
  ],
  "total_holding_amount": 120000.00,
  "total_profit": 4000.00,
  "total_holding_profit": 2300.00
}
```

#### 返回格式

```json
{
  "success": true,
  "message": "JSON 数据解析成功",
  "etf_count": 2,
  "etf_list": [
    {
      "code": "513050",
      "name": "易方达中证海外互联 ETF",
      "amount": 50000,
      "total_profit": 5000,
      "holding_profit": 3000
    }
  ],
  "total_amount": 120000,
  "original_positions_count": 3
}
```

---

### 接口 3：分步 - 分析 ETF 持仓

**POST** `/api/json-analyze`

分析 ETF 持仓，返回 JSON 格式结果。

#### 请求格式

```json
{
  "etf_list": [
    {
      "code": "513050",
      "name": "易方达中证海外互联 ETF",
      "amount": 50000
    }
  ],
  "total_amount": 50000
}
```

#### 返回格式

```json
{
  "success": true,
  "data": {
    "basic_info": {
      "total_amount": 50000,
      "penetration_amount": 42500.25,
      "coverage": 85.0,
      "stock_count": 30
    },
    "concentration": {
      "top50_pct": 68.5,
      "top100_pct": 82.3,
      "top200_pct": 90.1,
      "top500_pct": 95.2
    },
    "industry_distribution": [...],
    "summary": [...],
    "holdings": [...]
  },
  "message": "分析完成"
}
```

---

## 💻 使用示例

### Python 示例

```python
import requests
import json

# 一键式分析（推荐）
positions_data = {
    "positions": [
        {"code": "513050", "name": "易方达中证海外互联 ETF", "holding_amount": 50000},
        {"code": "159915", "name": "易方达创业板 ETF", "holding_amount": 30000}
    ]
}

response = requests.post(
    'http://localhost:5001/api/full-json-analysis',
    json=positions_data
)

result = response.json()
print(json.dumps(result, ensure_ascii=False, indent=2))
```

### curl 示例

```bash
# 一键式分析
curl -X POST http://localhost:5001/api/full-json-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "positions": [
      {"code": "513050", "name": "易方达中证海外互联 ETF", "holding_amount": 50000}
    ]
  }' | jq '.'
```

### JavaScript 示例

```javascript
const positionsData = {
  positions: [
    { code: "513050", name: "易方达中证海外互联 ETF", holding_amount: 50000 }
  ]
};

fetch('http://localhost:5001/api/full-json-analysis', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(positionsData)
})
  .then(res => res.json())
  .then(result => console.log(result));
```

---

## 📊 JSON 数据格式说明

### 输入格式

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| positions | Array | ✅ | 持仓列表 |
| positions[].code | String | ✅ | 股票/ETF 代码 |
| positions[].name | String | ❌ | 名称 |
| positions[].holding_amount | Number | ✅ | 持有金额 |
| positions[].total_profit | Number | ❌ | 累计收益 |
| positions[].holding_profit | Number | ❌ | 持有收益 |
| total_holding_amount | Number | ❌ | 总持仓金额（可选，不填则自动计算） |

### 输出格式（一键式分析）

| 字段 | 类型 | 说明 |
|------|------|------|
| success | Boolean | 是否成功 |
| timestamp | String | 分析时间戳 |
| input | Object | 输入数据汇总 |
| input.etf_count | Number | ETF 数量 |
| input.total_holding_amount | Number | 总持仓金额 |
| output | Object | 分析结果 |
| output.basic_info | Object | 基本信息 |
| output.basic_info.penetration_stock_count | Number | 穿透股票数量 |
| output.basic_info.total_penetration_amount | Number | 总穿透金额 |
| output.basic_info.coverage_rate | Number | 覆盖度（%） |
| output.concentration_analysis | Object | 集中度分析 |
| output.industry_distribution | Array | 行业分布 |
| output.top_holdings | Array | 前 50 大持仓 |
| output.all_holdings | Array | 所有持仓明细 |

---

## 🛠️ 更多示例

运行示例脚本：

```bash
cd backend
python3 api_example.py
```

---

## ⚠️ 注意事项

1. **ETF 识别规则**：代码以 51/15/56 开头
2. **覆盖度说明**：ETF 通常持有 85-95% 股票，剩余为现金
3. **数据时效性**：ETF 持仓数据来自东方财富，可能存在 1-2 季度延迟
4. **行业分类**：基于本地映射（1800+ 只股票），未识别的返回"其他"

---

## 📝 原有功能保留

原有的 Excel 上传功能仍然可用：
- Web 界面：http://localhost:5001
- API：`/api/upload`, `/api/analyze`, `/api/export`

新增的 JSON API 是对原有功能的补充，不会破坏现有功能。

---

## 📄 License

MIT License
