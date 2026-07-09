#!/usr/bin/env python3
"""
一次性迁移：将现有 JSON 历史数据导入 SQLite。

用法：
  python3 scripts/migrate_history.py

数据源：
  - scripts/shenwan_history.json → shenwan_daily 表
  - scripts/discipline_history.json → etf_daily 表（如有兼容字段）
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from scripts.market_db import MarketDB


def migrate_shenwan():
    """迁移申万行业历史数据
    格式: {date: {industry: {pct_chg, signal}}}
    """
    json_path = os.path.join(ROOT, "scripts", "shenwan_history.json")
    if not os.path.exists(json_path):
        print("  ⚠️ shenwan_history.json 不存在，跳过")
        return 0

    with open(json_path, "r") as f:
        data = json.load(f)

    db = MarketDB()
    count = 0
    for date, industries in data.items():
        rows = []
        for industry, info in industries.items():
            rows.append({
                "industry": industry,
                "etf_code": "",
                "etf_name": "",
                "close": None,
                "pct": info.get("pct_chg"),
                "signal": info.get("signal", "均衡"),
            })
        if rows:
            db.save_shenwan_batch(date, rows)
            count += len(rows)

    print(f"  ✅ 申万行业: {count} 条")
    return count


def migrate_discipline():
    """迁移持仓偏离度历史数据
    格式: [{date, positions: [{code, name, close, close, change_pct, ma5, ma20, ma60, dev5, vol_ratio}]}]
    """
    json_path = os.path.join(ROOT, "scripts", "discipline_history.json")
    if not os.path.exists(json_path):
        print("  ⚠️ discipline_history.json 不存在，跳过")
        return 0

    with open(json_path, "r") as f:
        data = json.load(f)

    db = MarketDB()
    count = 0
    # discipline_history.json is a list of daily snapshots
    if isinstance(data, list):
        for entry in data:
            date = entry.get("date", "")
            if not date:
                continue
            for item in entry.get("positions", []):
                db.save_etf(
                    date=date,
                    code=item.get("code", ""),
                    name=item.get("name", ""),
                    close=item.get("close"),
                    pct=item.get("change_pct"),
                    ma5=item.get("ma5"),
                    ma20=item.get("ma20"),
                    ma60=item.get("ma60"),
                    dev5=item.get("dev5"),
                    vol_ratio=item.get("vol_ratio"),
                )
                count += 1

    print(f"  ✅ 持仓偏离度: {count} 条")
    return count


if __name__ == "__main__":
    print("📦 迁移历史数据 → SQLite\n")
    total = 0
    total += migrate_shenwan()
    total += migrate_discipline()
    print(f"\n🎉 迁移完成: {total} 条")
