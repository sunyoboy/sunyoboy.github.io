#!/usr/bin/env python3
"""
收盘后自动抓取 A 股指数数据，写入复盘模板。
数据源：腾讯财经 API（实时/收盘价均可获取）

用法：
  python3 scripts/fetch-market-data.py            # 今天
  python3 scripts/fetch-market-data.py 2026-06-17 # ⚠️ 已废弃：腾讯 API 只返回实时快照，
                                                  #    传非今天的日期会被拒绝（否则把今天数据写进旧文件）。
                                                  #    历史回补请用华泰 query-indicator skill。

定时运行（macOS）：
  每个交易日 15:35 自动执行（通过 setup-cron.sh 安装的 launchd 任务）
"""

import sys
import os
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW_DIR = os.path.join(ROOT, "review")

# 腾讯财经 API 代码 → 名称
INDICES = {
    "sh000001": "上证指数",
    "sz399001": "深证成指",
    "sz399006": "创业板指",
    "sh000688": "科创50",
    "sh000016": "上证50",
    "sh000300": "沪深300",
    "sh000905": "中证500",
}

# 重点跟踪标的（ETF/个股，同一 API 接口）
WATCHLIST = {
    "sh588000": "科创50ETF",
    "sh510500": "中证500ETF",
    "sh518800": "黄金ETF",
    "sz002230": "科大讯飞",
    "sz002532": "天山铝业",
    "sh601899": "紫金矿业",
    "sh512400": "有色ETF",
}

DISPLAY_ORDER = ["上证指数", "深证成指", "创业板指", "科创50", "上证50", "沪深300", "中证500"]


def fetch_from_tencent(symbols=None, label="数据"):
    """从腾讯财经 API 获取实时数据（指数/ETF/个股通用）"""
    if symbols is None:
        symbols = INDICES
    results = {}
    for code, name in symbols.items():
        try:
            url = f"https://qt.gtimg.cn/q={code}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("gbk")
                data = raw.split("~")
                if len(data) > 32:
                    price = float(data[3])
                    pct = float(data[32])
                    prev_close = float(data[4]) if len(data) > 4 else None
                    results[name] = {
                        "close": round(price, 2),
                        "pct_chg": round(pct, 2),
                        "prev_close": round(prev_close, 2) if prev_close else None,
                        "api_dt": data[30] if len(data) > 30 else "",
                    }
                    print(f"  ✅ {name}: {results[name]['close']} ({results[name]['pct_chg']:+.2f}%)")
                else:
                    print(f"  ⚠️ {name}: 数据不完整")
        except Exception as e:
            print(f"  ❌ {name}: {e}")

    return results if results else None


def generate_template(date_str, index_data, watchlist_data=None, warning=""):
    """生成复盘 Markdown 模板"""
    if not index_data:
        return None

    dt = datetime.strptime(date_str, "%Y-%m-%d")
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][dt.weekday()]

    file_dir = os.path.join(REVIEW_DIR, year, month)
    file_path = os.path.join(file_dir, f"{date_str}.md")

    if os.path.exists(file_path):
        print(f"  ⚠️ {file_path} 已存在，跳过生成")
        return file_path

    os.makedirs(file_dir, exist_ok=True)

    rows = ""
    for name in DISPLAY_ORDER:
        if name in index_data:
            d = index_data[name]
            rows += f"| {name} | {d['close']} | **{d['pct_chg']:+.2f}%** |\n"

    # 低吸区间参考值（手动维护）
    BUY_ZONES = {
        "中证500ETF": "8.75-8.79",
        "黄金ETF": "9.05-9.09",
        "科大讯飞": "42.85-43.00",
        "天山铝业": "11.99-12.05",
        "紫金矿业": "29.08-29.21",
        "有色ETF": "2.05-2.06",
    }

    watchlist_rows = ""
    if watchlist_data:
        for name, d in watchlist_data.items():
            zone = BUY_ZONES.get(name, "—")
            watchlist_rows += f"| {name} | {d['close']} | {d['pct_chg']:+.2f}% | {zone} | — |\n"
    if not watchlist_rows:
        watchlist_rows = "| — | — | — | — | — |\n"

    template = f"""# {date_str}

{warning}## 目录

- [A股复盘](#a股复盘)
  - [指数表现](#指数表现)
  - [重点标的](#重点标的)
  - [盘面特征](#盘面特征)
  - [今日驱动](#今日驱动)
  - [热门板块](#热门板块)
  - [资金流向](#资金流向)
  - [机构观点](#机构观点)
  - [技术面](#技术面)
  - [后市关键](#后市关键)
- [做了什么](#做了什么)
- [持仓盈亏](#持仓盈亏)
- [学到了什么](#学到了什么)
- [明日计划](#明日计划)

---

## A股复盘

### 指数表现

| 指数 | 收盘 | 涨跌幅 |
|------|------|--------|
{rows}
> 成交额 — 亿。涨跌比 —。

### 重点标的

| 标的 | 收盘 | 涨跌幅 | 低吸区间 | 状态 |
|------|------|:------:|------|------|
{watchlist_rows}
> 🤖 数据由 fetch-market-data.py 自动抓取，低吸区间需手动维护。
> 📊 宏观背景参考：最新[月度市场概况](../05/2026-05-26-月度市场概况.md)

### 盘面特征

—

### 今日驱动

—

### 热门板块

-

### 资金流向

| 方向 | 板块 | 净流入/出 |
|------|------|-----------|
| 流入 | — | — |
| 流出 | — | — |

### 机构观点

—

### 技术面

-

### 后市关键

1.
2.

## 做了什么

| 股票名称 | 股票代码 | 数量 |
|----------|----------|------|
| — | — | — |

## 持仓盈亏

| 账户 | 总资产 | 今日盈亏 | 浮动盈亏 | 仓位 |
|------|--------|---------|---------|------|
| 华泰 | — | — | — | — |
| 广发 | — | — | — | — |
| 东北 | — | — | — | — |

## 学到了什么

-

## 明日计划

-
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(template)

    print(f"  📝 已生成: {file_path}")
    return file_path


if __name__ == "__main__":
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    # 🛑 防串位：腾讯 API 只返回「实时/最新」快照，无法回补历史日期。
    # 若 date_str 不是今天，会把「今天的实时数据」写进标着旧日期的文件——7/9-7/11 污染的根因。
    if date_str != today:
        print(f"🛑 拒绝执行：date_str={date_str} 不是今天({today})。")
        print("   腾讯实时 API 无法回补历史收盘，会写入错误数据。")
        print("   回补历史请用华泰 query-indicator skill 查询后手工填写。")
        sys.exit(1)

    # ⏰ 盘中警告：未到收盘(15:00)抓取的是盘中价，不能当收盘用。
    warning = ""
    if now.hour < 15:
        warning = f"> ⚠️ **盘中数据**：本文件于 {now.strftime('%H:%M')} 抓取，市场未收盘，为盘中快照，收盘后需重抓订正。\n\n"
        print(f"⚠️ 当前 {now.strftime('%H:%M')} 未到收盘，抓取的是盘中数据！")

    print(f"📊 KnowingDoing 市场数据抓取 · {date_str}  (腾讯财经)\n")

    # 抓取指数
    print("[指数]")
    data = fetch_from_tencent(INDICES, "指数")

    # 🔍 校验 API 时间戳日期是否与 date_str 一致（防非交易日返回上一交易日数据）
    if data:
        api_dt = next((v.get("api_dt", "") for v in data.values() if v.get("api_dt")), "")
        if api_dt[:8] and api_dt[:8] != date_str.replace("-", ""):
            print(f"⚠️ API 时间戳 {api_dt[:8]} 与目标日期 {date_str.replace('-', '')} 不符，可能是非交易日！")
            if not warning:
                warning = f"> ⚠️ **数据日期存疑**：API 时间戳 {api_dt} 与文件日期不符，请人工核对。\n\n"

    # 抓取重点标的
    print("\n[重点标的]")
    watchlist = fetch_from_tencent(WATCHLIST, "标的")

    generate_template(date_str, data, watchlist, warning)
    print(f"\n{'='*50}")
    if data:
        idx_count = len(data)
        wl_count = len(watchlist) if watchlist else 0
        print(f"✅ {idx_count} 大指数 + {wl_count} 重点标的 抓取完成")
        print(f"📝 打开编辑器补充分析")
    else:
        print(f"⚠️ 数据获取失败，请检查网络")
