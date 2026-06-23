# 建站决策记录


## 目录

- [1. 平台选型](#1-平台选型)
- [2. 静态站点生成器](#2-静态站点生成器)
- [3. Node.js 环境](#3-nodejs-环境)
- [4. 目录结构](#4-目录结构)
- [5. 复盘模块](#5-复盘模块)
- [6. 主题与风格](#6-主题与风格)
- [7. 部署方案](#7-部署方案)
- [8. 命令速查](#8-命令速查)
- [9. 导航结构约束](#9-导航结构约束)
- [10. 扩展方向](#10-扩展方向)

---

## 1. 平台选型

**决策**：一份源码，GitHub Pages + Gitee Pages 双平台部署。

**原因**：GitHub Actions 全自动，Gitee 兜底国内访问速度。

## 2. 静态站点生成器

**决策**：VitePress > Hexo。

| 对比维度 | VitePress | Hexo |
|---------|-----------|------|
| 构建速度 | Vite 加持，极快 | 慢 |
| 配置复杂度 | 一个 config 文件 | 主题配置繁琐 |
| 生态趋势 | 活跃增长 | 停滞 |
| Markdown 支持 | 原生 | 原生 |

## 3. Node.js 环境

**决策**：使用 nvm 安装 Node 18 LTS（VitePress 最低要求）。

```bash
nvm install 18 && nvm use 18
```

## 4. 目录结构

```
KnowingDoing/
├── .vitepress/          # VitePress 配置 & 主题
│   ├── config.mjs
│   └── theme/
│       ├── custom.css   # 护眼样式
│       └── index.js
├── review/              # 复盘模块
│   └── 2026/
│       ├── 2026.md      # 年复盘
│       └── 05/
│           ├── 2026-05.md      # 月复盘
│           ├── 2026-W21.md     # 周复盘
│           └── 2026-05-21.md   # 日复盘
├── docs/                # 站点文档
│   ├── deploy.md
│   └── decision-log.md
├── .github/workflows/   # GitHub Actions 部署
├── scripts/             # 辅助脚本
├── index.md             # 首页
├── about.md             # 关于
└── README.md
```

## 5. 复盘模块

**决策**：`年 → 月 → (周 + 日)` 层级嵌套。

| 粒度 | 路径 | 命名格式 |
|------|------|---------|
| 年复盘 | `review/2026/2026.md` | `YYYY.md` |
| 月复盘 | `review/2026/05/2026-05.md` | `YYYY-MM.md` |
| 周复盘 | `review/2026/05/2026-W21.md` | `YYYY-Www.md` |
| 日复盘 | `review/2026/05/2026-05-21.md` | `YYYY-MM-DD.md` |

新增 `.md` 文件即自动生成页面路由。侧边栏通过 `config.mjs` 折叠分组。

## 6. 主题与风格

**决策**：自定义 CSS，护眼暖色系。

- 主题色：柔绿 `#5b8c5a`
- 亮色背景：暖白纸色 `#fdf6ec`
- 暗色背景：暖暗 `#2b2722`
- 正文：16px，行高 1.85
- 标题字重：500/600，不压眼

## 7. 部署方案

| 平台 | 方式 | 触发 |
|------|------|------|
| GitHub Pages | Actions 自动 | push main |
| Gitee Pages | 手动点击更新 | 每次推送后 |

**双 remote 推送**：
```bash
git remote add github git@github.com:<username>/<repo>.git
git remote add gitee  git@gitee.com:<username>/<repo>.git
git push github main && git push gitee main
```

## 8. 命令速查

| 命令 | 说明 |
|------|------|
| `npm run dev` | 开发服务器 → localhost:5173 |
| `npm run build` | 构建 → .vitepress/dist/ |
| `npm run preview` | 预览构建结果 |

## 9. 导航结构约束

**决策**：顶部导航不超过 5 个，按「使用场景」划分入口。

| 顶部导航 | 场景 | 归入内容 |
|---------|------|---------|
| 复盘 | 高频·每日 | 交易记录、复盘总结 |
| 问题清单 | 高频·每日 | 每日疑问、思考记录 |
| 知识库 | 查阅·按需 | 方法论、工具清单、术语解释 |
| 关于 | 低频·站点信息 | 站点说明、个人简介 |

**新增内容归类规则**：
- 新内容不新增顶部菜单，一律归入现有模块
- 侧边栏负责模块内的内容细分，顶部负责场景入口
- 违反此规则需要更新本决策记录

## 10. 扩展方向

- 文件 > 50 篇时，可通过 `createContentLoader` 实现动态分页
- 复盘模板可按需增加「运动/阅读/技能」等维度
