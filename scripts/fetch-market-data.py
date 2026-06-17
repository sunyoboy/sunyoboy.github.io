#!/usr/bin/env python3
"""
收盘后自动抓取 A 股指数数据，写入复盘模板。
数据源：腾讯财经 API（实时/收盘价均可获取）

用法：
  python3 scripts/fetch-market-data.py            # 今天
  python3 scripts/fetch-market-data.py 2026-06-17 # 指定日期

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

DISPLAY_ORDER = ["上证指数", "深证成指", "创业板指", "科创50", "上证50", "沪深300", "中证500"]


def fetch_from_tencent():
    """从腾讯财经 API 获取指数实时数据"""
    results = {}
    for code, name in INDICES.items():
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
                    }
                    print(f"  ✅ {name}: {results[name]['close']} ({results[name]['pct_chg']:+.2f}%)")
                else:
                    print(f"  ⚠️ {name}: 数据不完整")
        except Exception as e:
            print(f"  ❌ {name}: {e}")

    return results if results else None


def generate_template(date_str, index_data):
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

    template = f"""# {date_str}

## 目录

- [A股复盘](#a股复盘)
  - [指数表现](#指数表现)
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
    print(f"📊 KnowingDoing 市场数据抓取 · {date_str}  (腾讯财经)")
    data = fetch_from_tencent()
    generate_template(date_str, data)
    print(f"\n{'='*50}")
    if data:
        print(f"✅ 7 大指数抓取完成")
        print(f"📝 打开编辑器补充分析")
    else:
        print(f"⚠️ 数据获取失败，请检查网络")
