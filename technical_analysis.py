# -*- coding: utf-8 -*-
"""
贵州茅台 (600519.SH) 技术指标分析
==================================
包含：数据诊断、RSI、MACD、布林带、KDJ 的计算与可视化

技术指标详解（见代码末尾 docstring 及图表输出）
"""

import matplotlib
matplotlib.use("Agg")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings("ignore")

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

# ============================================================
# 第〇步：数据加载与诊断
# ============================================================
print("=" * 60)
print("  贵州茅台 (600519.SH) 技术分析")
print("=" * 60)

df = pd.read_csv("贵州茅台_600519_日线数据.csv", encoding="utf-8-sig")
df["交易日期"] = pd.to_datetime(df["交易日期"])
df = df.sort_values("交易日期").reset_index(drop=True)

print(f"\n[数据加载] 共 {len(df)} 条记录")
print(f"[时间跨度] {df['交易日期'].min().strftime('%Y-%m-%d')} ~ {df['交易日期'].max().strftime('%Y-%m-%d')}")

# ---- 缺失值诊断 ----
print("\n" + "-" * 40)
print("【数据诊断】缺失值检查")
print("-" * 40)
missing = df.isnull().sum()
missing_pct = (df.isnull().sum() / len(df) * 100)
missing_table = pd.DataFrame({"缺失数量": missing, "缺失比例(%)": missing_pct.round(2)})
print(missing_table[missing_table["缺失数量"] > 0] if missing.sum() > 0 else "  无缺失值 [OK]")
print(f"\n  数据类型:")
print(df.dtypes)

# ---- 描述性统计 ----
print("\n" + "-" * 40)
print("【数据诊断】描述性统计量")
print("-" * 40)
stats_cols = ["开盘价", "最高价", "最低价", "收盘价", "涨跌幅(%)", "成交量(手)"]
stats = df[stats_cols].describe().round(2)
print(stats)

# ---- 涨跌日分布 ----
up = (df["涨跌额"] > 0).sum()
down = (df["涨跌额"] < 0).sum()
flat = (df["涨跌额"] == 0).sum()
print(f"\n  涨跌分布: 上涨 {up}天 ({up/len(df)*100:.1f}%) | "
      f"下跌 {down}天 ({down/len(df)*100:.1f}%) | "
      f"平盘 {flat}天")

# ============================================================
# 第一步：技术指标计算
# ============================================================

close = df["收盘价"]
high = df["最高价"]
low = df["最低价"]
vol = df["成交量(手)"]

# --- 1. RSI (Relative Strength Index) ---
# RSI = 100 - [100 / (1 + RS)], RS = 平均涨幅 / 平均跌幅
# 通常使用 14 日周期
def calc_rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()
    # 使用 Wilder's smoothing: 递推平滑
    for i in range(window, len(avg_gain)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (window-1) + gain.iloc[i]) / window
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (window-1) + loss.iloc[i]) / window
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df["RSI14"] = calc_rsi(close, 14)
df["RSI6"] = calc_rsi(close, 6)   # 短期 RSI

# --- 2. MACD (Moving Average Convergence Divergence) ---
# EMA12, EMA26, DIF=EMA12-EMA26, DEA=EMA(DIF,9), MACD柱=2*(DIF-DEA)
def calc_ema(series, window):
    return series.ewm(span=window, adjust=False).mean()

df["EMA12"] = calc_ema(close, 12)
df["EMA26"] = calc_ema(close, 26)
df["DIF"] = df["EMA12"] - df["EMA26"]
df["DEA"] = calc_ema(df["DIF"], 9)
df["MACD_hist"] = 2 * (df["DIF"] - df["DEA"])

# --- 3. 布林带 (Bollinger Bands) ---
# 中轨 = MA20, 上轨 = MA20 + 2*σ, 下轨 = MA20 - 2*σ
window_bb = 20
df["BB_mid"] = close.rolling(window=window_bb).mean()
df["BB_std"] = close.rolling(window=window_bb).std()
df["BB_upper"] = df["BB_mid"] + 2 * df["BB_std"]
df["BB_lower"] = df["BB_mid"] - 2 * df["BB_std"]
df["BB_width"] = (df["BB_upper"] - df["BB_lower"]) / df["BB_mid"] * 100  # 带宽百分比

# --- 4. KDJ (Stochastic Oscillator) ---
# 未成熟随机值 RSV = (C - L9) / (H9 - L9) * 100
# K = 2/3 * K_prev + 1/3 * RSV
# D = 2/3 * D_prev + 1/3 * K
# J = 3*K - 2*D
def calc_kdj(df, n=9):
    low_n = df["最低价"].rolling(window=n).min()
    high_n = df["最高价"].rolling(window=n).max()
    rsv = (df["收盘价"] - low_n) / (high_n - low_n) * 100
    
    k = pd.Series(50.0, index=df.index)  # 初始值
    d = pd.Series(50.0, index=df.index)
    for i in range(n, len(df)):
        k.iloc[i] = 2/3 * k.iloc[i-1] + 1/3 * rsv.iloc[i]
        d.iloc[i] = 2/3 * d.iloc[i-1] + 1/3 * k.iloc[i]
    j = 3 * k - 2 * d
    return k, d, j

df["K"], df["D"], df["J"] = calc_kdj(df, 9)

# ---- 最新指标快照 ----
latest = df.iloc[-1]
print("\n" + "-" * 40)
print(f"【最新指标快照】{latest['交易日期'].strftime('%Y-%m-%d')}")
print("-" * 40)
print(f"  收盘价:       RMB {latest['收盘价']:.2f}")
print(f"  RSI(14):       {latest['RSI14']:.1f}  (超卖<30, 中性30-70, 超买>70)")
print(f"  MACD DIF:      {latest['DIF']:.2f}")
print(f"  MACD DEA:      {latest['DEA']:.2f}")
print(f"  MACD 柱:       {latest['MACD_hist']:.2f}  ({'多头' if latest['MACD_hist']>0 else '空头'})")
print(f"  布林上轨:      RMB {latest['BB_upper']:.2f}")
print(f"  布林中轨:      RMB {latest['BB_mid']:.2f}")
print(f"  布林下轨:      RMB {latest['BB_lower']:.2f}")
print(f"  KDJ K/D/J:     {latest['K']:.1f} / {latest['D']:.1f} / {latest['J']:.1f}")

# ============================================================
# 第二步：可视化
# ============================================================

# 只取有指标数据的部分（前 26 天 NaN）
df_plot = df.iloc[26:].reset_index(drop=True)
dates = df_plot["交易日期"]

fig = plt.figure(figsize=(18, 22))
gs = GridSpec(5, 1, figure=fig, hspace=0.35,
              height_ratios=[2.5, 1.0, 1.0, 1.0, 1.0])

# ---- 子图 1: K线 + 布林带 + 均线 ----
ax1 = fig.add_subplot(gs[0])
ax1.plot(dates, df_plot["收盘价"], color="#2c3e50", linewidth=0.8, alpha=0.8, label="收盘价")
ax1.plot(dates, df_plot["BB_upper"], color="#e74c3c", linewidth=0.8, linestyle="--", alpha=0.6, label="布林上轨")
ax1.plot(dates, df_plot["BB_mid"], color="#3498db", linewidth=0.8, linestyle="--", alpha=0.6, label="布林中轨(MA20)")
ax1.plot(dates, df_plot["BB_lower"], color="#27ae60", linewidth=0.8, linestyle="--", alpha=0.6, label="布林下轨")
ax1.fill_between(dates, df_plot["BB_upper"], df_plot["BB_lower"], alpha=0.06, color="#3498db")
ax1.set_title("图 1: 贵州茅台(600519) 收盘价 & 布林带 (Bollinger Bands, 20,2)", fontsize=14, fontweight="bold")
ax1.set_ylabel("价格 (元)", fontsize=10)
ax1.legend(loc="upper left", fontsize=8, ncol=2)
ax1.grid(True, alpha=0.2)
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=8)

# 标注布林带收窄区域（带宽<8%的时期）
narrow = df_plot[df_plot["BB_width"] < 8]
if len(narrow) > 0:
    ax1.scatter(narrow["交易日期"], narrow["收盘价"], color="orange", s=10, alpha=0.5, zorder=5)

# ---- 子图 2: MACD ----
ax2 = fig.add_subplot(gs[1], sharex=ax1)
colors_macd = ["#c0392b" if v >= 0 else "#27ae60" for v in df_plot["MACD_hist"]]
ax2.bar(dates, df_plot["MACD_hist"], color=colors_macd, width=1.5, alpha=0.7, label="MACD柱")
ax2.plot(dates, df_plot["DIF"], color="#e74c3c", linewidth=1.0, label="DIF (快线)")
ax2.plot(dates, df_plot["DEA"], color="#3498db", linewidth=1.0, label="DEA (慢线)")
ax2.axhline(y=0, color="black", linewidth=0.5, linestyle="-")
ax2.set_title("图 2: MACD (12, 26, 9)", fontsize=13, fontweight="bold")
ax2.set_ylabel("MACD", fontsize=10)
ax2.legend(loc="upper left", fontsize=8, ncol=3)
ax2.grid(True, alpha=0.2)
plt.setp(ax2.xaxis.get_majorticklabels(), fontsize=8)

# ---- 子图 3: RSI ----
ax3 = fig.add_subplot(gs[2], sharex=ax1)
ax3.plot(dates, df_plot["RSI14"], color="#8e44ad", linewidth=1.2, label="RSI(14)")
ax3.plot(dates, df_plot["RSI6"], color="#e67e22", linewidth=0.8, alpha=0.6, label="RSI(6)")
ax3.axhline(y=70, color="#c0392b", linewidth=0.8, linestyle="--", alpha=0.5)
ax3.axhline(y=30, color="#27ae60", linewidth=0.8, linestyle="--", alpha=0.5)
ax3.axhline(y=50, color="gray", linewidth=0.5, linestyle=":", alpha=0.5)
ax3.fill_between(dates, 70, 100, alpha=0.05, color="#c0392b")
ax3.fill_between(dates, 0, 30, alpha=0.05, color="#27ae60")
ax3.set_ylim(0, 100)
ax3.set_title("图 3: RSI 相对强弱指标 (14日 & 6日)", fontsize=13, fontweight="bold")
ax3.set_ylabel("RSI", fontsize=10)
ax3.legend(loc="upper left", fontsize=8)
ax3.grid(True, alpha=0.2)
plt.setp(ax3.xaxis.get_majorticklabels(), fontsize=8)

# ---- 子图 4: KDJ ----
ax4 = fig.add_subplot(gs[3], sharex=ax1)
ax4.plot(dates, df_plot["K"], color="#c0392b", linewidth=1.0, label="K 值")
ax4.plot(dates, df_plot["D"], color="#3498db", linewidth=1.0, label="D 值")
ax4.plot(dates, df_plot["J"], color="#e67e22", linewidth=0.8, alpha=0.7, label="J 值")
ax4.axhline(y=80, color="#c0392b", linewidth=0.8, linestyle="--", alpha=0.4)
ax4.axhline(y=20, color="#27ae60", linewidth=0.8, linestyle="--", alpha=0.4)
ax4.fill_between(dates, 80, 100, alpha=0.05, color="#c0392b")
ax4.fill_between(dates, 0, 20, alpha=0.05, color="#27ae60")
ax4.set_ylim(0, 100)
ax4.set_title("图 4: KDJ 随机指标 (9, 3, 3)", fontsize=13, fontweight="bold")
ax4.set_ylabel("KDJ", fontsize=10)
ax4.legend(loc="upper left", fontsize=8)
ax4.grid(True, alpha=0.2)
plt.setp(ax4.xaxis.get_majorticklabels(), fontsize=8)

# ---- 子图 5: 成交量 ----
ax5 = fig.add_subplot(gs[4], sharex=ax1)
colors_vol = ["#c0392b" if df_plot["涨跌额"].iloc[i] >= 0 else "#27ae60" for i in range(len(df_plot))]
ax5.bar(dates, df_plot["成交量(手)"] / 10000, color=colors_vol, width=1.5, alpha=0.7)
ax5.set_title("图 5: 成交量 (万手)", fontsize=13, fontweight="bold")
ax5.set_ylabel("成交量 (万手)", fontsize=10)
ax5.grid(True, alpha=0.2)
ax5.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax5.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=8)

plt.tight_layout()
chart_path = "贵州茅台_600519_技术指标全景图.png"
plt.savefig(chart_path, dpi=150, bbox_inches="tight", facecolor="white")
print(f"\n图表已保存: {chart_path}")

# ============================================================
# 第三步：输出指标分析概要
# ============================================================
print("\n" + "=" * 60)
print("  指标分析概要")
print("=" * 60)

# RSI 趋势
latest_rsi = latest["RSI14"]
rsi_status = "超卖区域 (<30)，短期存在技术性反弹需求" if latest_rsi < 30 else \
             "超买区域 (>70)，短期回调风险较大" if latest_rsi > 70 else \
             "中性区间 (30-70)，多空力量相对均衡"
print(f"\n【RSI 解读】当前 RSI(14)={latest_rsi:.1f}，处于{rsi_status}。")

# MACD 趋势
macd_status = "多头市场（DIF上穿DEA，MACD柱为正）" if latest["DIF"] > latest["DEA"] else \
              "空头市场（DIF下穿DEA，MACD柱为负）"
print(f"【MACD 解读】当前 DIF={latest['DIF']:.2f}, DEA={latest['DEA']:.2f}，{macd_status}。")

# 布林带
bb_pos = (latest["收盘价"] - latest["BB_lower"]) / (latest["BB_upper"] - latest["BB_lower"]) * 100
print(f"【布林带解读】收盘价位于布林带 {bb_pos:.0f}% 位置，"
      f"带宽={latest['BB_width']:.1f}%。"
      f"{'布林带收窄，可能预示变盘。' if latest['BB_width'] < 8 else ''}")

# KDJ
kdj_status = "超买区域 (K>80)，短期过热" if latest["K"] > 80 else \
             "超卖区域 (K<20)，短期超跌" if latest["K"] < 20 else \
             "中性区间"
print(f"【KDJ 解读】K={latest['K']:.1f}, D={latest['D']:.1f}, J={latest['J']:.1f}，{kdj_status}。")

print("\n完成！")