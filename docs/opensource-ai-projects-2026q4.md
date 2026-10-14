# 开源 AI 项目榜单（2026 Q4）

> **快照** 2026-10-14 08:38 UTC　·　**来源** [Github-Ranking-AI](https://github.com/yuxiaopeng/Github-Ranking-AI)（每日自动更新）
> **可信度**：已用 **GitHub 官方 API** 交叉验证前 8 名，**全部吻合**（差异 <0.02%）。带 ✅ 的是实测值
> **约定**：每季度更新一次（下次 2027 Q1）

---

## 🎯 建议：这份榜单该怎么用

### 建议 1：想要可展示的 AI 作品 → 切入 ② 上下文 / 记忆层

**为什么**：它是 2026 年新崛起的一层（三个 8–11 万星的项目都在今年冒出来），门槛低，而且能直接补上你"**AI 未与 Java 打通**"的空白。

**下一步**：见《[AI 作品可行性分析 —— 上下文与记忆层](./ai-portfolio-feasibility)》。

### 建议 2：想找 Java 的切入点 → 别指望靠 Java 进 AI 开源圈

**依据**：LLM Top 100 里 **Java 只有 JeecgBoot（48k，AI 低代码）一个**。

**你的位置**：**AI 平台的工程底座** —— 网关 / 限流 / 多租户 / 数据管道 / 可观测。这是 Java 后端的天然延伸区。

### 建议 3：想系统学 → 中文资料优先

**推荐**：**hello-agents**（83k，datawhale《从零开始构建智能体》）、**ai-agent-book**（54k，李博杰《深入理解 AI Agent》）。

### 建议 4：考虑换语言 → Go 是 AI Infra 的现实选择

**依据**：ollama、ragflow、milvus、LocalAI、quivr、caveman 全是 Go。

### 建议 5：只想看趋势 → 直接跳到「二、三个关键观察」

---

## 一、九个能力层

按"**在 AI 系统里承担什么职责**"分层。**不用 GitHub 官方标签**（LLM / ChatGPT / RAG / Claude…）—— 那些标签大量重叠，同一个项目会在五六个榜里重复出现。

### ① Agent 运行时 / Harness　🔥 2026 最热

- openclaw **392k** ✅
- superpowers **299k** ✅
- ECC **279k** ✅
- hermes-agent **254k** ✅
- deepseek-harness **249k** ✅
- browser-use 118k
- pi 115k
- OpenHands 91k
- deer-flow 84k

### ② 上下文 / 记忆 / Token 优化　⭐ 今年新崛起，个人最易切入

- caveman 112k（省 65% token）
- claude-mem 101k
- rtk 83k（省 60–90% token）
- headroom 75k（压缩 tool 输出）
- mem0 67k
- context7 64k
- pathway 62k
- mempalace 59k

### ③ 模型与推理引擎　重资产，个人难切入

- ollama **183k**（Go）
- transformers **168k** ✅
- llama.cpp 131k（C++）
- vllm 94k
- LocalAI 49k（Go）
- BitNet 41k
- airllm 38k
- sglang 37k

### ④ RAG / 检索　已被卷透

- ragflow **92k** ✅（Go）
- LlamaIndex 52k
- LightRAG 40k
- PageIndex 39k
- Langchain-Chatchat 38k
- graphrag 36k（微软）

### ⑤ 向量库 / 数据基础设施

- Milvus 46k（Go）
- quivr 39k（Go）

### ⑥ 文档解析 / 网页抓取　Agent 的入口层

- firecrawl 191k
- markitdown 190k
- PaddleOCR 91k
- crawl4ai 85k
- MinerU 81k

### ⑦ 应用 / 工作流平台　低代码，非技术向

- n8n 207k
- dify 158k
- langflow 155k
- lobehub 83k
- Flowise 55k

### ⑧ 观测 / 评测　企业落地必备，但冷门

- langfuse 36k

### ⑨ 学习资源　🇨🇳 后两个是中文

- JavaGuide 159k
- generative-ai-for-beginners 121k
- LLMs-from-scratch 107k
- llm-course 83k
- **hello-agents 83k** 🇨🇳
- **ai-agent-book 54k** 🇨🇳

### 跨层头部（不属于上面任何小类的经典）

- rea 221k
- andrej-karpathy-skills 220k
- AutoGPT 188k
- prompts.chat 173k
- stable-diffusion-webui 165k
- ponytail 163k
- agency-agents 160k

---

## 二、三个关键观察

### 观察 1：榜首已经不是模型，而是「Harness + Skills + 上下文压缩」

跨层前 7 里有 **6 个**属于 harness / skills / 上下文类。更值得注意的是：**"省 token"这一类在 2026 年凭空长出三个 8–11 万星的项目**（caveman 112k、rtk 83k、headroom 75k）。

→ 这是"**瓶颈已从模型智能转向 context 密度**"这个论断的**独立证据**：钱和人都在往上下文工程涌，而不是继续卷模型。

### 观察 2：`deepseek-harness` 249k —— 就是本机此刻在用的工具

它在 DeepSeek 系仓库里排**第 1**，超过 DeepSeek-V3（105k）和 DeepSeek-R1（92k）。定位 "Everything is a Plugin"。

### 观察 3：Java 缺位，Go 占比高 ← 这条对求职最直接

- **Java**：LLM Top 100 里只有 **JeecgBoot**（48k，AI 低代码）一个
- **Go**：ollama、ragflow、milvus、LocalAI、quivr、caveman、new-api、open-code-review（阿里）全是 Go
- **含义**：❌「Java + AI」在开源生态里没有位置；✅ 但「AI 平台的工程底座」是 Java 后端的天然延伸区

---

## 三、数据可信度与季度更新

### 验证记录

| 项目 | GitHub API | 聚合器快照 |
|---|--:|--:|
| openclaw | 391,934 | 391,929 |
| superpowers | 298,854 | 298,830 |
| ECC | 278,842 | 278,818 |
| hermes-agent | 253,615 | 253,602 |
| deepseek-harness | 249,361 | 249,306 |
| transformers | 167,703 | 167,703 |
| langchain | 147,829 | 147,820 |
| ragflow | 92,185 | 92,182 |

→ 差异全部来自"聚合器快照时间"与"实时 API"之间的自然增长，**无虚报**。

### 更新命令

```bash
# 总榜（每日自动更新）
curl -sL https://raw.githubusercontent.com/yuxiaopeng/Github-Ranking-AI/master/README.md

# 分类 Top 100
curl -sL https://raw.githubusercontent.com/yuxiaopeng/Github-Ranking-AI/main/Top100/LLM.md

# 抽样交叉验证（免费、无需 token，限 60 次/小时）
curl -s https://api.github.com/repos/<owner>/<repo> | \
  python3 -c "import json,sys;print(json.load(sys.stdin)['stargazers_count'])"
```

### 校核要点

1. 记快照时间
2. 抽验 5–8 个头部
3. 三个月后回看"**新冒出来的层**"（本期就是 ② 上下文 / 记忆层）
