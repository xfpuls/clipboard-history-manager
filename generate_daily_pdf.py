"""Generate daily bug fix summary PDF."""
from fpdf import FPDF


class DailyPDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        font_path = 'C:/Windows/Fonts/simhei.ttf'
        self.add_font('SimHei', '', font_path)
        self.set_auto_page_break(True, 15)

    def header(self):
        self.set_font('SimHei', '', 16)
        self.set_text_color(91, 155, 213)
        self.cell(0, 10, 'Bug 修复日报', align='C')
        self.ln(6)
        self.set_font('SimHei', '', 10)
        self.set_text_color(147, 180, 208)
        self.cell(0, 6, '剪贴板历史管理器 — 2026/05/16 ~ 2026/05/17', align='C')
        self.ln(10)


pdf = DailyPDF()
pdf.add_page()

# Summary
pdf.set_font('SimHei', '', 12)
pdf.set_text_color(44, 62, 80)
pdf.cell(0, 8, '总计：11 个 Bug，跨越 2 天', align='C')
pdf.ln(10)

# ---- Day 1 ----
pdf.set_font('SimHei', '', 13)
pdf.set_text_color(91, 155, 213)
pdf.cell(0, 8, '第 1 天 — 2026/05/16（10 个）')
pdf.ln(8)

# Table header
col_w = [10, 22, 50, 108]  # #, Time, Problem, Root Cause
pdf.set_font('SimHei', '', 9)
pdf.set_fill_color(235, 243, 250)
pdf.set_text_color(44, 62, 80)
pdf.set_draw_color(200, 210, 220)

headers = ['#', '时间', '问题', '根本原因']
for i, h in enumerate(headers):
    pdf.cell(col_w[i], 7, h, border=1, fill=True, align='C')
pdf.ln()

# Day 1 data
day1 = [
    ('1', '18:00', '卡片文字显示不全', '固定高度58px+单行截断'),
    ('2', '18:10', '设置页文字截断', '标签无word wrap+无滚动条'),
    ('3', '18:30', '托盘右键菜单无反应', 'TrayManager非QObject,菜单被GC'),
    ('4', '19:00', '置顶闪烁,关闭按钮失效', 'setWindowFlags重建原生窗口'),
    ('5', '19:10', '叉号关闭进程残留', 'closeEvent只hide不quit退出'),
    ('6', '19:15', '双击exe不显示面板', '启动时未调用_show_panel()'),
    ('7', '19:15', '窗口置顶默认开启', '初始WindowStaysOnTopHint+checked'),
    ('8', '21:00', '点击卡片粘贴失效', 'QLabel拦截鼠标点击事件'),
    ('9', '21:40', '自动刷新定时器竞态', '2秒轮询重建卡片有竞态条件'),
    ('10', '22:00', '自定义Qt信号不稳定', 'Signal(dict)链条长,易出错'),
]

pdf.set_font('SimHei', '', 8)
for row in day1:
    h = 12 if len(row[3]) > 40 else 7
    for i, val in enumerate(row):
        align = 'C' if i <= 1 else 'L'
        pdf.cell(col_w[i], h, val, border=1, align=align)
    pdf.ln()

pdf.ln(6)

# ---- Day 2 ----
pdf.set_font('SimHei', '', 13)
pdf.set_text_color(91, 155, 213)
pdf.cell(0, 8, '第 2 天 — 2026/05/17（1 个）')
pdf.ln(8)

pdf.set_font('SimHei', '', 9)
pdf.set_fill_color(235, 243, 250)
for i, h in enumerate(headers):
    pdf.cell(col_w[i], 7, h, border=1, fill=True, align='C')
pdf.ln()

pdf.set_font('SimHei', '', 8)
pdf.set_fill_color(255, 235, 235)
row = ('11', '23:15', '点击不同卡片粘贴永远是第一条(核心bug)', '缺QApplication导入,NameError被try静默吞掉')
pdf.cell(col_w[0], 10, row[0], border=1, align='C', fill=True)
pdf.cell(col_w[1], 10, row[1], border=1, align='C', fill=True)
pdf.cell(col_w[2], 10, row[2], border=1, align='L', fill=True)
pdf.cell(col_w[3], 10, row[3], border=1, align='L', fill=True)
pdf.ln(12)

# Footer note
pdf.set_font('SimHei', '', 9)
pdf.set_text_color(200, 50, 50)
pdf.cell(0, 7, '关键教训: Bug#11一行NameError被try/except静默吞掉,诊断了一整天才靠诊断脚本定位。', align='L')

# Save
output = 'd:/lishiwenjian/lishijiil/每日总结.pdf'
pdf.output(output)
print(f'PDF saved: {output}')
