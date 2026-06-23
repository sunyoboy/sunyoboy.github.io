# KnowingDoing · 知行合一

个人知识输出平台，以「知行合一」为核心理念，用 Markdown 写作沉淀思考和记录。

## 技术选型

| 层 | 选型 | 原因 |
|---|---|---|
| 静态生成 | VitePress | 快、配置少、Markdown 原生支持 |
| 版本管理 | Git + 双 remote | 一份代码，两端同步 |
| 部署 | GitHub Actions + Gitee 手动 | GitHub 自动化，Gitee 兜底国内访问 |

## 目录结构

```
KnowingDoing/
├── .vitepress/           # VitePress 配置与主题
├── public/charts/        # 交互图表
├── index.md              # 首页
├── catalog.md            # 全站索引
├── growth/               # 个人成长（OKR/周报/财务/技能）
├── review/               # A股复盘（按年/月/日）
├── docs/                 # 知识库
├── questions/            # 问题清单
├── scripts/              # 工具脚本
├── package.json
└── .gitignore
```

## 命令

| 命令 | 说明 |
|---|---|
| `npm run dev` | 启动开发服务器 |
| `npm run build` | 构建静态文件到 `.vitepress/dist/` |
| `npm run preview` | 预览构建结果 |

## 部署流程

```
写 Markdown → npm run build → git push → GitHub/Gitee Pages 上线
```
