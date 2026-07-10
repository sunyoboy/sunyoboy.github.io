# AI 金融工具 · 分工指南

> 2026-07-10 · 四件套分工·各取所长·互不覆盖

---

## 一、分工原则

```
选股     → 问财（免费·数据最全）
报价     → 华泰 query-indicator（实时·交易级精度）
交易     → 华泰 paper-trading（模拟下单·全流程）
深度分析  → 东方财富妙想（研报+估值+基本面）
```

---

## 二、各工具速查

### 问财（同花顺）

| 维度 | 说明 |
|------|------|
| 用途 | 选股·行业筛选·条件过滤 |
| 费用 | **免费**·无限次 |
| 数据 | 同花顺24年·全品类A股+港股+ETF |
| 安装 | `pip install pywencai pandas` + `npx clawhub install pywencaistock` |
| 入口 | App / SkillHub / Claude Code Skill |

```
使用场景:
  "银行板块PE最低的前5只"
  "消费行业ROE>20%且营收增长>15%"
  "本周主力净流入最多的ETF"
  "业绩超预期的股票有哪些"
```

### 华泰 query-indicator

| 维度 | 说明 |
|------|------|
| 用途 | 实时报价·技术指标·行情诊断 |
| 费用 | 免费·**500次/天** |
| 精度 | 交易级·实时 |
| 安装 | [华泰AI涨乐Skills安装指南](htsc-skills-setup.md) |

```
使用场景:
  "中证500ETF最新价和MA5偏离度"
  "银行ETF的PE/PB/ROE"
  "黄金ETF近一个月走势"
```

### 华泰 paper-trading

| 维度 | 说明 |
|------|------|
| 用途 | 模拟下单·持仓管理·成交查询 |
| 费用 | 免费·同上 |
| 风险 | **仅模拟盘·不涉及真实资金** |

```
使用场景:
  买入: submitOrder --stock-code 510500 --exchange SH --direction buy --quantity 300 --price 8.50
  查仓: getPositions
  撤单: cancelOrder
```

### 东方财富妙想

| 维度 | 说明 |
|------|------|
| 用途 | 研报分析·财务模型·估值 |
| 费用 | 待确认 |
| 数据 | 东财·券商研报·财报 |

```
使用场景:
  "解读茅台最新财报"
  "银行板块估值分析"
  "中报业绩超预期行业梳理"
```

---

## 三、与现有体系的关系

```
现有工具                    补充后
─────────────────────────────────────
华泰 select-stock(500次/天) → 问财(免费无限次)  ← 选股主力
SQLite 数据仓库               → 已有·不依赖外部
Python 脚本(MA5/申万)         → 已有·不依赖外部
手动复盘                      → Claude Code + 四件套自动化
```

---

## 相关文档

- [华泰AI涨乐Skills安装指南](htsc-skills-setup.md)
- [AI金融投资工具调研](ai-finance-tools.md)
- [每日复盘Skill](knowingdoing-review-skill.md)
