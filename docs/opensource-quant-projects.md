# 开源量化项目调研

> 2026年6月 · 数据源、券商连接、选型建议

---

## 目录

- [顶级项目速览](#顶级项目速览)
- [数据源分类对比](#数据源分类对比)
- [券商API跨境对比](#券商api跨境对比)
- [选型推荐](#选型推荐)

---

## 顶级项目速览

### 1. Vibe-Trading（Python）⭐⭐⭐⭐⭐

| 维度 | 详情 |
|------|------|
| 仓库 | `github.com/HKUDS/Vibe-Trading` |
| 最新版 | v0.1.10（2026.6.19） |
| 定位 | AI Agent + 量化平台，自然语言生成策略 |

**18 个数据源**（免费优先→付费备选）：

```
免费（无需 API Key）：              需 API Key：
├── Tushare（A股）                  ├── Finnhub
├── AKShare（A股/宏观）             ├── Alpha Vantage
├── Baostock（A股历史）             ├── Tiingo
├── EastMoney（A股资金流/龙虎榜）    └── FMP
├── Sina / Tencent / Mootdx（实时行情）
├── Yahoo Finance（全球）
├── CCXT（100+加密交易所）
└── Stooq

10 个券商连接：
├── IBKR（盈透）— 全球多市场
├── Robinhood（美股，OAuth MCP）
├── Tiger（老虎证券）— 港美股+A股
├── Longbridge（长桥）— 港美股+A股
├── Futu（富途）— 港美股+A股
├── Alpaca — 美股
├── OKX / Binance — 加密
└── Dhan / Shoonya — 印度
```

**452 个预构建 Alpha 因子**（qlib158、alpha101、gtja191、academic 四库），7 个回测引擎，跨市场复合引擎，期权组合支持，MCP 协议集成。

---

### 2. Lumibot（Python）⭐⭐⭐⭐

| 维度 | 详情 |
|------|------|
| 协议 | MIT 开源 |
| 版本 | v4.5.9 |

**数据源**：Yahoo Finance（免费）、Polygon、ThetaData、DataBento、IBKR、Alpaca

**券商**：IBKR、Alpaca、Tradier、Schwab、CCXT、Bitunix

**特点**：同一份代码跑回测 + 实盘。内置 AI 交易 Agent。期权完整支持。这意味着"模拟→实盘"无缝打通，不需要重写任何代码。

---

### 3. Quool（Python）⭐⭐⭐

| 维度 | 详情 |
|------|------|
| 版本 | v7.0.16 |
| 架构 | 事件驱动回测 + 实盘 |

**数据源**：DataFrame自定义源、DuckDB/Parquet、**东方财富实时API**、XtQuant

**券商**：AShareBroker、**雪球模拟盘**、**XtQuant实盘网关**

**特点**：雪球模拟盘 + 东方财富数据源。你在 2026-05-26 的提问中调研过雪球组合，这个项目把雪球包成了可编程 API。

---

### 4. Quantbox（Python）⭐⭐

| 维度 | 详情 |
|------|------|
| 定位 | A股纯国产量化数据中台 |

**数据源**：**Tushare Pro**、**掘金量化(GMAdapter)**、本地 MongoDB

**特点**：全异步（10-20倍提速）、智能缓存预热 1491 条数据、Python 3.14 nogil 支持。如果你的场景是"只做A股、不要外部依赖"，这是最轻量的选择。

---

### 5. StockSharp（C# .NET）⭐⭐⭐⭐⭐

| 维度 | 详情 |
|------|------|
| 语言 | C# .NET，源码全开放 |
| 连接器 | **50+** |

覆盖 Binance、MT4/MT5、IBKR、OKX、Coinbase、Kraken、Oanda、FXCM、cTrader、PolygonIO、LMAX 等。附带可视化策略设计器。企业级首选，但需要 C# 技术栈。

---

### 6. Fincept Terminal（C++20/Qt6）⭐⭐⭐

| 维度 | 详情 |
|------|------|
| 协议 | AGPL-3.0 |

**100+ 数据连接器** + **16 券商集成**。内置 AI Agent（巴菲特/格雷厄姆/林奇风格投研助手）。原生桌面应用，性能极高。

---

### 7. 专业方向项目

| 项目 | 语言 | 聚焦 |
|------|:---:|------|
| **Floe** | TypeScript | 期权流分析，Tradier/Tastytrade/Schwab 实时 WebSocket |
| **CPZ-AI** | Python | 量子计算投资组合优化（IonQ/Rigetti 真实量子硬件） |
| **quant-system** | Rust | 超低延迟 HFT，cTrader FIX 直连 |
| **Moomoo API** | Python | 富途官方 Python SDK，港/美/A股行情+交易 |
| **War Room** | Python | IBKR 券商专属交易仪表盘 |

---

## 数据源分类对比

### A股

| 数据源 | 类型 | 费用 | 覆盖内容 | 被哪些项目使用 |
|------|:---:|:---:|------|------|
| **Tushare Pro** | REST API | 积分制 | 股票/期货/基金/宏观/资金流 | Quantbox, Vibe-Trading |
| **AKShare** | Python库 | 完全免费 | A股/期货/宏观/新闻 | Vibe-Trading, Fincept |
| **Baostock** | Python库 | 完全免费 | A股历史日线（最干净） | Vibe-Trading |
| **东方财富** | HTTP直接 | 免费 | 资金流/龙虎榜/板块 | Quool, Vibe-Trading |
| **腾讯财经** | HTTP `qt.gtimg.cn` | 免费 | 实时价格 | 你已经在用 |
| **新浪财经** | HTTP `hq.sinajs.cn` | 免费 | 价格+成交量+金价 | 你已经在用 |
| **掘金量化** | SDK | 模拟免费 | A股实时+历史+回测 | Quantbox |
| **Mootdx** | Python库 | 免费 | A股实时行情（通达信协议） | Vibe-Trading |

### 全球/美股

| 数据源 | 费用 | 适合场景 |
|------|:---:|------|
| **Yahoo Finance** | 免费 | 全球股票快照+股息 |
| **Polygon.io** | 付费 | 美股实时 Tick/Bar |
| **DataBento** | 付费 | 机构级 Tick 历史 |
| **Alpha Vantage** | 25次/天免费 | 美股基本面 |
| **FRED** | 免费 | 80万+宏观经济序列 |
| **CCXT** | 免费 | 100+加密交易所 |

---

## 券商API跨境对比

| 券商 | 覆盖市场 | 模拟盘 | Python库 | 用的项目 |
|------|------|:---:|:---:|------|
| **IBKR 盈透** | 全球（美股+港股+期货+期权） | ✅ | `ib_insync` | Lumibot, Vibe-Trading, StockSharp |
| **富途 Futu** | 港/美/A股通 | ✅ | `moomoo-api` / `futu-api` | Vibe-Trading, War Room |
| **老虎 Tiger** | 港/美/A股通 | ✅ | SDK | Vibe-Trading |
| **长桥 Longbridge** | 港/美/A股通 | ✅ | SDK | Vibe-Trading |
| **Alpaca** | 美股 | ✅ | `alpaca-py` | Lumibot, CPZ-AI, StockSharp |
| **XtQuant** | A股（迅投QMT） | ✅ 模拟 | SDK | Quool |
| **雪球** | A股组合模拟 | ✅ | HTTP | Quool |

---

## 选型推荐

### 推荐：Quool + 雪球模拟盘

> 针对你的实际情况——只做 A 股、Python 技术栈、需要模拟盘先行验证——推荐优先级最高的方案。

**为什么是 Quool 而不是 Vibe-Trading**：

| 维度 | Quool | Vibe-Trading |
|------|:---:|:---:|
| 学习曲线 | 低（事件驱动回测，直觉清晰） | 中高（452因子+MCP+7引擎，概念太多） |
| A股专注度 | **纯A股**，东方财富+雪球+XtQuant | 全球多市场，A股只是其一 |
| 模拟→实盘 | 雪球模拟盘 → XtQuant实盘，同代码 | 需跨项目配置券商连接 |
| 架构复杂度 | 简洁（DuckDB存储，单进程） | 复杂（多引擎、MCP服务、Agent） |
| 与你现有工具的整合 | 东方财富API你已经在用 | 你还需要学它的DSL |
| 当前阶段匹配 | ✅ 策略验证阶段 | ❌ 更适合实盘多市场阶段 |

**Vibe-Trading 更适合什么阶段**：当你已经有 3-5 个验证过的策略、需要在多个市场同时部署时，它的 10 个券商连接 + 7 个回测引擎就是正确选择。但当前你还在"第一轮策略验证"阶段，不需要一架波音 747——一辆皮卡就够了。

### 执行路径

```
第一步（本周）：Quool + 雪球模拟盘
  pip install quool
  用东方财富数据跑第一个回测（你来做T策略的回测）
  雪球创建模拟组合跟踪

第二步（1-2月）：策略回测验证
  胜率 ≥ 55%、盈亏比 ≥ 1.5 → 进入下一步
  不达标 → 调整策略，重新回测

第三步（验证后）：XtQuant 模拟盘
  同一份代码切换到 XtQuant 模拟网关
  验证实盘环境的滑点/成交率

第四步（长期）：实盘 + Vibe-Trading
  小资金实盘验证
  如果未来需要跨市场（港美股），再引入 Vibe-Trading
```

### 备选方案

如果你更看重"同一份代码跑回测+实盘"，**Lumibot** 也是一个好选择——MIT 协议、内置 AI Agent、期权支持。缺点是它的数据源偏美股（Yahoo Finance / Polygon），A 股数据需要自己适配。

---

## 链接

- [[ai-coding-models-2026]] — AI 编程模型性价比对比（量化策略的工具成本基础）
- [[第二增长曲线]] — 量化策略是路径一
- [[investment-discipline-indicators]] — 投资纪律指标化（策略的纪律框架）
- [[self-awareness]] — 自我认知框架（选型判断的思维工具）
