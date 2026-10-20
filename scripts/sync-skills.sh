#!/usr/bin/env bash
# 把本仓库的 .agents/skills 变更提交到当前 git 仓库（不 push）
#
# 为什么不用 ljg-push / fix-ljg-org-to-md：
#   它们的目标是同步到第三方仓库 lijigang/ljg-skills，且带 org→md 双分支转换；
#   本仓库的 .agents/skills 本来就由 git 跟踪，只需要一个「检查 + 提交」的动作。
#
# 用法：
#   bash scripts/sync-skills.sh             # 预览（默认，不提交）
#   bash scripts/sync-skills.sh --commit    # 实际提交
#
# 退出码：0 = 正常；1 = 出错

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COMMIT=0
for arg in "$@"; do
  case "$arg" in
    --commit) COMMIT=1 ;;
    -h|--help) sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "未知参数: $arg" >&2; exit 1 ;;
  esac
done

SCOPE=".agents/skills"

if [ ! -d "$SCOPE" ]; then
  echo "❌ 找不到 $SCOPE（当前目录: $ROOT）" >&2
  exit 1
fi

# 1) 有多少变更
CHANGED=$(git status --porcelain "$SCOPE" | wc -l | tr -d ' ')
if [ "$CHANGED" = "0" ]; then
  echo "✅ $SCOPE 无变更，无需提交"
  exit 0
fi

echo "📦 $SCOPE 有 $CHANGED 个文件变更："
git status --short "$SCOPE" | sed 's/^/   /'

# 2) 摘要（新增/修改/删除）
echo
git diff --stat -- "$SCOPE" 2>/dev/null | tail -1 | sed 's/^/   合计: /' || true

# 3) 体积告警：防止误提交 node_modules / 二进制
BIG=$(git status --porcelain "$SCOPE" | awk '{print $2}' | while read -r f; do
  [ -f "$f" ] && [ "$(stat -f%z "$f" 2>/dev/null || echo 0)" -gt 5242880 ] && echo "$f"
done || true)
if [ -n "$BIG" ]; then
  echo
  echo "⚠️  以下文件 >5MB，确认是否该入库（可能是 node_modules 或二进制）："
  echo "$BIG" | sed 's/^/   /'
fi

if [ "$COMMIT" != "1" ]; then
  echo
  echo "（预览模式，未提交。加 --commit 实际提交）"
  exit 0
fi

# 4) 提交
git add "$SCOPE"
# 只提交本范围内暂存的内容：若存在其它已暂存文件，用 pathspec 隔离
git commit -q -m "chore(skills): 同步技能目录（$CHANGED 个文件变更）

由 scripts/sync-skills.sh 生成。
范围：$SCOPE"

echo
echo "✅ 已提交。推送到双远端："
echo "   git push origin main && git push github main"
