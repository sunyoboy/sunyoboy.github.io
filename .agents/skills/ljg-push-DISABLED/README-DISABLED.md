# ⛔ 已禁用：ljg-push

## 为什么禁用

这个技能会把你本地的 `~/.agents/skills/ljg-*` **推送到第三方仓库**
`github.com/lijigang/ljg-skills`（别人的仓库），并且是**误触即执行**的写操作。

你没有该仓库的写权限，实际执行会报错；但如果哪天权限变化，或脚本行为改动，
风险不可控。因此默认禁用。

## 禁用方式

- 目录改名为 `ljg-push-DISABLED`
- `SKILL.md` 改名为 `SKILL.md.disabled` → **DSH 扫描不到，不会出现在技能目录里**

## 如需重新启用

```bash
cd .agents/skills/ljg-push-DISABLED
mv SKILL.md.disabled SKILL.md
cd ..
mv ljg-push-DISABLED ljg-push
```

⚠️ 重新启用前请先读一遍 `SKILL.md` 里的 `git push` 目标仓库，确认那真的是你想推的地方。
