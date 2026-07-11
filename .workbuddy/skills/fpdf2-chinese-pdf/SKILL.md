# fpdf2 中文 PDF 报告生成（宋体五号 · 1.5倍行距）

## 触发条件

当需要生成含中文内容的 PDF 报告，且格式要求为**宋体、五号字(10.5pt)、1.5倍行距**时，使用本 Skill。

## 核心问题与解决方案

### 问题1：中文字体变方块（tofu）

**根因**：reportlab 的 `<b>` 标签会触发字体族映射，TTC 字体（如 simsun.ttc）在 reportlab 中注册字体族不稳定。

**解决**：**不用 reportlab，用 fpdf2**。fpdf2 的 `add_font()` 直接注册 TTF/TTC，`set_font()` 切换时无需字体族映射。

### 问题2：文本右侧被截断（半截字）

**根因**：fpdf2 对 TTC 格式的字符宽度（glyph metrics）读取不准，导致 `multi_cell` 换行位置错误，文字冲出右边界。

**解决**（两步）：
1. **TTC → TTF 提取**：用 fontTools 把 SimSun 从 TTC 中提取为独立 TTF 文件
2. **手动逐字换行**：不用 `multi_cell`，自己用 `get_string_width()` 测量宽度后逐字拆分

---

## 字体准备（一次性）

```python
from fontTools.ttLib import TTCollection
import shutil, os

skills_dir = ".workbuddy/skills/fpdf2-chinese-pdf/fonts"
os.makedirs(skills_dir, exist_ok=True)

# 从 TTC 提取 SimSun 为独立 TTF
tc = TTCollection("C:/Windows/Fonts/simsun.ttc")
tc[0].save(f"{skills_dir}/simsun.ttf")

# SimHei 已经是独立 TTF，直接复制
shutil.copy("C:/Windows/Fonts/simhei.ttf", f"{skills_dir}/simhei.ttf")
```

提取后的两个字体文件：
- `.workbuddy/skills/fpdf2-chinese-pdf/fonts/simsun.ttf` — 宋体（正文）
- `.workbuddy/skills/fpdf2-chinese-pdf/fonts/simhei.ttf` — 黑体（标题/加粗）

> **重要**：不要直接用 `C:/Windows/Fonts/simsun.ttc` 注册字体。必须提取为 TTF，否则宽度测量会出错。

---

## PDF 类模板

```python
from fpdf import FPDF

class ReportPDF(FPDF):
    """中文报告 PDF — 宋体五号 · 1.5倍行距 · 手动换行"""
    
    # ========== 格式常量 ==========
    BODY_SIZE = 10.5       # 五号字 (pt)
    LINE_H = 5.56          # 10.5 × 1.5 × 0.3528 (mm)
    SMALL = 9              # 表格/脚注
    SUBTITLE_SIZE = 12     # 子标题
    SECTION_SIZE = 16      # 章节标题

    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        # ——— 字体注册（使用 TTF，不用 TTC）———
        skills = "E:/EN_study_tool/BA_task/.workbuddy/skills/fpdf2-chinese-pdf/fonts"
        self.add_font("CN", "", f"{skills}/simsun.ttf")    # 宋体
        self.add_font("CN", "B", f"{skills}/simhei.ttf")   # 黑体（粗体）
        self.cn = "CN"
        self.set_auto_page_break(True, 20)

    # ========== 页眉 / 页脚 ==========
    def header(self):
        if self.page_no() > 1:
            self.set_font(self.cn, '', 8)
            self.set_text_color(160, 160, 160)
            self.cell(0, 5, '报告标题', align='C')
            self.ln(7)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.cn, '', 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 8, str(self.page_no()), align='C')

    # ========== 封面 ==========
    def cover(self, title, subtitle, tagline, meta_lines):
        self.add_page()
        self.ln(55)
        self.set_font(self.cn, 'B', 30)
        self.set_text_color(26, 26, 46)
        self.cell(0, 20, title, align='C')
        self.ln(24)
        self.set_font(self.cn, 'B', 22)
        self.set_text_color(192, 57, 43)
        self.cell(0, 16, subtitle, align='C')
        self.ln(20)
        self.set_font(self.cn, '', 12)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, tagline, align='C')
        self.ln(30)
        # 分割线
        self.set_draw_color(192, 57, 43)
        self.set_line_width(0.8)
        self.line(65, self.get_y(), 145, self.get_y())
        self.ln(20)
        self.set_font(self.cn, '', 11)
        self.set_text_color(140, 140, 140)
        for line in meta_lines:
            self.cell(0, 8, line, align='C')
            self.ln(8)

    # ========== 标题层级 ==========
    def sec(self, title):
        """一级标题 — 16pt 粗体"""
        self.ln(6)
        self.set_font(self.cn, 'B', self.SECTION_SIZE)
        self.set_text_color(26, 26, 46)
        self.cell(0, 12, title)
        self.ln(16)

    def sub(self, title):
        """二级标题 — 12pt 粗体"""
        self.ln(2)
        self.set_font(self.cn, 'B', self.SUBTITLE_SIZE)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, title)
        self.ln(11)

    # ========== ★★★ 核心：手动逐字换行（不用 multi_cell）★★★ ==========
    def _wrap_text(self, text, max_w, first_line_indent=0):
        """
        逐字符用 get_string_width() 测量宽度后手动换行。
        这是解决「文字冲出右边界」的关键。
        """
        self.set_x(self.l_margin + first_line_indent)
        line = ''
        first_char = True
        for ch in text:
            test = line + ch
            test_w = self.get_string_width(test)
            if test_w > max_w - first_line_indent and not first_char:
                # 当前行满了，输出并开始新行
                self.cell(max_w, self.LINE_H, line, align='L')
                self.ln(self.LINE_H)
                self.set_x(self.l_margin)
                line = ch
                first_char = False
            else:
                line = test
                first_char = False
        # 输出最后一行
        if line:
            self.cell(max_w, self.LINE_H, line, align='L')
            self.ln(self.LINE_H)
        self.set_x(self.l_margin)

    def body(self, text):
        """正文 — 五号宋体、左对齐、1.5倍行距"""
        self.set_font(self.cn, '', self.BODY_SIZE)
        self.set_text_color(51, 51, 51)
        max_w = self.w - self.l_margin - self.r_margin
        for para in text.split('\n'):
            if para.strip():
                self._wrap_text(para, max_w)
            else:
                self.ln(self.LINE_H)

    def bullet(self, text, bold_prefix=""):
        """项目符号 — 缩进 5mm、左对齐"""
        self.set_font(self.cn, '', self.BODY_SIZE)
        self.set_text_color(51, 51, 51)
        max_w = self.w - self.l_margin - self.r_margin - 5
        full = '● ' + bold_prefix + text
        self._wrap_text(full, max_w, first_line_indent=5)

    # ========== 公式框 ==========
    def formula_box(self, lines):
        self.ln(2)
        y0 = self.get_y()
        h = len(lines) * 6.5 + 8
        self.set_fill_color(248, 248, 250)
        self.rect(self.l_margin, y0, self.w - self.l_margin - self.r_margin, h, 'F')
        self.set_xy(self.l_margin + 6, y0 + 4)
        self.set_font(self.cn, '', self.SMALL)
        self.set_text_color(60, 60, 80)
        for line in lines:
            self.cell(0, 6.5, line)
            self.ln(6.5)
            self.set_x(self.l_margin + 6)
        self.set_y(y0 + h + 3)

    # ========== 表格 ==========
    def write_table(self, headers, rows, col_widths=None):
        line_h = 7.5
        full_w = self.w - self.l_margin - self.r_margin
        if col_widths is None:
            col_widths = [full_w / len(headers)] * len(headers)
        total_w = sum(col_widths)
        self.ln(2)
        # 表头
        self.set_fill_color(230, 230, 235)
        self.set_font(self.cn, 'B', self.BODY_SIZE)
        self.set_text_color(44, 62, 80)
        self.set_x(self.l_margin)
        for i, h in enumerate(headers):
            self.cell(col_widths[i] / total_w * full_w, line_h, h, border=0, fill=True, align='C')
        self.ln(line_h)
        # 数据行
        self.set_font(self.cn, '', self.BODY_SIZE)
        self.set_text_color(51, 51, 51)
        for ri, row in enumerate(rows):
            bg = (245, 245, 250) if ri % 2 == 0 else (255, 255, 255)
            self.set_fill_color(*bg)
            self.set_x(self.l_margin)
            for i, val in enumerate(row):
                self.cell(col_widths[i] / total_w * full_w, line_h, str(val), border=0, fill=True, align='C')
            self.ln(line_h)
        self.ln(3)

    # ========== 图片 ==========
    def img(self, path, w=178):
        if os.path.exists(path):
            self.ln(3)
            self.image(path, x=self.l_margin + 1, w=w)
            self.ln(4)

    # ========== 免责声明 ==========
    def disclaimer(self):
        self.ln(8)
        y0 = self.get_y()
        self.set_fill_color(254, 249, 231)
        self.rect(self.l_margin, y0, self.w - self.l_margin - self.r_margin, 32, 'F')
        self.set_xy(self.l_margin + 5, y0 + 3)
        self.set_font(self.cn, 'B', 9)
        self.set_text_color(125, 102, 8)
        self.cell(0, 6, '免责声明：')
        self.set_xy(self.l_margin + 5, y0 + 11)
        self.set_font(self.cn, '', 9)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 10, 5,
            '本报告由 AI 自动生成，仅供北京大学BA工作坊量化交易公益课程学习参考。'
            '所有分析和观点均不构成投资建议。股市有风险，投资需谨慎。')
        self.set_y(y0 + 36)

    # ========== AI 标识 ==========
    def ai_tag(self):
        self.ln(5)
        self.set_font(self.cn, '', 9)
        self.set_text_color(160, 160, 160)
        self.cell(0, 8, '本报告由 AI 自动生成 | 2026-07-11', align='C')
```

---

## 使用方式

```python
pdf = ReportPDF()

# 封面
pdf.cover(
    title='贵州茅台 (600519.SH)',
    subtitle='双均线交叉策略研究报告',
    tagline='均线 · 金叉死叉 · 回测评估',
    meta_lines=[
        '数据区间: 2025-07-04 ~ 2026-07-03 | 242 个交易日',
        '北大BA工作坊 · 量化交易公益课'
    ]
)

# 内容
pdf.sec('一、章节标题')
pdf.sub('1.1 子标题')
pdf.body('这是正文段落，会自动逐字测量宽度后换行，不会超出右边界。')
pdf.bullet('这是带项目符号的文本', bold_prefix='加粗前缀：')
pdf.formula_box([
    'R = (V_final / V_initial) - 1',
    'MDD = min((V_t - peak_t) / peak_t)',
])
pdf.write_table(
    ['指标', '数值', '说明'],
    [['累计回报', '-9.51%', '总盈亏幅度'], ['夏普比率', '-1.15', '风险调整收益']]
)
pdf.img("chart.png")

# 结尾
pdf.disclaimer()
pdf.ai_tag()

pdf.output("报告.pdf")
```

---

## 格式规范速查

| 元素 | 字体 | 字号 | 对齐 | 颜色 |
|------|------|------|------|------|
| 封面标题 | 黑体 Bold | 30pt | 居中 | #1a1a2e |
| 封面副标题 | 黑体 Bold | 22pt | 居中 | #c0392b |
| 章节标题 | 黑体 Bold | 16pt | 左对齐 | #1a1a2e |
| 子标题 | 黑体 Bold | 12pt | 左对齐 | #2c3e50 |
| 正文 | 宋体 | 10.5pt | 左对齐 | #333333 |
| 项目符号 | 宋体 | 10.5pt | 左对齐 | #333333 |
| 公式 | 宋体 | 9pt | 左对齐 | #3c3c50 |
| 表格表头 | 黑体 Bold | 10.5pt | 居中 | #2c3e50 |
| 表格数据 | 宋体 | 10.5pt | 居中 | #333333 |
| 页眉 | 宋体 | 8pt | 居中 | #a0a0a0 |
| 页脚 | 宋体 | 8pt | 居中 | #a0a0a0 |

**行距**：正文 5.56mm（= 10.5pt × 1.5 × 0.3528 mm/pt）

**页边距**：使用 fpdf2 默认值（左10mm / 右10mm / 上10mm / 下10mm），不要手动设置 `set_margins()`。

---

## 踩坑记录

| 问题 | 原因 | 解决 |
|------|------|------|
| 中文变方块 | reportlab `<b>` 标签触发 TTC 字体族映射失败 | 用 fpdf2 替代 reportlab |
| 右侧文字被截断 | fpdf2 读 TTC 的 glyph width 不准 | TTC→TTF 提取 + 手动逐字换行 |
| `multi_cell` 换行位不对 | fpdf2 对 CJK 的 `multi_cell` 有已知 bug | 自己用 `get_string_width()` 拆分 |
| `set_margins(25)` 反而更糟 | 边距越大，fpdf2 的测量误差越容易触发溢出 | 保持默认 10mm 边距 |

---

## 依赖

```
pip install fpdf2 fontTools
```
