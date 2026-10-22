from io import BytesIO
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'tmp/pdf-author-deps'), str(ROOT / 'tmp/pdf-deps')]

import pymupdf
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

SOURCE = ROOT / '보고서/징검다WOORI_2페이지_페르소나_반페이지시안 (1).pdf'
OUT = ROOT / '보고서/징검다WOORI_2페이지_페르소나_금융준비부담수정본.pdf'
QA = ROOT / 'tmp/pdfs/page2_persona_preparation_burden_review'
QA.mkdir(parents=True, exist_ok=True)

pdfmetrics.registerFont(TTFont('MG', 'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MGB', 'C:/Windows/Fonts/malgunbd.ttf'))
pdfmetrics.registerFontFamily('MG', normal='MG', bold='MGB', italic='MG', boldItalic='MGB')

with pymupdf.open(SOURCE) as source:
    assert len(source) == 1
    W, H = source[0].rect.width, source[0].rect.height

M = 32
CW = W - 2 * M
BLUE = HexColor('#006CAF')
INK = HexColor('#29495F')
PALE = HexColor('#ECF6FB')
LINE = HexColor('#C7DDEB')
MUTED = HexColor('#71889B')
stream = BytesIO()
c = canvas.Canvas(stream, pagesize=(W, H), pageCompression=1)
text_regions = []


def p(text, x, top, width, size=9.8, leading=14.5, bold=False,
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
        assert height <= center_in
        top += (center_in - height) / 2
    assert x >= M - 0.01 and x + width <= W - M + 0.01
    assert top >= 440 and top + height <= 806
    para.drawOn(c, x, H - top - height)
    text_regions.append((x, top, x + width, top + height))
    return height


p('내 상황에 맞는 금융 준비,<br/>아직 고객이 직접 연결해야 한다',
  M, 444, CW, size=15.5, leading=20, bold=True, color=BLUE, maxh=40)

p('민우는 필요한 정보와 기능을 찾고, 자신의 조건과 비교해 실행 계획으로 엮어야 한다.<br/>'
  '생활이 달라질 때마다 이 과정을 다시 수행하는 부담이 생긴다.',
  M, 497, CW, size=9.8, leading=14.5, maxh=43.5)

TABLE_TOP = 540
HEADER_H = 26
ROW_H = 52
TABLE_H = HEADER_H + 3 * ROW_H
DIVIDER = 226

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
c.line(DIVIDER, H - TABLE_TOP, DIVIDER, H - TABLE_TOP - TABLE_H)
for i in range(3):
    top = TABLE_TOP + HEADER_H + i * ROW_H
    c.line(M, H - top, W - M, H - top)

p('고객에게 남는 부담', M + 13, TABLE_TOP, DIVIDER - M - 26,
  size=9.3, leading=13, color=BLUE, bold=True, center_in=HEADER_H)
p('민우의 상황에 적용하면', DIVIDER + 14, TABLE_TOP, W - M - DIVIDER - 28,
  size=9.3, leading=13, color=BLUE, bold=True, center_in=HEADER_H)

rows = [
    ('찾고 비교하는 시간', '지금 필요한 정보와 기능을 찾고, 여러 조건을 확인해야 한다.'),
    ('계획을 완성하는 노력', '수입·납부·저축 목표를 함께 계산하고, 준비 순서와 실행 일정을 직접 정해야 한다.'),
    ('생활 맥락을 반영한<br/>개인화', '자신의 목표·자금 용도·우선순위에 맞게 안내를 해석하고, 이전 선택과 연결해야 한다.'),
]
for i, (moment, help_text) in enumerate(rows):
    top = TABLE_TOP + HEADER_H + i * ROW_H
    badge_top = top + (ROW_H - 18) / 2
    c.setFillColor(BLUE)
    c.roundRect(M + 13, H - badge_top - 18, 20, 18, 4, stroke=0, fill=1)
    p(f'{i + 1:02d}', M + 13, badge_top, 20, size=8.2, leading=11.5,
      bold=True, color=HexColor('#FFFFFF'), center_in=18, align=1)
    p(moment, M + 43, top, DIVIDER - M - 55, size=9.4, leading=13.5,
      bold=True, maxh=27, center_in=ROW_H)
    p(help_text, DIVIDER + 14, top, W - M - DIVIDER - 28,
      size=9.6, leading=13.5, maxh=27, center_in=ROW_H)

c.setFillColor(PALE)
c.roundRect(M, H - 742 - 50, CW, 50, 6, stroke=0, fill=1)
p('민우에게 필요한 것은 자신의 상황을 이해하고,<br/>'
  '필요한 준비부터 실행과 이후의 조정까지 함께 이어주는 지원이다.',
  M + 12, 752, CW - 24, size=10.3, leading=15, bold=True,
  color=BLUE, maxh=30)

c.setStrokeColor(LINE)
c.setLineWidth(0.65)
c.line(M, H - 816, W - M, H - 816)
c.setFillColor(MUTED)
c.setFont('MG', 7.5)
c.drawString(M, H - 829, '징검다WOORI · 페르소나와 금융 준비의 부담')
c.drawRightString(W - M, H - 829, '02')
c.save()

with pymupdf.open(SOURCE) as result:
    with pymupdf.open(stream=stream.getvalue(), filetype='pdf') as overlay:
        result[0].show_pdf_page(result[0].rect, overlay, 0)
    metadata = result.metadata
    metadata.update({
        'title': '징검다WOORI | 02 민우의 금융 여정과 준비 부담',
        'author': '징검다WOORI',
        'subject': '정보 탐색의 시간, 계획 수립의 노력, 생활 맥락을 반영한 개인화의 필요',
    })
    result.set_metadata(metadata)
    result.save(OUT, garbage=4, deflate=True)

with pymupdf.open(SOURCE) as source, pymupdf.open(OUT) as result:
    assert len(result) == 1
    original, page = source[0], result[0]
    content = page.get_text()
    assert '\ufffd' not in content
    assert '이제 첫 취업·독립을 맞은 민우에게' not in content
    assert original.get_text() in content
    for expected in ['내 상황에 맞는 금융 준비', '아직 고객이 직접 연결해야 한다',
                     '찾고 비교하는 시간', '계획을 완성하는 노력',
                     '생활 맥락을 반영한', '개인화',
                     '필요한 준비부터 실행과 이후의 조정까지 함께 이어주는 지원이다.']:
        assert expected in content, expected
    upper = pymupdf.Rect(0, 0, W, 430)
    before = original.get_pixmap(matrix=pymupdf.Matrix(2, 2), clip=upper)
    after = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), clip=upper)
    assert before.samples == after.samples, 'The original upper section changed'
    for i, a in enumerate(text_regions):
        for b in text_regions[i + 1:]:
            assert not pymupdf.Rect(a).intersects(pymupdf.Rect(b)), (a, b)
    page.get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2)).save(QA / 'page_2.png')
    (QA / 'extracted_text.txt').write_text(content, encoding='utf-8')
    audit = {
        'pages': len(result), 'logical_page': '02',
        'original_upper_section_preserved_pixel_for_pixel': True,
        'preparation_burdens': len(rows), 'forced_page_transition_removed': True, 'added_text_regions_overlap': False,
        'replacement_characters': False,
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    }
    (QA / 'layout_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')

print(OUT)
print(json.dumps(audit, ensure_ascii=True))
