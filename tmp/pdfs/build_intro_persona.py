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
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader

OUT = ROOT / '보고서/징검다WOORI_제안개요_페르소나_2쪽초안.pdf'
SOURCE = ROOT / '보고서 초안/기능설명추가.pdf'
QA = ROOT / 'tmp/pdfs/intro_persona_review'
QA.mkdir(parents=True, exist_ok=True)

pdfmetrics.registerFont(TTFont('MG', 'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MGB', 'C:/Windows/Fonts/malgunbd.ttf'))
pdfmetrics.registerFontFamily('MG', normal='MG', bold='MGB', italic='MG', boldItalic='MGB')
W, H = A4
M = 42
CW = W - M * 2
BLUE = HexColor('#006CB5')
NAVY = HexColor('#143C5C')
INK = HexColor('#29445B')
MUTED = HexColor('#71889B')
LINE = HexColor('#D4E4EE')
PALE = HexColor('#EDF6FB')
audit = []
c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
c.setTitle('징검다WOORI | 제안 개요와 민우의 생애전환')
c.setAuthor('징검다WOORI')
c.setSubject('첫 페이지 제안 개요와 기존 페르소나를 연결한 2쪽 검토 초안')


def rect(x, y, w, h, color):
    c.setFillColor(color)
    c.rect(x, H - y - h, w, h, stroke=0, fill=1)


def paragraph(text, x, y, width, size=10.5, leading=17, color=INK, bold=False, maxh=None):
    style = ParagraphStyle(
        'text', fontName='MGB' if bold else 'MG', fontSize=size, leading=leading,
        textColor=color, wordWrap='LTR', splitLongWords=False,
    )
    p = Paragraph(text, style)
    _, height = p.wrap(width, H)
    if maxh is not None and height > maxh + 0.01:
        raise ValueError(f'Text exceeds allocated height: {height} > {maxh}: {text}')
    if x < M - .1 or x + width > W - M + .1 or y + height > 790:
        raise ValueError(f'Text exceeds content area: {text}')
    p.drawOn(c, x, H - y - height)
    audit.append({'page': c.getPageNumber(), 'y': y, 'height': height, 'text': text})
    return height


def chrome(label, number):
    rect(0, 0, W, 6, BLUE)
    paragraph(label, M, 32, CW, size=9, leading=13, color=BLUE, bold=True)
    c.setStrokeColor(LINE)
    c.setLineWidth(.6)
    c.line(M, H - 805, W - M, H - 805)
    c.setFillColor(MUTED)
    c.setFont('MG', 7.5)
    c.drawString(M, H - 822, '징검다WOORI · 제안 개요 및 페르소나 검토 초안')
    c.drawRightString(W - M, H - 822, f'{number:02d}')


chrome('01 / 제안하는 미래 뱅킹', 1)
paragraph('내 금융 생활을 함께 관리하는<br/>우리WON뱅킹의 미래', M, 63, CW,
          size=24, leading=30, color=BLUE, bold=True)
paragraph('징검다WOORI: 마이플래너 기반 AI Agent를 활용한 개인화 금융 서비스',
          M, 137, CW, size=10.7, leading=16, color=BLUE, bold=True)
paragraph('우리는 미래의 우리WON뱅킹을 고객의 생활이 달라질 때마다 필요한 금융 준비를 함께 정리하고, '
          '그 계획을 일상의 선택까지 이어가는 앱으로 제안한다.',
          M, 174, CW, size=10.8, leading=17, maxh=34)
paragraph('생활 변화에 따라 달라지는 금융 준비를 개별 업무와 연결하고, '
          '실행 이후의 변화까지 반영하는 것이 제안의 핵심이다.',
          M, 222, CW, size=10.8, leading=17, maxh=34)
c.setStrokeColor(LINE)
c.setLineWidth(.8)
c.line(M, H - 271, W - M, H - 271)
paragraph('마이플래너를 중심으로 금융생활을 연결하는 AI Agent',
          M, 288, CW, size=13.5, leading=20, color=BLUE, bold=True)
paragraph('<b>마이플래너의 일정과 목표를 중심으로 고객의 금융생활을 연결한다.</b> '
          'AI Agent는 고객의 생활 맥락과 활용을 허용한 금융정보를 함께 살펴, '
          '필요한 준비부터 일상 거래와 이후의 계획 조정까지 지원한다.',
          M, 320, CW, size=10.4, leading=16.4, maxh=49.2)

cards = [
    ('상황에 맞는 준비 제안',
     '고객의 일정·목표와 금융 상황을 함께 살피고, 필요한 내용을 고객에게 확인해 '
     '지금 준비할 일과 앞으로 확인할 일을 제안한다.'),
    ('일상 금융업무와 연결',
     '송금·입금·큰 지출이 납부와 목표에 미치는 영향을 살핀다. '
     '고객이 선택한 준비는 저축·납부 등 필요한 은행 업무로 이어지도록 돕는다.'),
    ('변화와 결과를 반영한 후속 관리',
     '준비 과제의 진행 결과와 수입·지출·일정 변화를 반영해 현재 계획을 갱신한다. '
     '달라진 상황에 맞춰 필요한 조정과 후속 과제를 제안한다.'),
    ('장기 기억으로 이어지는 개인화',
     '고객이 확인한 목표·제약·선택과 실행 결과를 장기 기억으로 축적·갱신한다. '
     '이전의 맥락을 활용해 다음 생활 변화에서도 고객의 우선순위에 맞는 준비를 제안한다.'),
]
for i, (title, body) in enumerate(cards):
    top = 378 + i * 83
    rect(M, top, CW, 75, PALE)
    paragraph(f'{i + 1:02d}', M + 12, top + 12, 26,
              size=10.5, leading=15, color=BLUE, bold=True)
    paragraph(title, M + 48, top + 10, CW - 60,
              size=11, leading=16, color=BLUE, bold=True)
    paragraph(body, M + 48, top + 31, CW - 62,
              size=9.5, leading=13.5, maxh=40.5)

rect(M, 716, CW, 64, BLUE)
paragraph('고객의 생활 계획을 중심으로 준비·거래·관리를 연결하고,<br/>'
          '확인한 목표와 선택을 다음 금융 준비까지 이어간다.',
          M + 12, 725, CW - 24, size=10.3, leading=15, color=white, bold=True, maxh=30)
paragraph('이러한 연결이 필요한 순간을, 가상 고객 민우의 삶을 통해 살펴본다.',
          M + 12, 762, CW - 24, size=9.3, leading=13, color=white, maxh=13)
c.showPage()

chrome('02 / 민우의 생애전환과 준비 부담', 2)
paragraph('민우의 삶이 달라질 때,<br/>금융 준비의 어려움도 달라진다',
          M, 63, CW, size=24, leading=30, color=BLUE, bold=True)
paragraph('성인·진학부터 취업·독립까지 이어지는 한 사람의 여정',
          M, 137, CW, size=11.5, leading=17, color=NAVY, bold=True)
paragraph('민우는 성인·진학, 첫 수입·반독립, 입대·전역, 첫 취업·독립을 거친다. '
          '같은 사람이라도 생활이 달라지면 돈의 목적과 준비해야 할 일이 바뀐다. '
          '네 장면을 통해, 금융업무와 자금 계획을 자신의 상황에 맞게 연결해야 하는 순간을 살펴본다.',
          M, 174, CW, size=10.5, leading=17, maxh=68)

# Reuse the original embedded persona image without changing its pixels.
source = pymupdf.open(SOURCE)
img_info = source[1].get_images(full=True)
assert len(img_info) == 1, 'Expected the original single persona image'
persona = source.extract_image(img_info[0][0])
image_height = CW * persona['height'] / persona['width']
c.drawImage(ImageReader(BytesIO(persona['image'])), M, H - 252 - image_height,
            width=CW, height=image_height, mask='auto')

paragraph('네 장면을 관통하는 하나의 어려움',
          M, 532, CW, size=12.4, leading=18, color=NAVY, bold=True)
paragraph('민우가 공통으로 겪는 어려움은 변화마다 필요한 금융업무와 자금 계획을 '
          '스스로 연결해야 한다는 것이다. 같은 상황이라도 목표와 여력이 다르므로, '
          '고객이 확인한 실제 계획을 기준으로 준비를 구체화해야 한다.',
          M, 560, CW, size=10.5, leading=17, maxh=51)

rect(M, 637, CW, 112, PALE)
paragraph('첫 취업·독립을 맞은 민우에게 초점을 맞추면',
          M + 12, 649, CW - 24, size=12, leading=18, color=NAVY, bold=True)
paragraph('취업한 민우는 독립을 준비하며 월세·생활비와 저축을 함께 지키고 싶다. '
          '준비할 일을 정리한 뒤에도 송금, 새로운 입금, 큰 지출이 계획에 어떤 영향을 주는지 판단해야 한다.',
          M + 12, 679, CW - 24, size=10.5, leading=17, maxh=34)
paragraph('이제 민우의 독립 준비와 일상의 선택을 징검다WOORI가 이어가는 과정을 살펴본다.',
          M + 12, 725, CW - 24, size=10, leading=15, color=NAVY, bold=True, maxh=15)
c.save()

with pymupdf.open(OUT) as result:
    assert len(result) == 2
    for i, page in enumerate(result):
        page.get_pixmap(matrix=pymupdf.Matrix(1.7, 1.7)).save(QA / f'page_{i+1}.png')
    text = '\n'.join(p.get_text() for p in result)
    assert '\ufffd' not in text
    assert '가상 고객 민우의 삶' in text
    assert '첫 취업·독립을 맞은 민우' in text
    # Confirm that the reused image preserves the original dimensions and pixels.
    embedded = result[1].get_images(full=True)
    assert len(embedded) == 1
    old_pixels = pymupdf.Pixmap(source, img_info[0][0])
    new_pixels = pymupdf.Pixmap(result, embedded[0][0])
    assert old_pixels.width == new_pixels.width
    assert old_pixels.height == new_pixels.height
    assert old_pixels.samples == new_pixels.samples

(QA / 'layout_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
print(OUT)
print('Verified: 2 pages; original persona image pixels preserved; page previews rendered.')
