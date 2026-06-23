#!/usr/bin/env python3
"""
持仓标的均线偏离度全景诊断。
三维指标：偏离方向 + 持续时间 + 价格位置

数据源：腾讯财经 K 线 API（前复权）

用法：
  python3 scripts/ma5-deviation.py

输出：
  1. 全景指标表（三指标维度一览）
  2. 综合操作建议（按优先级排列）
"""

import urllib.request
import json

# ── 当前持仓标的 ──────────────────────────────────────────
HOLDINGS = {
    "sh510500": "中证500ETF",
    "sh518800": "黄金基金",
    "sz002230": "科大讯飞",
    "sz002532": "天山铝业",
    "sh601899": "紫金矿业",
    "sh512400": "有色ETF",
    "sh563230": "卫星ETF",
}

# ── 关键支撑/阻力位（手动维护，与低吸区间一致）────────────
KEY_ZONES = {
    "中证500ETF":  {"low": 8.75, "support": 8.79},
    "黄金基金":    {"low": 9.05, "support": 9.09},
    "科大讯飞":    {"low": 42.85, "support": 43.00},
    "天山铝业":    {"low": 11.99, "support": 12.05},
    "紫金矿业":    {"low": 29.08, "support": 29.21},
    "有色ETF":     {"low": 2.05, "support": 2.06},
    "卫星ETF":     {"low": 1.35, "support": 1.35},  # 止损线
}


# ═══════════════════════════════════════════════════════════
# 数据获取
# ═══════════════════════════════════════════════════════════

def fetch_kline(code, days=120):
    """从腾讯财经 API 获取日 K 线数据（前复权），返回升序 list[dict]"""
    try:
        url = (
            f"http://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
            f"?param={code},day,,,{days},qfq"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ❌ {code}: 请求失败 — {e}")
        return None

    try:
        data = raw["data"][code]
        if data is None:
            url2 = (
                f"http://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
                f"?param={code},day,,,{days},"
            )
            req2 = urllib.request.Request(url2, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req2, timeout=15) as resp2:
                raw2 = json.loads(resp2.read().decode("utf-8"))
            data = raw2["data"][code]

        klines = data.get("qfqday", data.get("day"))
        if not klines:
            return None

        result = []
        for k in klines:
            result.append({
                "date": k[0],
                "open":  float(k[1]),
                "close": float(k[2]),
                "high":  float(k[3]),
                "low":   float(k[4]),
                "volume": float(k[5]) if len(k) > 5 else 0,
            })
        return result
    except Exception as e:
        print(f"  ❌ {code}: 解析失败 — {e}")
        return None


# ═══════════════════════════════════════════════════════════
# 指标计算
# ═══════════════════════════════════════════════════════════

def ma(values, n):
    """n 日均值"""
    if len(values) < n:
        return None
    return sum(values[-n:]) / n


def consecutive_days(klines, condition_fn):
    """从最近往前数，连续满足 condition_fn 的天数"""
    count = 0
    for k in reversed(klines):
        if condition_fn(k):
            count += 1
        else:
            break
    return count


def calc_all_indicators(klines):
    """
    输入升序 K 线列表（≥60 条），输出全景指标 dict。
    返回 None 表示数据不足。
    """
    if len(klines) < 60:
        return None

    closes = [k["close"] for k in klines]

    # ── 均线 ──────────────────────────────────────────
    ma5_val  = ma(closes, 5)
    ma20_val = ma(closes, 20)
    ma60_val = ma(closes, 60)
    current  = closes[-1]

    # ── 偏离度（三维度之①：方向）────────────────────
    dev5  = (current - ma5_val)  / ma5_val  * 100 if ma5_val  else None
    dev20 = (current - ma20_val) / ma20_val * 100 if ma20_val else None
    dev60 = (current - ma60_val) / ma60_val * 100 if ma60_val else None

    # ── 持续时间（三维度之②）─────────────────────────
    # 连续在 MA5 上方（收盘 > MA5）
    above_ma5_days = consecutive_days(klines, lambda k: k["close"] > ma5_val)
    # 连续在 MA5 下方（收盘 < MA5）
    below_ma5_days = consecutive_days(klines, lambda k: k["close"] < ma5_val)

    # 偏离趋势：用绝对偏离度判断是扩大还是收窄
    last_3 = closes[-3:] if len(closes) >= 3 else closes
    if len(last_3) >= 3 and ma5_val:
        dev_3d_ago = (last_3[0] - ma5_val) / ma5_val * 100
        dev_now    = (last_3[-1] - ma5_val) / ma5_val * 100
        abs_old = abs(dev_3d_ago)
        abs_new = abs(dev_now)
        delta = abs_new - abs_old  # >0 意味着离均线更远了（真·扩大）
        if abs(delta) < 0.3:
            dev_trend = "→ 持平"
        elif delta > 0:
            dev_trend = f"📈 扩大 +{delta:.1f}pp"
        else:
            dev_trend = f"📉 收窄 {delta:.1f}pp"
    else:
        dev_trend = "—"

    # ── 价格位置（三维度之③）─────────────────────────
    # MA5 vs MA20 交叉
    ma5_cross_ma20 = "金叉 ▲" if ma5_val and ma20_val and ma5_val > ma20_val else "死叉 ▼"

    # MA20 vs MA60（中期趋势背景）
    trend_bg = "中期多头" if ma20_val and ma60_val and ma20_val > ma60_val else "中期空头"

    # 距 20 日高 / 低点
    high_20 = max(k["high"] for k in klines[-20:])
    low_20  = min(k["low"]  for k in klines[-20:])
    dist_from_high = (current - high_20) / high_20 * 100 if high_20 else None
    dist_from_low  = (current - low_20)  / low_20  * 100 if low_20  else None

    # 距 60 日高 / 低点
    high_60 = max(k["high"] for k in klines[-60:])
    low_60  = min(k["low"]  for k in klines[-60:])
    dist_from_high60 = (current - high_60) / high_60 * 100 if high_60 else None
    dist_from_low60  = (current - low_60)  / low_60  * 100 if low_60  else None

    # 量能趋势（近 5 日 vs 近 20 日均量）
    vol_5  = ma([k["volume"] for k in klines], 5)
    vol_20 = ma([k["volume"] for k in klines], 20)
    vol_ratio = vol_5 / vol_20 if vol_20 and vol_20 > 0 else None

    return {
        "date":        klines[-1]["date"],
        "current":     round(current, 3),
        "ma5":         round(ma5_val, 3) if ma5_val else None,
        "ma20":        round(ma20_val, 3) if ma20_val else None,
        "ma60":        round(ma60_val, 3) if ma60_val else None,
        "dev5":        round(dev5, 2) if dev5 is not None else None,
        "dev20":       round(dev20, 2) if dev20 is not None else None,
        "dev60":       round(dev60, 2) if dev60 is not None else None,
        "above_days":  above_ma5_days,
        "below_days":  below_ma5_days,
        "dev_trend":   dev_trend,
        "cross":       ma5_cross_ma20,
        "trend_bg":    trend_bg,
        "high_20":     round(high_20, 3),
        "low_20":      round(low_20, 3),
        "dist_hi20":   round(dist_from_high, 2) if dist_from_high is not None else None,
        "dist_lo20":   round(dist_from_low, 2) if dist_from_low is not None else None,
        "high_60":     round(high_60, 3),
        "low_60":      round(low_60, 3),
        "dist_hi60":   round(dist_from_high60, 2) if dist_from_high60 is not None else None,
        "dist_lo60":   round(dist_from_low60, 2) if dist_from_low60 is not None else None,
        "vol_ratio":   round(vol_ratio, 2) if vol_ratio is not None else None,
    }


# ═══════════════════════════════════════════════════════════
# 信号生成
# ═══════════════════════════════════════════════════════════

def direction_signal(ind):
    """维度① 偏离方向 → 信号文字"""
    d = ind["dev5"]
    if d is None:
        return "—", "—"
    if d > 5:
        return "🔴 正偏·高危", "大幅高于 MA5，均线引力极强"
    elif d > 2:
        return "🟡 正偏·偏热", "高于 MA5，注意回踩风险"
    elif d > -2:
        return "🟢 贴合·均衡", "价格围绕均线，方向待选"
    elif d > -5:
        return "🟡 负偏·偏冷", "低于 MA5，超跌待反弹"
    else:
        return "🔵 负偏·冰点", "大幅低于 MA5，极端超跌"


def duration_signal(ind):
    """维度② 持续时间 → 信号文字"""
    days = ind["above_days"] or ind["below_days"] or 0
    trend = ind["dev_trend"]

    if ind["above_days"] and ind["above_days"] > 0:
        if "扩大" in trend:
            return (
                f"🟡 连涨 {days} 日 + 偏离扩大",
                "趋势加速中，暂不宜逆势减仓，等放量滞涨"
            )
        elif "收窄" in trend:
            return (
                f"🟢 连涨 {days} 日但偏离收窄",
                "动能减弱，可考虑止盈/减仓"
            )
        else:
            return (f"🟢 连涨 {days} 日", "趋势运行中，观察")

    elif ind["below_days"] and ind["below_days"] > 0:
        if "扩大" in trend:
            return (
                f"🔴 连跌 {days} 日 + 偏离扩大",
                "下跌加速，反弹即减仓窗口，勿抄底"
            )
        elif "收窄" in trend:
            return (
                f"🟡 连跌 {days} 日但偏离收窄",
                "超跌修复中，等反弹至 MA5 附近再决策"
            )
        else:
            return (f"🟡 连跌 {days} 日", "持续偏弱，观察是否企稳")

    return ("🟢 均线附近", "无持续偏离")


def position_signal(ind):
    """维度③ 价格位置 → 信号文字"""
    signals = []

    # 1. MA5/MA20 交叉
    if ind["cross"] == "金叉 ▲":
        signals.append("✅ MA5↑MA20 金叉")
    else:
        signals.append("❌ MA5↓MA20 死叉")

    # 2. 中期趋势
    if ind["trend_bg"] == "中期多头":
        signals.append("✅ 中期多头（MA20>MA60）")
    else:
        signals.append("⚠️ 中期空头（MA20<MA60）")

    # 3. 距 20 日低点
    dl = ind["dist_lo20"]
    if dl is not None and dl < 3:
        signals.append(f"⚡ 距 20 日低仅 +{dl}%")
    elif dl is not None and dl > 10:
        signals.append(f"📌 距 20 日低已 +{dl}%")

    # 4. 距 20 日高点
    dh = ind["dist_hi20"]
    if dh is not None and dh > -3:
        signals.append(f"⚡ 接近 20 日高（{dh}%）")
    elif dh is not None and dh < -10:
        signals.append(f"📌 距 20 日高 {dh}%")

    # 5. 成交量
    vr = ind["vol_ratio"]
    if vr is not None and vr > 1.5:
        signals.append("📊 放量（5日均量>1.5×20日均量）")
    elif vr is not None and vr < 0.6:
        signals.append("📊 缩量（5日均量<0.6×20日均量）")

    return " | ".join(signals) if signals else "—"


def composite_action(ind, name):
    """
    综合三维度指标 → 操作建议。
    返回 (优先级标签, 操作建议, 是否紧急)
    """
    d = ind["dev5"]
    above = ind["above_days"] or 0
    below = ind["below_days"] or 0
    cross = ind["cross"]
    trend_bg = ind["trend_bg"]
    trend = ind["dev_trend"]
    dl = ind["dist_lo20"] or 999
    dh = ind["dist_hi20"] or -999

    # ── 清仓条件 ──────────────────────────────────
    # 条件：MA5 死叉 MA20 + 中期空头 + 偏离 < -5% + 连续下跌 5+
    if cross == "死叉 ▼" and trend_bg == "中期空头" and d is not None and d < -5 and below >= 5:
        return ("🔴 清仓", "三重空头共振 — 死叉+空头趋势+持续下跌，清仓离场", True)

    # 条件：偏离 < -8% + 偏离扩大 + 放量
    if d is not None and d < -8 and "扩大" in trend:
        return ("🔴 清仓", "极端超跌且加速中，不等反弹直接清仓", True)

    # 条件：反弹触及 MA5 后再度回落，破前低
    if below >= 3 and d is not None and d < -3 and dl is not None and dl < 1:
        return ("🔴 减至观察仓", "贴近 20 日低，一旦跌破将加速，减至 1/4", True)

    # ── 减仓条件 ──────────────────────────────────
    # 条件：正偏离 > +5% + 偏离收窄（动能见顶）
    if d is not None and d > 5 and "收窄" in trend:
        return ("🟡 减仓 1/2", "正偏离过大且动能衰减，减半锁利，留底仓等回踩", False)

    # 条件：正偏离 > +3% + 接近 20 日高
    if d is not None and d > 3 and dh is not None and dh > -3:
        return ("🟡 减仓 1/3", "接近近期高点 + 偏离偏大，减 1/3 降风险", False)

    # 条件：负偏离 < -5% + 连续下跌 + 死叉
    if d is not None and d < -5 and below >= 3 and cross == "死叉 ▼":
        return ("🟡 反弹减仓", f"连跌 {below} 日偏离 {d}%，反弹至 MA5 附近减 1/2", False)

    # ── 持有观察 ──────────────────────────────────
    # 条件：贴合均线 + 金叉
    if d is not None and abs(d) < 2 and cross == "金叉 ▲":
        return ("🟢 持有", "价格健康，均线多头排列，无操作", False)

    # 条件：负偏离 < -3% + 偏离收窄（超跌修复中）
    if d is not None and d < -3 and "收窄" in trend:
        return ("🟢 持有等弹", "超跌但偏离在收窄，反弹概率↑，等 MA5 附近再决策", False)

    # ── 默认 ──────────────────────────────────────
    return ("🟢 观察", "无明显信号，按兵不动", False)


# ═══════════════════════════════════════════════════════════
# 主输出
# ═══════════════════════════════════════════════════════════

def main():
    print("# 持仓标的均线偏离度 · 全景诊断\n")
    print(f"> 三维指标：**偏离方向**（价格 vs MA5）· **持续时间**（连续偏向天数 + 趋势）· **价格位置**（MA20/MA60/高低点/量能）\n")

    # ── 表 1：三维指标全景 ────────────────────────────
    print("## 一、三维指标全景\n")
    print(
        "| 标的 | 现价 | 偏离度 | 方向信号 | "
        "连续偏向 | 偏离趋势 | "
        "MA5/MA20 | 中期背景 | 距20低 | 量能 |"
    )
    print(
        "|------|:----:|:------:|------|"
        "------|------|"
        "------|------|:--:|:--:|"
    )

    results = {}
    for code, name in HOLDINGS.items():
        symbol = code[2:]
        print(f"  📡 {name} ...", end=" ", flush=True)
        klines = fetch_kline(code, days=120)
        if not klines:
            print("❌")
            results[name] = None
            continue

        ind = calc_all_indicators(klines)
        if ind is None:
            print("⚠️ 数据不足")
            results[name] = None
            continue

        results[name] = ind
        dir_label, _ = direction_signal(ind)
        dur_label, _ = duration_signal(ind)

        vol_str = f"{ind['vol_ratio']}x" if ind["vol_ratio"] else "—"
        dl_str  = f"+{ind['dist_lo20']}%" if ind["dist_lo20"] is not None else "—"

        print(f"✅ {ind['current']}  dev5={ind['dev5']:+.1f}%")

        print(
            f"| {name} | {ind['current']} | "
            f"{ind['dev5']:+.2f}% | {dir_label} | "
            f"{dur_label} | {ind['dev_trend']} | "
            f"{ind['cross']} | {ind['trend_bg']} | "
            f"{dl_str} | {vol_str} |"
        )

    # ── 表 2：补充数据（MA20/MA60 偏离 + 高低点）─────
    print(f"\n## 二、均线与关键价位\n")
    print(
        "| 标的 | MA5 | MA20 | MA60 | "
        "偏离20 | 偏离60 | "
        "20日高 | 20日低 | 关键支撑 |"
    )
    print(
        "|------|:---:|:----:|:----:|"
        ":-----:|:-----:|"
        ":-----:|:-----:|------|"
    )

    for name, ind in results.items():
        if ind is None:
            print(f"| {name} | — | — | — | — | — | — | — | — |")
            continue

        zone = KEY_ZONES.get(name, {})
        support_str = str(zone.get("support", "—")) if zone else "—"

        print(
            f"| {name} | {ind['ma5']} | {ind['ma20']} | {ind['ma60']} | "
            f"{ind['dev20']:+.1f}% | {ind['dev60']:+.1f}% | "
            f"{ind['high_20']} | {ind['low_20']} | {support_str} |"
        )

    # ── 表 3：综合操作建议 ───────────────────────────
    print(f"\n## 三、综合操作建议\n")
    urgent_items = []
    normal_items = []

    for name, ind in results.items():
        if ind is None:
            continue
        action = composite_action(ind, name)
        item = (action[0], name, action[1])
        if action[2]:  # 紧急
            urgent_items.append(item)
        else:
            normal_items.append(item)

    if urgent_items:
        print("### ⚡ 紧急操作\n")
        for label, name, advice in urgent_items:
            print(f"- **{label}** — {name}：{advice}")

    if normal_items:
        print("\n### 📋 常规操作\n")
        for label, name, advice in normal_items:
            print(f"- **{label}** — {name}：{advice}")

    # ── 附录：指标名词解释 ────────────────────────────
    print(f"\n---\n")
    print("### 📖 指标说明\n")
    print("| 指标 | 含义 |")
    print("|------|------|")
    print("| **偏离度** | (现价 − MA5) ÷ MA5 × 100%，正=价格高于均线，负=低于均线 |")
    print("| **连续偏向** | 收盘价连续在 MA5 上方(正)或下方(负)的交易日数 |")
    print("| **偏离趋势** | 最近 3 个交易日偏离度的变化方向：扩大=加速，收窄=减速 |")
    print("| **金叉/死叉** | MA5 上穿/下穿 MA20，金叉=短期走强，死叉=短期走弱 |")
    print("| **中期背景** | MA20 vs MA60 的位置关系，决定大方向是多是空 |")
    print("| **距20低/高** | 当前价距 20 日最低/最高点的百分比，衡量短期位置 |")
    print("| **量能** | 5日均量 ÷ 20日均量：>1.5 放量，<0.6 缩量 |")
    print()
    print("> 📎 详细纪律：见 [`docs/ma5-deviation-discipline.md`](../docs/ma5-deviation-discipline.md)")


if __name__ == "__main__":
    main()
