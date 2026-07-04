# -*- coding: utf-8 -*-
"""
从 CSV 生成交互式 ECharts 平滑曲线图
支持鼠标滚轮缩放、底部滑块选择区间、tooltip 查看详情
"""

import pandas as pd
import json

# 读取 CSV
df = pd.read_csv("贵州茅台_600519_日线数据.csv", encoding="utf-8-sig")
df["交易日期"] = pd.to_datetime(df["交易日期"])

# 准备 ECharts 数据（日期字符串 + 收盘价数组）
dates = df["交易日期"].dt.strftime("%Y-%m-%d").tolist()
close_prices = [round(v, 2) for v in df["收盘价"].tolist()]

# 准备 tooltip 用的完整数据
ohlc_data = []
for _, row in df.iterrows():
    ohlc_data.append({
        "date": row["交易日期"].strftime("%Y-%m-%d"),
        "open": round(row["开盘价"], 2),
        "high": round(row["最高价"], 2),
        "low": round(row["最低价"], 2),
        "close": round(row["收盘价"], 2),
        "change": round(row["涨跌额"], 2),
        "pct_chg": round(row["涨跌幅(%)"], 2),
        "vol": round(row["成交量(手)"] / 10000, 2),  # 万手
        "amount": round(row["成交额(千元)"] / 100000000, 2),  # 亿元
    })

# 找最高最低点
max_idx = df["收盘价"].idxmax()
min_idx = df["收盘价"].idxmin()
start_price = df["收盘价"].iloc[0]
end_price = df["收盘价"].iloc[-1]

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>贵州茅台 (600519.SH) 收盘价走势 - 交互式曲线图</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
        background: #f5f6fa;
    }}
    .header {{
        background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
        color: white;
        padding: 20px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 15px;
    }}
    .header h1 {{
        font-size: 22px;
        font-weight: 600;
    }}
    .header .subtitle {{
        font-size: 13px;
        opacity: 0.85;
        margin-top: 4px;
    }}
    .stats {{
        display: flex;
        gap: 24px;
        flex-wrap: wrap;
    }}
    .stat-item {{
        text-align: center;
    }}
    .stat-value {{
        font-size: 26px;
        font-weight: 700;
    }}
    .stat-label {{
        font-size: 12px;
        opacity: 0.8;
        margin-top: 2px;
    }}
    .stat-value.down {{ color: #2ecc71; }}
    .stat-value.up {{ color: #fff; }}
    #chart {{
        width: 100%;
        height: calc(100vh - 120px);
        min-height: 550px;
        background: white;
        margin: 0;
    }}
    .tip {{
        position: fixed;
        bottom: 12px;
        right: 20px;
        font-size: 11px;
        color: #999;
        background: rgba(255,255,255,0.9);
        padding: 4px 10px;
        border-radius: 10px;
    }}
</style>
</head>
<body>

<div class="header">
    <div>
        <h1>贵州茅台 (600519.SH)</h1>
        <div class="subtitle">每日收盘价 · 交互式平滑曲线图</div>
    </div>
    <div class="stats">
        <div class="stat-item">
            <div class="stat-value">{dates[0]} ~ {dates[-1]}</div>
            <div class="stat-label">数据区间</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{end_price}</div>
            <div class="stat-label">最新收盘价</div>
        </div>
        <div class="stat-item">
            <div class="stat-value {'down' if (end_price - start_price) < 0 else 'up'}">{((end_price / start_price - 1) * 100):+.2f}%</div>
            <div class="stat-label">区间涨跌幅</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{df['收盘价'].max():.0f}</div>
            <div class="stat-label">最高收盘价</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{df['收盘价'].min():.0f}</div>
            <div class="stat-label">最低收盘价</div>
        </div>
    </div>
</div>

<div id="chart"></div>
<div class="tip">🖱 滚轮缩放 · 拖拽平移 · 底部滑块选择区间 · 悬停查看详情</div>

<script>
var dates = {json.dumps(dates, ensure_ascii=False)};
var closePrices = {json.dumps(close_prices)};
var ohlcData = {json.dumps(ohlc_data, ensure_ascii=False)};

var chart = echarts.init(document.getElementById('chart'));

// 涨跌颜色
var upColor = '#c0392b';
var downColor = '#27ae60';

var option = {{
    backgroundColor: '#fff',
    tooltip: {{
        trigger: 'axis',
        axisPointer: {{
            type: 'cross',
            crossStyle: {{ color: '#999' }},
            label: {{ backgroundColor: '#333' }}
        }},
        backgroundColor: 'rgba(255,255,255,0.96)',
        borderColor: '#ddd',
        borderWidth: 1,
        textStyle: {{ color: '#333', fontSize: 13 }},
        formatter: function(params) {{
            var idx = params[0].dataIndex;
            var d = ohlcData[idx];
            var color = d.change >= 0 ? upColor : downColor;
            var arrow = d.change >= 0 ? '▲' : '▼';
            return `<div style="font-weight:700;font-size:15px;margin-bottom:8px;border-bottom:1px solid #eee;padding-bottom:6px">
                        ${{d.date}}
                    </div>
                    <table style="width:100%;line-height:1.8">
                    <tr><td>开盘价</td><td style="text-align:right;font-weight:600">${{d.open}}</td></tr>
                    <tr><td>最高价</td><td style="text-align:right;font-weight:600">${{d.high}}</td></tr>
                    <tr><td>最低价</td><td style="text-align:right;font-weight:600">${{d.low}}</td></tr>
                    <tr><td>收盘价</td><td style="text-align:right;font-weight:700;font-size:15px">${{d.close}}</td></tr>
                    <tr><td>涨跌</td><td style="text-align:right;font-weight:600;color:${{color}}">${{arrow}} ${{d.change > 0 ? '+' : ''}}${{d.change}} (${{d.pct_chg > 0 ? '+' : ''}}${{d.pct_chg}}%)</td></tr>
                    <tr><td>成交量</td><td style="text-align:right">${{d.vol}} 万手</td></tr>
                    <tr><td>成交额</td><td style="text-align:right">${{d.amount}} 亿元</td></tr>
                    </table>`;
        }}
    }},
    grid: {{
        left: '3%',
        right: '4%',
        top: '8%',
        bottom: '15%',
        containLabel: true
    }},
    xAxis: {{
        type: 'category',
        boundaryGap: false,
        data: dates,
        axisLine: {{ lineStyle: {{ color: '#ccc' }} }},
        axisLabel: {{
            color: '#666',
            fontSize: 11,
            formatter: function(v) {{ return v.substring(5); }}  // 只显示 MM-DD
        }},
        splitLine: {{ show: false }}
    }},
    yAxis: {{
        type: 'value',
        name: '收盘价 (元)',
        nameTextStyle: {{ color: '#666', fontSize: 12 }},
        axisLabel: {{ color: '#666', fontSize: 11 }},
        splitLine: {{ lineStyle: {{ color: '#f0f0f0', type: 'dashed' }} }},
        min: function(value) {{ return Math.floor(value.min * 0.97); }},
        max: function(value) {{ return Math.ceil(value.max * 1.02); }}
    }},
    dataZoom: [
        {{
            type: 'slider',
            start: 0,
            end: 100,
            height: 28,
            bottom: '4%',
            borderColor: '#ddd',
            fillerColor: 'rgba(192,57,43,0.15)',
            handleStyle: {{ color: '#c0392b' }},
            dataBackground: {{
                lineStyle: {{ color: '#c0392b', width: 1 }},
                areaStyle: {{ color: 'rgba(192,57,43,0.08)' }}
            }},
            textStyle: {{ color: '#666', fontSize: 11 }},
            moveHandleStyle: {{ color: '#c0392b' }}
        }},
        {{
            type: 'inside',
            start: 0,
            end: 100,
            zoomOnMouseWheel: true,
            moveOnMouseMove: true,
            moveOnMouseWheel: false
        }}
    ],
    series: [
        {{
            name: '收盘价',
            type: 'line',
            data: closePrices,
            smooth: 0.4,           // 平滑曲线: 0=折线, 1=最大平滑
            symbol: 'none',        // 默认不显示数据点（缩放后自动显示）
            sampling: 'lttb',      // 大数据量时智能采样
            lineStyle: {{
                color: upColor,
                width: 2
            }},
            areaStyle: {{
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    {{ offset: 0, color: 'rgba(192,57,43,0.25)' }},
                    {{ offset: 1, color: 'rgba(192,57,43,0.02)' }}
                ])
            }},
            markPoint: {{
                symbol: 'pin',
                symbolSize: 50,
                label: {{ fontSize: 12, fontWeight: 'bold' }},
                data: [
                    {{
                        name: '区间最高',
                        coord: [{max_idx}, {df['收盘价'].max()}],
                        value: {df['收盘价'].max()},
                        itemStyle: {{ color: '#e74c3c' }},
                        label: {{ formatter: '最高\\n{{c}}' }}
                    }},
                    {{
                        name: '区间最低',
                        coord: [{min_idx}, {df['收盘价'].min()}],
                        value: {df['收盘价'].min()},
                        itemStyle: {{ color: '#27ae60' }},
                        label: {{ formatter: '最低\\n{{c}}' }}
                    }}
                ]
            }}
        }}
    ]
}};

chart.setOption(option);

// 响应式
window.addEventListener('resize', function() {{
    chart.resize();
}});
</script>

</body>
</html>"""

with open("贵州茅台_600519_收盘价曲线_交互版.html", "w", encoding="utf-8") as f:
    f.write(html)

print("交互式图表已生成: 贵州茅台_600519_收盘价曲线_交互版.html")
