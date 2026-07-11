# -*- coding: utf-8 -*-
"""海龟交易策略研究报告 PDF — 宋体五号 · 1.5倍行距"""
from fpdf import FPDF
import os, csv

class ReportPDF(FPDF):
    BODY_SIZE = 10.5; LINE_H = 5.56; SMALL = 9; SUBTITLE_SIZE = 12; SECTION_SIZE = 16

    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        skills = "E:/EN_study_tool/BA_task/.workbuddy/skills/fpdf2-chinese-pdf/fonts"
        self.add_font("CN", "", f"{skills}/simsun.ttf")
        self.add_font("CN", "B", f"{skills}/simhei.ttf")
        self.cn = "CN"
        self.set_auto_page_break(True, 20)

    def header(self):
        if self.page_no() > 1:
            self.set_font(self.cn, '', 8); self.set_text_color(160,160,160)
            self.cell(0,5,'贵州茅台(600519) 海龟交易策略研究报告',align='C'); self.ln(7)

    def footer(self):
        self.set_y(-15); self.set_font(self.cn, '', 8); self.set_text_color(160,160,160)
        self.cell(0,8,str(self.page_no()),align='C')

    def cover(self):  # 统一封面
        self.add_page(); self.ln(55)
        self.set_font(self.cn,'B',30); self.set_text_color(26,26,46)
        self.cell(0,20,'贵州茅台 (600519.SH)',align='C'); self.ln(24)
        self.set_font(self.cn,'B',22); self.set_text_color(192,57,43)
        self.cell(0,16,'海龟交易策略研究报告',align='C'); self.ln(20)
        self.set_font(self.cn,'',12); self.set_text_color(120,120,120)
        self.cell(0,10,'Donchian通道 · ATR止损 · 头寸管理',align='C'); self.ln(30)
        self.set_draw_color(192,57,43); self.set_line_width(0.8)
        self.line(65,self.get_y(),145,self.get_y()); self.ln(20)
        self.set_font(self.cn,'',11); self.set_text_color(140,140,140)
        self.cell(0,8,'数据区间: 2025-07-04 ~ 2026-07-03 | 242 个交易日',align='C'); self.ln(8)
        self.cell(0,8,'北大BA工作坊 · 量化交易公益课',align='C')

    def sec(self, title):
        self.ln(6); self.set_font(self.cn,'B',self.SECTION_SIZE); self.set_text_color(26,26,46)
        self.cell(0,12,title); self.ln(16)

    def sub(self, title):
        self.ln(2); self.set_font(self.cn,'B',self.SUBTITLE_SIZE); self.set_text_color(44,62,80)
        self.cell(0,10,title); self.ln(11)

    def _wrap_text(self, text, max_w, first_line_indent=0):
        self.set_x(self.l_margin + first_line_indent)
        line = ''; first_char = True
        for ch in text:
            test = line + ch
            if self.get_string_width(test) > max_w - first_line_indent and not first_char:
                self.cell(max_w, self.LINE_H, line, align='L')
                self.ln(self.LINE_H); self.set_x(self.l_margin)
                line = ch; first_char = False
            else:
                line = test; first_char = False
        if line:
            self.cell(max_w, self.LINE_H, line, align='L'); self.ln(self.LINE_H)
        self.set_x(self.l_margin)

    def body(self, text):
        self.set_font(self.cn,'',self.BODY_SIZE); self.set_text_color(51,51,51)
        max_w = self.w - self.l_margin - self.r_margin
        for para in text.split('\n'):
            if para.strip(): self._wrap_text(para, max_w)
            else: self.ln(self.LINE_H)

    def bullet(self, text, bold_prefix=""):
        self.set_font(self.cn,'',self.BODY_SIZE); self.set_text_color(51,51,51)
        max_w = self.w - self.l_margin - self.r_margin - 5
        self._wrap_text('● ' + bold_prefix + text, max_w, first_line_indent=5)

    def formula_box(self, lines):
        self.ln(2); y0 = self.get_y()
        h = len(lines)*6.5 + 8
        self.set_fill_color(248,248,250)
        self.rect(self.l_margin, y0, self.w-self.l_margin-self.r_margin, h, 'F')
        self.set_xy(self.l_margin+6, y0+4)
        self.set_font(self.cn,'',self.SMALL); self.set_text_color(60,60,80)
        for line in lines:
            self.cell(0,6.5,line); self.ln(6.5); self.set_x(self.l_margin+6)
        self.set_y(y0+h+3)

    def write_table(self, headers, rows, col_widths=None):
        line_h = 7.5; full_w = self.w - self.l_margin - self.r_margin
        if col_widths is None: col_widths = [full_w/len(headers)]*len(headers)
        total_w = sum(col_widths)
        self.ln(2); self.set_fill_color(230,230,235)
        self.set_font(self.cn,'B',self.BODY_SIZE); self.set_text_color(44,62,80)
        self.set_x(self.l_margin)
        for i,h in enumerate(headers):
            self.cell(col_widths[i]/total_w*full_w, line_h, h, border=0, fill=True, align='C')
        self.ln(line_h)
        self.set_font(self.cn,'',self.BODY_SIZE); self.set_text_color(51,51,51)
        for ri,row in enumerate(rows):
            bg = (245,245,250) if ri%2==0 else (255,255,255)
            self.set_fill_color(*bg); self.set_x(self.l_margin)
            for i,val in enumerate(row):
                self.cell(col_widths[i]/total_w*full_w, line_h, str(val), border=0, fill=True, align='C')
            self.ln(line_h)
        self.ln(3)

    def img(self, path, w=178):
        if os.path.exists(path): self.ln(3); self.image(path, x=self.l_margin+1, w=w); self.ln(4)

    def disclaimer(self):
        self.ln(8); y0=self.get_y()
        self.set_fill_color(254,249,231)
        self.rect(self.l_margin, y0, self.w-self.l_margin-self.r_margin, 32, 'F')
        self.set_xy(self.l_margin+5, y0+3); self.set_font(self.cn,'B',9); self.set_text_color(125,102,8)
        self.cell(0,6,'免责声明：')
        self.set_xy(self.l_margin+5, y0+11); self.set_font(self.cn,'',9)
        self.multi_cell(self.w-self.l_margin-self.r_margin-10, 5,
            '本报告由 AI 自动生成，仅供北京大学BA工作坊量化交易公益课程学习参考。'
            '所有分析和观点均不构成投资建议。股市有风险，投资需谨慎。')
        self.set_y(y0+36)

    def ai_tag(self):
        self.ln(5); self.set_font(self.cn,'',9); self.set_text_color(160,160,160)
        self.cell(0,8,'本报告由 AI 自动生成 | 2026-07-11',align='C')


def build():
    pdf = ReportPDF()
    pdf.cover()

    # ====== 一 ======
    pdf.sec('一、海龟交易策略概述')
    pdf.sub('1.1 策略起源与核心思想')
    pdf.body('海龟交易法则（Turtle Trading System）诞生于1983年，由传奇商品交易员理查德·丹尼斯（Richard Dennis）和威廉·埃克哈特（William Eckhardt）共同创立。丹尼斯坚信交易能力可以通过系统化训练获得，于是招募了一批毫无交易经验的新手，传授一套完整的机械交易规则，这群学员后来被称为"海龟"（Turtles）。')
    pdf.body('海龟法则的核心思想可以概括为：以趋势跟踪为基础，用客观量化的规则取代主观判断。策略不预测市场方向，而是被动地"跟随"趋势——当价格突破近期高点时入场做多，当价格跌破近期低点时离场。其哲学根基是：市场价格的重大波动往往以趋势形式展开，只要能在趋势的早中期介入并坚持持有，少数几笔大盈利就足以覆盖大量小亏损。')
    pdf.body('海龟策略之所以在量化交易史上占据里程碑地位，是因为它完整地构建了一套端到端的交易系统，包括：何时入场、交易多少、何时止损、何时离场——每一个环节都由明确的数学公式定义，没有任何模糊地带。')

    pdf.sub('1.2 海龟策略的核心优势')
    pdf.bullet('海龟法则的所有规则——入场、离场、头寸、止损——都无需主观判断，实现了100%的系统化和可重复性。这是机器学习、回测优化等现代量化手段得以应用的前提。', '完全机械化：')
    pdf.bullet('通过ATR（平均真实波幅）来动态调整头寸规模和止损距离，使得策略能自动适配不同波动率的市场和不同价格区间的标的。波动大时头寸小、止损宽；波动小时头寸大、止损窄。', '自适应风险管理：')
    pdf.bullet('利用Donchian通道（N日最高/最低价）作为趋势突破的判定标准，能有效捕捉中大型趋势的早期阶段，不会因为短期噪音而频繁进出。', '趋势捕捉能力强：')
    pdf.bullet('策略在大多数时间里空仓等待，只在趋势信号明确时才入场。这种"低频交易"风格天然地降低了交易成本和情绪损耗。', '交易频率低：')
    pdf.bullet('丹尼斯将海龟法则公之于众后，策略逻辑被无数交易者反复检验，其核心框架经受住了不同市场和时代的考验，至今仍是趋势跟踪领域的经典教科书。', '经得起历史检验：')

    # ====== 二 ======
    pdf.sec('二、海龟策略核心概念详解')
    pdf.sub('2.1 Donchian 通道 —— 趋势突破的判定标准')
    pdf.body('Donchian通道（Donchian Channel）由理查德·唐奇安（Richard Donchian）创立，是海龟策略中判断趋势方向的唯一依据。与均线交叉策略不同，Donchian 通道不依赖价格的平滑处理，而是直接观察价格是否"突破"了过去一段时间的高点或低点，信号更为直接和客观。')
    pdf.formula_box([
        '上轨 (入场信号): Upper = max(High_t-N+1, ..., High_t)',
        '               即：过去 N 日的最高价',
        '下轨 (离场信号): Lower = min(Low_t-M+1, ..., Low_t)',
        '               即：过去 M 日的最低价',
        '',
        '海龟 System 1: 入场 N=20  离场 M=10',
        '海龟 System 2: 入场 N=55  离场 M=20',
    ])
    pdf.body('当今日开盘价突破昨日收盘时的通道上轨，即触发买入信号。这意味着当前价格已经超越了最近N日内的所有最高价——市场出现了"创新高"的强势特征，极有可能是新一轮上涨趋势的起点。反之，当开盘价跌破离场通道下轨时，意味着趋势可能已经终结。')
    pdf.body('System 1（20日突破）更为灵敏，能更快捕捉趋势变化；System 2（55日突破）更为稳健，适合捕捉更大级别的趋势，但信号出现频率更低。海龟交易员通常同时运行两个系统，以不同的时间尺度覆盖市场。')

    pdf.sub('2.2 ATR —— 平均真实波幅')
    pdf.body('ATR（Average True Range，平均真实波幅）由威尔斯·威尔德（J. Welles Wilder）提出，用于量化市场的波动程度。在海龟策略中，ATR 扮演着头寸计算器和止损标尺的双重角色。')
    pdf.body('ATR 的"真实波幅"考虑了三种情况：当日最高到最低的振幅、当日最高到昨日收盘的跳空幅度、当日最低到昨日收盘的跳空幅度。取三者的最大值作为当日真实波幅，再对 N 日取平均，得到 ATR。')
    pdf.formula_box([
        'True Range (TR) = max(',
        '    High - Low,              // 当日振幅',
        '    |High - PrevClose|,      // 跳空高开幅度',
        '    |Low - PrevClose|        // 跳空低开幅度',
        ')',
        'ATR(N) = TR 的 N 日简单移动平均',
        '海龟默认: N = 20',
    ])
    pdf.body('ATR 的单位是"元"（或点），数值越大说明近期市场波动越剧烈。海龟策略中 ATR 的两个核心用途：（1）头寸规模 = 账户资金的1% ÷ ATR，波动大时自动缩小头寸；（2）硬止损 = 入场价 - 2×ATR，保证每笔交易的最大损失控制在账户的2%以内。')

    pdf.sub('2.3 止损与头寸管理')
    pdf.body('海龟策略的止损是刚性的——2倍ATR硬止损，没有"再看看"或"感觉会反弹"的余地。这是海龟法则区别于主观交易最核心的特征之一。当价格触及止损位时，无论对后市多么看好，都必须立即离场。这种纪律性确保了：任何单笔交易的最大亏损不会超过账户总资金的2%，从制度上杜绝了"扛单死扛"的风险。')
    pdf.body('头寸管理方面，海龟法则采用基于ATR的动态计算：单位风险 = 账户资金的1%；头寸规模 = 单位风险 ÷ ATR。例如：100万账户，1%风险 = 1万元；若ATR = 30元，则每笔交易最多买入 10,000÷30÷100 ≈ 300股。')
    pdf.formula_box([
        '单位风险 (Unit Risk) = 账户资金 × 1%',
        '头寸规模 (Shares) = Unit Risk ÷ ATR(20)',
        '  → 取整百股，最少100股',
        '',
        '硬止损价格 = 入场价 - 2 × ATR',
        '最大亏损控制 = 头寸规模 × 2 × ATR ≈ 账户资金的 2%',
    ])

    # ====== 三 ======
    pdf.sub('2.4 海龟策略的完整交易流程')
    pdf.body('综合以上各组件，海龟策略的完整交易流程如下：(1) 每个交易日盘前计算Donchian通道上下轨和ATR；(2) 若开盘价突破通道上轨且当前无持仓，按1%风险公式计算头寸，市价买入；(3) 若已有持仓且开盘价跌破离场通道下轨（或触及2×ATR止损），立即清仓；(4) 加仓规则：入场后每上涨0.5×ATR追加一次头寸，最多4次；(5) 空仓等待下一个信号。')

    pdf.sec('三、Python编程实现')
    pdf.sub('3.1 数据加载与预处理')
    pdf.body('读取工作目录下的"贵州茅台_600519_日线数据.csv"，解析交易日期并升序排列。数据包含242个交易日，覆盖2025年7月4日至2026年7月3日，字段包括开盘价、最高价、最低价、收盘价、成交量等。')
    pdf.sub('3.2 Donchian通道与ATR计算')
    pdf.body('Donchian通道上轨 = 过去20日最高价的滚动最大值（rolling max），下轨 = 过去10日最低价的滚动最小值（rolling min）。ATR = 真实波幅(TR)的20日简单移动平均。')
    pdf.body('买入信号：当日开盘价 > 昨日通道上轨 → 价格突破 → 入场做多。卖出信号：当日开盘价 < 离场通道下轨 → 趋势终结 → 清仓离场。同时盘中实时检查是否触及2×ATR止损线。')
    pdf.sub('3.3 模拟交易与回测假设')
    pdf.body('回测参数：初始资金100万元，单向佣金万三，T+1信号次日开盘价执行，头寸按1%风险+ATR动态计算。每日记录现金+持仓市值，构成资金曲线。')

    # ====== 四 ======
    pdf.sec('四、回测结果与绩效分析')
    pdf.sub('4.1 核心绩效指标（System 1: 20/10日）')

    pdf.write_table(
        ['指标', '数值'],
        [['初始资金','1,000,000.00 元'],['最终资金','970,830.00 元'],
         ['累计回报','-2.92%'],['年化收益率','-3.04%'],
         ['最大回撤 (MDD)','-5.43%'],['夏普比率','-1.33'],
         ['日胜率','5.39%'],['总交易次数','4 笔 (2买+2卖)']]
    )

    pdf.body('System 1 在回测期内仅触发了4笔交易（2次入场+2次离场）。累计回报-2.92%，虽然为负值，但远优于同期买入持有的-16.02%，超额收益达到+13.1个百分点。最大回撤仅-5.43%，远小于买入持有的全期最大回撤，风险控制效果显著。')
    pdf.body('交易次数极少（仅4笔）体现了海龟策略"宁缺毋滥"的本质：在茅台这种震荡偏弱行情中，Donchian通道大部分时间走平或收窄，只有2025年8月和2026年2月两波反弹才触发入场信号，其余时间策略始终空仓，完美规避了后续的大幅下跌。')

    pdf.sub('4.2 交易明细')
    pdf.write_table(
        ['日期','类型','价格(元)','数量(股)','金额(元)'],
        [['2025-08-25','突破入场','1,470.00','500','735,000'],
         ['2025-09-24','突破离场','1,434.10','500','717,050'],
         ['2026-02-04','突破入场','1,485.00','300','445,500'],
         ['2026-03-02','突破离场','1,450.00','300','435,000']]
    )

    pdf.img("E:/EN_study_tool/BA_task/chart_turtle_strategy.png", 178)
    pdf.body('图 1  贵州茅台（600519.SH）海龟策略示意图（System 1: 20/10日）')
    pdf.body('（注：红色▲为突破入场信号，绿色▼为突破离场信号。红色虚线为20日通道上轨，绿色虚线为10日通道下轨。下方为持仓区间标注。）')

    pdf.img("E:/EN_study_tool/BA_task/chart_turtle_equity.png", 178)
    pdf.body('图 2  策略净值曲线 vs 买入持有基准')
    pdf.body('（注：上图为累计净值对比，红色实线为海龟策略，蓝色虚线为买入持有；下图为策略回撤曲线。）')

    pdf.sub('4.3 与买入持有策略的对比')
    pdf.body('买入持有策略同期累计回报-16.02%，海龟策略-2.92%，策略超额收益+13.1%。更关键的是风险控制：买入持有可能经历超过24%的区间回撤，而海龟策略的最大回撤仅-5.43%。这一差异的核心在于：买入持有在下跌趋势中没有任何保护措施，而海龟策略通过Donchian通道离场信号和ATR止损，在趋势转弱后迅速空仓，避免参与主跌浪。')

    # ====== 五 ======
    pdf.sec('五、参数敏感性分析')
    pdf.sub('5.1 参数网格搜索')

    rows = []
    with open('E:/EN_study_tool/BA_task/turtle_param_results.csv', 'r', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            rows.append([r['入场周期'], r['离场周期'],
                        f"{float(r['累计回报 (%)']):.1f}", f"{float(r['最大回撤 (%)']):.1f}",
                        f"{float(r['夏普比率']):.1f}", r['交易次数']])

    pdf.write_table(['入场','离场','累计回报(%)','最大回撤(%)','夏普比率','交易次数'], rows,
                    [20,20,30,30,25,20])

    pdf.sub('5.2 热力图分析')
    pdf.img("E:/EN_study_tool/BA_task/chart_turtle_heatmap.png", 178)
    pdf.body('图 3  海龟策略参数网格搜索绩效热力图')

    pdf.body('从8组参数组合的实验结果来看：(1) 入场周期30日+离场周期10日的组合表现最优，累计回报-1.08%，最大回撤仅-3.10%，仅触发2笔交易；(2) 入场周期越长，信号越少，但单笔信号质量越高——55日入口未见信号，说明过去一年茅台从未出现"55日创新高"级别的强势突破；(3) 入场周期过短（如10/5）反而容易产生假突破信号，累计回报-6.54%，回撤-8.95%。(4) 整体来看，海龟策略在茅台这种低波动蓝筹上更偏向"少交易、防回撤"的保守风格，参数越长越稳健。')

    # ====== 六 ======
    pdf.sec('六、策略对比与适用场景总结')
    pdf.sub('6.1 海龟策略 vs 双均线策略 vs 买入持有')

    pdf.write_table(
        ['对比维度','海龟策略(20/10)','双均线(5/15)','买入持有'],
        [['累计回报','-2.92%','-9.51%','-16.02%'],
         ['最大回撤','-5.43%','-14.56%','-24.8%'],
         ['交易次数','4笔','18笔','0笔'],
         ['夏普比率','-1.33','-1.15','N/A'],
         ['信号类型','价格突破','均线交叉','无'],
         ['止损机制','2×ATR硬止损','无','无']]
    )

    pdf.body('海龟策略在累计回报和回撤控制上均显著优于双均线策略和买入持有。核心差异在于：海龟策略有ATR止损保护 + Donchian通道只在高确定性位置入场，交易次数极少但胜在质量。双均线策略信号更频繁但假信号多、无止损保护，在震荡市中反复"被摩擦"。')

    pdf.sub('6.2 海龟策略的适用场景')
    pdf.bullet('当市场出现持续的单边上行趋势时（如2019-2020年的茅台），海龟策略能在趋势早期入场并持有较长时间，捕获主要涨幅。以茅台此次回测为例，若在2020年的牛市中运行海龟策略，20日突破信号将带来可观的趋势收益。', '强趋势市场：')
    pdf.bullet('ATR值较高的股票（如小盘成长股、科技股）波动剧烈，海龟策略的ATR自适应头寸和止损机制能有效管理风险，高波动也为趋势突破提供了更清晰的信号。', '高波动标的：')
    pdf.bullet('海龟策略天然适合周线或日线级别操作，信号出现频率低、持仓时间长，不适合日内高频交易。', '中长期交易：')
    pdf.bullet('同时交易多个不相关标的时，海龟策略的趋势跟踪特性可以通过分散化平滑资金曲线，提高整体夏普比率。', '多品种组合：')

    pdf.sub('6.3 海龟策略的局限性')
    pdf.bullet('在茅台2025-2026年的这种震荡偏弱行情中，海龟策略大部分时间空仓，虽然保护了本金但也意味着无法通过逆势交易获利。这是所有趋势跟踪策略的共性——在震荡市里注定"无所作为"。', '震荡市无效：')
    pdf.bullet('Donchian通道突破往往在趋势已经运行了一段时间后才触发，入场时可能已经错过了趋势的前1/3甚至更多。这是"趋势跟踪"的固有代价。', '入场滞后：')
    pdf.bullet('海龟原版参数（20/10, 55/20）是根据1980年代美国期货市场设计的，直接照搬到A股或不同周期可能不是最优的，需要进行适应性测试。', '参数敏感：')

    pdf.sub('6.4 实盘应用建议')
    pdf.body('（1）建议同时运行System 1（20/10）和System 2（55/20），形成互补——短周期捕捉中级趋势，长周期捕捉大级别行情；（2）A股T+1和涨跌停制度会影响海龟策略的止损执行，实盘需预留滑点余量，建议将止损倍数从2倍提高到2.5-3倍ATR；（3）可加入成交量或波动率过滤条件，在缩量横盘时禁用入场信号，减少震荡市中的假突破损耗；（4）多品种分散是关键——海龟策略在5-10个不相关标的上同时运行，才能发挥其真正的威力。')

    # ====== 七 ======
    pdf.sec('七、结论')
    pdf.body('本报告以贵州茅台2025-2026年的日线数据为基础，完整实现了海龟交易法则的System 1（20/10日突破），并通过参数网格搜索进行了系统性对比。实验表明：（1）海龟策略-2.92%的回报远超买入持有的-16.02%，最大回撤仅-5.43%，风险控制能力突出；（2）交易频率极低（仅4笔），天然适合中长期趋势跟踪；（3）30/10日参数组合最优（-1.08%），且入场周期越长策略越稳健；（4）海龟法则的核心价值不在于单只股票的短期收益，而在于通过机械化规则+多品种分散，构建一个长期正期望值的交易系统。')

    pdf.disclaimer()
    pdf.ai_tag()
    pdf.output("E:/EN_study_tool/BA_task/郑富彬+TASK4.pdf")
    print("PDF 已生成: E:/EN_study_tool/BA_task/郑富彬+TASK4.pdf")

if __name__ == '__main__':
    build()
