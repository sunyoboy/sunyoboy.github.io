#!/usr/bin/env bash
# 统一入口：用仓库内置的 Bun 运行技能里的 TypeScript 工具
#
# 用法：
#   ./.agents/skills/.toolchain/run.sh <工具.ts> [参数...]
#
# 例：
#   ./.agents/skills/.toolchain/run.sh .agents/skills/ljg-is/Tools/ValidateNote.ts note.md
#
# 为什么需要它：
#   1) ljg 系列工具用了 Bun 专有 API（Bun.file / Bun.write / Bun.CryptoHasher），
#      标准 Node 跑不了（会报 "Bun is not defined"）
#   2) ljg-card / ljg-classic 依赖 playwright，浏览器装在仓库内，
#      必须通过 PLAYWRIGHT_BROWSERS_PATH 指过去
set -euo pipefail
TC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PLAYWRIGHT_BROWSERS_PATH="$TC_DIR/ms-playwright"
exec "$TC_DIR/bin/bun" "$@"
