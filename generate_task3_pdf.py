#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 TASK3 报告 PDF
格式要求:
  - 宋体(中文) + Times New Roman(英文/数字)
  - 五号字 (10.5pt)
  - 1.5 倍行距
  - 0 倍段前段后间距
  - 文字两端对齐
  - 图表有标号和标题
  - 命名 "郑富彬+TASK3.pdf"
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                 PageBreak, Table, TableStyle)
from reportlab.lib import colors
import os


# ---------------- 字体注册 ----------------
def register_fonts():
    """注册宋体（常规）和黑体（用于加粗替代），避免HTML标签导致字体崩坏"""
    # SimSun 常规
    pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc',
                                    subfontIndex=0))
    # 加粗用 SimHei 黑体（独立 TTF，不依赖 TTC subfontIndex）
    pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))
    # 宋体粗体（simsunb.ttf）
    pdfmetrics.registerFont(TTFont('SimSunBold', 'C:/Windows/Fonts/simsunb.ttf'))


# ---------------- 样式定义 ----------------
def get_styles():
    body = ParagraphStyle(
        name='Body',
        fontName='SimSun',
        fontSize=10.5,
        leading=10.5 * 1.5,
        spaceBefore=0,
        spaceAfter=0,
        alignment=TA_JUSTIFY,
        wordWrap='CJK',
    )
    body_bold = ParagraphStyle(
        name='BodyBold',
        fontName='SimHei',
        fontSize=10.5,
        leading=10.5 * 1.5,
        spaceBefore=0,
        spaceAfter=0,
        alignment=TA_JUSTIFY,
        wordWrap='CJK',
    )
    title_l1 = ParagraphStyle(
        name='Title1',
        fontName='SimHei',
        fontSize=18,
        leading=18 * 1.5,
        alignment=TA_CENTER,
        spaceBefore=12,
        spaceAfter=12,
    )
    title_l2 = ParagraphStyle(
        name='Title2',
        fontName='SimHei',
        fontSize=14,
        leading=14 * 1.5,
        alignment=TA_LEFT,
        spaceBefore=6,
        spaceAfter=6,
    )
    title_l3 = ParagraphStyle(
        name='Title3',
        fontName='SimHei',
        fontSize=12,
        leading=12 * 1.5,
        alignment=TA_LEFT,
        spaceBefore=3,
        spaceAfter=3,
    )
    fig_caption = ParagraphStyle(
        name='FigCaption',
        fontName='SimSun',
        fontSize=10.5,
        leading=10.5 * 1.5,
        alignment=TA_CENTER,
        spaceBefore=2,
        spaceAfter=6,
    )
    return {
        'body': body,
        'body_bold': body_bold,
        'title_l1': title_l1,
        'title_l2': title_l2,
        'title_l3': title_l3,
        'fig_caption': fig_caption,
    }


# ---------------- 混排文本处理（无HTML标签！） ----------------
def add_mixed(story, segments):
    """
    将 [(text, style_object), ...] 逐段添加到 story 中。
    无任何 HTML 标签，完全避免字体崩坏。
    """
    for text, style_obj in segments:
        story.append(Paragraph(text, style_obj))


# ---------------- 文档生成 ----------------
def build_pdf(output_path, chart_paths, param_results):
    register_fonts()
    s = get_styles()
    B, BB, H1, H2, H3, FC = s['body'], s['body_bold'], s['title_l1'], s['title_l2'], s['title_l3'], s['fig_caption']

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2.54 * cm,
        rightMargin=2.54 * cm,
        topMargin=2.54 * cm,
        bottomMargin=2.54 * cm,
        title='郑富彬+TASK3',
        author='郑富彬',
    )

    story = []

    # ====== 标题 ======
    story.append(Paragraph('基于双均线交叉的量化策略研究与回测', H1))
    story.append(Paragraph('——以贵州茅台（600519）为例', H2))
    story.append(Spacer(1, 8))

    # ====== 一、任务摘要 ======
    story.append(Paragraph('一、任务摘要', H2))
    story.append(Paragraph(
        '本报告基于贵州茅台（600519.SH）2025年7月4日至2026年7月3日共242个交易日的日线行情数据，'
        '实现并回测了双均线（Dual Moving Average, DMA）交叉量化策略。报告首先阐述双均线策略的核心概念——'
        '金叉与死叉，再介绍量化策略评估的三大基础指标：累计回报、最大回撤与夏普比率，'
        '随后通过 Python 编程完成策略的完整实现，最后进行多组参数对比实验，'
        '总结双均线策略的适用场景和实盘应用心得。', B))
    story.append(Spacer(1, 6))

    # ====== 二、双均线策略核心概念 ======
    story.append(Paragraph('二、双均线策略的核心概念', H2))
    story.append(Paragraph('2.1 双均线策略原理', H3))

    add_mixed(story, [
        ('双均线策略是技术分析中最经典的', B),
        ('趋势跟踪', BB),
        ('策略之一。其核心思想是：通过比较短期均线与长期均线的位置关系，'
         '判断当前股价的趋势方向，并据此产生交易信号。'
         '当短期均线位于长期均线之上时，说明近期价格走势强于远期，市场处于上升趋势；反之则处于下降趋势。'
         '本报告使用简单移动平均（Simple Moving Average, SMA），计算公式为：', B),
        ('MA(n) = (Ct + Ct-1 + ... + Ct-n+1) / n', BB),
        ('，其中 n 为窗口期，Ct 为第 t 日收盘价。', B),
    ])

    story.append(Paragraph('2.2 金叉与死叉', H3))
    add_mixed(story, [
        ('金叉（Golden Cross）：当短期均线由下向上穿越长期均线时形成的交叉点，常被视为买入信号，'
         '提示市场动能由弱转强，趋势可能反转向上。本策略定义：', B),
        ('MA_short(t-1) <= MA_long(t-1) 且 MA_short(t) > MA_long(t)', BB),
        ('，触发买入信号。信号出现后，以次日开盘价全仓买入。', B),
    ])
    add_mixed(story, [
        ('死叉（Death Cross）：当短期均线由上向下穿越长期均线时形成的交叉点，常被视为卖出信号，'
         '提示市场动能由强转弱，趋势可能反转向下。本策略定义：', B),
        ('MA_short(t-1) >= MA_long(t-1) 且 MA_short(t) < MA_long(t)', BB),
        ('，触发卖出信号。信号出现后，以次日开盘价清仓卖出。', B),
    ])

    # ====== 三、量化评估指标 ======
    story.append(Paragraph('三、量化策略评估的基础指标', H2))
    story.append(Paragraph('3.1 累计回报（Cumulative Return）', H3))
    add_mixed(story, [
        ('累计回报衡量策略在回测期内的总盈亏幅度，公式为：', B),
        ('累计回报 = (期末资产 / 期初资产) - 1', BB),
        ('。它是最直观的收益度量，但未考虑风险和时间因素。', B),
    ])

    story.append(Paragraph('3.2 最大回撤（Maximum Drawdown, MDD）', H3))
    add_mixed(story, [
        ('最大回撤衡量策略从历史最高点至最低点的最大跌幅，反映策略在最坏情况下的亏损幅度，'
         '是评估下行风险的核心指标。公式为：', B),
        ('MDD = max(Peak - Valley) / Peak', BB),
        ('。本回测中，MDD 越接近 0 表示回撤控制越好；负值越大表示回撤越深。', B),
    ])

    story.append(Paragraph('3.3 夏普比率（Sharpe Ratio）', H3))
    add_mixed(story, [
        ('夏普比率衡量每承担一单位总风险所能获得的超额回报，'
         '是综合考虑收益与风险的经典指标。公式为：', B),
        ('Sharpe = (Rp - Rf) / sigma_p', BB),
        ('，其中 Rp 为策略年化收益率，Rf 为无风险利率（取年化 3%），'
         'sigma_p 为策略年化波动率。一般认为 Sharpe > 1 为优秀，> 2 为卓越。', B),
    ])

    # ====== 四、策略实现与回测 ======
    story.append(PageBreak())
    story.append(Paragraph('四、Python 编程实现与回测', H2))
    story.append(Paragraph('4.1 数据加载与预处理', H3))
    story.append(Paragraph(
        '使用 Pandas 读取工作目录下的"贵州茅台_600519_日线数据.csv"文件，'
        '解析交易日期字段并按时间升序排列。最终获得 242 个有效交易日，'
        '时间区间为 2025-07-04 至 2026-07-03，覆盖了完整的近一年行情，'
        '包含开盘、收盘、最高、最低价、成交量等字段。', B))

    story.append(Paragraph('4.2 均线计算与信号识别', H3))
    add_mixed(story, [
        ('按题目要求，设定', B),
        ('短均线周期 5 日、长均线周期 15 日', BB),
        ('。通过滚动窗口计算两条均线，再依据"昨日差值符号"和"今日差值符号"判断交叉方向，'
         '识别出金叉（买入）与死叉（卖出）信号。'
         '回测期内共识别 9 次金叉、10 次死叉，共触发 18 笔交易（含期初与期末的对应买卖）。', B),
    ])

    story.append(Paragraph('4.3 模拟交易与回测', H3))
    add_mixed(story, [
        ('回测假设：', B),
        ('初始资金 100 万元', BB),
        ('，单边佣金万三（0.0003），T+1 信号次日开盘价成交，每次全仓买入/卖出，'
         '不考虑融资融券与分红送股。每日记录总资产（现金 + 持仓市值），最终计算资金曲线。', B),
    ])

    # 插入主图
    if 'main' in chart_paths and os.path.exists(chart_paths['main']):
        img = Image(chart_paths['main'], width=16 * cm, height=10 * cm)
        img.hAlign = 'CENTER'
        story.append(Spacer(1, 6))
        story.append(img)
        story.append(Paragraph(
            '图 1  贵州茅台（600519.SH）双均线策略示意图（5/15日）', FC))
        story.append(Paragraph(
            '（注：红色三角为金叉买入信号，绿色倒三角为死叉卖出信号，'
            '下图为持仓区间标注。数据时间：2025-07-04 至 2026-07-03。）', FC))

    # 净值曲线
    if 'equity' in chart_paths and os.path.exists(chart_paths['equity']):
        img = Image(chart_paths['equity'], width=15 * cm, height=8.5 * cm)
        img.hAlign = 'CENTER'
        story.append(Spacer(1, 6))
        story.append(img)
        story.append(Paragraph(
            '图 2  策略净值曲线 vs 买入持有基准', FC))
        story.append(Paragraph(
            '（注：上图为累计净值对比，红色实线为双均线策略，'
            '蓝色虚线为买入持有策略；下图为策略的回撤曲线 Drawdown。）', FC))

    # ====== 五、回测结果 ======
    story.append(PageBreak())
    story.append(Paragraph('五、回测结果与绩效分析', H2))
    story.append(Paragraph('5.1 核心绩效指标（5/15 日默认参数）', H3))

    metrics_data = [
        ['指标', '数值'],
        ['初始资金', '1,000,000.00 元'],
        ['最终资金', '904,938.05 元'],
        ['累计回报', '-9.51%'],
        ['年化收益率', '-9.88%'],
        ['最大回撤 (MDD)', '-14.56%'],
        ['夏普比率 (Sharpe)', '-1.15'],
        ['日胜率', '14.52%'],
        ['总交易次数', '18 次'],
    ]
    tbl = Table(metrics_data, colWidths=[6 * cm, 8 * cm])
    tbl.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'SimSun'),
        ('FONTSIZE', (0, 0), (-1, -1), 10.5),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'SimHei'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.HexColor('#f8f9fa'), colors.HexColor('#ffffff')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(tbl)
    story.append(Paragraph('表 1  双均线策略（5/15日）核心绩效指标汇总', FC))

    story.append(Spacer(1, 4))
    story.append(Paragraph('5.2 结果解读', H3))
    story.append(Paragraph(
        '在 5/15 日默认参数下，策略累计回报为 -9.51%，年化收益 -9.88%，夏普比率 -1.15，'
        '最大回撤 -14.56%。这意味着策略在该震荡偏空的行情中产生了较为明显的亏损。具体来看：', B))
    story.append(Paragraph(
        '(1) 18 笔交易中盈利交易较少，频繁的来回交易导致手续费侵蚀利润；'
        '(2) 在 2026 年 2 月后茅台出现持续下跌行情时，'
        '短均线快速下穿长均线，策略死叉后空仓规避了一定下跌（同期买入持有回报 -16.02%，'
        '策略 -9.51%），说明在趋势性下跌中双均线策略具有一定的"空仓保护"作用；'
        '(3) 但在 2025 年 8 月至 10 月的宽幅震荡中，'
        '策略反复被金叉/死叉"打脸"，造成"高买低卖"的负反馈。', B))

    # ====== 六、参数网格实验 ======
    story.append(PageBreak())
    story.append(Paragraph('六、不同参数组合的对比实验', H2))
    story.append(Paragraph(
        '为探究参数对策略表现的影响，本节对 8 组常见参数组合进行回测，结果如表 2 所示：', B))

    if not param_results.empty:
        table_data = [['短均线', '长均线', '累计回报(%)', '最大回撤(%)',
                       '夏普比率', '交易次数']]
        for _, r in param_results.iterrows():
            table_data.append([
                str(int(r['短均线'])),
                str(int(r['长均线'])),
                f"{r['累计回报 (%)']:.2f}",
                f"{r['最大回撤 (%)']:.2f}",
                f"{r['夏普比率']:.2f}",
                str(int(r['交易次数'])),
            ])
        tbl = Table(table_data, colWidths=[2.2*cm, 2.2*cm, 3*cm, 3*cm, 2.5*cm, 2.5*cm])
        tbl.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'SimSun'),
            ('FONTSIZE', (0, 0), (-1, -1), 9.5),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'SimHei'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.HexColor('#f8f9fa'), colors.HexColor('#ffffff')]),
        ]))
        story.append(tbl)
        story.append(Paragraph('表 2  不同均线周期组合的策略绩效对比', FC))

    story.append(Spacer(1, 6))

    if 'heatmap' in chart_paths and os.path.exists(chart_paths['heatmap']):
        img = Image(chart_paths['heatmap'], width=16 * cm, height=5.5 * cm)
        img.hAlign = 'CENTER'
        story.append(Spacer(1, 4))
        story.append(img)
        story.append(Paragraph(
            '图 3  双均线参数网格搜索的绩效热力图', FC))
        story.append(Paragraph(
            '（注：左图累计回报，绿色越深越好；中图最大回撤，绿色越浅回撤越小；'
            '右图夏普比率，绿色越深越好。）', FC))

    story.append(Paragraph('6.1 参数敏感度分析', H3))
    add_mixed(story, [
        ('从实验结果看，', B),
        ('较短的均线周期（如 3/10）反而表现最好', BB),
        ('，累计回报 3.44%，夏普比率 0.11。这与"茅台在回测期内主要呈宽幅震荡、'
         '短期反弹较多"的特征吻合。短均线对近期价格更敏感，能更快捕捉反弹。', B),
    ])
    add_mixed(story, [
        ('较长的均线周期（如 10/60、20/60）虽然交易次数少、回撤较小（20/60 仅 -9.77%），'
         '但累计回报均为负值，说明在茅台这种', B),
        ('低波动率蓝筹股', BB),
        ('上，过度延迟的均线难以跟上缓慢的趋势变化，造成长期踏空。', B),
    ])

    # ====== 七、策略对比与总结 ======
    story.append(PageBreak())
    story.append(Paragraph('七、策略对比与适用场景总结', H2))
    story.append(Paragraph('7.1 与买入持有策略的对比', H3))
    add_mixed(story, [
        ('在本次回测中，买入持有策略的累计回报为 -16.02%，年化 -16.62%。'
         '双均线策略（5/15 日）以 -9.51% 的累计回报跑赢了买入持有 6.51 个百分点，'
         '在风险指标上也更优（最大回撤 -14.56% vs 买入持有的全期回撤更大）。'
         '这一结果提示我们：即便双均线策略收益为负，', B),
        ('在下跌趋势中通过死叉空仓规避系统性风险', BB),
        ('，是其相对买入持有的核心优势。', B),
    ])

    story.append(Paragraph('7.2 双均线策略的适用场景', H3))
    add_mixed(story, [
        ('(1) ', B),
        ('趋势性强的市场', BB),
        ('：双均线策略最适合有明确方向的趋势行情，无论是单边上涨还是单边下跌，'
         '都能通过交叉信号捕捉主要波段；', B),
    ])
    add_mixed(story, [
        ('(2) ', B),
        ('波动率较高的标的', BB),
        ('：高波动率带来更多交叉信号，为策略提供更多交易机会；', B),
    ])
    add_mixed(story, [
        ('(3) ', B),
        ('中长期持仓周期', BB),
        ('：本策略不适合日内或超短线交易，更适合以日线为周期、'
         '持仓数周至数月的中长期投资者；', B),
    ])
    add_mixed(story, [
        ('(4) ', B),
        ('蓝筹股/趋势股', BB),
        ('：本报告的回测对象茅台属于低波动蓝筹，参数较敏感，建议谨慎使用，不宜直接照搬。', B),
    ])

    story.append(Paragraph('7.3 策略局限性与实盘应用心得', H3))
    add_mixed(story, [
        ('(1) ', B),
        ('滞后性', BB),
        ('：均线本身是滞后指标，金叉/死叉信号往往在趋势已经走出一段后才出现，'
         '"追涨杀跌"特性明显；', B),
    ])
    add_mixed(story, [
        ('(2) ', B),
        ('震荡市失效', BB),
        ('：在 A 股常见的宽幅震荡行情中，频繁的金叉死叉会带来大量"假信号"和手续费损耗，'
         '本报告茅台的回测中该问题尤为突出；', B),
    ])
    add_mixed(story, [
        ('(3) ', B),
        ('参数过拟合风险', BB),
        ('：网格搜索得到的"最优参数"在样本外未必有效，实盘中应进行样本外测试'
         '（Out-of-Sample Test）和滚动优化；', B),
    ])
    add_mixed(story, [
        ('(4) ', B),
        ('建议改进方向', BB),
        ('：可加入成交量过滤、波动率过滤（如 ATR）、'
         '或与 MACD、布林带等指标组合，构建多因子策略以提升胜率。', B),
    ])

    # ====== 八、结论 ======
    story.append(Paragraph('八、结论', H2))
    story.append(Paragraph(
        '本报告基于贵州茅台 2025-07-04 至 2026-07-03 的日线数据，'
        '完整实现了双均线交叉量化策略，并通过 Python 编程完成回测和绩效分析。'
        '实验表明：(1) 双均线策略概念清晰、实现简单，是入门量化的经典模型；'
        '(2) 5/15 日默认参数下策略累计回报 -9.51%，跑赢买入持有 -16.02%，'
        '体现出"下跌空仓"的优势；(3) 3/10 短周期参数在本期表现最佳（+3.44%），'
        '但需警惕过拟合风险；(4) 双均线策略更适合趋势性行情，'
        '在震荡市中容易失效，实盘应结合过滤条件和仓位管理优化。', B))

    doc.build(story)
    print(f"PDF生成完成: {output_path}")


# ---------------- 入口 ----------------
if __name__ == '__main__':
    import pandas as pd

    OUTPUT_DIR = 'E:/EN_study_tool/BA_task'
    OUTPUT_PDF = f'{OUTPUT_DIR}/郑富彬+TASK3.pdf'

    chart_paths = {
        'main': f'{OUTPUT_DIR}/chart_maotai_strategy.png',
        'equity': f'{OUTPUT_DIR}/chart_maotai_equity.png',
        'heatmap': f'{OUTPUT_DIR}/chart_parameter_heatmap.png',
    }

    if os.path.exists(f'{OUTPUT_DIR}/parameter_results.csv'):
        param_results = pd.read_csv(f'{OUTPUT_DIR}/parameter_results.csv')
    else:
        param_results = pd.DataFrame()

    build_pdf(OUTPUT_PDF, chart_paths, param_results)
