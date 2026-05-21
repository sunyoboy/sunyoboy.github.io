# 部署指南

## 前置准备

### 1. 创建仓库

| 平台 | 仓库名 |
|------|--------|
| GitHub | `<username>.github.io` |
| Gitee | `<username>` (用于 `<username>.gitee.io`) |

> 若使用 `<username>.github.io` 则不需要配置 `base`，否则需在 `config.mjs` 中设置 `base: '/<repo>/'`。

### 2. 配置 remote

```bash
git remote add github git@github.com:<username>/<repo>.git
git remote add gitee  git@gitee.com:<username>/<repo>.git
```

---

## GitHub Pages

**自动部署**，推送即上线。

1. 仓库 Settings → Pages → Source → **GitHub Actions**
2. 推送 `main` 分支，`.github/workflows/deploy.yml` 自动运行
3. 访问 `https://<username>.github.io`

---

## Gitee Pages

**手动部署**（免费版）。

1. `git push gitee main`
2. 仓库 → 服务 → Gitee Pages
3. 部署目录：`.vitepress/dist`
4. 点击 **更新**，访问 `https://<username>.gitee.io`

> 需实名认证。每次推送后手动点击更新。付费版支持自动部署。

---

## 日常推送

```bash
git push github main && git push gitee main
```
