# 本仓库使用的 Skills

> **来源**：自有 5 个 + 李继刚 [ljg-skills](https://github.com/lijigang/ljg-skills)（MIT）25 个
> **定位**：DSH 的 Skill 是「按需加载的方法论」，不是工具——它规定**怎么做**，不提供**数据**
> **整理**：2026-10-20 · 依据 DSH 实际扫描路径与各 `SKILL.md` frontmatter 逐条核对

---

## 目录

- [一、Skill 不是插件](#一skill-不是插件)
- [二、DSH 的发现规则（最重要）](#二dsh-的发现规则最重要)
- [三、总览](#三总览)
- [四、自有技能（5 个）](#四自有技能5-个)
- [五、李继刚 ljg-skills（25 个）](#五李继刚-ljg-skills25-个)
- [六、已禁用（2 个）](#六已禁用2-个)
- [七、工具链：为什么需要 Bun](#七工具链为什么需要-bun)
- [八、怎么选：场景 → 技能](#八怎么选场景--技能)
- [九、维护指南](#九维护指南)
- [十、授权](#十授权)

---

## 一、Skill 不是插件

| | Skill | 脚本 / Tool | MCP |
|---|---|---|---|
| 提供什么 | **方法与判断标准** | 数据与计算 | 能力的标准协议 |
| 形态 | `SKILL.md`（Markdown 指令） | `.py` / `.ts` | 服务端 |
| 何时生效 | 命中触发词后**加载进上下文** | 调用时执行 | 连接时注册 |
| 失败方式 | 输出质量下降（无报错） | 报错 | 报错 |

**一句话**：脚本负责「拿到数据」，Skill 负责「拿到数据之后怎么想」。

本仓库两者都有：`scripts/*.py` 抓行情、算偏离度；Skill 决定复盘该怎么写、纪律该怎么判。

---

## 二、DSH 的发现规则（最重要）

> ⚠️ **装错目录 = Skill 完全不生效，而且没有任何报错。**

DSH 按以下顺序扫描（Rank 越小越优先）：

| Rank | 来源 | 路径 |
|:--:|---|---|
| 100 | `project-dsh` | `<项目根>/.dsh/skills` |
| 200 | `project-agents` | **`<项目根>/.agents/skills`** ← 本项目使用 |
| 300 | `custom` | 配置项 `customSkillDirs` |
| 400 | `user-dsh` | `~/.dsh/skills` |
| 500 | `user-agents` | `~/.agents/skills` |

**项目根** = 最近的含 `.git` 的祖先目录。

### 三条硬规则

1. **必须有 `SKILL.md`**——目录里有 `SKILL.md` 才算技能。把 `SKILL.md` 改名成 `SKILL.md.disabled` 即可禁用（目录名改成什么都不影响）。
2. **`name:` 必须小写 + 连字符**——`knowledge summary`（带空格）不合规。
3. **`.claude/skills` 不是 DSH 路径**——本项目把它做成指向 `../.agents/skills` 的软链，只用于兼容 Claude Code。

> 📌 历史教训：本仓库曾有 5 个自有 Skill 放在 `.claude/skills/` 和根目录 `skills/`，**全部隐形**，CLAUDE.md 里写了几个月的 `/knowingdoing-review` 从未生效。

---

## 三、总览

| 来源 | 可用 | 禁用 | 说明 |
|---|:--:|:--:|---|
| 自有 | 5 | 0 | 与本项目强绑定（复盘/汇总/行情/审查/心理） |
| 李继刚 ljg-skills | 25 | 2 | 通用认知工具，MIT 许可 |
| **合计** | **30** | **2** | 上下文开销 ≈ 4,300 tokens/轮 |

---

## 四、自有技能（5 个）

### `knowingdoing-review` — 每日复盘助手

> 自动拉取行情数据、检查持仓纪律、生成复盘分析、给出操作建议。整合 MA5 偏离度、申万行业监测、华泰 API、避雷三问、止损止盈双维度。

| 项 | 内容 |
|---|---|
| **用在哪** | 收盘后 15:00–16:00 的主流程 |
| **触发** | "复盘" / 收盘后 |
| **依赖** | `scripts/fetch-market-data.py`、`ma5-deviation.py`、`shenwan-monitor.py`、`verify-prices.py` |
| **产出** | `review/2026/MM/YYYY-MM-DD.md` |

### `knowledge-summary` — 知识汇总助手

> 按规则总纲（`docs/report-note-sop.md`）生成周报（P/D/C/A）、沉淀笔记、按主题汇总知识库内容。

| 项 | 内容 |
|---|---|
| **用在哪** | 周日收尾块 / 周六深度块 |
| **三种模式** | A 周报生成 · B 笔记整理（过 N1 判据 + 路由表）· C 主题汇总 |
| **依赖** | `docs/report-note-sop.md`（日报 D1–D7 / 周报 W1–W6 / 笔记 N1–N6） |

### `hithink-market-query` — 行情查询

> 获取股票、ETF、指数等实时价格、涨跌幅、成交量、主力资金流向、大小单、技术指标，支持自然语言问句。

| 项 | 内容 |
|---|---|
| **用在哪** | 盘前 25 分钟的行业/标的速度查 |
| **来源** | 同花顺 SkillHub（溯源见 `.agents/skills/.skills_store_lock.json`） |
| **体积** | 24 KB（含 `scripts/cli.py`） |

### `code-review` — 代码审查

> Review code changes — VitePress site, Python scripts, Markdown docs；检查是否符合 CLAUDE.md 约定。

| 项 | 内容 |
|---|---|
| **用在哪** | commit 前 / push 前 |
| **检查项** | 项目约定、死链、构建、文件命名 |

### `anxiety-decomposition` — 焦虑拆解

> 把具体的焦虑、恐惧、内耗写下来，用「最坏情况 → 接受它 → 改善它」三步法拆成可执行任务清单。

| 项 | 内容 |
|---|---|
| **用在哪** | 交易焦虑、职业焦虑、孕期焦虑 |
| **边界** | 不替代专业心理诊疗，不替你做人生决定 |

---

## 五、李继刚 ljg-skills（25 个）

> 设计哲学是**压缩**：用极简表达式封装完整方法论。每个技能都是「一整套提问流程」，不是一句提示词。

### 5.1 写作与表达（5 个）

| 技能 | 做什么 | 触发词 | 体积 |
|---|---|---|---:|
| **`ljg-writes`** | 把一个观点写成可理解、可迁移、经得住反例的 **1000–1500 字**中文文章 | "写文章" / "展开观点" | 16 KB |
| **`ljg-card`** | 文本 → PNG（四种模具：长图 / 全文保真 / 漫画 / 白板） | "铸" / "做成卡片" / "海报" | 539 KB |
| **`ljg-present`** | 提纲 → 单文件离线 HTML 演讲（巨句 / 对照 / Unicode 关系图） | "present" / "做演讲" / "slides" | 529 KB |
| **`ljg-classic`** | 古文逐字注解 + 章节意旨图 → 长 PNG | "文言文" / "逐字注解" | 94 KB |
| **`ljg-analogy`** | 基于结构映射理论找类比，保留关键关系与**迁移边界** | "找个类比" / "打个比方" | 19 KB |

> ⚠️ `ljg-card` / `ljg-present` / `ljg-classic` 依赖 playwright + Chromium，见第七节。

### 5.2 深度理解（7 个）

| 技能 | 做什么 | 触发词 | 体积 |
|---|---|---|---:|
| **`ljg-think`** | 纵向深钻到**不可再分的本质**（追本之箭） | "想透" / "本质是什么" / "钻到底" | 2 KB |
| **`ljg-explain`** | 把概念/公式讲到**能推导、能迁移**，给成立条件 | "讲透" / "费曼讲解" / "ELI5" | 8 KB |
| **`ljg-is`** | 把名词写成「可使用的理解」：是什么 / 差在哪 / 怎么用 | "X 是什么" / "怎么理解" | 68 KB |
| **`ljg-learn`** | 八维解剖概念（历史/辩证/现象/语言/形式/存在/美感/元反思） | "解剖概念" | 2 KB |
| **`ljg-map`** | 文稿 → 形式化知识地图（节点带白话定义 + 短公式） | "/ljg-map" / "画成地图" | 16 KB |
| **`ljg-structure`** | 找**母题级结构**，再用风洞检验因果与边界 | "找结构" / "母题是什么" | 18 KB |
| **`ljg-rank`** | 把一个领域砍到**不可再少的生成器**（降秩） | "降秩" / "靠什么撑着" | 24 KB |

### 5.3 阅读与研究（5 个）

| 技能 | 做什么 | 触发词 | 体积 |
|---|---|---|---:|
| **`ljg-read`** | 伴读文本，用「下上结构」讲透并能迁移判断 | "伴读" / "讲透这段" | 8 KB |
| **`ljg-paper`** | 给非专业读者讲论文：研究了什么 / 贡献 / 证据不支持什么 | 论文链接 / PDF | 121 KB |
| **`ljg-book`** | 拆整本书：主线怎么连、在哪结束、证据如何改变理解 | "拆书" / "这本书在讲什么" | 180 KB |
| **`ljg-qa`** | 核心观点抽成 **Q-A 链**（Q 切要害，A 四段收口） | "问答" / "抽取问题" | 15 KB |
| **`ljg-word`** | 拆解一个英语单词的核心语义 | "这个词" | 1 KB |

### 5.4 决策与投资（2 个）

| 技能 | 做什么 | 触发词 | 体积 |
|---|---|---|---:|
| **`ljg-invest`** | 判断项目是不是一台**「秩序创造机器」**（飞轮转不转） | "投资报告" / "分析这个项目" | 6 KB |
| **`ljg-business-model`** | 九模块商业模式画布 → PNG + 可改 HTML | "商业模式画布" | 430 KB |

> ⚠️ **`ljg-invest` 是给一级市场用的**（BP、创始人对话、融资）。用于 A股持仓会跑偏——只借它两个提问：**「用我们自己的话定义赛道」**和**「飞轮在不在转」**，不要整套套用。

### 5.5 对话与关系（3 个）

| 技能 | 做什么 | 触发词 | 体积 |
|---|---|---|---:|
| **`ljg-roundtable`** | 3–5 位真实人物圆桌辩论，每轮出 ASCII 结构图 | "圆桌" / "辩论" | 12 KB |
| **`ljg-relationship`** | 五层结构诊断 + 精神分析，看见关系真实结构 | "关系分析" | 10 KB |
| **`ljg-blind`** | 读昨天全部 AI 对话，照出思维盲区，再从微信读书补一章 | "扫盲区" | 14 KB |

> ⚠️ **`ljg-blind` 会读取你与 AI 的全部对话**并发往微信读书 API（需 `WEREAD_API_KEY`）。介意隐私不要触发。

### 5.6 教学（1 个）

| 技能 | 做什么 | 触发词 | 体积 |
|---|---|---|---:|
| **`ljg-teach`** | 用情境而非定义教学：先给局面让其选择，再用意外显化认知缺口 | "用情境教我" / "别先讲答案" | 7 KB |

### 5.7 其他（2 个，已归类但少用）

| 技能 | 做什么 | 备注 |
|---|---|---|
| **`ljg-constraint`** | 找出真正框住一个领域的几条约束（硬/软/自设） | 20 KB |
| **`ljg-mechanism`** | 「看反常 → 追过程 → 分解释 → 带条件迁移」，**联网核对**竞争解释 | 14 KB |

---

## 六、已禁用（2 个）

| 技能 | 禁用什么 | 为什么 |
|---|---|---|
| **`ljg-push`** | 把本地 `ljg-*` 推送到 `github.com/lijigang/ljg-skills` | 会对**他人仓库**执行 `git push`，误触即越权写 |
| **`fix-ljg-org-to-md`** | 扫描 skills 目录改格式并**自动 `git commit`** | 无人确认的写操作；本项目全程 Markdown，无 org 需求 |

**禁用方式（可逆）**：

```bash
# 目录改名 + SKILL.md 改名（后者才是决定性的）
mv .agents/skills/ljg-push .agents/skills/ljg-push-DISABLED
mv .agents/skills/ljg-push-DISABLED/SKILL.md .agents/skills/ljg-push-DISABLED/SKILL.md.disabled
```

每个禁用目录里都留了 `README-DISABLED.md`，写明原因与恢复命令。

---

## 七、工具链：为什么需要 Bun

ljg 系列有 **13 个 TypeScript 工具**，它们用的是 **Bun 专有 API**，不是标准 Node：

```
Bun.file        38 次
Bun.write       32 次
Bun.CryptoHasher 7 次
Bun.spawnSync    6 次
Bun.spawn        4 次
Bun.argv         4 次
```

用 Node 跑会直接报 **`Bun is not defined`**（Node 22 能跑 `.ts`，但跑不了 Bun API）。

### 组件

| 组件 | 位置 | 体积 | 入库 |
|---|---|---:|---|
| Bun 1.4.3 | `.agents/skills/.toolchain/bin/bun` | 67 MB | ❌ |
| Chromium 1208 | `.agents/skills/.toolchain/ms-playwright/` | 522 MB | ❌ |
| 入口脚本 | `.agents/skills/.toolchain/run.sh` | 1 KB | ✅ |
| 重建说明 | `.agents/skills/.toolchain/README.md` | — | ✅ |

### 用法

```bash
./.agents/skills/.toolchain/run.sh <工具.ts> [参数...]
```

例：

```bash
# 校验一篇 ljg-is 笔记
./.agents/skills/.toolchain/run.sh .agents/skills/ljg-is/Tools/ValidateNote.ts note.md

# 渲染卡片
./.agents/skills/.toolchain/run.sh .agents/skills/ljg-card/assets/capture.ts in.html out.png 1200 630
```

**只有 13 个带 Tools 的技能受此影响**：`ljg-blind` `ljg-book` `ljg-business-model` `ljg-card` `ljg-classic` `ljg-is` `ljg-paper` `ljg-present`。其余 17 个纯提示词技能不依赖任何运行时。

---

## 八、怎么选：场景 → 技能

| 你想做什么 | 用哪个 | 备注 |
|---|---|---|
| 收盘后写复盘 | `knowingdoing-review` | 主流程 |
| 复盘「今日驱动」归因 | `ljg-mechanism` | 要求先有消息面数据，否则只能推断 |
| 复盘「学到了什么」写不深 | `ljg-think` | 钻到根因 |
| 写月度精品文章 | `ljg-writes` | 写作飞轮 |
| 把文章做成图发朋友圈 | `ljg-card` | 需 Chromium |
| 周报 / 沉淀笔记 | `knowledge-summary` | P/D/C/A |
| 盘前查行业涨跌 | `hithink-market-query` | 同花顺源 |
| 判断一个项目值不值得投 | `ljg-invest` | 一级市场框架 |
| 读一篇论文/一本书 | `ljg-paper` / `ljg-book` | 输出 Markdown 笔记 |
| 概念讲不清 | `ljg-explain` / `ljg-is` | 前者重推导，后者重可用 |
| 一个领域砍到本质 | `ljg-rank` / `ljg-constraint` | 前者找生成器，后者找边界 |
| 焦虑内耗 | `anxiety-decomposition` | 三步法 |
| commit 前自检 | `code-review` | 约定 + 死链 + 构建 |

### 反例：什么时候**不要**用

| 场景 | 别用 | 原因 |
|---|---|---|
| 日复盘 | `ljg-writes` | 日复盘是**维护**（要快、固定格式），精品文章才是**建造** |
| A股持仓分析 | `ljg-invest` | 它是一级市场 BP 框架，会跑偏 |
| 需要数据的判断 | 任何 ljg 技能 | 它们不给数据，只给方法 |
| 交易所/券商账户操作 | 全部 | 无此能力，别指望 |

---

## 九、维护指南

### 新增一个 Skill

```bash
# 1. 放到正确位置（唯一入口）
mkdir -p .agents/skills/<name>
# 2. 写入 SKILL.md，frontmatter 必须含 name + description
# 3. name 必须小写 + 连字符
# 4. 验证：下一轮对话的技能目录应出现该名称
```

### 禁用而不删除

```bash
mv .agents/skills/<name>/SKILL.md .agents/skills/<name>/SKILL.md.disabled
```

### 换机器后重建

见 `.agents/skills/.toolchain/README.md`：下载 Bun → 两个技能各 `bun install` → `playwright install chromium`。

### 成本提醒

30 个技能的 description 每轮都注入上下文，**约 4,300 tokens**。如果响应变慢，优先砍这些与本项目无关的：

`ljg-word`（英语单词）· `ljg-classic`（古文）· `ljg-read` / `ljg-paper`（英文论文）· `ljg-relationship` · `ljg-roundtable`

砍 6 个大约省 900 tokens/轮。

---

## 十、授权

| 来源 | 许可 | 要求 |
|---|---|---|
| 自有技能 | 本项目私有 | — |
| [ljg-skills](https://github.com/lijigang/ljg-skills) | **MIT** | 保留版权声明（各目录内 `LICENSE`） |

引用出处：

- 李继刚 GitHub：<https://github.com/lijigang/ljg-skills>（md 分支为 Markdown 格式）
- 工具目录介绍：<https://ai-bot.cn/sites/79766.html>

---

**相关文档**：[方法论](/growth/方法论) · [40 个经典思维模型](/docs/mental-models-40) · [建造并进化你的机器](/docs/dalio-machine)
