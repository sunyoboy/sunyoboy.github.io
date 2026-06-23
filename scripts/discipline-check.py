#!/usr/bin/env python3
"""
投资纪律指标自动化检查。

四项原则：
  1. 管住手   — 成交额情绪、个股振幅、追涨惩罚率、交易频次
  2. 控仓位   — 单品种仓位、关联品种合计、现金水位、高风险识别
  3. 别加杠杆 — 个人杠杆、市场杠杆、担保比例、极端回撤测试
  4. 黄金配置 — 仓位占比、投机检测、再平衡触发

数据源：
  - 腾讯财经 API（实时行情）
  - scripts/portfolio.json（个人持仓）
  - scripts/discipline_history.json（历史数据，自动积累）

用法：
  python3 scripts/discipline-check.py              # 市场公共指标
  python3 scripts/discipline-check.py --portfolio  # 含个人持仓检查
  python3 scripts/discipline-check.py --json       # JSON 输出（供程序消费）
"""

import sys
import os
import json
import urllib.request
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTFOLIO_FILE = os.path.join(ROOT, "scripts", "portfolio.json")
HISTORY_FILE = os.path.join(ROOT, "scripts", "discipline_history.json")

# ── 腾讯财经 API ──────────────────────────────────────────

def fetch_price(code):
    """抓取单只标的实时价格，返回 {price, pct_chg, prev_close, name}"""
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
    except Exception as e:
        return {"name": code, "price": None, "pct_chg": 0, "prev_close": None, "error": str(e)}
    return {"name": code, "price": None, "pct_chg": 0, "prev_close": None}


def fetch_batch(codes):
    """批量抓取"""
    results = {}
    for code, label in codes.items():
        info = fetch_price(code)
        if info:
            results[label] = info
    return results


# ── 历史数据管理 ───────────────────────────────────────────

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"records": []}


def save_history(h):
    h["records"] = h["records"][-120:]  # 保留最近 120 个交易日
    with open(HISTORY_FILE, "w") as f:
        json.dump(h, f, ensure_ascii=False, indent=2)


def record_today(h, index_data, stock_data):
    """追加今日行情到历史"""
    today = datetime.now().strftime("%Y-%m-%d")
    # 检查是否已记录
    if h["records"] and h["records"][-1].get("date") == today:
        h["records"][-1] = build_record(today, index_data, stock_data)
    else:
        h["records"].append(build_record(today, index_data, stock_data))


def build_record(date_str, index_data, stock_data):
    rec = {"date": date_str, "indices": {}, "stocks": {}}
    for name, d in index_data.items():
        if d.get("price"):
            rec["indices"][name] = {"close": d["price"], "pct": d["pct_chg"]}
    for name, d in stock_data.items():
        if d.get("price"):
            rec["stocks"][name] = {"close": d["price"], "pct": d["pct_chg"]}
    return rec


# ── 指标计算 ───────────────────────────────────────────────

def calc_volume_emotion(history):
    """成交额情绪指数。因API不返回成交额，用涨跌比近似。"""
    # 简化版：用近5日涨跌幅绝对值均值的比值
    # 完整版需要成交额数据，此处标记为不可用
    return None, "需接入成交额数据源（东方财富/同花顺API）"


def calc_amplitude_3d(history, name):
    """个股三日振幅"""
    records = history.get("records", [])
    if len(records) < 3:
        return None
    recent = records[-3:]
    prices = []
    for r in recent:
        s = r.get("stocks", {}).get(name, {})
        if s.get("close"):
            prices.append(s["close"])
    if len(prices) < 3:
        return None
    hi, lo = max(prices), min(prices)
    return round((hi - lo) / lo * 100, 1)


def calc_volatility_20d(history, name):
    """近20日波动率（标准差/均值）"""
    records = history.get("records", [])
    prices = []
    for r in records[-20:]:
        s = r.get("stocks", {}).get(name, {})
        if s.get("close"):
            prices.append(s["close"])
    if len(prices) < 5:
        return None
    mean = sum(prices) / len(prices)
    variance = sum((p - mean) ** 2 for p in prices) / len(prices)
    return round((variance ** 0.5) / mean * 100, 1)


def calc_max_drawdown_20d(history, name):
    """近20日最大单日跌幅"""
    records = history.get("records", [])
    max_dd = 0
    for r in records[-20:]:
        s = r.get("stocks", {}).get(name, {})
        if s.get("pct") is not None and s["pct"] < max_dd:
            max_dd = s["pct"]
    return abs(max_dd) if max_dd < 0 else 0


def load_portfolio():
    """加载个人持仓"""
    if not os.path.exists(PORTFOLIO_FILE):
        return None
    with open(PORTFOLIO_FILE, "r") as f:
        return json.load(f)


# ── 输出格式化 ─────────────────────────────────────────────

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

def ok(s):   return f"{GREEN}{s}{RESET}"
def warn(s): return f"{YELLOW}{s}{RESET}"
def bad(s):  return f"{RED}{s}{RESET}"


def print_discipline_report(index_data, stock_data, history, pf):
    """主输出"""
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{BOLD}═══════════════════════════════════════════{RESET}")
    print(f"{BOLD}  投资纪律指标检查 · {today}{RESET}")
    print(f"{BOLD}═══════════════════════════════════════════{RESET}\n")

    records = history.get("records", [])
    has_history = len(records) >= 3

    # ━━━ 1. 管住手 ━━━
    print(f"{BOLD}【一、管住手】{RESET}")
    print(f"  原则：不在情绪高潮点开仓，不在高波动期追涨\n")

    # 成交额情绪（用价格波幅代理）
    emotion, _ = calc_volume_emotion(history)
    if emotion:
        status = ok(f"{emotion:.2f} 🟢") if emotion < 1.3 else bad(f"{emotion:.2f} 🔴")
        print(f"  成交额情绪:    {status}  (阈值 < 1.3)")
    else:
        print(f"  成交额情绪:    {warn('— (需成交额数据源)')}")

    # 三日振幅
    for name in ["天山铝业", "紫金矿业", "有色ETF"]:
        amp = calc_amplitude_3d(history, name)
        if amp is not None:
            status = bad(f"{amp}% 🔴") if amp > 15 else (warn(f"{amp}% 🟡") if amp > 8 else ok(f"{amp}% 🟢"))
            print(f"  三日振幅({name}): {status}  (阈值 < 8% / > 15% 红灯)")

    # 追涨惩罚率
    print(f"  追涨惩罚率:    {warn('— (需涨停股列表)')}")
    print()

    # ━━━ 2. 控仓位 ━━━
    print(f"{BOLD}【二、控仓位】{RESET}")
    print(f"  原则：单品种不超总资产 10%，同板块不超 20%\n")

    if pf:
        total = pf["total_assets"]
        cash = pf.get("cash", 0)
        cash_pct = round(cash / total * 100, 1)
        holdings = pf.get("holdings", [])

        # 计算各持仓市值
        position_values = {}
        sector_values = {}
        for h in holdings:
            stk = stock_data.get(h["name"], {})
            price = stk.get("price") if stk else None
            if price and h["shares"]:
                val = price * h["shares"]
                position_values[h["name"]] = val
                sector = h.get("sector", "其他")
                sector_values[sector] = sector_values.get(sector, 0) + val

        # 单品种仓位
        max_pos_name, max_pos_pct = "", 0
        for name, val in position_values.items():
            pct = round(val / total * 100, 1)
            if pct > max_pos_pct:
                max_pos_pct, max_pos_name = pct, name
            status = bad(f"{pct}% 🔴") if pct > 20 else (warn(f"{pct}% 🟡") if pct > 10 else ok(f"{pct}% 🟢"))
            print(f"  单品种({name}): {status}")

        print()
        # 关联品种合计
        for sector, val in sector_values.items():
            pct = round(val / total * 100, 1)
            status = bad(f"{pct}% 🔴") if pct > 30 else (warn(f"{pct}% 🟡") if pct > 20 else ok(f"{pct}% 🟢"))
            print(f"  板块合计({sector}): {status}")

        print()
        # 现金水位
        c_status = bad(f"{cash_pct}% 🔴") if cash_pct < 40 else (warn(f"{cash_pct}% 🟡") if cash_pct < 50 else ok(f"{cash_pct}% 🟢"))
        print(f"  现金水位:      {c_status}  (阈值 ≥ 50% / < 40% 红灯)")

        # 高风险品种识别
        print()
        print(f"  高风险品种（近20日波动率 > 3%）:")
        found = False
        for h in holdings:
            vol = calc_volatility_20d(history, h["name"])
            if vol is not None and vol > 3:
                status = bad(f"波动率 {vol}% → 仓位减半")
                print(f"    {h['name']}:  {status}")
                found = True
        if not found:
            print(f"    {ok('无')}")
    else:
        print(f"  {warn('(需配置 portfolio.json)')}")
    print()

    # ━━━ 3. 别加杠杆 ━━━
    print(f"{BOLD}【三、别加杠杆】{RESET}")
    print(f"  原则：普通投资者杠杆倍数为 0\n")

    if pf:
        leverage = pf.get("margin_debt", 0) / pf["total_assets"] if pf["total_assets"] > 0 else 0
        l_status = ok("0 🟢") if leverage == 0 else bad(f"{leverage:.1%} 🔴")
        print(f"  个人杠杆倍数:  {l_status}  (唯一绿灯 = 0)")

        # 极端回撤测试
        print()
        print(f"  极端回撤压力测试（假设各品种再跌 20%）：")
        for h in pf.get("holdings", []):
            stk = stock_data.get(h["name"], {})
            price = stk.get("price") if stk else None
            if price and h["shares"]:
                val = price * h["shares"]
                loss = val * 0.2
                pct_of_total = round(loss / pf["total_assets"] * 100, 1)
                indicator = ok(f"-{pct_of_total}%") if pct_of_total < 2 else (warn(f"-{pct_of_total}%") if pct_of_total < 5 else bad(f"-{pct_of_total}%"))
                print(f"    {h['name']}: {indicator} 对总资产影响")
    else:
        print(f"  {warn('(需配置 portfolio.json)')}")
    print()

    # ━━━ 4. 黄金 = 配置非投机 ━━━
    print(f"{BOLD}【四、黄金 = 配置非投机】{RESET}")
    print(f"  原则：5-10% 资产占比，季度再平衡，不做短线\n")

    gold_stk = stock_data.get("黄金ETF", {})
    gold_price = gold_stk.get("price") if gold_stk else None

    if pf and gold_price:
        total = pf["total_assets"]
        gold_shares = 0
        for h in pf.get("holdings", []):
            if h["name"] == "黄金ETF":
                gold_shares = h["shares"]
        gold_value = gold_price * gold_shares
        gold_pct = round(gold_value / total * 100, 1)
        target = round(pf.get("target_allocation", {}).get("黄金", 0.07) * 100, 1)

        g_status = ok(f"{gold_pct}% 🟢") if 5 <= gold_pct <= 10 else (
            warn(f"{gold_pct}% 🟡") if 3 <= gold_pct <= 12 else bad(f"{gold_pct}% 🔴"))
        print(f"  黄金仓位占比:  {g_status}  (目标 {target}%)")

        distance = gold_pct - target
        if abs(distance) > 2:
            direction = "卖出" if distance > 0 else "买入"
            amount = abs(distance) / 100 * total
            print(f"  ⚠️ 距目标偏离 {distance:+.1f}% → 触发再平衡：{direction} 约 ¥{amount:,.0f}")
        else:
            print(f"  距目标偏离:    {distance:+.1f}%  未触发再平衡（±2% 为阈值）")

        # 投机检测
        print()
        print(f"  投机检测:")
        print(f"    盯盘频率:    每日 → 如果是金价波动驱动操作 → 投机模式")
        print(f"    建议:        改为每季度第一天检查一次")
    else:
        print(f"  黄金现价:      {gold_price if gold_price else warn('(无数据)')}")
        print(f"  {warn('(需配置 portfolio.json 中的黄金持仓)')}")

    # ━━━ 汇总 ━━━
    print(f"\n{BOLD}═══════════════════════════════════════════{RESET}")
    print(f"{BOLD}  检查完成{RESET}")
    print(f"{BOLD}═══════════════════════════════════════════{RESET}\n")

    if not has_history:
        print(f"  ⚠️ 历史数据不足（< 3天），部分指标不可用。")
        print(f"  连续运行 3-5 个交易日后将完整覆盖。\n")


# ── JSON 输出模式 ──────────────────────────────────────────

def json_report(index_data, stock_data, history, pf):
    """结构化 JSON 输出"""
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "indicators": {},
    }

    # 管住手
    report["indicators"]["hold_hand"] = {
        "volume_emotion": "unavailable",
        "amplitude_3d": {},
    }
    for name in ["天山铝业", "紫金矿业", "有色ETF"]:
        amp = calc_amplitude_3d(history, name)
        if amp is not None:
            report["indicators"]["hold_hand"]["amplitude_3d"][name] = {
                "value": amp,
                "alert": amp > 15,
                "threshold": 15,
            }

    # 控仓位
    if pf:
        total = pf["total_assets"]
        cash = pf.get("cash", 0)
        report["indicators"]["control_position"] = {
            "cash_ratio": round(cash / total * 100, 1),
            "single_max_pct": 0,
            "sector_max_pct": 0,
        }
        sector_vals = {}
        for h in pf.get("holdings", []):
            stk = stock_data.get(h["name"], {})
            price = stk.get("price") if stk else 0
            val = price * h.get("shares", 0)
            pct = round(val / total * 100, 1)
            if pct > report["indicators"]["control_position"]["single_max_pct"]:
                report["indicators"]["control_position"]["single_max_pct"] = pct
            sector = h.get("sector", "其他")
            sector_vals[sector] = sector_vals.get(sector, 0) + val
        for s, v in sector_vals.items():
            sp = round(v / total * 100, 1)
            if sp > report["indicators"]["control_position"]["sector_max_pct"]:
                report["indicators"]["control_position"]["sector_max_pct"] = sp

    # 别加杠杆
    if pf:
        report["indicators"]["no_leverage"] = {
            "personal_leverage": round(pf.get("margin_debt", 0) / pf["total_assets"] * 100, 1),
            "alert": pf.get("margin_debt", 0) > 0,
        }

    # 黄金
    gold_stk = stock_data.get("黄金ETF", {})
    if pf and gold_stk.get("price"):
        gold_shares = sum(h["shares"] for h in pf.get("holdings", []) if h["name"] == "黄金ETF")
        gold_val = gold_stk["price"] * gold_shares
        target = pf.get("target_allocation", {}).get("黄金", 0.07)
        gold_pct = round(gold_val / pf["total_assets"] * 100, 1)
        report["indicators"]["gold_config"] = {
            "gold_pct": gold_pct,
            "target_pct": target * 100,
            "deviation": round(gold_pct - target * 100, 1),
            "rebalance_triggered": abs(gold_pct - target * 100) > 2,
        }

    return report


# ── main ───────────────────────────────────────────────────

if __name__ == "__main__":
    use_portfolio = "--portfolio" in sys.argv or "-p" in sys.argv
    output_json = "--json" in sys.argv

    # 指数代码
    INDICES = {
        "sh000001": "上证指数", "sz399001": "深证成指", "sz399006": "创业板指",
        "sh000688": "科创50", "sh000016": "上证50", "sh000300": "沪深300",
        "sh000905": "中证500",
    }

    # 标的代码
    WATCHLIST = {
        "sh510500": "中证500ETF", "sh518800": "黄金ETF",
        "sz002230": "科大讯飞", "sz002532": "天山铝业",
        "sh601899": "紫金矿业", "sh512400": "有色ETF",
    }

    # 抓取数据
    index_data = fetch_batch(INDICES)
    stock_data = fetch_batch(WATCHLIST)

    # 加载持仓
    pf = load_portfolio() if use_portfolio else None

    # 补充抓取 portfolio 中但不在默认 WATCHLIST 里的标的
    EXTRA = {}
    if pf:
        for h in pf.get("holdings", []):
            if h["name"] not in stock_data and h.get("code"):
                EXTRA[h["code"]] = h["name"]
    if EXTRA:
        extra_data = fetch_batch(EXTRA)
        stock_data.update(extra_data)

    # 加载历史
    history = load_history()
    record_today(history, index_data, stock_data)
    save_history(history)

    if output_json:
        report = json_report(index_data, stock_data, history, pf)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_discipline_report(index_data, stock_data, history, pf)
