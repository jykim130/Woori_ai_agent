from pathlib import Path
import sys, json, math

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tmp/pdf-author-deps'), str(ROOT/'tmp/pdf-deps')]
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
import pymupdf

OUT = ROOT/'output/pdf/WON_이어봄_생애이벤트_AI동반자_문제정의와근거.pdf'
QA = ROOT/'tmp/pdfs/lifelong_agent_review'
OUT.parent.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
pdfmetrics.registerFont(TTFont('MG','C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MGB','C:/Windows/Fonts/malgunbd.ttf'))
pdfmetrics.registerFontFamily('MG',normal='MG',bold='MGB',italic='MG',boldItalic='MGB')
W,H = landscape(A4)
M=36; CW=W-2*M
NAVY=HexColor('#102F46'); INK=HexColor('#253E4D'); BLUE=HexColor('#006EBD')
TEAL=HexColor('#008576'); MUTED=HexColor('#5D7280'); LINE=HexColor('#D9E4EB')
PALE=HexColor('#F0F6FB'); MINT=HexColor('#EAF6F2'); SAND=HexColor('#FFF4E3')
AMBER=HexColor('#886022'); BG=HexColor('#FCFDFE')
SOURCES={
'S1':('IBK경제연구소 | 2026 개인금융 인사이트',
 '국내 / 2025.10 조사 / 20~64세 은행 계좌 보유자 4,700명, 온라인 설문.',
 '9~10쪽: 초기 거래 유지·이탈 사유. 62.8%는 해당 은행 이탈 경험자의 복수응답 지표. 연령대 비교를 전역 직후의 추적 결과로 해석하지 않음.',
 'https://research.ibk.co.kr/fup/support/institute/about/finance/2026031616371429459317707366478.pdf#page=10'),
'S2':('Rivel Banking Research | Banking on Life',
 '미국 / 2025.4 조사 / 최근 5년 내 생애 이벤트 경험과 은행 변경에 대한 응답.',
 '세대·이벤트별 표본수와 오차 미공개. 차트는 Z세대만 표시. 인과효과·국내 이탈률·전체 이벤트 순위로 해석하지 않음.',
 'https://www.rivel.com/banking-research/why-customers-switch-banks'),
'S3':('Commerce Commission | Personal banking services market study',
 '뉴질랜드 경쟁당국 / 2024.8 최종보고서 / 64쪽, 2.114~2.115절.',
 '첫 취업·첫 주택 마련·결혼 등을 금융기관 재선택 계기로 설명. 이벤트별 이탈률을 산출한 자료는 아님.',
 'https://www.comcom.govt.nz/__data/assets/pdf_file/0019/362035/Final-report-Personal-banking-services-market-study-20-August-2024-Amended-27-August-2024.pdf#page=64'),
'S4':('Accenture | Banking Consumer Study 2025',
 '39개국 / 은행 고객 49,300명 / 2025.3 발간 / 18~20쪽.',
 '개인화의 선택 영향 72%, 주거래은행 개인화 도구 이용 3%. 서로 다른 질문이며 차이를 미충족 고객 비율로 계산하지 않음. 지속 지원은 보고서의 제안.',
 'https://www.accenture.com/content/dam/accenture/final/industry/banking/document/Accenture-Global-Banking-Consumer-Study-2025-Report.pdf#page=18'),
'S5':('J.D. Power | 2026 U.S. Retail Banking Satisfaction Study',
 '미국 / 고객 응답 107,059건 / 2025.1~2026.1 조사 / 2026.3 발표.',
 '최근 3개월 자금 이동 경험 20%, 전년 17%, 40세 미만 23%. 자금 이동은 계좌 해지·전면 이탈과 다름. 생애 이벤트가 원인이라는 분석은 아님.',
 'https://www.jdpower.com/business/press-releases/2026-us-retail-banking-satisfaction-study'),
'S6':('Son et al. (2020) | Digital banking adoption and hidden defection',
 'Journal of Operations Management, 66(4), 418-440. DOI: 10.1002/joom.1066.',
 '실제 개인 거래자료로 경쟁 은행 상품 구매를 분석. 충성 고객에게도 숨은 이탈이 나타날 수 있음. 저자 소속 대학의 초록 확인; 유료 전체 본문 미확보.',
 'https://researchconnect.suny.edu/en/publications/impact-of-customers-digital-banking-adoption-on-hidden-defection-/'),
'S7':('De Caigny et al. (2025) | Life event-based marketing using AI',
 'Journal of Business Research, 193, 115349. DOI: 10.1016/j.jbusres.2025.115349.',
 '유럽 금융회사 고객 21,898명·이메일 94,161건. 출산 전후 상품 보유·가치 변화와 이벤트 예측 연구. 공개 초록·방법·결과 요약 확인. Agent 유지 효과의 실험은 아님.',
 'https://www.sciencedirect.com/science/article/pii/S0148296325001729'),
'S8':('Beyer Diaz et al. (2024) | Improved decision-making through life event prediction',
 'Decision Support Systems, 187, 114342. DOI: 10.1016/j.dss.2024.114342.',
 '유럽 고객 760,438명. 주택 구매 등을 포함한 이벤트 예측에 시계열 활용. 공개 초록·연구 설계 확인. 예측 성능을 서비스 유지 효과로 해석하지 않음.',
 'https://www.sciencedirect.com/science/article/pii/S0167923624001751'),
'S9':('공병엽 (2025) | 금융기관 선택에 대한 인식 연구: 20대 청년층을 대상으로',
 '대한경영학회지, 38(1), 65-95. DOI: 10.18032/kaaba.2025.38.1.65.',
 '국내 20대의 신뢰·전환비용과 주거래은행 지속 의도를 분석. KCI 저자 초록 확인. 실제 이탈 추적 연구가 아니며 표본수·세부 계수는 본 문서에서 인용하지 않음.',
 'https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART003172790')}

c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('WON 이어봄 | 생애 이벤트를 연결하는 AI 금융 동반자 - 문제 정의와 근거')
c.setAuthor('WON 이어봄 기획')
c.setSubject('생애 이벤트·지원 연속성·장기 이용에 관한 공개 근거와 서비스 가설')
audit=[]
def box(x,y,w,h,fill=white,stroke=LINE,r=10):
 c.setFillColor(fill);c.setStrokeColor(stroke or fill);c.setLineWidth(.7)
 c.roundRect(x,H-y-h,w,h,r,stroke=bool(stroke),fill=1)
def t(s,x,y,size=11,color=INK,bold=False):
 font='MGB' if bold else 'MG';tw=pdfmetrics.stringWidth(s,font,size)
 if x+tw>W-M+1: raise ValueError(f'Text overflow: {s}')
 c.setFont(font,size);c.setFillColor(color);c.drawString(x,H-y-size,s)
 audit.append(dict(page=c.getPageNumber(),x=x,y=y,w=tw,h=size,text=s))
def p(s,x,y,w,size=10.5,color=INK,bold=False,leading=None,maxh=None):
 st=ParagraphStyle('b',fontName='MGB' if bold else 'MG',fontSize=size,leading=leading or size*1.5,textColor=color,wordWrap='CJK',splitLongWords=True)
 ob=Paragraph(s,st);_,ph=ob.wrap(w,H)
 if maxh and ph>maxh+.2: raise ValueError(f'Paragraph overflow p{c.getPageNumber()}: {ph}>{maxh}: {s}')
 if y+ph>H-33: raise ValueError(f'Page overflow {s}')
 ob.drawOn(c,x,H-y-ph);audit.append(dict(page=c.getPageNumber(),x=x,y=y,w=w,h=ph,text=s));return ph
def line(x1,y1,x2,y2,color=LINE,width=.7,dash=False):
 c.saveState();c.setStrokeColor(color);c.setLineWidth(width)
 if dash:c.setDash(3,3)
 c.line(x1,H-y1,x2,H-y2);c.restoreState()
def arrow(x1,y1,x2,y2,color=BLUE,dash=False):
 line(x1,y1,x2,y2,color,1.2,dash)
 angle=math.atan2(-(y2-y1),x2-x1);xx=x2;yy=H-y2
 q=c.beginPath();q.moveTo(xx,yy)
 for d in [2.65,-2.65]:q.lineTo(xx+6*math.cos(angle+d),yy+6*math.sin(angle+d))
 q.close();c.setFillColor(color);c.drawPath(q,fill=1,stroke=0)
def pill(s,x,y,fill=PALE,color=BLUE,size=8.4):
 w=pdfmetrics.stringWidth(s,'MGB',size)+17;box(x,y,w,20,fill,None,9);t(s,x+8,y+4,size,color,True);return w
def tag(key,x,y,label=None):
 s=label or key;tw=pdfmetrics.stringWidth(s,'MGB',8.2)
 t(s,x,y,8.2,BLUE,True)
 c.linkURL(SOURCES[key][3],(x,H-y-13,x+tw+3,H-y+2),thickness=0)
def start(n,kicker,title,sub):
 c.setFillColor(BG);c.rect(0,0,W,H,fill=1,stroke=0)
 c.bookmarkPage('p'+str(n));c.addOutlineEntry(title,'p'+str(n),0)
 t('WON 이어봄',M,21,10,NAVY,True);t('PROBLEM / EVIDENCE / AGENT',W-M-203,22,8.3,MUTED)
 line(M,45,W-M,45);t(kicker,M,62,9,TEAL,True)
 t(title,M,81,24,NAVY,True);p(sub,M,119,CW,10.2,MUTED,maxh=31)
def end(n,note='공개 근거와 서비스 제안을 구분 | 2026.10.21 기준 정리'):
 line(M,H-32,W-M,H-32);t(note,M,H-24,7.7,MUTED)
 t(f'{n:02} / 08',W-M-36,H-24,8,BLUE,True);c.showPage()
def note(s,y=525):p(s,M,y,CW,8.5,MUTED,leading=12,maxh=30)
def track(x,y,w,v,color=BLUE,h=13):
 box(x,y,w,h,LINE,None,h/2)
 if v:box(x,y,w*v/100,h,color,None,h/2)

# 1. Definition and evidence logic
start(1,'01  /  문제 정의','삶의 변화마다, 금융 지원을 이어가다',
 '서비스 목표: 생애 이벤트가 생겨도 고객에게 필요한 지원을 이어가며 장기 이용을 만든다.')
box(M,158,CW,107,NAVY,None,12)
pill('문제 정의 | 자료를 종합한 기획 가설',M+19,174,MINT,TEAL)
p('고객의 삶과 금융수요는 바뀌는데,<br/>금융서비스의 지원은 그 변화를 따라 이어지지 않는다.',M+19,205,CW-38,21,white,True,leading=28,maxh=57)
gap=14;ww=(CW-2*gap)/3
cards=[('01','변화하는 금융 선택','진학·취업·주거 변화는<br/>금융기관 선택을 다시 검토할 계기.','S2','S3'),
 ('02','지원의 연속성 공백','개인화 기대와 도구 이용의 간극,<br/>초기 거래 이후 사후관리의 필요.','S1','S4'),
 ('03','거래 관계의 약화','계좌가 남아 있어도 자금과<br/>다음 상품 거래는 분산될 수 있음.','S5','S6')]
for i,(num,title,body,a,b) in enumerate(cards):
 x=M+i*(ww+gap);box(x,282,ww,115)
 t(num,x+14,294,10,TEAL,True);t(title,x+39,291,13,NAVY,True)
 p(body,x+14,321,ww-28,10.7,leading=16,maxh=35)
 tag(a,x+14,375);tag(b,x+45,375)
box(M,415,CW,89,MINT,None)
t('제안하는 서비스',M+17,427,10,TEAL,True)
p('고객의 이전 목표와 금융생활을 기억하고,<br/>생애 이벤트마다 계획·실행·점검을 이어가는 AI 금융 동반자.',M+17,449,CW-34,16,NAVY,True,leading=22,maxh=46)
note('공개 자료는 금융 선택의 변화·지원 공백·거래 약화를 보여준다. 우리은행의 공백 규모와 Agent의 유지 효과는 검증 대상이다.')
end(1)

# 2. Event-linked banking choice, same generation chart
start(2,'02  /  근거 A - 생애 이벤트','이벤트가 생기면, 금융 선택도 움직인다',
 'Rivel 미국 조사: 최근 5년 내 해당 이벤트를 경험한 Z세대 중, 이벤트 중 은행을 변경했다고 응답한 비율.')
leftw=470;rightx=M+leftw+18;rightw=CW-leftw-18
box(M,162,leftw,337)
t('은행 변경 경험 | Z세대',M+17,178,12,NAVY,True)
cx=M+137;cw=285;ys=[230,287,344,401]
for tick in [0,10,20,30,40]:
 xx=cx+cw*tick/40;line(xx,219,xx,437,LINE,.5);t(str(tick),xx-4,446,8,MUTED)
for i,(label,val) in enumerate([('대학 진학',22),('경제활동 시작',24),('이직·직업 변경',32),('출산·부모 됨',30)]):
 yy=ys[i];t(label,M+17,yy+2,10.5,INK)
 box(cx,yy,cw*val/40,21,BLUE if i<3 else TEAL,None,3)
 t(f'{val}%',cx+cw*val/40+7,yy,12,BLUE if i<3 else TEAL,True)
t('축: 0~40% / 각 이벤트 경험자 기준',M+17,476,8.2,MUTED)
box(rightx,162,rightw,159,MINT,None)
pill('기관 분석',rightx+14,175,MINT,TEAL)
p('첫 취업·첫 주택 마련·결혼은<br/>금융기관 재선택의 계기',rightx+14,205,rightw-28,13,NAVY,True,leading=20,maxh=43)
p('뉴질랜드 경쟁당국의 시장조사.<br/>전환 시점에 고객 선택이 활발해질 수 있음을 설명한다.',rightx+14,253,rightw-28,9.6,leading=15,maxh=47)
tag('S3',rightx+14,301,'S3 | 최종보고서 64쪽')
box(rightx,335,rightw,164)
t('근거가 말하는 범위',rightx+14,349,11,NAVY,True)
p('진학·취업·이직은 청년 시나리오의 직접 근거로 활용.<br/><br/>출산은 장기 확장 사례다. 주택 구입의 근거를 첫 자취에 그대로 적용하지 않는다.',rightx+14,376,rightw-28,10.2,leading=16,maxh=100)
tag('S2',M,512,'S2 | Rivel 원문·방법론')
note('미국 조사이며 사건·세대별 표본수와 오차 미공개. 서로 다른 경험자 집단이며 중복 가능. 국내 이탈률·인과효과·전체 이벤트 순위를 뜻하지 않는다.',533)
end(2)

# 3. Continuity gap - independent questions, independent survey
start(3,'03  /  근거 B - 지속 지원','고객이 바라는 맞춤 지원과, 이용 경험의 간극',
 '서로 다른 조사와 질문을 함께 보되, 비율을 합치거나 하나의 인과관계로 연결하지 않는다.')
ww=(CW-18)/2;x2=M+ww+18
box(M,162,ww,312);box(x2,162,ww,312)
pill('글로벌 고객 기대·이용',M+16,177)
t('개인화가 은행 선택에 영향',M+16,211,11,NAVY,True)
t('72%',M+16,234,34,BLUE,True);track(M+113,249,ww-132,72)
t('주거래은행 개인화 도구 이용',M+16,294,11,NAVY,True)
t('3%',M+16,317,34,TEAL,True);track(M+113,332,ww-132,3,TEAL)
p('각 막대는 0~100% 눈금. 서로 다른 질문이다.<br/>차이를 미충족 고객 비율로 계산하지 않는다.',M+16,375,ww-32,9.3,MUTED,leading=14,maxh=32)
p('39개국 49,300명 | Accenture 2025',M+16,421,ww-32,9.2,MUTED)
tag('S4',M+16,450,'S4 | 18~20쪽')
pill('국내 초기 거래 이후',x2+16,177,MINT,TEAL)
t('62.8%',x2+16,212,42,TEAL,True)
p('취업 전 맺은 은행을 떠난 응답자 중<br/><b>관리 미흡을 이탈 사유로 지적</b>',x2+16,275,ww-32,12,leading=19,maxh=44)
track(x2+16,331,ww-32,62.8,TEAL)
p('사후관리 부재·서비스 불만족 등, 복수응답.<br/>전체 고객의 이탈률이 아니며 인과효과도 아니다.',x2+16,375,ww-32,9.3,MUTED,leading=14,maxh=32)
p('국내 대중 조사 4,700명 중 해당 집단 | IBK 2026',x2+16,421,ww-32,9.2,MUTED)
tag('S1',x2+16,450,'S1 | 3·10쪽')
box(M,489,CW,58,NAVY,None,8)
p('<b>기획 해석</b>  상황이 바뀔 때 이전 목표·상담·실행 결과를 연결해, 고객에게 필요한 다음 행동을 제시할 필요가 있다.',M+15,504,CW-30,12,white,leading=18,maxh=36)
end(3)

# 4. Banking relationship vs service continuity
start(4,'04  /  근거 C - 관계 약화','계좌 유지와 거래 관계의 유지는 다를 수 있다',
 'J.D. Power가 설명하는 soft switching: 다른 기관에 계좌를 추가하고 주거래은행의 자금을 점진적으로 옮기는 현상.')
chartw=440;rx=M+chartw+18;rw=CW-chartw-18
box(M,162,chartw,304);t('최근 3개월 내 주거래은행에서 자금 이동',M+16,177,11.5,NAVY,True)
base=410;charttop=226;plotx=M+63;plotw=310;ph=180
for v in [0,5,10,15,20,25]:
 yy=base-ph*v/25;line(plotx,yy,plotx+plotw,yy,LINE,.6);t(f'{v}%',M+19,yy-6,8.4,MUTED)
for xx,val,label,col in [(plotx+39,17,'2025년 조사',HexColor('#8AA6BA')),(plotx+192,20,'2026년 조사',BLUE)]:
 h=ph*val/25;box(xx,base-h,64,h,col,None,3);t(f'{val}%',xx+12,base-h-27,20,col,True);t(label,xx-5,425,9.6,INK)
box(rx,162,rw,132,MINT,None);t('40세 미만 고객',rx+16,179,11,NAVY,True)
t('23%',rx+16,205,38,TEAL,True)
p('같은 자금 이동 경험 비율.<br/>전체 응답자의 하위집단이다.',rx+119,218,rw-135,9.8,leading=15,maxh=47)
box(rx,308,rw,158)
t('숨은 이탈의 학술 근거',rx+16,324,11,NAVY,True)
p('기존 주거래은행 대신 경쟁 은행에서 다음 금융상품을 구매하는 행동.<br/><br/>실제 개인 거래자료를 분석한 연구는 충성 고객에게도 이 현상이 나타날 수 있음을 보고했다. [S6]',rx+16,351,rw-32,10.1,leading=15.5,maxh=98)
tag('S5',M,480,'S5 | 공식 발표·조사 개요');tag('S6',M+178,480,'S6 | 연구 초록')
note('2026년 조사: 미국 고객 응답 107,059건, 2025.1~2026.1 조사. 전년 수치는 같은 발표의 비교값. 자금 이동은 전면 이탈이 아니며 생애 이벤트의 효과를 뜻하지 않는다.',503)
box(M,536,CW,18,PALE,None,4)
t('검증할 두 결과: Agent 지원의 지속 이용 / 은행 거래 관계의 유지',M+10,538,9,BLUE,True)
end(4)

# 5. Scenario mapping, no fabricated event sequence
start(5,'05  /  이벤트별 적용 - 기획 제안','여러 이벤트를 하나의 목표·지원 이력으로 연결',
 '고객마다 발생 순서와 경험 여부가 다르다. 아래는 우선 지원할 사례이며, 네 가지가 이탈률 상위 구간이라는 뜻은 아니다.')
ww=(CW-18)/2;hh=167
scenarios=[
 ('진학·첫 수입','진학 직접 근거 / 첫 수입은 확장',
  '<b>근거</b> 대학 진학 중 은행 변경 경험 [S2]. 아르바이트 첫 입금에 따른 이탈 효과는 미확인.<br/><b>지원</b> 생활비·저축 목표를 세우고 새 수입에 맞춰 조정.<br/><b>이어갈 이력</b> 목표 금액·기간, 고정 지출, 실천 결과.','S2'),
 ('취업·이직','선택 변화의 근거 확보',
  '<b>근거</b> 급여계좌와 연계된 주거래 변경 [S1], 취업·이직 중 은행 변경 경험 [S2].<br/><b>지원</b> 기존 목표를 급여·지출 구조에 맞춰 재설계.<br/><b>이어갈 이력</b> 학생 때의 목표, 저축 습관, 변경된 소득.','S1'),
 ('군 복무·전역','장기 관계 연결의 필요',
  '<b>근거</b> 군 계좌 유입 고객의 거래 유지 약화 [S1]. 전역 직후나 적금 만기 직후의 이탈 급증은 미확인.<br/><b>지원</b> 군 금융거래를 복학·취업 준비 자금계획으로 연결.<br/><b>이어갈 이력</b> 전역 후 목표, 자금 배분, 실행 일정.','S1'),
 ('주거 변화','주택 마련 근거 / 자취는 확장',
  '<b>근거</b> 첫 주택 마련 시 금융기관 재선택 [S3]. 주택 구입 결과를 첫 월세·자취에 일반화하지 않음.<br/><b>지원</b> 보증금·월세·이사 비용을 기존 계획에 반영.<br/><b>이어갈 이력</b> 소득·저축 계획, 주거비, 비상자금.','S3')]
for i,(title,badge,body,source) in enumerate(scenarios):
 x=M+(i%2)*(ww+18);yy=160+(i//2)*(hh+16)
 box(x,yy,ww,hh);t(title,x+14,yy+12,14,NAVY,True)
 pill(badge,x+14,yy+39,MINT,TEAL,7.7)
 p(body,x+14,yy+69,ww-28,9.6,leading=15,maxh=92)
 tag(source,x+ww-35,yy+14)
note('서비스의 장기 확장: 결혼·출산·주택 마련 등. 출산 전후 실제 상품 보유 변화 연구 [S7]는 확장 배경이며, 청년 네 이벤트의 효과를 대신하지 않는다.',520)
tag('S7',M,546,'S7 | 생애 이벤트와 실제 행동 변화 연구')
end(5)

# 6. Agent support cycle and falsifiable outcomes
start(6,'06  /  해결 방향과 검증 - 서비스 가설','기억한 목표가, 다음 지원의 출발점이 되도록',
 '제안: 고객의 이전 목표와 금융생활을 기억하고, 생애 이벤트마다 계획·실행·점검을 이어가는 AI 금융 동반자.')
box(M,160,CW,60,NAVY,None)
t('공유하는 고객의 맥락',M+15,172,11,white,True)
p('목표·기한  /  현재 소득과 지출  /  이전 상담  /  실행·점검 결과  /  고객이 확인한 변화',M+15,193,CW-30,10.5,white,maxh=20)
steps=[('변화 확인','고객에게 달라진 상황 확인'),('계획 조정','이전 목표와 새 필요 연결'),('실행 지원','선택한 행동·절차 안내'),('점검·갱신','결과 확인 후 계획 수정')]
ww=(CW-42)/4
for i,(title,body) in enumerate(steps):
 x=M+i*(ww+14);box(x,240,ww,76,MINT if i==3 else PALE,None)
 t(title,x+12,251,13,TEAL if i==3 else BLUE,True)
 p(body,x+12,279,ww-24,9.5,leading=14,maxh=29)
 if i<3:arrow(x+ww+2,278,x+ww+12,278)
# feedback path returns to memory
line(W-M-16,317,W-M-16,331,TEAL,1.1);line(W-M-16,331,M+4,331,TEAL,1.1)
line(M+4,331,M+4,224,TEAL,1.1);arrow(M+4,224,M+4,220,TEAL)
ww=(CW-18)/2;rx=M+ww+18
box(M,346,ww,149);box(rx,346,ww,149)
t('목표 1 | Agent의 지속 이용',M+14,359,12,NAVY,True)
p('이벤트 이후 30·90·180일의 의미 있는 지원 이용<br/>계획 갱신·실행·점검 완료 / 다음 이벤트에서 재이용',M+14,390,ww-28,10.1,leading=17,maxh=54)
p('의미 있는 이용 = 계획·실행·점검 중 실제 행동.<br/>단순 앱 실행·알림 클릭과 구분한다.',M+14,450,ww-28,8.8,MUTED,leading=13,maxh=29)
t('목표 2 | 은행 거래 관계의 유지',rx+14,359,12,NAVY,True)
p('급여·정기 입금의 지속 / 결제 이용 / 저축 유지<br/>이벤트 전후 거래 변화와 비교군의 차이 확인',rx+14,390,ww-28,10.1,leading=17,maxh=54)
p('일시적 자금 이동을 이탈로 확정하지 않는다.<br/>두 목표의 효과는 각각 측정한다.',rx+14,450,ww-28,8.8,MUTED,leading=13,maxh=29)
p('<b>선행연구의 범위</b> 시계열·텍스트로 이벤트를 예측한 연구 [S7·S8]와 국내 20대의 신뢰·지속 의도 연구 [S9]가 설계 배경이다. 위 Agent 흐름과 유지 효과는 제안이며, 비교 실험으로 검증한다.',M,511,CW,9.2,MUTED,leading=14,maxh=29)
for i,key in enumerate(['S7','S8','S9']):tag(key,M+i*35,546)
end(6)

def source_row(key,y,h):
 title,meta,limit,url=SOURCES[key]
 box(M,y,CW,h)
 pill(key,M+11,y+12)
 p(title,M+58,y+11,CW-153,10.2,NAVY,True,leading=14.2,maxh=29)
 p(meta,M+58,y+31,CW-78,8.7,MUTED,leading=12,maxh=24)
 p(limit,M+58,y+47,CW-78,8.6,INK,leading=12,maxh=h-49)
 bx=W-M-79;by=y+11;box(bx,by,65,22,PALE,None,7);t('원문 열기',bx+10,by+5,8.5,BLUE,True)
 c.linkURL(url,(bx,H-by-22,bx+65,H-by),thickness=0)

# 7. source register - clear provenance
start(7,'07  /  출처와 읽는 법','근거 목록 1 | 기관·기업 보고서',
 '본문의 S 번호와 연결된다. 각 원문 버튼은 공식 보고서 또는 조사 발표로 이동한다.')
for i,key in enumerate(['S1','S2','S3','S4','S5']):source_row(key,155+i*78,72)
end(7,'출처의 대상·기간·분모를 함께 확인 | 원문 링크 포함')

# 8. source register and claims boundary
start(8,'08  /  출처와 읽는 법','근거 목록 2 | 학술논문과 검증 범위',
 '공개 초록·방법·결과 요약으로 확인한 범위를 명시했다. 미확인 효과 크기와 표본수는 추가하지 않았다.')
for i,key in enumerate(['S6','S7','S8','S9']):source_row(key,155+i*83,77)
box(M,496,CW,51,SAND,None,8)
p('<b>관찰 결과</b> 이벤트와 금융 선택·거래 변화  /  <b>기획 해석</b> 지원을 이어갈 필요  /  <b>검증할 가설</b> Agent가 장기 이용과 관계 유지를 높이는가.<br/>해외 비율을 우리은행 이탈률로 환산하지 않으며, 문서의 네 사례는 보편적인 순서나 이탈 상위 4개를 뜻하지 않는다.',M+13,505,CW-26,9.3,AMBER,leading=14,maxh=33)
end(8,'WON 이어봄 | 문제 정의·근거·서비스 가설의 연결')
c.save()

d=pymupdf.open(OUT)
assert len(d)==8
alltext=[]
for i,page in enumerate(d):
 tx=page.get_text();assert len(tx)>300
 assert '\ufffd' not in tx
 alltext.append(f'===== PAGE {i+1} =====\n{tx}')
 page.get_pixmap(matrix=pymupdf.Matrix(1.6,1.6),alpha=False).save(QA/f'page-{i+1:02}.png')
 for block in page.get_text('dict')['blocks']:
  for ln in block.get('lines',[]):
   for sp in ln.get('spans',[]):
    x0,y0,x1,y1=sp['bbox']
    if x0<M-2 or x1>W-M+2 or y0<12 or y1>H-8:
     raise ValueError(f'PDF text out of bounds p{i+1}: {sp}')
for a in audit:
 if a['x']<M-1 or a['x']+a['w']>W-M+1 or a['y']+a['h']>H-12:
  raise ValueError(f'Drawing out of bounds: {a}')
(QA/'extracted_text.txt').write_text('\n\n'.join(alltext),encoding='utf-8')
(QA/'layout_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(pdf=str(OUT),pages=len(d),bytes=OUT.stat().st_size,links=sum(len(pg.get_links()) for pg in d),renders=str(QA)),ensure_ascii=False))
