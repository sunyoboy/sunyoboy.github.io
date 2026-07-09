---
name: knowingdoing-review
description: 知行合一 · 每日复盘助手。自动拉取行情数据、检查持仓纪律、生成复盘分析、给出操作建议。整合 MA5 偏离度、申万行业监测、华泰 API、避雷三问、止损止盈双维度。
user-invocable: true
metadata:
  author: KnowingDoing
  requires:
    bins: ["python3"]
---

# 知行合一 · 每日复盘助手

## 何时使用

当用户执行每日复盘、分析行情、检查持仓、或需要操作建议时使用。

触发词：复盘、分析行情、持仓检查、操作建议、今天怎么样

---

## 执行流程

### Step 1: 拉取数据

```bash
cd $KNOWINGDOING_HOME  # 项目根目录
python3 scripts/fetch-market-data.py $(date +%Y-%m-%d)
python3 scripts/ma5-deviation.py
python3 scripts/shenwan-monitor.py
python3 scripts/save-to-db.py   # 数据持久化到 SQLite
```

### Step 2: 检查纪律信号

对照以下文档逐条检查：

| 检查项 | 参考文档 | 行动 |
|------|------|------|
| MA5 偏离度是否触发信号 | `docs/ma5-deviation-discipline.md` | 高危→清仓·偏热→减仓·偏冷+金叉→可低吸 |
| 止损线是否触发 | `docs/position-discipline.md` 第三节 | 触发就走·不犹豫 |
| 止盈信号是否出现 | `docs/position-discipline.md` 第四节 | 三连大阳线·三破五·偏离度 |
| 买入前三问 | `docs/position-discipline.md` 第一节 | PE/主力/炒作 |
| 月初/月末/节前 | `docs/position-discipline.md` 第十节 | 不开新仓 |
| 候选池扫一眼 | CLAUDE.md 盘后检查 | 30秒·不碰≠不看 |

### Step 3: 使用华泰 Skill 补充分析

```bash
export HT_APIKEY=$(cat ~/.htsc-skills/config | grep HT_APIKEY | cut -d= -f2)
python3 ~/.claude/skills/query-indicator/query_indicator.py queryIndicator --query "<标的>最新价和MA20偏离度"
python3 ~/.claude/skills/a-share-paper-trading/a_share_paper_trading.py getAccountBalance
```

### Step 4: 输出结构

按以下结构输出分析：

```
## 大盘概况（指数+涨跌比+成交额）
## 持仓诊断（每只标的·MA5偏离度·信号·操作）
## 申万行业（领涨Top5·领跌Top5·极端信号）
## 纪律检查（止损/止盈/避雷/事件）
## 操作建议（买什么·卖什么·挂什么单）
```

---

## 关键规则速查

### 止损规则
- 宽基 ETF: -3% 止损
- 行业 ETF: -5% 止损·20个交易日时间止损
- 个股: -8% 价格止损·10个交易日时间止损
- 所有个股: -20% 硬止损红线

### 买入前必问
1. PE<20 且有利润支撑？（ETF 看 PE 分位 <20%）
2. 近10日主力净流入？
3. 公司没发「炒作风险」公告？

### 不碰清单
- 月初/月末/大节假日前 → 不开新仓
- 个股 PE>100 或利润崩塌 → 不碰
- 大股东减持中 → 不碰
- 金叉已破的品种 → 不加仓

### 候选池跟踪
- 38只 A股行业 + 8只全球补充 → 见 `docs/etf-watchlist-2026-07-06.md`
- 每天扫一眼涨跌 → 条件变了就重新评估
- 不碰 ≠ 不看
