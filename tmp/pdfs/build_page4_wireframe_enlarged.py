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
OUT = ROOT / '보고서/징검다WOORI_4페이지_좌측설명_와이어프레임확대.pdf'
QA = ROOT / 'tmp/pdfs/page4_wireframe_enlarged_review'
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
c.setTitle('징검다WOORI | 04 입금과 큰 지출 - 기능 및 AI 적용')
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


c.setFillColor(CYAN)
c.rect(M, H - 27, 23, 4, stroke=0, fill=1)
p('04 / 금융 준비와 거래에 적용하는 AI Agent', M + 32, 21, CW - 32,
  size=9, leading=13, color=BLUE, bold=True)
p('입금과 큰 지출에도,<br/>계획에 맞는 선택을 돕는다',
  M, 44, CW, size=22, leading=25, color=BLUE, bold=True, maxh=50)
p('AI Agent가 입금의 성격과 구매 맥락을 확인하고, 계산 도구로 기존 계획에 미치는 영향을 살핀다. '
  '고객이 선택한 배분안과 실제 결제 결과를 계획과 미션에 반영한다.',
  M, 104, CW, size=9.7, leading=14, maxh=28)

source = pymupdf.open(SOURCE)
source_page = source[3]
all_images = []
for info in source_page.get_images(full=True):
    bounds = source_page.get_image_rects(info[0])[0]
    all_images.append((bounds.y0, bounds.x0, info[0]))
top = sorted([item for item in all_images if item[0] < 300], key=lambda item: item[1])
bottom = sorted([item for item in all_images if item[0] > 500], key=lambda item: item[1])
assert len(top) == 3 and len(bottom) == 4
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


feature(142, '03', '입금 성격에 맞춰<br/>자금 활용 계획 조정',
        '예상 밖의 입금이 생기면 돈의 성격을 확인하고, 기존 목표에 맞는 활용안을 제안한다.',
        [
            ('정보 조회', '조회 도구로 입금 내역과 기존 목표·비상금 현황을 불러온다.'),
            ('맥락 확인', 'AI가 입금 성격과 반복 여부를 물어 소득·환불·계좌 이동을 구분한다.'),
            ('배분안 구성', '계산 도구로 여유 자금을 확인하고, AI가 비상금·목표자금 배분안을 구성한다.'),
            ('계획 갱신', '고객이 선택한 배분안을 계획과 관련 미션·일정에 반영한다.'),
        ], top[:2], ['입금 성격 확인', '자금 활용 방향 선택'])

feature(472, '04', '큰 지출이 예정 납부에<br/>미치는 영향 확인',
        '큰 지출 이후의 자금 흐름을 미리 계산해, 예정 납부와 비상금에 미치는 영향을 안내한다.',
        [
            ('정보 조회', '조회 도구로 구매 금액·결제수단과 잔액·예정 납부를 불러온다.'),
            ('영향 계산', '계산 도구로 출금 시점별 잔액과 납부 부족액을 산출한다.'),
            ('대안 구성', 'AI가 구매 시점·금액 조정과 다른 결제 방법을 대안으로 구성한다.'),
            ('선택·반영', '고객의 결제 선택을 확인하고, 실제 결제 결과를 계획에 반영한다.'),
        ], bottom[1:3], ['납부 부족 알림', '자금 흐름 상세'])

p('화면·금액은 가상 예시이며, 데이터 조회·도구 호출·미션 연동은 제안하는 구현 구조다.',
  M, 798, CW, size=7.2, leading=10, color=MUTED, maxh=10)
rule(M, 816, W - M, 816)
c.setFillColor(MUTED)
c.setFont('MG', 7.5)
c.drawString(M, H - 829, '징검다WOORI · 기능 설명 및 AI 적용 시안')
c.drawRightString(W - M, H - 829, '04')
c.save()

with pymupdf.open(OUT) as result:
    assert len(result) == 1
    text = result[0].get_text()
    assert '\ufffd' not in text
    assert '배분안 구성' in text and '선택·반영' in text
    images = result[0].get_images(full=True)
    assert len(images) == 4
    samples = {pymupdf.Pixmap(source, xref).samples for xref in used_xrefs}
    for image in images:
        assert pymupdf.Pixmap(result, image[0]).samples in samples
    result[0].get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2)).save(QA / 'page_4.png')
print(OUT)
print('Verified: page 04; two functions with 2x2 explanation cards on left; four original source wireframes at 284pt height on right; no arrows.')
