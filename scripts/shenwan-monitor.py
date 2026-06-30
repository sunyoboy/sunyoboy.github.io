#!/usr/bin/env python3
"""
申万一级行业全景监测
====================
通过行业代表 ETF + 腾讯 API 快速监测 31 个申万一级行业的走势。
输出全景热力图 + 领涨/领跌 + 极端信号。

用法：
  python3 scripts/shenwan-monitor.py
"""

import sys
import os
import json
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 31 个申万一级行业 → 代表 ETF（腾讯接口可用）
# 部分行业无直接 ETF，用最相关的替代
INDUSTRY_MAP = {
    "农林牧渔":    ("sz159865", "养殖ETF"),
    "基础化工":    ("sh516020", "化工ETF"),
    "钢铁":        ("sh515210", "钢铁ETF"),
    "有色金属":    ("sh512400", "有色ETF"),
    "电子":        ("sz159997", "电子ETF"),
    "汽车":        ("sh516110", "汽车ETF"),
    "家用电器":    ("sh561120", "家电ETF"),
    "食品饮料":    ("sh515170", "食品饮料ETF"),
    "纺织服饰":    ("sz159850", "纺织服装ETF"),
    "轻工制造":    ("sz159811", "轻工ETF"),
    "医药生物":    ("sh512010", "医药ETF"),
    "公用事业":    ("sh561190", "电力ETF"),
    "交通运输":    ("sz159662", "交运ETF"),
    "房地产":      ("sh512200", "房地产ETF"),
    "商贸零售":    ("sz159936", "可选消费ETF"),
    "社会服务":    ("sz159766", "旅游ETF"),
    "银行":        ("sh512800", "银行ETF"),
    "非银金融":    ("sh512070", "证券保险ETF"),
    "综合":        ("sh510210", "综指ETF"),
    "建筑材料":    ("sh516750", "建材ETF"),
    "建筑装饰":    ("sh516970", "基建ETF"),
    "电力设备":    ("sh516160", "新能源ETF"),
    "国防军工":    ("sh512660", "军工ETF"),
    "计算机":      ("sz159998", "计算机ETF"),
    "传媒":        ("sh512980", "传媒ETF"),
    "通信":        ("sh515880", "通信ETF"),
    "煤炭":        ("sh515220", "煤炭ETF"),
    "石油石化":    ("sh516860", "石化ETF"),
    "环保":        ("sh516890", "环保ETF"),
    "美容护理":    ("sh516130", "消费龙头ETF"),
    "机械设备":    ("sz159886", "机械ETF"),
}

TENCENT_URL = "https://qt.gtimg.cn/q="


def fetch_all():
    """批量抓取所有行业代表 ETF"""
    codes = [code for code, _ in INDUSTRY_MAP.values()]
    url = TENCENT_URL + ",".join(codes)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("gbk")
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return {}

    results = {}
    lines = raw.strip().split("\n")

    for line in lines:
        if "~" not in line:
            continue
        parts = line.split("~")
        if len(parts) < 33:
            continue
        # parts[1] = name, parts[2] = code, parts[3] = price, parts[32] = pct
        try:
            etf_name = parts[1]
            etf_code = parts[2]
            price = float(parts[3])
            pct = float(parts[32])

            # 反查行业名（腾讯返回的code不带sh/sz前缀）
            etf_code_short = etf_code.replace("sh","").replace("sz","")
            industry = None
            for ind, (code, ename) in INDUSTRY_MAP.items():
                if code.replace("sh","").replace("sz","") == etf_code_short:
                    industry = ind
                    break
            if industry is None:
                continue

            results[industry] = {
                "etf": etf_name,
                "price": price,
                "pct_chg": round(pct, 2),
            }
        except (ValueError, IndexError):
            continue

    return results


def compute_signals(data):
    """计算信号"""
    for d in data.values():
        pct = d["pct_chg"]
        if pct > 5:
            d["signal"] = "🔴 过热"
            d["action"] = "减仓/不追"
        elif pct > 2:
            d["signal"] = "🟡 偏热"
            d["action"] = "持有/观察"
        elif pct < -5:
            d["signal"] = "🔵 冰点"
            d["action"] = "低吸候选"
        elif pct < -2:
            d["signal"] = "🟡 偏冷"
            d["action"] = "关注企稳"
        else:
            d["signal"] = "🟢 均衡"
            d["action"] = "正常"


def print_report(data):
    """双列输出全景报告"""
    compute_signals(data)
    sorted_data = sorted(data.values(), key=lambda x: x["pct_chg"], reverse=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║      申万一级行业全景监测  ·  {now}        ║
║      31 个行业 × 代表 ETF  ·  腾讯行情 API                 ║
╚══════════════════════════════════════════════════════════════════╝
""")

    # TOP/BOTTOM 5
    top5 = sorted_data[:5]
    bot5 = sorted_data[-5:]

    print("🔥 今日领涨                          📉 今日领跌")
    print("─"*40 + "  " + "─"*40)
    for i in range(5):
        left = f"  {i+1}. {top5[i]['etf']:<14} {top5[i]['pct_chg']:>+6.2f}%"
        right = f"  {i+1}. {bot5[4-i]['etf']:<14} {bot5[4-i]['pct_chg']:>+6.2f}%"
        print(f"{left:<42}{right}")

    # 涨跌统计
    up = sum(1 for d in data.values() if d["pct_chg"] > 0)
    down = sum(1 for d in data.values() if d["pct_chg"] < 0)
    flat = len(data) - up - down

    # 极端信号
    hot = [d for d in data.values() if d["pct_chg"] > 5]
    cold = [d for d in data.values() if d["pct_chg"] < -5]

    print(f"\n📊 涨跌比: {up}↑  |  {down}↓  |  {flat}→  |  总计 {len(data)}")

    if hot:
        print("\n⚠️  过热（+5%以上）:")
        for d in hot:
            print(f"    {d['etf']} {d['pct_chg']:+.2f}%  →  不追")

    if cold:
        print("\n🔵 冰点（-5%以下）:")
        for d in cold:
            print(f"    {d['etf']} {d['pct_chg']:+.2f}%  →  低吸候选")

    if not hot and not cold:
        print("✅ 无极端信号，各行业正常波动")

    # 全行业双列
    print(f"\n{'─'*80}")
    print(f"{'行业':<8} {'ETF':<14} {'涨跌':>7} {'信号':<10} {'行x业':<8} {'ETF':<14} {'涨跌':>7} {'信号'}")
    print(f"{'─'*80}")

    mid = (len(sorted_data) + 1) // 2
    for i in range(mid):
        left = f"  {sorted_data[i]['name']:<8} {sorted_data[i]['etf']:<12} {sorted_data[i]['pct_chg']:>+5.2f}% {sorted_data[i]['signal']:<10}"
        right = ""
        if i + mid < len(sorted_data):
            d = sorted_data[i + mid]
            right = f"  {d['name']:<8} {d['etf']:<12} {d['pct_chg']:>+5.2f}% {d['signal']}"
        print(f"{left:<55}{right}")

    print(f"{'─'*80}")
    print("信号: 🔴 +5%↑过热  🟡 ±5%偏  🟢 ±2%均衡  🔵 -5%↓冰点")
    print("="*80)


def main():
    print("\n📊 申万行业监测 · 正在抓取 31 个行业 ETF...\n")

    raw = fetch_all()
    if len(raw) < 15:
        print(f"\n⚠️  仅获取 {len(raw)}/31 个行业，请检查网络。")
        return

    # 补全行业名
    for ind, d in raw.items():
        d["name"] = ind

    print_report(raw)

    # 保存
    date_str = datetime.now().strftime("%Y-%m-%d")
    history_file = os.path.join(ROOT, "scripts", "shenwan_history.json")
    history = {}
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            try:
                history = json.load(f)
            except:
                pass
    history[date_str] = {
        k: {"pct_chg": v["pct_chg"], "signal": v["signal"]}
        for k, v in raw.items()
    }
    with open(history_file, "w") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 数据已保存 → scripts/shenwan_history.json\n")


if __name__ == "__main__":
    main()
