# -*- coding: utf-8 -*-
"""为 PDF 报告生成各指标独立图表"""
import matplotlib
matplotlib.use("Agg")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("贵州茅台_600519_日线数据.csv", encoding="utf-8-sig")
df["交易日期"] = pd.to_datetime(df["交易日期"])
df = df.sort_values("交易日期").reset_index(drop=True)
close = df["收盘价"]
high = df["最高价"]
low = df["最低价"]

# ---- 指标计算 ----
def calc_ema(s, w):
    return s.ewm(span=w, adjust=False).mean()

def calc_rsi(s, w=14):
    delta = s.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(w, min_periods=w).mean()
    avg_loss = loss.rolling(w, min_periods=w).mean()
    for i in range(w, len(avg_gain)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1]*(w-1) + gain.iloc[i]) / w
        avg_loss.iloc[i] = (avg_loss.iloc[i-1]*(w-1) + loss.iloc[i]) / w
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calc_kdj(d, n=9):
    low_n = d["最低价"].rolling(n).min()
    high_n = d["最高价"].rolling(n).max()
    rsv = (d["收盘价"] - low_n) / (high_n - low_n) * 100
    k = pd.Series(50.0, index=d.index)
    d_val = pd.Series(50.0, index=d.index)
    for i in range(n, len(d)):
        k.iloc[i] = 2/3 * k.iloc[i-1] + 1/3 * rsv.iloc[i]
        d_val.iloc[i] = 2/3 * d_val.iloc[i-1] + 1/3 * k.iloc[i]
    return k, d_val, 3*k - 2*d_val

df["RSI14"] = calc_rsi(close)
df["EMA12"] = calc_ema(close, 12)
df["EMA26"] = calc_ema(close, 26)
df["DIF"] = df["EMA12"] - df["EMA26"]
df["DEA"] = calc_ema(df["DIF"], 9)
df["MACD_hist"] = 2 * (df["DIF"] - df["DEA"])
df["BB_mid"] = close.rolling(20).mean()
df["BB_std"] = close.rolling(20).std()
df["BB_upper"] = df["BB_mid"] + 2 * df["BB_std"]
df["BB_lower"] = df["BB_mid"] - 2 * df["BB_std"]
df["K"], df["D"], df["J"] = calc_kdj(df, 9)

dp = df.iloc[26:].reset_index(drop=True)
dates = dp["交易日期"]
COLOR_UP = "#c0392b"
COLOR_DOWN = "#27ae60"
COLOR_BLUE = "#2980b9"
COLOR_PURPLE = "#8e44ad"
W, H = 12, 5.5

# ---- 图1: RSI ----
fig, ax = plt.subplots(figsize=(W, H))
ax.plot(dates, dp["RSI14"], color=COLOR_PURPLE, linewidth=1.6, label="RSI(14)")
ax.axhline(70, color=COLOR_UP, ls="--", lw=0.8, alpha=0.5)
ax.axhline(30, color=COLOR_DOWN, ls="--", lw=0.8, alpha=0.5)
ax.axhline(50, color="gray", ls=":", lw=0.5, alpha=0.4)
ax.fill_between(dates, 70, 100, alpha=0.06, color=COLOR_UP)
ax.fill_between(dates, 0, 30, alpha=0.06, color=COLOR_DOWN)
ax.set_ylim(0, 100)
ax.set_title("图 1: RSI(14) 相对强弱指标", fontsize=14, fontweight="bold")
ax.set_ylabel("RSI", fontsize=11)
ax.legend(loc="upper left")
ax.grid(True, alpha=0.2)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=9)
plt.tight_layout()
fig.savefig("chart_rsi.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close()

# ---- 图2: MACD ----
fig, ax = plt.subplots(figsize=(W, H))
colors = [COLOR_UP if v >= 0 else COLOR_DOWN for v in dp["MACD_hist"]]
ax.bar(dates, dp["MACD_hist"], color=colors, width=1.5, alpha=0.7, label="MACD 柱")
ax.plot(dates, dp["DIF"], color=COLOR_UP, lw=1.2, label="DIF (EMA12-EMA26)")
ax.plot(dates, dp["DEA"], color=COLOR_BLUE, lw=1.2, label="DEA (DIF的9日EMA)")
ax.axhline(0, color="black", lw=0.5)
ax.set_title("图 2: MACD(12,26,9)", fontsize=14, fontweight="bold")
ax.legend(loc="upper left", ncol=3, fontsize=9)
ax.grid(True, alpha=0.2)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=9)
plt.tight_layout()
fig.savefig("chart_macd.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close()

# ---- 图3: 布林带+收盘价 ----
fig, ax = plt.subplots(figsize=(W, H))
ax.plot(dates, dp["收盘价"], color="#2c3e50", lw=1.0, alpha=0.8, label="收盘价")
ax.plot(dates, dp["BB_upper"], color=COLOR_UP, lw=0.8, ls="--", alpha=0.6, label="上轨 (MA20+2σ)")
ax.plot(dates, dp["BB_mid"], color=COLOR_BLUE, lw=0.8, ls="--", alpha=0.6, label="中轨 (MA20)")
ax.plot(dates, dp["BB_lower"], color=COLOR_DOWN, lw=0.8, ls="--", alpha=0.6, label="下轨 (MA20-2σ)")
ax.fill_between(dates, dp["BB_upper"], dp["BB_lower"], alpha=0.06, color=COLOR_BLUE)
ax.set_title("图 3: 布林带 Bollinger Bands(20,2)", fontsize=14, fontweight="bold")
ax.set_ylabel("价格 (元)", fontsize=11)
ax.legend(loc="upper left", ncol=2, fontsize=8)
ax.grid(True, alpha=0.2)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=9)
plt.tight_layout()
fig.savefig("chart_bollinger.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close()

# ---- 图4: KDJ ----
fig, ax = plt.subplots(figsize=(W, H))
ax.plot(dates, dp["K"], color=COLOR_UP, lw=1.0, label="K 值")
ax.plot(dates, dp["D"], color=COLOR_BLUE, lw=1.0, label="D 值")
ax.plot(dates, dp["J"], color="#e67e22", lw=0.8, alpha=0.7, label="J 值 (3K-2D)")
ax.axhline(80, color=COLOR_UP, ls="--", lw=0.7, alpha=0.4)
ax.axhline(20, color=COLOR_DOWN, ls="--", lw=0.7, alpha=0.4)
ax.fill_between(dates, 80, 100, alpha=0.05, color=COLOR_UP)
ax.fill_between(dates, 0, 20, alpha=0.05, color=COLOR_DOWN)
ax.set_ylim(0, 100)
ax.set_title("图 4: KDJ 随机指标(9,3,3)", fontsize=14, fontweight="bold")
ax.legend(loc="upper left", ncol=3, fontsize=9)
ax.grid(True, alpha=0.2)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=9)
plt.tight_layout()
fig.savefig("chart_kdj.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close()

print("四个指标图表已生成: chart_rsi.png, chart_macd.png, chart_bollinger.png, chart_kdj.png")
