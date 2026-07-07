# 华泰证券 AI涨乐 Skills · 安装与量化接入指南

> 2026-07-07 · 五个 Skill 覆盖行情查询、条件选股、模拟交易、金融分析、自选股管理。
> 全部通过华泰 API 调用，需预先申请 `HT_APIKEY`。

---

## 一、Skills 一览

| Skill | 功能 | 核心工具 | 量化用途 |
|------|------|------|------|
| **query-indicator** | 金融指标与行情检索 | `queryIndicator` | 获取 PE/PB/MA/行情数据 |
| **select-stock** | 条件选股 | `selectStock` | 按多维度筛选标的池 |
| **a-share-paper-trading** | A 股模拟交易 | `getQuote/searchStock/submitOrder/getPositions` | 模拟下单+持仓跟踪 |
| **financial-analysis** | 金融分析与资讯 | `diagnosisStock/marketInsight` | 个股诊断+大盘研判 |
| **watchlist-management** | 自选股管理 | `addWatchlist/getWatchlist` | 维护候选池 |

---

## 二、前提条件

- Python 3.9+
- 已从华泰证券获取 `HT_APIKEY`
- macOS / Linux（Windows 需调整路径）

```bash
# 验证 Python
python3 --version  # 需 ≥ 3.9
```

---

## 三、一键安装脚本

> 将以下脚本保存为 `install-htsc-skills.sh`，执行 `bash install-htsc-skills.sh`。
> **不会修改系统 Python，不需要 sudo。**

```bash
#!/bin/bash
set -e

# ============================================
# 华泰 AI涨乐 Skills 一键安装
# 适用: Claude Code / OpenClaw / Hermes / WorkBuddy
# ============================================

echo "📦 华泰证券 AI涨乐 Skills 安装"

# ---- 1. 检测 Agent 类型，确定安装目录 ----
detect_install_root() {
  [ -n "$SKILLS_INSTALL_DIR" ] && echo "$SKILLS_INSTALL_DIR" && return
  [ -n "$OPENCLAW_SKILLS_DIR"  ] && echo "$OPENCLAW_SKILLS_DIR"  && return
  [ -n "$HERMES_SKILLS_DIR"    ] && echo "$HERMES_SKILLS_DIR"    && return
  [ -n "$WORKBUDDY_SKILLS_DIR" ] && echo "$WORKBUDDY_SKILLS_DIR" && return

  # 检测 Claude Code
  if [ -d "$HOME/.claude" ]; then
    echo "$HOME/.claude/skills"
    return
  fi

  # 检测其他 Agent
  _pid=$$
  for _ in 1 2 3 4 5; do
    _pid=$(ps -o ppid= -p "$_pid" 2>/dev/null | tr -d ' ')
    [ -z "$_pid" ] || [ "$_pid" = "1" ] && break
    _comm=$(ps -o comm= -p "$_pid" 2>/dev/null)
    case "$_comm" in
      *openclaw*|*qclaw*) echo "$HOME/.openclaw/skills" && return ;;
      *hermes*)           echo "$HOME/.hermes/skills"   && return ;;
      *workbuddy*)        echo "$HOME/.workbuddy/skills" && return ;;
    esac
  done
  echo "$HOME/.claude/skills"
}

INSTALL_ROOT=$(detect_install_root)
echo "📁 安装目录: $INSTALL_ROOT"
mkdir -p "$INSTALL_ROOT"

# ---- 2. 配置 API Key ----
if [ -z "$HT_APIKEY" ]; then
  echo ""
  echo "⚠️  未检测到环境变量 HT_APIKEY。"
  echo "   请先申请 API Key: https://ai.zhangle.com"
  read -s -p "   请输入 HT_APIKEY (输入不显示): " input_key
  echo ""
  if [ -z "$input_key" ]; then
    echo "❌ 输入为空，安装终止。"
    exit 1
  fi
  HT_APIKEY_VALUE="$input_key"
else
  HT_APIKEY_VALUE="$HT_APIKEY"
  echo "✅ 检测到 HT_APIKEY 环境变量"
fi

# 写入 shell 配置文件（永久生效）
for RC_FILE in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
  if [ -f "$RC_FILE" ]; then
    grep -v "^export HT_APIKEY=" "$RC_FILE" > /tmp/_ht_rc_tmp 2>/dev/null && mv /tmp/_ht_rc_tmp "$RC_FILE"
    echo "export HT_APIKEY=\"$HT_APIKEY_VALUE\"" >> "$RC_FILE"
  fi
done

# 保存到独立配置文件（非交互 shell 可用）
mkdir -p ~/.htsc-skills
printf "HT_APIKEY=%s\n" "$HT_APIKEY_VALUE" > ~/.htsc-skills/config
chmod 600 ~/.htsc-skills/config
export HT_APIKEY="$HT_APIKEY_VALUE"
echo "✅ HT_APIKEY 已配置"

# ---- 3. 下载并安装 5 个 Skills ----
SKILLS=(
  "query-indicator:query-indicator_763636519.zip"
  "financial-analysis:financial-analysis_473880149.zip"
  "a-share-paper-trading:a-share-paper-trading_140059101.zip"
  "select-stock:select-stock_506098113.zip"
  "watchlist-management:watchlist-management_444870522.zip"
)

BASE_URL="https://d.zhangle.com/nzl/allinone/skills/docs/1780588800000"

for skill in "${SKILLS[@]}"; do
  name="${skill%%:*}"
  file="${skill##*:}"
  echo ""
  echo "--- 安装 $name ---"
  
  # 清理旧版本
  rm -rf "$INSTALL_ROOT/$name"
  
  # 下载
  curl -fsSL -o "/tmp/${name}.zip" "${BASE_URL}/${file}"
  
  # 解压
  unzip -q -o "/tmp/${name}.zip" -d "$INSTALL_ROOT"
  rm "/tmp/${name}.zip"
  
  # 验证
  if [ -f "$INSTALL_ROOT/$name/SKILL.md" ]; then
    echo "  ✅ $name 安装成功"
  else
    echo "  ❌ $name 安装失败"
  fi
done

# ---- 4. 验证 ----
echo ""
echo "=== 验证安装 ==="

verify_skill() {
  local name=$1
  local py=$2
  if [ -f "$INSTALL_ROOT/$name/$py" ] && [ -f "$INSTALL_ROOT/$name/SKILL.md" ]; then
    echo "  ✅ $name"
  else
    echo "  ❌ $name (文件缺失)"
  fi
}

verify_skill "query-indicator"        "query_indicator.py"
verify_skill "financial-analysis"     "financial_analysis.py"
verify_skill "a-share-paper-trading"  "a_share_paper_trading.py"
verify_skill "select-stock"           "select_stock.py"
verify_skill "watchlist-management"   "watchlist_management.py"

# ---- 5. 连通性测试 ----
echo ""
echo "=== 连通性测试 ==="

test_api() {
  python3 "$INSTALL_ROOT/a-share-paper-trading/a_share_paper_trading.py" \
    getAccountBalance 2>/dev/null | \
    python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get('ok') else 1)" 2>/dev/null \
    && echo "  ✅ API 连通正常" \
    || echo "  ⚠️  API 连通失败（请检查 HT_APIKEY 和网络）"
}
test_api

echo ""
echo "🎉 安装完成！"
echo "   Skills 目录: $INSTALL_ROOT"
echo "   配置文件:    ~/.htsc-skills/config"
echo ""
echo "   使用方式:"
echo "     python3 $INSTALL_ROOT/query-indicator/query_indicator.py queryIndicator --query \"上证指数\""
echo "     python3 $INSTALL_ROOT/select-stock/select_stock.py selectStock --query \"银行PE<5\""
echo "     python3 $INSTALL_ROOT/a-share-paper-trading/a_share_paper_trading.py getAccountBalance"
```

---

## 四、手动分步安装（如脚本不可用）

### 1. 配置环境变量

```bash
# 临时生效（当前终端）
export HT_APIKEY="你的API_KEY"

# 永久生效（追加到 ~/.zshrc 或 ~/.bashrc）
echo 'export HT_APIKEY="你的API_KEY"' >> ~/.zshrc
source ~/.zshrc
```

### 2. 确定安装目录

```bash
# Claude Code
SKILLS_DIR="$HOME/.claude/skills"

# 或手动指定
export SKILLS_INSTALL_DIR="$HOME/.claude/skills"
```

### 3. 下载解压

```bash
mkdir -p "$SKILLS_DIR"
BASE="https://d.zhangle.com/nzl/allinone/skills/docs/1780588800000"

for skill in \
  "query-indicator:query-indicator_763636519.zip" \
  "financial-analysis:financial-analysis_473880149.zip" \
  "a-share-paper-trading:a-share-paper-trading_140059101.zip" \
  "select-stock:select-stock_506098113.zip" \
  "watchlist-management:watchlist-management_444870522.zip"
do
  name="${skill%%:*}" file="${skill##*:}"
  curl -fsSL "$BASE/$file" -o "/tmp/$name.zip"
  unzip -q -o "/tmp/$name.zip" -d "$SKILLS_DIR"
  rm "/tmp/$name.zip"
done
```

### 4. 验证

```bash
python3 "$SKILLS_DIR/a-share-paper-trading/a_share_paper_trading.py" getAccountBalance
# 返回 {"ok": true, "data": {...}} 即成功
```

---

## 五、量化接入方案

### 方案 A：Claude Code 交互式（Skill 工具调用）

在 Claude Code 中直接使用——Skill 会被自动识别为可调用工具：

```
/query-indicator     → 查行情/指标
/select-stock        → 条件选股
/a-share-paper-trading → 模拟下单
```

### 方案 B：Python 脚本调用

```python
import subprocess, json

SKILLS = "$HOME/.claude/skills"

def query_indicator(query):
    r = subprocess.run([
        "python3", f"{SKILLS}/query-indicator/query_indicator.py",
        "queryIndicator", "--query", query
    ], capture_output=True, text=True)
    return json.loads(r.stdout)

def select_stock(query):
    r = subprocess.run([
        "python3", f"{SKILLS}/select-stock/select_stock.py",
        "selectStock", "--query", query
    ], capture_output=True, text=True)
    return json.loads(r.stdout)

def paper_buy(stock_code, exchange, price, quantity):
    r = subprocess.run([
        "python3", f"{SKILLS}/a-share-paper-trading/a_share_paper_trading.py",
        "submitOrder",
        "--stock-code", stock_code,
        "--exchange", exchange,
        "--direction", "buy",
        "--order-type", "limit",
        "--price", str(price),
        "--quantity", str(quantity)
    ], capture_output=True, text=True)
    return json.loads(r.stdout)

# 示例：查 PE < 5 的银行股 → 模拟买入
banks = select_stock("银行板块市盈率最低的前3只股票")
print(banks)
```

### 方案 C：整合到现有脚本

```bash
# 替代 fetch-market-data.py 的部分功能
python3 $SKILLS_DIR/query-indicator/query_indicator.py queryIndicator \
  --query "中证500ETF(510500)最新价、涨跌幅、MA5偏离度"

# 替代人工选股
python3 $SKILLS_DIR/select-stock/select_stock.py selectStock \
  --query "PE<15且ROE>15%且营收同比增长>20%的消费股"
```

---

## 六、Skill 工具速查

### a-share-paper-trading（模拟交易）

| 工具 | 说明 | 示例 |
|------|------|------|
| `searchStock` | 搜索股票 | `--query "中证500ETF"` |
| `getQuote` | 实时报价 | `--stock-code "510500" --exchange "SH"` |
| `getAccountBalance` | 账户总览 | 无参数 |
| `getPositions` | 持仓明细 | 无参数 |
| `submitOrder` | 下单 | `--stock-code/--exchange/--direction/--order-type/--price/--quantity` |
| `cancelOrder` | 撤单 | `--order-id "xxx"` |
| `listPendingOrders` | 未成交委托 | 无参数 |
| `listTradeHistory` | 成交记录 | 无参数 |

### select-stock（条件选股）

```
"银行板块市盈率最低的前5只股票"
"消费行业ROE>20%且营收增长>15%"
"上周涨幅前10的科技股"
"均线金叉的创业板股票"
"业绩超预期的标的"
```

### query-indicator（指标查询）

```
"上证指数最新价和成交额"
"茅台PE/PB/ROE"
"中证500ETF的MA5和MA20偏离度"
"银行板块平均市盈率"
"黄金ETF近一个月涨幅"
```

---

## 七、注意事项

- 五个 Skill 共用一个 `HT_APIKEY`，只需配置一次
- 模拟交易**不涉及真实资金**
- Skill 本身只做 HTTP 转发，业务逻辑由华泰后端提供
- 如后端服务不可用，Skill 返回结构化 error（含原因）
- 源码在 `$SKILLS_DIR/<name>/`，许可证见各 Skill 的 README.md

---

## 相关文档

- [资产定价权全景图](asset-pricing-power.md) — 买之前先问价格由谁决定
- [三账户ETF观察清单](etf-watchlist-2026-07-06.md) — 38只候选池
- [债券ETF投资入门](bond-investment-basics.md) — 30年国债购买指南
