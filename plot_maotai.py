# -*- coding: utf-8 -*-
"""
贵州茅台 (600519.SH) 历史日线数据分析脚本
从 Tushare 获取的数据，绘制收盘价曲线并保存 CSV
"""

import json
import matplotlib
matplotlib.use("Agg")  # 非交互式后端，无需 GUI
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# ==================== 1. 读取数据 ====================
with open("maotai_data.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# 转换为 DataFrame
df = pd.DataFrame(raw_data)

# ==================== 2. 数据整理 ====================
# 转换日期格式
df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
# 按日期升序排列
df = df.sort_values("trade_date").reset_index(drop=True)

# 重命名列，更清晰
df.rename(columns={
    "ts_code": "股票代码",
    "trade_date": "交易日期",
    "open": "开盘价",
    "high": "最高价",
    "low": "最低价",
    "close": "收盘价",
    "pre_close": "前收盘价",
    "change": "涨跌额",
    "pct_chg": "涨跌幅(%)",
    "vol": "成交量(手)",
    "amount": "成交额(千元)"
}, inplace=True)

print(f"数据范围: {df['交易日期'].min().strftime('%Y-%m-%d')} ~ {df['交易日期'].max().strftime('%Y-%m-%d')}")
print(f"共 {len(df)} 个交易日")
print(f"区间涨幅: {((df['收盘价'].iloc[-1] / df['收盘价'].iloc[0] - 1) * 100):.2f}%")
print(f"最高收盘价: {df['收盘价'].max():.2f} (出现在 {df.loc[df['收盘价'].idxmax(), '交易日期'].strftime('%Y-%m-%d')})")
print(f"最低收盘价: {df['收盘价'].min():.2f} (出现在 {df.loc[df['收盘价'].idxmin(), '交易日期'].strftime('%Y-%m-%d')})")

# ==================== 3. 保存 CSV ====================
csv_path = "贵州茅台_600519_日线数据.csv"
df.to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"\nCSV 已保存至: {csv_path}")

# ==================== 4. 绘制收盘价曲线 ====================
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(16, 8))

# 绘制收盘价折线
ax.plot(df["交易日期"], df["收盘价"], color="#c0392b", linewidth=1.5, alpha=0.9)

# 填充区域：收盘价与最低点之间
ax.fill_between(df["交易日期"], df["收盘价"].min() * 0.95, df["收盘价"],
                alpha=0.1, color="#c0392b")

# 标注关键点
ax.scatter(df["交易日期"].iloc[0], df["收盘价"].iloc[0],
           color="blue", s=80, zorder=5, label=f"起始: {df['收盘价'].iloc[0]:.2f}")
ax.scatter(df["交易日期"].iloc[-1], df["收盘价"].iloc[-1],
           color="green", s=80, zorder=5, label=f"最新: {df['收盘价'].iloc[-1]:.2f}")

max_idx = df["收盘价"].idxmax()
min_idx = df["收盘价"].idxmin()
ax.scatter(df["交易日期"].iloc[max_idx], df["收盘价"].iloc[max_idx],
           color="red", s=80, zorder=5, label=f"最高: {df['收盘价'].max():.2f}")
ax.scatter(df["交易日期"].iloc[min_idx], df["收盘价"].iloc[min_idx],
           color="orange", s=80, zorder=5, label=f"最低: {df['收盘价'].min():.2f}")

# 标题与标签
ax.set_title("贵州茅台 (600519.SH) 每日收盘价走势\n"
             f"区间: {df['交易日期'].iloc[0].strftime('%Y-%m-%d')} ~ {df['交易日期'].iloc[-1].strftime('%Y-%m-%d')}",
             fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("日期", fontsize=12)
ax.set_ylabel("收盘价 (元)", fontsize=12)
ax.legend(loc="upper left", fontsize=10, framealpha=0.9)
ax.grid(True, alpha=0.3, linestyle="--")

# 日期格式化
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=9)

# 添加区间涨跌幅文字
change_text = f"区间涨跌幅: {((df['收盘价'].iloc[-1] / df['收盘价'].iloc[0] - 1) * 100):.2f}%"
ax.text(0.98, 0.03, change_text, transform=ax.transAxes,
        fontsize=12, ha="right", va="bottom",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", alpha=0.8))

plt.tight_layout()

# 保存图表
chart_path = "贵州茅台_600519_收盘价曲线.png"
plt.savefig(chart_path, dpi=150, bbox_inches="tight")
print(f"图表已保存至: {chart_path}")

print("\n完成!")
