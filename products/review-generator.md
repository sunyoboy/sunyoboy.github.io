# 🤖 一键复盘生成器

> 抓数据 → 纪律诊断 → AI 生成复盘 Markdown · 把每日 60 分钟压缩到一条命令

---

## 它是什么

把每日复盘的「拉数据 → 诊断 → 写复盘」三步流水线，封装成一条命令。
跑完脚本后，行情表、持仓纪律诊断、申万行业全景自动汇入上下文，
再由 AI 依据固定结构生成一份完整、可直接发布的复盘 Markdown。

## 它解决什么问题

| 传统流程（~55 分钟） | 一键流程（< 5 分钟） |
|---|---|
| 手动跑 3~4 个脚本，逐个复制数字 | 一条命令自动抓取并汇总 |
| 逐只核对持仓、查纪律信号 | 自动调用 MA5 偏离度诊断 |
| 手写盘面特征/驱动/资金流向 | AI 基于真实数据生成分析 |
| 反复对照模板结构补字段 | 固定结构自动产出，人工只审校 |

## 工作原理

```
generate-review.py
  ├─ 1. 抓行情     复用 fetch-market-data.py 的腾讯接口（指数 + 持仓标的）
  ├─ 2. 纪律诊断   调用 ma5-deviation.py（MA5 偏离度三维全景）
  ├─ 3. 行业全景   调用 shenwan-monitor.py（申万 31 行业）
  ├─ 4. 组织上下文  指数表 + 标的报价 + 持仓明细 + 诊断 + 纪律规则
  └─ 5. AI 生成     OpenAI 兼容接口 → 完整复盘 Markdown
```

## 两种运行模式

| 模式 | 触发 | 产出 |
|------|------|------|
| 🤖 AI 模式 | 配置 `REVIEW_LLM_API_KEY` | 完整的复盘报告 Markdown |
| 📝 草稿模式 | 未配置 Key（自动降级） | 数据填充草稿 + 给 AI 的提示词 |

> 🎯 **与 TraeCN 的协同**：草稿模式输出的提示词可直接交给 TraeCN / Claude 完成分析——
> 这也是「把思考交给 AI 落地」的最小闭环。

## 快速开始

```bash
# 今天（有 Key 则 AI 生成，无 Key 出草稿）
python3 scripts/generate-review.py

# 仅数据填充 / 只打印提示词
python3 scripts/generate-review.py --no-ai
python3 scripts/generate-review.py --prompt-only
```

环境变量（`.env`）：

```
REVIEW_LLM_API_KEY=<你的 Key>
REVIEW_LLM_BASE_URL=https://api.deepseek.com   # 任意 OpenAI 兼容接口
REVIEW_LLM_MODEL=deepseek-flash                # DeepSeek V4.1 Flash
```

## 技术实现

| 项 | 说明 |
|---|---|
| 语言 | Python 3.11（标准库，无第三方依赖） |
| 数据 | 腾讯财经行情接口 |
| AI | 任意 OpenAI 兼容接口（DeepSeek / 通义 / 智谱 / OpenAI…） |
| 复用 | importlib 加载现存脚本，避免重复实现 |

## 设计原则

- **不重复造轮子**：抓取、诊断全部复用已有脚本，新代码只做「编排 + AI」。
- **优雅降级**：没有 AI Key 也能产出可用草稿，绝不因缺配置而中断。
- **人审校优先**：AI 负责「初稿」，数据核对与最终判断仍由人把关。

---

## 相关

- [全球股市行情平台](/products/global-markets) — 复盘的行情数据来源
- [站点技术底座](/products/site-stack)
- [每日复盘 SOP](/docs/daily-review-sop) — 生成器所遵循的流程规范
