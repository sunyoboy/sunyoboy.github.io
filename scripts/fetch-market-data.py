#!/usr/bin/env python3
"""
收盘后自动抓取 A 股指数数据，写入复盘模板。

用法：
  python3 scripts/fetch-market-data.py           # 自动检测今天日期
  python3 scripts/fetch-market-data.py 2026-06-17  # 指定日期

依赖：
  pip3 install akshare pandas

定时运行（macOS cron）：
  # 每个交易日 15:30 执行
  30 15 * * 1-5 cd /path/to/KnowingDoing && python3 scripts/fetch-market-data.py >> scripts/fetch.log 2>&1
"""

import sys
import os
from datetime import datetime, timedelta

# 项目根目录
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW_DIR = os.path.join(ROOT, "review")

# 要抓取的指数数据源（akshare 支持的指数代码）
INDICES = {
    "上证指数": "sh000001",
    "深证成指": "sz399001",
    "创业板指": "sz399006",
    "科创50": "sh000688",
    "上证50": "sh000016",
    "沪深300": "sh000300",
    "中证500": "sh000905",
}

def get_date():
    """获取目标日期"""
    if len(sys.argv) > 1:
        return sys.argv[1]  # 格式: 2026-06-17
    return datetime.now().strftime("%Y-%m-%d")

def fetch_indices(date_str):
    """抓取指数数据"""
    try:
        import akshare as ak
    except ImportError:
        print("[ERROR] 请先安装 akshare: pip3 install akshare")
        return None

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 抓取 {date_str} 指数数据...")

    try:
        # 获取 A 股指数日行情
        df = ak.stock_zh_index_daily(symbol="sh000001")  # 上证指数作为入口
        # 实际上需要逐个获取，这里简化处理
        results = {}
        for name, code in INDICES.items():
            try:
                df = ak.stock_zh_index_daily(symbol=code)
                # 找目标日期的数据
                row = df[df['date'] == date_str]
                if not row.empty:
                    r = row.iloc[-1]
                    results[name] = {
                        "close": round(float(r['close']), 2),
                        "pct_chg": round(float(r.get('pct_change', r.get('pct_chg', 0))), 2),
                        "volume": int(r.get('volume', 0)) if 'volume' in r else None,
                    }
                    print(f"  ✅ {name}: {results[name]['close']} ({results[name]['pct_chg']:+.2f}%)")
                else:
                    print(f"  ⚠️ {name}: {date_str} 无数据（可能非交易日）")
            except Exception as e:
                print(f"  ❌ {name}: {e}")

        return results if results else None

    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def generate_template(date_str, index_data):
    """生成复盘 Markdown 模板"""
    if not index_data:
        return None

    # 解析日期
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    day = dt.strftime("%d")
    weekday = ["周一","周二","周三","周四","周五","周六","周日"][dt.weekday()]

    # 文件路径
    file_dir = os.path.join(REVIEW_DIR, year, month)
    file_path = os.path.join(file_dir, f"{date_str}.md")

    # 如果文件已存在，不覆盖
    if os.path.exists(file_path):
        print(f"  ⚠️ {file_path} 已存在，跳过生成")
        return file_path

    os.makedirs(file_dir, exist_ok=True)

    # 构建表格行
    index_rows = ""
    for name in ["上证指数","深证成指","创业板指","科创50","上证50","沪深300","中证500"]:
        if name in index_data:
            d = index_data[name]
            index_rows += f"| {name} | {d['close']} | **{d['pct_chg']:+.2f}%** |\n"

    template = f"""# {date_str}

## A股复盘

### 指数表现

| 指数 | 收盘 | 涨跌幅 |
|------|------|--------|
{index_rows}
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

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"  📝 已生成: {file_path}")
    return file_path

def print_notification(ok):
    """打印提醒"""
    if ok:
        print(f"\n{'='*50}")
        print(f"✅ 数据抓取完成")
        print(f"📝 模板已生成，打开编辑器补充分析")
        print(f"🔗 http://localhost:5173/review/{date_str[:4]}/{date_str[:7]}/{date_str}")
    else:
        print(f"\n⚠️ 今日可能非交易日，无需操作")

if __name__ == "__main__":
    date_str = get_date()
    print(f"📊 KnowingDoing 市场数据抓取 · {date_str}")
    index_data = fetch_indices(date_str)
    generate_template(date_str, index_data)
    print_notification(index_data is not None)
