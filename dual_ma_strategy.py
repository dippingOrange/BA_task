#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
双均线交叉策略 —— 贵州茅台 (600519) 完整实现
包含：均线计算、交易信号、可视化、回测、绩效指标
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 全局绘图风格
# ============================================================
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150


# ============================================================
# 1. 加载数据
# ============================================================
def load_data(filepath):
    """加载CSV股价数据，解析日期并排序"""
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    df['交易日期'] = pd.to_datetime(df['交易日期'])
    df = df.sort_values('交易日期').reset_index(drop=True)
    return df


# ============================================================
# 2. 计算均线 & 交易信号
# ============================================================
def compute_ma_signals(df, short_window=5, long_window=15, price_col='收盘价'):
    """
    计算短期/长期均线及金叉死叉信号
    金叉（Golden Cross）：短均线上穿长均线 → 买入信号 (1)
    死叉（Death Cross）  ：短均线下穿长均线 → 卖出信号 (-1)
    """
    df = df.copy()
    df['MA_short'] = df[price_col].rolling(window=short_window).mean()
    df['MA_long'] = df[price_col].rolling(window=long_window).mean()

    # 计算交叉信号
    df['diff'] = df['MA_short'] - df['MA_long']
    df['signal'] = 0
    # 金叉：前一天 diff<=0, 当天 diff>0
    df.loc[(df['diff'] > 0) & (df['diff'].shift(1) <= 0), 'signal'] = 1
    # 死叉：前一天 diff>=0, 当天 diff<0
    df.loc[(df['diff'] < 0) & (df['diff'].shift(1) >= 0), 'signal'] = -1

    return df


# ============================================================
# 3. 模拟交易回测
# ============================================================
def backtest(df, initial_capital=1_000_000, commission=0.0003):
    """
    双均线策略回测
    - 初始资金 100 万元
    - 佣金 万分之三（双边）
    - 信号出现次日以开盘价成交
    - 每次全仓买入/卖出
    """
    capital = initial_capital
    shares = 0
    trades = []
    daily_values = []

    for i in range(len(df)):
        date = df.loc[i, '交易日期']
        price = df.loc[i, '开盘价']  # 按次日开盘价成交
        sig = df.loc[i, 'signal']

        # 买入信号（金叉）
        if sig == 1 and shares == 0:
            shares = int(capital * (1 - commission) / price)
            cost = shares * price * (1 + commission)
            capital -= cost
            trades.append({'日期': date, '类型': '买入', '价格': price,
                           '数量': shares, '金额': cost, '仓位价值': shares * price})
        # 卖出信号（死叉）
        elif sig == -1 and shares > 0:
            proceeds = shares * price * (1 - commission)
            capital += proceeds
            trades.append({'日期': date, '类型': '卖出', '价格': price,
                           '数量': shares, '金额': proceeds, '仓位价值': 0})
            shares = 0

        # 每日总资产 = 现金 + 持仓市值
        total = capital + shares * df.loc[i, '收盘价']
        daily_values.append({'日期': date, '总资产': total})

    # 持仓到期末
    if shares > 0:
        final_price = df.iloc[-1]['收盘价']
        capital += shares * final_price * (1 - commission)

    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
    equity_df = pd.DataFrame(daily_values)
    equity_df['日收益率'] = equity_df['总资产'].pct_change()

    return equity_df, trades_df, capital


# ============================================================
# 4. 绩效指标计算
# ============================================================
def compute_metrics(equity_df, risk_free_rate=0.03):
    """
    计算：
    - 累计回报 (Cumulative Return)
    - 年化收益率 (Annualized Return)
    - 最大回撤 (Maximum Drawdown, MDD)
    - 夏普比率 (Sharpe Ratio)
    - 胜率 (Win Rate)
    - 交易次数
    """
    total = equity_df['总资产'].values
    n = len(total)
    trading_days = 252

    # 累计回报
    cumulative_return = (total[-1] / total[0] - 1) * 100

    # 年化收益率
    years = n / trading_days
    annualized_return = (total[-1] / total[0]) ** (1 / years) - 1

    # 最大回撤
    peak = np.maximum.accumulate(total)
    drawdown = (total - peak) / peak
    max_drawdown = drawdown.min() * 100  # 负值，越小回撤越大

    # 夏普比率
    daily_returns = equity_df['日收益率'].dropna()
    excess = daily_returns - risk_free_rate / trading_days
    sharpe = np.sqrt(trading_days) * excess.mean() / excess.std() if excess.std() > 0 else 0

    # 日胜率
    win_rate = (daily_returns > 0).sum() / len(daily_returns) * 100 if len(daily_returns) > 0 else 0

    metrics = {
        '初始资金 (元)': equity_df['总资产'].iloc[0],
        '最终资金 (元)': total[-1],
        '累计回报 (%)': round(cumulative_return, 2),
        '年化收益率 (%)': round(annualized_return * 100, 2),
        '最大回撤 (%)': round(max_drawdown, 2),
        '夏普比率': round(sharpe, 2),
        '日胜率 (%)': round(win_rate, 2),
        '交易天数': n,
    }
    return metrics


# ============================================================
# 5. 可视化（主图）
# ============================================================
def plot_strategy(df, trades_df, short_window, long_window, stock_name, save_path):
    """绘制股价+均线+买卖信号的综合图表"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10),
                                    gridspec_kw={'height_ratios': [3, 1]})

    # ---- 上图：股价与均线 ----
    ax1.plot(df['交易日期'], df['收盘价'], color='#2c3e50', linewidth=1.2,
             label='收盘价', alpha=0.85)
    ax1.plot(df['交易日期'], df['MA_short'], color='#e74c3c', linewidth=1.0,
             label=f'{short_window}日均线 (短)', alpha=0.9)
    ax1.plot(df['交易日期'], df['MA_long'], color='#2980b9', linewidth=1.0,
             label=f'{long_window}日均线 (长)', alpha=0.9)

    # 标记买卖点
    buy_signals = df[df['signal'] == 1]
    sell_signals = df[df['signal'] == -1]

    ax1.scatter(buy_signals['交易日期'], buy_signals['收盘价'],
                color='red', marker='^', s=80, zorder=5,
                edgecolors='darkred', linewidths=0.5,
                label=f'金叉买入 ({len(buy_signals)}次)')
    ax1.scatter(sell_signals['交易日期'], sell_signals['收盘价'],
                color='green', marker='v', s=80, zorder=5,
                edgecolors='darkgreen', linewidths=0.5,
                label=f'死叉卖出 ({len(sell_signals)}次)')

    ax1.set_title(f'{stock_name} — 双均线策略 ({short_window}/{long_window}日)',
                  fontsize=14, fontweight='bold', pad=12)
    ax1.set_ylabel('价格 (元)', fontsize=11)
    ax1.legend(loc='upper left', fontsize=9, framealpha=0.9, ncol=2)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, ha='right')

    # ---- 下图：每日资产曲线 ----
    if not trades_df.empty:
        # 绘制累计净值
        ax2.plot(df['交易日期'],
                 df['收盘价'] / df['收盘价'].iloc[0],
                 color='#95a5a6', linewidth=0.8, alpha=0.7, label='买入持有净值')

    ax2.fill_between(range(len(df)),
                     0, 1,
                     color='#e74c3c', alpha=0.08, label='_nolegend_')

    # 标注交易区间
    start_idx = None
    for i in range(len(df)):
        sig = df.loc[i, 'signal']
        if sig == 1 and start_idx is None:
            start_idx = i
        elif sig == -1 and start_idx is not None:
            ax2.axvspan(start_idx, i, color='#e74c3c', alpha=0.08)
            start_idx = None
    if start_idx is not None:
        ax2.axvspan(start_idx, len(df) - 1, color='#e74c3c', alpha=0.08)

    ax2.set_title('交易信号区间（红色底色 = 持仓期间）', fontsize=11, pad=8)
    ax2.set_xlabel('日期', fontsize=11)
    ax2.set_ylabel('信号', fontsize=11)
    ax2.set_yticks([])
    ax2.grid(True, alpha=0.2, linestyle='--')

    plt.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  [图表] 已保存 → {save_path}")


# ============================================================
# 6. 绩效对比图
# ============================================================
def plot_equity_curve(equity_df, df, metrics, stock_name, save_path):
    """绘制资金曲线与回撤"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                    gridspec_kw={'height_ratios': [2.5, 1]})

    # 累计净值
    nav = equity_df['总资产'] / equity_df['总资产'].iloc[0]
    bench_nav = df['收盘价'] / df['收盘价'].iloc[0]

    ax1.plot(equity_df['日期'], nav, color='#e74c3c', linewidth=1.5, label='策略净值')
    ax1.plot(df['交易日期'], bench_nav, color='#3498db', linewidth=1.0,
             alpha=0.7, linestyle='--', label='买入持有净值')
    ax1.axhline(y=1.0, color='gray', linewidth=0.5, linestyle=':', alpha=0.5)
    ax1.set_title(f'{stock_name} — 策略净值 vs 买入持有',
                  fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.set_ylabel('累计净值', fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')

    # 回撤
    total = equity_df['总资产'].values
    peak = np.maximum.accumulate(total)
    drawdown = (total - peak) / peak * 100
    ax2.fill_between(range(len(drawdown)), drawdown, 0,
                     color='#e74c3c', alpha=0.35)
    ax2.plot(range(len(drawdown)), drawdown, color='#c0392b', linewidth=0.8)
    ax2.set_title('回撤曲线 (Drawdown)', fontsize=11)
    ax2.set_xlabel('交易日', fontsize=11)
    ax2.set_ylabel('回撤 (%)', fontsize=11)
    ax2.grid(True, alpha=0.3, linestyle='--')

    # 标注指标
    text = (f"累计回报: {metrics['累计回报 (%)']}%  |  "
            f"年化收益: {metrics['年化收益率 (%)']}%  |  "
            f"最大回撤: {metrics['最大回撤 (%)']}%  |  "
            f"夏普比率: {metrics['夏普比率']}")
    fig.text(0.5, 0.01, text, ha='center', fontsize=9,
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#ecf0f1', alpha=0.8))

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(save_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  [图表] 已保存 → {save_path}")


# ============================================================
# 7. 参数对比实验
# ============================================================
def run_parameter_experiment(df, param_grid, price_col='收盘价'):
    """遍历不同参数组合，比较绩效"""
    results = []
    for sw, lw in param_grid:
        temp = compute_ma_signals(df, short_window=sw, long_window=lw, price_col=price_col)
        eq, tr, final_cap = backtest(temp)
        if not eq.empty:
            m = compute_metrics(eq)
            m['短均线'] = sw
            m['长均线'] = lw
            m['交易次数'] = len(tr)
            results.append(m)
    return pd.DataFrame(results)


def plot_parameter_heatmap(results_df, save_path):
    """绘制参数对比热力图"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    metrics_labels = [
        ('累计回报 (%)', '累计回报 (%)', 'RdYlGn'),
        ('最大回撤 (%)', '最大回撤 (%)', 'RdYlGn_r'),
        ('夏普比率', '夏普比率', 'RdYlGn'),
    ]

    for ax, (col, title, cmap) in zip(axes, metrics_labels):
        pivot = results_df.pivot_table(values=col, index='短均线', columns='长均线')
        im = ax.imshow(pivot.values, cmap=cmap, aspect='auto', origin='lower')
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('长均线周期')
        ax.set_ylabel('短均线周期')
        # 标注数值
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                val = pivot.iloc[i, j]
                if not np.isnan(val):
                    ax.text(j, i, f'{val:.1f}', ha='center', va='center',
                            fontsize=8, fontweight='bold')
        plt.colorbar(im, ax=ax, shrink=0.8)

    plt.suptitle('双均线参数网格搜索 — 绩效对比', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  [图表] 已保存 → {save_path}")


# ============================================================
# 8. 主流程
# ============================================================
def main():
    OUTPUT_DIR = 'E:/EN_study_tool/BA_task'

    # ---- 8a. 贵州茅台主分析 ----
    print("=" * 60)
    print("  双均线策略分析 — 贵州茅台 (600519)")
    print("=" * 60)

    csv_path = f'{OUTPUT_DIR}/贵州茅台_600519_日线数据.csv'
    df = load_data(csv_path)
    print(f"\n[数据] 加载完成: {len(df)} 个交易日, "
          f"{df['交易日期'].iloc[0].strftime('%Y-%m-%d')} ~ "
          f"{df['交易日期'].iloc[-1].strftime('%Y-%m-%d')}")

    # 默认参数
    SHORT, LONG = 5, 15
    df_signals = compute_ma_signals(df, short_window=SHORT, long_window=LONG)

    n_buy = (df_signals['signal'] == 1).sum()
    n_sell = (df_signals['signal'] == -1).sum()
    print(f"[信号] 金叉(买入): {n_buy} 次, 死叉(卖出): {n_sell} 次")

    # 回测
    equity, trades, final_cap = backtest(df_signals)
    metrics = compute_metrics(equity)
    print(f"\n--- 绩效指标 (5/15 日) ---")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
    if not trades.empty:
        print(f"  交易次数: {len(trades)}")
        for _, t in trades.iterrows():
            print(f"    {t['日期'].strftime('%Y-%m-%d')}  {t['类型']}  "
                  f"@{t['价格']:.1f}  x{t['数量']}股  ¥{t['金额']:,.0f}")

    # 绘图
    plot_strategy(df_signals, trades, SHORT, LONG,
                  '贵州茅台 (600519)',
                  f'{OUTPUT_DIR}/chart_maotai_strategy.png')
    plot_equity_curve(equity, df, metrics,
                      '贵州茅台 (600519)',
                      f'{OUTPUT_DIR}/chart_maotai_equity.png')

    # ---- 8b. 参数网格搜索 ----
    print("\n" + "=" * 60)
    print("  参数网格搜索 (贵州茅台)")
    print("=" * 60)

    param_grid = [(3, 10), (5, 10), (5, 15), (5, 20),
                  (10, 20), (10, 30), (10, 60), (20, 60)]
    results = run_parameter_experiment(df, param_grid)
    print(results[['短均线', '长均线', '累计回报 (%)', '最大回撤 (%)',
                    '夏普比率', '交易次数']].to_string(index=False))

    plot_parameter_heatmap(results,
                           f'{OUTPUT_DIR}/chart_parameter_heatmap.png')

    # 保存结果CSV
    results.to_csv(f'{OUTPUT_DIR}/parameter_results.csv',
                   index=False, encoding='utf-8-sig')
    print(f"\n  [数据] 参数对比结果 → {OUTPUT_DIR}/parameter_results.csv")

    # ---- 8c. 最优参数详细分析 ----
    best = results.loc[results['累计回报 (%)'].idxmax()]
    print(f"\n[最优] 短均线={int(best['短均线'])}, 长均线={int(best['长均线'])}, "
          f"累计回报={best['累计回报 (%)']}%")

    best_sw, best_lw = int(best['短均线']), int(best['长均线'])
    df_best = compute_ma_signals(df, short_window=best_sw, long_window=best_lw)
    eq_best, tr_best, _ = backtest(df_best)
    m_best = compute_metrics(eq_best)
    plot_strategy(df_best, tr_best, best_sw, best_lw,
                  '贵州茅台 (600519) — 最优参数',
                  f'{OUTPUT_DIR}/chart_maotai_best.png')
    plot_equity_curve(eq_best, df, m_best,
                      '贵州茅台 (600519) — 最优参数',
                      f'{OUTPUT_DIR}/chart_maotai_best_equity.png')

    # ---- 8d. 与买入持有策略对比 ----
    print("\n--- 策略 vs 买入持有 ---")
    buy_hold_return = (df['收盘价'].iloc[-1] / df['收盘价'].iloc[0] - 1) * 100
    years = len(df) / 252
    buy_hold_ann = ((df['收盘价'].iloc[-1] / df['收盘价'].iloc[0]) ** (1 / years) - 1) * 100
    print(f"  买入持有: 累计回报 {buy_hold_return:.2f}%, 年化 {buy_hold_ann:.2f}%")
    print(f"  策略(5/15):  累计回报 {metrics['累计回报 (%)']}%, "
          f"年化 {metrics['年化收益率 (%)']}%")

    print("\n✅ 全部图表和分析完成！")
    return df, metrics, results


if __name__ == '__main__':
    df, metrics, results = main()
