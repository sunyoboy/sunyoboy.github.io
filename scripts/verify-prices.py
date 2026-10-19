#!/usr/bin/env python3
"""
防串价自动核对 —— 替代 CLAUDE.md 里那张会腐烂的硬编码价格区间表。

为什么要有它：
    旧做法是人工把当天收盘价和一张写死的区间表逐项比对。指数从 3000 点走到
    3730 点后，那张表全面失效，15 项里 13 项"超出区间"，但没有任何一项真的
    串价。长期如此，人会训练出"习惯性点过"的动作，等真串价时反而发现不了。

现在的做法：不比绝对值，只比**自洽性**。绝对价格会随行情漂移，而下面四条
关系在任何点位上都必须成立：

    C1 字段自洽：涨跌幅字段 与 (现价/昨收-1) 必须一致
    C2 数据新鲜：接口返回的时间戳必须是今天（否则是拿了上一交易日快照）
    C3 量级合理：现价/昨收 必须落在 0.7 ~ 1.4 之间
    C4 历史一致：现价与上一次记录相比跳变不得超过 25%（超过＝可能串价或除权）
    C5 均线一致：现价偏离 20 日均价不得超过 35%

C1/C2/C3 失败 = 阻断（数据本身不可信，禁止开写复盘）
C4/C5 告警 = 需人工判断（可能是除权、可能是串价）

用法：
    python3 scripts/verify-prices.py            # 核对并更新基线
    python3 scripts/verify-prices.py --dry-run  # 只核对，不更新基线

退出码：
    0 = 全部通过（允许有告警）
    1 = 存在阻断级异常
"""

import json
import os
import sys
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTFOLIO = os.path.join(ROOT, "scripts", "portfolio.json")
BASELINE = os.path.join(ROOT, "scripts", "price_baseline.json")

# 阈值
PCT_CONSISTENCY_TOL = 0.35      # C1：涨跌幅字段与计算值容差（百分点）
JUMP_WARN = 0.25                # C4：与上次记录相比跳变告警线
MA20_WARN = 0.35                # C5：偏离 MA20 告警线
RATIO_LO, RATIO_HI = 0.70, 1.40  # C3：现价/昨收 合理区间


def load_holdings():
    with open(PORTFOLIO, encoding="utf-8") as f:
        data = json.load(f)
    return [(h["code"], h["name"]) for h in data.get("holdings", [])
            if h.get("code") and h.get("name")]


def fetch_quote(code):
    """腾讯实时行情：现价 / 昨收 / 涨跌幅 / 时间戳"""
    url = f"https://qt.gtimg.cn/q={code}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        d = resp.read().decode("gbk").split("~")
    if len(d) < 33:
        raise ValueError(f"字段不足（{len(d)}）")
    return {
        "close": float(d[3]),
        "prev": float(d[4]),
        "pct": float(d[32]),
        "api_dt": d[30],
    }


def fetch_ma20(code):
    """取前复权日线算 MA20"""
    url = (f"http://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
           f"?param={code},day,,,30,qfq")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    node = raw.get("data", {}).get(code, {})
    rows = node.get("qfqday") or node.get("day") or []
    closes = [float(r[2]) for r in rows if len(r) > 2]
    if len(closes) < 20:
        return None
    return sum(closes[-20:]) / 20


def load_baseline():
    try:
        with open(BASELINE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_baseline(data):
    tmp = BASELINE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, BASELINE)


def main():
    dry = "--dry-run" in sys.argv
    today = datetime.now().strftime("%Y-%m-%d")
    holdings = load_holdings()
    base = load_baseline()

    print(f"🔍 防串价自动核对 · {today} · {len(holdings)} 个标的")
    print("   范围：C1 字段自洽 / C2 数据新鲜 / C3 量级 / C4 历史一致 / C5 均线一致\n")

    rows, blockers, warns, new_base = [], [], [], {}
    for code, name in holdings:
        rec = {"code": code, "name": name}
        try:
            q = fetch_quote(code)
        except Exception as e:
            blockers.append(f"{name} 取价失败：{e}")
            rows.append((name, "—", "❌ 阻断", f"取价失败 {e}"))
            continue

        close, prev, pct = q["close"], q["prev"], q["pct"]
        rec.update({"close": close, "date": today, "api_dt": q["api_dt"]})
        problems, notes = [], []

        # C1 字段自洽
        if prev > 0:
            calc = (close / prev - 1) * 100
            if abs(calc - pct) > PCT_CONSISTENCY_TOL:
                problems.append(f"C1 涨跌幅字段 {pct:+.2f}% ≠ 计算值 {calc:+.2f}%")
        else:
            problems.append("C1 昨收为 0，无法校验")

        # C2 数据新鲜
        stamp = q["api_dt"].replace("-", "").replace(" ", "")[:8]
        if stamp != today.replace("-", ""):
            problems.append(f"C2 时间戳 {stamp} 非今日（可能是上一交易日快照）")

        # C3 量级
        if prev > 0:
            ratio = close / prev
            if not (RATIO_LO <= ratio <= RATIO_HI):
                problems.append(f"C3 现价/昨收 = {ratio:.2f}，超出 {RATIO_LO}~{RATIO_HI}")

        # C4 历史一致（跨几次运行）
        old = base.get(code)
        if old and old.get("close") and old.get("date") != today:
            jump = close / old["close"] - 1
            if abs(jump) > JUMP_WARN:
                notes.append(f"C4 较上次({old['date']}) 跳变 {jump:+.1%}（疑除权或串价）")

        # C5 均线一致
        try:
            ma20 = fetch_ma20(code)
            if ma20:
                dev = close / ma20 - 1
                rec["ma20"] = round(ma20, 4)
                if abs(dev) > MA20_WARN:
                    notes.append(f"C5 偏离 MA20 {dev:+.1%}（>{MA20_WARN:.0%}）")
        except Exception as e:
            notes.append(f"C5 均线取数失败：{e}")

        if problems:
            status = "❌ 阻断"
            blockers.extend(f"{name}：{p}" for p in problems)
        elif notes:
            status = "⚠️ 告警"
            warns.extend(f"{name}：{n}" for n in notes)
        else:
            status = "✅ 通过"

        detail = "；".join(problems + notes) or f"自洽（{pct:+.2f}%）"
        rows.append((name, f"{close}", status, detail))
        new_base[code] = rec

    # 输出表格
    w = max((len(r[0]) for r in rows), default=8)
    print(f"  {'标的':<{w}}  {'现价':>9}  {'状态':<6}  说明")
    print("  " + "-" * (w + 9 + 8 + 40))
    for name, px, status, detail in rows:
        print(f"  {name:<{w}}  {px:>9}  {status:<6}  {detail[:80]}")

    print()
    if blockers:
        print(f"❌ 阻断级异常 {len(blockers)} 项（数据不可信，禁止开写复盘）：")
        for b in blockers:
            print(f"   · {b}")
    if warns:
        print(f"⚠️  需人工判断 {len(warns)} 项：")
        for w_ in warns:
            print(f"   · {w_}")
    if not blockers and not warns:
        print("✅ 全部通过：字段自洽、数据新鲜、量级与均线均正常")

    if not dry and new_base and not blockers:
        save_baseline(new_base)
        print(f"\n💾 基线已更新 → {os.path.relpath(BASELINE, ROOT)}")
    elif blockers:
        print("\n⚠️  存在阻断级异常，基线**未**更新（避免把坏数据写成基准）")
    elif dry:
        print("\n（--dry-run：未更新基线）")

    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
