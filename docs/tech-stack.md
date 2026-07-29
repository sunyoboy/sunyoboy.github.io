# 项目技术栈

> 轻量栈——VitePress 做壳 + Markdown 做内容 + Python 做数据 + 华泰 API 做行情源。
> 没有数据库（SQLite 刚引入但未深度使用），没有后端，纯静态站点。

## 静态站点

| 技术 | 版本 | 用途 |
|------|:--:|------|
| **VitePress** | ^1.6.4 | Markdown → 静态站点生成 |
| **Node.js** | 24.16.0 | VitePress 构建/开发环境 |
| **npm** | — | 包管理 |

```bash
npm run dev      # 本地开发
npm run build    # 构建静态站点
npm run preview  # 预览构建结果
```

## 数据处理

| 技术 | 版本 | 用途 |
|------|:--:|------|
| **Python** | 3.11.11（pyenv 管理） | 脚本/数据分析 |
| **pandas** | 2.0.3 | 数据处理 |
| **numpy** | 1.26.4 | 数值计算 |
| **matplotlib** | 3.9.2 | 图表渲染 |
| **akshare** | 1.18.64 | A 股历史行情数据 |
| **pywencai** | 0.13.1 | 同花顺问财数据接口 |
| **scikit-learn** | 1.8.0 | 因子挖掘（预留） |

### 核心脚本

| 脚本 | 用途 | 频率 |
|------|------|:--:|
| `scripts/fetch-market-data.py` | 抓取 7 大指数 + 持仓标的行情，生成复盘模板 | 每日 |
| `scripts/ma5-deviation.py` | 持仓标的 MA5 偏离度三维全景诊断 | 每日 |
| `scripts/shenwan-monitor.py` | 31 个申万一级行业全景监测 | 每日 |
| `scripts/discipline-check.py` | 持仓纪律自动检查 | 按需 |
| `scripts/market_db.py` | SQLite 数据仓库模块（建表·写入·查询） | 按需 |
| `scripts/save-to-db.py` | 将当日脚本数据写入 SQLite | 按需 |
| `scripts/migrate_history.py` | 将 JSON 历史数据迁移至 SQLite | 一次性 |
| `scripts/backfill-history.py` | 补写历史数据 | 按需 |
| `scripts/wechat-publish.py` | 微信公众号发布 | 按需 |

## API / 数据源

| 优先级 | 数据源 | 适用场景 | 可靠性 |
|:--:|------|------|:--:|
| 🥇 | **华泰 API**（HT_APIKEY） | 行情/指标/历史数据/成交额/财务 | ⭐⭐⭐ 最稳定 |
| 🥈 | 问财 SkillHub（IWENCAI_API_KEY） | 个股行情/指数/行业/宏观/选股 | ⭐⭐ |
| 🥉 | 腾讯行情 API（qt.gtimg.cn） | 日内快照/批量抓取 | ⭐⭐ |
| 🚫 | 东方财富 API | **已禁用**（多次远端断开） | ❌ |

## Skills（Claude Code）

| 类型 | Skill | 用途 |
|------|------|------|
| 每日复盘 | `/knowingdoing-review` | 自动拉数据+查纪律+给建议 |
| 行情 | `/knowingdoing-quotes` | 个股/ETF 实时行情 |
| 指数 | `/knowingdoing-index` | 7 大 A 股指数+海外指数 |
| 行业 | `/knowingdoing-sector` | 申万 31 行业全景 |
| 宏观 | `/knowingdoing-macro` | GDP/CPI/PMI/M2/社融/LPR |
| 财务 | `/knowingdoing-financials` | 营收/净利润/ROE/估值 |
| 选股 | `/knowingdoing-stock-screener` | 多条件组合筛选 |
| 华泰 | `/query-indicator` | 金融指标综合检索 |

## 工具链

| 工具 | 用途 |
|------|------|
| **Git** + 双 remote | gitee（origin）+ github |
| **macOS launchd** | 交易日定时抓取（15:35） |
| **Claude Code** | AI 助手/复盘分析/知识管理 |
| **Gitee Pages** | 静态站点托管（需手动点击更新） |
| **GitHub Pages** | 备用托管 |

## 环境要求

| 依赖 | 最低版本 | 当前 |
|------|:--:|:--:|
| Python | ≥ 3.11（SSL 兼容性） | 3.11.11 |
| Node.js | ≥ 18（VitePress） | 24.16.0 |

## 初始化

```bash
pyenv local 3.11.11 && python3 --version   # Python 3.11.11 ✓
nvm use 18 && node --version               # Node 18+ ✓
npm install && npm run build               # VitePress 构建通过 ✓
source ~/.zshrc && echo $HT_APIKEY         # 华泰 API Key ✓
```
