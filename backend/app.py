#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETF 穿透分析网站 - 后端 API
"""
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import pandas as pd
import akshare as ak
import json
import os
from datetime import datetime
import io
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__, static_folder='../static', template_folder='../templates')
CORS(app)

# 行业映射数据
INDUSTRY_MAP = {}

def load_industry_map():
    """加载行业映射数据"""
    map_file = os.path.join(os.path.dirname(__file__), '../data/industry_map.json')
    if os.path.exists(map_file):
        with open(map_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_industry_map(data):
    """保存行业映射数据"""
    map_file = os.path.join(os.path.dirname(__file__), '../data/industry_map.json')
    with open(map_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 初始化加载行业映射
INDUSTRY_MAP = load_industry_map()
print(f"已加载本地行业映射：{len(INDUSTRY_MAP)} 只股票")

def get_industry(code, name):
    """获取股票所属行业 - 仅从本地映射读取"""
    code = str(code).zfill(6)
    
    # 直接查本地映射
    if code in INDUSTRY_MAP:
        return INDUSTRY_MAP[code]
    
    # 本地没有，返回默认值
    return '其他'

def is_etf(code):
    """判断是否为 ETF"""
    code = str(code).zfill(6)
    return code.startswith(('51', '15', '56', '510', '512', '513', '515', '516', '518'))

def get_etf_holdings(etf_code, year='2024'):
    """获取 ETF 持仓数据"""
    try:
        result = ak.fund_portfolio_hold_em(symbol=etf_code, date=year)
        if len(result) > 0:
            latest_quarter = result['季度'].iloc[-1]
            result = result[result['季度'] == latest_quarter]
            return result, latest_quarter
    except Exception as e:
        print(f"Error getting {etf_code} holdings: {e}")
    return None, None

@app.route('/')
def index():
    """首页"""
    return send_file('../templates/index.html')

@app.route('/json-api')
def json_api():
    """JSON API 测试页面"""
    return send_file('../templates/json-api.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传持仓文件"""
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    try:
        # 读取 Excel
        df = pd.read_excel(file)
        
        # 检测列名
        required_cols = ['代码', '持有金额']
        for col in required_cols:
            if col not in df.columns:
                return jsonify({'error': f'缺少必要列：{col}'}), 400
        
        # 处理数据
        df = df[df['代码'].notna()].copy()
        
        def safe_code(code):
            try:
                return str(int(code)).zfill(6)
            except:
                return str(code).zfill(6)
        
        df['代码'] = df['代码'].apply(safe_code)
        
        # 筛选 ETF
        etf_list = []
        for idx, row in df.iterrows():
            code = row['代码']
            if is_etf(code) and code != '汇总':
                etf_list.append({
                    'code': code,
                    'name': row.get('名称', ''),
                    'amount': float(row.get('持有金额', 0))
                })
        
        total_amount = df[df['代码'] != '汇总']['持有金额'].sum() if '持有金额' in df.columns else 0
        
        return jsonify({
            'success': True,
            'etf_count': len(etf_list),
            'etf_list': etf_list,
            'total_amount': total_amount,
            'columns': df.columns.tolist()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """分析 ETF 持仓"""
    data = request.json
    etf_list = data.get('etf_list', [])
    total_amount = data.get('total_amount', 0)
    
    if not etf_list:
        return jsonify({'error': 'ETF 列表为空'}), 400
    
    all_holdings = []
    progress = 0
    
    for i, etf in enumerate(etf_list, 1):
        progress = int((i / len(etf_list)) * 100)
        
        holdings, quarter = get_etf_holdings(etf['code'], '2024')
        
        if holdings is not None and len(holdings) > 0:
            for _, stock in holdings.iterrows():
                weight = stock.get('占净值比例', 0)
                if pd.notna(weight):
                    weight = float(weight) / 100.0
                else:
                    weight = 0
                
                amount = etf['amount'] * weight
                
                if amount > 0:
                    stock_code = str(stock.get('股票代码', '')).zfill(6)
                    stock_name = stock.get('股票名称', '')
                    industry = get_industry(stock_code, stock_name)
                    
                    all_holdings.append({
                        '股票代码': stock_code,
                        '股票名称': stock_name,
                        '所属行业': industry,
                        '所属 ETF': etf['code'],
                        'ETF 名称': etf['name'],
                        'ETF 持有金额': etf['amount'],
                        '持仓权重': f"{weight*100:.2f}%",
                        '穿透金额': round(amount, 2),
                        '季度': quarter
                    })
    
    if not all_holdings:
        return jsonify({'error': '未获取到任何持仓数据'}), 400
    
    # 转换为 DataFrame
    holdings_df = pd.DataFrame(all_holdings)
    
    # 汇总
    summary = holdings_df.groupby(['股票代码', '股票名称', '所属行业']).agg({
        '穿透金额': 'sum',
        '所属 ETF': 'count',
        'ETF 持有金额': 'sum'
    }).reset_index()
    
    summary = summary.rename(columns={'所属 ETF': 'ETF 数量'})
    summary = summary.sort_values('穿透金额', ascending=False)
    
    # 计算占总持仓比例
    summary['占总持仓%'] = (summary['穿透金额'] / total_amount * 100).round(2)
    
    # 行业分布
    industry_dist = summary.groupby('所属行业')['穿透金额'].sum().sort_values(ascending=False).reset_index()
    industry_dist['占比'] = (industry_dist['穿透金额'] / total_amount * 100).round(2)
    
    # 层级汇总 (基于穿透金额)
    top50 = summary.head(50)['穿透金额'].sum()
    top100 = summary.head(100)['穿透金额'].sum()
    top200 = summary.head(200)['穿透金额'].sum()
    top500 = summary.head(500)['穿透金额'].sum()
    penetration_total = summary['穿透金额'].sum()
    
    # 占比计算基于总持仓 (ETF 金额)
    return jsonify({
        'success': True,
        'progress': 100,
        'total_amount': total_amount,  # ETF 总持仓
        'penetration_amount': penetration_total,  # 穿透后股票总金额
        'coverage': round(penetration_total / total_amount * 100, 1) if total_amount > 0 else 0,
        'stock_count': len(summary),
        'summary': summary.head(500).to_dict('records'),
        'industry_distribution': industry_dist.to_dict('records'),
        'concentration': {
            'top50': round(top50 / total_amount * 100, 1),
            'top100': round(top100 / total_amount * 100, 1),
            'top200': round(top200 / total_amount * 100, 1),
            'top500': round(top500 / total_amount * 100, 1)
        },
        'holdings': holdings_df.to_dict('records')
    })

@app.route('/api/industry-map', methods=['GET'])
def get_industry_map_api():
    """获取行业映射"""
    return jsonify(INDUSTRY_MAP)

@app.route('/api/industry-map', methods=['POST'])
def update_industry_map_api():
    """更新行业映射"""
    global INDUSTRY_MAP
    data = request.json
    code = data.get('code', '').zfill(6)
    industry = data.get('industry', '')
    
    if code and industry:
        INDUSTRY_MAP[code] = industry
        save_industry_map(INDUSTRY_MAP)
        return jsonify({'success': True, 'message': '已更新'})
    
    return jsonify({'error': '参数错误'}), 400

@app.route('/api/export', methods=['POST'])
def export():
    """导出结果"""
    data = request.json
    summary_data = data.get('summary', [])
    
    if not summary_data:
        return jsonify({'error': '数据为空'}), 400
    
    df = pd.DataFrame(summary_data)
    
    # 保存为 Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='汇总', index=False)
    
    output.seek(0)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'ETF 穿透分析_{timestamp}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


# ============== 新增：JSON 数据上传和穿透 API ==============

@app.route('/api/json-upload', methods=['POST'])
def upload_json():
    """
    上传 JSON 格式的持仓数据
    支持的 JSON 格式：
    {
        "positions": [
            {
                "code": "513050",
                "name": "易方达中证海外互联 ETF",
                "holding_amount": 50000.00,
                "total_profit": 5000.00,
                "holding_profit": 3000.00
            },
            ...
        ],
        "total_holding_amount": 120000.00,
        "total_profit": 4000.00,
        "total_holding_profit": 2300.00
    }
    """
    try:
        # 支持 application/json 和 multipart/form-data
        if request.is_json:
            data = request.get_json()
        else:
            # 从 form data 中读取 JSON 字符串
            json_str = request.form.get('json_data') or request.data.decode('utf-8')
            data = json.loads(json_str)
        
        # 验证必要字段
        if 'positions' not in data:
            return jsonify({'error': '缺少 positions 字段'}), 400
        
        positions = data['positions']
        if not isinstance(positions, list) or len(positions) == 0:
            return jsonify({'error': 'positions 必须是非空数组'}), 400
        
        # 验证每个持仓的字段
        required_fields = ['code', 'holding_amount']
        for i, pos in enumerate(positions):
            for field in required_fields:
                if field not in pos:
                    return jsonify({'error': f'第{i+1}个持仓缺少必要字段：{field}'}), 400
        
        # 处理持仓数据，筛选 ETF
        etf_list = []
        total_amount = 0.0
        
        for pos in positions:
            code = str(pos['code']).zfill(6)
            name = pos.get('name', '')
            amount = float(pos.get('holding_amount', 0) or 0)
            
            # 计算总金额（如果是直接传入的 total_holding_amount 则使用它）
            if is_etf(code) and code != '汇总':
                etf_list.append({
                    'code': code,
                    'name': name,
                    'amount': amount,
                    'total_profit': pos.get('total_profit', 0),
                    'holding_profit': pos.get('holding_profit', 0)
                })
        
        # 如果没有指定 total_holding_amount，则从 ETF 列表计算
        if 'total_holding_amount' in data and data['total_holding_amount']:
            total_amount = float(data['total_holding_amount'])
        else:
            total_amount = sum(etf['amount'] for etf in etf_list)
        
        return jsonify({
            'success': True,
            'message': 'JSON 数据解析成功',
            'etf_count': len(etf_list),
            'etf_list': etf_list,
            'total_amount': total_amount,
            'original_positions_count': len(positions)
        })
        
    except json.JSONDecodeError as e:
        return jsonify({'error': f'JSON 格式错误：{str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'解析失败：{str(e)}'}), 500


@app.route('/api/json-analyze', methods=['POST'])
def analyze_json():
    """
    分析 JSON 格式的 ETF 持仓数据，返回 JSON 格式结果
    
    请求格式：
    {
        "etf_list": [
            {"code": "513050", "name": "易方达中证海外互联 ETF", "amount": 50000},
            ...
        ],
        "total_amount": 120000
    }
    
    返回格式：
    {
        "success": true,
        "data": {
            "summary": {...},
            "industry_distribution": [...],
            "concentration": {...},
            "holdings": [...]
        }
    }
    """
    try:
        # 支持多种输入方式
        if request.is_json:
            data = request.get_json()
        else:
            json_str = request.form.get('json_data') or request.data.decode('utf-8')
            data = json.loads(json_str)
        
        etf_list = data.get('etf_list', [])
        total_amount = data.get('total_amount', 0)
        
        if not etf_list:
            return jsonify({'success': False, 'error': 'ETF 列表为空'}), 400
        
        all_holdings = []
        
        for i, etf in enumerate(etf_list, 1):
            holdings, quarter = get_etf_holdings(etf['code'], '2024')
            
            if holdings is not None and len(holdings) > 0:
                for _, stock in holdings.iterrows():
                    weight = stock.get('占净值比例', 0)
                    if pd.notna(weight):
                        weight = float(weight) / 100.0
                    else:
                        weight = 0
                    
                    amount = etf['amount'] * weight
                    
                    if amount > 0:
                        stock_code = str(stock.get('股票代码', '')).zfill(6)
                        stock_name = stock.get('股票名称', '')
                        industry = get_industry(stock_code, stock_name)
                        
                        all_holdings.append({
                            '股票代码': stock_code,
                            '股票名称': stock_name,
                            '所属行业': industry,
                            '所属 ETF': etf['code'],
                            'ETF 名称': etf.get('name', ''),
                            'ETF 持有金额': etf['amount'],
                            '持仓权重': f"{weight*100:.2f}%",
                            '穿透金额': round(amount, 2),
                            '季度': quarter
                        })
        
        if not all_holdings:
            return jsonify({'success': False, 'error': '未获取到任何持仓数据'}), 400
        
        # 转换为 DataFrame
        holdings_df = pd.DataFrame(all_holdings)
        
        # 汇总
        summary = holdings_df.groupby(['股票代码', '股票名称', '所属行业']).agg({
            '穿透金额': 'sum',
            '所属 ETF': 'count',
            'ETF 持有金额': 'sum'
        }).reset_index()
        
        summary = summary.rename(columns={'所属 ETF': 'ETF 数量'})
        summary = summary.sort_values('穿透金额', ascending=False)
        summary['占总持仓%'] = (summary['穿透金额'] / total_amount * 100).round(2)
        
        # 行业分布
        industry_dist = summary.groupby('所属行业')['穿透金额'].sum().sort_values(ascending=False).reset_index()
        industry_dist['占比'] = (industry_dist['穿透金额'] / total_amount * 100).round(2)
        
        # 集中度分析
        top50 = summary.head(50)['穿透金额'].sum()
        top100 = summary.head(100)['穿透金额'].sum()
        top200 = summary.head(200)['穿透金额'].sum()
        top500 = summary.head(500)['穿透金额'].sum()
        penetration_total = summary['穿透金额'].sum()
        
        # 构建返回结果
        result = {
            'success': True,
            'data': {
                'basic_info': {
                    'total_amount': total_amount,
                    'penetration_amount': round(penetration_total, 2),
                    'coverage': round(penetration_total / total_amount * 100, 1) if total_amount > 0 else 0,
                    'stock_count': len(summary)
                },
                'concentration': {
                    'top50_pct': round(top50 / total_amount * 100, 1),
                    'top100_pct': round(top100 / total_amount * 100, 1),
                    'top200_pct': round(top200 / total_amount * 100, 1),
                    'top500_pct': round(top500 / total_amount * 100, 1)
                },
                'industry_distribution': industry_dist.to_dict('records'),
                'summary': summary.head(500).to_dict('records'),
                'holdings': holdings_df.to_dict('records')
            },
            'message': '分析完成'
        }
        
        return jsonify(result)
        
    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'error': f'JSON 格式错误：{str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'分析失败：{str(e)}'}), 500


@app.route('/api/full-json-analysis', methods=['POST'])
def full_json_analysis():
    """
    一键式完整分析：直接上传持仓 JSON，返回穿透分析结果
    合并了 upload 和 analyze 两个步骤
    
    请求格式：
    {
        "positions": [
            {"code": "513050", "name": "xxx", "holding_amount": 50000, ...},
            ...
        ]
    }
    
    返回格式：完整的穿透分析结果 JSON
    """
    try:
        # 解析输入 JSON
        if request.is_json:
            data = request.get_json()
        else:
            json_str = request.form.get('json_data') or request.data.decode('utf-8')
            data = json.loads(json_str)
        
        positions = data.get('positions', [])
        if not positions:
            return jsonify({'success': False, 'error': 'positions 为空'}), 400
        
        # 筛选 ETF
        etf_list = []
        total_amount = data.get('total_holding_amount', 0)
        
        for pos in positions:
            code = str(pos['code']).zfill(6)
            if is_etf(code) and code != '汇总':
                amount = float(pos.get('holding_amount', 0) or 0)
                etf_list.append({
                    'code': code,
                    'name': pos.get('name', ''),
                    'amount': amount
                })
        
        if not total_amount and etf_list:
            total_amount = sum(etf['amount'] for etf in etf_list)
        
        if not etf_list:
            return jsonify({'success': False, 'error': '未找到 ETF 持仓'}), 400
        
        # 执行穿透分析
        all_holdings = []
        
        for etf in etf_list:
            holdings, quarter = get_etf_holdings(etf['code'], '2024')
            
            if holdings is not None and len(holdings) > 0:
                for _, stock in holdings.iterrows():
                    weight = stock.get('占净值比例', 0)
                    if pd.notna(weight):
                        weight = float(weight) / 100.0
                    else:
                        weight = 0
                    
                    amount = etf['amount'] * weight
                    
                    if amount > 0:
                        stock_code = str(stock.get('股票代码', '')).zfill(6)
                        stock_name = stock.get('股票名称', '')
                        industry = get_industry(stock_code, stock_name)
                        
                        all_holdings.append({
                            '股票代码': stock_code,
                            '股票名称': stock_name,
                            '所属行业': industry,
                            '所属 ETF': etf['code'],
                            'ETF 名称': etf['name'],
                            'ETF 持有金额': etf['amount'],
                            '持仓权重': f"{weight*100:.2f}%",
                            '穿透金额': round(amount, 2),
                            '季度': quarter
                        })
        
        if not all_holdings:
            return jsonify({'success': False, 'error': '未获取到任何持仓数据'}), 400
        
        holdings_df = pd.DataFrame(all_holdings)
        
        # 汇总统计
        summary = holdings_df.groupby(['股票代码', '股票名称', '所属行业']).agg({
            '穿透金额': 'sum',
            '所属 ETF': 'count',
            'ETF 持有金额': 'sum'
        }).reset_index()
        summary = summary.rename(columns={'所属 ETF': 'ETF 数量'})
        summary = summary.sort_values('穿透金额', ascending=False)
        summary['占总持仓%'] = (summary['穿透金额'] / total_amount * 100).round(2)
        
        industry_dist = summary.groupby('所属行业')['穿透金额'].sum().sort_values(ascending=False).reset_index()
        industry_dist['占比'] = (industry_dist['穿透金额'] / total_amount * 100).round(2)
        
        penetration_total = summary['穿透金额'].sum()
        
        # 构建完整返回结果
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'input': {
                'etf_count': len(etf_list),
                'total_holding_amount': total_amount
            },
            'output': {
                'basic_info': {
                    'penetration_stock_count': len(summary),
                    'total_penetration_amount': round(penetration_total, 2),
                    'coverage_rate': round(penetration_total / total_amount * 100, 1) if total_amount > 0 else 0
                },
                'concentration_analysis': {
                    'top50_pct': round(summary.head(50)['穿透金额'].sum() / total_amount * 100, 1),
                    'top100_pct': round(summary.head(100)['穿透金额'].sum() / total_amount * 100, 1),
                    'top200_pct': round(summary.head(200)['穿透金额'].sum() / total_amount * 100, 1),
                    'top500_pct': round(summary.head(500)['穿透金额'].sum() / total_amount * 100, 1)
                },
                'industry_distribution': industry_dist.to_dict('records'),
                'top_holdings': summary.head(50).to_dict('records'),
                'all_holdings': holdings_df.to_dict('records')
            }
        }
        
        return jsonify(result)
        
    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'error': f'JSON 格式错误：{str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'分析失败：{str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=18080)
