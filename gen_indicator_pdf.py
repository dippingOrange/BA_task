# -*- coding: utf-8 -*-
"""生成技术指标详解 PDF — 宋体五号、1.5倍行距、两端对齐、含图表"""

from fpdf import FPDF
import os

class IndicatorPDF(FPDF):
    BODY_SIZE = 10.5       # 五号
    LINE_H = 5.56          # 1.5倍行距 (mm)
    SMALL = 9
    SUBTITLE = 12
    SECTION = 16

    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        fp = "C:/Windows/Fonts/simsun.ttc"
        if os.path.exists(fp):
            self.add_font("CN", "", fp)
            self.add_font("CN", "B", fp)
            self.cn = "CN"
        else:
            self.cn = "Helvetica"
        self.set_auto_page_break(True, 20)

    def header(self):
        if self.page_no() > 1:
            self.set_font(self.cn, '', 8)
            self.set_text_color(160, 160, 160)
            self.cell(0, 5, '贵州茅台(600519) 技术指标详解', align='C')
            self.ln(7)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.cn, '', 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 8, str(self.page_no()), align='C')

    def cover(self):
        self.add_page()
        self.ln(55)
        self.set_font(self.cn, 'B', 30); self.set_text_color(26, 26, 46)
        self.cell(0, 20, '贵州茅台 (600519.SH)', align='C'); self.ln(24)
        self.set_font(self.cn, 'B', 22); self.set_text_color(192, 57, 43)
        self.cell(0, 16, '技术指标详解', align='C'); self.ln(20)
        self.set_font(self.cn, '', 12); self.set_text_color(120, 120, 120)
        self.cell(0, 10, 'RSI / MACD / 布林带 / KDJ', align='C'); self.ln(30)
        self.set_draw_color(192, 57, 43); self.set_line_width(0.8)
        self.line(65, self.get_y(), 145, self.get_y()); self.ln(20)
        self.set_font(self.cn, '', 11); self.set_text_color(140, 140, 140)
        self.cell(0, 8, '数据区间: 2025-07-04 ~ 2026-07-03 | 242 个交易日', align='C'); self.ln(8)
        self.cell(0, 8, '北大BA工作坊 · 量化交易公益课', align='C')

    def sec(self, title):
        self.ln(6)
        self.set_font(self.cn, 'B', self.SECTION); self.set_text_color(26, 26, 46)
        self.cell(0, 12, title); self.ln(16)

    def sub(self, title):
        self.ln(2)
        self.set_font(self.cn, 'B', self.SUBTITLE); self.set_text_color(44, 62, 80)
        self.cell(0, 10, title); self.ln(11)

    def body(self, text):
        self.set_font(self.cn, '', self.BODY_SIZE); self.set_text_color(51, 51, 51)
        self.multi_cell(self.w - self.l_margin - self.r_margin, self.LINE_H, text, align='J')

    def bullet(self, text, bold_pre=""):
        self.set_font(self.cn, '', self.BODY_SIZE); self.set_text_color(51, 51, 51)
        full = '● ' + bold_pre + text
        self.set_x(self.l_margin + 5)
        w = self.w - self.r_margin - self.get_x()
        self.multi_cell(w, self.LINE_H, full, align='J')
        self.set_x(self.l_margin)

    def img(self, path, w=178):
        if os.path.exists(path):
            self.ln(3)
            self.image(path, x=self.l_margin + 1, w=w)
            self.ln(4)

    def formula_box(self, lines):
        """公式框"""
        self.ln(2)
        y0 = self.get_y()
        h = len(lines) * 6.5 + 8
        self.set_fill_color(248, 248, 250)
        self.rect(self.l_margin, y0, self.w - self.l_margin - self.r_margin, h, 'F')
        self.set_xy(self.l_margin + 6, y0 + 4)
        self.set_font(self.cn, '', self.SMALL); self.set_text_color(60, 60, 80)
        for line in lines:
            self.cell(0, 6.5, line); self.ln(6.5)
            self.set_x(self.l_margin + 6)
        self.set_y(y0 + h + 3)

    def disclaimer(self):
        self.ln(8)
        y0 = self.get_y()
        self.set_fill_color(254, 249, 231)
        self.rect(self.l_margin, y0, self.w - self.l_margin - self.r_margin, 32, 'F')
        self.set_xy(self.l_margin + 5, y0 + 3)
        self.set_font(self.cn, 'B', 9); self.set_text_color(125, 102, 8)
        self.cell(0, 6, '免责声明：')
        self.set_xy(self.l_margin + 5, y0 + 11)
        self.set_font(self.cn, '', 9)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 10, 5,
            '本报告由 AI 自动生成，仅供北京大学BA工作坊量化交易公益课程学习参考。'
            '所有分析和观点均不构成投资建议。股市有风险，投资需谨慎。')
        self.set_y(y0 + 36)

    def ai_tag(self):
        self.ln(5)
        self.set_font(self.cn, '', 9); self.set_text_color(160, 160, 160)
        self.cell(0, 8, '本报告由 AI 自动生成 | 2026-07-04', align='C')


def build():
    pdf = IndicatorPDF()

    # ========== 封面 ==========
    pdf.cover()

    # ========== 引言 ==========
    pdf.sec('引言')
    pdf.body('技术分析（Technical Analysis）是量化交易的重要组成部分，通过研究历史价格和成交量数据，运用数学方法计算各类指标，辅助投资者判断市场趋势、超买超卖状态以及潜在的转折点。')
    pdf.body('本报告以贵州茅台（600519.SH）2025年7月至2026年7月的日线交易数据为基础，详细讲解三个核心技术指标——RSI、MACD、布林带，并扩展介绍KDJ随机指标，包括各自的定义、计算方法和实战解读。')

    # ========== RSI ==========
    pdf.sec('一、RSI — 相对强弱指标')
    pdf.sub('1.1 概述')
    pdf.body('RSI（Relative Strength Index，相对强弱指标）由 J. Welles Wilder 于1978年在《New Concepts in Technical Trading Systems》一书中提出，是技术分析领域最经典且应用最广的指标之一。RSI 通过比较一段时期内价格上涨幅度与下跌幅度的比值，来衡量价格变动的内在强度，从而判断市场是否处于"超买"或"超卖"状态。')
    pdf.body('核心思想：如果一段时间内上涨的天数多且涨幅大，说明买方力量强劲（RSI偏高）；反之则卖方占优（RSI偏低）。RSI 取值范围为 0-100。')

    pdf.sub('1.2 计算方法')
    pdf.body('RSI 的标准计算周期为 14 日，采用 Wilder 递推平滑算法（而非简单移动平均），以保证指标的光滑性和稳定性。')
    pdf.formula_box([
        '第1步: 计算每日涨跌幅 delta = Close(t) - Close(t-1)',
        '第2步: 分离上涨与下跌: gain = max(delta, 0),  loss = max(-delta, 0)',
        '第3步: 初次平均:  AvgGain(14) = 前14日gain均值,  AvgLoss(14) = 前14日loss均值',
        '第4步: 递推平滑:  AvgGain(t) = [AvgGain(t-1)*13 + gain(t)] / 14',
        '                     AvgLoss(t) = [AvgLoss(t-1)*13 + loss(t)] / 14',
        '第5步: RS = AvgGain / AvgLoss',
        '第6步: RSI = 100 - [100 / (1 + RS)]',
    ])

    pdf.sub('1.3 使用规则')
    pdf.bullet('当 RSI > 70 时，市场处于"超买"状态，短期内价格可能面临回调压力。', '超买信号：')
    pdf.bullet('当 RSI < 30 时，市场处于"超卖"状态，短期内价格可能存在反弹机会。', '超卖信号：')
    pdf.bullet('RSI 在 50 附近波动，表示多空力量均衡；RSI 上穿 50 意味买方占优，下穿 50 意味卖方占优。', '中线分界：')
    pdf.bullet('当价格创新高而 RSI 未能同步创新高时，形成"顶背离"，预示上涨动能衰竭、可能见顶回落。当价格创新低而 RSI 未同步创新低时，形成"底背离"，预示下跌动能减弱、可能见底回升。', '背离信号：')

    pdf.sub('1.4 贵州茅台 RSI 实战分析')
    pdf.body('下图展示了贵州茅台过去一年的 RSI(14) 走势。从图中可以看出，RSI 在 2026 年 1 月底至 2 月初一度进入 70 以上的超买区域（对应股价快速拉升到 ¥1555 的阶段），此后 RSI 持续走低，目前位于 37.5 的中性偏低水平。值得注意的是，6 月下旬股价创出新低 ¥1168.63 时，RSI 并未同步创出新低，呈现出"底背离"的雏形，暗示下跌动能可能正在衰竭。')
    pdf.img("chart_rsi.png", 180)

    # ========== MACD ==========
    pdf.sec('二、MACD — 指数平滑异同移动平均线')
    pdf.sub('2.1 概述')
    pdf.body('MACD（Moving Average Convergence Divergence）由 Gerald Appel 于 1979 年提出，是最受欢迎的趋势跟踪指标之一。MACD 通过两条不同周期的指数移动平均线（EMA）的差值来揭示价格趋势的变化速度和方向，兼顾了趋势跟踪和动量分析的双重功能。')
    pdf.body('MACD 由三个组成部分构成：DIF（快线）、DEA（慢线/信号线）和 MACD 柱状图（柱线）。三者配合使用可以判断趋势方向、力度变化以及买卖时机。')

    pdf.sub('2.2 计算方法')
    pdf.body('标准参数为 (12, 26, 9)，即快线周期 12 日、慢线周期 26 日、信号线周期 9 日。')
    pdf.formula_box([
        'EMA12 = 收盘价的 12 日指数加权移动平均',
        'EMA26 = 收盘价的 26 日指数加权移动平均',
        'DIF (快线) = EMA12 - EMA26',
        'DEA (慢线/信号线) = DIF 的 9 日 EMA',
        'MACD 柱 = 2 × (DIF - DEA)   （柱线高度反映 DIF 与 DEA 的偏离程度）',
    ])

    pdf.sub('2.3 使用规则')
    pdf.bullet('当 DIF 线从下方上穿 DEA 线时，形成"金叉"，是买入信号。当 DIF 从上方下穿 DEA 时，形成"死叉"，是卖出信号。', '金叉与死叉：')
    pdf.bullet('DIF 和 DEA 在零轴上方运行，表示市场处于多头格局；在零轴下方运行，表示空头格局。零轴下方的金叉力度弱于零轴上方的金叉。', '零轴分界：')
    pdf.bullet('MACD 柱由负转正（红色转绿色），说明多头动能增强；由正转负，说明空头动能增强。柱线高度的变化速度反映趋势加速度。', '柱线变化：')
    pdf.bullet('当价格创新高而 DIF 未同步创新高，为顶背离，预示可能见顶；价格创新低而 DIF 未同步创新低，为底背离，预示可能见底。', '背离信号：')

    pdf.sub('2.4 贵州茅台 MACD 实战分析')
    pdf.body('从下图的 MACD 走势来看，DIF 和 DEA 自 2026 年 2 月以来持续运行在零轴下方，属于典型的空头格局。值得关注的是，7 月初 MACD 柱由负转正，DIF 开始向 DEA 靠拢，出现了弱势区域的金叉雏形。不过，由于 DIF/DEA 均在零轴下方较远位置（约 -32），这个金叉的可靠性有限，需要后续持续放量确认。同时，6 月底股价创出新低时 MACD 柱的低点明显抬高，形成了底背离信号。')
    pdf.img("chart_macd.png", 180)

    # ========== 布林带 ==========
    pdf.sec('三、布林带 — Bollinger Bands')
    pdf.sub('3.1 概述')
    pdf.body('布林带（Bollinger Bands）由 John Bollinger 于 1980 年代创立，是一种基于统计学原理的波动率指标。布林带由三条轨道组成：中轨是简单移动平均线（通常为 20 日均线），上轨和下轨分别在中轨的基础上加减一定倍数的标准差（通常为 2 倍）。')
    pdf.body('布林带的核心思想是：在统计学中，价格数据近似服从正态分布，约有 95% 的价格会落在均值 ± 2 倍标准差的区间内。因此，当价格触及或突破上下轨时，属于统计上的"小概率事件"，往往意味着价格可能向中轨回归。')

    pdf.sub('3.2 计算方法')
    pdf.body('标准参数为 (20, 2)，即 20 日均线 ± 2 倍标准差。')
    pdf.formula_box([
        '中轨 (Middle) = MA20 = 20 日简单移动平均',
        '上轨 (Upper)  = MA20 + 2 × σ   （σ 为 20 日收盘价标准差）',
        '下轨 (Lower)  = MA20 - 2 × σ',
        '带宽 (Width)  = (上轨 - 下轨) / 中轨 × 100%   （衡量波动率）',
    ])

    pdf.sub('3.3 使用规则')
    pdf.bullet('价格沿上轨运行，说明处于强势上涨通道；价格沿下轨运行，说明处于弱势下跌通道。正常行情中价格在上下轨之间波动。', '趋势判断：')
    pdf.bullet('当带宽明显收窄（如 < 8%）时，表明市场波动率极低，多空力量高度胶着，往往是"暴风雨前的宁静"，预示即将出现方向性突破。', '"Squeeze" 变盘信号：')
    pdf.bullet('价格触及上轨后可能回落，触及下轨后可能反弹。但需注意：在强趋势行情中，价格可以沿轨道持续运行（"walking the band"），不能简单逆势操作。', '超买超卖：')
    pdf.bullet('当带宽持续扩大时，表明波动率上升，趋势可能加速；当带宽从高位回落时，趋势可能进入休整阶段。', '带宽变化：')

    pdf.sub('3.4 贵州茅台布林带实战分析')
    pdf.body('从下图可以看出，贵州茅台自 2026 年 2 月见顶以来，股价持续运行在布林带中轨下方，说明处于弱势下跌通道。进入 6 月下旬后，股价在逼近下轨 ¥1158 后出现企稳迹象，布林带带宽从 14% 收窄至 12%，波动率有所降低。当前收盘价 ¥1194.45 位于中下轨之间，距离下轨约 3% 的空间，距离中轨 ¥1232 约 3.2%。若后续能放量站上中轨，则可能意味趋势反转的信号。')
    pdf.img("chart_bollinger.png", 180)

    # ========== 扩展指标 ==========
    pdf.sec('四、技术指标扩展')
    pdf.sub('4.1 其他常用技术指标概览')
    pdf.body('除了前述的 RSI、MACD 和布林带三大经典指标外，技术分析领域还有众多实用指标，各有侧重：')
    pdf.bullet('由 George Lane 提出，通过比较收盘价在最近 N 日最高最低价区间中的位置来判断超买超卖。在中国 A 股市场中应用极广，由 K、D、J 三条线构成，J 值最为敏感。', 'KDJ（随机指标）：')
    pdf.bullet('能量潮指标，以成交量累加的方式判断资金流向。OBV 上升表示买盘积极，OBV 下降表示卖盘占优。常用于验证价格趋势的有效性。', 'OBV（能量潮）：')
    pdf.bullet('衡量价格的平均波动幅度，不判断方向只衡量烈度。常用于设定止盈止损位——止损距离 = ATR × 倍数。', 'ATR（平均真实波幅）：')
    pdf.bullet('由 Larry Williams 提出，与 KDJ 原理类似但计算更简洁，取值范围 -100 到 0，-20 以上为超买，-80 以下为超卖。', 'WR（威廉指标）：')
    pdf.bullet('衡量收盘价偏离移动平均线的百分比，正值表示价格高于均线（多头），负值表示低于均线（空头）。极端乖离率往往预示均值回归。', 'BIAS（乖离率）：')

    pdf.sub('4.2 重点扩展：KDJ 随机指标详解')
    pdf.body('KDJ 指标（Stochastic Oscillator）由 George Lane 于 1950 年代提出，其核心思想是：在上升趋势中，收盘价倾向于接近当日最高价；在下降趋势中，收盘价倾向于接近当日最低价。KDJ 通过计算当日收盘价在最近 N 日价格区间中的相对位置，来判断趋势的强度和转折点。')

    pdf.sub('4.3 KDJ 计算方法')
    pdf.body('KDJ 标准参数为 (9, 3, 3)，即计算周期为 9 日，K 和 D 的平滑因子各为 1/3。计算过程分为三步：')
    pdf.formula_box([
        '第1步 计算 RSV (未成熟随机值):',
        '  RSV = (收盘价 - 9日最低价) / (9日最高价 - 9日最低价) × 100',
        '',
        '第2步 递推计算 K 和 D (初始值取 50):',
        '  K(t) = 2/3 × K(t-1) + 1/3 × RSV(t)',
        '  D(t) = 2/3 × D(t-1) + 1/3 × K(t)',
        '',
        '第3步 计算 J 值:',
        '  J = 3 × K - 2 × D   （J 值反应更灵敏，可超过 100 或低于 0）',
    ])

    pdf.sub('4.4 KDJ 使用规则')
    pdf.bullet('K、D 值超过 80 为超买区，低于 20 为超卖区。J 值超过 100 为严重超买，低于 0 为严重超卖。', '超买超卖：')
    pdf.bullet('当 K 线从下方上穿 D 线时形成"金叉"（买入信号），当 K 线从上方下穿 D 线时形成"死叉"（卖出信号）。在 20 以下的金叉和 80 以上的死叉信号更为可靠。', '金叉死叉：')
    pdf.bullet('J 值是 KDJ 三线中最为灵敏的一条，常率先发出信号。当 J 值从 0 以下回升上穿 0，是短线买入信号；当 J 值从 100 以上回落跌破 100，是短线卖出信号。', 'J 值特殊用法：')
    pdf.bullet('KDJ 在单边趋势中容易钝化（持续在超买/超卖区），此时应结合趋势类指标（如 MACD、均线）综合判断，不可机械使用。', '钝化现象：')

    pdf.sub('4.5 贵州茅台 KDJ 实战分析')
    pdf.body('从下图的 KDJ 走势分析，过去一年中 KDJ 指标提供了多个有效的买卖信号。2026 年 1 月底 J 值一度飙升到 100 以上极端超买区域，随后股价在 2 月初见顶 ¥1555。进入 6 月后，K、D、J 三线在 20 附近的超卖区域运行较长时间（钝化），反映市场持续弱势。截至 7 月 3 日，K=35.4、D=29.0、J=48.0，三线从超卖区回升但尚未形成明确的低位金叉，继续等待信号确认。')
    pdf.img("chart_kdj.png", 180)

    # ========== 总结 ==========
    pdf.sec('五、总结')
    pdf.body('本报告以贵州茅台（600519.SH）的真实交易数据为基础，系统介绍了技术分析中最核心的四个指标：RSI、MACD、布林带和 KDJ。每个指标都有其独特的视角和适用场景：')
    pdf.bullet('侧重衡量价格变动的内在力度，判断超买超卖和背离信号，适合震荡市。', 'RSI：')
    pdf.bullet('侧重跟踪趋势方向和动能变化，金叉死叉是重要的买卖参考，适合趋势市。', 'MACD：')
    pdf.bullet('基于统计学原理，用标准差衡量波动区间，"Squeeze" 收窄是变盘的重要预警。', '布林带：')
    pdf.bullet('源自收盘价相对位置的思想，三线配合使用灵敏度高，在 A 股市场应用极广。', 'KDJ：')
    pdf.body('在实际量化交易中，单一指标往往不足以做出准确判断。建议将多个指标结合起来使用——例如：当 RSI 显示底背离、MACD 出现金叉、布林带收窄且股价站上中轨、KDJ 在低位金叉时，多个信号的共振可以显著提高判断的可靠性。技术指标是工具，而非"圣杯"，理性使用、综合判断才是量化交易的正道。')

    # ========== 结尾 ==========
    pdf.disclaimer()
    pdf.ai_tag()

    pdf.output("贵州茅台_600519_技术指标详解报告.pdf")
    print("PDF 已生成: 贵州茅台_600519_技术指标详解报告.pdf")

if __name__ == "__main__":
    build()
