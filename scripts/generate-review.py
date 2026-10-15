#!/usr/bin/env python3
"""
一键复盘生成器 · KnowingDoing
=============================

把 SOP 里的「拉数据 → 诊断 → 写复盘」三步压成一条命令。

流程：
  1. 抓行情数据   （复用 fetch-market-data.py 的腾讯接口）
  2. 持仓纪律诊断 （调用 ma5-deviation.py）
  3. 申万行业全景 （调用 shenwan-monitor.py）
  4. 组织上下文   （指数表 + 标的报价 + 持仓诊断 + 行业全景 + 持仓明细 + 纪律规则）
  5. AI 分析      （可选：OpenAI 兼容接口，生成完整复盘 Markdown）
       └─ 未配置 API Key 时：输出「数据填充草稿 + 给 AI 的提示词」，可在 TraeCN / Claude 中一键完成

用法：
  python3 scripts/generate-review.py                 # 今天 · 有 Key 则 AI 生成，无 Key 则出草稿
  python3 scripts/generate-review.py --no-ai         # 仅数据填充，不做 AI
  python3 scripts/generate-review.py --prompt-only   # 只打印给 AI 的提示词（不落盘）
  python3 scripts/generate-review.py --date 2026-05-25  # 指定日期（腾讯接口仅返回实时快照，慎用）
  python3 scripts/generate-review.py --force         # 覆盖已存在的复盘文件

AI 配置（.env 或环境变量）：
  REVIEW_LLM_API_KEY   必填才有 AI 能力
  REVIEW_LLM_BASE_URL  默认 https://api.deepseek.com
  REVIEW_LLM_MODEL     默认 deepseek-flash（DeepSeek V4.1 Flash）
"""

import os
import sys
import json
import argparse
import subprocess
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
REVIEW_DIR = os.path.join(ROOT, "review")

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-flash"


# ─────────────────────────────────────────────────────────────
# 1. 复用 fetch-market-data.py 的抓取能力（文件名带连字符，用 importlib 加载）
# ─────────────────────────────────────────────────────────────
def load_fetch_module():
    import importlib.util
    path = os.path.join(SCRIPTS, "fetch-market-data.py")
    spec = importlib.util.spec_from_file_location("fetch_market_data", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_script(name):
    """运行 scripts/ 下的脚本并捕获 stdout（用于 ma5 / shenwan 诊断）"""
    path = os.path.join(SCRIPTS, name)
    if not os.path.exists(path):
        return f"⚠️ 脚本不存在：{name}"
    try:
        out = subprocess.run(
            [sys.executable, path],
            capture_output=True, text=True, timeout=180, cwd=ROOT,
        )
        return out.stdout.strip() or out.stderr.strip() or f"⚠️ {name} 无输出"
    except Exception as e:
        return f"⚠️ {name} 执行失败：{e}"


def load_portfolio():
    p = os.path.join(SCRIPTS, "portfolio.json")
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# ─────────────────────────────────────────────────────────────
# 2. 组织上下文
# ─────────────────────────────────────────────────────────────
DISCIPLINE_RULES = """\
止损规则（价格 × 时间）：
- 宽基ETF：-3% 止损；行业ETF：-5% / 20 交易日；个股：-8% / 10 交易日；所有个股：-20% 硬止损
买入前三问（缺一不买）：① PE<20（ETF 看 PE 分位<20%）② 近10日主力净流入 ③ 无炒作风险公告
不碰清单：月初/月末/节假日前不开新仓；PE>100 或利润崩塌不碰；大股东减持中不碰；金叉已破不加仓
"""

OUTPUT_STRUCTURE = """\
请输出一份完整的每日复盘 Markdown，严格使用以下结构（缺失数据用「—」占位，不要编造数字）：

# {date}

## A股复盘
### 指数表现        （表格：指数/收盘/涨跌幅）
### 重点标的        （表格：标的/收盘/涨跌幅/状态）
### 盘面特征        （3-5 条，有数据支撑）
### 今日驱动        （按权重排序，每条一句话因果链）
### 热门板块        （领涨/领跌 + 逻辑）
### 资金流向        （流入/流出表格）
### 机构观点
### 技术面          （每个指数一句话）
### 后市关键        （3-5 个待验证信号）
## 做了什么        （交易记录表格：股票名称/代码/数量）
## 持仓盈亏        （三账户表格：账户/总资产/今日盈亏/浮动盈亏/仓位）
## 学到了什么      （至少 1 条反思，不要流水账）
## 明日计划        （具体标的+价格+条件+不做清单）

要求：专业、克制、只基于给定数据推断；不确定的地方标注「需人工确认」。
"""


def build_context(date_str, index_data, watchlist_data, ma5_out, shenwan_out, portfolio):
    idx_rows = "\n".join(
        f"| {n} | {d['close']} | {d['pct_chg']:+.2f}% |"
        for n, d in index_data.items()
    ) or "| — | — | — |"

    wl_rows = "\n".join(
        f"| {n} | {d['close']} | {d['pct_chg']:+.2f}% |"
        for n, d in (watchlist_data or {}).items()
    ) or "| — | — | — |"

    holdings = portfolio.get("holdings", [])
    hold_lines = "\n".join(
        f"- {h['name']}（{h.get('code','')}）{h.get('shares','?')}股 成本{h.get('cost','?')} "
        f"[{h.get('type','')}/{h.get('sector','')}] 止损线{h.get('stop_loss','—')}"
        for h in holdings
    ) or "（无持仓数据）"

    total = portfolio.get("total_assets")
    cash = portfolio.get("cash")

    return f"""\
## 复盘日期
{date_str}

## 指数行情（腾讯接口实时快照）
| 指数 | 收盘 | 涨跌幅 |
|------|------|--------|
{idx_rows}

## 重点标的行情
| 标的 | 收盘 | 涨跌幅 |
|------|------|--------|
{wl_rows}

## 账户概览
总资产 {total} · 现金 {cash}
持仓明细：
{hold_lines}

## 持仓 MA5 偏离度诊断（ma5-deviation.py 输出）
{ma5_out}

## 申万行业全景（shenwan-monitor.py 输出）
{shenwan_out}

## 纪律规则参考
{DISCIPLINE_RULES}
"""


# ─────────────────────────────────────────────────────────────
# 3. AI 调用（OpenAI 兼容）
# ─────────────────────────────────────────────────────────────
def call_llm(prompt, api_key, base_url, model):
    url = base_url.rstrip("/") + "/v1/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "你是专业的 A 股交易复盘助手，输出克制、准确、结构化的中文复盘报告。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


# ─────────────────────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="一键复盘生成器")
    ap.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    ap.add_argument("--no-ai", action="store_true", help="仅数据填充，不调用 AI")
    ap.add_argument("--prompt-only", action="store_true", help="只打印给 AI 的提示词")
    ap.add_argument("--force", action="store_true", help="覆盖已存在的复盘文件")
    args = ap.parse_args()

    date_str = args.date
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    if dt.weekday() >= 5:
        print(f"🛑 {date_str} 是周末，A 股非交易日。如确需生成加 --force。")
        if not args.force:
            sys.exit(0)

    print(f"📊 一键复盘生成器 · {date_str}\n")

    # Step 1: 抓行情
    print("[1/3] 抓取行情数据 …")
    fetch = load_fetch_module()
    index_data = fetch.fetch_from_tencent(fetch.INDICES, "指数") or {}
    watchlist_data = fetch.fetch_from_tencent(fetch.WATCHLIST, "标的") or {}

    # Step 2: 纪律诊断
    print("\n[2/3] 持仓纪律诊断 …")
    ma5_out = run_script("ma5-deviation.py")
    shenwan_out = run_script("shenwan-monitor.py")
    portfolio = load_portfolio()

    # Step 3: 组织上下文
    print("\n[3/3] 组织上下文并生成 …")
    context = build_context(date_str, index_data, watchlist_data, ma5_out, shenwan_out, portfolio)
    prompt = context + "\n\n" + OUTPUT_STRUCTURE.format(date=date_str)

    file_dir = os.path.join(REVIEW_DIR, dt.strftime("%Y"), dt.strftime("%m"))
    file_path = os.path.join(file_dir, f"{date_str}.md")
    prompt_path = os.path.join(file_dir, f"{date_str}-ai-prompt.md")

    if args.prompt_only:
        print("\n" + "=" * 60 + "\n")
        print(prompt)
        return

    if os.path.exists(file_path) and not args.force:
        print(f"  ⚠️ {file_path} 已存在，跳过（加 --force 覆盖）。")
        print(f"  💡 提示词仍保存到：{prompt_path}")
        os.makedirs(file_dir, exist_ok=True)
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        return

    os.makedirs(file_dir, exist_ok=True)

    api_key = os.environ.get("REVIEW_LLM_API_KEY")
    if args.no_ai or not api_key:
        # 无 AI：落盘「数据填充草稿 + 提示词」
        draft = prompt  # 上下文本身即为可读的数据填充草稿
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"> ⚠️ 数据填充草稿（未做 AI 分析）。运行 `generate-review.py`（配置 REVIEW_LLM_API_KEY）或把 `{os.path.basename(prompt_path)}` 交给 TraeCN/Claude 即可补全。\n\n")
            f.write(draft)
        print(f"  📝 草稿已生成：{file_path}")
        print(f"  🤖 提示词已保存：{prompt_path}")
        if not api_key and not args.no_ai:
            print("  ℹ️ 未检测到 REVIEW_LLM_API_KEY —— 已输出草稿+提示词。")
            print("     补 AI：把上面提示词贴给 TraeCN/Claude，或配置 Key 后重跑。")
        return

    # 有 Key：调用 AI 生成完整复盘
    base_url = os.environ.get("REVIEW_LLM_BASE_URL", DEFAULT_BASE_URL)
    model = os.environ.get("REVIEW_LLM_MODEL", DEFAULT_MODEL)
    print(f"  🤖 调用 AI（{model} @ {base_url}）…")
    try:
        content = call_llm(prompt, api_key, base_url, model)
    except Exception as e:
        print(f"  ❌ AI 调用失败：{e}")
        print("     已回退为草稿模式，提示词保存到：", prompt_path)
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        sys.exit(1)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ 复盘已生成：{file_path}")
    print(f"\n{'='*50}\n📌 下一步：人工审校数据 → 更新 catalog.md + config.mjs → npm run build → git push")


if __name__ == "__main__":
    main()
