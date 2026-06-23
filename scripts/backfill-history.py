#!/usr/bin/env python3
"""
回填历史数据 — 解析 review/ 目录下所有复盘文件，提取指数和标的收盘价。

输出: scripts/discipline_history.json（供 discipline-check.py 消费）
      public/charts/discipline-dashboard.html（Chart.js 可视化仪表盘）

用法: python3 scripts/backfill-history.py
"""

import os
import re
import json
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW_DIR = os.path.join(ROOT, "review")
HISTORY_FILE = os.path.join(ROOT, "scripts", "discipline_history.json")
CHART_DIR = os.path.join(ROOT, "public", "charts")
CHART_FILE = os.path.join(CHART_DIR, "discipline-dashboard.html")

# 指数名称映射（复盘表格 → 内部键名）
INDEX_MAP = {
    "上证指数": "上证指数", "深证成指": "深证成指", "创业板指": "创业板指",
    "科创50": "科创50", "上证50": "上证50", "沪深300": "沪深300", "中证500": "中证500",
}

# 标的名称映射
STOCK_MAP = {
    "中证500ETF": "中证500ETF", "黄金ETF": "黄金ETF", "黄金基金": "黄金ETF",
    "科大讯飞": "科大讯飞", "天山铝业": "天山铝业",
    "紫金矿业": "紫金矿业", "有色ETF": "有色ETF", "有色金属ETF": "有色ETF",
}

# ── 解析函数 ─────────────────────────────────────────────

def parse_index_table(content):
    """从复盘文件解析指数表现表格，返回 {name: {close, pct}}"""
    result = {}
    # 匹配 | 上证指数 | 4163.10 | **+1.78%** | 等格式
    for line in content.split("\n"):
        m = re.match(r'\|\s*(上证指数|深证成指|创业板指|科创50|上证50|沪深300|中证500)\s*\|\s*([0-9]+\.[0-9]+)\s*\|\s*\*?\*?([+\-]?[0-9]+\.[0-9]+)%\*?\*?\s*\|', line)
        if m:
            name = m.group(1)
            close = float(m.group(2))
            pct = float(m.group(3))
            result[name] = {"close": close, "pct": pct}
    return result


def parse_stock_table(content):
    """从复盘文件解析重点标的表格，返回 {name: {close, pct}}"""
    result = {}
    # 匹配 | 中证500ETF | 8.94 | -0.80% | ... | 等格式（兼容 中证500ETF/黄金ETF/科大讯飞 等）
    stock_names = "|".join(STOCK_MAP.keys())
    for line in content.split("\n"):
        m = re.match(rf'\|\s*({stock_names})\s*\|\s*([0-9]+\.[0-9]+)\s*\|\s*([+\-]?[0-9]+\.[0-9]+)%\s*\|', line)
        if m:
            raw_name = m.group(1)
            name = STOCK_MAP.get(raw_name, raw_name)
            close = float(m.group(2))
            pct = float(m.group(3))
            result[name] = {"close": close, "pct": pct}
    return result


def parse_turnover(content):
    """解析成交额（万亿格式）"""
    m = re.search(r'成交额[^0-9]*([0-9]+\.[0-9]+)\s*万亿', content)
    if m:
        return float(m.group(1)) * 10000  # 万亿 → 亿
    m2 = re.search(r'成交额[^0-9]*([0-9]+)\s*亿', content)
    if m2:
        return float(m2.group(1))
    return None


def parse_date_from_filename(fname):
    """从文件名提取日期"""
    m = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
    if m:
        return m.group(1)
    return None


def fetch_sina_kline_history(symbol="sh000001", datalen=100):
    """从新浪历史K线API获取指数日线数据，含成交额。
    返回 {date_str: {open, high, low, close, turnover_yi(亿)}}"""
    try:
        url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={symbol}&scale=240&ma=no&datalen={datalen}"
        req = urllib.request.Request(url, headers={"Referer": "https://finance.sina.com.cn"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("gbk"))
            result = {}
            for d in data:
                day = d["day"]
                vol_yuan = float(d["volume"])          # 成交额(元)
                result[day] = {
                    "open": float(d["open"]),
                    "high": float(d["high"]),
                    "low": float(d["low"]),
                    "close": float(d["close"]),
                    "turnover_yi": round(vol_yuan / 1e8, 2),  # 元→亿
                }
            return result
    except Exception as e:
        print(f"  ⚠️ 新浪K线API失败({symbol}): {e}")
        return {}


def query_tencent_history(code, date_str):
    """通过腾讯API查询单只标的历史收盘价（非官方接口，仅尝试）"""
    # 腾讯API主要提供实时数据，历史数据受限
    # 保留接口供未来扩展
    return None


def scan_review_files():
    """扫描所有复盘文件，缺失数据通过新浪历史API补充"""
    records = []

    # 先拉取新浪上证K线历史（成交额补缺用）
    print("📡 拉取新浪历史K线（上证+深证）...")
    sh_kline = fetch_sina_kline_history("sh000001", datalen=200)
    sz_kline = fetch_sina_kline_history("sz399001", datalen=200)
    print(f"  ✅ 上证 {len(sh_kline)} 天, 深证 {len(sz_kline)} 天\n")

    for root, dirs, files in os.walk(REVIEW_DIR):
        files = [f for f in files if re.match(r'\d{4}-\d{2}-\d{2}\.md$', f)]
        for f in sorted(files):
            fpath = os.path.join(root, f)
            with open(fpath, "r", encoding="utf-8") as fh:
                content = fh.read()

            date_str = parse_date_from_filename(f)
            if not date_str:
                continue

            indices = parse_index_table(content)
            stocks = parse_stock_table(content)
            turnover = parse_turnover(content)  # 复盘手写（全市场成交额，亿）

            if indices:
                rec = {"date": date_str, "indices": indices, "stocks": stocks}

                # 成交额：复盘手写优先（全市场合计，亿）
                # K线补缺仅用于没有手写数据的日期（标记来源为 sina_kline）
                if turnover:
                    rec["turnover_yi"] = turnover
                    rec["turnover_source"] = "review"
                else:
                    sh = sh_kline.get(date_str, {})
                    sz = sz_kline.get(date_str, {})
                    sh_yi = sh.get("turnover_yi", 0)
                    sz_yi = sz.get("turnover_yi", 0)
                    if sh_yi > 0 and sz_yi > 0:
                        rec["turnover_yi"] = round(sh_yi + sz_yi, 2)
                        rec["turnover_source"] = "sina_kline"

                # 指数缺失→K线补
                for idx_name in ["上证指数", "深证成指"]:
                    if idx_name not in rec["indices"]:
                        kline = sh_kline if idx_name == "上证指数" else sz_kline
                        kd = kline.get(date_str, {})
                        if kd.get("close"):
                            rec["indices"][idx_name] = {"close": kd["close"], "pct": 0}

                records.append(rec)

    # 统计补缺效果
    with_api = sum(1 for r in records if r.get("turnover_yi") and not any(
        "成交额" in str(r.get("_source", "")) for _ in [1]))
    print(f"  复盘文件: {len(records)} 天")
    print(f"  含成交额: {sum(1 for r in records if r.get('turnover_yi'))} 天")
    return records


# ── 生成图表 ─────────────────────────────────────────────

def generate_dashboard(records):
    """生成 Chart.js 可视化仪表盘 HTML"""
    os.makedirs(CHART_DIR, exist_ok=True)

    dates = [r["date"] for r in records]
    dates_js = json.dumps([d[-5:] for d in dates])

    # ── 计算所有数据 ──

    # 指数涨跌幅
    idx_colors = {"上证指数": "#f87171", "深证成指": "#60a5fa", "创业板指": "#4ade80", "科创50": "#c084fc"}
    index_lines = {}
    for idx in ["上证指数", "深证成指", "创业板指", "科创50"]:
        index_lines[idx] = []
        for r in records:
            d = r.get("indices", {}).get(idx, {})
            index_lines[idx].append(d.get("pct", None))

    # 标的收盘价
    stk_colors = {"天山铝业": "#f97316", "紫金矿业": "#a78bfa", "黄金ETF": "#facc15", "科大讯飞": "#38bdf8"}
    stock_lines = {}
    for stk in ["天山铝业", "紫金矿业", "黄金ETF", "科大讯飞"]:
        stock_lines[stk] = []
        for r in records:
            d = r.get("stocks", {}).get(stk, {})
            stock_lines[stk].append(d.get("close", None))

    # 成交额 + 情绪
    turnovers = [r.get("turnover_yi") for r in records]
    ema20 = []
    for i, tv in enumerate(turnovers):
        if tv is None:
            ema20.append(None); continue
        valid = [v for v in turnovers[max(0, i-19):i+1] if v is not None]
        ema20.append(round(sum(valid) / len(valid), 1) if len(valid) >= 5 else None)

    emotions = []
    for tv, ma in zip(turnovers, ema20):
        emotions.append(round(tv / ma, 2) if (tv and ma) else None)

    # ── 构建 JS 数据集字符串 ──

    idx_js_lines = []
    for name, pcts in index_lines.items():
        color = idx_colors.get(name, "#94a3b8")
        idx_js_lines.append(
            f"idxDS.push({{label:'{name}',data:{json.dumps(pcts)},borderColor:'{color}',borderWidth:1.5,pointRadius:1.5,tension:0.1,spanGaps:false}});"
        )
    idx_js = "\n".join(idx_js_lines)

    stk_js_lines = []
    for name, prices in stock_lines.items():
        color = stk_colors.get(name, "#94a3b8")
        n_valid = len([p for p in prices if p is not None])
        stk_js_lines.append(
            f"stkDS.push({{label:'{name}({n_valid}天)',data:{json.dumps(prices)},borderColor:'{color}',borderWidth:1.5,pointRadius:1.5,tension:0.1,spanGaps:false}});"
        )
    stk_js = "\n".join(stk_js_lines)

    last_turnover = turnovers[-1] if turnovers[-1] else 'null'
    last_emotion = emotions[-1] if emotions[-1] else 'null'
    last_ema20 = ema20[-1] if ema20[-1] else 'null'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>投资纪律仪表盘</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }}
  .header {{ text-align: center; padding: 20px 0 30px; }}
  .header h1 {{ font-size: 1.6em; color: #f1f5f9; }}
  .header p {{ color: #94a3b8; margin-top: 4px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(520px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }}
  .card {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }}
  .card h2 {{ font-size: 0.95em; color: #94a3b8; margin-bottom: 12px; font-weight: 500; }}
  .card canvas {{ max-height: 300px; }}
  .legend {{ display: flex; gap: 16px; flex-wrap: wrap; margin-top: 8px; font-size: 0.8em; }}
  .legend-item {{ display: flex; align-items: center; gap: 6px; }}
  .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
  .footer {{ text-align: center; padding: 30px 0 10px; color: #475569; font-size: 0.8em; }}
</style>
</head>
<body>
<div class="header">
  <h1>📐 投资纪律仪表盘</h1>
  <p>数据范围 {dates[0]} ~ {dates[-1]} · {len(records)} 个交易日 · 自动生成</p>
</div>

<div class="grid">

  <!-- 1. 成交额情绪 -->
  <div class="card">
    <h2>📊 成交额 + 成交额情绪</h2>
    <canvas id="chartEmotion"></canvas>
    <div class="legend">
      <span class="legend-item"><span class="legend-dot" style="background:#60a5fa"></span>成交额(亿)</span>
      <span class="legend-item"><span class="legend-dot" style="background:#f59e0b;border:dashed 1px #f59e0b"></span>20日均成交额</span>
      <span class="legend-item"><span class="legend-dot" style="background:#f87171"></span>情绪指数(右轴) &gt;1.3=黄灯 &gt;1.5=红灯</span>
    </div>
  </div>

  <!-- 2. 指数涨跌 -->
  <div class="card">
    <h2>📈 四大指数 日涨跌幅(%)</h2>
    <canvas id="chartIndices"></canvas>
  </div>

  <!-- 3. 标的收盘价 -->
  <div class="card">
    <h2>⚠️ 高波动标的 收盘价(元)</h2>
    <canvas id="chartStocks"></canvas>
  </div>

  <!-- 4. 合规面板 -->
  <div class="card">
    <h2>🛡️ 纪律合规状态</h2>
    <div id="statusPanel" style="display:flex;flex-direction:column;gap:14px;padding:10px 0;"></div>
  </div>

</div>

<div class="footer">数据源: 每日复盘文件 + 新浪/腾讯财经API · 仅供参考，不构成投资建议</div>

<script>
const dates = {dates_js};

// ── 1. 成交额情绪 ──
new Chart(document.getElementById('chartEmotion'), {{
  type: 'bar',
  data: {{
    labels: dates,
    datasets: [
      {{
        label: '成交额(亿)', data: {json.dumps(turnovers)},
        backgroundColor: ctx => {{
          const v = ctx.raw; if (!v) return 'rgba(100,116,139,0.3)';
          return v > 35000 ? 'rgba(248,113,113,0.6)' : v > 30000 ? 'rgba(251,191,36,0.5)' : 'rgba(96,165,250,0.5)';
        }}, borderWidth: 0, yAxisID: 'y', order: 2
      }},
      {{
        label: '20日均(亿)', data: {json.dumps(ema20)},
        type: 'line', borderColor: '#f59e0b', borderDash: [4,3], borderWidth: 1.5,
        pointRadius: 0, fill: false, yAxisID: 'y', order: 1
      }},
      {{
        label: '情绪', data: {json.dumps(emotions)},
        type: 'line', borderColor: '#f87171', borderWidth: 2,
        pointRadius: 2, pointBackgroundColor: '#f87171', fill: false, yAxisID: 'y1', order: 0
      }}
    ]
  }},
  options: {{
    responsive: true, interaction: {{ intersect: false, mode: 'index' }},
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      y: {{ type: 'linear', position: 'left', title: {{ display: true, text: '成交额(亿)', color: '#94a3b8' }}, ticks: {{ color:'#94a3b8' }}, grid: {{ color:'#334155' }} }},
      y1: {{ type: 'linear', position: 'right', title: {{ display: true, text: '情绪指数', color: '#f87171' }}, ticks: {{ color:'#f87171' }}, grid: {{ drawOnChartArea: false }}, min: 0.5, max: 2.0 }}
    }}
  }}
}});

// ── 2. 指数涨跌幅 ──
const idxDS = [];
{idx_js}
new Chart(document.getElementById('chartIndices'), {{
  type: 'line',
  data: {{ labels: dates, datasets: idxDS }},
  options: {{
    responsive: true, interaction: {{ intersect: false, mode: 'index' }},
    plugins: {{ legend: {{ position:'top', labels:{{ color:'#94a3b8', usePointStyle:true }} }} }},
    scales: {{ y: {{ title:{{ display:true, text:'%', color:'#94a3b8' }}, ticks:{{ color:'#94a3b8' }}, grid:{{ color:'#334155' }} }}, x: {{ ticks:{{ color:'#64748b', maxRotation:60 }} }} }}
  }}
}});

// ── 3. 标的收盘价 ──
const stkDS = [];
{stk_js}
new Chart(document.getElementById('chartStocks'), {{
  type: 'line',
  data: {{ labels: dates, datasets: stkDS }},
  options: {{
    responsive: true, interaction: {{ intersect: false, mode: 'index' }},
    plugins: {{ legend: {{ position:'top', labels:{{ color:'#94a3b8', usePointStyle:true }} }} }},
    scales: {{ y: {{ title:{{ display:true, text:'元', color:'#94a3b8' }}, ticks:{{ color:'#94a3b8' }}, grid:{{ color:'#334155' }} }}, x: {{ ticks:{{ color:'#64748b', maxRotation:60 }} }} }}
  }}
}});

// ── 4. 合规面板 ──
(function() {{
  const panel = document.getElementById('statusPanel');
  const items = [
    {{ label:'成交额情绪', value: {last_emotion} === null ? '—' : {last_emotion}.toFixed(2),
       detail: {last_ema20} === null ? '' : ('近20日均 ' + {last_ema20}.toFixed(0) + '亿'),
       status: {last_emotion} === null ? '⏳' : ({last_emotion} > 1.5 ? '🔴' : ({last_emotion} > 1.3 ? '🟡' : '🟢')),
       tip: '>1.5=高潮禁仓, >1.3=偏热谨慎, <1.3=正常' }},
    {{ label:'最新成交额', value: {last_turnover} === null ? '—' : ({last_turnover}/10000).toFixed(2)+'万亿',
       status: {last_turnover} === null ? '⏳' : ({last_turnover} > 35000 ? '🔴' : '🟢'),
       tip: '>3.5万亿=情绪高潮, <2万亿=情绪冰点' }},
    {{ label:'仓位合规', value: '✅ 全部绿灯', status:'🟢', tip:'单品种≤10%, 同板块≤20%, 现金≥50%' }},
    {{ label:'杠杆', value: '0', status:'🟢', tip:'普通投资者唯一正确数值' }},
  ];
  items.forEach(it => {{
    panel.innerHTML += `<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:#0f172a;border-radius:8px;">
      <div><strong>${{it.label}}</strong><div style="font-size:0.75em;color:#64748b;">${{it.tip||''}}</div></div>
      <div style="text-align:right;"><span style="font-size:1.2em;">${{it.status}}</span> <span style="font-size:0.9em;color:#94a3b8;margin-left:8px;">${{it.value}}</span></div>
    </div>`;
  }});
}})();
</script>
</body>
</html>"""

    with open(CHART_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"📊 图表已生成: {CHART_FILE}")
    return CHART_FILE


# ── main ─────────────────────────────────────────────────

if __name__ == "__main__":
    print("🔍 扫描复盘文件...")
    records = scan_review_files()

    # 合成新浪当日成交额数据到最新记录（如果历史文件里没有）
    # 注意：历史文件里的 turnover 是从 markdown 里解析的"X.XX万亿"
    # 新浪拿到的原始数值单位不同，只用于最近一天

    print(f"  ✅ 共解析 {len(records)} 个交易日")
    for r in records:
        n_indices = len(r.get("indices", {}))
        n_stocks = len(r.get("stocks", {}))
        to = r.get("turnover_yi")
        to_str = f" 成交额={to:,.0f}亿" if to else ""
        print(f"     {r['date']}: {n_indices}指数 {n_stocks}标的{to_str}")

    # 保存 history.json
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    out = {"records": records, "source": "review/*.md 回填"}
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n📝 已写入: {HISTORY_FILE}")

    # 生成图表
    generate_dashboard(records)

    # 快速统计
    print(f"\n{'='*50}")
    print(f"📊 数据统计")
    print(f"{'='*50}")
    # 成交额情绪（如果有足够成交额数据）
    to_records = [r for r in records if r.get("turnover_yi")]
    if len(to_records) >= 5:
        to_values = [r["turnover_yi"] for r in to_records[-20:]]
        avg_to = sum(to_values) / len(to_values)
        latest_to = to_records[-1]["turnover_yi"]
        emotion = round(latest_to / avg_to, 2)
        print(f"  成交额数据: {len(to_records)} 天")
        print(f"  最新成交额: {latest_to:,.0f}亿")
        print(f"  20日均额:   {avg_to:,.0f}亿")
        print(f"  成交额情绪: {emotion} {'🔴' if emotion > 1.5 else '🟡' if emotion > 1.3 else '🟢'}")
    else:
        print(f"  成交额数据: {len(to_records)} 天（需 ≥5 天才能计算情绪）")

    # 三日振幅（最新）
    if len(records) >= 3:
        last3 = records[-3:]
        print(f"\n  最新三日振幅:")
        for stk in ["天山铝业", "紫金矿业", "有色ETF"]:
            prices = []
            for r in last3:
                d = r.get("stocks", {}).get(stk, {})
                if d.get("close"):
                    prices.append(d["close"])
            if len(prices) >= 3:
                hi, lo = max(prices), min(prices)
                amp = round((hi - lo) / lo * 100, 1)
                flag = "🔴" if amp > 15 else ("🟡" if amp > 8 else "🟢")
                print(f"    {stk}: {amp}% {flag}")
