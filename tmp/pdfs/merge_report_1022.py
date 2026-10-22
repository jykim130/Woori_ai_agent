from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tmp/pdf-deps'))
import pymupdf

SOURCES = [
    ROOT / '보고서/징검다WOORI_첫페이지_시안A.pdf',
    ROOT / '보고서/징검다WOORI_2페이지_페르소나_금융준비부담수정본.pdf',
    ROOT / '보고서/징검다WOORI_3페이지_좌측설명_와이어프레임확대.pdf',
    ROOT / '보고서/징검다WOORI_4페이지_좌측설명_와이어프레임확대.pdf',
]
OUT = ROOT / '보고서/10-22내용/징검다WOORI_제안서_1-4페이지_1022.pdf'
QA = ROOT / 'tmp/pdfs/merged_report_1022_review'
OUT.parent.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)

with pymupdf.open() as merged:
    for source_path in SOURCES:
        with pymupdf.open(source_path) as source:
            assert len(source) == 1, str(source_path)
            merged.insert_pdf(source)
    assert len(merged) == 4
    merged.set_metadata({
        'title': '징검다WOORI 제안서 | 10월 22일 내용',
        'author': '징검다WOORI',
        'subject': '제안 개요, 대표 페르소나와 금융 준비 부담, 금융 준비 및 일상 거래의 AI Agent 적용',
    })
    merged.save(OUT, garbage=4, deflate=True)

audit = {'pages': 4, 'order': [], 'all_source_pages_preserved': True}
with pymupdf.open(OUT) as merged:
    assert len(merged) == 4
    for i, source_path in enumerate(SOURCES):
        with pymupdf.open(source_path) as source:
            original, final = source[0], merged[i]
            assert original.rect == final.rect
            assert original.get_text() == final.get_text(), f'Page {i + 1}: text differs'
            matrix = pymupdf.Matrix(2, 2)
            before = original.get_pixmap(matrix=matrix)
            after = final.get_pixmap(matrix=matrix)
            assert before.samples == after.samples, f'Page {i + 1}: visual differs'
            after.save(QA / f'page_{i + 1}.png')
            audit['order'].append({
                'page': i + 1,
                'source': source_path.name,
                'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
                'text_and_pixels_match': True,
            })

(QA / 'merge_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
print(str(OUT))
print('Verified: 4 pages in requested order; source text and rendered pixels preserved exactly.')
