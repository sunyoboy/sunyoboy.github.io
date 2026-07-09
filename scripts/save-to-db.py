#!/usr/bin/env python3
"""
收盘后一键入库：拉数据 → 存 SQLite。
在现有脚本之后运行，不修改原有脚本逻辑。

用法：
  python3 scripts/save-to-db.py                 # 今天
  python3 scripts/save-to-db.py 2026-07-09      # 指定日期

前置：需要先运行 fetch-market-data.py、ma5-deviation.py、shenwan-monitor.py
"""

import sys
import os
import json
import subprocess
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from scripts.market_db import MarketDB


def get_date():
    """获取目标日期"""
    if len(sys.argv) > 1:
        return sys.argv[1]
    return datetime.now().strftime("%Y-%m-%d")


def parse_ma5_output(text):
    """从 ma5-deviation.py 的 stdout 中解析 ETF 数据"""
    import re
    results = {}
    # Pattern: | 中证500ETF | 8.51 | -2.69% | ... | 金叉 ▲ | ... | +5.48% | 0.96x |
    for line in text.split("\n"):
        if "|" not in line or "dev5" in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 10:
            name = parts[0]
            close_val = float(parts[1]) if parts[1].replace('.', '').replace('-', '').isdigit() else None
            pct_val = float(parts[2].replace('%', '')) if '%' in parts[2] else None
            # Extract MA5/MA20/MA60 from table2 if available
            results[name] = {
                "close": close_val,
                "pct": pct_val,
            }
    return results


def parse_shenwan_output(text):
    """从 shenwan-monitor.py 的 stdout 中解析申万数据"""
    import re
    rows = []
    in_table = False
    for line in text.split("\n"):
        if "行业" in line and "ETF" in line and "涨跌" in line:
            in_table = True
            continue
        if in_table and "────────────────" in line:
            continue
        if in_table and len(line.strip()) < 10:
            break
        if in_table:
            parts = [p.strip() for p in line.split() if p.strip()]
            if len(parts) >= 3:
                rows.append({
                    "industry": parts[0],
                    "etf_name": parts[1],
                    "close": None,
                    "pct": float(parts[2].replace('%', '').replace('+', '')) if parts[2] else None,
                    "signal": "均衡",
                    "etf_code": "",
                })
    return rows


def main():
    date = get_date()
    db = MarketDB()
    print(f"📦 入库日期: {date}")

    # 1. 从 shenwan_history.json 读取申万数据
    # 格式: {date: {industry: {pct_chg, signal}}}
    shenwan_path = os.path.join(ROOT, "scripts", "shenwan_history.json")
    if os.path.exists(shenwan_path):
        with open(shenwan_path, "r") as f:
            history = json.load(f)
        if date in history:
            rows = []
            for industry, info in history[date].items():
                rows.append({
                    "industry": industry,
                    "etf_code": "",
                    "etf_name": "",
                    "close": None,
                    "pct": info.get("pct_chg"),
                    "signal": info.get("signal", "均衡"),
                })
            db.save_shenwan_batch(date, rows)
            print(f"  ✅ 申万行业: {len(rows)} 条")

    # 2. 从 discipline_history.json 读取 ETF 数据
    # 格式: [{date, positions: [{code, name, close, change_pct, ma5, ma20, ma60, dev5, vol_ratio}]}]
    disc_path = os.path.join(ROOT, "scripts", "discipline_history.json")
    if os.path.exists(disc_path):
        with open(disc_path, "r") as f:
            disc = json.load(f)
        if isinstance(disc, list):
            for entry in disc:
                if entry.get("date") == date:
                    count = 0
                    for pos in entry.get("positions", []):
                        db.save_etf(
                            date=date,
                            code=pos.get("code", ""),
                            name=pos.get("name", ""),
                            close=pos.get("close"),
                            pct=pos.get("change_pct"),
                            ma5=pos.get("ma5"),
                            ma20=pos.get("ma20"),
                            ma60=pos.get("ma60"),
                            dev5=pos.get("dev5"),
                            vol_ratio=pos.get("vol_ratio"),
                        )
                        count += 1
                    print(f"  ✅ ETF偏离度: {count} 条")

    # 3. 验证
    latest = db.latest_date()
    total = db.query("SELECT COUNT(*) as cnt FROM etf_daily")[0]['cnt']
    sw = db.query("SELECT COUNT(*) as cnt FROM shenwan_daily")[0]['cnt']
    print(f"\n📊 数据库统计: ETF {total}条 | 申万 {sw}条 | 最新 {latest}")


if __name__ == "__main__":
    main()
