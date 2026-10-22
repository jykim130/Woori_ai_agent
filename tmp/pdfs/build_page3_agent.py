from pathlib import Path
from io import BytesIO
import json
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

SOURCE = ROOT / '보고서 초안/기능설명추가.pdf'
OUT = ROOT / '보고서/징검다WOORI_3페이지_독립준비_AI적용시안.pdf'
QA = ROOT / 'tmp/pdfs/page3_agent_review'
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
audit = []
c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
c.setTitle('징검다WOORI | 03 독립 준비와 AI Agent 적용')
c.setAuthor('징검다WOORI')
c.setSubject('기존 준비 제안 와이어프레임과 정보 조회·맥락 해석·도구 활용·미션 생성의 제안 구조')


def p(text, x, y, width, size=10.3, leading=16, color=INK, bold=False, maxh=None, align=0):
    style = ParagraphStyle('text', fontName='MGB' if bold else 'MG', fontSize=size,
                           leading=leading, textColor=color, wordWrap='LTR',
                           splitLongWords=False, alignment=align)
    para = Paragraph(text, style)
    _, height = para.wrap(width, H)
    if maxh is not None and height > maxh + .01:
        raise ValueError(f'Text overflow {height} > {maxh}: {text}')
    assert x >= M - .1 and x + width <= W - M + .1
    assert y + height <= 801
    para.drawOn(c, x, H - y - height)
    audit.append({'y': y, 'height': height, 'text': text})
    return height


def line(x1, y1, x2, y2, color=LINE, width=.65):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, H - y1, x2, H - y2)


def arrow(x1, x2, y):
    line(x1, y, x2, y, BLUE, 1.1)
    c.setFillColor(BLUE)
    path = c.beginPath()
    path.moveTo(x2, H - y)
    path.lineTo(x2 - 4.5, H - y + 2.4)
    path.lineTo(x2 - 4.5, H - y - 2.4)
    path.close()
    c.drawPath(path, stroke=0, fill=1)


c.setFillColor(CYAN)
c.rect(M, H - 27, 23, 4, stroke=0, fill=1)
p('03 / 독립 준비와 AI Agent 적용', M + 32, 21, CW - 32,
  size=9, leading=13, color=BLUE, bold=True)
p('민우의 독립 일정을<br/>실행할 금융 준비로 연결한다',
  M, 57, CW, size=23, leading=28, color=BLUE, bold=True, maxh=56)
p('민우는 독립을 앞두고 월세·생활비·저축을 어떤 순서로 준비해야 할지 고민한다. '
  '징검다WOORI는 일정과 금융정보를 함께 확인하고, 민우가 선택한 준비를 실행할 미션으로 연결한다.',
  M, 130, CW, size=10.3, leading=16, maxh=48)

source = pymupdf.open(SOURCE)
source_page = source[2]
top_images = []
for info in source_page.get_images(full=True):
    positions = source_page.get_image_rects(info[0])
    if positions and positions[0].y0 < 300:
        top_images.append((positions[0].x0, info[0]))
top_images.sort()
assert len(top_images) == 3

labels = ['준비 제안', '추천 준비 확인', '미션 진행 관리']
col = CW / 3
screen_height = 199
screen_rects = []
for i, ((_, xref), label) in enumerate(zip(top_images, labels)):
    p(label, M + i * col, 188, col, size=10, leading=15,
      color=BLUE, bold=True, align=1, maxh=15)
    image = source.extract_image(xref)
    screen_width = screen_height * image['width'] / image['height']
    x = M + i * col + (col - screen_width) / 2
    c.drawImage(ImageReader(BytesIO(image['image'])), x, H - 211 - screen_height,
                width=screen_width, height=screen_height, mask='auto')
    screen_rects.append((x, x + screen_width))
for i in range(2):
    arrow(screen_rects[i][1] + 11, screen_rects[i+1][0] - 11, 310)

p('독립 일정에서 필요한 준비를 제안하고, 고객이 선택한 과제를 마이플래너의 일정과 미션으로 관리한다.',
  M, 425, CW, size=10.2, leading=16, maxh=32)
line(M, 466, W - M, 466)
p('화면 뒤에서 AI Agent가 수행하는 과정',
  M, 479, CW, size=12.5, leading=18, color=BLUE, bold=True)
p('AI Agent는 맥락 해석·질문·대안 구성을, 조회·계산·기록 도구는 정해진 처리를 맡는다.',
  M, 507, CW, size=8.8, leading=13, color=MUTED, maxh=13)

steps = [
    ('정보 조회',
     '독립 일정이 등록되면 AI Agent가 조회 도구를 호출해 일정·목표와 활용을 허용한 계좌 잔액·예정 납부 정보를 불러온다. '
     '정보의 출처와 조회 시점을 함께 확인한다.'),
    ('맥락 해석·질문',
     'AI Agent는 독립 일정과 금융 현황을 바탕으로 필요한 준비와 누락 정보를 파악한다. '
     '월세·관리비 등 새로 부담할 비용과 우선 지킬 목표는 고객에게 확인한다.'),
    ('계산·대안 구성',
     '확인한 금액과 지급일을 자금흐름 계산 도구에 전달한다. 도구가 날짜별 예상 잔액과 부족액을 계산하면, '
     'AI Agent가 비상금·저축 목표에 맞는 조정 대안을 구성한다.'),
    ('미션 생성·저장',
     '고객이 선택한 대안을 기한·선후관계·완료 조건을 가진 미션으로 구조화한다. '
     '일정·미션 관리 기능에 저장하고, 은행 업무 결과나 고객 확인을 받아 진행 상태를 갱신한다.'),
]
for i, (title, body) in enumerate(steps):
    y = 531 + i * 62
    c.setFillColor(PALE)
    c.roundRect(M, H - y - 56, CW, 56, 5, stroke=0, fill=1)
    p(f'{i + 1:02d}', M + 10, y + 11, 21, size=9.5, leading=14,
      color=BLUE, bold=True, maxh=14)
    p(title, M + 37, y + 10, 78, size=10, leading=14,
      color=BLUE, bold=True, maxh=28)
    p(body, M + 129, y + 7, CW - 141, size=9.4, leading=14,
      maxh=42)

p('화면은 서비스 흐름의 예시이며, 데이터 조회·도구 호출·미션 연동은 제안하는 구현 구조다.',
  M, 789, CW, size=7.2, leading=10, color=MUTED, maxh=10)
line(M, 813, W - M, 813)
c.setFillColor(MUTED)
c.setFont('MG', 7.5)
c.drawString(M, H - 829, '징검다WOORI · 기능 설명 및 AI 적용 시안')
c.drawRightString(W - M, H - 829, '03')
c.save()

with pymupdf.open(OUT) as result:
    assert len(result) == 1
    page = result[0]
    text = page.get_text()
    assert '자금흐름 계산 도구' in text
    assert '\ufffd' not in text
    images = page.get_images(full=True)
    assert len(images) == 3
    original_samples = {pymupdf.Pixmap(source, xref).samples for _, xref in top_images}
    for image in images:
        assert pymupdf.Pixmap(result, image[0]).samples in original_samples
    page.get_pixmap(matrix=pymupdf.Matrix(2, 2)).save(QA / 'page_3.png')
    (QA / 'extracted_text.txt').write_text(text, encoding='utf-8')
(QA / 'layout_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
print(OUT)
print('Verified: one page, numbered 03; three original wireframes preserved; rendered for review.')
