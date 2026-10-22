from pathlib import Path
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

FIRST = ROOT / '보고서/징검다WOORI_첫페이지_시안A.pdf'
PERSONA = ROOT / '페르소나/민우의 금융 생애 주기 인포그래픽.png'
OUT = ROOT / '보고서/징검다WOORI_시안A_우리의삶_2쪽수정본.pdf'
QA = ROOT / 'tmp/pdfs/variant_a_our_lives_review'
QA.mkdir(parents=True, exist_ok=True)
SECOND = QA / 'persona_page.pdf'
pdfmetrics.registerFont(TTFont('MG', 'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MGB', 'C:/Windows/Fonts/malgunbd.ttf'))
W, H = A4
M = 32
CW = W - 2 * M
BLUE = HexColor('#006CAF')
CYAN = HexColor('#20C2E8')
INK = HexColor('#29495F')
PALE = HexColor('#ECF6FB')
LINE = HexColor('#C7DDEB')
MUTED = HexColor('#71889B')
c = canvas.Canvas(str(SECOND), pagesize=A4, pageCompression=1)


def p(text, x, y, width, size=10.5, leading=17, color=INK, bold=False, maxh=None):
    style = ParagraphStyle('text', fontName='MGB' if bold else 'MG', fontSize=size,
                           leading=leading, textColor=color, wordWrap='LTR', splitLongWords=False)
    para = Paragraph(text, style)
    _, height = para.wrap(width, H)
    if maxh is not None and height > maxh + .01:
        raise ValueError(f'Text overflow: {height} > {maxh}: {text}')
    assert y + height <= 800
    para.drawOn(c, x, H - y - height)
    return height


c.setFillColor(CYAN)
c.rect(M, H - 27, 23, 4, stroke=0, fill=1)
p('02 / 민우의 생애전환과 준비 부담', M + 32, 21, CW - 32,
  size=9, leading=13, color=BLUE, bold=True)
p('우리의 삶이 달라질 때,<br/>금융 준비의 어려움도 달라진다',
  M, 57, CW, size=24, leading=29, color=BLUE, bold=True, maxh=58)
p('성인·진학부터 취업·독립까지 이어지는 한 사람의 여정',
  M, 127, CW, size=11.5, leading=17, color=BLUE, bold=True)
p('생활 변화에 맞춰 금융 준비를 연결하는 경험이 필요한 순간을, 가상 고객 민우의 삶을 통해 살펴본다. '
  '민우는 성인·진학, 첫 수입·반독립, 입대·전역, 첫 취업·독립을 거친다. '
  '같은 사람이라도 생활이 달라지면 돈의 목적과 준비해야 할 일도 바뀐다.',
  M, 167, CW, size=10.5, leading=17, maxh=51)

with Image.open(PERSONA) as image:
    image_width, image_height = image.size
display_height = CW * image_height / image_width
c.drawImage(ImageReader(str(PERSONA)), M, H - 250 - display_height,
            width=CW, height=display_height, mask='auto')

p('네 장면을 관통하는 하나의 어려움',
  M, 507, CW, size=13, leading=19, color=BLUE, bold=True)
p('민우가 공통으로 겪는 어려움은 변화마다 필요한 금융업무와 자금 계획을 스스로 연결해야 한다는 것이다. '
  '같은 상황이라도 목표와 여력이 다르므로, 고객이 확인한 실제 계획을 기준으로 준비를 구체화해야 한다.',
  M, 538, CW, size=10.5, leading=17, maxh=51)

c.setFillColor(PALE)
c.roundRect(M, H - 622 - 134, CW, 134, 7, stroke=0, fill=1)
p('첫 취업·독립을 맞은 민우에게 초점을 맞추면',
  M + 14, 637, CW - 28, size=12, leading=18, color=BLUE, bold=True)
p('취업한 민우는 독립을 준비하며 월세·생활비와 저축을 함께 지키고 싶다. '
  '준비할 일을 정리한 뒤에도 송금, 새로운 입금, 큰 지출이 계획에 어떤 영향을 주는지 판단해야 한다.',
  M + 14, 669, CW - 28, size=10.5, leading=17, maxh=51)
p('이제 민우의 독립 준비와 일상의 선택을 징검다WOORI가 이어가는 과정을 살펴본다.',
  M + 14, 729, CW - 28, size=10.2, leading=15, color=BLUE, bold=True, maxh=15)

c.setStrokeColor(LINE)
c.setLineWidth(.6)
c.line(M, H - 813, W - M, H - 813)
c.setFont('MG', 7.5)
c.setFillColor(MUTED)
c.drawString(M, H - 829, '징검다WOORI · 시안 A 연결 · 페르소나')
c.drawRightString(W - M, H - 829, '02')
c.save()

with pymupdf.open(FIRST) as first, pymupdf.open(SECOND) as second:
    assert len(first) == 1
    result = pymupdf.open()
    result.insert_pdf(first)
    result.insert_pdf(second)
    result.set_metadata({'title': '징검다WOORI | 시안 A와 우리의 삶이 달라질 때',
                         'author': '징검다WOORI',
                         'subject': '첫 페이지 시안 A와 제목 없는 페르소나 이미지를 연결한 2쪽 초안'})
    result.save(OUT, garbage=4, deflate=True)
    result.close()

with pymupdf.open(OUT) as result, pymupdf.open(FIRST) as first:
    assert len(result) == 2
    first_text = result[0].get_text()
    second_text = result[1].get_text()
    assert '이러한 연결이 필요한 순간' not in first_text
    assert '우리의 삶이 달라질 때,' in second_text
    assert '민우의 삶이 달라질 때,' not in second_text
    # The first page is copied directly from variant A and must remain visually identical.
    assert result[0].get_pixmap().samples == first[0].get_pixmap().samples
    images = result[1].get_images(full=True)
    assert len(images) == 1
    pix = pymupdf.Pixmap(result, images[0][0])
    with Image.open(PERSONA) as original:
        original = original.convert('RGB')
        assert (pix.width, pix.height) == original.size
        assert pix.samples == original.tobytes()
    for i, page in enumerate(result):
        page.get_pixmap(matrix=pymupdf.Matrix(1.7, 1.7)).save(QA / f'page_{i+1}.png')
    assert '민우의 금융 생애 주기 페르소나' not in result[1].get_text()
print(OUT)
print('Verified: 2 pages; variant A unchanged; supplied title-free persona image preserved pixel-for-pixel.')
