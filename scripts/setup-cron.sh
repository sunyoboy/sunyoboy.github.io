#!/bin/bash
# 设置定时任务（macOS launchd / Linux cron）
# 用法：chmod +x scripts/setup-cron.sh && ./scripts/setup-cron.sh

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT/scripts/fetch-market-data.py"
LOG="$ROOT/scripts/fetch.log"

echo "📋 KnowingDoing 定时任务设置"
echo "============================"
echo ""

# --- macOS: 使用 launchd ---
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLIST="$HOME/Library/LaunchAgents/com.knowingdoing.fetch.plist"

    # 检查是否已安装 akshare
    if ! python3 -c "import akshare" 2>/dev/null; then
        echo "⚠️  akshare 未安装，正在安装..."
        pip3 install akshare pandas
    fi

    cat > "$PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.knowingdoing.fetch</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$SCRIPT</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>15</integer>
        <key>Minute</key><integer>35</integer>
        <key>Weekday</key><integer>1</integer>
    </dict>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>15</integer>
        <key>Minute</key><integer>35</integer>
        <key>Weekday</key><integer>2</integer>
    </dict>
    <dict>
        <key>Hour</key><integer>15</integer>
        <key>Minute</key><integer>35</integer>
        <key>Weekday</key><integer>3</integer>
    </dict>
    <dict>
        <key>Hour</key><integer>15</integer>
        <key>Minute</key><integer>35</integer>
        <key>Weekday</key><integer>4</integer>
    </dict>
    <dict>
        <key>Hour</key><integer>15</integer>
        <key>Minute</key><integer>35</integer>
        <key>Weekday</key><integer>5</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$LOG</string>
    <key>StandardErrorPath</key>
    <string>$LOG</string>
    <key>WorkingDirectory</key>
    <string>$ROOT</string>
</dict>
</plist>
EOF

    launchctl unload "$PLIST" 2>/dev/null
    launchctl load "$PLIST"
    echo ""
    echo "✅ launchd 定时任务已设置"
    echo "   每个交易日 15:35 自动执行"
    echo "   日志: $LOG"
    echo ""
    echo "   管理命令:"
    echo "   launchctl list | grep knowingdoing   # 查看状态"
    echo "   launchctl unload $PLIST               # 停止"
    echo "   launchctl load $PLIST                 # 启动"

# --- Linux: 使用 cron ---
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CRON_LINE="35 15 * * 1-5 cd $ROOT && python3 $SCRIPT >> $LOG 2>&1"
    (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
    echo "✅ cron 定时任务已设置"
    echo "   crontab -l   # 查看"
    echo "   crontab -r   # 删除"
fi

echo ""
echo "📊 手动测试: python3 $SCRIPT"
echo "📊 模拟指定日期: python3 $SCRIPT 2026-06-17"
