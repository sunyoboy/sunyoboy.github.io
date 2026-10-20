# ⛔ 已禁用：fix-ljg-org-to-md

## 为什么禁用

这个技能会**扫描 skills 目录、批量修改输出格式、然后自动 `git commit`**。
属于无人确认的写操作，且本项目全程使用 Markdown，没有 org-mode 转换需求。

## 禁用方式

- 目录改名为 `fix-ljg-org-to-md-DISABLED`
- `SKILL.md` 改名为 `SKILL.md.disabled` → DSH 扫描不到

## 如需重新启用

```bash
cd .agents/skills/fix-ljg-org-to-md-DISABLED
mv SKILL.md.disabled SKILL.md
cd ..
mv fix-ljg-org-to-md-DISABLED fix-ljg-org-to-md
```
