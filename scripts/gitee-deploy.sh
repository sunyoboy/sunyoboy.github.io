#!/bin/bash
# 站点部署脚本（Gitee Pages 已于2024年暂停服务，仅保留构建功能）
# 用法: bash scripts/gitee-deploy.sh

set -e

echo "=== 安装依赖 ==="
npm ci

echo "=== 构建站点 ==="
npm run build

echo "=== 构建完成 ==="
echo "dist 目录: .vitepress/dist/"
echo ""
echo "=== 部署渠道 ==="
echo "GitHub Pages: git push github main → Actions 自动部署"
echo "  → https://sunyoboy.github.io"
echo ""
echo "⚠️  Gitee Pages 已于2024年暂停服务，无需再推送 Gitee。"
