#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETF 穿透分析 API 使用示例
演示如何使用 JSON 格式进行穿透分析
"""
import requests
import json

# API 基础 URL
BASE_URL = 'http://localhost:5001'


def example_upload_json():
    """示例 1：上传 JSON 持仓数据"""
    
    # 持仓数据（可以包含股票和 ETF）
    positions_data = {
        "positions": [
            {
                "code": "513050",
                "name": "易方达中证海外互联 ETF",
                "holding_amount": 50000.00,
                "total_profit": 5000.00,
                "holding_profit": 3000.00
            },
            {
                "code": "159915",
                "name": "易方达创业板 ETF",
                "holding_amount": 30000.00,
                "total_profit": -2000.00,
                "holding_profit": -1500.00
            },
            {
                "code": "510300",
                "name": "华泰柏瑞沪深 300ETF",
                "holding_amount": 40000.00,
                "total_profit": 1000.00,
                "holding_profit": 800.00
            },
            {
                "code": "00700",
                "name": "腾讯控股",
                "holding_amount": 20000.00,
                "total_profit": 5000.00,
                "holding_profit": 4000.00
            }
        ],
        "total_holding_amount": 140000.00,
        "total_profit": 9000.00,
        "total_holding_profit": 6300.00
    }
    
    # 方法 1：直接发送 JSON
    response = requests.post(
        f'{BASE_URL}/api/json-upload',
        json=positions_data
    )
    
    print("=" * 60)
    print("示例 1：上传 JSON 持仓数据")
    print("=" * 60)
    print(f"状态码：{response.status_code}")
    print(f"返回结果：{json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    print()
    
    return response.json()


def example_analyze_json(etf_list, total_amount):
    """示例 2：分析 ETF 持仓（返回 JSON）"""
    
    analyze_data = {
        "etf_list": etf_list,
        "total_amount": total_amount
    }
    
    response = requests.post(
        f'{BASE_URL}/api/json-analyze',
        json=analyze_data
    )
    
    print("=" * 60)
    print("示例 2：分析 ETF 持仓（JSON 返回）")
    print("=" * 60)
    print(f"状态码：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"分析成功！")
        print(f"穿透股票数：{result['data']['basic_info']['stock_count']}")
        print(f"总穿透金额：¥{result['data']['basic_info']['penetration_amount']:,.2f}")
        print(f"覆盖度：{result['data']['basic_info']['coverage']}%")
        print(f"\n前 5 大行业分布:")
        for i, ind in enumerate(result['data']['industry_distribution'][:5], 1):
            print(f"  {i}. {ind['所属行业']}: ¥{ind['穿透金额']:,.2f} ({ind['占比']}%)")
    else:
        print(f"分析失败：{response.json()}")
    print()
    
    return response.json()


def example_full_analysis():
    """示例 3：一键式完整分析（推荐）"""
    
    positions_data = {
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
    
    response = requests.post(
        f'{BASE_URL}/api/full-json-analysis',
        json=positions_data
    )
    
    print("=" * 60)
    print("示例 3：一键式完整分析（推荐）")
    print("=" * 60)
    print(f"状态码：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n时间戳：{result['timestamp']}")
        print(f"输入 ETF 数量：{result['input']['etf_count']}")
        print(f"总持仓金额：¥{result['input']['total_holding_amount']:,.2f}")
        print(f"\n输出结果:")
        print(f"  穿透股票数：{result['output']['basic_info']['penetration_stock_count']}")
        print(f"  总穿透金额：¥{result['output']['basic_info']['total_penetration_amount']:,.2f}")
        print(f"  覆盖度：{result['output']['basic_info']['coverage_rate']}%")
        print(f"\n集中度分析:")
        print(f"  Top 50: {result['output']['concentration_analysis']['top50_pct']}%")
        print(f"  Top 100: {result['output']['concentration_analysis']['top100_pct']}%")
        print(f"\n前 3 大行业:")
        for ind in result['output']['industry_distribution'][:3]:
            print(f"  - {ind['所属行业']}: {ind['占比']}%")
        
        # 保存完整结果到文件
        with open('../data/analysis_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n完整结果已保存到：../data/analysis_result.json")
    else:
        print(f"分析失败：{response.json()}")
    print()
    
    return response.json()


def example_curl_examples():
    """示例 4：curl 命令示例"""
    
    print("=" * 60)
    print("示例 4：curl 命令示例")
    print("=" * 60)
    print("""
# 1. 上传 JSON 持仓数据
curl -X POST http://localhost:5001/api/json-upload \\
  -H "Content-Type: application/json" \\
  -d '{
    "positions": [
      {"code": "513050", "name": "易方达中证海外互联 ETF", "holding_amount": 50000}
    ]
  }'

# 2. 分析 ETF 持仓
curl -X POST http://localhost:5001/api/json-analyze \\
  -H "Content-Type: application/json" \\
  -d '{
    "etf_list": [
      {"code": "513050", "name": "易方达中证海外互联 ETF", "amount": 50000}
    ],
    "total_amount": 50000
  }'

# 3. 一键式完整分析（推荐）
curl -X POST http://localhost:5001/api/full-json-analysis \\
  -H "Content-Type: application/json" \\
  -d '{
    "positions": [
      {"code": "513050", "name": "易方达中证海外互联 ETF", "holding_amount": 50000},
      {"code": "159915", "name": "易方达创业板 ETF", "holding_amount": 30000}
    ]
  }' | jq '.'
    """)


if __name__ == '__main__':
    print("ETF 穿透分析 API 使用示例")
    print("请确保后端服务已启动：python3 app.py\n")
    
    try:
        # 示例 1：上传 JSON
        upload_result = example_upload_json()
        
        if upload_result.get('success'):
            # 示例 2：分析
            etf_list = upload_result['etf_list']
            total_amount = upload_result['total_amount']
            analyze_result = example_analyze_json(etf_list, total_amount)
            
            # 示例 3：一键式分析
            example_full_analysis()
        
        # 示例 4：curl 命令
        example_curl_examples()
        
    except requests.exceptions.ConnectionError:
        print("错误：无法连接到服务器")
        print(f"请确保后端服务已启动：python3 {BASE_URL}/app.py")
    except Exception as e:
        print(f"发生错误：{e}")
