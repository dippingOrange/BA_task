# -*- coding: utf-8 -*-
"""
贵州茅台 (600519.SH) 综合分析报告
生成 PDF 格式，包含 K线/曲线分析、基本面、技术面、投资建议
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime

# ==============================
# 1. 加载数据
# ==============================
df = pd.read_csv("贵州茅台_600519_日线数据.csv", encoding="utf-8-sig")
df["交易日期"] = pd.to_datetime(df["交易日期"])
df = df.sort_values("交易日期").reset_index(drop=True)

# ==============================
# 2. 技术指标计算
# ==============================

def calc_ma(series, window):
    return series.rolling(window=window).mean()

def calc_ema(series, window):
    return series.ewm(span=window, adjust=False).mean()

def calc_macd(close, fast=12, slow=26, signal=9):
    ema_fast = calc_ema(close, fast)
    ema_slow = calc_ema(close, slow)
    dif = ema_fast - ema_slow
    dea = calc_ema(dif, signal)
    macd_hist = 2 * (dif - dea)
    return dif, dea, macd_hist

def calc_rsi(close, window=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calc_bollinger(close, window=20, num_std=2):
    ma = calc_ma(close, window)
    std = close.rolling(window=window).std()
    upper = ma + num_std * std
    lower = ma - num_std * std
    return upper, ma, lower

# 计算所有指标
df["MA5"] = calc_ma(df["收盘价"], 5)
df["MA10"] = calc_ma(df["收盘价"], 10)
df["MA20"] = calc_ma(df["收盘价"], 20)
df["MA60"] = calc_ma(df["收盘价"], 60)
df["DIF"], df["DEA"], df["MACD"] = calc_macd(df["收盘价"])
df["RSI14"] = calc_rsi(df["收盘价"], 14)
df["BB_upper"], df["BB_mid"], df["BB_lower"] = calc_bollinger(df["收盘价"])

# ==============================
# 3. 统计数据
# ==============================
latest = df.iloc[-1]
first = df.iloc[0]
max_close = df["收盘价"].max()
min_close = df["收盘价"].min()
max_date = df.loc[df["收盘价"].idxmax(), "交易日期"]
min_date = df.loc[df["收盘价"].idxmin(), "交易日期"]

# 涨跌统计
up_days = (df["涨跌额"] > 0).sum()
down_days = (df["涨跌额"] < 0).sum()
flat_days = (df["涨跌额"] == 0).sum()
avg_pct_chg = df["涨跌幅(%)"].mean()
max_up = df["涨跌幅(%)"].max()
max_down = df["涨跌幅(%)"].min()
volatility = df["涨跌幅(%)"].std()

total_return = (latest["收盘价"] / first["收盘价"] - 1) * 100

# 近期技术信号
latest_rsi = df["RSI14"].iloc[-1]
latest_dif = df["DIF"].iloc[-1]
latest_dea = df["DEA"].iloc[-1]
latest_macd = df["MACD"].iloc[-1]

# 均线关系
ma5_latest = df["MA5"].iloc[-1]
ma10_latest = df["MA10"].iloc[-1]
ma20_latest = df["MA20"].iloc[-1]
ma60_latest = df["MA60"].iloc[-1]

# 布林带位置
bb_upper = df["BB_upper"].iloc[-1]
bb_lower = df["BB_lower"].iloc[-1]
bb_mid = df["BB_mid"].iloc[-1]
close_latest = latest["收盘价"]

# 月度收益
df["month"] = df["交易日期"].dt.to_period("M")
monthly_close = df.groupby("month")["收盘价"].last()
monthly_return = monthly_close.pct_change() * 100

# ==============================
# 4. 生成报告 HTML
# ==============================

# 确定技术面信号
signals = []

# MACD信号
if latest_macd > 0 and latest_dif > latest_dea:
    signals.append("MACD金叉向上，短期动能偏多")
elif latest_macd < 0 and latest_dif < latest_dea:
    signals.append("MACD死叉向下，短期动能偏空")
else:
    signals.append("MACD方向不明，观望")

# RSI信号
if latest_rsi > 70:
    signals.append(f"RSI(14)={latest_rsi:.1f}，处于超买区域")
elif latest_rsi < 30:
    signals.append(f"RSI(14)={latest_rsi:.1f}，处于超卖区域")
else:
    signals.append(f"RSI(14)={latest_rsi:.1f}，处于中性区间")

# 均线信号
if ma5_latest > ma10_latest > ma20_latest > ma60_latest:
    signals.append("均线多头排列（MA5>MA10>MA20>MA60），中期趋势偏多")
elif ma5_latest < ma10_latest < ma20_latest < ma60_latest:
    signals.append("均线空头排列（MA5<MA10<MA20<MA60），中期趋势偏空")
else:
    signals.append("均线交织，方向不明确")

# 布林带信号
bb_position = (close_latest - bb_lower) / (bb_upper - bb_lower) * 100 if bb_upper != bb_lower else 50
signals.append(f"收盘价位于布林带 {bb_position:.0f}% 位置（上轨{bb_upper:.0f}，中轨{bb_mid:.0f}，下轨{bb_lower:.0f}）")

signals_text = "\n".join([f"<li>{s}</li>" for s in signals])

# 月度收益表
monthly_table_rows = ""
for m, r in monthly_return.dropna().tail(12).items():
    color = "#c0392b" if r >= 0 else "#27ae60"
    monthly_table_rows += f"<tr><td>{m}</td><td style='color:{color};text-align:right'>{r:+.2f}%</td></tr>\n"

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>贵州茅台 (600519.SH) 综合分析报告</title>
<style>
    @page {{
        size: A4;
        margin: 20mm 25mm;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: "SimSun", "Microsoft YaHei", serif;
        font-size: 13px;
        line-height: 1.8;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
        padding: 40px 30px;
    }}
    .cover {{
        text-align: center;
        padding: 80px 0 60px;
        page-break-after: always;
    }}
    .cover h1 {{
        font-size: 28px;
        font-weight: 900;
        color: #1a1a2e;
        margin-bottom: 12px;
        letter-spacing: 3px;
    }}
    .cover .subtitle {{
        font-size: 18px;
        color: #c0392b;
        margin-bottom: 8px;
    }}
    .cover .stock-code {{
        font-size: 15px;
        color: #666;
        margin-bottom: 30px;
    }}
    .cover .meta {{
        font-size: 14px;
        color: #888;
        line-height: 2.2;
    }}
    .cover .divider {{
        width: 60px;
        height: 3px;
        background: #c0392b;
        margin: 30px auto;
    }}

    h2 {{
        font-size: 20px;
        color: #1a1a2e;
        border-bottom: 2px solid #c0392b;
        padding-bottom: 6px;
        margin: 36px 0 18px;
    }}
    h3 {{
        font-size: 16px;
        color: #2c3e50;
        margin: 24px 0 12px;
    }}
    p {{ margin-bottom: 10px; text-indent: 2em; }}
    ul, ol {{ margin: 8px 0 12px 3em; }}
    li {{ margin-bottom: 4px; }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 14px 0;
        font-size: 12px;
    }}
    th, td {{
        border: 1px solid #ddd;
        padding: 8px 12px;
        text-align: left;
    }}
    th {{
        background: #f0f0f0;
        font-weight: 700;
        color: #1a1a2e;
    }}
    tr:nth-child(even) {{ background: #fafafa; }}

    .stat-box {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 16px 0;
    }}
    .stat-item {{
        flex: 1;
        min-width: 140px;
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 8px;
        padding: 14px;
        text-align: center;
        border: 1px solid #dee2e6;
    }}
    .stat-item .val {{
        font-size: 22px;
        font-weight: 900;
        color: #1a1a2e;
    }}
    .stat-item .lab {{
        font-size: 11px;
        color: #888;
        margin-top: 4px;
    }}
    .stat-item .red {{ color: #c0392b; }}
    .stat-item .green {{ color: #27ae60; }}

    .signal-badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }}
    .signal-bullish {{ background: #fdecea; color: #c0392b; }}
    .signal-bearish {{ background: #e8f5e9; color: #27ae60; }}
    .signal-neutral {{ background: #fff3e0; color: #e67e22; }}

    .disclaimer {{
        margin-top: 50px;
        padding: 16px 20px;
        background: #fef9e7;
        border-left: 4px solid #f39c12;
        font-size: 12px;
        color: #7d6608;
        border-radius: 4px;
    }}
    .disclaimer p {{ text-indent: 0; }}
    .ai-tag {{
        text-align: center;
        color: #999;
        font-size: 11px;
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid #eee;
    }}

    .page-break {{ page-break-before: always; }}

    @media print {{
        body {{ padding: 0; }}
    }}
</style>
</head>
<body>

<!-- ====== 封面 ====== -->
<div class="cover">
    <h1>贵州茅台</h1>
    <div class="subtitle">综合分析报告</div>
    <div class="stock-code">600519.SH · 贵州茅台酒股份有限公司</div>
    <div class="divider"></div>
    <div class="meta">
        报告生成日期：{datetime.now().strftime('%Y年%m月%d日')}<br>
        数据区间：{first['交易日期'].strftime('%Y-%m-%d')} ~ {latest['交易日期'].strftime('%Y-%m-%d')}<br>
        北大BA工作坊 · 量化交易公益课
    </div>
</div>

<!-- ====== 第一部分：线 ====== -->
<h2>一、"线"——价格走势与图形分析</h2>

<h3>1.1 什么是"线"</h3>
<p>"线"在股票分析中通常指代价格走势图（K线图、收盘价曲线等），是技术分析的基石。通过观察价格曲线的形态、趋势和关键点位，投资者可以直观理解股价的历史轨迹，辅助判断买卖时机。</p>
<p>K线（Candlestick）由开盘价、最高价、最低价、收盘价四个价格构成，实体部分表示开盘到收盘的涨跌，影线表示日内波动范围。收盘价折线则将每日收盘价连成曲线，便于观察中长期趋势。</p>

<h3>1.2 过去一年价格走势回顾</h3>
<p>贵州茅台在近一年的走势呈现<strong>先涨后跌</strong>格局：2025年7月初收盘价为 ¥{first['收盘价']:.2f}，2025年下半年股价在 ¥1400~1550 区间震荡。进入2026年后，1月29日出现单日大涨 8.61%，2月5日创出年内最高收盘价 <strong>¥{max_close:.2f}</strong>。此后股价持续走低，到6月26日触及年内最低 <strong>¥{min_close:.2f}</strong>，区间最大回撤幅度达到 24.8%。</p>
<p>截至最新交易日（{latest['交易日期'].strftime('%Y-%m-%d')}），收盘价为 <strong>¥{close_latest:.2f}</strong>，较一年前累计下跌 <strong>{total_return:+.2f}%</strong>。</p>

<h3>1.3 价格统计概览</h3>
<div class="stat-box">
    <div class="stat-item">
        <div class="val">¥{close_latest:.2f}</div>
        <div class="lab">最新收盘价</div>
    </div>
    <div class="stat-item">
        <div class="val">{total_return:+.2f}%</div>
        <div class="lab">一年涨跌幅</div>
    </div>
    <div class="stat-item">
        <div class="val red">¥{max_close:.2f}</div>
        <div class="lab">年内最高 ({max_date.strftime('%m/%d')})</div>
    </div>
    <div class="stat-item">
        <div class="val green">¥{min_close:.2f}</div>
        <div class="lab">年内最低 ({min_date.strftime('%m/%d')})</div>
    </div>
    <div class="stat-item">
        <div class="val">{volatility:.2f}%</div>
        <div class="lab">日波动率(标准差)</div>
    </div>
</div>

<table>
    <tr><th>指标</th><th>数值</th></tr>
    <tr><td>交易日总数</td><td>{len(df)} 天</td></tr>
    <tr><td>上涨天数</td><td>{up_days} 天 ({up_days/len(df)*100:.1f}%)</td></tr>
    <tr><td>下跌天数</td><td>{down_days} 天 ({down_days/len(df)*100:.1f}%)</td></tr>
    <tr><td>日均涨跌幅</td><td>{avg_pct_chg:+.3f}%</td></tr>
    <tr><td>最大单日涨幅</td><td style="color:#c0392b">+{max_up:.2f}%</td></tr>
    <tr><td>最大单日跌幅</td><td style="color:#27ae60">{max_down:.2f}%</td></tr>
</table>

<h3>1.4 月度收益分析</h3>
<table>
    <tr><th>月份</th><th>月度涨跌幅</th></tr>
    {monthly_table_rows}
</table>

<!-- ====== 第二部分：基本面 ====== -->
<div class="page-break"></div>
<h2>二、基本面分析</h2>

<h3>2.1 什么是基本面</h3>
<p>基本面分析（Fundamental Analysis）是通过研究公司的财务状况、经营能力、行业地位、宏观经济等内在价值因素来评估股票是否值得投资的方法。核心逻辑是：股票价格最终会回归其内在价值。</p>

<h3>2.2 公司概况</h3>
<table>
    <tr><th style="width:150px">项目</th><th>内容</th></tr>
    <tr><td>公司全称</td><td>贵州茅台酒股份有限公司</td></tr>
    <tr><td>股票代码</td><td>600519.SH（上交所主板）</td></tr>
    <tr><td>成立日期</td><td>1999年11月20日</td></tr>
    <tr><td>注册地址</td><td>贵州省遵义市</td></tr>
    <tr><td>员工人数</td><td>34,992 人</td></tr>
    <tr><td>法定代表人/董事长</td><td>陈华</td></tr>
    <tr><td>总经理</td><td>王莉</td></tr>
    <tr><td>总股本</td><td>12.50 亿股（全流通）</td></tr>
    <tr><td>主营业务</td><td>贵州茅台酒系列产品的生产与销售，涵盖飞天茅台、茅台王子酒、茅台迎宾酒、陈年茅台等多个系列，同时涉及饮料、食品、包装材料及防伪技术等领域。</td></tr>
</table>

<h3>2.3 估值指标（截至 {latest['交易日期'].strftime('%Y-%m-%d')}）</h3>
<p>以下数据来自 Tushare 金融数据库：</p>
<table>
    <tr><th>指标</th><th>数值</th><th>说明</th></tr>
    <tr><td>总市值</td><td>约 1.49 万亿元</td><td>A股市值第一，全球烈酒行业市值领先</td></tr>
    <tr><td>市盈率 PE(TTM)</td><td>18.05 倍</td><td>处于历史较低分位，近5年PE中枢约30倍</td></tr>
    <tr><td>市净率 PB</td><td>5.51 倍</td><td>品牌溢价显著，远高于白酒行业平均</td></tr>
    <tr><td>市销率 PS(TTM)</td><td>8.67 倍</td><td>高利润率支撑较高市销率</td></tr>
</table>

<h3>2.4 基本面优势</h3>
<ul>
    <li><strong>品牌护城河极深：</strong>茅台是中国白酒行业绝对的龙头品牌，具有无可替代的品牌价值和消费者心智占有率。飞天茅台长期供不应求，出厂价与市场零售价之间存在巨大价差，体现了强大的定价权。</li>
    <li><strong>盈利能力卓越：</strong>茅台毛利率长期维持在 90% 以上，净利率超过 50%，ROE 常年高于 25%，在A股中属于顶级盈利质量。</li>
    <li><strong>现金流充裕：</strong>公司账上现金储备充足，预收款模式带来极强的现金流，几乎没有有息负债。</li>
    <li><strong>行业地位稳固：</strong>在白酒行业整体进入存量竞争的背景下，茅台凭借品牌力持续抢占高端市场份额，业绩确定性较高。</li>
    <li><strong>分红回报：</strong>茅台持续高比例分红，近年来分红率超过 50%，对长期投资者具有吸引力。</li>
</ul>

<h3>2.5 需关注的风险</h3>
<ul>
    <li><strong>消费环境变化：</strong>宏观经济下行可能影响高端消费需求，商务宴请场景减少对茅台消费有一定冲击。</li>
    <li><strong>估值中枢下移：</strong>当前 PE 18倍虽然处于历史低位，但白酒行业整体估值中枢有下移趋势，需关注是否持续。</li>
    <li><strong>提价空间收窄：</strong>飞天茅台出厂价与零售价价差虽然大，但提价节奏受到政策和市场舆论制约。</li>
    <li><strong>库存周期波动：</strong>渠道库存和社会库存的周期性变化可能短期影响批价和销量。</li>
</ul>


<!-- ====== 第三部分：技术面 ====== -->
<div class="page-break"></div>
<h2>三、技术面分析</h2>

<h3>3.1 什么是技术面</h3>
<p>技术分析（Technical Analysis）是通过研究历史价格、成交量等市场交易数据，运用各种技术指标和图形形态来预测未来价格走势的方法。技术分析基于三个核心假设：市场行为包容一切、价格以趋势方式演变、历史会重演。</p>

<h3>3.2 均线系统分析</h3>
<table>
    <tr><th>均线</th><th>最新值 (元)</th><th>与收盘价关系</th></tr>
    <tr><td>MA5（5日均线）</td><td>{ma5_latest:.2f}</td><td>{'收盘价在MA5之上，短期偏强' if close_latest > ma5_latest else '收盘价在MA5之下，短期偏弱'}</td></tr>
    <tr><td>MA10（10日均线）</td><td>{ma10_latest:.2f}</td><td>{'收盘价在MA10之上' if close_latest > ma10_latest else '收盘价在MA10之下'}</td></tr>
    <tr><td>MA20（20日均线）</td><td>{ma20_latest:.2f}</td><td>{'收盘价在MA20之上' if close_latest > ma20_latest else '收盘价在MA20之下'}</td></tr>
    <tr><td>MA60（60日均线）</td><td>{ma60_latest:.2f}</td><td>{'收盘价在MA60之上，中长期趋势尚可' if close_latest > ma60_latest else '收盘价在MA60之下，中长期压力较大'}</td></tr>
</table>

<p>均线形态判断：{'目前MA5、MA10、MA20、MA60呈现空头排列，短期均线位于长期均线下方，表明股价处于下降趋势中。' if ma5_latest < ma60_latest else '均线系统显示股价处于震荡格局，方向尚不明朗。'}</p>

<h3>3.3 MACD 指标</h3>
<table>
    <tr><th>指标</th><th>最新值</th></tr>
    <tr><td>DIF（快线）</td><td>{latest_dif:.2f}</td></tr>
    <tr><td>DEA（慢线）</td><td>{latest_dea:.2f}</td></tr>
    <tr><td>MACD 柱</td><td style="color:{'#c0392b' if latest_macd > 0 else '#27ae60'}">{latest_macd:.2f}</td></tr>
</table>
<p>MACD 解读：{'DIF位于DEA上方，MACD柱为正，短期动能偏多，关注金叉能否持续。' if latest_dif > latest_dea and latest_macd > 0 else 'DIF位于DEA下方，MACD柱为负，空头动能占优。但需关注零轴附近是否形成金叉信号。' if latest_dif < latest_dea and latest_macd < 0 else 'MACD方向不明，建议观望。'}</p>

<h3>3.4 RSI 相对强弱指标</h3>
<p>最新 RSI(14) = <strong>{latest_rsi:.1f}</strong>。{'RSI处于超卖区域（<30），短期可能存在技术性反弹需求。' if latest_rsi < 30 else 'RSI处于中性区间（30-70），多空力量相对均衡。' if latest_rsi <= 70 else 'RSI处于超买区域（>70），短期回调风险加大。'}</p>

<h3>3.5 布林带 (Bollinger Bands)</h3>
<table>
    <tr><th>轨道</th><th>数值 (元)</th></tr>
    <tr><td>上轨 (Upper)</td><td>{bb_upper:.2f}</td></tr>
    <tr><td>中轨 (Middle / MA20)</td><td>{bb_mid:.2f}</td></tr>
    <tr><td>下轨 (Lower)</td><td>{bb_lower:.2f}</td></tr>
    <tr><td>带宽 (Width)</td><td>{bb_upper - bb_lower:.2f} ({(bb_upper - bb_lower)/bb_mid*100:.1f}%)</td></tr>
</table>

<h3>3.6 技术指标综合信号</h3>
<ul>
    {signals_text}
</ul>


<!-- ====== 第四部分：投资建议 ====== -->
<div class="page-break"></div>
<h2>四、综合分析与投资建议</h2>

<h3>4.1 三维分析汇总</h3>
<table>
    <tr><th style="width:80px">维度</th><th>评级</th><th>核心观点</th></tr>
    <tr>
        <td><strong>线</strong></td>
        <td>偏弱</td>
        <td>过去一年累计下跌 {abs(total_return):.1f}%，处于下降通道。近期在 ¥{min_close:.0f} 附近有初步企稳迹象，但尚未形成明确反转形态。</td>
    </tr>
    <tr>
        <td><strong>基本面</strong></td>
        <td>优秀</td>
        <td>品牌护城河极深，盈利能力A股顶级。当前PE 18倍处于历史低位，估值有安全边际。但需关注白酒行业整体需求结构变化。</td>
    </tr>
    <tr>
        <td><strong>技术面</strong></td>
        <td>中性偏弱</td>
        <td>均线空头排列，短期承压。RSI中性，MACD有待确认方向。布林带收窄可能预示变盘窗口临近。</td>
    </tr>
</table>

<h3>4.2 投资建议</h3>

<p><strong>长期投资者：</strong>贵州茅台作为A股核心资产，当前估值处于历史较低分位，PE仅18倍左右的茅台具有较高的长期配置价值。建议采取<strong>分批逢低建仓</strong>策略，关注 ¥1100-1200 区间作为较好的中长期布局窗口。不建议一次性重仓，保留部分资金应对可能的进一步回调。</p>

<p><strong>中短期交易者：</strong>当前股价处于下降趋势中，技术面信号偏弱。建议等待以下信号出现再考虑介入：（1）股价放量站上 MA20（约 ¥{ma20_latest:.0f}）；（2）MACD在零轴下方形成金叉；（3）RSI突破50中轴。若股价跌破 ¥{min_close:.0f}（前低），止损观望。</p>

<p><strong>核心关注点：</strong></p>
<ul>
    <li>飞天茅台批价走势——是判断终端需求的最直接指标</li>
    <li>季度业绩披露——关注营收和净利润增速是否企稳</li>
    <li>分红政策——高分红是持有茅台的"底仓逻辑"之一</li>
    <li>宏观消费数据——社零、餐饮收入等反映消费景气度</li>
</ul>

<h3>4.3 风险提示</h3>
<ul>
    <li>本报告仅为技术学习和学术交流用途，不构成任何投资建议</li>
    <li>股票投资具有高风险性，历史表现不代表未来收益</li>
    <li>投资者应基于独立判断做出投资决策，盈亏自负</li>
    <li>数据来源：Tushare金融数据库，可能存在延迟或误差</li>
</ul>

<!-- ====== 免责声明 ====== -->
<div class="disclaimer">
    <p><strong>⚠️ 免责声明：</strong>本报告由 AI 大模型自动生成，仅供北京大学BA工作坊量化交易公益课程学习参考。报告中的所有分析、观点和建议均不构成任何形式的投资建议或承诺。股票市场存在较大风险，投资者应根据自身风险承受能力和投资目标，结合专业投资顾问的意见，独立做出投资决策。作者及AI模型不对因使用本报告中的任何内容所导致的任何直接或间接损失承担责任。</p>
</div>

<div class="ai-tag">
    🤖 本报告由 AI 自动生成 | {datetime.now().strftime('%Y-%m-%d %H:%M')}
</div>

</body>
</html>"""

# 保存 HTML
html_path = "贵州茅台_600519_综合分析报告.html"
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"HTML 报告已生成: {html_path}")

# 尝试转换为 PDF
pdf_path = "贵州茅台_600519_综合分析报告.pdf"
try:
    # 尝试 weasyprint
    from weasyprint import HTML as WeasyHTML
    WeasyHTML(filename=html_path).write_pdf(pdf_path)
    print(f"PDF 报告已生成 (weasyprint): {pdf_path}")
except ImportError:
    try:
        # 尝试 pdfkit
        import pdfkit
        pdfkit.from_file(html_path, pdf_path)
        print(f"PDF 报告已生成 (pdfkit): {pdf_path}")
    except ImportError:
        print("警告: 未安装 PDF 库 (weasyprint/pdfkit)，仅保存了 HTML 版本")
        print("可使用浏览器打开 HTML 文件后「打印 → 另存为 PDF」来获取 PDF")
