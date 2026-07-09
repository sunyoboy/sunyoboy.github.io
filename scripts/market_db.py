#!/usr/bin/env python3
"""
SQLite 本地数据仓库 · 持久化存储 A 股历史行情数据
================================================================
用法：
  from scripts.market_db import MarketDB
  db = MarketDB()
  db.save_index(date, code, name, open_p, high, low, close, pct, vol)
  db.save_etf(date, code, name, open_p, high, low, close, pct, ma5, ma20, ma60, dev5, vol_ratio)
  db.save_shenwan(date, industry, etf_code, etf_name, close, pct, signal)
  db.save_position(date, account, code, name, qty, cost, price, mv, profit, profit_pct)

查询：
  rows = db.query("SELECT * FROM etf_daily WHERE code='510500' ORDER BY date DESC LIMIT 30")
"""

import os
import sqlite3
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "data", "market.db")


class MarketDB:
    """市场数据本地 SQLite 仓库"""

    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_tables()

    def _init_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS index_daily (
                    date TEXT NOT NULL,
                    code TEXT NOT NULL,
                    name TEXT,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    close_price REAL,
                    change_pct REAL,
                    volume REAL,
                    PRIMARY KEY (date, code)
                );

                CREATE TABLE IF NOT EXISTS etf_daily (
                    date TEXT NOT NULL,
                    code TEXT NOT NULL,
                    name TEXT,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    close_price REAL,
                    change_pct REAL,
                    ma5 REAL,
                    ma20 REAL,
                    ma60 REAL,
                    dev5 REAL,
                    volume_ratio REAL,
                    PRIMARY KEY (date, code)
                );

                CREATE TABLE IF NOT EXISTS shenwan_daily (
                    date TEXT NOT NULL,
                    industry TEXT NOT NULL,
                    etf_code TEXT,
                    etf_name TEXT,
                    close_price REAL,
                    change_pct REAL,
                    signal TEXT,
                    PRIMARY KEY (date, industry)
                );

                CREATE TABLE IF NOT EXISTS position_snapshot (
                    date TEXT NOT NULL,
                    account TEXT NOT NULL,
                    code TEXT NOT NULL,
                    name TEXT,
                    quantity REAL,
                    cost_price REAL,
                    current_price REAL,
                    market_value REAL,
                    profit REAL,
                    profit_pct REAL,
                    PRIMARY KEY (date, account, code)
                );

                CREATE INDEX IF NOT EXISTS idx_etf_date ON etf_daily(date DESC);
                CREATE INDEX IF NOT EXISTS idx_etf_code ON etf_daily(code);
                CREATE INDEX IF NOT EXISTS idx_index_date ON index_daily(date DESC);
                CREATE INDEX IF NOT EXISTS idx_shenwan_date ON shenwan_daily(date DESC);
            """)

    # ── 写入方法 ──

    def save_index(self, date, code, name, open_p=None, high=None, low=None,
                   close=None, pct=None, vol=None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO index_daily
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (date, code, name, open_p, high, low, close, pct, vol))

    def save_etf(self, date, code, name, open_p=None, high=None, low=None,
                 close=None, pct=None, ma5=None, ma20=None, ma60=None,
                 dev5=None, vol_ratio=None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO etf_daily
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (date, code, name, open_p, high, low, close, pct,
                  ma5, ma20, ma60, dev5, vol_ratio))

    def save_shenwan(self, date, industry, etf_code, etf_name,
                     close=None, pct=None, signal="均衡"):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO shenwan_daily
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (date, industry, etf_code, etf_name, close, pct, signal))

    def save_position(self, date, account, code, name, quantity,
                      cost, price, mv, profit, profit_pct):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO position_snapshot
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (date, account, code, name, quantity, cost, price,
                  mv, profit, profit_pct))

    # ── 批量写入 ──

    def save_indices_batch(self, date, indices_dict):
        """indices_dict = {code: {name, open, high, low, close, pct, vol}}"""
        with sqlite3.connect(self.db_path) as conn:
            for code, d in indices_dict.items():
                conn.execute("""
                    INSERT OR REPLACE INTO index_daily VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (date, code, d.get('name'), d.get('open'), d.get('high'),
                      d.get('low'), d.get('close'), d.get('pct'), d.get('vol')))

    def save_etfs_batch(self, date, etfs_dict):
        """etfs_dict = {code: {name, open, high, low, close, pct, ma5, ma20, ma60, dev5, vol_ratio}}"""
        with sqlite3.connect(self.db_path) as conn:
            for code, d in etfs_dict.items():
                conn.execute("""
                    INSERT OR REPLACE INTO etf_daily VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (date, code, d.get('name'), d.get('open'), d.get('high'),
                      d.get('low'), d.get('close'), d.get('pct'),
                      d.get('ma5'), d.get('ma20'), d.get('ma60'),
                      d.get('dev5'), d.get('vol_ratio')))

    def save_shenwan_batch(self, date, rows):
        """rows = [{industry, etf_code, etf_name, close, pct, signal}]"""
        with sqlite3.connect(self.db_path) as conn:
            for r in rows:
                conn.execute("""
                    INSERT OR REPLACE INTO shenwan_daily VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (date, r['industry'], r.get('etf_code'), r.get('etf_name'),
                      r.get('close'), r.get('pct'), r.get('signal', '均衡')))

    # ── 查询方法 ──

    def query(self, sql, params=None):
        """执行查询并返回所有行"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(sql, params or ())
            return [dict(row) for row in cur.fetchall()]

    def latest_date(self, table="index_daily"):
        """获取最新数据的日期"""
        row = self.query(f"SELECT MAX(date) as d FROM {table}")
        return row[0]['d'] if row and row[0]['d'] else None

    def get_etf_history(self, code, days=30):
        """获取 ETF 最近 N 天数据"""
        return self.query("""
            SELECT * FROM etf_daily
            WHERE code = ? ORDER BY date DESC LIMIT ?
        """, (code, days))

    def get_index_history(self, code, days=30):
        """获取指数最近 N 天数据"""
        return self.query("""
            SELECT * FROM index_daily
            WHERE code = ? ORDER BY date DESC LIMIT ?
        """, (code, days))

    def get_shenwan_ranking(self, date=None, order="ASC"):
        """获取某日申万行业排名"""
        if date is None:
            date = self.latest_date("shenwan_daily")
        return self.query(f"""
            SELECT * FROM shenwan_daily
            WHERE date = ? ORDER BY change_pct {order}
        """, (date,))

    def get_position_history(self, code, days=30):
        """获取某标的的持仓历史"""
        return self.query("""
            SELECT * FROM position_snapshot
            WHERE code = ? ORDER BY date DESC LIMIT ?
        """, (code, days))

    # ── 统计方法 ──

    def count_days_below_ma20(self, code, days=10):
        """某 ETF 最近 N 天收盘价低于 MA20 的天数"""
        rows = self.query("""
            SELECT date, close_price, ma20 FROM etf_daily
            WHERE code = ? AND ma20 IS NOT NULL
            ORDER BY date DESC LIMIT ?
        """, (code, days))
        return sum(1 for r in rows if r['close_price'] and r['ma20']
                   and r['close_price'] < r['ma20'])

    def sector_rotation(self, date=None):
        """当前风格：防御 or 进攻？"""
        if date is None:
            date = self.latest_date("shenwan_daily")
        top5 = self.get_shenwan_ranking(date, "DESC")[:5]
        bottom5 = self.get_shenwan_ranking(date, "ASC")[:5]
        return {
            'date': date,
            'leaders': [(r['industry'], r['change_pct']) for r in top5],
            'laggards': [(r['industry'], r['change_pct']) for r in bottom5],
        }


# ── 命令行入口 ──

if __name__ == "__main__":
    db = MarketDB()
    print(f"📦 数据库: {db.db_path}")
    for table in ['index_daily', 'etf_daily', 'shenwan_daily', 'position_snapshot']:
        row = db.query(f"SELECT COUNT(*) as cnt FROM {table}")[0]
        print(f"  {table}: {row['cnt']} 条")
    latest = db.latest_date()
    print(f"  最新日期: {latest or '无数据'}")
