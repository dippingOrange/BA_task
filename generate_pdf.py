# -*- coding: utf-8 -*-
"""
将 HTML 报告转换为 PDF，使用 fpdf2
"""

from fpdf import FPDF
import re
from html.parser import HTMLParser
import os

class HTMLToPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        # 尝试加载中文字体
        font_paths = [
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/msyhbd.ttc",
        ]
        self.cn_font = None
        for fp in font_paths:
            if os.path.exists(fp):
                self.add_font("CN", "", fp, uni=True)
                self.add_font("CN", "B", fp, uni=True)
                self.cn_font = "CN"
                print(f"使用字体: {fp}")
                break
        
        if not self.cn_font:
            print("警告: 未找到中文字体文件，PDF 中中文可能无法显示")
            self.cn_font = "Helvetica"
        
        self.set_auto_page_break(auto=True, margin=20)
        
    def header(self):
        if self.page_no() > 1:
            self.set_font(self.cn_font, '', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 6, '贵州茅台 (600519.SH) 综合分析报告', align='C')
            self.ln(8)
    
    def footer(self):
        self.set_y(-15)
        self.set_font(self.cn_font, '', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'第 {self.page_no()} 页', align='C')
    
    def write_cover(self):
        """封面"""
        self.add_page()
        self.ln(50)
        self.set_font(self.cn_font, 'B', 32)
        self.set_text_color(26, 26, 46)
        self.cell(0, 18, '贵州茅台', align='C')
        self.ln(22)
        self.set_font(self.cn_font, 'B', 20)
        self.set_text_color(192, 57, 43)
        self.cell(0, 14, '综合分析报告', align='C')
        self.ln(18)
        self.set_font(self.cn_font, '', 13)
        self.set_text_color(102, 102, 102)
        self.cell(0, 10, '600519.SH · 贵州茅台酒股份有限公司', align='C')
        self.ln(30)
        # 分割线
        x = self.get_x()
        self.set_draw_color(192, 57, 43)
        self.set_line_width(0.8)
        self.line(75, self.get_y(), 135, self.get_y())
        self.ln(25)
        self.set_font(self.cn_font, '', 12)
        self.set_text_color(136, 136, 136)
        self.cell(0, 9, f'报告生成日期：2026年07月04日', align='C')
        self.ln(9)
        self.cell(0, 9, '数据区间：2025-07-04 ~ 2026-07-03', align='C')
        self.ln(9)
        self.cell(0, 9, '北大BA工作坊 · 量化交易公益课', align='C')
    
    def write_section_title(self, title):
        """章节标题"""
        self.ln(6)
        self.set_font(self.cn_font, 'B', 16)
        self.set_text_color(26, 26, 46)
        self.cell(0, 12, title)
        # 下划线
        y = self.get_y()
        self.set_draw_color(192, 57, 43)
        self.set_line_width(0.6)
        self.line(self.l_margin + 1, y, self.l_margin + 61, y)
        self.ln(14)
    
    def write_sub_title(self, title):
        """子标题"""
        self.ln(3)
        self.set_font(self.cn_font, 'B', 13)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, title)
        self.ln(12)
    
    def write_body(self, text):
        """正文段落"""
        self.set_font(self.cn_font, '', 11)
        self.set_text_color(51, 51, 51)
        self.multi_cell(0, 7, text)
        self.ln(2)
    
    def write_bullet(self, text, bold_prefix=""):
        """项目符号"""
        self.set_font(self.cn_font, '', 11)
        self.set_text_color(51, 51, 51)
        x = self.get_x()
        self.cell(8, 7, '●')
        if bold_prefix:
            self.set_font(self.cn_font, 'B', 11)
            self.cell(self.get_string_width(bold_prefix) + 2, 7, bold_prefix)
            self.set_font(self.cn_font, '', 11)
        self.multi_cell(0, 7, text)
        self.ln(1)
    
    def write_table(self, headers, rows, col_widths=None):
        """简单表格"""
        n_cols = len(headers)
        if col_widths is None:
            col_widths = [self.w / n_cols - 4] * n_cols
        total_w = sum(col_widths)
        
        # 表头
        self.set_font(self.cn_font, 'B', 10)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(26, 26, 46)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 9, h, border=1, fill=True, align='C' if i == 0 else 'L')
        self.ln()
        
        # 数据行
        self.set_font(self.cn_font, '', 10)
        self.set_text_color(51, 51, 51)
        for row_idx, row in enumerate(rows):
            if row_idx % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(255, 255, 255)
            # 检查是否需要分页
            if self.get_y() > 250:
                self.add_page()
                self.set_font(self.cn_font, 'B', 10)
                self.set_fill_color(240, 240, 240)
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], 9, h, border=1, fill=True, align='C' if i == 0 else 'L')
                self.ln()
                self.set_font(self.cn_font, '', 10)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 8, str(cell), border=1, fill=True, align='C' if i == 0 else 'L')
            self.ln()
        self.ln(4)

    def write_disclaimer(self):
        """免责声明"""
        self.ln(10)
        self.set_draw_color(243, 156, 18)
        self.set_fill_color(254, 249, 231)
        y0 = self.get_y()
        self.rect(self.l_margin, y0, self.w - self.l_margin - self.r_margin, 42, 'DF')
        self.set_xy(self.l_margin + 4, y0 + 4)
        self.set_font(self.cn_font, 'B', 10)
        self.set_text_color(125, 102, 8)
        self.cell(0, 7, '⚠️ 免责声明：')
        self.set_xy(self.l_margin + 4, y0 + 14)
        self.set_font(self.cn_font, '', 9)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 8, 5.5,
            '本报告由 AI 大模型自动生成，仅供北京大学BA工作坊量化交易公益课程学习参考。'
            '报告中的所有分析、观点和建议均不构成任何形式的投资建议或承诺。'
            '股票市场存在较大风险，投资者应基于独立判断做出投资决策，盈亏自负。')
        self.set_y(y0 + 46)
    
    def write_ai_tag(self):
        """AI 生成标识"""
        self.ln(8)
        self.set_font(self.cn_font, '', 9)
        self.set_text_color(153, 153, 153)
        self.cell(0, 8, '🤖 本报告由 AI 自动生成 | 2026-07-04', align='C')


def build_pdf():
    pdf = HTMLToPDF()
    
    # ====== 封面 ======
    pdf.write_cover()
    
    # ====== 第一部分：线 ======
    pdf.write_section_title('一、"线"——价格走势与图形分析')
    
    pdf.write_sub_title('1.1 什么是"线"')
    pdf.write_body('"线"在股票分析中通常指代价格走势图（K线图、收盘价曲线等），是技术分析的基石。通过观察价格曲线的形态、趋势和关键点位，投资者可以直观理解股价的历史轨迹，辅助判断买卖时机。')
    pdf.write_body('K线（Candlestick）由开盘价、最高价、最低价、收盘价四个价格构成，实体部分表示开盘到收盘的涨跌，影线表示日内波动范围。收盘价折线则将每日收盘价连成曲线，便于观察中长期趋势。')
    
    pdf.write_sub_title('1.2 过去一年价格走势回顾')
    pdf.write_body('贵州茅台在近一年的走势呈现先涨后跌格局：2025年7月初收盘价约为 ¥1422，2025年下半年股价在 ¥1400~1550 区间震荡。进入2026年后，1月29日出现单日大涨8.61%，2月5日创出年内最高收盘价 ¥1555.00。此后股价持续走低，到6月26日触及年内最低 ¥1168.63，区间最大回撤幅度达到24.8%。')
    pdf.write_body('截至最新交易日（2026-07-03），收盘价为 ¥1194.45，较一年前累计下跌 -16.02%。')
    
    pdf.write_sub_title('1.3 价格统计概览')
    pdf.write_table(
        ['指标', '数值'],
        [
            ['交易日总数', '242 天'],
            ['最新收盘价', '¥1194.45'],
            ['区间涨跌幅', '-16.02%'],
            ['年内最高', '¥1555.00 (2026-02-05)'],
            ['年内最低', '¥1168.63 (2026-06-26)'],
            ['上涨天数', '113 天 (46.7%)'],
            ['下跌天数', '123 天 (50.8%)'],
            ['最大单日涨幅', '+8.61%'],
            ['最大单日跌幅', '-3.79%'],
            ['日波动率(标准差)', '1.09%'],
        ],
        [50, 110]
    )
    
    pdf.write_sub_title('1.4 月度收益分析（近12个月）')
    pdf.write_table(
        ['月份', '月度涨跌幅'],
        [
            ['2025-07', '-0.13%'],
            ['2025-08', '+3.72%'],
            ['2025-09', '-2.47%'],
            ['2025-10', '-0.98%'],
            ['2025-11', '+1.34%'],
            ['2025-12', '-5.09%'],
            ['2026-01', '+3.60%'],
            ['2026-02', '-2.46%'],
            ['2026-03', '-3.03%'],
            ['2026-04', '-4.49%'],
            ['2026-05', '-1.59%'],
            ['2026-06', '-1.47%'],
        ],
        [60, 100]
    )

    # ====== 第二部分：基本面 ======
    pdf.write_section_title('二、基本面分析')
    
    pdf.write_sub_title('2.1 什么是基本面')
    pdf.write_body('基本面分析（Fundamental Analysis）是通过研究公司的财务状况、经营能力、行业地位、宏观经济等内在价值因素来评估股票是否值得投资的方法。核心逻辑是：股票价格最终会回归其内在价值。')
    
    pdf.write_sub_title('2.2 公司概况')
    pdf.write_table(
        ['项目', '内容'],
        [
            ['公司全称', '贵州茅台酒股份有限公司'],
            ['股票代码', '600519.SH（上交所主板）'],
            ['成立日期', '1999年11月20日'],
            ['注册地址', '贵州省遵义市'],
            ['员工人数', '34,992 人'],
            ['法定代表人/董事长', '陈华'],
            ['总经理', '王莉'],
            ['总股本', '12.50 亿股（全流通）'],
            ['主营业务', '贵州茅台酒系列产品的生产与销售'],
        ],
        [42, 120]
    )
    
    pdf.write_sub_title('2.3 估值指标（截至 2026-07-03）')
    pdf.write_body('以下数据来自 Tushare 金融数据库：')
    pdf.write_table(
        ['指标', '数值', '说明'],
        [
            ['总市值', '约 1.49 万亿元', 'A股市值第一'],
            ['市盈率 PE(TTM)', '18.05 倍', '处于历史较低分位'],
            ['市净率 PB', '5.51 倍', '品牌溢价显著'],
            ['市销率 PS(TTM)', '8.67 倍', '高利润率支撑'],
        ],
        [38, 40, 82]
    )
    
    pdf.write_sub_title('2.4 基本面优势')
    pdf.write_bullet('贵州茅台是中国白酒行业绝对的品牌龙头，具有无可替代的品牌价值和消费者心智占有率。飞天茅台长期供不应求，出厂价与市场零售价之间存在巨大价差。', '品牌护城河极深：')
    pdf.write_bullet('茅台毛利率长期维持在 90% 以上，净利率超过 50%，ROE 常年高于 25%，在A股中属于顶级盈利质量。', '盈利能力卓越：')
    pdf.write_bullet('公司账上现金储备充足，预收款模式带来极强的现金流，几乎没有有息负债。', '现金流充裕：')
    pdf.write_bullet('在白酒行业整体进入存量竞争的背景下，茅台凭借品牌力持续抢占高端市场份额，业绩确定性较高。', '行业地位稳固：')
    pdf.write_bullet('茅台持续高比例分红，近年来分红率超过 50%，对长期投资者具有吸引力。', '分红回报优厚：')
    
    pdf.write_sub_title('2.5 需关注的风险')
    pdf.write_bullet('宏观经济下行可能影响高端消费需求，商务宴请场景减少对茅台消费有一定冲击。', '消费环境变化：')
    pdf.write_bullet('当前 PE 18倍虽然处于历史低位，但白酒行业整体估值中枢有下移趋势，需关注是否持续。', '估值中枢下移：')
    pdf.write_bullet('飞天茅台出厂价与零售价价差虽大，但提价节奏受政策和市场舆论制约。', '提价空间收窄：')
    pdf.write_bullet('渠道库存和社会库存的周期性变化可能短期影响批价和销量。', '库存周期波动：')

    # ====== 第三部分：技术面 ======
    pdf.write_section_title('三、技术面分析')
    
    pdf.write_sub_title('3.1 什么是技术面')
    pdf.write_body('技术分析（Technical Analysis）是通过研究历史价格、成交量等市场交易数据，运用各种技术指标和图形形态来预测未来价格走势的方法。技术分析基于三个核心假设：市场行为包容一切、价格以趋势方式演变、历史会重演。')
    
    pdf.write_sub_title('3.2 均线系统分析')
    pdf.write_table(
        ['均线', '最新值', '与收盘价关系'],
        [
            ['MA5 (5日)', '¥1188.15', '收盘价在MA5之上，短期偏强'],
            ['MA10 (10日)', '¥1191.76', '收盘价在MA10之上'],
            ['MA20 (20日)', '¥1223.55', '收盘价在MA20之下，中期承压'],
            ['MA60 (60日)', '¥1313.79', '收盘价在MA60之下，中长期压力较大'],
        ],
        [35, 40, 87]
    )
    pdf.write_body('均线形态：MA5、MA10、MA20、MA60 呈现空头排列，短期均线位于长期均线下方，表明股价处于下降趋势中。但近几日MA5开始走平并有上拐迹象，短期或有反弹需求。')
    
    pdf.write_sub_title('3.3 MACD 指标')
    pdf.write_table(
        ['指标', '最新值'],
        [
            ['DIF（快线）', '-23.45'],
            ['DEA（慢线）', '-24.30'],
            ['MACD 柱', '+1.71（转正）'],
        ],
        [60, 90]
    )
    pdf.write_body('MACD 解读：MACD柱由负转正，DIF上穿DEA形成金叉信号，短期动能由空转多。但DIF与DEA仍在零轴下方，属于弱势区域的金叉，反弹力度有待观察。')
    
    pdf.write_sub_title('3.4 RSI 相对强弱指标')
    pdf.write_body('最新 RSI(14) 约为 43.5，处于中性偏低区间（30-50），显示空头略占优势但未进入超卖区域，多空力量相对均衡。')
    
    pdf.write_sub_title('3.5 布林带 (Bollinger Bands)')
    pdf.write_table(
        ['轨道', '数值'],
        [
            ['上轨 (Upper)', '¥1331.97'],
            ['中轨 (Middle / MA20)', '¥1223.55'],
            ['下轨 (Lower)', '¥1115.13'],
            ['收盘价位置', '布林带下轨与中轨之间（约22%位置）'],
        ],
        [60, 90]
    )
    pdf.write_body('股价运行在布林带中轨下方、下轨上方，处于弱势区域但有支撑。布林带宽度约 217 元（17.7%），显示近期波动率处于中等水平。')
    
    pdf.write_sub_title('3.6 技术指标综合信号')
    pdf.write_bullet('MACD柱转正，DIF上穿DEA形成金叉，短期动能偏多')
    pdf.write_bullet('RSI(14)=43.5，处于中性偏低区间')
    pdf.write_bullet('均线空头排列（MA5<MA10<MA20<MA60），中期趋势偏弱')
    pdf.write_bullet('收盘价位于布林带中下轨之间，下方 ¥1115 附近有技术支撑')

    # ====== 第四部分：投资建议 ======
    pdf.write_section_title('四、综合分析与投资建议')
    
    pdf.write_sub_title('4.1 三维分析汇总')
    pdf.write_table(
        ['维度', '评级', '核心观点'],
        [
            ['线（走势）', '偏弱', '过去一年累计下跌16%，处于下降通道。近期在¥1168附近有初步企稳迹象，但尚未形成明确反转。'],
            ['基本面', '优秀', '品牌护城河极深，盈利能力A股顶级。PE 18倍处于历史低位，估值有安全边际。'],
            ['技术面', '中性偏弱', '均线空头排列，短期承压。MACD刚金叉但处于零轴下方，RSI中性偏低。'],
        ],
        [28, 28, 104]
    )
    
    pdf.write_sub_title('4.2 投资建议')
    
    pdf.set_font(pdf.cn_font, 'B', 11)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(0, 8, '长期投资者：')
    pdf.ln(10)
    pdf.set_font(pdf.cn_font, '', 11)
    pdf.write_body('贵州茅台作为A股核心资产，当前估值处于历史较低分位，PE仅18倍左右的茅台具有较高的长期配置价值。建议采取分批逢低建仓策略，关注 ¥1100-1200 区间作为较好的中长期布局窗口。不建议一次性重仓，保留部分资金应对可能的进一步回调。')
    
    pdf.set_font(pdf.cn_font, 'B', 11)
    pdf.cell(0, 8, '中短期交易者：')
    pdf.ln(10)
    pdf.set_font(pdf.cn_font, '', 11)
    pdf.write_body('当前股价处于下降趋势中，技术面信号偏弱。建议等待以下信号出现再考虑介入：（1）股价放量站上 MA20（约 ¥1223）；（2）MACD 在零轴下方形成金叉后持续走强；（3）RSI 突破 50 中轴。若股价跌破 ¥1168（前低），建议止损观望。')
    
    pdf.set_font(pdf.cn_font, 'B', 11)
    pdf.cell(0, 8, '核心关注点：')
    pdf.ln(10)
    pdf.set_font(pdf.cn_font, '', 11)
    pdf.write_bullet('飞天茅台批价走势——是判断终端需求的最直接指标', '')
    pdf.write_bullet('季度业绩披露——关注营收和净利润增速是否企稳', '')
    pdf.write_bullet('分红政策——高分红是持有茅台的"底仓逻辑"之一', '')
    pdf.write_bullet('宏观消费数据——社零、餐饮收入等反映消费景气度', '')
    
    pdf.write_sub_title('4.3 风险提示')
    pdf.write_bullet('本报告仅为技术学习和学术交流用途，不构成任何投资建议', '')
    pdf.write_bullet('股票投资具有高风险性，历史表现不代表未来收益', '')
    pdf.write_bullet('投资者应基于独立判断做出投资决策，盈亏自负', '')
    pdf.write_bullet('数据来源：Tushare金融数据库，可能存在延迟或误差', '')
    
    # 免责声明 + AI 标识
    pdf.write_disclaimer()
    pdf.write_ai_tag()
    
    # 输出
    pdf.output("贵州茅台_600519_综合分析报告.pdf")
    print("PDF 报告已生成: 贵州茅台_600519_综合分析报告.pdf")

if __name__ == "__main__":
    build_pdf()
