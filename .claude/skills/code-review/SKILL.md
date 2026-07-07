---
name: code-review
description: Review code changes in the KnowingDoing project — VitePress site, Python scripts, Markdown docs. Use when the user asks for code review, wants to verify changes before committing, or needs to check that project conventions (CLAUDE.md rules) are followed. Triggers on "review my changes", "check this code", "code review", "review before commit", "is this ready to push", or any request to verify/audit project files.
---

# Code Review · KnowingDoing 项目专属

对 KnowingDoing 项目的代码变更进行结构化审查。审查维度与该项目的 CLAUDE.md 规范强绑定。

## 审查流程

```
1. 获取变更范围 → git diff / git status / 用户指定的文件
2. 逐维度审查（见下方审查清单）
3. 输出分级报告（Critical / Important / Minor）
4. 给出可执行的修复建议
```

## 审查清单

### 一、构建验证 🔴 Critical

```bash
npm run build
```

- VitePress build 是否通过？
- 有无 dead link（相对路径拼写错误、文件缺失）？
- 侧边栏引用的文件路径是否全部存在？

> **这是绝对不能跳过的检查。** build 不过 = 不能 push。

### 二、联动更新检查 🔴 Critical

新增 Markdown 文档时，以下文件是否同步更新：

| 新文件位置 | 需更新的文件 | 检查方法 |
|------|------|------|
| `review/2026/0X/*.md` | `catalog.md` + `.vitepress/config.mjs` | grep 文件名是否出现在这两个文件中 |
| `docs/*.md` | `catalog.md` + `.vitepress/config.mjs` | 同上 |
| `growth/*.md` | `catalog.md` + `.vitepress/config.mjs` | 同上 |
| `questions/2026/0X/*.md` | `catalog.md` + `questions/index.md` | 同上 |

```bash
# 快速检查：新增的 .md 文件是否都被 catalog.md 引用
git diff --name-only HEAD~1 | grep '\.md$' | while read f; do
  grep -q "$(basename $f)" catalog.md || echo "⚠️ $f 未出现在 catalog.md"
done
```

### 三、命名规范检查 🟡 Important

```
✅ review/2026/07/2026-07-07.md
✅ review/2026/06/2026-06-12-持仓分析.md
✅ questions/2026/07/2026-07-06.md
✅ growth/2026/06/2026-06-月回顾.md

❌ review/2026/07/复盘-7月7日.md        ← 不是 YYYY-MM-DD 格式
❌ questions/2026/07/2026-07-06-问题.md  ← 日期后主题需用中文连字符
```

规则：`YYYY-MM-DD[-中文主题描述].md`

### 四、文档结构检查 🟡 Important

Markdown 内容文件应包含：
- [ ] 标题（`# 标题`）
- [ ] 目录章节（`## 目录` + 锚点链接）
- [ ] 必要的 frontmatter 或元信息（日期、背景、状态）
- [ ] 无残缺的 Markdown 语法（未闭合的代码块、表格等）

### 五、脚本完整性检查 🟡 Important

Python 脚本变更时检查：

- [ ] `fetch-market-data.py` — BUY_ZONES 是否与最新持仓一致？抓取函数 URL 是否有效？
- [ ] `ma5-deviation.py` — KEY_ZONES 止损/低吸区间是否更新？标的列表是否与实盘一致？
- [ ] 新脚本是否有对应的 catalog.md 条目？
- [ ] 脚本是否在 CLAUDE.md「脚本速查」表中注册？

### 六、Git 规范检查 🔵 Minor

- [ ] commit message 格式：`feat(scope): description` 或 `fix(scope): description`
- [ ] 是否在正确的分支上（不要直接在 main 上开发）
- [ ] `git remote -v` 确认双 remote 正常（origin=gitee, github=github）
- [ ] 无 force push 风险

### 七、内容质量检查 🔵 Minor

- [ ] 是否有未填写的模板占位符（`______`、`TODO`、`⏳` 过多的待办）？
- [ ] 关键数字是否有核对（交易数据、孕期指标、财务金额）？
- [ ] 日期引用是否一致（如「下周五」在文档发布后是否仍然正确）？

## 输出格式

```markdown
# Code Review · [范围描述]

## Build
- [ ] `npm run build`: PASS / FAIL

## 发现

### Critical
- [ ] **问题描述** — 文件:行号 — 修复建议

### Important
- [ ] **问题描述** — 文件:行号 — 修复建议

### Minor
- [ ] **问题描述** — 文件:行号 — 修复建议

## 评估
🟢 Ready to merge / 🟡 Fix Important first / 🔴 Blocked by Critical
```

## 审查原则

1. **Build 不过绝不放过** — 这是唯一的 hard block
2. **联动更新是最容易忘的** — 新增文件时优先查 catalog.md + sidebar
3. **不要因为「改动小」就跳过审查** — 一个错别字在 VitePress 里就是一个 dead link
4. **修复建议要具体到文件:行号** — 不说「修复命名」，说「重命名为 `2026-07-07.md`」
5. **区分项目规范问题 vs 通用代码质量问题** — 前者阻塞 push，后者建议改进
