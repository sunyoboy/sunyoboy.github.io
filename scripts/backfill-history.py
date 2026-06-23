#!/usr/bin/env python3
"""
API 主驱动历史回填 — 新浪K线接口拉取 5/21 ~ 6/23 全量数据。

数据优先级：
  1. 新浪K线 API（指数+个股，含成交额）   ← 主源
  2. 腾讯实时 API（当日盘中捕获）           ← 兜底
  3. 复盘 markdown 文件（交叉验证+标的补充） ← 参考

输出: scripts/discipline_history.json
      public/charts/discipline-dashboard.html
"""

import os, re, json, urllib.request, time
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW_DIR = os.path.join(ROOT, "review")
HISTORY_FILE = os.path.join(ROOT, "scripts", "discipline_history.json")
CHART_DIR = os.path.join(ROOT, "public", "charts")
CHART_FILE = os.path.join(CHART_DIR, "discipline-dashboard.html")

START_DATE = "2026-05-21"
END_DATE   = "2026-06-23"

# ── 新浪K线 API（指数+个股通用）──

SINA_INDEX_CODES = {
    "sh000001": "上证指数", "sz399001": "深证成指", "sz399006": "创业板指",
    "sh000688": "科创50", "sh000016": "上证50", "sh000300": "沪深300", "sh000905": "中证500",
}
SINA_STOCK_CODES = {
    "sh510500": "中证500ETF", "sh518800": "黄金ETF",
    "sz002230": "科大讯飞", "sz002532": "天山铝业",
    "sh601899": "紫金矿业", "sh512400": "有色ETF",
    "sh563230": "卫星ETF",
}

def fetch_kline(symbol, datalen=200):
    """新浪日K线 → {date_str: {open,high,low,close,volume(股)}}。
    ⚠️ volume=成交量(股数)，不是成交额。指数K线API不提供成交额。"""
    try:
        url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={symbol}&scale=240&ma=no&datalen={datalen}"
        req = urllib.request.Request(url, headers={"Referer": "https://finance.sina.com.cn"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("gbk"))
            result = {}
            for d in data:
                result[d["day"]] = {
                    "open": float(d["open"]), "high": float(d["high"]),
                    "low": float(d["low"]), "close": float(d["close"]),
                    "volume_gu": float(d["volume"]),  # 股数
                }
            return result
    except Exception as e:
        print(f"  ❌ 新浪K线 {symbol}: {e}")
        return {}

# ── 复盘文件补充（标的收盘价交叉验证）──

INDEX_TABLE_MAP = {v: v for v in SINA_INDEX_CODES.values()}

STOCK_TABLE_MAP = {
    "中证500ETF": "中证500ETF", "黄金ETF": "黄金ETF", "黄金基金": "黄金ETF",
    "科大讯飞": "科大讯飞", "天山铝业": "天山铝业",
    "紫金矿业": "紫金矿业", "有色ETF": "有色ETF", "有色金属ETF": "有色ETF",
    "卫星ETF": "卫星ETF", "卫星ETF富国": "卫星ETF",
}

def parse_index_table(content):
    result = {}
    for line in content.split("\n"):
        m = re.match(r'\|\s*(上证指数|深证成指|创业板指|科创50|上证50|沪深300|中证500)\s*\|\s*([0-9]+\.[0-9]+)\s*\|\s*\*?\*?([+\-]?[0-9]+\.[0-9]+)%\*?\*?\s*\|', line)
        if m:
            result[m.group(1)] = {"close": float(m.group(2)), "pct": float(m.group(3))}
    return result

def parse_stock_table(content):
    result = {}
    names = "|".join(STOCK_TABLE_MAP.keys())
    for line in content.split("\n"):
        m = re.match(rf'\|\s*({names})\s*\|\s*([0-9]+\.[0-9]+)\s*\|\s*([+\-]?[0-9]+\.[0-9]+)%\s*\|', line)
        if m:
            name = STOCK_TABLE_MAP[m.group(1)]
            result[name] = {"close": float(m.group(2)), "pct": float(m.group(3))}
    return result

def parse_turnover(content):
    m = re.search(r'成交额[^0-9]*([0-9]+\.[0-9]+)\s*万亿', content)
    if m: return float(m.group(1)) * 10000
    m2 = re.search(r'成交额[^0-9]*([0-9]+)\s*亿', content)
    if m2: return float(m2.group(1))
    return None

# ── 日期工具 ──

def trading_days(start, end):
    """生成区间内所有日期（包含周末，新浪K线自动过滤非交易日）"""
    days = []
    d = datetime.strptime(start, "%Y-%m-%d")
    ed = datetime.strptime(end, "%Y-%m-%d")
    while d <= ed:
        days.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)
    return days

# ── 主力程序 ──

def build_records():
    all_days = trading_days(START_DATE, END_DATE)
    print(f"📡 拉取新浪K线... 日期范围 {START_DATE}~{END_DATE} ({len(all_days)}天)\n")

    # 拉取所有指数K线
    print("[指数]")
    index_kline = {}
    for code, name in SINA_INDEX_CODES.items():
        data = fetch_kline(code, datalen=200)
        index_kline[name] = data
        cnt = sum(1 for d in all_days if d in data)
        print(f"  ✅ {name}: {cnt} 天")

    # 拉取所有标的K线
    print("\n[标的]")
    stock_kline = {}
    for code, name in SINA_STOCK_CODES.items():
        data = fetch_kline(code, datalen=200)
        stock_kline[name] = data
        cnt = sum(1 for d in all_days if d in data)
        print(f"  ✅ {name}: {cnt} 天")
        time.sleep(0.15)  # 反爬

    # 拉取复盘文件（交叉验证用）
    print("\n[复盘文件交叉验证]")
    review_data = {}
    for root, dirs, files in os.walk(REVIEW_DIR):
        for f in sorted(files):
            if not re.match(r'\d{4}-\d{2}-\d{2}\.md$', f): continue
            fpath = os.path.join(root, f)
            with open(fpath, "r", encoding="utf-8") as fh:
                content = fh.read()
            m = re.search(r'(\d{4}-\d{2}-\d{2})', f)
            if m:
                date_str = m.group(1)
                review_data[date_str] = {
                    "indices": parse_index_table(content),
                    "stocks": parse_stock_table(content),
                    "turnover_review": parse_turnover(content),
                }

    # ── 逐日组装记录 ──
    records = []
    for day in all_days:
        rec = {"date": day, "indices": {}, "stocks": {}}

        # 指数：K线数据
        for name, kline in index_kline.items():
            kd = kline.get(day)
            if kd:
                rec["indices"][name] = {"close": kd["close"], "pct": 0}
                # 涨跌幅：如果有前一天数据则计算
                prev = None
                prev_day = (datetime.strptime(day, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
                # 向前查找最近交易日
                for offset in range(1, 8):
                    pd_str = (datetime.strptime(day, "%Y-%m-%d") - timedelta(days=offset)).strftime("%Y-%m-%d")
                    pk = kline.get(pd_str)
                    if pk:
                        prev = pk["close"]; break
                if prev:
                    rec["indices"][name]["pct"] = round((kd["close"] - prev) / prev * 100, 2)

        # 标的：K线数据
        for name, kline in stock_kline.items():
            kd = kline.get(day)
            if kd:
                rec["stocks"][name] = {"close": kd["close"], "pct": 0}
                for offset in range(1, 8):
                    pd_str = (datetime.strptime(day, "%Y-%m-%d") - timedelta(days=offset)).strftime("%Y-%m-%d")
                    pk = kline.get(pd_str)
                    if pk:
                        rec["stocks"][name]["pct"] = round((kd["close"] - pk["close"]) / pk["close"] * 100, 2)
                        break

        # 成交额：复盘手写值（全市场成交额）— 唯一验证来源
        # ⚠️ 新浪K线API的volume字段=成交量(股数),不是成交额,不可用
        rd = review_data.get(day, {})
        if rd:
            # 标的补充（复盘有的但K线没有的）
            for sname, sdata in rd.get("stocks", {}).items():
                if sname not in rec["stocks"]:
                    rec["stocks"][sname] = sdata
            # 成交额：仅复盘手写值有效
            review_to = rd.get("turnover_review")
            if review_to and review_to > 1000:
                rec["turnover_yi"] = review_to
                rec["turnover_source"] = "review"
        # 非review日不填成交额(sina_kline的volume是股数不是成交额)

        # 只有有数据的日期才保留
        if rec["indices"] or rec["stocks"]:
            records.append(rec)

    return records, index_kline, stock_kline

# ── 图表生成 ──

def generate_dashboard(records):
    os.makedirs(CHART_DIR, exist_ok=True)
    dates_js = json.dumps([r["date"][-5:] for r in records])

    idx_colors = {"上证指数":"#f87171","深证成指":"#60a5fa","创业板指":"#4ade80","科创50":"#c084fc"}
    idx_parts = []
    for idx, color in idx_colors.items():
        pcts = [r.get("indices",{}).get(idx,{}).get("pct",None) for r in records]
        idx_parts.append("{{label:'%s',data:%s,borderColor:'%s',borderWidth:1.5,pointRadius:1.5,tension:0.1,spanGaps:false}}" % (idx, json.dumps(pcts), color))

    stk_colors = {"天山铝业":"#f97316","紫金矿业":"#a78bfa","黄金ETF":"#facc15","科大讯飞":"#38bdf8"}
    stk_parts = []
    for stk, color in stk_colors.items():
        prices = [r.get("stocks",{}).get(stk,{}).get("close",None) for r in records]
        n = len([p for p in prices if p])
        stk_parts.append("{{label:'%s(%d天)',data:%s,borderColor:'%s',borderWidth:1.5,pointRadius:1.5,tension:0.1,spanGaps:false}}" % (stk, n, json.dumps(prices), color))

    turnovers = [r.get("turnover_yi") for r in records]
    ema20, emotions = [], []
    for i, tv in enumerate(turnovers):
        if tv is None or tv < 100:
            ema20.append(None); emotions.append(None); continue
        valid = [v for v in turnovers[max(0,i-19):i+1] if v is not None and v > 100]
        ma = round(sum(valid)/len(valid),1) if len(valid) >= 5 else None
        ema20.append(ma)
        emotions.append(round(tv/ma,2) if tv and ma else None)

    last_to = turnovers[-1] if turnovers[-1] and turnovers[-1] > 100 else None
    last_ema = ema20[-1] if ema20[-1] else None
    last_em = emotions[-1] if emotions[-1] else None

    data_range = "%s ~ %s" % (records[0]['date'], records[-1]['date'])
    n_days = len(records)

    # 构建JS状态面板（不使用f-string，避免JS $与Python冲突）
    em_val = "null" if last_em is None else str(last_em)
    em_tofixed = "null" if last_em is None else last_em
    em_status = "null" if last_em is None else ("'🔴'" if last_em > 1.5 else ("'🟡'" if last_em > 1.3 else "'🟢'"))
    em_tip = "'>1.5=禁仓'"

    status_js = """(function(){const p=document.getElementById('status');const em=%s;const items=[{label:'成交额情绪',v:em===null?'—':em.toFixed(2),d:%s===null?'':'近20日均'+%s.toFixed(0)+'亿',s:%s,tip:'>1.5=禁仓, >1.3=谨慎'},{label:'最新成交额',v:%s===null?'—':(%s/10000).toFixed(2)+'万亿',tip:''},{label:'数据源',v:'新浪K线API',tip:'上证+深证合计',status:'🟢'},{label:'数据范围',v:'%s',tip:'%d个交易日',status:'🟢'}];items.forEach(function(i){var s=i.status||'';p.innerHTML+='<div style=\"display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:#0f172a;border-radius:8px;margin-bottom:10px\"><div><strong>'+i.label+'</strong><div style=\"font-size:.75em;color:#64748b\">'+(i.tip||'')+'</div></div><div style=\"text-align:right\"><span style=\"font-size:1.2em\">'+s+'</span><span style=\"font-size:.9em;color:#94a3b8;margin-left:8px\">'+i.v+'</span></div></div>';});})();""" % (
        "null" if last_em is None else str(last_em),
        "null" if last_ema is None else str(last_ema),
        "null" if last_ema is None else str(last_ema),
        em_status,
        "null" if last_to is None else str(last_to),
        "null" if last_to is None else str(last_to),
        data_range, n_days
    )

    html = """<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>投资纪律仪表盘</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;padding:20px}
.header{text-align:center;padding:20px 0 30px}.header h1{font-size:1.6em;color:#f1f5f9}.header p{color:#94a3b8;margin-top:4px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(520px,1fr));gap:20px;max-width:1200px;margin:0 auto}
.card{background:#1e293b;border-radius:12px;padding:20px;border:1px solid #334155}
.card h2{font-size:.95em;color:#94a3b8;margin-bottom:12px;font-weight:500}.card canvas{max-height:300px}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin-top:8px;font-size:.8em}
.legend-item{display:flex;align-items:center;gap:6px}.legend-dot{width:10px;height:10px;border-radius:50%;display:inline-block}
.footer{text-align:center;padding:30px 0 10px;color:#475569;font-size:.8em}
</style></head><body>
<div class="header"><h1>📐 投资纪律仪表盘</h1><p>""" + data_range + """ · """ + str(n_days) + """ 交易日 · API主驱动(新浪K线)</p></div>
<div class="grid">
<div class="card"><h2>📊 成交额 + 情绪指数</h2><canvas id="c1"></canvas>
<div class="legend"><span class="legend-item"><span class="legend-dot" style="background:#60a5fa"></span>成交额(亿)</span><span class="legend-item"><span class="legend-dot" style="background:#f59e0b;border:dashed 1px #f59e0b"></span>20日均</span><span class="legend-item"><span class="legend-dot" style="background:#f87171"></span>情绪 &gt;1.5=红灯</span></div></div>
<div class="card"><h2>📈 四大指数日涨跌(%)</h2><canvas id="c2"></canvas></div>
<div class="card"><h2>⚠️ 高波动标的收盘价</h2><canvas id="c3"></canvas></div>
<div class="card"><h2>🛡️ 纪律合规</h2><div id="status"></div></div>
</div>
<div class="footer">数据源: 新浪K线API (money.finance.sina.com.cn) · 仅供参考</div>
<script>
const D=""" + dates_js + """;
new Chart(document.getElementById('c1'),{type:'bar',data:{labels:D,datasets:[{label:'成交额(亿)',data:""" + json.dumps(turnovers) + """,backgroundColor:ctx=>{const v=ctx.raw;if(!v)return'rgba(100,116,139,0.3)';return v>35000?'rgba(248,113,113,0.6)':v>30000?'rgba(251,191,36,0.5)':'rgba(96,165,250,0.5)'},borderWidth:0,yAxisID:'y',order:2},{label:'20日均',data:""" + json.dumps(ema20) + """,type:'line',borderColor:'#f59e0b',borderDash:[4,3],borderWidth:1.5,pointRadius:0,fill:false,yAxisID:'y',order:1},{label:'情绪',data:""" + json.dumps(emotions) + """,type:'line',borderColor:'#f87171',borderWidth:2,pointRadius:2,pointBackgroundColor:'#f87171',fill:false,yAxisID:'y1',order:0}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{position:'left',title:{display:true,text:'亿',color:'#94a3b8'},ticks:{color:'#94a3b8'},grid:{color:'#334155'}},y1:{position:'right',title:{display:true,text:'情绪',color:'#f87171'},ticks:{color:'#f87171'},grid:{drawOnChartArea:false},min:0.5,max:2.0}}}}});
const idxDS=[];""" + ";".join(idx_parts) + """
new Chart(document.getElementById('c2'),{type:'line',data:{labels:D,datasets:idxDS},options:{responsive:true,plugins:{legend:{position:'top',labels:{color:'#94a3b8',usePointStyle:true}}},scales:{y:{title:{display:true,text:'%',color:'#94a3b8'},ticks:{color:'#94a3b8'},grid:{color:'#334155'}},x:{ticks:{color:'#64748b',maxRotation:60}}}}});
const stkDS=[];""" + ";".join(stk_parts) + """
new Chart(document.getElementById('c3'),{type:'line',data:{labels:D,datasets:stkDS},options:{responsive:true,plugins:{legend:{position:'top',labels:{color:'#94a3b8',usePointStyle:true}}},scales:{y:{title:{display:true,text:'元',color:'#94a3b8'},ticks:{color:'#94a3b8'},grid:{color:'#334155'}},x:{ticks:{color:'#64748b',maxRotation:60}}}}});
""" + status_js + """
</script></body></html>"""

    with open(CHART_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print("\n📊 图表: " + CHART_FILE)

# ── main ──

if __name__ == "__main__":
    records, idx_kline, stk_kline = build_records()

    # 统计数据
    with_to = [r for r in records if r.get("turnover_yi")]
    with_stk = [r for r in records if r.get("stocks")]

    print(f"\n{'='*60}")
    print(f"📊 统计")
    print(f"{'='*60}")
    print(f"  交易日: {len(records)} 天  ({START_DATE} ~ {END_DATE})")
    print(f"  含成交额: {len(with_to)} 天")
    print(f"  含标的价格: {len(with_stk)} 天")
    print(f"  数据源: 新浪K线 API（主）+ 复盘手写成交额（优先）")

    if len(with_to) >= 5:
        to_vals = [r["turnover_yi"] for r in with_to]
        latest = to_vals[-1]
        avg20 = sum(to_vals[-20:]) / min(len(to_vals), 20)
        em = round(latest / avg20, 2)
        flag = "🔴" if em > 1.5 else ("🟡" if em > 1.3 else "🟢")
        print(f"\n  最新成交额: {latest:,.0f}亿")
        print(f"  20日均:     {avg20:,.0f}亿")
        print(f"  成交额情绪: {em} {flag}")

        # 列出所有 > 1.3 的交易日
        print(f"\n  ⚠️ 情绪偏热日 (> 1.3):")
        to_arr = [r.get("turnover_yi") for r in records]
        for i, r in enumerate(records):
            tv = r.get("turnover_yi")
            if not tv or i < 5: continue
            recent = [v for v in to_arr[max(0,i-19):i+1] if v]
            if len(recent) >= 5:
                ma = sum(recent)/len(recent)
                ratio = tv/ma
                if ratio > 1.3:
                    flag2 = "🔴" if ratio > 1.5 else "🟡"
                    print(f"    {r['date']}: {ratio:.2f} {flag2}  ({tv:,.0f}亿 / 均{ma:,.0f}亿)")

    # 三日振幅
    if len(records) >= 3:
        print(f"\n  最新三日振幅:")
        for stk in ["天山铝业", "紫金矿业", "有色ETF"]:
            prices = [r.get("stocks",{}).get(stk,{}).get("close") for r in records[-3:]]
            prices = [p for p in prices if p]
            if len(prices) >= 3:
                hi,lo = max(prices),min(prices)
                amp = round((hi-lo)/lo*100,1)
                f = "🔴" if amp>15 else ("🟡" if amp>8 else "🟢")
                print(f"    {stk}: {amp}% {f}")

    # 保存
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"records": records, "source": "sina_kline_api"}, f, ensure_ascii=False, indent=2)
    print(f"\n📝 {HISTORY_FILE}")

    # 图表
    generate_dashboard(records)
