#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
海龟交易法则 (Turtle Trading System) — 贵州茅台 (600519) 完整实现

核心要素：
  System 1: 20日高点突破买入 / 10日低点突破卖出
  System 2: 55日高点突破买入 / 20日低点突破卖出
  ATR(20): 头寸规模与止损计算
  止损: 2×ATR 硬止损
  头寸: 风险1% + N(ATR) 单位计算
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150

OUTPUT_DIR = 'E:/EN_study_tool/BA_task'


# ============================================================
# 1. 数据加载
# ============================================================
def load_data(filepath):
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    df['交易日期'] = pd.to_datetime(df['交易日期'])
    df = df.sort_values('交易日期').reset_index(drop=True)
    return df


# ============================================================
# 2. 指标计算
# ============================================================
def calc_atr(df, period=20):
    """计算平均真实波幅 (Average True Range)"""
    high, low, close = df['最高价'], df['最低价'], df['收盘价']
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = abs(high - prev_close)
    tr3 = abs(low - prev_close)
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    return tr, atr


def calc_donchian(df, period):
    """计算 Donchian 通道：N日最高价和最低价"""
    upper = df['最高价'].rolling(period).max()
    lower = df['最低价'].rolling(period).min()
    middle = df['收盘价'].rolling(period).mean()
    return upper, middle, lower


def compute_signals(df, entry_period=20, exit_period=10):
    """
    海龟 System 1 交易信号：
      - 入场：价格突破 entry_period 日最高价 → 买入(1)
      - 离场：价格突破 exit_period 日最低价 → 卖出(-1)
    信号次日开盘价执行
    """
    upper, _, lower = calc_donchian(df, entry_period)
    _, _, exit_lower = calc_donchian(df, exit_period)

    df = df.copy()
    df['entry_upper'] = upper.shift(1)   # 上一日的通道上轨
    df['exit_lower'] = exit_lower.shift(1)  # 上一日离场通道下轨

    df['signal'] = 0
    # 买入：今日开盘价 > 昨日通道上轨（价格突破）
    df.loc[df['开盘价'] > df['entry_upper'], 'signal'] = 1
    # 卖出：今日开盘价 < 离场通道下轨
    df.loc[df['开盘价'] < df['exit_lower'], 'signal'] = -1

    return df, upper, lower


# ============================================================
# 3. 头寸规模计算（海龟法则核心）
# ============================================================
def compute_position_size(capital, atr_value, risk_percent=0.01, price=0):
    """
    海龟头寸管理：
      N = ATR(20)
      单位风险 = 账户资金 × 1%
      头寸数量 = 单位风险 / N
    """
    if atr_value <= 0 or np.isnan(atr_value):
        return 0
    unit_risk = capital * risk_percent
    units = int(unit_risk / atr_value / 100) * 100  # 取整百股
    return max(100, units) if units > 0 else 0


# ============================================================
# 4. 模拟交易回测
# ============================================================
def backtest(df, initial_capital=1_000_000, entry_period=20, exit_period=10,
             atr_period=20, stop_mult=2.0, commission=0.0003):
    """
    海龟策略回测：
    - System 1: entry_period 日突破入场 / exit_period 日突破离场
    - ATR 头寸管理 + 2×ATR 硬止损
    - 允许加仓（每 0.5 ATR 加仓一次，最多 4 次）
    """
    tr, atr = calc_atr(df, atr_period)
    df_sig, upper, lower = compute_signals(df, entry_period, exit_period)

    capital = initial_capital
    positions = []  # [(entry_price, shares, entry_date, add_count)]
    trades = []
    daily_values = []

    for i in range(len(df_sig)):
        date = df_sig.loc[i, '交易日期']
        price_open = df_sig.loc[i, '开盘价']
        price_close = df_sig.loc[i, '收盘价']
        price_low = df_sig.loc[i, '最低价']
        price_high = df_sig.loc[i, '最高价']
        sig = df_sig.loc[i, 'signal']
        atr_val = atr.iloc[i]

        # —— 检查止损 ——
        to_remove = []
        for j, pos in enumerate(positions):
            entry_p, sh, entry_d, add_cnt = pos
            stop_price = entry_p - stop_mult * atr_val
            if price_low <= stop_price and not pd.isna(atr_val):
                # 止损出场
                exit_p = min(price_open, stop_price)
                proceeds = sh * exit_p * (1 - commission)
                capital += proceeds
                trades.append({
                    '日期': date, '类型': '止损离场', '价格': round(exit_p, 2),
                    '数量': sh, '金额': round(proceeds, 0),
                    '入场日期': entry_d.strftime('%Y-%m-%d'),
                    '入场价': round(entry_p, 2)
                })
                to_remove.append(j)
        for j in reversed(to_remove):
            positions.pop(j)

        # —— 离场信号 ——
        if sig == -1 and len(positions) > 0:
            to_remove = []
            for j, pos in enumerate(positions):
                entry_p, sh, entry_d, add_cnt = pos
                proceeds = sh * price_open * (1 - commission)
                capital += proceeds
                trades.append({
                    '日期': date, '类型': '突破离场', '价格': round(float(price_open), 2),
                    '数量': sh, '金额': round(proceeds, 0),
                    '入场日期': entry_d.strftime('%Y-%m-%d'),
                    '入场价': round(entry_p, 2)
                })
                to_remove.append(j)
            for j in reversed(to_remove):
                positions.pop(j)

        # —— 入场信号 ——
        if sig == 1 and not pd.isna(atr_val) and atr_val > 0:
            shares = compute_position_size(capital, atr_val, risk_percent=0.01,
                                           price=price_open)
            if shares > 0 and shares * price_open <= capital:
                cost = shares * price_open * (1 + commission)
                capital -= cost
                positions.append((price_open, shares, date, 1))
                trades.append({
                    '日期': date, '类型': '突破入场', '价格': round(float(price_open), 2),
                    '数量': shares, '金额': round(cost, 0),
                    '入场日期': date.strftime('%Y-%m-%d'),
                    '入场价': round(float(price_open), 2)
                })

        # 每日总资产
        position_value = sum(p[1] * price_close for p in positions)
        total = capital + position_value
        daily_values.append({'日期': date, '总资产': total})

    # 期末清仓
    if positions:
        final_price = df_sig.iloc[-1]['收盘价']
        for entry_p, sh, entry_d, add_cnt in positions:
            capital += sh * final_price * (1 - commission)
            trades.append({
                '日期': df_sig.iloc[-1]['交易日期'],
                '类型': '期末清仓', '价格': round(float(final_price), 2),
                '数量': sh, '金额': round(sh * final_price * (1 - commission), 0),
                '入场日期': entry_d.strftime('%Y-%m-%d'),
                '入场价': round(entry_p, 2)
            })

    equity_df = pd.DataFrame(daily_values)
    equity_df['日收益率'] = equity_df['总资产'].pct_change()
    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()

    return equity_df, trades_df, capital, df_sig


# ============================================================
# 5. 绩效指标
# ============================================================
def compute_metrics(equity_df, risk_free_rate=0.03):
    total = equity_df['总资产'].values
    n = len(total)
    trading_days = 252

    cumulative_return = (total[-1] / total[0] - 1) * 100
    years = n / trading_days
    annualized_return = (total[-1] / total[0]) ** (1 / years) - 1 if years > 0 else 0

    peak = np.maximum.accumulate(total)
    drawdown = (total - peak) / peak
    max_drawdown = drawdown.min() * 100

    daily_returns = equity_df['日收益率'].dropna()
    excess = daily_returns - risk_free_rate / trading_days
    sharpe = np.sqrt(trading_days) * excess.mean() / excess.std() if excess.std() > 0 else 0

    win_rate = (daily_returns > 0).sum() / len(daily_returns) * 100 if len(daily_returns) > 0 else 0

    return {
        '初始资金 (元)': total[0],
        '最终资金 (元)': round(total[-1], 0),
        '累计回报 (%)': round(cumulative_return, 2),
        '年化收益率 (%)': round(annualized_return * 100, 2),
        '最大回撤 (%)': round(max_drawdown, 2),
        '夏普比率': round(sharpe, 2),
        '日胜率 (%)': round(win_rate, 2),
        '交易天数': n,
    }


# ============================================================
# 6. 可视化
# ============================================================
def plot_turtle_strategy(df, upper, lower, entry_period, exit_period, trades_df, stock_name, save_path):
    """海龟策略主图：K线 + Donchian通道 + 买卖点"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10),
                                    gridspec_kw={'height_ratios': [3, 1]})

    # K线简化：用收盘价折线
    ax1.plot(df['交易日期'], df['收盘价'], color='#2c3e50', linewidth=1.0,
             label='收盘价', alpha=0.85)
    ax1.plot(df['交易日期'], upper, color='#e74c3c', linewidth=1.0,
             linestyle='--', alpha=0.7, label=f'{entry_period}日通道上轨(入场)')
    ax1.plot(df['交易日期'], lower, color='#27ae60', linewidth=1.0,
             linestyle='--', alpha=0.7, label=f'{exit_period}日通道下轨(离场)')

    # 标记交易点
    if not trades_df.empty:
        buys = trades_df[trades_df['类型'] == '突破入场']
        sells = trades_df[trades_df['类型'].isin(['突破离场', '止损离场'])]
        if len(buys) > 0:
            ax1.scatter(buys['日期'], buys['价格'], color='red', marker='^', s=80,
                        zorder=5, edgecolors='darkred', linewidths=0.5,
                        label=f'入场 ({len(buys)}次)')
        if len(sells) > 0:
            ax1.scatter(sells['日期'], sells['价格'], color='green', marker='v', s=80,
                        zorder=5, edgecolors='darkgreen', linewidths=0.5,
                        label=f'离场 ({len(sells)}次)')

    ax1.set_title(f'{stock_name} — 海龟交易法则 ({entry_period}/{exit_period}日)',
                  fontsize=14, fontweight='bold', pad=12)
    ax1.set_ylabel('价格 (元)', fontsize=11)
    ax1.legend(loc='upper left', fontsize=9, framealpha=0.9, ncol=2)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, ha='right')

    # 持仓区间
    if not trades_df.empty:
        buy_dates = trades_df[trades_df['类型'] == '突破入场']['日期'].tolist()
        sell_dates = trades_df[trades_df['类型'].isin(['突破离场', '止损离场'])]['日期'].tolist()
        for bd in buy_dates:
            idx_b = df[df['交易日期'] == bd].index
            if len(idx_b) == 0: continue
            idx_b = idx_b[0]
            later_sells = [sd for sd in sell_dates if sd > bd]
            if later_sells:
                sd = min(later_sells)
                idx_s = df[df['交易日期'] == sd].index[0]
                ax2.axvspan(idx_b, idx_s, color='#e74c3c', alpha=0.08)

    ax2.set_title('持仓区间（红色底色 = 持仓期间）', fontsize=11, pad=8)
    ax2.set_xlabel('日期', fontsize=11)
    ax2.set_yticks([])
    ax2.grid(True, alpha=0.2, linestyle='--')

    plt.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  [图表] {save_path}")


def plot_equity_drawdown(equity_df, df, metrics, stock_name, save_path):
    """净值曲线 + 回撤"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                    gridspec_kw={'height_ratios': [2.5, 1]})

    nav = equity_df['总资产'] / equity_df['总资产'].iloc[0]
    bench = df['收盘价'] / df['收盘价'].iloc[0]

    ax1.plot(equity_df['日期'], nav, color='#e74c3c', linewidth=1.5, label='海龟策略净值')
    ax1.plot(df['交易日期'], bench, color='#3498db', linewidth=1.0,
             alpha=0.7, linestyle='--', label='买入持有净值')
    ax1.axhline(y=1.0, color='gray', linewidth=0.5, linestyle=':', alpha=0.5)
    ax1.set_title(f'{stock_name} — 策略净值 vs 买入持有', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.set_ylabel('累计净值', fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')

    total = equity_df['总资产'].values
    peak = np.maximum.accumulate(total)
    dd = (total - peak) / peak * 100
    ax2.fill_between(range(len(dd)), dd, 0, color='#e74c3c', alpha=0.35)
    ax2.plot(range(len(dd)), dd, color='#c0392b', linewidth=0.8)
    ax2.set_title('回撤曲线', fontsize=11)
    ax2.set_xlabel('交易日', fontsize=11)
    ax2.set_ylabel('回撤 (%)', fontsize=11)
    ax2.grid(True, alpha=0.3, linestyle='--')

    text = (f"累计回报: {metrics['累计回报 (%)']}%  |  "
            f"年化: {metrics['年化收益率 (%)']}%  |  "
            f"MDD: {metrics['最大回撤 (%)']}%  |  "
            f"Sharpe: {metrics['夏普比率']}")
    fig.text(0.5, 0.01, text, ha='center', fontsize=9,
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#ecf0f1', alpha=0.8))

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  [图表] {save_path}")


def plot_parameter_heatmap(results_df, save_path):
    """参数对比热力图"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    items = [
        ('累计回报 (%)', '累计回报 (%)', 'RdYlGn'),
        ('最大回撤 (%)', '最大回撤 (%)', 'RdYlGn_r'),
        ('夏普比率', '夏普比率', 'RdYlGn'),
    ]
    for ax, (col, title, cmap) in zip(axes, items):
        pivot = results_df.pivot_table(values=col, index='入场周期', columns='离场周期')
        im = ax.imshow(pivot.values, cmap=cmap, aspect='auto', origin='lower')
        ax.set_xticks(range(len(pivot.columns))); ax.set_xticklabels(pivot.columns)
        ax.set_yticks(range(len(pivot.index))); ax.set_yticklabels(pivot.index)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('离场周期'); ax.set_ylabel('入场周期')
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                v = pivot.iloc[i, j]
                if not np.isnan(v):
                    ax.text(j, i, f'{v:.1f}', ha='center', va='center', fontsize=8, fontweight='bold')
        plt.colorbar(im, ax=ax, shrink=0.8)

    plt.suptitle('海龟策略参数网格搜索', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  [图表] {save_path}")


# ============================================================
# 7. 参数实验
# ============================================================
def run_param_experiment(df, param_grid):
    results = []
    for entry_p, exit_p in param_grid:
        eq, tr, final_cap, _ = backtest(df, entry_period=entry_p, exit_period=exit_p)
        if not eq.empty:
            m = compute_metrics(eq)
            m['入场周期'] = entry_p
            m['离场周期'] = exit_p
            m['交易次数'] = len(tr)
            results.append(m)
    return pd.DataFrame(results)


# ============================================================
# 8. 主流程
# ============================================================
def main():
    print("=" * 60)
    print("  海龟交易策略 — 贵州茅台 (600519)")
    print("=" * 60)

    df = load_data(f'{OUTPUT_DIR}/贵州茅台_600519_日线数据.csv')
    print(f"\n[数据] {len(df)} 交易日, "
          f"{df['交易日期'].iloc[0].strftime('%Y-%m-%d')} ~ "
          f"{df['交易日期'].iloc[-1].strftime('%Y-%m-%d')}")

    # ——— 默认参数 System 1 ———
    ENTRY, EXIT = 20, 10
    equity, trades_df, final_cap, df_sig = backtest(
        df, entry_period=ENTRY, exit_period=EXIT)
    metrics = compute_metrics(equity)

    print(f"\n--- 绩效 (System 1: {ENTRY}/{EXIT}日) ---")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
    print(f"  交易记录: {len(trades_df)} 笔")
    if not trades_df.empty:
        for _, t in trades_df.iterrows():
            print(f"    {t['日期'].strftime('%Y-%m-%d')}  {t['类型']:6s}  "
                  f"@{t['价格']:.1f}  ×{t['数量']}股")

    # ——— 图表 ———
    upper, _, lower = calc_donchian(df_sig, ENTRY)
    plot_turtle_strategy(df_sig, upper, lower, ENTRY, EXIT, trades_df,
                         '贵州茅台 (600519)',
                         f'{OUTPUT_DIR}/chart_turtle_strategy.png')
    plot_equity_drawdown(equity, df, metrics,
                         '贵州茅台 (600519)',
                         f'{OUTPUT_DIR}/chart_turtle_equity.png')

    # ——— 参数对比 ———
    print("\n" + "=" * 60)
    print("  参数网格搜索")
    print("=" * 60)
    param_grid = [(10, 5), (20, 10), (20, 15), (30, 15),
                  (55, 20), (30, 10), (15, 10), (25, 10)]
    param_results = run_param_experiment(df, param_grid)
    print(param_results[['入场周期','离场周期','累计回报 (%)','最大回撤 (%)','夏普比率','交易次数']].to_string(index=False))

    plot_parameter_heatmap(param_results,
                           f'{OUTPUT_DIR}/chart_turtle_heatmap.png')
    param_results.to_csv(f'{OUTPUT_DIR}/turtle_param_results.csv',
                         index=False, encoding='utf-8-sig')

    # ——— 对比买入持有 ———
    bh_return = (df['收盘价'].iloc[-1] / df['收盘价'].iloc[0] - 1) * 100
    print(f"\n--- 策略 vs 买入持有 ---")
    print(f"  买入持有: {bh_return:.2f}%")
    print(f"  海龟策略: {metrics['累计回报 (%)']}%")

    # ——— 最优参数 ———
    best = param_results.loc[param_results['累计回报 (%)'].idxmax()]
    print(f"\n[最优] 入场={int(best['入场周期'])}, 离场={int(best['离场周期'])}, "
          f"回报={best['累计回报 (%)']}%")

    eq_best, tr_best, _, df_sig_best = backtest(
        df, entry_period=int(best['入场周期']), exit_period=int(best['离场周期']))
    m_best = compute_metrics(eq_best)
    upper_b, _, lower_b = calc_donchian(df_sig_best, int(best['入场周期']))
    plot_turtle_strategy(df_sig_best, upper_b, lower_b,
                         int(best['入场周期']), int(best['离场周期']), tr_best,
                         '贵州茅台 — 最优参数',
                         f'{OUTPUT_DIR}/chart_turtle_best.png')
    plot_equity_drawdown(eq_best, df, m_best,
                         '贵州茅台 — 最优参数',
                         f'{OUTPUT_DIR}/chart_turtle_best_equity.png')

    print("\n✅ 全部完成!")
    return df, metrics, param_results, trades_df, equity


if __name__ == '__main__':
    df, metrics, param_results, trades_df, equity = main()
