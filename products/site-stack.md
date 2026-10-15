# 🏗️ 站点技术底座

> VitePress + Python + GitHub Actions · 个人投研知识库的工程化载体

---

## 它是什么

本知识库站点本身的工程实现。它不是「一个博客」，而是一套**内容 + 数据 + 自动化**的个人研究系统：
Markdown 写作 + Python 抓数 + CI 自动部署，一整套跑在自己一台电脑上。

## 架构总览

```
Markdown 内容  ──►  VitePress 静态构建  ──►  GitHub Pages 自动部署
      ▲                                              ▲
      │                                              │
Python 数据脚本 ──► 复盘模板/图表                   Git + 双 remote
      ▲
      │
本地定时任务（launchd · 交易日 15:35 自动抓取）
```

## 技术栈

| 层 | 选型 | 用途 |
|---|---|---|
| 静态生成 | VitePress ^1.6.4 | Markdown → 站点 |
| 内容 | Markdown + 本地搜索 | 复盘 / 知识库 / 成长 / 问题清单 |
| 数据 | Python 3.11 + pandas + akshare | 行情抓取、指标计算、图表 |
| 自动化 | GitHub Actions / macOS launchd | 构建部署 / 定时抓数 |
| 版本管理 | Git + 双 remote（GitHub + Gitee） | 一份代码两端同步 |

## 工程亮点

- **纯静态、零后端**：没有数据库、没有服务器，成本几乎为零，但覆盖了完整的研究工作流。
- **内容与数据分离**：Markdown 是「人写的判断」，Python 脚本产出是「机器给的事实」，两者在复盘里汇合。
- **CI 即发布**：`git push` → Actions 自动构建 → Pages 上线，人不需要碰部署。
- **私有数据隔离**：含个人信息的 `data/` 目录通过 `srcExclude` 永不参与构建与发布。

## 为什么值得做

> 它本身就是作品——用一次，多个飞轮同时受益：写作产生内容、Python 产生数据、AI 提高效率、站点沉淀品牌。

---

## 相关

- [全球股市行情平台](/products/global-markets)
- [一键复盘生成器](/products/review-generator)
- [技术栈详表](/docs/tech-stack)
