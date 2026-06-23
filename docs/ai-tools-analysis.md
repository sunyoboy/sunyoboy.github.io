# AI 工具全景分析与使用建议

> 2026-06-04 | 机器环境：Mac (Apple Silicon) | Node v24.16.0


## 目录

- [一、当前已安装的 AI 工具](#一当前已安装的-ai-工具)
  - [命令行 AI 工具（3 个）](#命令行-ai-工具3-个)
  - [AI IDE / 编辑器（4 个）](#ai-ide-编辑器4-个)
  - [VS Code AI 扩展](#vs-code-ai-扩展)
  - [桌面 AI 应用（4 个）](#桌面-ai-应用4-个)
- [二、Claude Code 当前配置](#二claude-code-当前配置)
- [三、核心问题：工具严重重叠](#三核心问题工具严重重叠)
- [四、优化建议](#四优化建议)
  - [做减法：精简到 5 个核心工具](#做减法精简到-5-个核心工具)
  - [按场景选工具](#按场景选工具)
  - [DeepSeek 后端优化](#deepseek-后端优化)
  - [插件不是开了就行，要真正用起来](#插件不是开了就行要真正用起来)
  - [定期清理项目记忆](#定期清理项目记忆)
- [五、理想工具组合（一张图）](#五理想工具组合一张图)
- [六、一句话总结](#六一句话总结)

---

---

## 一、当前已安装的 AI 工具

### 命令行 AI 工具（3 个）

| 工具 | 版本 | 定位 |
|------|------|------|
| Claude Code | v2.1.119 | 主力终端 AI 编程助手，已深度配置 |
| OpenAI Codex | v0.137.0 | OpenAI 出品，功能与 Claude Code 重叠 |
| GitHub Copilot CLI | v1.0.59 | GitHub 官方命令行助手，功能重叠 |

### AI IDE / 编辑器（4 个）

| 工具 | 特点 |
|------|------|
| Cursor | AI-native IDE，基于 VS Code，深度 AI 集成 |
| VS Code | 传统 IDE，通过扩展获得 AI 能力（装了 4 个 AI 扩展） |
| Trae CN | 字节跳动 AI IDE，国内版，内置免费 AI 模型 |
| CodeBuddy CN | 腾讯 AI IDE，国内版 |

### VS Code AI 扩展

| 扩展 | 功能 |
|------|------|
| `anthropic.claude-code` | Claude Code IDE 集成 |
| `saoudrizwan.claude-dev` | Claude Dev，自主编程 AI agent |
| `alibaba-cloud.tongyi-lingma` | 通义灵码，代码补全 + 问答 |
| `volartools.volar-ai` | Vue AI 辅助工具 |

### 桌面 AI 应用（4 个）

| 工具 | 定位 |
|------|------|
| Chatbox | 多模型 AI 聊天客户端 |
| Doubao | 字节跳动豆包 AI 助手 |
| iTermAI | 终端 AI 伴侣 |
| ima.copilot | 腾讯 AI 助手 |

---

## 二、Claude Code 当前配置

```
API 后端      DeepSeek（通过 Anthropic 兼容 API）
主力模型      deepseek-v4-pro[1m]（1M 上下文）
快速模型      deepseek-v4-flash
输入上限      150K tokens
输出上限      30K tokens
主题          暗色
```

**已启用的插件（10 个）：**

| 插件 | 用途 |
|------|------|
| superpowers | TDD、debug、code review 工作流 |
| figma | 设计稿转代码、生成架构图 |
| playwright | 浏览器自动化测试和页面抓取 |
| firecrawl | 外部网页/文档抓取 |
| code-review | 自动代码审查 |
| feature-dev | 大型功能架构设计 |
| frontend-design | 前端界面生成 |
| github | PR/Issue 操作 |
| linear | 项目管理 |
| brightdata | 数据采集 |

**管理的项目：** 12 个（knowledge-base、KnowingDoing、RuoYi、api-v6 等）

---

## 三、核心问题：工具严重重叠

当前装了 **7 个 AI IDE/编辑器 + 3 个 CLI + 4 个桌面应用 = 14 个工具**，同质化严重：

- Claude Code vs Codex vs Copilot CLI：三个终端 AI 助手功能 90% 重叠
- Cursor vs VS Code vs Trae vs CodeBuddy：四个 AI IDE 同时存在
- Doubao vs Chatbox vs iTermAI vs ima.copilot：四个桌面 AI 客户端

**负面影响：** 配置、插件、上下文记忆分散在不同工具中，哪个都没深入掌握。

---

## 四、优化建议

### 做减法：精简到 5 个核心工具

| 场景 | 推荐 | 理由 |
|------|------|------|
| 日常编码主力 | Claude Code CLI | 已深度配置，功能最全 |
| 图形化 IDE | 只留 Cursor + VS Code | VS Code 用于轻量编辑和 Git 可视化；Cursor 用于需要图形化 AI 编程的场景 |
| 中文/国内模型 | Trae CN 或 CodeBuddy（二选一） | 不需要两个都装 |
| 多模型聊天 | Chatbox | 对比模型、做 prompt 实验 |
| 放弃 | Doubao / iTermAI / ima.copilot | 与主力工具高度重叠 |
| 闲置 | Codex CLI / Copilot CLI | 等需要对比时再用 |

### 按场景选工具

```
新功能开发      Claude Code（需求分析 → 架构设计 → TDD → 编码）
Bug 修复        Claude Code（定位 → 写复现测试 → 修复 → 验证）
代码审查        Claude Code + /code-review
设计稿转代码    Claude Code + Figma 插件
浏览器相关      Claude Code + Playwright 插件
前端页面        Claude Code + frontend-design 插件
外部信息抓取    Claude Code + Firecrawl 插件
PR 操作         Claude Code + gh CLI
轻量文件编辑    VS Code
复杂重构        Cursor（图形化 AI 交互更适合大范围改动）
```

### DeepSeek 后端优化

当前所有模型（Haiku/Sonnet/Opus）都映射到 DeepSeek，失去了模型阶梯选择——轻量任务也用了大模型。

建议调整为：
```
Haiku  → deepseek-v4-flash   （轻量任务：简单问答、文件检索）
Sonnet → deepseek-v4-pro[1m] （主力任务）
Opus   → deepseek-v4-pro[1m] （保持现状）
```

或者找一家支持原生 Claude 4.x 的 API 提供商作为按需补充。

### 插件不是开了就行，要真正用起来

| 插件 | 什么时候必须用它 |
|------|-----------------|
| superpowers | 每次开发自动触发，不需要手动调用 |
| figma | 有设计稿/需要生成架构图时 |
| playwright | 需要浏览器测试或爬取页面时 |
| firecrawl | 需要抓取外部网站内容时 |
| feature-dev | 大型功能开发，先走架构设计 |
| github | 操作 PR/Issue，比手敲 gh 命令方便 |

### 定期清理项目记忆

12 个项目中部分已不活跃，建议清理：

```bash
claude projects list          # 查看所有项目
claude projects delete <name> # 删除不活跃项目
```

---

## 五、理想工具组合（一张图）

```
┌─────────────────────────────────────────────┐
│                 主力：Claude Code CLI         │
│        （编码 · Debug · 审查 · 部署）          │
├─────────────────────────────────────────────┤
│  辅助1: VS Code           辅助2: Cursor      │
│  （轻量编辑 · Git · MR）   （图形化 AI 编程）   │
├─────────────────────────────────────────────┤
│  辅助3: Chatbox           辅助4: Trae/CodeBuddy│
│  （多模型对比 · 实验）     （国内模型备用）      │
└─────────────────────────────────────────────┘

闲置：Codex CLI · Copilot CLI
放弃：Doubao · iTermAI · ima.copilot
```

---

## 六、一句话总结

> 工具太多，砍掉一半。把 Claude Code 用到极致，产出比什么都高。
