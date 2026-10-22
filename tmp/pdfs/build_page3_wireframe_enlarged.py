from pathlib import Path
from io import BytesIO
import sys
from PIL import Image

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
from reportlab.lib.utils import ImageReader
from step_card_style import draw_step_card

SOURCE = ROOT / '보고서 초안/기능설명추가.pdf'
OUT = ROOT / '보고서/징검다WOORI_3페이지_좌측설명_와이어프레임확대.pdf'
QA = ROOT / 'tmp/pdfs/page3_wireframe_enlarged_review'
QA.mkdir(parents=True, exist_ok=True)
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
c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
c.setTitle('징검다WOORI | 03 독립 준비와 송금 - 기능 및 AI 적용')
c.setAuthor('징검다WOORI')


def p(text, x, y, width, size=9.6, leading=14, color=INK, bold=False, maxh=None, align=0):
    style = ParagraphStyle('text', fontName='MGB' if bold else 'MG', fontSize=size,
                           leading=leading, textColor=color, wordWrap='LTR',
                           splitLongWords=False, alignment=align)
    para = Paragraph(text, style)
    _, height = para.wrap(width, H)
    if maxh is not None and height > maxh + .01:
        raise ValueError(f'Text overflow {height} > {maxh}: {text}')
    assert x >= M - .1 and x + width <= W - M + .1
    assert y + height <= 808
    para.drawOn(c, x, H - y - height)
    return height


def rule(x1, y1, x2, y2, color=LINE, width=.65):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, H - y1, x2, H - y2)


def arrow(x1, x2, y):
    rule(x1, y, x2, y, BLUE, 1)
    c.setFillColor(BLUE)
    path = c.beginPath()
    path.moveTo(x2, H - y)
    path.lineTo(x2 - 4, H - y + 2.2)
    path.lineTo(x2 - 4, H - y - 2.2)
    path.close()
    c.drawPath(path, stroke=0, fill=1)


c.setFillColor(CYAN)
c.rect(M, H - 27, 23, 4, stroke=0, fill=1)
p('03 / 금융 준비와 거래에 적용하는 AI Agent', M + 32, 21, CW - 32,
  size=9, leading=13, color=BLUE, bold=True)
p('독립 준비부터 송금까지,<br/>계획에 맞는 선택을 돕는다',
  M, 44, CW, size=22, leading=25, color=BLUE, bold=True, maxh=50)
p('AI Agent가 고객 맥락을 해석해 필요한 준비와 대안을 구성하고, 조회·계산·기록 도구를 연결한다. '
  '고객이 선택한 준비와 실제 거래 결과는 같은 계획에 반영한다.',
  M, 104, CW, size=9.7, leading=14, maxh=28)

source = pymupdf.open(SOURCE)
source_page = source[2]
all_images = []
for info in source_page.get_images(full=True):
    bounds = source_page.get_image_rects(info[0])[0]
    all_images.append((bounds.y0, bounds.x0, info[0]))
top = sorted([item for item in all_images if item[0] < 300], key=lambda item: item[1])
bottom = sorted([item for item in all_images if item[0] > 500], key=lambda item: item[1])
assert len(top) == 3 and len(bottom) == 3
used_xrefs = []


def feature(top_y, number, title, context, steps, image_items, labels):
    c.setStrokeColor(LINE)
    c.setLineWidth(.7)
    c.roundRect(M, H - top_y - 320, CW, 320, 7, stroke=1, fill=0)
    c.setFillColor(BLUE)
    c.roundRect(M + 8, H - top_y - 32, 24, 18, 4, stroke=0, fill=1)
    p(number, M + 8, top_y + 15, 24, size=9.2, leading=13,
      color=HexColor('#FFFFFF'), bold=True, align=1, maxh=13)
    p(title, M + 39, top_y + 12, 135, size=11.5, leading=16,
      color=BLUE, bold=True, maxh=32)
    left_x = M + 8
    left_w = 166
    p(context, left_x, top_y + 57, left_w, size=9.2, leading=14,
      maxh=42)
    card_w = (left_w - 8) / 2
    cards_y = top_y + 112
    for i, (step_title, body) in enumerate(steps):
        x = left_x + (i % 2) * (card_w + 8)
        y = cards_y + (i // 2) * 104
        draw_step_card(c, x, y, card_w, 96, H)
        p(f'{i + 1:02d}  {step_title}', x + 7, y + 8, card_w - 14,
          size=8.5, leading=12, color=BLUE, bold=True, maxh=12)
        p(body, x + 7, y + 25, card_w - 14,
          size=8.3, leading=10.1, maxh=70.7)
    right_x = M + 190
    right_w = CW - 198
    column = right_w / 2
    image_h = 284
    extents = []
    for i, (item, label) in enumerate(zip(image_items, labels)):
        xref = item[2]
        used_xrefs.append(xref)
        p(label, right_x + i * column, top_y + 8, column,
          size=9.2, leading=13, color=BLUE, bold=True, align=1, maxh=13)
        image = source.extract_image(xref)
        image_w = image_h * image['width'] / image['height']
        x = right_x + i * (right_w - image_w)
        c.drawImage(ImageReader(BytesIO(image['image'])), x,
                    H - top_y - 28 - image_h, width=image_w, height=image_h, mask='auto')
        extents.append((x, x + image_w))


feature(142, '01', '독립 일정을<br/>준비 미션으로 연결',
        '독립 일정과 금융 현황을 바탕으로, 준비할 일을 미션과 일정으로 구체화한다.',
        [
            ('정보 조회', '조회 도구로 일정·목표와 허용된 잔액·예정 납부를 불러온다.'),
            ('맥락 확인', 'AI가 새 생활비와 우선 목표를 묻고, 누락된 맥락을 보완한다.'),
            ('진단·계획', '계산 도구로 자금 여력을 확인한 뒤, AI가 준비 순서를 정한다.'),
            ('미션 저장', '선택한 준비를 기한·완료 조건이 있는 미션으로 저장한다.'),
        ], top[:2], ['준비 제안', '추천 준비 확인'])

feature(472, '02', '송금이 예정 납부에<br/>미치는 영향 확인',
        '송금 이후의 자금 흐름을 미리 계산해, 납부 부족 위험과 대응안을 안내한다.',
        [
            ('정보 조회', '조회 도구로 송금액·잔액과 예정 납부·급여 일정을 불러온다.'),
            ('부족액 계산', '계산 도구로 납부일별 잔액과 부족액을 산출한다.'),
            ('대안 구성', 'AI가 송금액 조정·다른 가용자금 활용 등의 대응안을 구성한다.'),
            ('실행·갱신', '기존 인증 후 실제 송금 결과와 고객의 선택을 계획에 반영한다.'),
        ], bottom[:2], ['납부 부족 위험 확인', '대응안 선택'])

p('화면·금액은 가상 예시이며, 데이터 조회·도구 호출·미션 연동은 제안하는 구현 구조다.',
  M, 798, CW, size=7.2, leading=10, color=MUTED, maxh=10)
rule(M, 816, W - M, 816)
c.setFillColor(MUTED)
c.setFont('MG', 7.5)
c.drawString(M, H - 829, '징검다WOORI · 기능 설명 및 AI 적용 시안')
c.drawRightString(W - M, H - 829, '03')
c.save()

with pymupdf.open(OUT) as result:
    assert len(result) == 1
    text = result[0].get_text()
    assert '\ufffd' not in text
    assert '미션 저장' in text and '부족액 계산' in text
    images = result[0].get_images(full=True)
    assert len(images) == 4
    samples = {pymupdf.Pixmap(source, xref).samples for xref in used_xrefs}
    for image in images:
        assert pymupdf.Pixmap(result, image[0]).samples in samples
    result[0].get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2)).save(QA / 'page_3.png')
print(OUT)
print('Verified: page 03; all function titles and descriptions on left; four source wireframes enlarged from 244pt to 284pt.')
