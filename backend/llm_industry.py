#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 DeepSeek 大模型识别股票所属行业
"""
from openai import OpenAI
import os
import json
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# DeepSeek 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'

if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY 环境变量未设置，请在 .env 文件中配置")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)

# 行业分类体系
INDUSTRY_CATEGORIES = """
互联网科技：互联网 - 社交平台、互联网 - 电商、互联网 - 本地生活、互联网 - OTA、互联网 - 搜索、互联网 - 游戏、互联网 - 短视频、互联网 - 教育、互联网 - 医疗、互联网 - 金融、互联网 - 软件、互联网 -AI、互联网 -SaaS
消费电子：消费电子 - 手机、消费电子 - 电脑、消费电子 - 光学、消费电子 - 代工、消费电子 - 配件
半导体：半导体 - 设计、半导体 - 制造、半导体 - 代工、半导体 - 设备、半导体 - 材料、半导体 -GPU、半导体 - 模拟
新能源：新能源 - 电池、新能源 - 光伏、新能源 - 风电、新能源 - 储能、新能源汽车、新能源汽车 - 电池、新能源汽车 - 整车、光伏 - 逆变器、光伏 - 设备
医药医疗：医药 - 创新药、医药 - 中药、医药 - 生物药、医药 - 化学药、医药 - 原料药、医药 - 制剂、医药 -CXO、医药 - 疫苗、医药 - 血制、医药 - 维生素、医药 - 生长激素、医药 - 麻醉、医药 - 精神、医疗器械 -IVD、医疗器械 - 影像、医疗器械 - 心血管、医疗器械 - 骨科、医疗器械 - 眼科、医疗器械 - 牙科、医疗器械 - 血透、医疗器械 -CGM、医疗器械 - 家用、医疗器械 - 耗材、医疗器械 - 电生理、医疗器械 - 神经、医疗器械 - 内镜、医疗器械 -OK 镜、医疗器械 - 低温存储、医疗服务 - 眼科、医疗服务 - 牙科、医疗服务 - 肿瘤、医疗服务 - 生殖、医疗服务 - 中医、医美 - 玻尿酸、医美 - 整形、医美 - 敷料
食品饮料：食品饮料 - 白酒、食品饮料 - 啤酒、食品饮料 - 葡萄酒、食品饮料 - 黄酒、食品饮料 - 乳业、食品饮料 - 饮料、食品饮料 - 包装水、食品饮料 - 酱油、食品饮料 - 醋、食品饮料 - 调味品、食品饮料 - 粮油、食品饮料 - 肉制、食品饮料 - 水产、食品饮料 - 蔬菜、食品饮料 - 零食、食品饮料 - 烘焙、食品饮料 - 火锅料、食品饮料 - 卤味、食品饮料 - 速冻、食品饮料 - 榨菜、食品饮料 - 味精、食品饮料 - 酵母、食品饮料 - 保健、食品饮料 - 植物、食品饮料 - 预调酒
金融：金融 - 银行、金融 - 证券、金融 - 保险、金融 - 信托、金融 - 租赁、金融 - 期货、金融 - 基金、金融 - 交易所、金融 - 资管
房地产：房地产 - 开发、房地产 - 商业、房地产 - 住宅、房地产 -REITs、房地产 - 综合、房地产 - 酒店、房地产 - 博彩、房地产 - 交通、建筑材料 - 水泥、建筑材料 - 玻璃、建筑材料 - 涂料
通信：通信 - 运营商、通信 - 设备、通信 - 服务、通信 - 光模块
能源资源：能源 - 石油、能源 - 煤炭、能源 - 天然气、能源 - 电力、有色金属 - 铜、有色金属 - 铝、有色金属 - 黄金、有色金属 - 锂、有色金属 - 钴、有色金属 - 稀土
农业：农业 - 养殖、农业 - 种植、农业 - 饲料、农业 - 农药、农业 - 化肥、农业 - 种子、农业 - 农机
家电：家电 - 白电、家电 - 黑电、家电 - 小家电、家电 - 厨电
工业制造：工业 - 工具、工业 - 机械、工业 - 自动化、工业 - 机器人、工业 - 机床、工业 - 军工、工业 - 航天、工业 - 船舶、工业 - 铁路、工业 - 建筑、航运、物流
传媒教育：传媒 - 影视、传媒 - 游戏、传媒 - 广告、传媒 - 营销、传媒 - 出版、传媒 - 文学、传媒 - 音乐、传媒 - 视频、传媒 - 图片、教育
服装消费：服装 - 运动、服装 - 休闲、服装 - 奢侈品、服装 - 内衣、服装 - 代工、化妆品、化妆品 - 重组胶原、个人护理 - 纸巾、零售 - 商超、零售 - 电商、零售 - 免税、餐饮服务、商业 - 零售、商业 - 贸易、商业 - 租赁
公用事业：公用事业 - 电力、公用事业 - 燃气、公用事业 - 水务、公用事业 - 环保、公用事业 - 基建
汽车：汽车 - 整车、汽车 - 零部件、汽车 - 经销商、汽车 - 服务
其他：其他
"""

PROMPT_TEMPLATE = """
请判断以下股票所属的行业分类。

股票信息：
- 代码：{code}
- 名称：{name}

可选的行业分类（请从以下分类中选择最匹配的一个）：
{categories}

回答规则：
1. 只返回行业分类名称，不要任何其他内容
2. 如果股票是 ETF/基金，返回 "ETF/基金"
3. 如果无法判断，返回 "其他"
4. 确保返回的分类在上述列表中

示例：
输入：00700 - 腾讯控股
输出：互联网 - 社交平台

输入：600519 - 贵州茅台
输出：食品饮料 - 白酒

输入：300760 - 迈瑞医疗
输出：医疗器械 -IVD

现在请判断：{code} - {name}
"""

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_industry_by_llm(code: str, name: str) -> str:
    """
    使用 DeepSeek 识别股票所属行业
    
    Args:
        code: 股票代码
        name: 股票名称
    
    Returns:
        行业分类字符串
    """
    try:
        prompt = PROMPT_TEMPLATE.format(
            code=code, 
            name=name,
            categories=INDUSTRY_CATEGORIES
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的 A 股和港股股票行业分类专家，擅长根据股票名称和代码判断其所属细分行业。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=50
        )
        
        industry = response.choices[0].message.content.strip()
        
        # 验证返回的行业是否在分类体系中
        if industry and industry in INDUSTRY_CATEGORIES:
            return industry
        elif "ETF" in industry or "基金" in industry:
            return "ETF/基金"
        else:
            return "其他"
    
    except Exception as e:
        print(f"LLM 识别失败：{code} - {name}, 错误：{e}")
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
    total = len(stock_list)
    
    print(f"开始批量识别 {total} 只股票的行业...")
    
    for i, stock in enumerate(stock_list, 1):
        code = str(stock['code']).zfill(6)
        name = stock.get('name', '')
        
        industry = get_industry_by_llm(code, name)
        results[code] = industry
        
        print(f"[{i}/{total}] {code} - {name} -> {industry}")
    
    print(f"\n批量识别完成，成功识别 {len(results)} 只股票")
    return results

if __name__ == '__main__':
    # 测试
    test_stocks = [
        {'code': '00700', 'name': '腾讯控股'},
        {'code': '600519', 'name': '贵州茅台'},
        {'code': '300760', 'name': '迈瑞医疗'},
        {'code': '000858', 'name': '五粮液'},
        {'code': '09988', 'name': '阿里巴巴-W'},
    ]
    
    results = batch_get_industry(test_stocks)
    print("\n识别结果:")
    print(json.dumps(results, ensure_ascii=False, indent=2))
