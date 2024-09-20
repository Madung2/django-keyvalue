import os
import fitz  # PyMuPDF
from PIL import Image

def convert_pdf_to_images(pdf_path, output_folder):
    # PDF 파일 열기
    pdf_document = fitz.open(pdf_path)
    # 각 페이지를 이미지로 변환
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        output_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page{page_num+1}.png")
        # 이미지 저장
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.save(output_path)
        print(f"Saved {output_path}")

def process_directory(directory):
    # 디렉토리 내 모든 파일 확인
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory, filename)
            convert_pdf_to_images(pdf_path, directory)

# 지정된 디렉토리 경로
directory_path = r"C:\Users\tulip\Desktop\신한캐피탈시연\OCR분류기능\4pagefiles_cut"
process_directory(directory_path)