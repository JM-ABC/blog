import pdfplumber
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pdf_path = r'C:\Users\USER\Downloads\일잘러 장피엠_코딩 1도 모르는 직장인을 위한 Claude Code 시작 가이드_가이드 프롬프트.pdf'

pdf = pdfplumber.open(pdf_path)

for i, page in enumerate(pdf.pages):
    print(f'\n====== PAGE {i+1} ======\n')
    text = page.extract_text()
    if text:
        print(text)
    else:
        print('[No text extracted]')

pdf.close()
