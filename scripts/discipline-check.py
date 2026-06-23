#!/usr/bin/env python3
"""
投资纪律指标自动化检查。

数据源：
  - 新浪财经 API → 成交量/成交额（万元→亿归一化）
  - 腾讯财经 API → 实时价格
  - scripts/portfolio.json → 个人持仓
  - scripts/discipline_history.json → 历史积累（自动回填）

用法：
  python3 scripts/discipline-check.py              # 市场公共指标
  python3 scripts/discipline-check.py --portfolio  # 含个人持仓检查
  python3 scripts/discipline-check.py --json       # JSON 输出
"""

import sys, os, json, urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTFOLIO_FILE = os.path.join(ROOT, "scripts", "portfolio.json")
HISTORY_FILE = os.path.join(ROOT, "scripts", "discipline_history.json")

# ═══════════════════════════════════════════════════════════
# 新浪 API（成交量/成交额）
# 字段: [0]名称 [1]现价 [2]涨跌额 [3]% [4]成交量(手) [5]成交额(万元)
# ═══════════════════════════════════════════════════════════

SINA_INDICES = {
    "s_sh000001": "上证指数", "s_sz399001": "深证成集",
    "s_sz399006": "创业板指", "s_sh000688": "科创50",
}
SINA_REAL = {"s_sh000001": "上证指数", "s_sz399001": "深证成指"}

def fetch_sina(code):
    try:
        url = f"https://hq.sinajs.cn/list={code}"
        req = urllib.request.Request(url, headers={"Referer": "https://finance.sina.com.cn"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            parts = resp.read().decode("gbk").split('"')[1].split(",")
            if len(parts) >= 6:
                return {
                    "price": round(float(parts[1]), 2),
                    "pct_chg": round(float(parts[3]), 2),
                    "volume": int(parts[4]),
                    "turnover_yi": round(int(parts[5]) / 10000, 2),  # 万元→亿
                }
    except: pass
    return None

def fetch_sina_market_turnover():
    """上证+深证成交额合计（亿）"""
    total = 0
    for code in SINA_REAL:
        d = fetch_sina(code)
        if d and d["turnover_yi"] > 0:
            total += d["turnover_yi"]
    return total if total > 0 else None

def fetch_international_gold():
    try:
        d = fetch_sina("hf_XAU")
        return d["price"] if d else None
    except: return None

# ═══════════════════════════════════════════════════════════
# 腾讯 API（价格）
# ═══════════════════════════════════════════════════════════

TENCENT_INDICES = {
    "sh000001": "上证指数", "sz399001": "深证成指", "sz399006": "创业板指",
    "sh000688": "科创50", "sh000016": "上证50", "sh000300": "沪深300", "sh000905": "中证500",
}
WATCHLIST = {
    "sh510500": "中证500ETF", "sh518800": "黄金ETF",
    "sz002230": "科大讯飞", "sz002532": "天山铝业",
    "sh601899": "紫金矿业", "sh512400": "有色ETF",
}

def fetch_tencent(code):
    try:
        url = f"https://qt.gtimg.cn/q={code}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode("gbk").split("~")
            if len(data) > 32:
                return {
                    "price": round(float(data[3]), 2),
                    "prev_close": round(float(data[4]), 2),
                    "pct_chg": round(float(data[32]), 2),
                    "high": round(float(data[33]), 2) if len(data) > 33 and data[33] else None,
                    "low": round(float(data[34]), 2) if len(data) > 34 and data[34] else None,
                }
    except: pass
    return None

def fetch_all_tencent(symbols):
    results = {}
    for code, name in symbols.items():
        d = fetch_tencent(code)
        if d: results[name] = d
    return results

# ═══════════════════════════════════════════════════════════
# 历史数据
# ═══════════════════════════════════════════════════════════

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f: return json.load(f)
    return {"records": []}

def save_history(h):
    h["records"] = h["records"][-120:]
    with open(HISTORY_FILE, "w") as f: json.dump(h, f, ensure_ascii=False, indent=2)

def record_today(h, index_data, stock_data, turnover_yi):
    today = datetime.now().strftime("%Y-%m-%d")
    rec = {"date": today, "indices": {}, "stocks": {}}
    for name, d in index_data.items():
        if d and d.get("price"):
            rec["indices"][name] = {"close": d["price"], "pct": d["pct_chg"]}
    for name, d in stock_data.items():
        if d and d.get("price"):
            rec["stocks"][name] = {"close": d["price"], "pct": d["pct_chg"]}
    if turnover_yi:
        rec["turnover_yi"] = turnover_yi
        rec["turnover_source"] = "sina_realtime"   # 与 review 同尺度（全市场合计）

    # 去重同一天
    if h["records"] and h["records"][-1].get("date") == today:
        h["records"][-1] = rec
    else:
        h["records"].append(rec)

# ═══════════════════════════════════════════════════════════
# 指标计算（统一使用 turnover_yi 字段，亿）
# ═══════════════════════════════════════════════════════════

def calc_volume_emotion(history):
    """成交额情绪 = 今日 ÷ 近20日均。仅使用同尺度数据源（review + sina_realtime，排除 sina_kline）。"""
    records = history.get("records", [])
    # 过滤：排除 sina_kline 源（单指数尺度，与全市场不可比）
    valid = [r.get("turnover_yi") for r in records
             if r.get("turnover_yi") and r.get("turnover_source") != "sina_kline"]
    if len(valid) < 5:
        # 回退：使用所有源（可能有尺度偏差但至少给出参考值）
        valid2 = [r.get("turnover_yi") for r in records if r.get("turnover_yi")]
        if len(valid2) >= 5:
            today, avg20 = valid2[-1], sum(valid2[-20:]) / min(len(valid2), 20)
            return round(today / avg20, 2), "⚠️ 含不同尺度数据，仅供参考"
        return None, f"成交额数据不足（{len(valid2)}/5天）"
    today, avg20 = valid[-1], sum(valid[-20:]) / min(len(valid), 20)
    return round(today / avg20, 2), None

def calc_amplitude_3d(history, name):
    records = history.get("records", [])
    if len(records) < 3: return None
    prices = [r.get("stocks", {}).get(name, {}).get("close") for r in records[-3:]]
    prices = [p for p in prices if p]
    if len(prices) < 3: return None
    hi, lo = max(prices), min(prices)
    return round((hi - lo) / lo * 100, 1)

def calc_volatility_20d(history, name):
    records = history.get("records", [])
    prices = [r.get("stocks", {}).get(name, {}).get("close") for r in records[-20:]]
    prices = [p for p in prices if p]
    if len(prices) < 5: return None
    mean = sum(prices) / len(prices)
    var = sum((p - mean) ** 2 for p in prices) / len(prices)
    return round((var ** 0.5) / mean * 100, 1)

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE) as f: return json.load(f)
    return None

# ═══════════════════════════════════════════════════════════
# 输出
# ═══════════════════════════════════════════════════════════

G = "\033[92m"; R = "\033[91m"; Y = "\033[93m"; X = "\033[0m"; B = "\033[1m"
def ok(s): return f"{G}{s}{X}"
def wrn(s): return f"{Y}{s}{X}"
def bad(s): return f"{R}{s}{X}"
def bld(s): return f"{B}{s}{X}"

def print_report(index_data, stock_data, history, pf, gold_intl, turnover_yi):
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{B}═══════════════════════════════════════════{X}")
    print(f"{B}  投资纪律指标检查 · {today}{X}")
    print(f"{B}═══════════════════════════════════════════{X}\n")

    records = history.get("records", [])
    n_yi = len([r for r in records if r.get("turnover_yi")])

    # ═══ 1. 管住手 ═══
    print(f"{B}【一、管住手】{X}")
    print(f"  原则：不在情绪高潮点开仓，不在高波动期追涨\n")

    emotion, em_note = calc_volume_emotion(history)
    if emotion:
        note = f" {wrn(em_note)}" if em_note else ""
        label = ok(f"{emotion:.2f} 🟢") if emotion < 1.3 else (
                bad(f"{emotion:.2f} 🔴 高潮日，不开新仓") if emotion >= 1.5 else
                wrn(f"{emotion:.2f} 🟡 偏热，谨慎"))
        print(f"  成交额情绪:    {label}{note}  (阈值 < 1.3 / > 1.5 红灯)")
        if turnover_yi:
            recent_same = [r for r in records if r.get("turnover_yi") and r.get("turnover_source") != "sina_kline"]
            valid_yi = [r["turnover_yi"] for r in recent_same[-20:]]
            if valid_yi:
                avg20 = sum(valid_yi) / len(valid_yi)
                print(f"                今日= {turnover_yi:,.0f}亿  近{len(valid_yi)}日均= {avg20:,.0f}亿")
    else:
        if turnover_yi:
            print(f"  成交额情绪:    {wrn('— (' + em_note + ')')}")
            print(f"                今日= {turnover_yi:,.0f}亿（已采集 {n_yi} 天）")
        else:
            print(f"  成交额情绪:    {wrn('— (未获取到成交额)')}")

    # 三日振幅
    has_amp = False
    for name in ["天山铝业", "紫金矿业", "有色ETF"]:
        amp = calc_amplitude_3d(history, name)
        if amp is not None:
            has_amp = True
            s = bad(f"{amp}% 🔴 禁止") if amp > 15 else (wrn(f"{amp}% 🟡 谨慎") if amp > 8 else ok(f"{amp}% 🟢"))
            print(f"  三日振幅({name}): {s}  (阈值 < 8% / > 15% 红灯)")
    if not has_amp:
        print(f"  三日振幅:      {wrn('— (历史数据不足 3 天)')}")

    print(f"  追涨惩罚率:    {wrn('— (需涨停股列表)')}")
    print(f"  数据源:        新浪(成交额) + 腾讯(价格)\n")

    # ═══ 2. 控仓位 ═══
    print(f"{B}【二、控仓位】{X}")
    print(f"  原则：单品种 ≤ 10%，同板块 ≤ 20%，现金 ≥ 50%\n")

    if pf:
        total = pf["total_assets"]; cash = pf.get("cash", 0)
        cash_pct = round(cash / total * 100, 1)

        pos_vals, sec_vals = {}, {}
        for h in pf.get("holdings", []):
            stk = stock_data.get(h["name"], {})
            price = stk.get("price") if stk else None
            if price and h["shares"]:
                val = price * h["shares"]
                pos_vals[h["name"]] = val
                sec_vals.setdefault(h.get("sector", "其他"), 0)
                sec_vals[h.get("sector", "其他")] += val

        for name, val in pos_vals.items():
            pct = round(val / total * 100, 1)
            s = bad(f"{pct}% 🔴") if pct > 20 else (wrn(f"{pct}% 🟡") if pct > 10 else ok(f"{pct}% 🟢"))
            print(f"  单品种({name}): {s}")
        print()
        for sec, val in sec_vals.items():
            pct = round(val / total * 100, 1)
            s = bad(f"{pct}% 🔴") if pct > 30 else (wrn(f"{pct}% 🟡") if pct > 20 else ok(f"{pct}% 🟢"))
            print(f"  板块合计({sec}): {s}")
        print()
        cs = bad(f"{cash_pct}% 🔴") if cash_pct < 40 else (wrn(f"{cash_pct}% 🟡 偏保守") if cash_pct > 70 else ok(f"{cash_pct}% 🟢"))
        print(f"  现金水位:      {cs}  (阈值 ≥ 50% / < 40% 红灯)\n")

        print(f"  高风险品种（近20日波动率 > 3%）:")
        found = False
        for h in pf.get("holdings", []):
            vol = calc_volatility_20d(history, h["name"])
            if vol is not None and vol > 3:
                print(f"    {bad(h['name'] + ': ' + str(vol) + '% → 仓位减半')}")
                found = True
        if not found:
            print(f"    {ok('无')}" if n_yi >= 5 else f"    {wrn('— (历史不足 5 天)')}")
    else:
        print(f"  {wrn('(需 --portfolio)')}")
    print()

    # ═══ 3. 别加杠杆 ═══
    print(f"{B}【三、别加杠杆】{X}")
    print(f"  原则：普通投资者杠杆倍数为 0\n")
    if pf:
        lev = pf.get("margin_debt", 0)
        ls = ok("0 🟢") if lev == 0 else bad(f"有杠杆!")
        print(f"  个人杠杆:      {ls}")
        print(f"\n  极端压力测试（再跌 20%）：")
        for h in pf.get("holdings", []):
            stk = stock_data.get(h["name"], {})
            price = stk.get("price") if stk else None
            if price and h["shares"]:
                lpct = round(price * h["shares"] * 0.2 / pf["total_assets"] * 100, 1)
                t = ok(f"-{lpct}%") if lpct < 2 else (wrn(f"-{lpct}%") if lpct < 5 else bad(f"-{lpct}%"))
                print(f"    {h['name']}: {t} 对总资产影响")
    else:
        print(f"  {wrn('(需 --portfolio)')}")
    print()

    # ═══ 4. 黄金 ═══
    print(f"{B}【四、黄金 = 配置非投机】{X}")
    print(f"  原则：5-10% 资产占比，季度再平衡\n")

    gold_stk = stock_data.get("黄金ETF", {})
    gold_price = gold_stk.get("price") if gold_stk else None

    if pf and gold_price:
        total = pf["total_assets"]
        gold_sh = sum(h["shares"] for h in pf.get("holdings", []) if h["name"] == "黄金ETF")
        gold_val = gold_price * gold_sh
        gold_pct = round(gold_val / total * 100, 1)
        target = round(pf.get("target_allocation", {}).get("黄金", 0.07) * 100, 1)

        gs = ok(f"{gold_pct}% 🟢") if 5 <= gold_pct <= 10 else (
             wrn(f"{gold_pct}% 🟡") if 3 <= gold_pct <= 12 else bad(f"{gold_pct}% 🔴"))
        print(f"  黄金ETF:       ¥{gold_price}  占比 {gs}  (目标 {target}%)")
        if gold_intl: print(f"  国际金价:      ${gold_intl:,.1f}/oz")

        dev = round(gold_pct - target, 1)
        if abs(dev) > 2:
            act = "卖出" if dev > 0 else "买入"
            print(f"  {bad(f'⚠️ 触发再平衡: {act} 约 ¥{abs(dev)/100*total:,.0f}')}  (偏离 {dev:+.1f}%)")
        else:
            print(f"  偏离目标:      {dev:+.1f}%  {ok('未触发再平衡')}")
        print(f"\n  投机检测:      盯盘=每日 → {wrn('投机模式风险')}  建议改为季度检查")
    else:
        if gold_price: print(f"  黄金ETF:       ¥{gold_price}")
        if gold_intl:  print(f"  国际金价:      ${gold_intl:,.1f}/oz")
    print()

    # ═══ 汇总 ═══
    issues = 1 if (emotion and emotion >= 1.5) else 0
    print(f"{B}═══════════════════════════════════════════{X}")
    print(f"{B}  检查完成 · {ok('全部绿灯 ✅') if issues == 0 else bad(f'{issues} 项警报')}{X}")
    print(f"{B}═══════════════════════════════════════════{X}\n")
    if n_yi < 5:
        print(f"  ⚠️ 成交额历史仅 {n_yi} 天（需 ≥5 天），每日运行自动积累。\n")

# ═══════════════════════════════════════════════════════════
# main
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    use_pf = "--portfolio" in sys.argv or "-p" in sys.argv
    json_out = "--json" in sys.argv

    # 腾讯 — 指数+标的价格
    index_data = fetch_all_tencent(TENCENT_INDICES)
    stock_data = fetch_all_tencent(WATCHLIST)

    # 新浪 — 成交额 + 国际金价
    turnover_yi = fetch_sina_market_turnover()
    gold_intl = fetch_international_gold()

    # 持仓
    pf = load_portfolio() if use_pf else None
    if pf:
        extra = {}
        for h in pf.get("holdings", []):
            if h["name"] not in stock_data and h.get("code"):
                extra[h["code"]] = h["name"]
        if extra:
            stock_data.update(fetch_all_tencent(extra))

    # 历史
    history = load_history()
    record_today(history, index_data, stock_data, turnover_yi)
    save_history(history)

    if json_out:
        rep = {"date": datetime.now().strftime("%Y-%m-%d"),
               "turnover_yi": turnover_yi,
               "emotion": calc_volume_emotion(history)[0],
               "gold_intl": gold_intl}
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print_report(index_data, stock_data, history, pf, gold_intl, turnover_yi)
