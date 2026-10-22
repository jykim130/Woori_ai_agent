from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'tmp/pdf-author-deps'), str(ROOT / 'tmp/pdf-deps')]
import pymupdf
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from step_card_style import draw_step_card

OUT = ROOT / '보고서/10-22내용/징검다WOORI_5페이지_실현가능성보완.pdf'
QA = ROOT / 'tmp/pdfs/page5_feasibility_case_review'
OUT.parent.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)

REVENUE_PARAGRAPHS = [
    '징검다WOORI의 수익 모델은 고객의 금융 맥락을 축적해 장기적인 거래 관계를 유지하고, 생활 변화에 따라 발생하는 신규 금융 수요를 연결하는 데 있다.',
    '고객이 확인한 목표와 제약, 과거의 선택과 실행 결과를 다음 금융 준비에 활용함으로써, 고객이 같은 상황을 반복해서 설명하고 금융 업무를 다시 구성하는 부담을 줄인다. 이러한 경험이 지속적인 이용으로 이어지면, 우리은행은 생활자금·납부·저축 등 기존 거래에서 발생하는 수익을 더 오래 유지할 수 있다.',
    '또한 취업·독립·이사 등 새로운 금융 수요가 발생하는 시점에 고객의 상황에 맞는 준비와 업무 실행을 지원함으로써, 추가적인 자금 유입과 적합한 금융상품 이용으로 이어질 기회를 확보한다. 서비스의 경제적 가치는 이러한 거래 유지와 확대에서 발생하는 추가 수익이 AI 및 시스템 운영비용을 초과하는지에 따라 판단한다.',
]

pdfmetrics.registerFont(TTFont('MG', 'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MGB', 'C:/Windows/Fonts/malgunbd.ttf'))
pdfmetrics.registerFontFamily('MG', normal='MG', bold='MGB', italic='MG', boldItalic='MGB')
W, H = A4
M = 32
CW = W - 2 * M
BLUE = HexColor('#006CAF')
CYAN = HexColor('#20C2E8')
INK = HexColor('#29495F')
PALE = HexColor('#ECF6FB')
LINE = HexColor('#C7DDEB')
MUTED = HexColor('#71889B')
WHITE = HexColor('#FFFFFF')

c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
c.setTitle('징검다WOORI | 05 기대효과와 실현 가능성 및 수익성')
c.setAuthor('징검다WOORI')
text_regions = []


def p(text, x, top, width, size=9.7, leading=14.2, bold=False,
      color=INK, maxh=None, center_in=None, align=0):
    style = ParagraphStyle(
        'body', fontName='MGB' if bold else 'MG', fontSize=size,
        leading=leading, textColor=color, wordWrap='LTR',
        splitLongWords=False, alignment=align,
    )
    para = Paragraph(text, style)
    _, height = para.wrap(width, H)
    if maxh is not None:
        assert height <= maxh + 0.01, (text, height, maxh)
    if center_in is not None:
        assert height <= center_in + 0.01
        top += (center_in - height) / 2
    assert M - 0.01 <= x and x + width <= W - M + 0.01
    assert top >= 20 and top + height <= 808
    para.drawOn(c, x, H - top - height)
    text_regions.append((x, top, x + width, top + height))
    return height


def line(x1, y1, x2, y2, color=LINE, width=0.65):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, H - y1, x2, H - y2)


def arrow_right(x1, x2, y):
    assert x2 - x1 >= 5
    line(x1, y, x2, y, BLUE, 0.8)
    c.setFillColor(BLUE)
    path = c.beginPath()
    path.moveTo(x2, H - y)
    path.lineTo(x2 - 3.5, H - y + 2)
    path.lineTo(x2 - 3.5, H - y - 2)
    path.close()
    c.drawPath(path, stroke=0, fill=1)


def arrow_down(x, y1, y2):
    assert y2 - y1 >= 5
    line(x, y1, x, y2, BLUE, 0.8)
    c.setFillColor(BLUE)
    path = c.beginPath()
    path.moveTo(x, H - y2)
    path.lineTo(x - 2, H - y2 + 3.5)
    path.lineTo(x + 2, H - y2 + 3.5)
    path.close()
    c.drawPath(path, stroke=0, fill=1)


def box(x, top, width, height, fill=PALE, stroke=None, radius=5):
    c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke)
        c.setLineWidth(0.65)
    c.roundRect(x, H - top - height, width, height, radius,
                fill=1, stroke=1 if stroke is not None else 0)


def section(number, title, top):
    box(M, top, 23, 18, BLUE, radius=4)
    p(number, M, top, 23, size=8.8, leading=12, bold=True,
      color=WHITE, center_in=18, align=1)
    p(title, M + 32, top, CW - 32, size=11.5, leading=16,
      bold=True, color=BLUE, center_in=18, maxh=16)


c.setFillColor(CYAN)
c.rect(M, H - 27, 23, 4, stroke=0, fill=1)
p('05 / 기대효과와 실현 가능성·수익성', M + 32, 21, CW - 32,
  size=9, leading=13, bold=True, color=BLUE, maxh=13)
p('고객의 금융 준비를 돕고,<br/>지속적인 거래 관계로 이어간다',
  M, 44, CW, size=22, leading=25, bold=True, color=BLUE, maxh=50)

# Customer and bank outcomes use the same rows, without assuming a measured causal effect.
section('01', '고객과 은행이 기대하는 변화', 113)
TABLE_TOP, HEADER_H, ROW_H = 139, 23, 30
TABLE_H = HEADER_H + 3 * ROW_H
HALF = CW / 2
MID = M + HALF
c.saveState()
clip = c.beginPath()
clip.roundRect(M, H - TABLE_TOP - TABLE_H, CW, TABLE_H, 6)
c.clipPath(clip, stroke=0, fill=0)
c.setFillColor(PALE)
c.rect(M, H - TABLE_TOP - HEADER_H, CW, HEADER_H, stroke=0, fill=1)
for i in range(3):
    c.setFillColor(HexColor('#FFFFFF' if i % 2 == 0 else '#F8FCFE'))
    top = TABLE_TOP + HEADER_H + i * ROW_H
    c.rect(M, H - top - ROW_H, CW, ROW_H, stroke=0, fill=1)
c.restoreState()
c.setStrokeColor(LINE)
c.setLineWidth(0.65)
c.roundRect(M, H - TABLE_TOP - TABLE_H, CW, TABLE_H, 6, stroke=1, fill=0)
line(MID, TABLE_TOP, MID, TABLE_TOP + TABLE_H)
for i in range(3):
    y = TABLE_TOP + HEADER_H + i * ROW_H
    line(M, y, W - M, y)
p('고객이 얻는 변화', M + 12, TABLE_TOP, HALF - 24,
  size=9.4, leading=13, bold=True, color=BLUE, center_in=HEADER_H)
p('우리은행이 기대하는 변화', MID + 12, TABLE_TOP, HALF - 24,
  size=9.4, leading=13, bold=True, color=BLUE, center_in=HEADER_H)
effects = [
    ('필요한 정보·기능을 찾는 시간 감소', '도움이 필요한 시점에 금융서비스 연결'),
    ('준비 순서·자금 계획을 구성하는 부담 감소', '생활자금·납부·저축 등 거래 관계 유지'),
    ('이전 목표와 선택을 활용한 지속적인 개인화', '취업·독립·이사에 따른 신규 수요 연결'),
]
for i, (customer, bank) in enumerate(effects):
    top = TABLE_TOP + HEADER_H + i * ROW_H
    for text, x in ((customer, M + 12), (bank, MID + 12)):
        p(text, x, top, HALF - 24, size=9.4, leading=13,
          center_in=ROW_H, maxh=26)

# Feasibility case: control technical scope, initial costs, and deployment size.
section('02', '실현 가능성: 기존 업무를 활용하고 단계적으로 검증·확장', 269)
CARD_GAP = 10
CARD_W = (CW - 2 * CARD_GAP) / 3
feasibility = [
    ('기술적 구현 범위',
     '마이플래너의 일정·목표와 조회 가능한 금융정보를 활용하도록 설계한다. AI는 맥락 확인과 계획·대안 설명을 맡고, 계산과 실행은 도구와 기존 업무 흐름에 연결한다.'),
    ('투자·운영비 통제',
     '대상 고객과 시나리오를 제한해 시작한다. 필요한 시점에 AI를 호출하고, 건당 운영비와 시스템 연동 비용을 확인해 도입·운영 범위를 조정한다.'),
    ('단계적 검증과 확장',
     '대표 시나리오의 조회·계산·계획 제안부터 검증한다. 정확도와 준비 부담 감소, 건당 운영비를 확인한 뒤 실행 연동과 적용 범위를 넓힌다.'),
]
for i, (title, body) in enumerate(feasibility):
    x = M + i * (CARD_W + CARD_GAP)
    draw_step_card(c, x, 296, CARD_W, 144, H)
    p(title, x + 12, 307, CARD_W - 24, size=10.2, leading=14.5,
      bold=True, color=BLUE, maxh=14.5)
    p(body, x + 12, 332, CARD_W - 24, size=9.1, leading=12.7,
      maxh=95.25)
p('실제 데이터 접근·업무 연동 범위와 비용을 사전 검증하고, 초기 적용 결과에 따라 확대 여부를 결정한다.',
  M, 447, CW, size=7.2, leading=9.5, color=MUTED, maxh=9.5)

# Revenue mechanism is a business hypothesis; the user's approved text is kept verbatim.
section('03', '수익성: 거래 관계의 유지와 신규 수요 연결', 468)
LEFT_W, JOIN, DEST_X = 208, 264, 289
line(M + LEFT_W, 505.5, JOIN, 505.5, BLUE, 0.8)
line(M + LEFT_W, 535.5, JOIN, 535.5, BLUE, 0.8)
line(JOIN, 505.5, JOIN, 535.5, BLUE, 0.8)
arrow_right(JOIN, DEST_X - 3, 521)
for top, text in ((494, '기존 거래 관계의 장기 유지'),
                  (524, '생활 변화에 따른 신규 수요 연결')):
    box(M, top, LEFT_W, 23, PALE, LINE)
    p(text, M + 8, top, LEFT_W - 16, size=9.1, leading=12.5,
      color=BLUE, bold=True, center_in=23, maxh=12.5, align=1)
DEST_W = W - M - DEST_X
box(DEST_X, 502, DEST_W, 40, BLUE)
p('거래 유지·확대의 추가 수익', DEST_X + 10, 508, DEST_W - 20,
  size=10, leading=14, color=WHITE, bold=True, maxh=14, align=1)
p('AI·시스템 운영비용과 비교', DEST_X + 10, 526, DEST_W - 20,
  size=8.4, leading=11.5, color=HexColor('#E6F5FF'), maxh=11.5, align=1)

top = 561
for i, text in enumerate(REVENUE_PARAGRAPHS):
    height = p(text, M, top, CW, size=10, leading=15, maxh=60)
    top += height + (6 if i < len(REVENUE_PARAGRAPHS) - 1 else 0)
assert top <= 721, ('Revenue body is too long', top)

p('검증할 결과', M, 731, CW, size=8.9, leading=12.5,
  color=BLUE, bold=True, maxh=12.5)
METRIC_TOP, METRIC_H = 750, 45
box(M, METRIC_TOP, CW, METRIC_H, PALE)
metrics = [
    ('고객 효과', '준비 소요시간·과제 완료율'),
    ('거래 관계', '거래 유지·목적자금 유입'),
    ('경제성', '추가 수익 대비 운영비용'),
]
for i, (label, value) in enumerate(metrics):
    x = M + i * CW / 3
    if i:
        line(x, METRIC_TOP + 8, x, METRIC_TOP + METRIC_H - 8)
    p(label, x + 12, METRIC_TOP + 6, CW / 3 - 24,
      size=8.2, leading=11, bold=True, color=BLUE, maxh=11)
    p(value, x + 12, METRIC_TOP + 23, CW / 3 - 24,
      size=8.6, leading=12, maxh=12)
p('기대효과와 경제성은 향후 실제 이용 결과로 검증한다.',
  M, 799, CW, size=7.2, leading=9, color=MUTED, maxh=9)

line(M, 816, W - M, 816)
c.setFillColor(MUTED)
c.setFont('MG', 7.5)
c.drawString(M, H - 829, '징검다WOORI · 기대효과와 도입 가능성 및 수익 모델')
c.drawRightString(W - M, H - 829, '05')
c.save()

with pymupdf.open(OUT) as result:
    assert len(result) == 1
    page = result[0]
    content = page.get_text()
    assert '\ufffd' not in content
    normalize = lambda s: re.sub(r'\s+', '', s)
    for paragraph in REVENUE_PARAGRAPHS:
        assert normalize(paragraph) in normalize(content), 'Revenue text was changed or omitted'
    for i, a in enumerate(text_regions):
        for b in text_regions[i + 1:]:
            assert not pymupdf.Rect(a).intersects(pymupdf.Rect(b)), (a, b)
    assert content.rstrip().endswith('05')
    page.get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2)).save(QA / 'page_5.png')
    (QA / 'extracted_text.txt').write_text(content, encoding='utf-8')
    audit = {
        'pages': len(result), 'logical_page': '05',
        'revenue_paragraphs_preserved_verbatim': len(REVENUE_PARAGRAPHS),
        'effect_pairs': len(effects), 'validation_metrics': len(metrics),
        'feasibility_arguments': len(feasibility),
        'feasibility_topics': [item[0] for item in feasibility],
        'revenue_body_end_y': top,
        'text_regions_overlap': False,
    }
    (QA / 'layout_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')

print(OUT)
print(json.dumps(audit, ensure_ascii=True))
