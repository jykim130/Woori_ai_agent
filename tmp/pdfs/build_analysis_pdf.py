from pathlib import Path
import sys
import re
from html import escape

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tmp/pdf-author-deps'))
sys.path.insert(0, str(ROOT / 'tmp/pdf-deps'))

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, Flowable,
)
import pymupdf

SOURCE = ROOT / 'output/WON_이어봄_AI_Agent_활용분석.md'
OUTPUT = ROOT / 'output/pdf/WON_이어봄_AI_Agent_활용분석.pdf'
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

pdfmetrics.registerFont(TTFont('Malgun', 'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunBold', 'C:/Windows/Fonts/malgunbd.ttf'))
pdfmetrics.registerFontFamily('Malgun', normal='Malgun', bold='MalgunBold', italic='Malgun', boldItalic='MalgunBold')

NAVY = colors.HexColor('#123A59')
BLUE = colors.HexColor('#006EAF')
INK = colors.HexColor('#263746')
MUTED = colors.HexColor('#647887')
PALE = colors.HexColor('#EEF5FA')
LINE = colors.HexColor('#D5E1E9')
WIDTH = A4[0] - 38 * mm

BODY = ParagraphStyle('Body', fontName='Malgun', fontSize=9.6, leading=15.5,
    textColor=INK, wordWrap='CJK', spaceAfter=7, splitLongWords=True)
TITLE = ParagraphStyle('Title', parent=BODY, fontName='MalgunBold', fontSize=24,
    leading=33, textColor=NAVY, spaceAfter=10)
H2 = ParagraphStyle('H2', parent=BODY, fontName='MalgunBold', fontSize=15,
    leading=22, textColor=BLUE, spaceBefore=17, spaceAfter=10, keepWithNext=True)
H3 = ParagraphStyle('H3', parent=BODY, fontName='MalgunBold', fontSize=11.3,
    leading=18, textColor=NAVY, spaceBefore=10, spaceAfter=7, keepWithNext=True)
BULLET = ParagraphStyle('Bullet', parent=BODY, leftIndent=11, firstLineIndent=-10,
    spaceAfter=5)
SMALL = ParagraphStyle('Small', parent=BODY, fontSize=8.3, leading=13,
    textColor=MUTED, spaceAfter=8)
CELL = ParagraphStyle('Cell', parent=BODY, fontSize=8.25, leading=12.7, spaceAfter=0)
CELL_HEAD = ParagraphStyle('CellHead', parent=CELL, fontName='MalgunBold', textColor=colors.white)
QUOTE = ParagraphStyle('Quote', parent=BODY, fontName='MalgunBold', textColor=NAVY,
    fontSize=10.3, leading=17, spaceAfter=0)


def inline(text):
    text = text.replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', '-')
    tokens = []
    def link(match):
        key = f'ZZLINKTOKEN{len(tokens)}ZZ'
        tokens.append(f'<link href="{escape(match.group(2), quote=True)}" color="#006EAF"><u>{escape(match.group(1))}</u></link>')
        return key
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text)
    text = escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`', r'<font color="#145B80">\1</font>', text)
    for i, token in enumerate(tokens):
        text = text.replace(f'ZZLINKTOKEN{i}ZZ', token)
    return text


class Architecture(Flowable):
    def __init__(self):
        Flowable.__init__(self)
        self.width = WIDTH
        self.height = 374

    def draw(self):
        c = self.canv
        w = self.width
        cx = w / 2
        c.setStrokeColor(LINE)
        c.setFillColor(colors.HexColor('#F7FAFC'))
        c.roundRect(0, 0, w, self.height, 8, fill=1, stroke=1)
        def box(text, top, bw=410, bh=27, x=None, accent=False):
            x = (w-bw)/2 if x is None else x
            y = self.height-top-bh
            c.setFillColor(BLUE if accent else colors.white)
            c.setStrokeColor(BLUE if accent else LINE)
            c.roundRect(x,y,bw,bh,5,fill=1,stroke=1)
            style=ParagraphStyle('Node', parent=CELL, alignment=TA_CENTER,
                fontName='MalgunBold' if accent else 'Malgun',
                fontSize=9.1,leading=13,textColor=colors.white if accent else INK)
            p=Paragraph(text,style)
            _,ph=p.wrap(bw-14,bh)
            p.drawOn(c,x+7,y+(bh-ph)/2+1)
        def arrow(y_top, y_bottom, x=cx):
            y1=self.height-y_top
            y2=self.height-y_bottom
            c.setStrokeColor(MUTED)
            c.setLineWidth(.8)
            c.line(x,y1,x,y2)
            c.line(x,y2,x-2.5,y2+4)
            c.line(x,y2,x+2.5,y2+4)
        box('고객 입력 / 내부 금융 사건 / 허용된 외부 데이터 갱신', 12)
        arrow(39,49)
        box('동의·접근권한·데이터 최신성 확인',49)
        arrow(76,86)
        box('사건 후보 탐지 + 고객 확인 + 계획 상태 저장',86)
        arrow(113,123)
        box('총괄 에이전트',123,accent=True)
        arrow(150,160)
        gap=8
        bw=(w-36-2*gap)/3
        for i,label in enumerate(['공식 자료 검색','현금흐름 계산','서류·상담 준비']):
            box(label,160,bw=bw,x=18+i*(bw+gap))
        arrow(187,197)
        box('규칙 검사·근거 확인·권한 검사',197)
        arrow(224,234)
        box('고객 선택 / 필요한 직원 검토·인증',234)
        arrow(261,271)
        box('허용된 업무 도구 또는 기존 신청 화면',271)
        arrow(298,308)
        box('결과 확인·과제 갱신·후속 일정 관리',308)
        c.setFont('Malgun',8)
        c.setFillColor(MUTED)
        c.drawCentredString(cx,15,'변경 사건 발생 시 정보 확인과 계획 수립 단계로 돌아가 재검토')


def make_table(rows):
    count=len(rows[0])
    header=rows[0]
    if count==2:
        fractions=[.36,.64]
    elif count==3 and header[1]=='관련 쪽':
        fractions=[.29,.13,.58]
    elif count==3:
        fractions=[.17,.43,.40]
    else:
        fractions=[.15,.25,.32,.28]
    data=[[Paragraph(inline(x),CELL_HEAD if i==0 else CELL) for x in row]
          for i,row in enumerate(rows)]
    table=Table(data,colWidths=[WIDTH*f for f in fractions],repeatRows=1,
        hAlign='LEFT',spaceBefore=3,spaceAfter=11)
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),BLUE),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE]),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),8),
        ('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),8),
        ('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LINEBELOW',(0,-1),(-1,-1),.5,LINE),
    ]))
    return table


class Report(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable,Paragraph) and flowable.style.name=='H2':
            title=flowable.getPlainText()
            key='section-'+title.split('.')[0]
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title,key,level=0,closed=False)


def page_decoration(c,doc):
    c.saveState()
    pw,ph=A4
    c.setFont('Malgun',7.7)
    c.setFillColor(MUTED)
    c.drawString(19*mm,ph-14*mm,'WON 이어봄 1426 | AI Agent 활용 분석')
    c.drawRightString(pw-19*mm,ph-14*mm,'공모전 서비스 구체화 자료')
    c.setStrokeColor(LINE)
    c.setLineWidth(.5)
    c.line(19*mm,ph-17*mm,pw-19*mm,ph-17*mm)
    c.line(19*mm,17*mm,pw-19*mm,17*mm)
    c.setFont('Malgun',7.4)
    c.drawString(19*mm,12*mm,'분석 기준 2026.10.15 | 서비스 제안·구현 방안·검증 가설')
    c.drawRightString(pw-19*mm,12*mm,str(doc.page))
    c.restoreState()


lines=SOURCE.read_text(encoding='utf-8').splitlines()
story=[]
i=0
while i<len(lines):
    line=lines[i].strip()
    if not line:
        i+=1
        continue
    if line.startswith('# '):
        story.append(Paragraph('WON 이어봄 1426<br/>AI Agent 활용 분석',TITLE))
        story.append(Paragraph('고객 서비스 구성 · 은행 업무 효율화 · 단계별 도입과 미래 확장',SMALL))
        i+=1
    elif line.startswith('## '):
        story.append(Paragraph(inline(line[3:]),H2))
        i+=1
    elif line.startswith('### '):
        if re.match(r'### 3\.[1-7] ',line):
            group=[Paragraph(inline(line[4:]),H3)]
            i+=1
            while i<len(lines) and not lines[i].startswith('#'):
                b=lines[i].strip()
                if b.startswith('- '):
                    group.append(Paragraph('• '+inline(b[2:]),BULLET))
                elif b:
                    group.append(Paragraph(inline(b),BODY))
                i+=1
            story.append(KeepTogether(group))
        else:
            story.append(Paragraph(inline(line[4:]),H3))
            i+=1
    elif line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].strip().startswith('|'):
            cells=[v.strip() for v in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?',v) for v in cells):
                rows.append(cells)
            i+=1
        story.append(make_table(rows))
    elif line.startswith('```'):
        i+=1
        while i<len(lines) and not lines[i].strip().startswith('```'):
            i+=1
        i+=1
        story.append(Architecture())
        story.append(Spacer(1,10))
    elif line.startswith('> '):
        q=Table([[Paragraph(inline(line[2:]),QUOTE)]],colWidths=[WIDTH],spaceBefore=3,spaceAfter=10)
        q.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),PALE),
            ('LINEBEFORE',(0,0),(0,-1),3,BLUE),
            ('LEFTPADDING',(0,0),(-1,-1),13),
            ('RIGHTPADDING',(0,0),(-1,-1),13),
            ('TOPPADDING',(0,0),(-1,-1),11),
            ('BOTTOMPADDING',(0,0),(-1,-1),11),
        ]))
        story.append(q)
        i+=1
    elif line.startswith('- '):
        story.append(Paragraph('• '+inline(line[2:]),BULLET))
        i+=1
    elif re.match(r'^\d+\. ',line):
        story.append(Paragraph(inline(line),BULLET))
        i+=1
    else:
        p=[line]
        i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||-|>|```|\d+\. )',lines[i].strip()):
            p.append(lines[i].strip())
            i+=1
        style=SMALL if p[0].startswith(('분석일:', '분석 대상:')) else BODY
        story.append(Paragraph(inline(' '.join(p)),style))

start=next(i for i,f in enumerate(story) if isinstance(f,Paragraph) and f.style.name=='H2' and f.getPlainText().startswith('11.'))
end=next(i for i,f in enumerate(story[start+1:],start+1) if isinstance(f,Paragraph) and f.style.name=='H2')
story[start:end]=[KeepTogether(story[start:end])]

doc=Report(str(OUTPUT),pagesize=A4,rightMargin=19*mm,leftMargin=19*mm,
    topMargin=23*mm,bottomMargin=23*mm,title='WON 이어봄 1426 AI Agent 활용 분석',
    author='서비스 기획 분석',subject='AI 에이전트 활용 지점, 서비스 구현, 효율화 및 미래 확장')
doc.build(story,onFirstPage=page_decoration,onLaterPages=page_decoration)

render=ROOT/'tmp/pdfs/analysis_render'
render.mkdir(exist_ok=True)
pdf=pymupdf.open(OUTPUT)
print(f'pages={len(pdf)} bytes={OUTPUT.stat().st_size}')
alltext=''
for n,page in enumerate(pdf,1):
    alltext+=page.get_text()
    page.get_pixmap(matrix=pymupdf.Matrix(1.15,1.15)).save(render/f'page-{n:02d}.png')
    print(f'page={n} text_chars={len(page.get_text())} links={len(page.get_links())}')
for n in range(1,13):
    assert re.search(rf'{n}\. ',alltext),f'Missing section {n}'
assert '\ufffd' not in alltext
(render/'extracted_text.txt').write_text(alltext,encoding='utf-8')
print('content_checks=passed')
