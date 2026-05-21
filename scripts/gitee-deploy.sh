#!/bin/bash
# Gitee Pages 部署脚本
# 用法: bash scripts/gitee-deploy.sh

set -e

echo "=== 安装依赖 ==="
npm ci

echo "=== 构建站点 ==="
npm run build

echo "=== 构建完成 ==="
echo "dist 目录: .vitepress/dist/"
echo ""
echo "=== Gitee Pages 部署步骤 ==="
echo "1. 将代码推送到 Gitee: git push gitee main"
echo "2. 登录 Gitee → 进入仓库 → 服务 → Gitee Pages"
echo "3. 部署目录填写: .vitepress/dist"
echo "4. 点击「更新」按钮触发部署"
echo ""
echo "注意: Gitee Pages 免费版每次推送后需手动点击更新。"
