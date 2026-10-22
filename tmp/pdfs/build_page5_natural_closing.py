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

OUT = ROOT / '보고서/10-22내용/징검다WOORI_5페이지_미래뱅킹_마무리수정본.pdf'
QA = ROOT / 'tmp/pdfs/page5_natural_closing_review'
OUT.parent.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)

PARAGRAPHS = [
    '징검다WOORI는 고객이 생활의 변화마다 필요한 정보를 다시 찾고, 여러 금융 업무를 자신의 계획에 맞게 연결하는 수고를 줄이고자 한다. 고객이 확인한 목표와 우선순위, 이전의 선택과 실행 결과를 다음 준비에 활용해, 자신을 이해하는 금융 지원을 계속 이어받도록 돕는다.',
    '이 경험은 마이플래너와 기존 금융 업무를 연결하는 것에서 시작한다. 대상 고객과 시나리오를 제한해 조회·계산·계획 제안부터 검증하고, AI는 맥락 확인과 대안 설명을 맡도록 설계한다. 계산과 실행은 도구와 기존 업무 흐름에 연결하며, 지원의 정확성과 준비 부담 감소, 연동 비용과 건당 운영비를 확인해 적용 범위를 넓힌다.',
    '함께 준비한 경험이 쌓이면 고객이 다음 생활 변화에서도 우리WON뱅킹을 찾을 이유가 된다. 이러한 경험이 지속적인 이용으로 이어지면, 우리은행은 생활자금·납부·저축 등 기존 거래에서 발생하는 수익을 더 오래 유지할 수 있다.',
    '또한 취업·독립·이사 등 새로운 금융 수요가 발생하는 시점에 고객의 상황에 맞는 준비와 업무 실행을 지원함으로써, 추가적인 자금 유입과 적합한 금융상품 이용으로 이어질 기회를 확보한다. 거래 관계의 유지와 확대에서 발생하는 추가 수익과 AI·시스템 운영비용을 함께 살펴, 지속할 수 있는 금융 지원으로 발전시킨다.',
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
PALE = HexColor('#F3F9FD')
LINE = HexColor('#C7DDEB')
MUTED = HexColor('#71889B')
WHITE = HexColor('#FFFFFF')

c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
c.setTitle('징검다WOORI | 05 고객의 삶과 함께 이어가는 금융 준비')
c.setAuthor('징검다WOORI')
text_regions = []


def p(text, x, top, width, size=11.5, leading=19, bold=False,
      color=INK, maxh=None, align=0):
    style = ParagraphStyle(
        'body', fontName='MGB' if bold else 'MG', fontSize=size,
        leading=leading, textColor=color, wordWrap='LTR',
        splitLongWords=False, alignment=align,
    )
    para = Paragraph(text, style)
    _, height = para.wrap(width, H)
    if maxh is not None:
        assert height <= maxh + 0.01, (text, height, maxh)
    assert M - 0.01 <= x and x + width <= W - M + 0.01
    assert top >= 20 and top + height <= 800
    para.drawOn(c, x, H - top - height)
    text_regions.append((x, top, x + width, top + height))
    return height


def line(x1, y1, x2, y2, color=LINE, width=0.65):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, H - y1, x2, H - y2)


def arrow_right(x1, x2, y):
    assert x2 - x1 >= 5
    line(x1, y, x2, y, BLUE, 0.85)
    c.setFillColor(BLUE)
    path = c.beginPath()
    path.moveTo(x2, H - y)
    path.lineTo(x2 - 3.4, H - y + 2)
    path.lineTo(x2 - 3.4, H - y - 2)
    path.close()
    c.drawPath(path, stroke=0, fill=1)


def arrow_up(x, bottom, top):
    line(x, bottom, x, top, BLUE, 0.8)
    c.setFillColor(BLUE)
    path = c.beginPath()
    path.moveTo(x, H - top)
    path.lineTo(x - 2, H - top - 3.4)
    path.lineTo(x + 2, H - top - 3.4)
    path.close()
    c.drawPath(path, stroke=0, fill=1)


def box(x, top, width, height, fill, stroke=None, radius=6):
    c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke)
        c.setLineWidth(0.65)
    c.roundRect(x, H - top - height, width, height, radius,
                fill=1, stroke=1 if stroke is not None else 0)


c.setFillColor(CYAN)
c.rect(M, H - 27, 23, 4, stroke=0, fill=1)
p('05 / 우리가 제안하는 미래 뱅킹', M + 32, 21, CW - 32,
  size=9, leading=13, bold=True, color=BLUE, maxh=13)
p('고객의 삶이 달라질 때마다,<br/>금융 준비도 함께 이어지도록',
  M, 48, CW, size=22, leading=27, bold=True, color=BLUE, maxh=54)

p(PARAGRAPHS[0], M, 127, CW, maxh=76)

# One continuous customer experience replaces evaluation-category panels.
FLOW_TOP, FLOW_H = 218, 132
box(M, FLOW_TOP, CW, FLOW_H, PALE, radius=7)
PAD, GAP = 10, 14
NODE_W = (CW - 2 * PAD - 3 * GAP) / 4
NODE_TOP, NODE_H = 235, 60
nodes = [
    ('상황 이해', '일정·목표·제약 확인'),
    ('준비와 실행 지원', '필요한 금융 업무 연결'),
    ('선택과 결과 축적', '확인한 맥락 갱신'),
    ('다음 변화에 활용', '현재 상황 재확인'),
]
node_xs = [M + PAD + i * (NODE_W + GAP) for i in range(4)]
for i in range(3):
    arrow_right(node_xs[i] + NODE_W + 3, node_xs[i + 1] - 3, NODE_TOP + NODE_H / 2)
first_center = node_xs[0] + NODE_W / 2
last_center = node_xs[-1] + NODE_W / 2
line(last_center, NODE_TOP + NODE_H, last_center, 315, BLUE, 0.8)
line(last_center, 315, first_center, 315, BLUE, 0.8)
arrow_up(first_center, 315, NODE_TOP + NODE_H + 1)
for i, ((title, body), x) in enumerate(zip(nodes, node_xs)):
    dark = i == len(nodes) - 1
    box(x, NODE_TOP, NODE_W, NODE_H, BLUE if dark else WHITE, None if dark else LINE)
    p(title, x + 5, NODE_TOP + 12, NODE_W - 10, size=10, leading=14,
      bold=True, color=WHITE if dark else BLUE, maxh=14, align=1)
    p(body, x + 5, NODE_TOP + 35, NODE_W - 10, size=8.1, leading=11.5,
      color=HexColor('#E6F5FF') if dark else INK, maxh=11.5, align=1)
p('다음 준비에서 목표와 우선순위를 다시 확인',
  M + 12, 327, CW - 24, size=8.5, leading=12, color=BLUE, maxh=12, align=1)

top = 378
for text in PARAGRAPHS[1:]:
    height = p(text, M, top, CW, maxh=95)
    top += height + 20
body_bottom = top - 20
assert body_bottom <= 681

p('징검다WOORI가 제안하는 우리WON뱅킹의 미래는<br/>'
  '고객의 삶이 달라질 때마다 금융 준비를 함께 이어가는 앱이다.',
  M, 718, CW, size=13.1, leading=21, bold=True, color=BLUE, maxh=42)

line(M, 816, W - M, 816)
c.setFillColor(MUTED)
c.setFont('MG', 7.5)
c.drawString(M, H - 829, '징검다WOORI · 고객의 삶과 함께 이어가는 금융 준비')
c.drawRightString(W - M, H - 829, '05')
c.save()

with pymupdf.open(OUT) as result:
    assert len(result) == 1
    page = result[0]
    content = page.get_text()
    assert '\ufffd' not in content
    normalize = lambda s: re.sub(r'\s+', '', s)
    for paragraph in PARAGRAPHS:
        assert normalize(paragraph) in normalize(content), 'Narrative paragraph omitted'
    for removed in ['기대효과', '실현 가능성', '수익성', '검증할 결과']:
        assert removed not in content, removed
    for expected in ['준비 부담 감소', '건당 운영비', '추가적인 자금 유입',
                     '추가 수익과 AI·시스템 운영비용', '목표와 우선순위']:
        assert expected in content, expected
    for i, a in enumerate(text_regions):
        for b in text_regions[i + 1:]:
            assert not pymupdf.Rect(a).intersects(pymupdf.Rect(b)), (a, b)
    assert content.rstrip().endswith('05')
    page.get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2)).save(QA / 'page_5.png')
    (QA / 'extracted_text.txt').write_text(content, encoding='utf-8')
    audit = {
        'pages': len(result), 'logical_page': '05',
        'narrative_paragraphs': len(PARAGRAPHS), 'customer_flow_nodes': len(nodes),
        'explicit_evaluation_headings_removed': True,
        'customer_value_deployment_and_economics_retained': True,
        'text_regions_overlap': False, 'body_bottom_y': body_bottom,
    }
    (QA / 'layout_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')

print(OUT)
print(json.dumps(audit, ensure_ascii=True))
