# DeepSeek 大模型集成说明

## 第一步：注册 DeepSeek 账号

1. 访问 https://platform.deepseek.com/
2. 点击"注册"或"登录"
3. 使用邮箱或手机号注册
4. 完成注册后登录控制台

## 第二步：获取 API Key

1. 登录后进入控制台
2. 点击左侧菜单 "API Keys"
3. 点击 "创建新的 API Key"
4. 输入名称（如：ETF 穿透分析）
5. 点击创建，**立即复制 API Key**（只显示一次！）

## 第三步：配置环境变量

1. 在 `backend` 目录下创建 `.env` 文件：
   ```bash
   cd /Users/changdaye/Downloads/tonghuashun/etf-penetration-website/backend
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入你的 API Key：
   ```bash
   DEEPSEEK_API_KEY=sk-你的真实 APIKey
   ```

3. 保存文件

## 第四步：安装依赖

```bash
cd /Users/changdaye/Downloads/tonghuashun/etf-penetration-website/backend
pip3 install -r requirements.txt
```

## 第五步：测试 LLM

```bash
python3 llm_industry.py
```

如果看到类似输出，说明配置成功：
```
开始批量识别 5 只股票的行业...
[1/5] 00700 - 腾讯控股 -> 互联网 - 社交平台
[2/5] 600519 - 贵州茅台 -> 食品饮料 - 白酒
[3/5] 300760 - 迈瑞医疗 -> 医疗器械 -IVD
[4/5] 000858 - 五粮液 -> 食品饮料 - 白酒
[5/5] 09988 - 阿里巴巴-W -> 互联网 - 电商

批量识别完成，成功识别 5 只股票
```

## 第六步：重启网站

```bash
# 停止旧服务
pkill -f "python3 app.py"

# 启动新服务
python3 app.py
```

访问 http://localhost:5001，上传 Excel 进行测试。

## 工作流程

1. **上传 Excel** → 识别 ETF 列表
2. **点击分析** → 获取每只 ETF 的持仓股票
3. **遍历股票** → 对每只股票：
   - 有本地映射？ → 直接使用
   - 没有映射？ → 调用 DeepSeek 识别 → 保存到本地映射
4. **生成结果** → 展示行业分布和持仓明细

## 成本说明

- DeepSeek 价格：输入 ¥1/百万 tokens，输出 ¥2/百万 tokens
- 单次识别：约 220 tokens
- 单只股票成本：约 ¥0.00024
- 1000 只股票成本：约 ¥0.24

**首次分析后，映射会保存在 `data/industry_map.json`，后续分析不收费！**

## 常见问题

### Q: LLM 识别失败怎么办？
A: 会自动降级为"其他"行业，不影响分析结果

### Q: 映射保存在哪里？
A: `data/industry_map.json`，可以手动编辑

### Q: 可以离线使用吗？
A: 可以，只需首次配置，后续使用本地缓存

### Q: API Key 安全吗？
A: `.env` 文件已加入 `.gitignore`，不会上传到 Git
