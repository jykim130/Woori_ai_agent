from pathlib import Path
import sys
import json
from html import escape

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'tmp/pdf-author-deps'), str(ROOT / 'tmp/pdf-deps')]

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
import pymupdf

OUT = ROOT / 'output/pdf/WON_이어봄_4대전환_문제정의_근거도식.pdf'
QA = ROOT / 'tmp/pdfs/dropout_evidence_review'
OUT.parent.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
pdfmetrics.registerFont(TTFont('MG', 'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MGB', 'C:/Windows/Fonts/malgunbd.ttf'))
pdfmetrics.registerFontFamily('MG', normal='MG', bold='MGB', italic='MG', boldItalic='MGB')

W, H = A4
M = 36
CW = W - 2*M
NAVY = HexColor('#12334D')
BLUE = HexColor('#006BB6')
TEAL = HexColor('#008577')
INK = HexColor('#263D4D')
MUTED = HexColor('#657785')
LINE = HexColor('#D9E3EA')
PALE = HexColor('#F1F6FA')
MINT = HexColor('#EAF6F3')
AMBER = HexColor('#986114')
SAND = HexColor('#FFF5E4')
RED = HexColor('#A2544C')

SOURCES = {
    'S1': 'https://research.ibk.co.kr/fup/support/institute/about/finance/2026031616371429459317707366478.pdf',
    'S2': 'https://www.rivel.com/banking-research/downloads/banking-on-life-why-customers-switch-banks-rivel-banking-research.pdf',
    'S2M': 'https://www.rivel.com/banking-research/why-customers-switch-banks',
    'S3': 'https://www.consumerinsight.co.kr/up_files/2606_finance.pdf',
}

c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
c.setTitle('WON 이어봄 | 네 가지 생애 전환의 문제 정의와 근거')
c.setAuthor('WON 이어봄 기획 자료')
c.setSubject('공개 조사에 근거한 청년 금융 관계 단절 위험의 도식화')
c.setCreator('ReportLab / vector diagrams / embedded Korean fonts')
audit = []

def box(x, top, w, h, fill=white, stroke=LINE, radius=10):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.setLineWidth(.7)
    c.roundRect(x, H-top-h, w, h, radius, stroke=bool(stroke), fill=1)

def txt(s, x, top, size=10.5, color=INK, bold=False):
    c.setFont('MGB' if bold else 'MG', size)
    c.setFillColor(color)
    c.drawString(x, H-top-size, s)
    audit.append({'page': c.getPageNumber(), 'text': s, 'x': x, 'top': top, 'w': pdfmetrics.stringWidth(s, 'MGB' if bold else 'MG', size), 'h': size})

def para(s, x, top, w, size=10.3, color=INK, bold=False, leading=None, maxh=None):
    style = ParagraphStyle('body', fontName='MGB' if bold else 'MG', fontSize=size,
                           leading=leading or size*1.55, textColor=color,
                           wordWrap='CJK', splitLongWords=True, spaceAfter=0)
    p = Paragraph(s, style)
    pw, ph = p.wrap(w, H)
    if maxh is not None and ph > maxh + .2:
        raise ValueError(f'Paragraph overflow page {c.getPageNumber()}: {ph:.1f}>{maxh}: {s}')
    if top+ph > H-38:
        raise ValueError(f'Page overflow: {s}')
    p.drawOn(c, x, H-top-ph)
    audit.append({'page': c.getPageNumber(), 'text': s, 'x': x, 'top': top, 'w': pw, 'h': ph})
    return ph

def rule(y, x=M, w=CW):
    c.setStrokeColor(LINE)
    c.setLineWidth(.7)
    c.line(x, H-y, x+w, H-y)

def pill(s, x, top, color=BLUE, fill=PALE, size=8.4):
    w = pdfmetrics.stringWidth(s, 'MGB', size) + 16
    box(x, top, w, 20, fill, None, 10)
    txt(s, x+8, top+4, size, color, True)
    return w

def arrow(x1, y1, x2, y2, color=BLUE, dashed=False):
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.1)
    if dashed:
        c.setDash(3, 3)
    c.line(x1, H-y1, x2, H-y2)
    c.setDash()
    p = c.beginPath()
    if abs(y2-y1) < .1:
        p.moveTo(x2, H-y2); p.lineTo(x2-5, H-y2+3); p.lineTo(x2-5, H-y2-3)
    else:
        p.moveTo(x2, H-y2); p.lineTo(x2-3, H-y2+5); p.lineTo(x2+3, H-y2+5)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()

def bar(x, top, w, value, color=BLUE, h=10):
    box(x, top, w, h, LINE, None, h/2)
    if value:
        box(x, top, w*value/100, h, color, None, h/2)

def source_note(label, top, key, page=None, x=M, w=CW):
    para(label, x, top, w, 8.2, MUTED, leading=12.1)
    target = SOURCES[key] + (f'#page={page}' if page else '')
    c.linkURL(target, (x, H-top-24, x+w, H-top+2), relative=0, thickness=0)

def start(kicker, title, subtitle, num, bookmark):
    c.bookmarkPage(bookmark)
    c.addOutlineEntry(title.replace('<br/>',' '), bookmark, 0)
    txt('WON 이어봄 1426', M, 23, 9, NAVY, True)
    txt('문제 정의 · 근거 시각화', W-M-133, 23, 9, MUTED)
    rule(45)
    txt(kicker, M, 62, 9.5, BLUE, True)
    para(title, M, 82, CW, 23, NAVY, True, leading=31, maxh=67)
    para(subtitle, M, 152, CW, 10, MUTED, leading=15, maxh=34)

def footer(num, note='공개 조사 수치와 기획 해석을 구분한 신규 서비스 검토 자료'):
    rule(H-39)
    txt(note, M, H-29, 7.6, MUTED)
    txt(f'{num} / 5', W-M-29, H-29, 8, BLUE, True)
    c.showPage()

def small_title(num, title, x, top):
    pill(num, x, top, BLUE, PALE)
    txt(title, x+38, top+1, 14, NAVY, True)

# PAGE 1 - one-page definition, independent denominators
start('01 / 문제의 핵심', '청소년기의 계좌 관계는<br/>다음 생활까지 이어지고 있는가?',
      '핵심 문제: 생애 전환기에 달라진 금융 수요를 연결하지 못하면 거래 관계가 약해질 수 있다.', 1, 'overview')

gap = 14
cardw = (CW-gap)/2
for x in [M, M+cardw+gap]:
    box(x, 204, cardw, 208)

pill('거래 지속 지표', M+16, 220)
txt('48.7%', M+16, 250, 38, BLUE, True)
para('취업 전 금융거래로 맺은 은행과<br/><b>현재도 거래를 유지</b>', M+16, 306, cardw-32, 11.2, leading=17)
bar(M+16, 354, cardw-32, 48.7)
para('해당 금융거래 이벤트 경험자 기준.<br/>단순 계좌 보유는 제외. [S1, 9쪽]', M+16, 374, cardw-32, 8.5, MUTED, leading=12.5)

x = M+cardw+gap
pill('이탈 사유 응답', x+16, 220, TEAL, MINT)
txt('62.8%', x+16, 250, 38, TEAL, True)
para('해당 은행을 떠난 응답자가<br/><b>관리 미흡을 이탈 사유로 지적</b>', x+16, 306, cardw-32, 11.2, leading=17)
bar(x+16, 354, cardw-32, 62.8, TEAL)
para('사후관리 부재·서비스 불만족 등.<br/>이탈 경험자 대상 복수응답. [S1, 10쪽]', x+16, 374, cardw-32, 8.5, MUTED, leading=12.5)

para('두 수치는 대상이 다르다. 62.8%는 전체 고객의 이탈률이 아니며, 두 지표를 합산하지 않는다.',
     M, 425, CW, 8.8, MUTED, leading=13)

txt('우선 관리할 네 가지 전환', M, 469, 13.2, NAVY, True)
tw = (CW-30)/4
stages = [('01', '성인·진학', '계좌·결제 기반'), ('02', '첫 수입·반독립', '생활비·저축'),
          ('03', '입대·전역', '복무·목돈 준비'), ('04', '취업·독립', '급여·주거 금융')]
for i,(n,t,d) in enumerate(stages):
    xx=M+i*(tw+10)
    box(xx, 498, tw, 99, PALE, None, 8)
    txt(n, xx+12, 509, 12, BLUE, True)
    txt(t, xx+12, 535, 10.1, NAVY, True)
    txt(d, xx+12, 560, 8.4, MUTED)
    if i<3:
        arrow(xx+tw+1, 547, xx+tw+9, 547, MUTED, True)
    c.linkRect('', 'stages12' if i<2 else 'stages34', (xx,H-597,xx+tw,H-498), thickness=0)

box(M, 621, CW, 107, NAVY, None)
para('문제 정의', M+18, 636, CW-36, 10, HexColor('#A8D5F4'), True)
para('생애 전환으로 금융 목적이 바뀔 때,<br/>기존 관계가 다음 생활의 주거래로 이어지지 않을 위험이 있다.',
     M+18, 659, CW-36, 14, white, True, leading=22, maxh=50)
source_note('S1  IBK경제연구소, 「2026 개인금융 인사이트」. 조사: 2025.10, 계좌 보유 20~64세 4,700명. 원문 3·9~10쪽.', 747, 'S1', 9)
footer(1)

# PAGE 2 - stage 1 and stage 2, separate metric types
start('02 / 전환별 근거 ①·②', '성인 생활과 첫 수입,<br/>금융 선택이 새로 시작되는 구간',
      '해외의 은행 변경 경험과 국내의 타행 가입 의향을 각각 제시한다. 같은 이탈률로 비교하지 않는다.', 2, 'stages12')

box(M, 204, CW, 255)
small_title('01', '미성년에서 성인·대학 진학으로', M+16, 220)
pill('해외 보조 근거 · 은행 변경 경험', M+16, 253, BLUE, PALE)
txt('22%', M+16, 286, 35, BLUE, True)
para('대학 진학을 경험한 미국 Z세대 중<br/>해당 생애 사건 중 은행을 변경한 응답 비율', M+133, 291, CW-166, 11, leading=17)
bar(M+16, 339, CW-32, 22, BLUE, 9)
para('<b>기획 해석</b>  진학 전후에 계좌·결제 기반을 다시 선택할 수 있으므로, 기존 금융 수단의 적합성을 점검하는 접점이 필요하다.',
     M+16, 363, CW-32, 10.2, maxh=38)
para('범위: 미국 2025.4 조사, 최근 5년 내 사건 경험. 세대별 표본 수·오차 미공개.<br/>국내 만 19세 생일의 이탈률 또는 안내 부족의 인과효과를 뜻하지 않는다. [S2, 3쪽]',
     M+16, 411, CW-32, 8.3, MUTED, leading=12.5, maxh=30)

box(M, 477, CW, 274)
small_title('02', '용돈에서 첫 수입·반독립으로', M+16, 493)
pill('국내 간접 근거 · 타행 상품 가입 의향', M+16, 526, AMBER, SAND)
txt('73%', M+16, 556, 35, AMBER, True)
para('조건이 좋으면 거래하지 않던 은행에서도<br/>청년미래적금에 가입할 의향', M+133, 561, CW-166, 11, leading=17)
labels=[('우대금리 수준',33),('우대조건 충족 가능성',31),('기존 거래 여부',14)]
for i,(label,val) in enumerate(labels):
    yy=611+i*22
    txt(label, M+16, yy, 8.9, INK)
    bar(M+161, yy+3, 220, val, AMBER, 7)
    txt(f'{val}%', M+395, yy-1, 10, AMBER, True)
para('가입 은행 선택 기준 중 주요 3개 항목 발췌. 각 항목의 분모는 동일하다.', M+16, 681, CW-32, 7.8, MUTED, leading=11)
para('기획 해석: 첫 저축의 선택을 선점하려면 실현 가능한 조건과 현금흐름 지원이 필요하다.<br/>이 조사는 첫 아르바이트 고객의 실제 이탈을 직접 측정하지 않았다. [S3, 3쪽]',
     M+16, 704, CW-32, 8.4, MUTED, leading=12, maxh=31)
source_note('S2  Rivel, Banking on Life, 3쪽.  /  S3  컨슈머인사이트, 2026.6.18, 3쪽. 가입 의향·유보층 n=200.', 767, 'S3', 3)
footer(2)

# PAGE 3 - army evidence is qualitative; employment metrics remain independent
start('03 / 전환별 근거 ③·④', '군 금융 이후와 첫 취업,<br/>다음 거래로 이어지는가?',
      '가입 이벤트가 끝난 뒤의 거래 지속과, 급여·대출을 계기로 일어나는 관계 재편을 살펴본다.', 3, 'stages34')

box(M, 204, CW, 255)
small_title('03', '입대·전역과 군 금융 이후', M+16, 220)
pill('국내 근거 · 연령대별 거래 지속 비교', M+16, 253, TEAL, MINT)
para('군 복무 계좌·군 적금은<br/><b>거래 유지 약화가 관찰된 유입 유형</b>', M+16, 287, CW-32, 16, NAVY, leading=24, maxh=52)
para('IBK는 군 복무 계좌와 청년 예·적금 고객에서 연령대별 유지율 하락 폭이 큰 것으로 분석한다. [S1, 10쪽]',
     M+16, 350, CW-32, 10.1, leading=15.6, maxh=34)
steps=[('군 금융 유입','가입·납입'),('전역 이후 생활','복학·자립'),('후속 금융 준비','목적·기한 연결')]
bw=(CW-64)/3
for i,(a,b) in enumerate(steps):
    xx=M+16+i*(bw+16)
    box(xx, 395, bw, 43, MINT if i!=1 else PALE, None, 6)
    txt(a, xx+9, 402, 9.3, NAVY, True)
    txt(b, xx+9, 419, 7.8, MUTED)
    if i<2: arrow(xx+bw+2, 417, xx+bw+14, 417, TEAL, True)

para('위 연결은 기획 모형이다. 전역 직후 만기금의 타행 유출 규모·원인은 별도 검증이 필요하다.',
     M+6, 466, CW-12, 8.3, MUTED, leading=12)

box(M, 499, CW, 254)
small_title('04', '첫 취업·독립과 주거래 재편', M+16, 515)
pill('서로 다른 두 집단의 지표', M+16, 548, BLUE, PALE)
sx=M+16; sw=(CW-48)/2
rule(581, sx, CW-32)
txt('24%', sx, 594, 30, BLUE, True)
para('미국 Z세대의 첫 경제활동 진입 중<br/>은행 변경 응답 [S2, 3쪽]', sx, 638, sw, 9.5, leading=14.5)
txt('74.3%', sx+sw+16, 594, 30, TEAL, True)
para('국내 대출 이용 경험자의<br/>대출 계기 부수거래 경험 [S1, 33쪽]', sx+sw+16, 638, sw, 9.5, leading=14.5)
para('기획 해석: 급여·주거자금 준비를 카드·납부·저축의 후속 과제로 연결할 필요가 있다.<br/>대출 수치는 사회초년생·주거대출만의 결과가 아니며, 24%와 비교·합산하지 않는다.',
     M+16, 693, CW-32, 8.6, MUTED, leading=13, maxh=40)
source_note('S1  IBK경제연구소, 10·33쪽.  /  S2  Rivel, Banking on Life, 3쪽. 미국 자료는 국내 이탈률로 대입하지 않는다.', 767, 'S1', 33)
footer(3)

# PAGE 4 - explanatory model and a concrete, reviewable problem definition
start('04 / 근거에서 문제 정의로', '관측된 사실과 검증할 연결을<br/>분리하면 기획이 선명해진다',
      '파랑은 확인할 고객 상황, 초록은 공개 조사에서 관찰한 거래 변화다. 점선은 검증할 연결을 뜻한다.', 4, 'definition')

txt('문제를 설명하는 네 단계', M, 205, 12.5, NAVY, True)
flow=[('생활 전환','고객이 확인한 사건'),('금융 수요 변화','새 목적·조건·기한'),('거래은행 재선택','새 상품·급여·대출'),('기존 관계 약화','거래 축소·중단')]
fw=(CW-36)/4
for i,(a,b) in enumerate(flow):
    xx=M+i*(fw+12)
    box(xx, 236, fw, 76, PALE if i<2 else MINT, LINE, 8)
    txt(f'{i+1:02d}', xx+10, 247, 9, BLUE, True)
    txt(a, xx+10, 268, 10.3, NAVY, True)
    txt(b, xx+10, 290, 7.8, MUTED)
    if i<3: arrow(xx+fw+2, 275, xx+fw+10, 275, MUTED, True)
para('전체 경로의 인과관계는 입증되지 않았다. 특히 수요 변화와 이탈 사유는 고객 확인 및 거래 자료로 검증한다.',
     M, 325, CW, 8.6, MUTED, leading=13)

box(M, 372, CW, 140, NAVY, None)
txt('보고서용 문제 정의', M+18, 389, 10.5, HexColor('#A8D5F4'), True)
para('초기 계좌 유치가 이후 생활의 주거래 관계를 보장하지는 않는다.<br/>본 기획은 성인 전환, 첫 수입, 입대·전역, 취업·독립을<br/>우선 관리 구간으로 설정하고, 달라진 금융 목적에 필요한 준비와<br/>후속 관리를 연결해 거래 관계의 지속을 검증한다.',
     M+18, 417, CW-36, 11.7, white, leading=20, maxh=85)

txt('검증할 문제를 측정 가능한 질문으로 바꾸기', M, 541, 12.4, NAVY, True)
rows=[
    ('① 성인·진학', '전환 후 90일 동안 입금·결제가 이어지는가?'),
    ('② 첫 수입', '첫 3개월 수입 유입과 필요한 저축이 지속되는가?'),
    ('③ 입대·전역', '확정 목적 지출 후 보유 예정 잔여자금이 유지되는가?'),
    ('④ 취업·독립', '6·12개월 뒤 급여·생활비 등 핵심 거래가 이어지는가?'),
]
for i,(a,b) in enumerate(rows):
    yy=572+i*36
    box(M, yy, CW, 31, PALE if i%2==0 else white, None, 5)
    txt(a, M+12, yy+8, 9, BLUE, True)
    txt(b, M+119, yy+8, 9.2, INK)

para('위 기간·지표는 검증 설계 제안이다. 전환 전후를 같은 기준으로 관찰하고, 유사한 비교집단을 둔다.<br/>등록금·보증금 납부는 목적 지출로 분리한다. 지원이 실제 이탈을 줄였는지는 별도 평가한다.',
     M, 734, CW, 8.5, MUTED, leading=13, maxh=35)
footer(4, '도식의 연결·측정 기준은 기획 제안이며, 우리은행의 실측 결과가 아님')

# PAGE 5 - source register, source quality and reading rules
start('05 / 출처와 해석 기준', '각 수치의 대상·시점·범위를<br/>원문으로 확인할 수 있게',
      '확인 기준일 2026.10.20  |  모든 그래프는 공개 수치를 바탕으로 새로 구성한 벡터 도식이다.', 5, 'sources')

def source_card(key, title, top, h, lines, button='원문 PDF 열기', link=None, kind=''):
    box(M, top, CW, h)
    pill(key, M+14, top+13)
    txt(title, M+54, top+16, 11, NAVY, True)
    para(lines, M+16, top+48, CW-32, 9.1, leading=14, maxh=h-83)
    label = button
    yy=top+h-27
    txt(label, M+16, yy, 8.7, BLUE, True)
    target=link or SOURCES[key]
    c.linkURL(target, (M+14,H-yy-15,M+145,H-yy+2), thickness=0)
    if kind:
        txt(kind, M+174, yy, 8.2, MUTED)

source_card('S1', 'IBK경제연구소 · 2026 개인금융 인사이트', 204, 151,
    '국내 은행 연구소 / 발간 2026.3 / 대중 조사 2025.10<br/>'
    '표본: 은행 계좌 보유 20~64세 4,700명, 온라인 조사.<br/>'
    '활용: 3쪽 조사 개요, 9~10쪽 초기 금융 관계·이탈 사유, 33쪽 대출 부수거래.<br/>'
    '본 문서에 인용한 세부 집단의 개별 표본 수는 해당 도표에 제시되지 않음.',
    kind='핵심 국내 근거')

source_card('S2', 'Rivel Banking Research · Banking on Life', 371, 165,
    '미국 금융시장 민간 조사기관 / 조사 2025.4<br/>'
    '활용: 3쪽 생애 사건별 은행 변경 경험. 최근 5년 내 사건 경험에 대한 응답.<br/>'
    '세대·사건별 표본 수와 오차 미공개. 국내 청년 고객으로 직접 일반화하지 않음.<br/>'
    '사건과 변경의 연관성을 제시하며, 사건이 원인임을 입증한 설계는 아님.',
    kind='해외 보조 근거')
c.linkURL(SOURCES['S2M'], (M+170,H-523,M+CW-16,H-502), thickness=0)

source_card('S3', '컨슈머인사이트 · 청년미래적금 인식 조사', 552, 151,
    '국내 금융 리서치 기관 / 조사 2026.6.1~12 / 발표 2026.6.18<br/>'
    '전체: 전국 20~34세 266명. 본 문서의 은행 선택·타행 의향 지표: 200명.<br/>'
    '활용: 3쪽 표2. 가입 의향자 및 유보층을 대상으로 한 응답.<br/>'
    '상품 가입 의향 지표로, 실제 거래은행 변경·기존 은행 이탈과 구분.',
    kind='청년 상품 선택의 간접 근거')

box(M, 723, CW, 51, SAND, None, 7)
para('<b>해석 원칙</b>  네 구간은 기획상 우선 검증 대상이다. 실제 이탈률 상위 4개라는 순위는 확인되지 않았다. 공개 조사만으로 우리은행의 이탈률이나 AI 도입 효과를 산정하지 않는다.',
     M+12, 733, CW-24, 9.1, AMBER, leading=14, maxh=34)
footer(5, '원문 링크 포함 · 수치의 대상·분모와 기획 해석을 함께 확인')

c.save()

# Reopen, inspect structure, extract text and render every page.
d=pymupdf.open(OUT)
if len(d)!=5:
    raise ValueError(f'Expected 5 pages, got {len(d)}')
alltext=[]
for i,page in enumerate(d):
    text=page.get_text()
    if len(text)<300:
        raise ValueError(f'Unexpectedly little text on page {i+1}')
    if '\ufffd' in text:
        raise ValueError(f'Invalid replacement glyph on page {i+1}')
    alltext.append(f'===== PAGE {i+1} =====\n{text}')
    page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5), alpha=False).save(QA/f'page-{i+1:02}.png')
    for link in page.get_links():
        if link['kind']==pymupdf.LINK_URI and not link.get('uri','').startswith('https://'):
            raise ValueError(f'Invalid URL: {link}')

escaped=[a for a in audit if a['x']<M-1 or a['x']+a['w']>W-M+1 or a['top']+a['h']>H-20]
if escaped:
    raise ValueError(f'Out-of-bounds drawing: {escaped}')
(QA/'extracted_text.txt').write_text('\n\n'.join(alltext),encoding='utf-8')
(QA/'layout_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pdf':str(OUT),'pages':len(d),'bytes':OUT.stat().st_size,
                  'links':sum(len(p.get_links()) for p in d),'render_dir':str(QA)},ensure_ascii=False))
