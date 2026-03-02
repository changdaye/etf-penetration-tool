#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量使用 DeepSeek 识别所有持仓股票的行业
读取汇总持仓 Excel，提取所有 ETF 的底层股票，批量调用 LLM 识别
"""
import pandas as pd
import akshare as ak
import json
import os
from datetime import datetime
from llm_industry import get_industry_by_llm

def get_all_stocks_from_etf(etf_code):
    """获取 ETF 的所有持仓股票"""
    try:
        result = ak.fund_portfolio_hold_em(symbol=etf_code, date='2024')
        if len(result) > 0:
            latest_quarter = result['季度'].iloc[-1]
            result = result[result['季度'] == latest_quarter]
            stocks = []
            for _, row in result.iterrows():
                stocks.append({
                    'code': str(row['股票代码']).zfill(6),
                    'name': row['股票名称']
                })
            return stocks
    except Exception as e:
        print(f"获取 {etf_code} 持仓失败：{e}")
    return []

def main():
    print("=" * 80)
    print("批量股票行业识别工具")
    print("=" * 80)
    
    # 1. 读取持仓 Excel
    excel_file = '../../汇总持仓.xlsx'
    if not os.path.exists(excel_file):
        print(f"错误：文件不存在 {excel_file}")
        return
    
    print(f"\n读取持仓文件：{excel_file}")
    df = pd.read_excel(excel_file)
    
    # 2. 筛选 ETF
    etf_list = []
    for idx, row in df.iterrows():
        code = str(row['代码']).zfill(6) if pd.notna(row['代码']) else ''
        if code.startswith(('51', '15', '56')) and code != '汇总':
            etf_list.append(code)
    
    print(f"识别到 {len(etf_list)} 只 ETF")
    
    # 3. 获取所有股票
    all_stocks_dict = {}
    print(f"\n开始获取 ETF 持仓股票...")
    
    for i, etf_code in enumerate(etf_list, 1):
        print(f"[{i}/{len(etf_list)}] 获取 {etf_code} 的持仓...", end=' ')
        stocks = get_all_stocks_from_etf(etf_code)
        for stock in stocks:
            all_stocks_dict[stock['code']] = stock['name']
        print(f"获取到 {len(stocks)} 只股票")
    
    print(f"\n总共获取到 {len(all_stocks_dict)} 只不同的股票")
    
    # 4. 加载已有的映射（如果有）
    industry_map_file = 'industry_map.json'
    if os.path.exists(industry_map_file):
        with open(industry_map_file, 'r', encoding='utf-8') as f:
            industry_map = json.load(f)
    else:
        industry_map = {}
    
    # 5. 批量识别
    print(f"\n开始批量识别行业...")
    print(f"已有映射：{len(industry_map)} 只")
    print(f"待识别：{len(all_stocks_dict) - len(industry_map)} 只")
    
    unknown_stocks = []
    for code, name in all_stocks_dict.items():
        if code not in industry_map:
            unknown_stocks.append({'code': code, 'name': name})
    
    if not unknown_stocks:
        print("\n所有股票都已有映射，无需识别！")
        return
    
    print(f"\n需要识别 {len(unknown_stocks)} 只股票...\n")
    
    # 6. 调用 LLM 识别
    new_count = 0
    for i, stock in enumerate(unknown_stocks, 1):
        code = stock['code']
        name = stock['name']
        
        industry = get_industry_by_llm(code, name)
        
        if industry and industry != '其他':
            industry_map[code] = industry
            new_count += 1
            print(f"[{i}/{len(unknown_stocks)}] {code} - {name} -> {industry} ✅")
        else:
            print(f"[{i}/{len(unknown_stocks)}] {code} - {name} -> 其他 ❌")
        
        # 每识别 10 只保存一次，防止意外丢失
        if i % 10 == 0:
            with open(industry_map_file, 'w', encoding='utf-8') as f:
                json.dump(industry_map, f, ensure_ascii=False, indent=2)
            print(f"  -> 已保存进度 ({len(industry_map)} 只)")
    
    # 7. 最终保存
    with open(industry_map_file, 'w', encoding='utf-8') as f:
        json.dump(industry_map, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("批量识别完成！")
    print("=" * 80)
    print(f"\n统计信息:")
    print(f"  总股票数：{len(all_stocks_dict)}")
    print(f"  已有映射：{len(industry_map) - new_count}")
    print(f"  新识别：{new_count}")
    print(f"  已保存：{len(industry_map)}")
    print(f"\n保存位置：{os.path.abspath(industry_map_file)}")

if __name__ == '__main__':
    main()
