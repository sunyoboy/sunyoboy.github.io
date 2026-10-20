---
name: fix-ljg-org-to-md
description: 扫描 skills 目录，把 org 输出格式改为 markdown，提交代码，同步到全局。Use when user says '/fix-ljg-org-to-md', 'fix org format', 'org 转 md', '把 org 改成 md', '修正输出格式'.
user_invocable: true
version: "1.0.0"
---

# fix-ljg-org-to-md: org 输出格式 → markdown

扫描 `skills/` 目录下所有 SKILL.md 及关联文件，把"要求模型输出 org 格式"的内容改为 markdown，然后提交并同步到全局。

## 硬编码路径

```
SKILLS_DIR="$HOME/learning/code/github/ljg-skills/skills"
GLOBAL_SKILLS="$HOME/.claude/skills"
```

## Step 1 — 扫描并替换

### 1-A 定位命中文件

```bash
grep -rl \
  -e '\.org\b' \
  -e '#+title' \
  -e '#+date' \
  -e '#+filetags' \
  -e '__.*\.org' \
  -e 'org 格式\|org格式\|以 org 输出\|输出.*\.org' \
  $SKILLS_DIR
```

对每个命中文件，用 Read 工具读取全文，然后按下表逐条替换。

### 1-B 替换规则表

| 场景 | 查找 | 替换 |
|------|------|------|
| 文件名扩展名 | `__paper.org` | `__paper.md` |
| 文件名扩展名 | `__qa.org` | `__qa.md` |
| 文件名扩展名 | `__plain.org` | `__plain.md` |
| 文件名扩展名 | `__writes.org` | `__writes.md` |
| 通用 denote 扩展名 | `__{type}.org` 模式 | `__{type}.md` |
| org 头：title | `#+title:` | `title:` (置于 `---` YAML 块内) |
| org 头：date | `#+date:` | `date:` (置于 `---` YAML 块内) |
| org 头：filetags | `#+filetags:` | `tags:` (置于 `---` YAML 块内) |
| org 头块整体 | `#+title: X\n#+date: Y\n...` | `---\ntitle: X\ndate: Y\n...\n---` |
| 输出格式声明 | `org 格式` / `org格式` | `markdown 格式` |
| 输出格式声明 | `以 org 输出` / `输出 org` | `以 markdown 输出` / `输出 markdown` |
| 输出文件扩展 | `.org` (非 URL 上下文) | `.md` |

**注意**：`*bold*` 不在自动替换范围内——在 SKILL.md 的 markdown 正文中它是斜体，只在明确是 org 输出模板的代码块内才改成 `**bold**`。判断方式：看上下文是否为 ` ``` ` 包裹的"输出示例"块。

### 1-C org 头块重构示例

原始：
```
#+title:      论文核心思想
#+date:       {date}
#+filetags:   :paper:
```

改为：
```
---
title: 论文核心思想
date: {date}
tags: [paper]
---
```

### 1-D 验证

替换完后确认无遗漏：

```bash
grep -rn "#+title\|#+date\|#+filetags\|__.*\.org\b" $SKILLS_DIR
# 预期：无输出（arxiv.org 等 URL 中的 .org 不计）
```

如仍有命中，逐一判断是否需要修改（URL 中的 `.org` 不改）。

## Step 2 — 提交代码

```bash
cd $(dirname $SKILLS_DIR)
git add -A
git status   # 展示变更文件列表
git commit -m "fix: convert org output format to markdown in skills"
```

如果 Step 1 无任何文件被修改，报告"无需转换，工作目录已是 markdown 格式"，不提交空 commit。

## Step 3 — 同步到全局

```bash
rsync -av --delete $SKILLS_DIR/ $GLOBAL_SKILLS/
```

同步后抽查改动最多的 skill：

```bash
grep -n "#+title\|\.org\b" $GLOBAL_SKILLS/ljg-paper/SKILL.md | head -5
# 预期：仅 URL 中的 arxiv.org，无 org 头
```

## 完成报告

```
fix-ljg-org-to-md 完成
- 扫描文件：X 个
- 修改文件：X 个（或"无需修改"）
- Commit：<sha> fix: convert org output format to markdown in skills
- 全局同步：X 个 skills 已更新
```

## Gotchas

- **URL 里的 `.org` 不改**——`arxiv.org`、`gnu.org` 等域名保持原样；替换前用 Read 看上下文
- **org 头块必须整体转为 YAML frontmatter**——逐行替换 `#+title:` 会留下散乱的裸字段，需要把整个头块包进 `---` / `---`
- **`*bold*` 仅改输出模板**——SKILL.md 正文里的 `*text*` 是合法斜体，不要动；只改代码块内"模型输出示例"里的 `*bold*`
- **rsync --delete 会删除 global 里 repo 没有的文件**——如果 global skills 有本地实验文件，先告知用户
