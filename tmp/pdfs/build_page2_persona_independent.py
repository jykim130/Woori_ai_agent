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
OUT = ROOT / '보고서/징검다WOORI_2페이지_페르소나_독립상황추가시안.pdf'
QA = ROOT / 'tmp/pdfs/page2_persona_independent_review'
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


p('첫 독립을 준비하는 민우,<br/>계획은 일상에서도 계속 바뀐다',
  M, 444, CW, size=15.5, leading=20, bold=True, color=BLUE, maxh=40)

p('민우는 월세와 생활비를 감당하면서 비상금과 저축 목표도 지키고 싶다. '
  '독립 준비 중에도 송금, 예상 밖의 입금, 큰 지출이 기존 계획에 어떤 영향을 주는지 판단해야 한다.',
  M, 497, CW, size=9.8, leading=14.5, maxh=43.5)

TABLE_TOP = 548
HEADER_H = 26
ROW_H = 39
TABLE_H = HEADER_H + 4 * ROW_H
DIVIDER = 300

c.saveState()
clip = c.beginPath()
clip.roundRect(M, H - TABLE_TOP - TABLE_H, CW, TABLE_H, 6)
c.clipPath(clip, stroke=0, fill=0)
c.setFillColor(PALE)
c.rect(M, H - TABLE_TOP - HEADER_H, CW, HEADER_H, stroke=0, fill=1)
for i in range(4):
    c.setFillColor(HexColor('#FFFFFF' if i % 2 == 0 else '#F8FCFE'))
    top = TABLE_TOP + HEADER_H + i * ROW_H
    c.rect(M, H - top - ROW_H, CW, ROW_H, stroke=0, fill=1)
c.restoreState()

c.setStrokeColor(LINE)
c.setLineWidth(0.65)
c.roundRect(M, H - TABLE_TOP - TABLE_H, CW, TABLE_H, 6, stroke=1, fill=0)
c.line(DIVIDER, H - TABLE_TOP, DIVIDER, H - TABLE_TOP - TABLE_H)
for i in range(4):
    top = TABLE_TOP + HEADER_H + i * ROW_H
    c.line(M, H - top, W - M, H - top)

p('민우가 마주하는 순간', M + 13, TABLE_TOP, DIVIDER - M - 26,
  size=9.3, leading=13, color=BLUE, bold=True, center_in=HEADER_H)
p('그때 필요한 도움', DIVIDER + 14, TABLE_TOP, W - M - DIVIDER - 28,
  size=9.3, leading=13, color=BLUE, bold=True, center_in=HEADER_H)

rows = [
    ('독립 일정을 등록했을 때', '무엇부터 준비해야 할지 정리'),
    ('돈을 보내려 할 때', '예정된 월세와 생활비에 미치는 영향 확인'),
    ('예상 밖의 보너스가 들어왔을 때', '비상금과 독립자금에 맞는 활용 방향 선택'),
    ('노트북을 구매하려 할 때', '구매 후 납부 여력과 구매 시점 점검'),
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
c.roundRect(M, H - 750 - 46, CW, 46, 6, stroke=0, fill=1)
p('민우가 확인한 목표와 일정, 선택을 공유하며<br/>'
  '준비부터 일상의 판단까지 하나의 계획으로 이어간다.',
  M + 12, 758, CW - 24, size=10.5, leading=15, bold=True,
  color=BLUE, maxh=30)

c.setStrokeColor(LINE)
c.setLineWidth(0.65)
c.line(M, H - 816, W - M, H - 816)
c.setFillColor(MUTED)
c.setFont('MG', 7.5)
c.drawString(M, H - 829, '징검다WOORI · 페르소나와 일상 금융 경험')
c.drawRightString(W - M, H - 829, '02')
c.save()

with pymupdf.open(SOURCE) as result:
    with pymupdf.open(stream=stream.getvalue(), filetype='pdf') as overlay:
        result[0].show_pdf_page(result[0].rect, overlay, 0)
    metadata = result.metadata
    metadata.update({
        'title': '징검다WOORI | 02 민우의 금융 여정과 첫 독립',
        'author': '징검다WOORI',
        'subject': '대표 페르소나에서 준비·송금·입금·큰 지출 경험으로 이어지는 구성',
    })
    result.set_metadata(metadata)
    result.save(OUT, garbage=4, deflate=True)

with pymupdf.open(SOURCE) as source, pymupdf.open(OUT) as result:
    assert len(result) == 1
    original, page = source[0], result[0]
    content = page.get_text()
    assert '\ufffd' not in content
    assert original.get_text() in content
    for expected in ['첫 독립을 준비하는 민우', '노트북을 구매하려 할 때',
                     '무엇부터 준비해야 할지 정리', '하나의 계획으로 이어간다.']:
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
        'added_situations': len(rows), 'added_text_regions_overlap': False,
        'replacement_characters': False,
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    }
    (QA / 'layout_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')

print(OUT)
print(json.dumps(audit, ensure_ascii=True))
