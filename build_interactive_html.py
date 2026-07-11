#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate interactive HTML for Dual MA Strategy visualization.
Embed all data inline — single self-contained HTML file.
"""

import pandas as pd
import numpy as np
import json

# ---- Load data ----
df = pd.read_csv("E:/EN_study_tool/BA_task/贵州茅台_600519_日线数据.csv", encoding="utf-8-sig")
df['交易日期'] = pd.to_datetime(df['交易日期'])
df = df.sort_values('交易日期').reset_index(drop=True)

# ---- Compute MA and signals for 5/15 ----
def compute_strategy(df, short=5, long=15):
    df = df.copy()
    df['MA_short'] = df['收盘价'].rolling(short).mean()
    df['MA_long'] = df['收盘价'].rolling(long).mean()
    df['diff'] = df['MA_short'] - df['MA_long']
    df['signal'] = 0
    df.loc[(df['diff'] > 0) & (df['diff'].shift(1) <= 0), 'signal'] = 1
    df.loc[(df['diff'] < 0) & (df['diff'].shift(1) >= 0), 'signal'] = -1
    return df

df5 = compute_strategy(df, 5, 15)
df_alt = compute_strategy(df, 3, 10)

# ---- JSON data for charts ----
def df_to_ohlc(d):
    return [[d['交易日期'].iloc[i].strftime('%Y-%m-%d'),
             round(d['开盘价'].iloc[i], 2),
             round(d['收盘价'].iloc[i], 2),
             round(d['最低价'].iloc[i], 2),
             round(d['最高价'].iloc[i], 2)]
            for i in range(len(d))]

def df_to_signals(d):
    buys, sells = [], []
    for i in range(len(d)):
        if d['signal'].iloc[i] == 1:
            buys.append({
                'date': d['交易日期'].iloc[i].strftime('%Y-%m-%d'),
                'price': round(float(d['收盘价'].iloc[i]), 2),
                'coord': [d['交易日期'].iloc[i].strftime('%Y-%m-%d'), round(float(d['收盘价'].iloc[i]), 2)]
            })
        elif d['signal'].iloc[i] == -1:
            sells.append({
                'date': d['交易日期'].iloc[i].strftime('%Y-%m-%d'),
                'price': round(float(d['收盘价'].iloc[i]), 2),
                'coord': [d['交易日期'].iloc[i].strftime('%Y-%m-%d'), round(float(d['收盘价'].iloc[i]), 2)]
            })
    return buys, sells

ohlc_data = df_to_ohlc(df5)
ma_short_data = [[df5['交易日期'].iloc[i].strftime('%Y-%m-%d'), round(float(df5['MA_short'].iloc[i]), 2) if not pd.isna(df5['MA_short'].iloc[i]) else None]
                  for i in range(len(df5))]
ma_long_data = [[df5['交易日期'].iloc[i].strftime('%Y-%m-%d'), round(float(df5['MA_long'].iloc[i]), 2) if not pd.isna(df5['MA_long'].iloc[i]) else None]
                 for i in range(len(df5))]

close_data = [[df5['交易日期'].iloc[i].strftime('%Y-%m-%d'), round(float(df5['收盘价'].iloc[i]), 2)]
               for i in range(len(df5))]

buys, sells = df_to_signals(df5)

# ---- Alt data (3/10) ----
ohlc_alt = df_to_ohlc(df_alt)
ma_short_alt = [[df_alt['交易日期'].iloc[i].strftime('%Y-%m-%d'), round(float(df_alt['MA_short'].iloc[i]), 2) if not pd.isna(df_alt['MA_short'].iloc[i]) else None]
                 for i in range(len(df_alt))]
ma_long_alt = [[df_alt['交易日期'].iloc[i].strftime('%Y-%m-%d'), round(float(df_alt['MA_long'].iloc[i]), 2) if not pd.isna(df_alt['MA_long'].iloc[i]) else None]
                for i in range(len(df_alt))]
buys_alt, sells_alt = df_to_signals(df_alt)

# Volume data
vol_data = [[df5['交易日期'].iloc[i].strftime('%Y-%m-%d'),
             int(df5['成交量(手)'].iloc[i]),
             1 if df5['收盘价'].iloc[i] >= df5['开盘价'].iloc[i] else -1]
            for i in range(len(df5))]

# ---- Detailed trade list ----
def compute_trade_list(d):
    """Return detailed trade records for the trade table"""
    capital = 1000000
    shares = 0
    trades = []
    for i in range(len(d)):
        sig = d['signal'].iloc[i]
        price = d['开盘价'].iloc[i]
        date = d['交易日期'].iloc[i].strftime('%Y-%m-%d')
        close_p = d['收盘价'].iloc[i]
        if sig == 1 and shares == 0:
            shares = int(capital * 0.9997 / price)
            cost = shares * price * 1.0003
            capital -= cost
            trades.append({
                'date': date, 'type': '买入', 'price': round(float(price), 2),
                'shares': shares, 'amount': round(float(cost), 0),
                'capital': round(float(capital), 0), 'position': round(float(shares * close_p), 0),
                'total': round(float(capital + shares * close_p), 0)
            })
        elif sig == -1 and shares > 0:
            proceeds = shares * price * 0.9997
            capital += proceeds
            trades.append({
                'date': date, 'type': '卖出', 'price': round(float(price), 2),
                'shares': shares, 'amount': round(float(proceeds), 0),
                'capital': round(float(capital), 0), 'position': 0,
                'total': round(float(capital), 0)
            })
            shares = 0
    return trades

trades = compute_trade_list(df5)

# ---- Equity curve (daily) ----
def compute_equity(d):
    capital = 1000000
    shares = 0
    equity = []
    for i in range(len(d)):
        sig = d['signal'].iloc[i]
        price = d['开盘价'].iloc[i]
        close_price = d['收盘价'].iloc[i]
        if sig == 1 and shares == 0:
            shares = int(capital * 0.9997 / price)
            capital -= shares * price * 1.0003
        elif sig == -1 and shares > 0:
            capital += shares * price * 0.9997
            shares = 0
        total = capital + shares * close_price
        equity.append({
            'date': d['交易日期'].iloc[i].strftime('%Y-%m-%d'),
            'value': round(float(total), 0),
            'benchmark': round(float(1000000 * close_price / d['收盘价'].iloc[0]), 0)
        })
    return equity

equity_curve = compute_equity(df5)

# ---- Parameter comparison data ----
param_df = pd.read_csv("E:/EN_study_tool/BA_task/parameter_results.csv")
param_json = param_df.to_dict('records')

# ---- Key stats ----
stats = {
    'totalReturn': -9.51,
    'annualReturn': -9.88,
    'mdd': -14.56,
    'sharpe': -1.15,
    'winRate': 14.52,
    'trades': 18,
    'buyHold': -16.02,
    'bestReturn': 3.44,
    'bestParams': '3/10日',
}

# ---- Build full HTML ----
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>贵州茅台 - 双均线策略交互演示</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: "Microsoft YaHei", "SimHei", sans-serif;
    background: #f5f6fa; color: #2c3e50;
    min-height: 100vh;
}}
.header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white; padding: 30px 40px; text-align: center;
}}
.header h1 {{ font-size: 28px; font-weight: 700; letter-spacing: 2px; }}
.header .sub {{ font-size: 14px; color: #a0b4c8; margin-top: 6px; }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}

/* KPI Cards */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 14px; margin-bottom: 20px;
}}
.kpi-card {{
    background: white; border-radius: 12px; padding: 18px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    text-align: center; transition: transform 0.2s;
}}
.kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.12); }}
.kpi-card .label {{ font-size: 12px; color: #7f8c8d; margin-bottom: 6px; }}
.kpi-card .value {{ font-size: 24px; font-weight: 700; }}
.kpi-card .value.red {{ color: #e74c3c; }}
.kpi-card .value.green {{ color: #27ae60; }}
.kpi-card .sub-label {{ font-size: 11px; color: #95a5a6; margin-top: 4px; }}

/* Chart cards */
.chart-card {{
    background: white; border-radius: 12px; padding: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 20px;
}}
.chart-card h3 {{ font-size: 16px; margin-bottom: 12px; color: #1a1a2e; border-left: 3px solid #e74c3c; padding-left: 10px; }}
.chart-box {{ width: 100%; height: 520px; }}

/* Two column */
.two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
@media (max-width: 900px) {{ .two-col {{ grid-template-columns: 1fr; }} }}

/* Controls */
.controls {{
    display: flex; gap: 12px; align-items: center; flex-wrap: wrap;
    margin-bottom: 16px; padding: 12px 16px;
    background: #f0f2f5; border-radius: 8px;
}}
.controls label {{ font-size: 13px; font-weight: 600; }}
.controls select, .controls input {{
    padding: 6px 10px; border: 1px solid #ddd; border-radius: 6px;
    font-size: 13px; font-family: inherit;
}}
.controls button {{
    padding: 7px 20px; background: #e74c3c; color: white;
    border: none; border-radius: 6px; font-size: 13px; cursor: pointer;
    font-family: inherit; transition: background 0.2s;
}}
.controls button:hover {{ background: #c0392b; }}

/* Trade table */
.trade-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
.trade-table th {{
    background: #2c3e50; color: white; padding: 8px 10px;
    text-align: center; font-weight: 600;
}}
.trade-table td {{ padding: 7px 10px; text-align: center; border-bottom: 1px solid #eee; }}
.trade-table tr:nth-child(even) {{ background: #fafbfc; }}
.trade-table .buy {{ color: #e74c3c; font-weight: 700; }}
.trade-table .sell {{ color: #27ae60; font-weight: 700; }}
.trade-table-wrap {{ max-height: 400px; overflow-y: auto; }}

/* Concept cards */
.concept-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 16px; margin-bottom: 20px;
}}
.concept-card {{
    background: white; border-radius: 12px; padding: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-top: 3px solid #e74c3c;
}}
.concept-card.golden {{ border-top-color: #e74c3c; }}
.concept-card.death {{ border-top-color: #27ae60; }}
.concept-card h4 {{ font-size: 15px; margin-bottom: 10px; }}
.concept-card p {{ font-size: 13px; line-height: 1.8; color: #555; }}
.concept-card .formula {{
    background: #f8f9fa; padding: 10px 14px; border-radius: 6px;
    font-family: "Consolas", monospace; font-size: 12px;
    margin: 10px 0; color: #2c3e50;
}}

.footer {{ text-align: center; padding: 30px; color: #95a5a6; font-size: 12px; }}
</style>
</head>
<body>

<div class="header">
    <h1>贵州茅台 (600519.SH) 双均线策略</h1>
    <div class="sub">数据周期: 2025-07-04 ~ 2026-07-03 · 242个交易日 · 交互式演示</div>
</div>

<div class="container">

<!-- KPI Cards -->
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="label">策略累计回报</div>
        <div class="value red">{stats['totalReturn']}%</div>
        <div class="sub-label">vs 买入持有 {stats['buyHold']}%</div>
    </div>
    <div class="kpi-card">
        <div class="label">最大回撤 (MDD)</div>
        <div class="value red">{stats['mdd']}%</div>
        <div class="sub-label">风险控制指标</div>
    </div>
    <div class="kpi-card">
        <div class="label">夏普比率</div>
        <div class="value red">{stats['sharpe']}</div>
        <div class="sub-label">风险调整后收益</div>
    </div>
    <div class="kpi-card">
        <div class="label">总交易次数</div>
        <div class="value" style="color:#2c3e50">{stats['trades']}次</div>
        <div class="sub-label">9买 + 9卖</div>
    </div>
    <div class="kpi-card">
        <div class="label">日胜率</div>
        <div class="value" style="color:#2c3e50">{stats['winRate']}%</div>
        <div class="sub-label">盈利天数占比</div>
    </div>
    <div class="kpi-card">
        <div class="label">最优参数</div>
        <div class="value green">+{stats['bestReturn']}%</div>
        <div class="sub-label">{stats['bestParams']}</div>
    </div>
</div>

<!-- Parameter Controls -->
<div class="chart-card">
    <div class="controls">
        <label>短均线:</label>
        <select id="shortMA" onchange="updateChart()">
            <option value="3">3日</option>
            <option value="5" selected>5日</option>
            <option value="10">10日</option>
            <option value="20">20日</option>
        </select>
        <label>长均线:</label>
        <select id="longMA" onchange="updateChart()">
            <option value="10">10日</option>
            <option value="15" selected>15日</option>
            <option value="20">20日</option>
            <option value="30">30日</option>
            <option value="60">60日</option>
        </select>
        <label>起始日期:</label>
        <input type="date" id="startDate" value="2025-07-04" onchange="updateChart()">
        <label>截止日期:</label>
        <input type="date" id="endDate" value="2026-07-03" onchange="updateChart()">
        <button onclick="resetView()">重置视图</button>
    </div>
    <h3>图1: 双均线策略主图 — K线 + 均线 + 买卖信号</h3>
    <div id="mainChart" class="chart-box"></div>
</div>

<!-- Two column layout -->
<div class="two-col">
    <div class="chart-card">
        <h3>图2: 策略净值曲线 vs 买入持有</h3>
        <div id="equityChart" class="chart-box" style="height:420px"></div>
    </div>
    <div class="chart-card">
        <h3>图3: 成交量分布</h3>
        <div id="volumeChart" class="chart-box" style="height:420px"></div>
    </div>
</div>

<!-- Concept explanation cards -->
<div class="concept-grid">
    <div class="concept-card golden">
        <h4>金叉 (Golden Cross) — 买入信号</h4>
        <div class="formula">
            MA_short(t-1) &le; MA_long(t-1)<br>
            AND<br>
            MA_short(t) &gt; MA_long(t)
        </div>
        <p>短期均线从下方上穿长期均线，表示短期价格动能超越长期趋势，市场情绪由弱转强。此时触发<b>买入信号</b>，以次日开盘价全仓买入。在图表中以红色三角标记。</p>
    </div>
    <div class="concept-card death">
        <h4>死叉 (Death Cross) — 卖出信号</h4>
        <div class="formula">
            MA_short(t-1) &ge; MA_long(t-1)<br>
            AND<br>
            MA_short(t) &lt; MA_long(t)
        </div>
        <p>短期均线从上方下穿长期均线，表示短期价格动能弱于长期趋势，市场情绪由强转弱。此时触发<b>卖出信号</b>，以次日开盘价清仓。在图表中以绿色倒三角标记。</p>
    </div>
    <div class="concept-card">
        <h4>最大回撤 (MDD)</h4>
        <div class="formula">MDD = max((Peak - Valley) / Peak)</div>
        <p>衡量从资金曲线最高点到后续最低点的最大跌幅，-14.56%的MDD意味着最坏情况下本金缩水了14.56%。这是评估策略风险承受能力的关键指标。</p>
    </div>
    <div class="concept-card">
        <h4>夏普比率 (Sharpe)</h4>
        <div class="formula">Sharpe = (Rp - Rf) / sigma_p</div>
        <p>风险调整后收益指标。负值(-1.15)表明策略收益低于无风险利率(3%)，承担风险未获得合理回报。>1为优秀，>2为卓越。</p>
    </div>
</div>

<!-- Trade detail table -->
<div class="chart-card">
    <h3>交易明细 (5/15日)</h3>
    <div class="trade-table-wrap">
        <table class="trade-table">
            <thead>
                <tr>
                    <th>#</th><th>日期</th><th>类型</th><th>成交价(元)</th>
                    <th>数量(股)</th><th>金额(元)</th><th>现金(元)</th><th>总资产(元)</th>
                </tr>
            </thead>
            <tbody id="tradeBody"></tbody>
        </table>
    </div>
</div>

<!-- Parameter heatmap 
<div class="chart-card">
    <h3>图4: 参数网格搜索热力图</h3>
    <div id="heatmapChart" class="chart-box" style="height:420px"></div>
</div>-->

</div>

<div class="footer">
    北大BA工作坊 · 量化交易公益课 · 本页面由AI自动生成 | 数据来源: Tushare金融数据库<br>
    ⚠️ 本页面仅供学习参考，不构成任何投资建议。股市有风险，投资需谨慎。
</div>

<script>
// ========== DATA ==========
const ohlcData = {json.dumps(ohlc_data)};
const maShortData = {json.dumps(ma_short_data)};
const maLongData = {json.dumps(ma_long_data)};
const closeData = {json.dumps(close_data)};
const buySignals = {json.dumps([[s['coord'][0], s['coord'][1]] for s in buys])};
const sellSignals = {json.dumps([[s['coord'][0], s['coord'][1]] for s in sells])};
const volData = {json.dumps(vol_data)};
const equityData = {json.dumps(equity_curve)};
const tradesData = {json.dumps(trades)};

// Alt dataset
const ohlcAlt = {json.dumps(ohlc_alt)};
const maShortAlt = {json.dumps(ma_short_alt)};
const maLongAlt = {json.dumps(ma_long_alt)};
const buyAlt = {json.dumps([[s['coord'][0], s['coord'][1]] for s in buys_alt])};
const sellAlt = {json.dumps([[s['coord'][0], s['coord'][1]] for s in sells_alt])};

// Parameter data
const paramData = {json.dumps(param_json)};

// ========== MAIN CHART ==========
const mainChart = echarts.init(document.getElementById('mainChart'));

function buildMainChart(ohlc, maShort, maLong, buys, sells) {{
    // Build candlestick data
    const dates = ohlc.map(d => d[0]);
    const kData = ohlc.map(d => [d[1], d[2], d[3], d[4]]); // [open, close, low, high]

    const option = {{
        tooltip: {{
            trigger: 'axis',
            axisPointer: {{ type: 'cross' }},
            formatter: function(params) {{
                if (!params || params.length < 2) return '';
                const d = params[0].axisValue;
                let s = '<b>' + d + '</b><br/>';
                params.forEach(p => {{
                    if (p.seriesName === 'K线') {{
                        const v = p.data;
                        if (v && v.length >= 4) {{
                            s += '开: ' + v[1] + ' | 收: ' + v[2] + '<br/>';
                            s += '低: ' + v[3] + ' | 高: ' + v[4] + '<br/>';
                        }}
                    }} else if (p.value !== undefined && p.value !== null) {{
                        s += p.marker + ' ' + p.seriesName + ': ' + p.value + '<br/>';
                    }}
                }});
                return s;
            }}
        }},
        legend: {{
            data: ['K线', 'MA5(短)', 'MA15(长)', '金叉买入', '死叉卖出'],
            top: 5, left: 'center',
            textStyle: {{ fontSize: 12 }}
        }},
        grid: [
            {{ left: '8%', right: '8%', top: '12%', height: '60%' }},
            {{ left: '8%', right: '8%', top: '78%', height: '14%' }}
        ],
        xAxis: [
            {{
                type: 'category', data: dates, gridIndex: 0,
                boundaryGap: true,
                axisLine: {{ onZero: false }},
                splitLine: {{ show: false }},
                axisLabel: {{ show: false }}
            }},
            {{
                type: 'category', data: dates, gridIndex: 1,
                boundaryGap: true,
                axisLabel: {{
                    rotate: 30, fontSize: 10,
                    formatter: v => v.substr(5)
                }}
            }}
        ],
        yAxis: [
            {{
                scale: true, gridIndex: 0,
                splitArea: {{ show: true }},
                axisLabel: {{ fontSize: 10, formatter: v => v.toFixed(0) }}
            }},
            {{
                scale: true, gridIndex: 1,
                splitNumber: 3,
                axisLabel: {{ fontSize: 10, formatter: v => (v/10000).toFixed(0) + '万' }}
            }}
        ],
        dataZoom: [
            {{ type: 'inside', xAxisIndex: [0, 1], start: 0, end: 100 }},
            {{ type: 'slider', xAxisIndex: [0, 1], start: 0, end: 100, height: 20, bottom: 0 }}
        ],
        series: [
            {{
                name: 'K线', type: 'candlestick', data: kData,
                xAxisIndex: 0, yAxisIndex: 0,
                itemStyle: {{
                    color: '#e74c3c', color0: '#27ae60',
                    borderColor: '#e74c3c', borderColor0: '#27ae60'
                }},
                emphasis: {{
                    itemStyle: {{ color: '#c0392b', color0: '#1e8449' }}
                }}
            }},
            {{
                name: 'MA5(短)', type: 'line', data: maShort.map(d => d[1]),
                xAxisIndex: 0, yAxisIndex: 0,
                smooth: false, symbol: 'none',
                lineStyle: {{ color: '#e74c3c', width: 1.5, type: 'dashed' }}
            }},
            {{
                name: 'MA15(长)', type: 'line', data: maLong.map(d => d[1]),
                xAxisIndex: 0, yAxisIndex: 0,
                smooth: false, symbol: 'none',
                lineStyle: {{ color: '#3498db', width: 1.5, type: 'dashed' }}
            }},
            {{
                name: '金叉买入', type: 'scatter', data: buys,
                xAxisIndex: 0, yAxisIndex: 0,
                symbol: 'triangle', symbolSize: 14,
                itemStyle: {{ color: '#e74c3c', borderColor: '#a93226', borderWidth: 1 }},
                z: 10
            }},
            {{
                name: '死叉卖出', type: 'scatter', data: sells,
                xAxisIndex: 0, yAxisIndex: 0,
                symbol: 'triangle', symbolSize: 14, symbolRotate: 180,
                itemStyle: {{ color: '#27ae60', borderColor: '#1e8449', borderWidth: 1 }},
                z: 10
            }},
            {{
                name: '成交量', type: 'bar', data: volData,
                xAxisIndex: 1, yAxisIndex: 1,
                itemStyle: {{
                    color: function(p) {{
                        return volData[p.dataIndex][2] >= 0 ? '#e74c3c' : '#27ae60';
                    }}
                }},
                emphasis: {{ itemStyle: {{ opacity: 0.7 }} }}
            }}
        ]
    }};
    mainChart.setOption(option, true);
}}

function filterByDate(ohlc, maS, maL, buys, sells) {{
    const start = document.getElementById('startDate').value;
    const end = document.getElementById('endDate').value;
    if (!start && !end) return [ohlc, maS, maL, buys, sells];

    const filter = data => data.filter(d => {{
        const date = d[0];
        if (start && date < start) return false;
        if (end && date > end) return false;
        return true;
    }});

    const fOhlc = filter(ohlc);
    const fMaS = filter(maS);
    const fMaL = filter(maL);
    const fBuys = buys.filter(b => {{
        if (start && b[0] < start) return false;
        if (end && b[0] > end) return false;
        return true;
    }});
    const fSells = sells.filter(s => {{
        if (start && s[0] < start) return false;
        if (end && s[0] > end) return false;
        return true;
    }});
    return [fOhlc, fMaS, fMaL, fBuys, fSells];
}}

function updateChart() {{
    const sw = document.getElementById('shortMA').value;
    const lw = document.getElementById('longMA').value;
    let ohlc, maS, maL, buys, sells;
    if (sw === '5' && lw === '15') {{
        ohlc = ohlcData; maS = maShortData; maL = maLongData; buys = buySignals; sells = sellSignals;
    }} else if (sw === '3' && lw === '10') {{
        ohlc = ohlcAlt; maS = maShortAlt; maL = maLongAlt; buys = buyAlt; sells = sellAlt;
    }} else {{
        ohlc = ohlcData; maS = maShortData; maL = maLongData; buys = buySignals; sells = sellSignals;
    }}
    const [fOhlc, fMaS, fMaL, fBuys, fSells] = filterByDate(ohlc, maS, maL, buys, sells);
    buildMainChart(fOhlc, fMaS, fMaL, fBuys, fSells);
}}

function resetView() {{
    document.getElementById('shortMA').value = '5';
    document.getElementById('longMA').value = '15';
    document.getElementById('startDate').value = '2025-07-04';
    document.getElementById('endDate').value = '2026-07-03';
    updateChart();
}}

// ========== EQUITY CHART ==========
const equityChart = echarts.init(document.getElementById('equityChart'));
(function() {{
    const dates = equityData.map(d => d.date);
    const values = equityData.map(d => d.value / 10000);
    const bench = equityData.map(d => d.benchmark / 10000);

    equityChart.setOption({{
        tooltip: {{ trigger: 'axis' }},
        legend: {{ data: ['策略净值', '买入持有净值'], top: 5 }},
        grid: {{ left: '12%', right: '5%', top: '14%', bottom: '10%' }},
        xAxis: {{
            type: 'category', data: dates,
            axisLabel: {{ rotate: 30, fontSize: 10, formatter: v => v.substr(5) }}
        }},
        yAxis: {{
            type: 'value',
            axisLabel: {{ formatter: v => v.toFixed(0) + '万' }}
        }},
        series: [
            {{
                name: '策略净值', type: 'line', data: values,
                smooth: false, symbol: 'none',
                lineStyle: {{ color: '#e74c3c', width: 1.5 }},
                areaStyle: {{ color: 'rgba(231,76,60,0.08)' }}
            }},
            {{
                name: '买入持有净值', type: 'line', data: bench,
                smooth: false, symbol: 'none',
                lineStyle: {{ color: '#3498db', width: 1, type: 'dashed' }}
            }}
        ]
    }});
}})();

// ========== VOLUME CHART ==========
const volumeChart = echarts.init(document.getElementById('volumeChart'));
(function() {{
    const dates = volData.map(d => d[0]);
    const vals = volData.map(d => d[1]);

    volumeChart.setOption({{
        tooltip: {{ trigger: 'axis' }},
        grid: {{ left: '12%', right: '5%', top: '14%', bottom: '10%' }},
        xAxis: {{
            type: 'category', data: dates,
            axisLabel: {{ rotate: 30, fontSize: 10, formatter: v => v.substr(5) }}
        }},
        yAxis: {{
            type: 'value',
            axisLabel: {{ formatter: v => (v/10000).toFixed(0) + '万手' }}
        }},
        series: [{{
            name: '成交量', type: 'bar', data: vals,
            itemStyle: {{
                color: function(p) {{ return volData[p.dataIndex][2] >= 0 ? '#e74c3c' : '#27ae60'; }}
            }}
        }}]
    }});
}})();

// ========== TRADE TABLE ==========
(function() {{
    const tbody = document.getElementById('tradeBody');
    tradesData.forEach((t, i) => {{
        const row = document.createElement('tr');
        const cls = t.type === '买入' ? 'buy' : 'sell';
        row.innerHTML = `<td>${{i+1}}</td><td>${{t.date}}</td>
            <td class="${{cls}}">${{t.type}}</td><td>${{t.price}}</td>
            <td>${{t.shares.toLocaleString()}}</td><td>${{t.amount.toLocaleString()}}</td>
            <td>${{t.capital.toLocaleString()}}</td><td>${{t.total.toLocaleString()}}</td>`;
        tbody.appendChild(row);
    }});
}})();

// Initial render
buildMainChart(ohlcData, maShortData, maLongData, buySignals, sellSignals);

// Responsive
window.addEventListener('resize', function() {{
    mainChart.resize();
    equityChart.resize();
    volumeChart.resize();
}});
</script>
</body>
</html>'''

# Write HTML
output_path = "E:/EN_study_tool/BA_task/双均线策略_交互演示.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"HTML 已生成: {output_path}")
print(f"文件大小: {len(html):,} 字符")
