#!/usr/bin/env python3
"""
投资纪律指标自动化检查。

数据源：
  - 腾讯财经 API → 实时价格
  - 新浪财经 API → 成交量/成交额 → 成交额情绪
  - scripts/portfolio.json → 个人持仓
  - scripts/discipline_history.json → 历史积累

用法：
  python3 scripts/discipline-check.py              # 市场公共指标
  python3 scripts/discipline-check.py --portfolio  # 含个人持仓检查
  python3 scripts/discipline-check.py --json       # JSON 输出
"""

import sys
import os
import json
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTFOLIO_FILE = os.path.join(ROOT, "scripts", "portfolio.json")
HISTORY_FILE = os.path.join(ROOT, "scripts", "discipline_history.json")

# ── 新浪财经 API ──────────────────────────────────────────
# 返回 6 字段: name, price, change, pct, volume(手), turnover(百元)
# turnover 原始单位推测为百元，计算结果仅用比值（单位无关）

SINA_INDICES = {
    "s_sh000001": "上证指数",
    "s_sz399001": "深证成指",
    "s_sz399006": "创业板指",
    "s_sh000688": "科创50",
}

def fetch_sina_index(code):
    """从新浪获取指数行情（含成交额）"""
    try:
        url = f"https://hq.sinajs.cn/list={code}"
        req = urllib.request.Request(url, headers={"Referer": "https://finance.sina.com.cn"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("gbk")
            parts = raw.split('"')[1].split(",")
            if len(parts) >= 6:
                return {
                    "name": parts[0],
                    "price": round(float(parts[1]), 2),
                    "change": round(float(parts[2]), 2),
                    "pct_chg": round(float(parts[3]), 2),
                    "volume": int(parts[4]),       # 手
                    "turnover": int(parts[5]),     # 百元（推测）
                }
    except Exception as e:
        return {"name": code, "error": str(e)}
    return None


def fetch_sina_all():
    results = {}
    for code, name in SINA_INDICES.items():
        d = fetch_sina_index(code)
        if d and d.get("price"):
            results[name] = d
    return results


# ── 腾讯财经 API ──────────────────────────────────────────

def fetch_price(code):
    """从腾讯获取单只标的价格"""
    try:
        url = f"https://qt.gtimg.cn/q={code}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("gbk")
            data = raw.split("~")
            if len(data) > 32:
                return {
                    "name": data[1],
                    "price": round(float(data[3]), 2),
                    "prev_close": round(float(data[4]), 2),
                    "pct_chg": round(float(data[32]), 2),
                    "high": round(float(data[33]), 2) if len(data) > 33 and data[33] else None,
                    "low": round(float(data[34]), 2) if len(data) > 34 and data[34] else None,
                }
    except:
        return None
    return None


def fetch_batch(codes):
    results = {}
    for code, label in codes.items():
        info = fetch_price(code)
        if info:
            results[label] = info
    return results


# ── 历史数据管理 ──────────────────────────────────────────

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"records": []}


def save_history(h):
    h["records"] = h["records"][-120:]
    with open(HISTORY_FILE, "w") as f:
        json.dump(h, f, ensure_ascii=False, indent=2)


def record_today(h, index_data, stock_data, sina_data):
    today = datetime.now().strftime("%Y-%m-%d")
    rec = {"date": today, "indices": {}, "stocks": {}}

    for name, d in index_data.items():
        if d and d.get("price"):
            rec["indices"][name] = {"close": d["price"], "pct": d["pct_chg"]}

    for name, d in stock_data.items():
        if d and d.get("price"):
            rec["stocks"][name] = {"close": d["price"], "pct": d["pct_chg"]}

    # 新增：成交额数据
    total_turnover = 0
    for name, d in sina_data.items():
        if d and d.get("turnover") and d["turnover"] > 0:
            total_turnover += d["turnover"]
    rec["total_turnover"] = total_turnover

    if h["records"] and h["records"][-1].get("date") == today:
        h["records"][-1] = rec
    else:
        h["records"].append(rec)


# ── 指标计算 ──────────────────────────────────────────────

def calc_volume_emotion(history):
    """成交额情绪 = 今日成交额 ÷ 近20日均成交额"""
    records = history.get("records", [])
    if len(records) < 5:
        return None, "历史数据不足（需 5 天以上）"

    today = records[-1].get("total_turnover", 0)
    if today == 0:
        return None, "今日成交额缺失"

    recent = [r.get("total_turnover", 0) for r in records[-20:]]
    recent = [v for v in recent if v > 0]
    if len(recent) < 5:
        return None, "历史成交额数据不足"

    avg = sum(recent) / len(recent)
    return round(today / avg, 2), None


def calc_amplitude_3d(history, name):
    """个股三日振幅"""
    records = history.get("records", [])
    if len(records) < 3:
        return None
    recent = records[-3:]
    prices = [r.get("stocks", {}).get(name, {}).get("close") for r in recent]
    prices = [p for p in prices if p]
    if len(prices) < 3:
        return None
    hi, lo = max(prices), min(prices)
    return round((hi - lo) / lo * 100, 1)


def calc_volatility_20d(history, name):
    """近20日波动率（标准差/均值 %）"""
    records = history.get("records", [])
    prices = [r.get("stocks", {}).get(name, {}).get("close") for r in records[-20:]]
    prices = [p for p in prices if p]
    if len(prices) < 5:
        return None
    mean = sum(prices) / len(prices)
    variance = sum((p - mean) ** 2 for p in prices) / len(prices)
    return round((variance ** 0.5) / mean * 100, 1)


def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        return None
    with open(PORTFOLIO_FILE, "r") as f:
        return json.load(f)


# ── 输出 ──────────────────────────────────────────────────

GREEN = "\033[92m"; RED = "\033[91m"; YELLOW = "\033[93m"; RESET = "\033[0m"; BOLD = "\033[1m"

def ok(s):   return f"{GREEN}{s}{RESET}"
def warn(s): return f"{YELLOW}{s}{RESET}"
def bad(s):  return f"{RED}{s}{RESET}"


def print_report(index_data, stock_data, sina_data, history, pf):
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{BOLD}═══════════════════════════════════════════{RESET}")
    print(f"{BOLD}  投资纪律指标检查 · {today}{RESET}")
    print(f"{BOLD}═══════════════════════════════════════════{RESET}\n")

    records = history.get("records", [])
    n_days = len([r for r in records if r.get("total_turnover", 0) > 0])

    # ═══ 1. 管住手 ═══
    print(f"{BOLD}【一、管住手】{RESET}")
    print(f"  原则：不在情绪高潮点开仓，不在高波动期追涨\n")

    # 成交额情绪
    emotion, em_note = calc_volume_emotion(history)
    if emotion:
        label = ok(f"{emotion:.2f} 🟢") if emotion < 1.3 else (
               bad(f"{emotion:.2f} 🔴 高潮日，不开新仓") if emotion >= 1.5 else
               warn(f"{emotion:.2f} 🟡 偏热，谨慎"))
        print(f"  成交额情绪:    {label}  (阈值 < 1.3 / > 1.5 红灯)")
        # 原始成交额
        if records and records[-1].get("total_turnover"):
            raw = records[-1]["total_turnover"]
            recent = [r.get("total_turnover", 0) for r in records[-20:] if r.get("total_turnover", 0) > 0]
            avg_t = sum(recent) / len(recent) if recent else 0
            print(f"                今日总额= {raw:,.0f}  近{n_days}日均= {avg_t:,.0f}")
    else:
        # 至少展示今日成交额
        if records and records[-1].get("total_turnover"):
            raw = records[-1]["total_turnover"]
            print(f"  成交额情绪:    {warn('— (' + em_note + ')')}")
            print(f"                今日总额= {raw:,.0f}（积累中，已采集 {n_days} 天）")
        else:
            print(f"  成交额情绪:    {warn('— (未获取到成交额数据)')}")

    # 三日振幅
    has_amp = False
    for name in ["天山铝业", "紫金矿业", "有色ETF"]:
        amp = calc_amplitude_3d(history, name)
        if amp is not None:
            has_amp = True
            status = bad(f"{amp}% 🔴 禁止") if amp > 15 else (
                     warn(f"{amp}% 🟡 谨慎") if amp > 8 else ok(f"{amp}% 🟢"))
            print(f"  三日振幅({name}): {status}  (阈值 < 8% / > 15% 红灯)")
    if not has_amp:
        print(f"  三日振幅:      {warn('— (历史数据不足 3 天)')}")

    # 追涨惩罚率
    print(f"  追涨惩罚率:    {warn('— (需接口: 涨停股列表)')}")

    # 数据源
    print(f"  数据源:        新浪财经(成交额) + 腾讯财经(价格)")
    print()

    # ═══ 2. 控仓位 ═══
    print(f"{BOLD}【二、控仓位】{RESET}")
    print(f"  原则：单品种 ≤ 10%，同板块 ≤ 20%，现金 ≥ 50%\n")

    if pf:
        total = pf["total_assets"]
        cash = pf.get("cash", 0)
        cash_pct = round(cash / total * 100, 1)

        position_values = {}
        sector_values = {}

        for h in pf.get("holdings", []):
            stk = stock_data.get(h["name"], {})
            price = stk.get("price") if stk else None
            if price and h["shares"]:
                val = price * h["shares"]
                position_values[h["name"]] = val
                sector_values.setdefault(h.get("sector", "其他"), 0)
                sector_values[h.get("sector", "其他")] += val

        for name, val in position_values.items():
            pct = round(val / total * 100, 1)
            s = bad(f"{pct}% 🔴") if pct > 20 else (warn(f"{pct}% 🟡") if pct > 10 else ok(f"{pct}% 🟢"))
            print(f"  单品种({name}): {s}")

        print()
        for sec, val in sector_values.items():
            pct = round(val / total * 100, 1)
            s = bad(f"{pct}% 🔴") if pct > 30 else (warn(f"{pct}% 🟡") if pct > 20 else ok(f"{pct}% 🟢"))
            print(f"  板块合计({sec}): {s}")

        print()
        cs = bad(f"{cash_pct}% 🔴") if cash_pct < 40 else (
             warn(f"{cash_pct}% 🟡 偏保守") if cash_pct > 70 else ok(f"{cash_pct}% 🟢"))
        print(f"  现金水位:      {cs}  (阈值 ≥ 50% / < 40% 红灯)")

        print()
        print(f"  高风险品种（近20日波动率 > 3%）:")
        found = False
        for h in pf.get("holdings", []):
            vol = calc_volatility_20d(history, h["name"])
            if vol is not None and vol > 3:
                print(f"    {bad(h['name'] + ': ' + str(vol) + '% → 仓位减半')}")
                found = True
        if not found:
            print(f"    {ok('无')}" if n_days >= 5 else f"    {warn('— (历史数据不足 5 天)')}")
    else:
        print(f"  {warn('(需 --portfolio)')}")
    print()

    # ═══ 3. 别加杠杆 ═══
    print(f"{BOLD}【三、别加杠杆】{RESET}")
    print(f"  原则：普通投资者杠杆倍数为 0\n")

    if pf:
        lev = pf.get("margin_debt", 0)
        lpct = round(lev / pf["total_assets"] * 100, 1) if pf["total_assets"] > 0 else 0
        ls = ok("0 🟢") if lev == 0 else bad(f"{lpct}% 🔴 有杠杆!")
        print(f"  个人杠杆:      {ls}")

        print()
        print(f"  极端压力测试（各品种再跌 20%）：")
        for h in pf.get("holdings", []):
            stk = stock_data.get(h["name"], {})
            price = stk.get("price") if stk else None
            if price and h["shares"]:
                loss_pct = round(price * h["shares"] * 0.2 / pf["total_assets"] * 100, 1)
                tag = ok(f"-{loss_pct}%") if loss_pct < 2 else (warn(f"-{loss_pct}%") if loss_pct < 5 else bad(f"-{loss_pct}%"))
                print(f"    {h['name']}: {tag} 对总资产影响")
    else:
        print(f"  {warn('(需 --portfolio)')}")
    print()

    # ═══ 4. 黄金 ═══
    print(f"{BOLD}【四、黄金 = 配置非投机】{RESET}")
    print(f"  原则：5-10% 资产占比，季度再平衡\n")

    gold_stk = stock_data.get("黄金ETF", {})
    gold_price = gold_stk.get("price") if gold_stk else None

    # 也查国际金价（sina hf_GC）
    international_gold = None
    try:
        url = "https://hq.sinajs.cn/list=hf_XAU"
        req = urllib.request.Request(url, headers={"Referer": "https://finance.sina.com.cn"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("gbk")
            parts = raw.split('"')[1].split(",")
            if len(parts) > 1 and parts[1]:
                international_gold = float(parts[1])
    except:
        pass

    if pf and gold_price:
        total = pf["total_assets"]
        gold_shares = sum(h["shares"] for h in pf.get("holdings", []) if h["name"] == "黄金ETF")
        gold_value = gold_price * gold_shares
        gold_pct = round(gold_value / total * 100, 1)
        target = round(pf.get("target_allocation", {}).get("黄金", 0.07) * 100, 1)

        gs = ok(f"{gold_pct}% 🟢") if 5 <= gold_pct <= 10 else (
             warn(f"{gold_pct}% 🟡") if 3 <= gold_pct <= 12 else bad(f"{gold_pct}% 🔴"))
        print(f"  黄金ETF:       ¥{gold_price}  占比 {gs}  (目标 {target}%)")
        if international_gold:
            print(f"  国际金价:      ${international_gold:,.1f}/oz")

        dev = round(gold_pct - target, 1)
        if abs(dev) > 2:
            act = "卖出" if dev > 0 else "买入"
            amt = abs(dev) / 100 * total
            print(f"  {bad(f'⚠️ 触发再平衡: {act} 约 ¥{amt:,.0f}')}  (偏离 {dev:+.1f}%)")
        else:
            print(f"  偏离目标:      {dev:+.1f}%  {ok('未触发再平衡')}")

        print()
        print(f"  投机检测:      盯盘频率=每日 → {warn('投机模式风险')}")
        print(f"                 改为每季度第一天检查一次即可")
    else:
        if gold_price:
            print(f"  黄金ETF:       ¥{gold_price}")
        if international_gold:
            print(f"  国际金价:      ${international_gold:,.1f}/oz")
        print(f"  {warn('(需 --portfolio 查看持仓合规)')}")

    # ═══ 汇总 ═══
    print(f"\n{BOLD}═══════════════════════════════════════════{RESET}")
    issues = 0
    # count (emotion > 1.5)
    if emotion and emotion >= 1.5: issues += 1
    summary = ok("全部绿灯 ✅") if issues == 0 else bad(f"{issues} 项警报")
    print(f"{BOLD}  检查完成 · {summary}{RESET}")
    print(f"{BOLD}═══════════════════════════════════════════{RESET}\n")

    if n_days < 5:
        print(f"  ⚠️ 成交额历史仅 {n_days} 天，需积累 20 天后成交额情绪才完整可靠。")
        print(f"  每日运行此脚本即可自动积累。\n")


# ── main ─────────────────────────────────────────────────

if __name__ == "__main__":
    use_pf = "--portfolio" in sys.argv or "-p" in sys.argv
    json_out = "--json" in sys.argv

    # 腾讯 — 指数 + 个股价格
    TENCENT_INDICES = {
        "sh000001": "上证指数", "sz399001": "深证成指", "sz399006": "创业板指",
        "sh000688": "科创50", "sh000016": "上证50", "sh000300": "沪深300", "sh000905": "中证500",
    }
    WATCHLIST = {
        "sh510500": "中证500ETF", "sh518800": "黄金ETF",
        "sz002230": "科大讯飞", "sz002532": "天山铝业",
        "sh601899": "紫金矿业", "sh512400": "有色ETF",
    }

    index_data = fetch_batch(TENCENT_INDICES)
    stock_data = fetch_batch(WATCHLIST)
    sina_data = fetch_sina_all()

    pf = load_portfolio() if use_pf else None

    if pf:
        EXTRA = {}
        for h in pf.get("holdings", []):
            if h["name"] not in stock_data and h.get("code"):
                EXTRA[h["code"]] = h["name"]
        if EXTRA:
            stock_data.update(fetch_batch(EXTRA))

    history = load_history()
    record_today(history, index_data, stock_data, sina_data)
    save_history(history)

    if json_out:
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "volume_emotion": calc_volume_emotion(history)[0],
            "amplitude_3d": {},
            "gold": None,
        }
        for name in ["天山铝业", "紫金矿业", "有色ETF"]:
            amp = calc_amplitude_3d(history, name)
            if amp is not None:
                report["amplitude_3d"][name] = amp
        if pf:
            gs = stock_data.get("黄金ETF", {})
            if gs.get("price"):
                g_shares = sum(h["shares"] for h in pf["holdings"] if h["name"] == "黄金ETF")
                report["gold"] = round(gs["price"] * g_shares / pf["total_assets"] * 100, 1)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(index_data, stock_data, sina_data, history, pf)
