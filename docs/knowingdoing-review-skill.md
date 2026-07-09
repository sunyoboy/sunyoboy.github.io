# 知行合一 · 每日复盘 Skill

> 2026-07-10 · 自动化复盘助手 · 集成 CLAUDE.md 全部纪律规范

---

## 功能

一句话：**每天收盘后打 `/knowingdoing-review`，自动拉数据、查纪律、给建议。**

| 步骤 | 动作 | 工具 |
|------|------|------|
| 1 | 拉取行情数据 | `fetch-market-data.py` + `ma5-deviation.py` + `shenwan-monitor.py` |
| 2 | 检查纪律信号 | MA5偏离度·止损/止盈·避雷三问·事件日历 |
| 3 | 华泰API补充 | `query-indicator`·`select-stock`·`paper-trading` |
| 4 | 候选池扫描 | 38只行业 + 8只全球·不碰≠不看 |
| 5 | 输出结构化分析 | 大盘→持仓→行业→纪律→建议 |

---

## 集成的纪律规则

### 止损（价格 × 时间）

| 品种 | 价格止损 | 时间止损 |
|------|:--:|:--:|
| 宽基ETF | -3% | 不设 |
| 行业ETF | -5% | 20交易日 |
| 个股短线 | -5% | 5交易日 |
| 个股中长线 | -8% | 10交易日 |
| 所有个股 | **-20%硬止损** | — |

### 买入前三问

1. PE<20 且有利润？（ETF：PE分位<20%）
2. 近10日主力净流入？
3. 公司没发「炒作风险」公告？

### 不碰清单

- 月初/月末/大节假日前 → 不开新仓
- 个股PE>100或利润崩塌
- 大股东减持中
- 金叉已破 → 不加仓
- 不在38候选池 → 不买

### 候选池

见 [三账户ETF观察清单](etf-watchlist-2026-07-06.md)

---

## 安装

Skill 文件位于 `.claude/skills/knowingdoing-review/SKILL.md`，Claude Code 自动加载。

前置条件：
- 已安装 Python 3.9+
- 已配置华泰 API（可选但推荐）
- 项目脚本可正常运行

---

## 相关文档

- [交易纪律](position-discipline.md)
- [交易执行SOP](trading-sop-pdca.md)
- [手机端速查清单](mobile-checklist.md)
- [华泰AI涨乐Skills安装指南](htsc-skills-setup.md)
