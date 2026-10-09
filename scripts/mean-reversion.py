#!/usr/bin/env python3
"""
均值回归（Mean Reversion）全景诊断。

核心逻辑：价格对中期均值的偏离，在统计上具有回归倾向。
  ① 偏离幅度  — z = (P - MA60) / σ60   （回归力度）
  ② 超买超卖  — RSI14                    （动能极限）
  ③ 位置      — 距 120 日低/高           （回归空间）
  ④ 长期结构  — MA60 - MA250 / 距 250 低  （决定是"回调"还是"趋势破坏"）

判定原则：
  均值回归 ≠ 越跌越买。长期结构完好 + 短期深度负偏离 = 买点；
  长期结构已破 + 深度负偏离 = 均值下移（下跌趋势），不是买点而是卖点。

用法：python3 scripts/mean-reversion.py
数据源：腾讯财经日 K 线（前复权，500 根）
"""

import json
import time
import urllib.request
from datetime import datetime

# ── 关注池：持仓 + 候选池 ────────────────────────────────
POOL = {
    # 现有持仓（2026-10-08 复盘）
    "sh510500": "中证500ETF",
    "sh518800": "黄金ETF",
    "sz002230": "科大讯飞",
    "sz002532": "天山铝业",
    "sh601899": "紫金矿业",
    "sz002149": "西部材料",
    "sh512400": "有色ETF",
    "sh563230": "卫星ETF",
    "sh510300": "沪深300ETF",
    "sz159915": "创业板ETF",
    "sh588000": "科创50ETF",
    "sz159992": "创新药ETF",
    "sz512100": "中证1000ETF",
    "sh515220": "煤炭ETF",
    "sh600111": "北方稀土",
    "sh600276": "恒瑞医药",
    "sz000001": "平安银行",
    "sz000651": "格力电器",
    "sh601288": "农业银行",
    # 候选池 — 红利/防守
    "sh520890": "红利低波ETF",
    "sh512800": "银行ETF",
    "sh515170": "食品饮料ETF",
    "sh510880": "红利ETF",
    "sh563020": "红利低波100",
    # 候选池 — 资源/周期
    "sh561360": "石油ETF",
    "sh562800": "稀土ETF",
    "sh516150": "电池ETF",
    # 候选池 — 科技/成长
    "sh513130": "恒生科技ETF",
    "sh512760": "芯片ETF",
    "sh515050": "通信ETF",
    "sh512010": "医药ETF",
    "sh513120": "港股创新药ETF",
    "sh159611": "电力ETF",
    "sh512660": "军工ETF",
    "sh516970": "基建ETF",
    "sh159766": "旅游ETF",
    "sh512690": "酒ETF",
    # 指数（结构参考）
    "sh000001": "上证指数",
    "sh000300": "沪深300",
    "sh000905": "中证500",
    "sh000852": "中证1000",
    "sz399006": "创业板指",
    "sh000688": "科创50",
    # 利率/债
    "sh511090": "30年国债ETF",
    "sh511010": "国债ETF",
    "sh511260": "十年国债ETF",
}


def fetch_kline(code, days=500):
    url = (f"http://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
           f"?param={code},day,,,{days},qfq")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    data = raw["data"][code]
    klines = data.get("qfqday") or data.get("day")
    if not klines:
        raise ValueError("no kline")
    out = []
    for k in klines:
        out.append({
            "date": k[0], "open": float(k[1]), "close": float(k[2]),
            "high": float(k[3]), "low": float(k[4]),
            "volume": float(k[5]) if len(k) > 5 else 0.0,
        })
    return out


def ma(vals, n):
    return sum(vals[-n:]) / n if len(vals) >= n else None


def stdev(vals, n):
    if len(vals) < n:
        return None
    seg = vals[-n:]
    m = sum(seg) / n
    return (sum((x - m) ** 2 for x in seg) / n) ** 0.5


def rsi(closes, n=14):
    if len(closes) < n + 1:
        return None
    gains, losses = [], []
    for i in range(-n, 0):
        chg = closes[i] - closes[i - 1]
        gains.append(max(chg, 0.0))
        losses.append(max(-chg, 0.0))
    ag, al = sum(gains) / n, sum(losses) / n
    if al == 0:
        return 100.0
    rs = ag / al
    return 100 - 100 / (1 + rs)


def analyze(code, name, klines):
    closes = [k["close"] for k in klines]
    lows = [k["low"] for k in klines]
    highs = [k["high"] for k in klines]
    p = closes[-1]

    ma20, ma60, ma120, ma250 = ma(closes, 20), ma(closes, 60), ma(closes, 120), ma(closes, 250)
    sd60 = stdev(closes, 60)
    sd120 = stdev(closes, 120)

    z60 = (p - ma60) / sd60 if sd60 else None
    z120 = (p - ma120) / sd120 if sd120 else None
    dev20 = (p - ma20) / ma20 * 100 if ma20 else None
    dev60 = (p - ma60) / ma60 * 100 if ma60 else None
    dev250 = (p - ma250) / ma250 * 100 if ma250 else None

    low120, high120 = min(lows[-120:]), max(highs[-120:])
    low250 = min(lows[-250:]) if len(lows) >= 250 else min(lows)
    high250 = max(highs[-250:]) if len(highs) >= 250 else max(highs)
    dist_lo120 = (p - low120) / low120 * 100
    dist_hi120 = (p - high120) / high120 * 100
    dist_lo250 = (p - low250) / low250 * 100
    dist_hi250 = (p - high250) / high250 * 100

    r = rsi(closes, 14)

    # 布林带（60日）位置：0=下轨 1=上轨
    upper = ma60 + 2 * sd60 if sd60 and ma60 else None
    lower = ma60 - 2 * sd60 if sd60 and ma60 else None
    bb = (p - lower) / (upper - lower) if upper and lower and upper != lower else None

    # 长期结构
    struct = "长期多头" if ma60 and ma250 and ma60 > ma250 else "长期空头"
    # 距 250 日低位置
    pos250 = (p - low250) / (high250 - low250) * 100 if high250 != low250 else None

    return {
        "name": name, "code": code, "date": klines[-1]["date"], "price": p,
        "z60": z60, "z120": z120, "dev20": dev20, "dev60": dev60, "dev250": dev250,
        "rsi": r, "bb": bb,
        "dist_lo120": dist_lo120, "dist_hi120": dist_hi120,
        "dist_lo250": dist_lo250, "pos250": pos250,
        "ma20": ma20, "ma60": ma60, "ma250": ma250,
        "struct": struct,
        "low120": low120, "high120": high120,
    }


def main():
    rows, fails = [], []
    for code, name in POOL.items():
        if name == "—":
            continue
        try:
            k = fetch_kline(code)
            if len(k) < 130:
                fails.append((name, code, f"数据不足 {len(k)}"))
                continue
            rows.append(analyze(code, name, k))
        except Exception as e:
            fails.append((name, code, str(e)[:60]))
        time.sleep(0.15)

    print(f"\n## 均值回归全景 · 数据日 {rows[0]['date'] if rows else '—'}\n")
    hdr = ("| 标的 | 现价 | z60 | z120 | dev20 | dev60 | RSI14 | 布林位 | "
           "距120低 | 距120高 | 距250低 | 250区间位 | 结构 |")
    print(hdr)
    print("|" + "---|" * 13)
    for r in sorted(rows, key=lambda x: (x["z60"] if x["z60"] is not None else 0)):
        print("| {name} | {price:.3f} | {z60:+.2f} | {z120:+.2f} | {dev20:+.1f}% | "
              "{dev60:+.1f}% | {rsi:.0f} | {bb:.0%} | {dl:+.1f}% | {dh:+.1f}% | "
              "{d250:+.1f}% | {pos250:.0f}% | {struct} |".format(
                  name=r["name"], price=r["price"], z60=r["z60"], z120=r["z120"],
                  dev20=r["dev20"], dev60=r["dev60"], rsi=r["rsi"], bb=r["bb"],
                  dl=r["dist_lo120"], dh=r["dist_hi120"], d250=r["dist_lo250"],
                  pos250=r["pos250"], struct=r["struct"]))

    print("\n### 深度负偏离（z60 < -1.5）— 均值回归候选\n")
    for r in sorted(rows, key=lambda x: x["z60"]):
        if r["z60"] < -1.5:
            print(f"- **{r['name']}** z60={r['z60']:+.2f} RSI={r['rsi']:.0f} "
                  f"距120低={r['dist_lo120']:+.1f}% 结构={r['struct']} "
                  f"距250低={r['dist_lo250']:+.1f}%")

    print("\n### 极端超买（z60 > +1.5 或 RSI > 70）\n")
    for r in sorted(rows, key=lambda x: -(x["z60"] or 0)):
        if r["z60"] > 1.5 or (r["rsi"] and r["rsi"] > 70):
            print(f"- **{r['name']}** z60={r['z60']:+.2f} RSI={r['rsi']:.0f} "
                  f"距120高={r['dist_hi120']:+.1f}% 结构={r['struct']}")

    if fails:
        print("\n### 抓取失败\n")
        for n, c, e in fails:
            print(f"- {n} ({c}): {e}")

    with open("scripts/mean-reversion-data.json", "w") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
