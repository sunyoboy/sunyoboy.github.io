#!/usr/bin/env bash
# 把本仓库的 .agents/skills 发布到独立的 skills 仓库（sunyoboy-skills）
#
# 与 sync-skills.sh 的区别：
#   sync-skills.sh     → 提交到**当前仓库**（ThinkingDoing）
#   publish-skills.sh  → 镜像到**独立仓库** sunyoboy-skills（可移植到任意项目）
#
# 用法：
#   bash scripts/publish-skills.sh              # 生成/更新本地镜像（不推送）
#   bash scripts/publish-skills.sh --push       # 镜像 + 推送
#   bash scripts/publish-skills.sh --dry-run    # 只看会同步什么
#
# 环境变量：
#   SKILLS_REPO   本地镜像目录，默认 ~/code/sunyoboy-skills
#   SKILLS_REMOTE 远端地址，默认 git@github.com:sunyoboy/sunyoboy-skills.git
#
# 排除项（体积大 / 环境相关）：
#   node_modules/  .toolchain/bin/  .toolchain/ms-playwright/

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/.agents/skills"
DEST="${SKILLS_REPO:-$HOME/code/sunyoboy-skills}"
REMOTE="${SKILLS_REMOTE:-git@github.com:sunyoboy/sunyoboy-skills.git}"

PUSH=0
DRY=0
for arg in "$@"; do
  case "$arg" in
    --push)    PUSH=1 ;;
    --dry-run) DRY=1 ;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "未知参数: $arg" >&2; exit 1 ;;
  esac
done

[ -d "$SRC" ] || { echo "❌ 找不到源目录: $SRC" >&2; exit 1; }

EXCLUDES=(
  --exclude='node_modules/'
  --exclude='.toolchain/bin/'
  --exclude='.toolchain/ms-playwright/'
  --exclude='.DS_Store'
  --exclude='.git/'
)

echo "源   : $SRC"
echo "镜像 : $DEST"
echo "远端 : $REMOTE"
echo

# ── 0. dry-run：只列出会同步的文件 ──────────────────────
if [ "$DRY" = "1" ]; then
  echo "=== 将同步的内容（预览）==="
  rsync -an --itemize-changes "${EXCLUDES[@]}" "$SRC/" "$DEST/skills/" 2>/dev/null | head -30 || true
  echo "…"
  echo "（--dry-run 结束，未写入）"
  exit 0
fi

# ── 1. 初始化镜像仓库 ──────────────────────────────────
mkdir -p "$DEST"
if [ ! -d "$DEST/.git" ]; then
  echo "🆕 初始化镜像仓库"
  git -C "$DEST" init -q
  git -C "$DEST" branch -M main 2>/dev/null || true
  git -C "$DEST" remote add origin "$REMOTE" 2>/dev/null || true
else
  git -C "$DEST" remote get-url origin >/dev/null 2>&1 || git -C "$DEST" remote add origin "$REMOTE"
fi

# ── 2. 同步文件 ────────────────────────────────────────
echo "🔄 同步 .agents/skills → $DEST/skills"
mkdir -p "$DEST/skills"
rsync -a --delete "${EXCLUDES[@]}" "$SRC/" "$DEST/skills/"

# ── 3. 生成 README（每次覆盖，保持与内容一致）───────────
ACTIVE=$(find "$DEST/skills" -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')
DISABLED=$(find "$DEST/skills" -maxdepth 2 -name SKILL.md.disabled | wc -l | tr -d ' ')

cat > "$DEST/README.md" <<EOF
# sunyoboy-skills

个人 AI Skill 集合（Agent Skills 标准 · \`SKILL.md\`）。

- **可用**：${ACTIVE} 个
- **已禁用**：${DISABLED} 个（\`SKILL.md.disabled\`，不会被自动发现）

## 安装到其他项目

DSH 的发现路径（按优先级）：

| Rank | 路径 |
|:--:|---|
| 100 | \`<项目根>/.dsh/skills\` |
| 200 | \`<项目根>/.agents/skills\` ← 推荐 |
| 400 | \`~/.dsh/skills\` |
| 500 | \`~/.agents/skills\` |

\`\`\`bash
# 项目级安装（推荐）
git clone https://github.com/sunyoboy/sunyoboy-skills.git /tmp/skills
mkdir -p .agents && cp -R /tmp/skills/skills .agents/skills

# 或全用户安装
cp -R /tmp/skills/skills/* ~/.agents/skills/
\`\`\`

## 需要运行时的技能

部分技能带 \`Tools/*.ts\`，依赖 **Bun**（用了 \`Bun.file\`/\`Bun.write\` 等专有 API，Node 跑不了）。
\`.toolchain/run.sh\` 是统一入口，重建步骤见 \`.toolchain/README.md\`。

## 来源与授权

| 来源 | 许可 |
|---|---|
| 自有技能 | 私有 |
| [ljigang/ljg-skills](https://github.com/lijigang/ljg-skills) | MIT（各目录内 LICENSE） |

> 本仓库由 \`scripts/publish-skills.sh\` 从主仓库镜像生成，**请勿直接在此编辑**。
EOF

# ── 4. 提交 ────────────────────────────────────────────
cd "$DEST"
git add -A
if git diff --cached --quiet; then
  echo "✅ 无变更，跳过提交"
else
  git -c user.name="${GIT_AUTHOR_NAME:-sunyoboy}" \
      -c user.email="${GIT_AUTHOR_EMAIL:-sunyoboy@users.noreply.github.com}" \
      commit -q -m "sync: ${ACTIVE} 个技能（$(date +%F)）"
  echo "✅ 已提交"
  git log --oneline -1
fi

# ── 5. 推送 ────────────────────────────────────────────
if [ "$PUSH" = "1" ]; then
  echo
  echo "🚀 推送到 $REMOTE"
  if git push -u origin main 2>&1; then
    echo "✅ 推送成功"
  else
    cat <<'MSG' >&2

❌ 推送失败。最常见原因：**远端仓库还不存在**。

请先去创建空仓库（不要勾选 README/.gitignore）：
  https://github.com/new?name=sunyoboy-skills

创建后重新执行：
  bash scripts/publish-skills.sh --push
MSG
    exit 1
  fi
else
  echo
  echo "（未推送。确认无误后加 --push）"
fi
