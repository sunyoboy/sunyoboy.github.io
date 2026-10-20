# 技能工具链（本地，不入库）

这些文件体积大，已在 `.gitignore` 中排除，**不会提交**。

## 内容

| 文件 | 体积 | 用途 |
|---|---:|---|
| `bin/bun` | 67 MB | Bun 运行时（ljg 工具使用 Bun 专有 API） |
| `ms-playwright/` | 522 MB | Chromium（ljg-card / ljg-classic 渲染用） |

## 为什么是 Bun 而不是 Node

ljg 系列的 13 个工具用了 Bun 专有 API：
`Bun.file`(38) · `Bun.write`(32) · `Bun.CryptoHasher`(7) · `Bun.spawnSync`(6) · `Bun.spawn`(4) · `Bun.argv`(4)

用 Node 跑会直接报 `Bun is not defined`。

## 用法

```bash
# 统一入口（自动设置 PLAYWRIGHT_BROWSERS_PATH）
./.agents/skills/.toolchain/run.sh <工具.ts> [参数...]
```

## 重建（换机器时）

```bash
mkdir -p .agents/skills/.toolchain/bin
curl -sL https://github.com/oven-sh/bun/releases/latest/download/bun-darwin-aarch64.zip -o /tmp/bun.zip
unzip -q /tmp/bun.zip -d /tmp && cp /tmp/bun-darwin-aarch64/bun .agents/skills/.toolchain/bin/ && chmod +x .agents/skills/.toolchain/bin/bun

cd .agents/skills/ljg-card && ../.toolchain/bin/bun install
cd ../ljg-classic && ../.toolchain/bin/bun install

export PLAYWRIGHT_BROWSERS_PATH="$PWD/.agents/skills/.toolchain/ms-playwright"
cd .agents/skills/ljg-card && ../.toolchain/bin/bun x playwright install chromium
```
